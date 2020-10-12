import scrapy
import re
from pprint import pprint

class GamesSpider(scrapy.Spider):
    name = "saalihokiee-games"

    re_whitespace = re.compile(r"\s+")

    def clean_whitespace(self, s):
        return self.re_whitespace.sub(" ", s)

    def rm_whitespace(self, s):
        return self.re_whitespace.sub("", s)

    def extract_players(self, tbl):
        rows = tbl.css("tr")
        players_array = []
        for tr in rows[1:]:
            cells = tr.css("td")
            vv = False
            k = False
            nr = int(self.rm_whitespace(cells[2].css("td::text").extract_first()))
            player_id = None

            if nr < 100:    # Normal player
                nimi = self.clean_whitespace(cells[3].css("a::text").extract_first())
                player_id = int(cells[3].css("a")[0].attrib["info"])
            else:           # Official
                content = cells[3].css("span span::text").extract_first()
                if content is None:
                    continue   # Empty cell
                nimi = self.clean_whitespace(content)

            if len(cells[0].css(".check")) == 1:
                vv = True
            if len(cells[1].css(".check")) == 1:
                k = True

            player = [vv, k, nr, nimi, player_id]
            players_array.append(player)

        return players_array

    def extract_goals(self, tbl):
        goals = []

        useful_rows = tbl.css("tr")[2:]
        header = ["Seis", "Aeg", "Nr", "Sööt", "Kood"]
        for row in useful_rows:
            cells = []
            for cell_content in row.css("td::text()"):
                cells.append(self.rm_whitespace(cell_content))

            goals.append({k: v for (k, v) in zip(header, cells)})



        pass  # TODO

    def start_requests(self):
        urls = [
            'http://saalihoki.ee/Events/Loppenud-mangud.aspx'
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse_page)

    def parse_page(self, response):
        table_rows = response.css("#sisu_content tr")

        for tr in table_rows[1:]:  # First row is header
            cells = tr.css("td")
            url = response.urljoin(cells[1].css("a::attr(href)").extract()[0])
            print(url)

            req = scrapy.Request(url=url, callback=self.parse_protocol)
            req.meta["cells"] = cells
            yield req

    def parse_protocol(self, response):
        cells = response.meta["cells"]

        game = {
            "meta": {
                "voistlus": cells[0].css("td::text").extract_first().strip(),
                "mang": cells[1].css("a::text").extract_first().strip(),
                "tulemus": cells[2].css("td::text").extract_first().strip(),
                "aeg": self.clean_whitespace(cells[3].css("td::text").extract_first().strip()),
                "koht": cells[4].css("td::text").extract_first().strip()
            },
            "a": {},
            "b": {}
        }

        print(game)

        # Teams
        game["a"]["name"] = response.css(".infotulp .header-home-small::text").extract_first().strip()
        game["b"]["name"] = response.css(".infotulp .header-visitor-small::text").extract_first().strip()

        # Players
        players_tbl_a = response.css("#sisu_Protokoll1_tblMeeskond1")[0]
        players_tbl_b = response.css("#sisu_Protokoll1_tblMeeskond2")[0]
        game["a"]["players"] = self.extract_players(players_tbl_a)
        game["b"]["players"] = self.extract_players(players_tbl_b)

        # Goals
        goals_tbl_a = response.css(".infotulp tr")[1].css("td")[0]
        goals_tbl_b = response.css(".infotulp tr")[1].css("td")[0]
        #game["a"]["goals"] = self.extract_goals(goals_tbl_a)
        #game["b"]["goals"] = self.extract_goals(goals_tbl_b)

        # Penalties

        # Timeouts

        # Goalies

        yield game

