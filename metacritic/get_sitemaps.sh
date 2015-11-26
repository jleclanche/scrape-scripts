command='import ssmp
for sitemap in ssmp.SiteMapIndex("http://www.metacritic.com/siteindex.xml").get_sitemaps():
	print(sitemap.url)'

urls=$(python -c "$command")

wget --user-agent="BulletBot/0.1" -x -nH $urls
