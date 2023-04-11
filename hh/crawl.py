from multiprocessing import Process
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from scraper.spiders.job import JobSpider


class DomainCrawlerScript():

    def __init__(self):
        self.crawler = CrawlerProcess(get_project_settings())
        # self.crawler.install()
        # self.crawler.configure()

    def _crawl(self):

        self.crawler.crawl(JobSpider)
        self.crawler.start()
        self.crawler.stop()

    def crawl(self):
        p = Process(target=self._crawl)
        p.start()
        p.join()

crawler = DomainCrawlerScript()

def domain_crawl():
    crawler.crawl()