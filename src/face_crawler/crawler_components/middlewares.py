from scrapy import signals
from scrapy.exceptions import IgnoreRequest


# class AldreadyScrapedMiddleware:
#     def __init__(self):
#         self.client = Client()
#
#     @classmethod
#     def from_crawler(cls, crawler):
#         instance = cls()
#         crawler.signals.connect(instance.spider_opened, signal=signals.spider_opened)
#         return instance
#
#     def process_request(self, request, spider):
#         current_person = request.meta['current_person']
#         already_scraped = False
#         if request.callback == spider.manage_friends_callback:
#             already_scraped = self.client.person_friends_are_scraped(current_person)
#         # momentan sunt doar alte 2 callback-uri
#         elif request.callback == spider.get_person_info_callback:
#             already_scraped = self.client.person_is_in_process(current_person)
#
#         if already_scraped:
#             raise IgnoreRequest(f"This url has already been scraped {request.url}")
#
#     def spider_opened(self, spider):
#         spider.logger.info('Spider opened: %s' % spider.name)
