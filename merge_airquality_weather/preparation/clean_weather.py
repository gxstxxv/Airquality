import pandas as pd

INPUT_FILE = ""

df = pd.read_csv(INPUT_FILE)

columns_to_keep = [
    "longitude",
    "latitude",
    "date",
    "dataset",
    "value",
]
df = df[columns_to_keep]

df['date'] = pd.to_datetime(df['date']).dt.strftime('%Y-%m-%d %H:%M:%S')

column_rename_map = {
    "longitude": "longitude",
    "latitude": "latitude",
    "date": "datetime",
    "dataset": "component",
    "value": "value",
}
df = df.rename(columns=column_rename_map)

df.to_csv(f"_{INPUT_FILE}", index=False)

print(f"Neue Datei '_{INPUT_FILE}' wurde erfolgreich erstellt.")
