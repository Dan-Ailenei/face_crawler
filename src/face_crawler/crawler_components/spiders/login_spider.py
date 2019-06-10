import scrapy
from scrapy import FormRequest, Spider
from scrapy.conf import settings
from scrapy.exceptions import CloseSpider


class LoginSpider(Spider):
    name = 'login'
    logged_in = False

    def start_requests(self):
        if None in settings['CREDENTIALS'].values():
            raise CloseSpider("You need to complete the credentials in crawler_components/settings to start crawling")
        yield scrapy.Request('https://www.facebook.com/login', self.parse, dont_filter=True)

    def parse(self, response):
        yield FormRequest.from_response(response, formdata=settings['CREDENTIALS'],
                                        callback=self.after_login, dont_filter=True)

    def after_login(self, response):
        # if not 200 you should stop crawling
        if response.request.meta.get('redirect_urls') is not None:
            print("LOGGED IN SUCCESFULLY")
            LoginSpider.logged_in = True
        else:
            raise CloseSpider("LOGGED IN FAILED, INVALID CREDENTIALS")
