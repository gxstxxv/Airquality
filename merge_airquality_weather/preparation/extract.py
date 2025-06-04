import pandas as pd

INPUT_FILE = ""
OUTPUT_FILE = ""
COMPONENT = ""

df = pd.read_csv(INPUT_FILE)

df = df[df['component'] == COMPONENT]

df.to_csv(OUTPUT_FILE, index=False)

print(f"Datei gespeichert unter: {OUTPUT_FILE}")
