import scrapy
import re

re_season = re.compile(r"Hooaeg\s+(20\d\d\s+\/\s+20\d\d)\s+-\s+(.*)")
re_name = re.compile(r"(.*)\,(.*)")
re_whitespace = re.compile(r"\s+")

class PlayersSpider(scrapy.Spider):
    name = "saalihokiee-players"

    def clean_whitespace(self, s):
        return re_whitespace.sub(" ", s).strip()

    def rm_whitespace(self, s):
        return re_whitespace.sub("", s)

    def start_requests(self):
        url_base = "https://www.saalihoki.ee/Meeskonnad/Mangija.aspx?id={}"
        for i in range(3285):
            url = url_base.format(i)
            yield scrapy.Request(url=url, callback=self.parse_page)

    def extract_player_history(self, league_rows, player_id):
        rows = league_rows[1:] # Ignore header row

        parsed_rows = []
        for row in rows:
            if len(row.css("th")) > 0:
                th_text = "".join(row.css("th ::text").extract())
                match = re_season.search(th_text)
                season = match.group(1)
                team = match.group(2)

                parsed_rows.append({
                    "type": "header",
                    "season": self.clean_whitespace(season),
                    "team": self.clean_whitespace(team),
                    "player_id": player_id
                })
            elif len(row.css("td")) > 0:
                # League
                league_name = row.css("td a::text")[0].get()

                # Stats
                stats_elems = row.css("td")[1:5]
                stats_list = [int(s.css("::text").get()) for s in stats_elems]

                parsed_rows.append({
                    "type": "stats",
                    "league_name": self.clean_whitespace(league_name),
                    "n_games": stats_list[0],
                    "n_goals": stats_list[1],
                    "n_passes": stats_list[2]
                })
            else:
                print("Unknown row")

        # Aggregate into one result per season-league
        split_indices = [i for (i, r) in enumerate(parsed_rows) if r["type"] == "header"]
        
        groups = []
        for start, end in zip(split_indices, split_indices[1:] + [len(parsed_rows)]):
            groups.append(parsed_rows[start:end])
        
        results = []
        for group in groups:
            header = group[0]
            rest = group[1:]

            result = header
            result.update({
                "item": "player_history_item",
                "league_name": rest[0]["league_name"],
                "n_games": sum([r["n_games"] for r in rest]),
                "n_goals": sum([r["n_goals"] for r in rest]),
                "n_passes": sum([r["n_passes"] for r in rest]),
            })
            del result["type"]

            results.append(result)

        return results

    def parse_page(self, response):
        table = response.css("table")[0]
        rows = table.css("tr")
        
        if len(rows) <= 1:
            return # Empty player page

        # Parse general data
        name_text = response.css("h1::text")[0].extract()
        match = re_name.search(name_text)
        name = match.group(1)
        birthday = match.group(2)
        player_id = int(response.request.url.split("=")[-1])

        res_player = {
            "player_id": player_id,
            "name": self.clean_whitespace(name),
            "birthday": self.clean_whitespace(birthday),
            "item": "player_item",
        }
        yield res_player

        player_history = self.extract_player_history(rows, player_id)
        yield from player_history

