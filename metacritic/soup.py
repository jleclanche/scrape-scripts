#!/usr/bin/env python
import bs4
import requests
import requests_cache


# Cache all requests
requests_cache.install_cache()

METACRITIC_ROOT = "http://www.metacritic.com"
GAME_RELEASES_ROOT = "/browse/games/release-date/available/%(platform)s/date/"
PLATFORMS = {
	"pc",
	"ps4",
	"xboxone",
	"ps3",
	"xbox360",
	"wii-u",
	"3ds",
	"vita",
	"ios",
	# Legacy
	"ps2",
	"ps1",
	"xbox",
	"wii",
	"ds",
	"gamecube",
	"n64",
	"gba",
	"psp",
	"dreamcast",
}


def get_game_list(platform):
	params = {
		"page": 0,
	}
	while True:
		path = METACRITIC_ROOT + GAME_RELEASES_ROOT % {"platform": platform}
		print("Querying path", path, params)
		r = requests.get(path, params=params)
		soup = bs4.BeautifulSoup(r.text)
		print(soup)
		last_page = int(soup.select(".last_page").text)
		params["page"] += 1
		if params["page"] == (last_page - 1):
			break
		break


print(get_game_list("pc"))
