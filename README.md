


```
rm res.jl && scrapy crawl -O res.jl -t jl saalihokiee-players

grep player_history_item res.jl > player_history.jl
grep player_item res.jl > player.jl

~/miniconda3/bin/python make_tables.py

```