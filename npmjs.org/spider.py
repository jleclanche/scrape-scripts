import json
import scrapy


class NpmJsSpider(scrapy.Spider):
	name = "npmjsspider"
	start_urls = ["https://www.npmjs.com/browse/star"]
	filename = "packages.json"

	def __init__(self):
		self.packages = {}

	def parse(self, response):
		for package in response.css(".package-details"):
			url = package.css('a.name::attr("href")').extract()[0]
			name = package.css("a.name::text").extract()[0]
			description = package.css("p.description::text").extract()
			if description:
				description = description[0]
			version = package.css("p.author a.version::text").extract()
			if version:
				version = version[0]
			date = package.css('p.author span::attr("data-date")').extract()
			if date:
				date = date[0]
			self.packages[name] = {
				"url": url,
				"name": name,
				"description": description,
				"version": version,
				"date": date
			}

		next_page = response.css('.pagination a.next::attr("href")')
		if next_page:
			url = response.urljoin(next_page[0].extract())
			yield scrapy.Request(url, self.parse)

	def closed(self, reason):
		with open(self.filename, "w") as f:
			json.dump(self.packages, f)
