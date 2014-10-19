#!/usr/bin/env python
import requests
import requests_cache


# Cache all requests
requests_cache.install_cache()

API_ROOT = "https://www.gog.com"
API_GAMES_PATH = "/games/ajax/filtered"
API_REVIEWS_PATH = "/reviews/product/%(id)i.json"


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


def get_reviews(id):
	path = API_ROOT + API_REVIEWS_PATH % {"id": id}
	params = {
		"page": 1,
	}
	reviews = []
	while True:
		print("Querying path", path, params)
		r = requests.get(path, params=params)
		data = r.json()
		reviews += data["reviews"]
		if params["page"] >= data["totalPages"]:
			break

		params["page"] += 1

	return reviews

if __name__ == "__main__":
	games = get_games()
	for game in games:
		print(len(get_reviews(game["id"])), "reviews for", game["title"])
