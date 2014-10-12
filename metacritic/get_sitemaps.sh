command='import ssmp
for sitemap in ssmp.SiteMapIndex("http://www.metacritic.com/siteindex.xml").get_sitemaps():
	print(sitemap.url)'

urls=$(python -c "$command")

for url in $urls; do
	wget --user-agent="BulletBot/0.1" $url
done
