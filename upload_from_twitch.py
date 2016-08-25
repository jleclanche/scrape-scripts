#!/usr/bin/env python
import json
import sys
from argparse import ArgumentParser
from datetime import datetime
from youtube_upload.main import main as upload_main


def get_uploader_args(meta):
	category = "Gaming"
	privacy = "unlisted"
	display_id = meta["display_id"]
	title = meta.get("title") or meta.get("fulltitle") or display_id
	description = meta.get("description") or ""

	ret = [
		"--title", title,
		"--description", description,
		"--category", category,
		"--privacy", privacy,
	]

	tags = [meta["extractor"], display_id]
	uploader = meta.get("uploader")
	if uploader:
		tags.append(uploader)
	ret += ["--tags", ", ".join(tags)]

	timestamp = meta.get("timestamp")
	if timestamp:
		ts = datetime.fromtimestamp(timestamp)
		ret += ["--recording-date", ts.isoformat() + ".0Z"]

	return ret


def main():
	p = ArgumentParser()
	p.add_argument("-j", "--json", help="JSON description file")
	p.add_argument("-n", "--dry-run", action="store_true", help="Do not run the uploader")
	p.add_argument("video")
	args = p.parse_args(sys.argv[1:])

	with open(args.json, "r") as f:
		upload_args = get_uploader_args(json.load(f))

	upload_args.append(args.video)
	print("Running with arguments: %r" % (upload_args))
	if not args.dry_run:
		upload_main(upload_args)

if __name__ == "__main__":
	main()
