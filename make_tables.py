import pandas as pd
import json

def convert_file(path, out_path):
    with open(path) as f:
        lines = f.readlines()

    jlines = [json.loads(line) for line in lines]

    df = pd.DataFrame(jlines)

    df.to_csv(out_path, index=False)

convert_file("player_history.jl", "player_history.csv")
convert_file("player.jl", "player.csv")