import scrapy
import re
from pprint import pprint

re_season = re.compile(r"Hooaeg\s+(20\d\d\s+\/\s+20\d\d)")

class PlayersSpider(scrapy.Spider):
    name = "saalihokiee-players"

    re_whitespace = re.compile(r"\s+")

    def clean_whitespace(self, s):
        return self.re_whitespace.sub(" ", s)

    def rm_whitespace(self, s):
        return self.re_whitespace.sub("", s)

    def start_requests(self):
        url_base = "https://www.saalihoki.ee/Meeskonnad/Mangija.aspx?id={}"
        for i in range(3285):
            url = url_base.format(i)
            yield scrapy.Request(url=url, callback=self.parse_page)

    def parse_page(self, response):
        table = response.css("table")[0]
        rows = table.css("tr")[1:] # Ignore header row

        for row in rows:
            if len(row.css("th")) > 0:
                th_text = row.css("th::text")[0].get()
                season_str = re_season.search(th_text).group(1)
            elif len(row.css("td")) > 0:
                stats_elems = row.css("td")[1:5]
                stats_list = [int(s.css("::text").get()) for s in stats_elems]
                stats = {
                    "n_games": stats_list[0],
                    "n_goals": stats_list[1],
                    "n_passes": stats_list[2]
                }

            else:
                print("Unknown row")
