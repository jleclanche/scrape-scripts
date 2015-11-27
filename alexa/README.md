Scans a csv file of the format "rank,url". Queues jobs to download and gzip the
sources for the highest N, where N is the MAX setting.


Settings
--------

Change settings at the top of the `main.py` file.


Run
---

Launch a new worker with `rqworker`.

To start a new scan, run `./main.py`.

Do not launch scans more than once a day, otherwise conflicts may appear.


Notes
-----

Alexa top 1M available at: http://s3.amazonaws.com/alexa-static/top-1m.csv.zip
