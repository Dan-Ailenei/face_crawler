# self.write_to_file(response, "take_profiel_picture.html")
# from scrapy.shell import inspect_response
# inspect_response(response, self)
# -*- coding: utf-8 -*-
import json
from urllib.parse import urlparse

from scrapy.conf import settings as scrapy_settings
import logging
from io import BytesIO
import requests
import scrapy
from django.core.files.uploadedfile import InMemoryUploadedFile
from scrapy import Spider
from crawler_components.selector import PageSelector
from crawler_components.utils import clean_url, add_query_argument
from models.models import Person
from models.utils import person_to_dict

try:
    import face_recognition
    import numpy as np
    from PIL import Image
except ImportError:
    face_recognition = None
    print("Face recognition module is not installed, if you want to detect no_faces in the picture, install it\n"
          "refer to https://face-recognition.readthedocs.io/en/latest/installation.html\n"
          "Running the following commands should be enough\n"
          "pip install cmake\n"
          "pip install face_recognition")


class PersonSpider(Spider):
    name = 'person'

    def __init__(self, *args, **kwargs):
        super(PersonSpider, self).__init__(*args, **kwargs)
        self.MOBILE_URL = 'https://m.facebook.com'
        self.MAIN_URL = 'https://www.facebook.com'
        self.SERVER_URL = scrapy_settings.pop('SERVER_URL', None)
        name = scrapy_settings.pop('FACEBOOK_NAME', None)
        facebook_id = scrapy_settings.pop('FACEBOOK_ID', None)
        self.first_requests = []
        if None in (name, facebook_id, self.SERVER_URL):
            raise ValueError("facebook id and name need to be specified")
        # useless if you run the crawler properly, but just for safety
        self.SUBJECT = self.check_if_friend_saved(facebook_id)
        if self.SUBJECT is None:
            self.SUBJECT = Person.objects.create(identifier=facebook_id, name=name)
        self.selector = PageSelector(self.SUBJECT)
        self.serialize_fields = Person._meta.get_fields()

    def start_requests(self):
        yield self.request_person_info_medium(self.SUBJECT)
        yield self.request_get_friends_low(self.SUBJECT)

    def get_person_friends_callback(self, response):
        current_person = response.meta['current_person']
        friends_a_tags, next_url = self.selector.select_hrefs_and_next_url(response, current_person)

        friends = []
        for friend_a in friends_a_tags:
            friend_id = clean_url(friend_a.get('href'), "id")
            friend_name = friend_a.get_text()
            current_friend = Person.objects.get_or_create(identifier=friend_id, name=friend_name)[0]
            current_person.add_to_friends(current_friend)
            friends.append(current_friend)

        yield self.request_verify_friends_are_scraped(friends, current_person, 1001)
        if next_url:
            yield scrapy.Request(f'{self.MOBILE_URL}{next_url}', self.get_person_friends_callback,
                                 meta={'current_person': current_person}, priority=1000)

    def manage_friends_callback(self, response):
        friends = response.meta['friends']
        persons_ids = json.loads(response.body)['persons_ids']
        friends = [friend for friend in friends if friend.identifier in persons_ids]
        for friend in friends:
            yield self.request_get_friends_low(friend)
            yield self.request_person_info_medium(friend)

    def get_person_info_callback(self, response):
        current_person = response.meta['current_person']
        url, siblings = self.selector.select_person_info_and_picture_url(response, current_person)

        # probabil ca daca se opreste aici la sigint ai pus-o desi nu cred
        if url:
            for kind, sibling in siblings:
                if kind == 'Frate':
                    current_person.brothers.add(sibling)
                elif kind == 'Soră':
                    current_person.sisters.add(sibling)
                elif kind == 'Mamă':
                    current_person.mother = sibling
                elif kind == 'Tată':
                    current_person.father = sibling
                elif kind == "Fiică" or kind == "Fiu":
                    if current_person.sex:
                        sibling.father = current_person
                    elif current_person.sex is not None:
                        sibling.mother = current_person
                    sibling.save()
            if '/profile/picture/view' in urlparse(url).path:
                using_url = self.MOBILE_URL
            else:
                using_url = self.MAIN_URL
            yield scrapy.Request(f'{using_url}{url}', self.get_person_picture_callback,
                                 meta={'current_person': current_person,
                                       'meta_url': using_url}, priority=101)
        else:
            current_person.scraped = True
            yield self.request_post_person_high(current_person)

        current_person.save()

    def get_person_picture_callback(self, response):
        meta_url = response.meta['meta_url']
        im_bytes = b''
        if meta_url == self.MAIN_URL:
            picture_url = self.selector.select_profile_image(response)
        else:
            picture_url = self.selector.select_profile_image_mobile(response)
        current_person = response.meta['current_person']
        if picture_url:
            profile_picturre, n_faces, im_bytes = self.get_profile_picture_url(picture_url, current_person.name)
            if profile_picturre:
                current_person.picture = profile_picturre
                current_person.number_of_face = n_faces
        else:
            logging.debug(f"{self.get_person_picture_callback.__name__} this page doesn't have a image url "
                          f"url: {response.url}")
        current_person.scraped = True
        current_person.save()
        yield self.request_post_person_high(current_person, im_bytes)

    def try_get_other_picture_with_face_url(self, friend):
        raise NotImplemented("We do not support to try another picture yet")

    def get_current_url(self, url, current_person):
        return f'{url}{current_person.identifier}'

    def get_profile_url(self, current_person):
        url = f'{self.get_current_url(self.MOBILE_URL, current_person)}'
        if 'php' in current_person.identifier:
            url = add_query_argument(url, 'v', 'info')
        else:
            url = f'{url}/about'
        return url

    def get_current_friends_url(self, current_person):
        return f'{self.get_current_url(self.MOBILE_URL, current_person)}/friends'

    def request_get_friends_low(self, current_person):
        return self.request_get_friends(current_person, -100000)

    def request_person_info_medium(self, current_person):
        return scrapy.Request(self.get_profile_url(current_person),
                              self.get_person_info_callback, meta={'current_person': current_person},
                              priority=100)

    def request_get_friends(self, current_person, priority):
        return scrapy.Request(f'{self.MOBILE_URL}{current_person.identifier}/friends', self.get_person_friends_callback,
                              meta={'current_person': current_person}, priority=priority)

    @staticmethod
    def write_to_file(response, filename):
        with open(filename, 'wb') as f:
            f.write(response.body)

    @staticmethod
    def check_if_friend_saved(friend_url):
        try:
            return Person.objects.get(identifier=friend_url)
        except Person.DoesNotExist:
            return None

    @staticmethod
    def get_profile_picture_url(picture_url, name):
        image_request = requests.get(picture_url)
        no_faces = None
        if image_request.status_code != 200:
            logging.debug(f"this url could not be downloaded {picture_url}")
            return None, None
        img_bytes = BytesIO(image_request.content)

        if face_recognition:
            array_image = np.array(Image.open(img_bytes))
            no_faces = len(face_recognition.face_locations(array_image))
        img = InMemoryUploadedFile(img_bytes, None, f'{name}.jpg', 'image/jpeg', img_bytes.getbuffer().nbytes, None)
        return img, no_faces, image_request.content

    def parse(self, response):
        pass

    def request_verify_friends_are_scraped(self, friends, current_person, priority):
        payload = json.dumps({'ids_names': [(friend.identifier, friend.name) for friend in friends],
                              'current_person_id_name': (current_person.identifier, current_person.name)})
        return scrapy.Request(f'{self.SERVER_URL}/persons/filter', self.manage_friends_callback,
                              body=payload, priority=priority, method='POST', meta={'friends': friends})

    def request_post_person_high(self, current_person, im_bytes=b''):
        payload = json.dumps(person_to_dict(current_person)).encode('utf-8')
        return scrapy.Request(f'{self.SERVER_URL}/persons', method='POST', body=payload+im_bytes, priority=1050)
