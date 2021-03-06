import six
from scrapy.core.downloader import Downloader, _get_concurrency_delay, Slot
from scrapy.core.engine import ExecutionEngine
from scrapy.core.scheduler import Scheduler
from scrapy.core.scraper import Scraper
from scrapy.crawler import Crawler, CrawlerProcess
from scrapy.utils.misc import load_object


class MyCrawlerProcess(CrawlerProcess):
    def create_crawler(self, crawler_or_spidercls):
        if isinstance(crawler_or_spidercls, MyCrawler):
            return crawler_or_spidercls
        return self._create_crawler(crawler_or_spidercls)

    def _create_crawler(self, spidercls):
        if isinstance(spidercls, six.string_types):
            spidercls = self.spider_loader.load(spidercls)
        return MyCrawler(spidercls, self.settings)


class CloseOnlyLastTime:
    def __init__(self, f):
        self.f = f
        self.first = True

    def __call__(self, *args, **kwargs):
        if not self.first:
            self.f(*args, **kwargs)
        self.first = False


class MyExecutionEngine(ExecutionEngine):
    downloader = None

    def __init__(self, crawler, spider_closed_callback):
        self.crawler = crawler
        self.settings = crawler.settings
        self.signals = crawler.signals
        self.logformatter = crawler.logformatter
        self.slot = None
        self.spider = None
        self.running = False
        self.paused = False
        self.scheduler_cls = load_object(self.settings['SCHEDULER'])
        self.scraper = Scraper(crawler)
        self._spider_closed_callback = spider_closed_callback
        if self.downloader is None:
            downloader_cls = load_object(self.settings['DOWNLOADER'])
            MyExecutionEngine.downloader = downloader_cls(crawler)
        self.downloader = MyExecutionEngine.downloader
        self.downloader.close = CloseOnlyLastTime(self.downloader.close)


class MyCrawler(Crawler):
    def _create_engine(self):
        return MyExecutionEngine(self, lambda _: self.stop())


class MyDownloader(Downloader):
    def _get_slot(self, request, spider):
        key = self._get_slot_key(request, spider)
        if key not in self.slots:
            conc = self.ip_concurrency if self.ip_concurrency else self.domain_concurrency
            if 'facebook' in key:
                conc, delay = _get_concurrency_delay(conc, spider, self.settings)
            else:
                conc, delay = 10, 0
            self.slots[key] = Slot(conc, delay, self.randomize_delay)

        return key, self.slots[key]
