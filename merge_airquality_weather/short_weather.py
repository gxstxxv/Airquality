import pandas as pd

# <- Passe den Dateinamen ggf. an
df = pd.read_csv("data/wetterdaten_2016-01-01_2016-01-02_clean.csv")

# Gewünschte Spalten auswählen
columns_to_keep = [
    "station_id",
    "dataset",
    "value",
    "latitude",
    "longitude",
    "datetime",
]
filtered_df = df[columns_to_keep]

column_rename_map = {
    "station_id": "station_id",
    "dataset": "component",
    "value": "value",
    "latitude": "latitude",
    "longitude": "longitude",
    "datetime": "datetime",
}
filtered_df = filtered_df.rename(columns=column_rename_map)

# Neue Datei speichern
filtered_df.to_csv("filtered_data.csv", index=False)

print("Neue Datei 'filtered_data.csv' wurde erfolgreich erstellt.")
