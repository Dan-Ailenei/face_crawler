# self.write_to_file(response, "take_profiel_picture.html")
# from scrapy.shell import inspect_response
# inspect_response(response, self)
# -*- coding: utf-8 -*-
from urllib.parse import urlparse

from scrapy.conf import settings as scrapy_settings
import logging
from io import BytesIO
import requests
import scrapy
from django.core.files.uploadedfile import InMemoryUploadedFile
from scrapy import Spider
from face_crawler.selector import PageSelector
from face_crawler.utils import clean_url, add_query_argument
from models.models import Person

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
        name = scrapy_settings.pop('FACEBOOK_NAME', None)
        facebook_id = scrapy_settings.pop('FACEBOOK_ID', None)
        self.first_requests = []
        if name is None or facebook_id is None:
            raise ValueError("facebook id and name need to be specified")
        # useless if you run the crawler properly, but just for safety
        self.SUBJECT = self.check_if_friend_saved(facebook_id)
        if self.SUBJECT is None:
            self.SUBJECT = Person.objects.create(identifier=facebook_id, name=name)
        self.selector = PageSelector(self.SUBJECT)

    def start_requests(self):
        yield from self.request_manage_friends_low(self.SUBJECT)
        yield from self.request_person_info_medium(self.SUBJECT)

    def manage_friends(self, response):
        current_person = response.meta['current_person']
        friends_a_tags, next_url = self.selector.select_hrefs_and_next_url(response, current_person)

        # trebuie sa incerc sa le iau pe toate odata din db
        for friend_a in friends_a_tags:
            # incerc sa-l iau din db, care o sa fie pe server
            current_friend_id = friend_a.get('href')
            current_friend_id = clean_url(current_friend_id, "id")
            current_friend = self.check_if_friend_saved(current_friend_id)
            if not current_friend:
                current_friend = Person.objects.create(identifier=current_friend_id, name=friend_a.get_text())
                current_person.add_to_friends(current_friend)

            yield from self.request_manage_friends_low(current_friend)
            yield from self.request_person_info_medium(current_friend)

        if next_url:
            yield scrapy.Request(f'{self.MOBILE_URL}{next_url}', self.manage_friends,
                                 meta={'current_person': current_person}, priority=1000)

    def get_person_info(self, response):
        current_person = response.meta['current_person']
        url, siblings = self.selector.select_person_info_and_picture_url(response, current_person)

        if url:
            for kind, sibling in siblings:
                # salveaza numa daca nu e deja in db
                sibling.save()
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
                # nu are rost sa pornesec un alt request pentru ca tebuie sa il aibe la prieteni
            if '/profile/picture/view' in urlparse(url).path:
                using_url = self.MOBILE_URL
            else:
                using_url = self.MAIN_URL
            yield scrapy.Request(f'{using_url}{url}', self.get_person_picture,
                                 meta={'current_person': current_person,
                                       'meta_url': using_url}, priority=100)
        else:
            current_person.scraped = True

        current_person.save()

    def get_person_picture(self, response):
        meta_url = response.meta['meta_url']
        if meta_url == self.MAIN_URL:
            picture_url = self.selector.select_profile_image(response)
        else:
            picture_url = self.selector.select_profile_image_mobile(response)
        current_person = response.meta['current_person']
        if picture_url:
            profile_picturre, n_faces = self.get_profile_picture_url(picture_url, current_person.name)
            if profile_picturre:
                current_person.picture = profile_picturre
                current_person.number_of_face = n_faces
        else:
            logging.debug(f"{self.get_person_picture.__name__} this page doesn't have a image url "
                          f"url: {response.url}")
        current_person.scraped = True
        current_person.save()

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

    def request_manage_friends_low(self, current_person):
        yield from self.request_manage_friends(current_person, -100000)

    def request_person_info_medium(self, current_person):
        yield scrapy.Request(self.get_profile_url(current_person),
                             self.get_person_info, meta={'current_person': current_person},
                             priority=100)

    def request_manage_friends(self, current_person, priority):
        yield scrapy.Request(self.get_current_friends_url(current_person), self.manage_friends,
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
        return img, no_faces

    def parse(self, response):
        pass