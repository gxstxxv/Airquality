import pandas as pd

INPUT_FILE = "./data/airquality_2024-01-01_2025-01-01.csv"
OUTPUT_FILE = "pm2_2024-01-01_2025-01-01.csv"
COMPONENT = "PM2"

df = pd.read_csv(INPUT_FILE)

df = df[df['Component Name'] == COMPONENT]

unique_stations = df['Station ID'].unique()
print(f"anzahl vorher: {len(unique_stations)}")

stations = []
for station in unique_stations:
    count = (df['Station ID'] == station).sum()
    if count > 8784:
        stations.append(str(int(station)))


print(f"anzahl nachher: {len(stations)}")

df = df[df['Station ID'].isin([int(s) for s in stations])]

columns_to_keep = [
    "Station Longitude",
    "Station Latitude",
    "Start Datetime",
    "Value",
]
filtered_df = df[columns_to_keep]

column_rename_map = {
    "Station Longitude": "longitude",
    "Station Latitude": "latitude",
    "Start Datetime": "datetime",
    "Value": "value",
}
filtered_df = filtered_df.rename(columns=column_rename_map)

filtered_df.to_csv(f"{OUTPUT_FILE}", index=False)

print(f"Neue Datei '{OUTPUT_FILE}' wurde erfolgreich erstellt.")
