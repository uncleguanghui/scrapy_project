# Scrapy settings for project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html

local_cookies_store = False  # 是否要本地缓存 cookies

BOT_NAME = 'spider_project'

SPIDER_MODULES = ['spider_project.spiders']
NEWSPIDER_MODULE = 'spider_project.spiders'

# 允许指定状态码的 response (将使用自定义的 ErrorCodeMiddleware 中间件打印接口详情）
HTTPERROR_ALLOWED_CODES = [400, 401, 403, 404]

# 日志等级以及格式
LOG_LEVEL = 'INFO'
LOG_FORMATTER = 'spider_project.logformatter.PoliteLogFormatter'

# Crawl responsibly by identifying yourself (and your website) on the user-agent
# USER_AGENT = 'spider_project (+http://www.yourdomain.com)'

# 不遵守 robots.txt 规则
ROBOTSTXT_OBEY = False

# 允许重定向
MEDIA_ALLOW_REDIRECTS = True

# 每个请求之间的延迟（秒）
DOWNLOAD_DELAY = 0.25

# 失败重试次数
RETRY_TIMES = 3

# 代理池
PROXY_URL = 'http://127.0.0.1:5555/random'

# Configure maximum concurrent requests performed by Scrapy (default: 16)
# CONCURRENT_REQUESTS = 32

# Configure a delay for requests for the same website (default: 0)
# See https://docs.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
# DOWNLOAD_DELAY = 3
# The download delay setting will honor only one of:
# CONCURRENT_REQUESTS_PER_DOMAIN = 16
# CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
# COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
# TELNETCONSOLE_ENABLED = False

# Override the default request headers:
# DEFAULT_REQUEST_HEADERS = {
#   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
#   'Accept-Language': 'en',
# }

# Enable or disable spider middlewares
# See https://docs.scrapy.org/en/latest/topics/spider-middleware.html
SPIDER_MIDDLEWARES = {
    'spider_project.middlewares.ErrorCodeMiddleware': 543,
}

# Enable or disable downloader middlewares
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
DOWNLOADER_MIDDLEWARES = {
    'spider_project.middlewares.IgnoreNoChangesRequestMiddleware': 541,
    'spider_project.middlewares.HeaderMiddleware': 542,
    'spider_project.middlewares.RandomUserAgentMiddleware': 543,
    'spider_project.middlewares.CookiesMiddleware': 544,
    # 'spider_project.middlewares.ProxyMiddleware': 545,
}

# Enable or disable extensions
# See https://docs.scrapy.org/en/latest/topics/extensions.html
# EXTENSIONS = {
#    'scrapy.extensions.telnet.TelnetConsole': None,
# }

# Configure item pipelines
# See https://docs.scrapy.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
    'spider_project.pipelines.DuplicatesPipeline': 200,
    'spider_project.pipelines.CleanPipeline': 300,
    'spider_project.pipelines.MysqlPipeline': 400,
    'spider_project.pipelines.MailPipeline': 500,
}

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/autothrottle.html
# AUTOTHROTTLE_ENABLED = True
# The initial download delay
# AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
# AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
# AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
# AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
# HTTPCACHE_ENABLED = True
# HTTPCACHE_EXPIRATION_SECS = 0
# HTTPCACHE_DIR = 'httpcache'
# HTTPCACHE_IGNORE_HTTP_CODES = []
# HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'
