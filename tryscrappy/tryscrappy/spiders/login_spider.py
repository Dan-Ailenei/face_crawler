import scrapy
from scrapy import FormRequest, Spider

from tryscrappy.credentials import credentials


class LoginSpider(Spider):
    name = 'login'

    def start_requests(self):
        yield scrapy.Request('https://www.facebook.com/login', self.parse, dont_filter=True)

    def parse(self, response):
        yield FormRequest.from_response(response, formdata=credentials,
                                        callback=self.after_login, dont_filter=True)

    def after_login(self, response):
        # if not 200 you should stop crawling
        print("SHUTTING DOWN")
