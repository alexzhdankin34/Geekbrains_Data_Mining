from dotenv import load_dotenv
import os
from pathlib import Path

from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings
from blogparse import settings
from blogparse.spiders.gb_blog import GbBlogSpider
from blogparse.spiders.avito import AvitoSpider
from blogparse.spiders.instagram import InstagramSpider

env_path = Path(os.path.dirname(__file__),'.env')
load_dotenv(dotenv_path=env_path)

if __name__ == "__main__":
        craw_settings = Settings()
        craw_settings.setmodule(settings)
        crawler_proc = CrawlerProcess(settings=craw_settings)
        #crawler_proc.crawl(GbBlogSpider)
        #crawler_proc.crawl(AvitoSpider)
        crawler_proc.crawl(InstagramSpider, (os.getenv('LOGIN'), os.getenv('INSTA_PWD')))
        crawler_proc.start()
