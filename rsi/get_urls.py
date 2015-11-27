#!/usr/bin/env python
import bs4
# import json
import re
import sys
import requests
import requests_cache


# Cache all requests
requests_cache.install_cache()


BASE_URL = "https://robertsspaceindustries.com"
CSS_URL_RE = re.compile(r"""background-image:\w?url\(['"](.+)['"]\)""")

IMAGE_TYPES = (
	"channel_item_full",
	"component_description",
	"cover",
	"heap_infobox",
	"heap_lightbox",
	"home_transmissions_item_expanded",
	"post",
	"post_section_header",
	"press_latest_source",
	"product_thumb_in_description",
	"product_thumb_large",
	"product_thumb_medium_and_small",
	"product_thumb_shipmod",
	"slideshow",
	"slideshow_pager",
	"source_pager",
	"source_section_header",
	"source_wide",
	"store_large",
	"store_small",
	"store_source_small_zoom",
	"subscribers_vault_thumbnail",
	"vault_thumb",
	"wallpaper_thumb",
)


def get_background(css):
	if css:
		return CSS_URL_RE.match(css).groups(1)[0]


def clean_image(src):
	for imgtype in IMAGE_TYPES:
		src = src.replace(imgtype, "source")
	if src.startswith("/"):
		src = BASE_URL + src
	return src


def main():
	with open(sys.argv[1]) as f:
		soup = bs4.BeautifulSoup(f.read(), "lxml")

	posts = []
	images = set()

	for a in soup.find_all("a"):
		obj = {}
		obj["type"] = a.select(".type")[0].text
		bg_elem = a.select(".background")[0]
		obj["background"] = get_background(bg_elem.attrs.get("style", ""))
		obj["comments"] = int(a.select("div.comments")[0].text)
		obj["when"] = a.select(".time_ago span.value")[0].text
		obj["body"] = a.select("div.body")[0].text.strip()
		obj["title"] = a.select("div.title")[0].text.strip()
		obj["href"] = a.attrs.get("href")

		posts.append(obj)

		if obj["background"]:
			images.add(clean_image(obj["background"]))

	print("Downloading articles:")
	i = 0
	for post in posts:
		i += 1
		sys.stdout.write("\r%i / %i" % (i, len(posts)))
		if not post["href"]:
			continue
		r = requests.get(BASE_URL + post["href"])
		soup = bs4.BeautifulSoup(r.content, "lxml")
		for image in soup.find_all("img"):
			for attr in ("src", "data-srcset"):
				if attr in image.attrs:
					src = clean_image(image.attrs[attr])
					images.add(src)
	sys.stdout.write("... done.\n")

	for url in images:
		print(url)

if __name__ == "__main__":
	main()
