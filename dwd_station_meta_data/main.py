import re
from glob import glob
import pandas as pd

paths = glob("data/hourly/**/*.csv", recursive=True)


def replace_whitespaces(line: str):
    line = line.rstrip()

    left_split = re.split(r"\s+", line, maxsplit=6)
    line_left = ";".join(left_split)

    if line.strip().endswith("Frei"):
        reversed_line = line_left[::-1]
        right_split = re.split(r"\s+", reversed_line, maxsplit=2)
        line_final = ";".join(right_split)[::-1]
    else:
        reversed_line = line_left[::-1]
        right_split = re.split(r"\s+", reversed_line, maxsplit=1)
        line_final = ";".join(right_split)[::-1]
        line_final += ";"

    return line_final


lines: dict[str, str] = {}

for path in paths:
    with open(path, "r", encoding="latin1", newline="") as file:
        i = 0
        for line in file:
            if i > 1:
                line = replace_whitespaces(line)
                station_id = line.split(";")[0]
                lines[station_id] = line
            i += 1


attr = "Stations_id;von_datum;bis_datum;Stationshoehe;" + \
    "geoBreite;geoLaenge;Stationsname Bundesland;Abgabe\n"

with open(
    "data/station_meta_data.csv",
    "w",
    encoding="latin1",
    newline="",
) as outfile:
    _ = outfile.write(attr)
    for line in sorted(lines.values()):
        _ = outfile.write(line + "\n")

df = pd.read_csv("data/station_meta_data.csv", sep=";", encoding="latin1")

print(df.head())
