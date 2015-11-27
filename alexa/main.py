#!/usr/bin/env python
import csv
import datetime
import os
import sys
from redis import Redis
from rq import Queue

from grabber import grab_url


queue = Queue(connection=Redis())
MAX = 50000
OUTDIR = "./results"
TIMEOUT = 15


def main():
	# create a new scan
	today = datetime.datetime.today().strftime("%Y%m%d")

	if len(sys.argv) < 2:
		print("USAGE: %s <top-1m.csv>" % (sys.argv[0]))
		return 1

	outdir = os.path.join(OUTDIR, today)
	if not os.path.exists(outdir):
		os.makedirs(outdir)

	with open(sys.argv[1]) as csvfile:
		reader = csv.reader(csvfile)

		for rank, urlbase in reader:
			rank = int(rank)

			if rank > MAX:
				break

			filename = "%i-%s.gz" % (rank, urlbase)
			filename = os.path.join(outdir, filename)

			print("Queuing %r (#%i)" % (urlbase, rank))
			result = queue.enqueue(grab_url, kwargs={
				"url": "http://%s" % (urlbase),
				"filename": filename,
			}, timeout=TIMEOUT)


if __name__ == "__main__":
	main()
