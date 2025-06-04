import pandas as pd

INPUT_FILE = ""

df = pd.read_csv(INPUT_FILE)

columns_to_keep = [
    "Station Longitude",
    "Station Latitude",
    "Start Datetime",
    "Component Name",
    "Value",
]
filtered_df = df[columns_to_keep]

column_rename_map = {
    "Station Longitude": "longitude",
    "Station Latitude": "latitude",
    "Start Datetime": "datetime",
    "Component Name": "component",
    "Value": "value",
}
filtered_df = filtered_df.rename(columns=column_rename_map)

filtered_df.to_csv(f"_{INPUT_FILE}", index=False)

print(f"Neue Datei '_{INPUT_FILE}' wurde erfolgreich erstellt.")
