import scrapy
from scrapy import Spider
from scrapy.selector import Selector
from scrapy.exceptions import CloseSpider

from wiki.items import WikiItem
from datetime import datetime

class WikiSpider(Spider):
  name = "wiki"
  counter = 0
  allowed_domains = ["en.wikipedia.org"]
  start_urls = [
      "https://en.wikipedia.org/wiki/Wikipedia:Contents/A%E2%80%93Z_index",
  ]

  def parse(self, response):
    pages = Selector(response).xpath("//table[@id='toc']//a/@href").getall()

    for page in pages:
      page = response.urljoin(page)
      #self.log("passing to next page")
      yield scrapy.Request(page, callback=self.next_page_parse)
      #self.log("passed to next page"+page)

  def next_page_parse(self,response):
    #self.log("entered next page")
    pages = Selector(response).xpath("//div[@class='mw-allpages-body']//li[@class='allpagesredirect']/a/@href").getall()

    for page in pages:
      page = response.urljoin(page)
      #self.log("passing to main page")
      yield scrapy.Request(page, callback=self.main_page)

  def main_page(self,response):
    title =  response.url.split("/")[-1]
    filename = f'htmlfiles/{title}.html'
    myfile = response.css('table.infobox').get()

    if (myfile is not None) and (myfile != ''):
      with open(filename,'w', encoding='utf-8') as f:
        f.write(myfile)
        self.log(f'saved file {filename}')
        WikiSpider.counter += 1
        if WikiSpider.counter==3:
          raise CloseSpider("successffullly saved 3 files")

      item = WikiItem()
      item["url"] = response.url
      item['title'] = title
      item['time_stamp'] = datetime.now().isoformat()
      item['file_name'] = filename

      yield item
          
      
            
      