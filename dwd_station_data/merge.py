import pandas as pd
import os

CSV_FILES = [
    "data/weather_2024-01-01_2024-02-01.csv",
    "data/weather_2024-02-01_2024-03-01.csv",
    "data/weather_2024-03-01_2024-04-01.csv",
    "data/weather_2024-04-01_2024-05-01.csv",
    "data/weather_2024-05-01_2024-06-01.csv",
    "data/weather_2024-06-01_2024-07-01.csv",
    "data/weather_2024-07-01_2024-08-01.csv",
    "data/weather_2024-08-01_2024-09-01.csv",
    "data/weather_2024-09-01_2024-10-01.csv",
    "data/weather_2024-10-01_2024-11-01.csv",
    "data/weather_2024-11-01_2024-12-01.csv",
    "data/weather_2024-12-01_2025-01-01.csv",
]

OUTPUT_FILE = "weather_2024-01-01_2025-01-01.csv"

dataframes = []

for file in CSV_FILES:
    df = pd.read_csv(file)
    dataframes.append(df)

df = pd.concat(dataframes, ignore_index=True)

df.to_csv(OUTPUT_FILE, index=False)
