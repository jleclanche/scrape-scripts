"""
The simple sitemap parser
"""
import lxml.etree
import requests
from dateutil.parser import parse as parse_utc


USER_AGENT = "PySSMP/0.1"
SM_NAMESPACE = "http://www.sitemaps.org/schemas/sitemap/0.9"

_namespaces = {"sitemap": SM_NAMESPACE}


class SiteMapBase(object):
	def __init__(self, url, user_agent=USER_AGENT):
		self.url = url
		self.user_agent = user_agent

	@property
	def tree(self):
		if not hasattr(self, "_tree"):
			headers = {"User-Agent": self.user_agent}
			self.r = requests.get(self.url, headers=headers)
			self._tree = lxml.etree.fromstring(self.r.content)
		return self._tree


class SiteMapIndex(SiteMapBase):
	def get_sitemaps(self):
		ret = []
		for sitemap in self.tree.xpath(".//sitemap:sitemap", namespaces=_namespaces):
			loc = sitemap.xpath("sitemap:loc", namespaces=_namespaces)[0]
			sm = SiteMap(loc.text.strip())
			ret.append(sm)
			lastmod = sitemap.xpath("sitemap:lastmod", namespaces=_namespaces)
			if lastmod:
				sm.lastmod = parse_utc(lastmod[0].text.strip())
		return ret


class SiteMap(SiteMapBase):
	@property
	def parsed(self):
		return hasattr(self, "_data")

	def parse(self):
		self._data = []
		for url in self.tree.xpath(".//sitemap:urlset", namespaces=_namespaces):
			d = {"loc": url.xpath("sitemap:loc")[0].text.strip()}

			lastmod = url.xpath("sitemap:lastmod", namespaces=_namespaces)
			if lastmod:
				d["lastmod"] = parse_utc(lastmod[0].text.strip())

			changefreq = url.xpath("sitemap:changefreq", namespaces=_namespaces)
			if changefreq:
				d["changefreq"] = changefreq[0].text.strip()

			priority = url.xpath("sitemap:priority", namespaces=_namespaces)
			if priority:
				d["priority"] = float(priority[0].text.strip())

			image = url.xpath("image")
			if image:
				d["image_loc"] = url.xpath("image/image:loc")[0]
				for tag in ("caption", "geo_location", "title", "license"):
					t = url.xpath("image/image:%s" % (tag))
					if t:
						d["image_%s" % (tag)] = t[0].text.strip()

			self._data.append(d)

	def get_urls(self):
		if not self.parsed:
			self.parse()
		return [url["loc"] for url in self._data]
