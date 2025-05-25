import pandas as pd

# <- Passe den Dateinamen ggf. an
df = pd.read_csv("data/airquality_2016-01-01_2016-01-02_clean.csv")

# Gewünschte Spalten auswählen
columns_to_keep = [
    "Station ID",
    "Station Longitude",
    "Station Latitude",
    "datetime",
    "Component Name",
    "Value"
]
filtered_df = df[columns_to_keep]

column_rename_map = {
    "Station ID": "station-id",
    "Station Longitude": "longitude",
    "Station Latitude": "latitude",
    "datetime": "datetime",
    "Component Name": "component",
    "Value": "value"
}
filtered_df = filtered_df.rename(columns=column_rename_map)


# Neue Datei speichern
filtered_df.to_csv("filtered_data.csv", index=False)

print("Neue Datei 'filtered_data.csv' wurde erfolgreich erstellt.")
