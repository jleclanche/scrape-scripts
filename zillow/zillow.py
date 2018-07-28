import csv
import random

import requests
from lxml import html

# zipcodes: https://simplemaps.com/static/data/us-zips/1.2/uszipsv1.2.csv

ZIPCODES = ["02129"]

PROXIES = []


def get_ua():
	return "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36"


def parse(zipcode, filter=None):
	"""
	available sort orders are :
	newest : Latest property details,
	cheapest : Properties with cheapest price
	"""

	if filter == "newest":
		url = "https://www.zillow.com/homes/for_sale/{0}/0_singlestory/days_sort".format(
			zipcode
		)
	elif filter == "cheapest":
		url = "https://www.zillow.com/homes/for_sale/{0}/0_singlestory/pricea_sort/".format(
			zipcode
		)
	else:
		url = "https://www.zillow.com/homes/for_sale/{0}_rb/?fromHomePage=true&shouldFireSellPageImplicitClaimGA=false&fromHomePageTab=buy".format(
			zipcode
		)

	for i in range(5):
		headers = {
			"accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
			"accept-encoding": "gzip, deflate, sdch, br",
			"accept-language": "en-GB,en;q=0.8,en-US;q=0.6,ml;q=0.4",
			"cache-control": "max-age=0",
			"upgrade-insecure-requests": "1",
			"user-agent": get_ua(),
		}
		proxies = {}
		if PROXIES:
			proxy = random.choice(PROXIES)
			proxies["http"] = f"http://{proxy}/"
			proxies["https"] = f"https://{proxy}/"

		response = requests.get(url, headers=headers, proxies=proxies)
		parser = html.fromstring(response.text)

		search_results = parser.xpath("//div[@id='search-results']//article")
		properties_list = []

		for properties in search_results:
			raw_address = properties.xpath(
				".//span[@itemprop='address']//span[@itemprop='streetAddress']//text()"
			)
			raw_city = properties.xpath(
				".//span[@itemprop='address']//span[@itemprop='addressLocality']//text()"
			)
			raw_state = properties.xpath(
				".//span[@itemprop='address']//span[@itemprop='addressRegion']//text()"
			)
			raw_postal_code = properties.xpath(
				".//span[@itemprop='address']//span[@itemprop='postalCode']//text()"
			)
			raw_price = properties.xpath(
				".//span[@class='zsg-photo-card-price']//text()"
			)
			raw_info = properties.xpath(".//span[@class='zsg-photo-card-info']//text()")
			raw_broker_name = properties.xpath(
				".//span[@class='zsg-photo-card-broker-name']//text()"
			)
			url = properties.xpath(".//a[contains(@class,'overlay-link')]/@href")
			raw_title = properties.xpath(".//h4//text()")

			address = " ".join(" ".join(raw_address).split()) if raw_address else None
			city = "".join(raw_city).strip() if raw_city else None
			state = "".join(raw_state).strip() if raw_state else None
			postal_code = "".join(raw_postal_code).strip() if raw_postal_code else None
			price = "".join(raw_price).strip() if raw_price else None
			info = " ".join(" ".join(raw_info).split()).replace(u"\xb7", ",")
			broker = "".join(raw_broker_name).strip() if raw_broker_name else None
			title = "".join(raw_title) if raw_title else None
			property_url = "https://www.zillow.com" + url[0] if url else None
			is_forsale = properties.xpath('.//span[@class="zsg-icon-for-sale"]')
			properties = {
				"address": address,
				"city": city,
				"state": state,
				"postal_code": postal_code,
				"price": price,
				"facts and features": info,
				"real estate provider": broker,
				"url": property_url,
				"title": title,
			}
			if is_forsale:
				properties_list.append(properties)

		return properties_list


def get_for_zipcode(zipcode):
	print("Fetching data for %s" % (zipcode))
	scraped_data = parse(zipcode, filter="Homes For You")
	print("Got data:", scraped_data)

	with open("%s.csv" % (zipcode), "w") as csvfile:
		fieldnames = [
			"title",
			"address",
			"city",
			"state",
			"postal_code",
			"price",
			"facts and features",
			"real estate provider",
			"url",
		]
		writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
		writer.writeheader()

		for row in scraped_data:
			writer.writerow(row)


def main():
	for zipcode in ZIPCODES:
		get_for_zipcode(zipcode)


if __name__ == "__main__":
	main()
