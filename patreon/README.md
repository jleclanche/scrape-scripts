Patreon
=======

Scanner for https://www.patreon.com


### Running the scanner

- Run `./process.py --scrape` to preload a sufficient amount of pages to `_res/`
- Run `./process.py --get-creators _res/*` to find and download creators from `_res/` to `creators/`
- Run `./process.py --datamine creators` to parse all files in creators/ and output data in CSV format
