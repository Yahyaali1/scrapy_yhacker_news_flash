import scrapy
from scrapy.spiders import Spider
from scrapy.selector import Selector

from ..items import YcombinatorItem
# TODO MOVE THE START URL IN FILE

from ..datakeys import DataKeys
DEFAULT_PAGE_COUNT = 2


class YCombinatorSpider(Spider):
    name = "news.ycombinator"
    start_urls = ["https://news.ycombinator.com/jobs?next=0"]

    def __init__(self, last_job_id=None, no_of_pages=None, *args, **kwargs):
        super(YCombinatorSpider, self).__init__(*args, **kwargs)
        self.init_values(last_job_id, no_of_pages)

    # Return based on the job url else extract and continue
    def init_values(self, last_job_id, no_of_pages):
        self.items = []
        if last_job_id is None:
            if no_of_pages is None:
                self.scrap_pages = DEFAULT_PAGE_COUNT
            else:
                self.scrap_pages = no_of_pages
            self.scrap_pages_count_flag = True
        else:
            self.scrap_pages_count_flag = False
            self.last_job_id = int(last_job_id)
        self.page_count = 0
        self.base_url = "https://news.ycombinator.com/"

    def read_next_job(self, job_id: int):
        if self.scrap_pages_count_flag:
            return True
        else:
            return job_id > self.last_job_id

    def parse(self, response):
        sel = Selector(response)
        jobs = sel.xpath('//tr[@class="athing"]')
        scrap_next_page = True
        self.page_count = self.page_count+1

        # LOOP through all jobs until last read job is found.
        for job in jobs:
            job_id = int(job.xpath('.//@id').get())
            if self.read_next_job(job_id):
                item = YcombinatorItem()
                item['job_id'] = job_id
                item['job_url'] = job.xpath(
                    './/td[@class="title"]/a[@class="storylink"]/@href').get()
                item['job_msg'] = job.xpath(
                    './/td[@class="title"]/a[@class="storylink"]/text()').get()
                item[DataKeys.COMPANY_NAME] = job.xpath(
                    './/td[@class="title"]/span[@class="sitebit comhead"]/a/span/text()').get()
                self.items.insert(0, item)
            else:
                scrap_next_page = False
                break
        if scrap_next_page and self.page_count < self.scrap_pages:
            next_link = sel.xpath('.//a[@class="morelink"]/@href').get()
            if next_link is not None:
                print(next_link)
                yield scrapy.Request(self.base_url+next_link, callback=self.parse)
        print(len(self.items))
        yield {'items': self.items}
