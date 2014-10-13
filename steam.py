#!/usr/bin/env python
import bs4
import requests
import requests_cache


# Cache all requests
requests_cache.install_cache()

API_ROOT = "https://api.steampowered.com"
STORE_API_ROOT = "https://store.steampowered.com"

CURATORS_PATH = "/curators/ajaxgetcurators/render/"
CURATORS_RECOMMENDATIONS_PATH = "/curators/ajaxgetcuratorrecommendations/%(id)i/"
APP_LIST_PATH = "/ISteamApps/GetAppList/v2"
APP_DETAILS_PATH = "/api/appdetails/"


def get_apps():
	path = API_ROOT + APP_LIST_PATH
	r = requests.get(path)
	data = r.json()
	return data["applist"]["apps"]


def get_app_details(*appids):
	path = STORE_API_ROOT + APP_DETAILS_PATH
	params = {"appids": ",".join(appids)}
	r = requests.get(path)
	data = r.json()
	return data


def get_recommendations(id):
	params = {
		"start": 0,
		"count": 50,
	}
	html = []
	while True:
		path = STORE_API_ROOT + CURATORS_RECOMMENDATIONS_PATH % {"id": id}
		print("Querying path", path)
		r = requests.get(path, params=params)
		data = r.json()
		html.append(data["results_html"])
		params["start"] += params["count"]
		if params["start"] >= data["total_count"]:
			break

	html = "".join(html)
	soup = bs4.BeautifulSoup(html)
	recommendations = soup.select(".recommendation")
	j_recommendations = []
	for rec in recommendations:
		readmore = rec.select(".recommendation_readmore")
		stats = rec.select(".recommendation_stats")[0].find_all("div")
		likes = 0
		comments = 0
		date = ""
		for div in stats:
			if div.get("class") == "recommendation_stat":
				img = div.img
				if img["src"].endswith("icon_btn_rateup.png"):
					likes = int(div.text.strip())
				elif img["src"].endswith("comment_quoteicon.png"):
					comments = int(div.text.strip())
			else:
				date = div.text.strip().lstrip("Recommended: ")
		j_recommendations.append({
			"appid": int(rec["data-ds-appid"]),
			"price": rec.select(".recommendation_app_price")[0].text.strip(),
			"name": rec.select(".recommendation_name")[0].text.strip(),
			"desc": rec.select(".recommendation_desc")[0].text.strip(),
			"readmore": readmore and readmore[0].a["href"],
			"comments": comments,
			"likes": likes,
			"date": date,
		})

	return j_recommendations


def get_curators():
	MAX_CURATORS_PER_PAGE = 50
	start = 0
	ret = {}
	while True:
		data, total_count = _get_curators(start, MAX_CURATORS_PER_PAGE)
		ret.update(data)
		start += MAX_CURATORS_PER_PAGE
		if start > total_count:
			break
	return ret


def _get_curators(start, count):
	ret = {}
	params = {
		# "query": "",
		"start": start,
		"count": count,
		#"filter": "all",
	}
	path = STORE_API_ROOT + CURATORS_PATH
	print("Querying", path, params)
	r = requests.get(path, params=params)
	data = r.json()
	soup = bs4.BeautifulSoup(data["results_html"])
	curators = soup.select(".steam_curator_row_ctn")
	for curator in curators:
		id = int(curator.a["data-clanid"])
		href = curator.a["href"].strip()
		desc = curator.select(".steam_curator_desc")
		if not href:
			# bad data
			continue
		ret[id] = {
			"href": href,
			"num_followers": int(curator.select(".num_followers")[0].text.replace(",", "")),
			"name": curator.select(".steam_curator_name")[0].text,
			"desc": desc and desc[0].text.strip(),
			"avatar": curator.select("img.steam_curator_avatar")[0]["src"],
		}

	return ret, data["total_count"]


if __name__ == "__main__":
	for curator in get_curators():
		print(get_recommendations(curator))

# print(get_apps())
# print(get_recommendations(1370293))
