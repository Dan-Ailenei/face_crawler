import os

CREDENTIALS = {
    'email': None,
    'pass': None
}
FACEBOOK_NAME = 'Dan Ailenei'
FACEBOOK_ID = '/dan.ailenei.9'

# CLOSESPIDER_ERRORCOUNT = 1
COOKIES_ENABLED = True
CONCURRENT_REQUESTS = 1
DOWNLOAD_DELAY = 5  # 0.25 - 250 ms of delay
ROBOTSTXT_OBEY = False
COOKIES_DEBUG = True
SCHEDULER_DEBUG = True
# 'LOG_FILE': 'logs.txt',
LOG_DATEFORMAT = '%d-%m-%Y %H:%M:%S'
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JOBDIR = os.path.join(BASE_DIR, "resources", "cached_requests/person-1")

DEFAULT_REQUEST_HEADERS = {
    'Accept': 'text/html',
    'Accept-Language': 'ro',
}

BOT_NAME = 'tryscrappy'

SPIDER_MODULES = ['crawler_components.spiders']
NEWSPIDER_MODULE = 'crawler_components.spiders'

ROBOTSTXT_OBEY = False

# custom settings
NOT_FACES_LIST = \
    [
    'https://scontent.fclj2-1.fna.fbcdn.net/v/t1.0-1/cp0/e15/q65/c15.0.50.50a/p50x50/10354686_10150004552801856_220367501106153455_n.jpg?_nc_cat=1&efg=eyJpIjoiYiJ9&_nc_ht=scontent.fclj2-1.fna&oh=a2814e99ff91bcbfb23ee5a57b82909f&oe=5D91883F',
    'https://scontent.fclj2-1.fna.fbcdn.net/v/t1.0-1/cp0/e15/q65/c15.0.50.50a/p50x50/10645251_10150004552801937_4553731092814901385_n.jpg?_nc_cat=1&efg=eyJpIjoiYiJ9&_nc_ht=scontent.fclj2-1.fna&oh=12e325c3d35a470bb016a3a472aeb057&oe=5D914140',
    'https://scontent.fclj2-1.fna.fbcdn.net/v/t1.0-1/cp0/e15/q65/c15.0.50.50a/p50x50/1379841_10150004552801901_469209496895221757_n.jpg?_nc_cat=1&efg=eyJpIjoiYiJ9&_nc_ht=scontent.fclj2-1.fna&oh=7ef0d577ed46ba37e83fe945204953b6&oe=5D97BE80',
        ]

DOWNLOADER = 'crawler_components.mechanism.MyDownloader'
SCHEDULER_DISK_QUEUE = 'scrapy.squeues.PickleFifoDiskQueue'
SCHEDULER_MEMORY_QUEUE = 'scrapy.squeues.FifoMemoryQueue'

SERVER_URL = 'http://kinship.go.ro'
