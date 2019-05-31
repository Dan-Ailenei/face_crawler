from scrapy.crawler import CrawlerRunner

from orm.ormsetup import setup_orm
from tryscrappy.mechanism import MyCrawlerRunner

setup_orm()

from tryscrappy.spiders.login_spider import LoginSpider
from scrapy.utils.project import get_project_settings
from tryscrappy.spiders.person_spider import PersonSpider
from twisted.internet import reactor, defer
from scrapy.utils.log import configure_logging


configure_logging()
runner = CrawlerRunner(
    get_project_settings()
)


@defer.inlineCallbacks
def crawl():
    yield runner.crawl(LoginSpider)
    yield runner.crawl(PersonSpider)
    reactor.stop()


crawl()
reactor.run() # the script will block here until the last crawl call is finished
