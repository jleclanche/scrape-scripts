import json
import os
import scrapy
from dateutil.parser import parse as parse_ts


class NpmJsSpider(scrapy.Spider):
	name = "npmjsspider"
	start_urls = ["https://www.npmjs.com/browse/star"]
	filename = "packages.json"
	registry_url = "https://registry.npmjs.org/{0}"

	def __init__(self, dir=None):
		super(NpmJsSpider, self).__init__()
		self.packages = {}
		if dir is None:
			raise Exception("Missing argument: -a dir=<path>")
		if not os.path.exists(dir):
			os.makedirs(dir)
		self.basedir = dir

	def get_package_path(self, name):
		name = name.replace("/", "-")
		dir = os.path.join(self.basedir, name[0])
		if not os.path.exists(dir):
			os.makedirs(dir)
		return os.path.join(dir, name + ".json")

	def save_package(self, response):
		data = json.loads(response.body.decode("utf-8"))
		path = self.get_package_path(data["name"])
		self.dump_json(data, path)

	def dump_json(self, obj, path):
		with open(path, "w") as f:
			json.dump(obj, f, indent=4, sort_keys=True, separators=(",", ": "))

	def extract_package_data(self, package):
		url = package.css('a.name::attr("href")').extract()[0]
		name = package.css("a.name::text").extract()[0]
		description = package.css("p.description::text").extract()
		if description:
			description = description[0]
		version = package.css("p.author a.version::text").extract()
		if version:
			version = version[0]
		date = package.css('p.author span::attr("data-date")').extract()
		return name, {
			"url": url,
			"name": name,
			"description": description,
			"version": version,
			"date": date and date[0],
		}

	def get_package_date(self, path):
		if not os.path.exists(path):
			return
		with open(path, "r") as f:
			data = json.load(f)
		mod_date = parse_ts(data["time"]["modified"])
		return mod_date

	def parse(self, response):
		for package in response.css(".package-details"):
			name, pkgdata = self.extract_package_data(package)
			self.packages[name] = pkgdata
			path = self.get_package_path(name)
			pkgdate = self.get_package_date(path)
			if not pkgdate or not pkgdata["date"] or pkgdate < parse_ts(pkgdata["date"]):
				url = self.registry_url.format(name)
				yield scrapy.Request(url, self.save_package)

		next_page = response.css('.pagination a.next::attr("href")')
		if next_page:
			url = response.urljoin(next_page[0].extract())
			yield scrapy.Request(url, self.parse)

	def closed(self, reason):
		self.dump_json(self.packages, os.path.join(self.basedir, self.filename))
