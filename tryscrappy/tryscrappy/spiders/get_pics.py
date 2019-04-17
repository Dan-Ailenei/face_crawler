# -*- coding: utf-8 -*-
import re
from collections import deque

import scrapy
from scrapy import Spider
from scrapy.http import FormRequest
from scrapy.utils.response import open_in_browser

from tryscrappy import credentials
from tryscrappy.queue.friends import Person


class QuotesSpider(Spider):
    name = 'pics'
    start_urls = ('https://www.facebook.com/login',)

    def __init__(self, *args, **kwargs):
        super(QuotesSpider, self).__init__(*args, **kwargs)
        self.BASE_URL = 'https://m.facebook.com/'
        self.subject = Person('dan.ailenei.9', None)
        self.current_person = self.subject
        self.people = deque()
        self.visited = set()
        self.href_reg = re.compile(r'/\w+(\.(\w+\.?)+)?\d*\?')

    def parse(self, response):
        return FormRequest.from_response(response,
                                         formdata=credentials.credentials,
                                         callback=self.after_login)

    def add_friends_to_queue(self, friends):
        for friend in friends:
            # incerc sa-l iau din db
            current_person = self.check_if_friend_saved(friend)
            if not current_person:
                picture_url = self.get_profile_picture_url(friend)
                if not picture_url:
                    picture_url = self.try_get_other_picture_with_face_url(friend)
                # salvam persoana in db chiar daca poza este None
                self.save_individual(friend, picture_url)
                current_person = Person(friend, self.get_picture_from_url(picture_url))

            self.people.append(current_person)

    def check_if_friend_saved(self, friend):
        pass

    def get_friends_urls(self, response):
        return []

    def get_profile_picture_url(self, friend):
        return None

    def try_get_other_picture_with_face_url(self, friend):
        return None

    def save_individual(self, friend, picture_url):
        pass

    def check_if_friend_saved(self, friend):
        return None

    def check_kinship(self, person, subject):
        return False

    def get_picture_from_url(self, picture_url):
        pass

    def get_friends_urls(self, person):
        return []

    def manage_friends(self, response):
        with open('mypage.html', 'wb') as f:
            f.write(response.body)
        # friends = self.get_friends_urls(response)
        # self.add_friends_to_queue(friends)

        # if not self.people:
        #     return
        # self.current_person = self.people.popleft()
        # if self.current_person.picture and self.check_kinship(self.current_person, self.subject):
        #     # log l-am gas pe tac-tu
        #     return
        # return scrapy.Request(self.get_current_url(), self.manage_friends)

    def get_current_url(self):
        return f'{self.BASE_URL}/{self.current_person.identifier}'

    def get_current_friends_url(self):
        return f'{self.get_current_url()}/friends'

    def after_login(self, response):
        return scrapy.Request(self.get_current_friends_url(), self.manage_friends)
