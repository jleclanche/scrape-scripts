#!/usr/bin/env python
import os
from decimal import Decimal
from argparse import ArgumentParser
from urllib.request import urlretrieve
from bs4 import BeautifulSoup


USAGE = "Usage: %(prog)s [FILES]"
BASE_URL = "http://www.patreon.com/"
ID_MATCH = "user?u="
CREATION_MATCH = "/creation?hid="


def process_files(files):
	creators = set()
	for filename in files:
		with open(filename, "r") as f:
			try:
				soup = BeautifulSoup(f)
			except UnicodeDecodeError as e:
				print("WARNING: Got %r while decoding %r. Ignoring." % (e, filename))
				continue
			for a in soup.find_all("a"):
				creator = a.get("href").replace(BASE_URL, "")
				if creator.startswith(ID_MATCH):
					creator = int(creator[len(ID_MATCH):])
				creators.add(creator)
	print(len(creators), "creators found")

	return creators


def bootstrap_creators(creators):
	if not os.path.exists("creators/id/"):
		os.makedirs("creators/id/")

	if not os.path.exists("creations/id/"):
		os.makedirs("creations/id/")

	for creator in creators:
		if isinstance(creator, int):
			source = BASE_URL + ID_MATCH + str(creator)
			dest = "creators/id/%i.html" % (creator)
		elif creator.startswith(CREATION_MATCH):
			id = int(creator[len(CREATION_MATCH):])
			source = BASE_URL + CREATION_MATCH + str(id)
			dest = "creations/id/%i.html" % (id)
			# Ignore
			continue
		else:
			if creator.startswith("http://"):
				# Some exploit in patreon that wasn't fixed...
				print("WARNING: Skipping %r" % (creator))
				continue
			elif creator.startswith("/creation?hid="):
				dest = "creations/id/%i.html"
			source = BASE_URL + creator
			dest = "creators/%s.html" % (creator)
		print("Downloading %s" % (source))
		if not os.path.exists(dest):
			urlretrieve(source, dest)


def datamine(paths):
	print("URL|# Patrons|Min. pledge|Earnings ($)|Condition")
	for path in paths:
		for root, dirs, files in os.walk(path):
			for filename in files:
				filename = os.path.join(root, filename)
				with open(filename, "r") as f:
					soup = BeautifulSoup(f)
					condition = soup.find("form", attrs={"id": "bePatron"})
					if not condition:
						# we got a 404 for some reason
						continue
					else:
						condition = condition.find("span", attrs={"class": "headorange"}).text
					min_amount = soup.find("input", attrs={"id": "patAmt"})
					min_amount = Decimal(min_amount["value"].replace(",", "")) if min_amount else 0
					earnings = soup.find("span", attrs={"id": "totalEarnings", "class": "dollars_per"})
					earnings = Decimal(earnings.text.replace(",", "") if earnings else 0)
					url = soup.find("link", attrs={"rel": "canonical"})["href"]
					patrons = soup.find("div", attrs={"id": "totalPatrons", "class": "numheader"})
					patrons = int(patrons.text) if patrons else 0
					print("%s|%i|%s|%s|%s" % (url, patrons, min_amount, earnings, condition))


def scrape():
	res_dir = "_res/"
	if not os.path.exists(res_dir):
		os.makedirs(res_dir)
	i = 0
	while True:
		i += 1
		source = BASE_URL + "discoverNext?srt=2&ty=cr&p=%i" % (i)
		dest = res_dir + "%i.html" % (i)
		_, headers = urlretrieve(source, dest)
		if headers.get("Content-Length") == "0":  # Header value is always a string
			print("Stopping")
			break
		print("Downloaded %r" % (source))


def main():
	import sys
	parser = ArgumentParser(prog=sys.argv[0])
	parser.add_argument(
		"--scrape",
		action="store_true",
		help="Scrapes 'discover' pages into res/"
	)
	parser.add_argument(
		"--get-creators",
		nargs="+",
		type=str,
		metavar="FILE",
		help="Parses files to download creators from them"
	)
	parser.add_argument(
		"--datamine",
		nargs=1,
		type=str,
		metavar="DIR",
		help="Parses files in a directory and outputs csv data."
	)
	args = parser.parse_args(sys.argv[1:])
	if args.scrape:
		scrape()
		exit()
	if args.get_creators:
		creators = process_files(args.get_creators)
		bootstrap_creators(creators)
	if args.datamine:
		datamine(args.datamine)


if __name__ == "__main__":
	main()
