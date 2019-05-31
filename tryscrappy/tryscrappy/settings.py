
#     https://doc.scrapy.org/en/latest/topics/settings.html
#     https://doc.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://doc.scrapy.org/en/latest/topics/spider-middleware.html

# 'USER_AGENT': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.100 Safari/537.36)',
COOKIES_ENABLED = True
FACEBOOK_NAME = 'Dan Ailenei'
FACEBOOK_ID = '/dan.ailenei.9'

CONCURRENT_REQUESTS = 1
DOWNLOAD_DELAY = 5  # 0.25 - 250 ms of delay
ROBOTSTXT_OBEY = False
COOKIES_DEBUG = True
SCHEDULER_DEBUG = True
# 'LOG_FILE': 'logs.txt',
LOG_DATEFORMAT = '%d-%m-%Y %H:%M:%S'
# 'LOG_STDOUT': True,
JOBDIR = "crawls/person-1"

DEFAULT_REQUEST_HEADERS = {
    'Accept': 'text/html',
    'Accept-Language': 'ro',
}

BOT_NAME = 'tryscrappy'

SPIDER_MODULES = ['tryscrappy.spiders']
NEWSPIDER_MODULE = 'tryscrappy.spiders'

ROBOTSTXT_OBEY = False

# DOWNLOADER_MIDDLEWARES = {
#     'tryscrappy.middlewares.LogginDownloaderMiddleware': 710,
# }
