
#DATE = 2020-02-24
DATE := $(shell date '+%Y-%m-%d' )
FILENAME := "data/${DATE}.json"
LOGFILENAME := "data/scrape-${DATE}.log"

scrape:
	echo "Scraping to ${FILENAME}"
	rm -f ${FILENAME}
	rm -f ${LOGFILENAME}
	scrapy crawl saalihokiee-games -o ${FILENAME} --logfile ${LOGFILENAME} --loglevel DEBUG
