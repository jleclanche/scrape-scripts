#!/usr/bin/env python
import requests
import requests_cache


# Cache all requests
requests_cache.install_cache()

API_ROOT = "https://www.gog.com"
API_GAMES_PATH = "/games/ajax/filtered"


def get_games():
	path = API_ROOT + API_GAMES_PATH
	params = {
		"page": 1,
	}
	games = []
	while True:
		print("Querying path", path, params)
		r = requests.get(path, params=params)
		data = r.json()
		games += data["products"]
		if params["page"] >= data["totalPages"]:
			break

		params["page"] += 1

	return games

if __name__ == "__main__":
	games = get_games()
	#print(games, len(games))
