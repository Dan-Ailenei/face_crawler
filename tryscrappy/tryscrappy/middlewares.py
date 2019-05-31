from scrapy import Request, signals
from scrapy.exceptions import IgnoreRequest


class LogginDownloaderMiddleware:
    def __init__(self):
        self.first = True

    @classmethod
    def from_crawler(cls, crawler):
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware, imediatly after cookie downloader middleware.
        if spider.first_requests is not None and request.callback not in (spider.parse, spider.after_login):
            spider.first_requests.append(request)
            if self.first:
                self.first = False
                return Request('https://www.facebook.com/login', spider.parse, dont_filter=True,
                               priority=10000000)
            else:
                raise IgnoreRequest("You are not logged in yet, don't stop the program untill then "
                                    "you will lose requests")

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)
