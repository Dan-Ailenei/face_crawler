from configuration_setup.ormsetup import setup_orm
setup_orm()
from crawler_components.mechanism import MyCrawlerProcess
from crawler_components.spiders.login_spider import LoginSpider
from scrapy.utils.project import get_project_settings
from crawler_components.spiders.person_spider import PersonSpider
from twisted.internet import reactor, defer
from scrapy.utils.log import configure_logging


def main():
    configure_logging()
    settings = get_project_settings()
    jobdir = settings.pop('JOBDIR', None)
    downloader_middlewares = settings.pop('DOWNLOADER_MIDDLEWARES', None)
    runner = MyCrawlerProcess(settings)

    @defer.inlineCallbacks
    def crawl():
        yield runner.crawl(LoginSpider)
        runner.settings['JOBDIR'] = jobdir
        runner.settings['DOWNLOADER_MIDDLEWARES'] = downloader_middlewares
        yield runner.crawl(PersonSpider)
        reactor.stop()

    crawl()
    reactor.run() # the script will block here until the last crawl call is finished


if __name__ == '__main__':
    main()
