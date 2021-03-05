import re
import scrapy
from scrapy.loader import ItemLoader
from ..items import CebItem
from itemloaders.processors import TakeFirst
pattern = r'(\xa0)?'

class CebSpider(scrapy.Spider):
	name = 'ceb'
	start_urls = ['https://www.ceb.cz/novinky/tiskove-zpravy/']

	def parse(self, response):
		post_links = response.xpath('//div[@id="js_sidebar"]/ul//a/@href').getall()
		yield from response.follow_all(post_links, self.parse_category)

	def parse_category(self, response):
		articles = response.xpath('//article[@class="card"]')
		for article in articles:
			date = ''.join(article.xpath('.//span[@class="card__date"]/text()').getall()).strip().split(' ')[0]
			post_links = article.xpath('.//a/@href').get()
			yield response.follow(post_links, self.parse_post,cb_kwargs=dict(date=date))

	def parse_post(self, response, date):
		title = response.xpath('//div[@id="js_content"]/h1/text()').get()
		content = response.xpath('//div[@class="documentText"]//text()').getall()
		content = [p.strip() for p in content if p.strip()]
		content = re.sub(pattern, "",' '.join(content))

		item = ItemLoader(item=CebItem(), response=response)
		item.default_output_processor = TakeFirst()

		item.add_value('title', title)
		item.add_value('link', response.url)
		item.add_value('content', content)
		item.add_value('date', date)

		yield item.load_item()
