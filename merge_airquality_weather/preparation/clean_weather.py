import pandas as pd

INPUT_FILE = "./data/weather_2024-01-01_2025-01-01.csv"
OUTPUT_FILE = "prec_2024-01-01_2025-01-01.csv"
COMPONENT = "precipitation"

df = pd.read_csv(INPUT_FILE)

df = df[df['dataset'] == COMPONENT]

unique_stations = df['station_id'].unique()
print(f"anzahl vorher: {len(unique_stations)}")

stations = []
for station in unique_stations:
    count = (df['station_id'] == station).sum()
    if count > 8784:
        stations.append(str(int(station)))


print(f"anzahl nachher: {len(stations)}")

df = df[df['station_id'].isin([int(s) for s in stations])]

columns_to_keep = [
    "longitude",
    "latitude",
    "date",
    "value",
]
df = df[columns_to_keep]

df['date'] = pd.to_datetime(df['date']).dt.strftime('%Y-%m-%d %H:%M:%S')

column_rename_map = {
    "longitude": "longitude",
    "latitude": "latitude",
    "date": "datetime",
    "value": "value",
}
df = df.rename(columns=column_rename_map)

df.to_csv(f"{OUTPUT_FILE}", index=False)

print(f"Neue Datei '{OUTPUT_FILE}' wurde erfolgreich erstellt.")
