import scrapy
from scrapy import Spider
from scrapy.http import FormRequest
from scrapy.utils.response import open_in_browser


class QuotesSpider(Spider):
    name = 'quotes'
    start_urls = ('https://www.facebook.com/login',)

    def parse(self, response):
        return FormRequest.from_response(response,
                                         formdata={
                                             'email': 'aileneidan@yahoo.com',
                                             'pass': 'chineziiardmeleaguri'
                                         },
                                         callback=self.scrape_pages)

    def scrape_pages(self, response):
        open_in_browser(response)
        yield scrapy.Request('https://www.facebook.com/dan.ailenei.9/friends', self.scrape_pages)
