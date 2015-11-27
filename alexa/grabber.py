import requests
import gzip


def grab_url(url, filename):
	resp = requests.get(url)
	with gzip.open(filename, "wb") as f:
		f.write(resp.content)
	return filename
