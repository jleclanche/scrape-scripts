#!/usr/bin/env python
import re
import requests
import requests_cache
from bs4 import BeautifulSoup


# Cache all requests
requests_cache.install_cache()

BASEURL = "http://eu.battle.net/blizzcon/en"
MENU = BASEURL + "/data/menu.json"
META_DATA = BASEURL + "/media/meta-data?id={id}&dataKey={dataKey}"
THUMBNAIL_PAGE = BASEURL + "/media/thumbnail-page?page={page}&dataKey={dataKey}"
MEDIA_URL = "http://media.blizzard.com/blizzcon/{url}/{id}-full.jpg"


def flatten_url_structure(item):
	if "children" not in item:
		return {item["url"]: item["label"]}

	urls = {}
	for child in item["children"]:
		urls.update(flatten_url_structure(child))
	return urls


def get_views_page(dataKey, page):
	path = THUMBNAIL_PAGE.format(page=page, dataKey=dataKey)
	# print(dataKey, "->", path)
	r = requests.get(path)
	soup = BeautifulSoup(r.content, "lxml")
	links = soup.find_all("a", href=re.compile(r"^\?view=.+"))
	hrefs = [a.attrs["href"][len("?view="):] for a in links]
	links = links[:1]
	pagination = soup.find(class_="ui-pagination")
	if pagination:
		max_page = int(pagination.find_all("a")[-1].attrs["data-pagenum"])
		if page < max_page:
			return hrefs, page + 1
	return hrefs, 0


def get_all_views(dataKey):
	ret = []
	page, next_page = 0, 1
	while page < next_page:
		page = next_page
		hrefs, next_page = get_views_page(dataKey, page)
		ret += hrefs
	return ret


def get_wallpapers(dataKey):
	ret = []
	for id in get_all_views(dataKey):
		r = requests.get(META_DATA.format(id=id, dataKey=dataKey))
		soup = BeautifulSoup(r.content, "lxml")
		best_resolution = soup.find_all("a")[-1]
		ret.append(best_resolution.attrs["href"])
	return ret


def process_urls(urls):
	images = []
	for url, name in urls.items():
		dataKey = ":".join(url[len("/media"):].strip("/").split("/"))
		if dataKey == "wallpapers":
			images += get_wallpapers(dataKey)
		else:
			ids = get_all_views(dataKey)
			images += [MEDIA_URL.format(url=url.lstrip("/"), id=id) for id in ids]
	return images


def main():
	images = []
	menu = requests.get(MENU).json()

	for item in menu["children"]:
		if item["label"] == "Media":
			urls = flatten_url_structure(item)
			images += process_urls(urls)

	for image in images:
		print(image)


if __name__ == "__main__":
	main()
