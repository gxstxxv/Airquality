import pandas as pd
import numpy as np
from scipy.spatial.distance import cdist
import warnings
warnings.filterwarnings('ignore')

# Daten laden
print("Lade bereinigte Datensätze...")
air_data = pd.read_csv('data/airquality_2016-01-01_2016-02-01_clean.csv')
weather_data = pd.read_csv(
    'data/wetterdaten_2016-01-01_2016-02-01_clean_short.csv')

print(f"Luftdaten: {len(air_data):,} Zeilen")
print(f"Wetterdaten: {len(weather_data):,} Zeilen")

# 1. Wetterdaten von Long zu Wide Format konvertieren
print("\n1. Konvertiere Wetterdaten zu Wide-Format...")

# Datetime sicherstellen
weather_data['datetime'] = pd.to_datetime(weather_data['datetime'])
air_data['datetime'] = pd.to_datetime(air_data['datetime'])

# Wetterdaten pivotieren: eine Zeile pro Station/Zeitpunkt, Komponenten als Spalten
weather_wide = weather_data.pivot_table(
    index=['station_id', 'datetime', 'latitude', 'longitude'],
    columns='component',
    values='value',
    aggfunc='first'  # Falls doppelte Einträge vorhanden
).reset_index()

# Spaltenname bereinigen
weather_wide.columns.name = None

print(f"Wetterdaten Wide-Format: {len(weather_wide):,} Zeilen")
print(f"Verfügbare Wetterkomponenten: {[col for col in weather_wide.columns if col not in [
      'station_id', 'datetime', 'latitude', 'longitude']]}")

# 2. Stationslisten erstellen
print("\n2. Erstelle Stationslisten...")

# Eindeutige Luftstationen
air_stations = air_data[['station_id',
                         'longitude', 'latitude']].drop_duplicates()
air_stations = air_stations.rename(columns={'station_id': 'air_station_id'})

# Eindeutige Wetterstationen
weather_stations = weather_wide[['station_id',
                                 'longitude', 'latitude']].drop_duplicates()
weather_stations = weather_stations.rename(
    columns={'station_id': 'weather_station_id'})

print(f"Luftstationen: {len(air_stations)}")
print(f"Wetterstationen: {len(weather_stations)}")

# 3. Räumliche Distanzen berechnen
print("\n3. Berechne räumliche Distanzen...")


def haversine_distance(lat1, lon1, lat2, lon2):
    """Berechnet Haversine-Distanz zwischen zwei Koordinatenpaaren in km"""
    R = 6371  # Erdradius in km

    lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = np.sin(dlat/2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2)**2
    c = 2 * np.arcsin(np.sqrt(a))
    distance = R * c

    return distance


# Distanzmatrix berechnen
print("Berechne Distanzmatrix...")
air_coords = air_stations[['latitude', 'longitude']].values
weather_coords = weather_stations[['latitude', 'longitude']].values

# Für jede Luftstation die Distanzen zu allen Wetterstationen
distances = cdist(air_coords, weather_coords,
                  lambda u, v: haversine_distance(u[0], u[1], v[0], v[1]))

print(f"Distanzmatrix: {distances.shape}")
print(f"Minimale Distanz: {distances.min():.2f} km")
print(f"Maximale Distanz: {distances.max():.2f} km")
print(f"Durchschnittliche Distanz zur nächsten Wetterstation: {
      distances.min(axis=1).mean():.2f} km")

# 4. Für jede Luftstation die nächsten Wetterstationen finden
print("\n4. Finde nächste Wetterstationen...")

MAX_DISTANCE = 30  # km
N_NEAREST = 5

station_mapping = []

for i, air_station in air_stations.iterrows():
    air_id = air_station['air_station_id']

    # Distanzen zu allen Wetterstationen für diese Luftstation
    station_distances = distances[i]

    # Finde die nächsten Stationen innerhalb des Radius
    valid_indices = np.where(station_distances <= MAX_DISTANCE)[0]

    if len(valid_indices) == 0:
        # Falls keine Station im Radius, nimm die nächste
        valid_indices = [np.argmin(station_distances)]
        print(f"Warnung: Luftstation {
              air_id} hat keine Wetterstation im {MAX_DISTANCE}km Radius")

    # Sortiere nach Distanz und nimm die nächsten N
    sorted_indices = valid_indices[np.argsort(
        station_distances[valid_indices])][:N_NEAREST]

    for j, weather_idx in enumerate(sorted_indices):
        weather_id = weather_stations.iloc[weather_idx]['weather_station_id']
        distance = station_distances[weather_idx]
        weight = 1 / (distance + 0.1)  # +0.1 um Division durch 0 zu vermeiden

        station_mapping.append({
            'air_station_id': air_id,
            'weather_station_id': weather_id,
            'distance_km': distance,
            'weight': weight,
            'rank': j + 1
        })

mapping_df = pd.DataFrame(station_mapping)
print(f"Station-Mappings erstellt: {len(mapping_df)}")

# Gewichte normalisieren (pro Luftstation summieren sich Gewichte zu 1)
mapping_df['weight_normalized'] = mapping_df.groupby('air_station_id')['weight'].transform(
    lambda x: x / x.sum()
)

# Übersicht der Zuordnungen
print(f"\nZuordnungsstatistiken:")
mapping_stats = mapping_df.groupby('air_station_id').agg({
    'distance_km': ['count', 'min', 'max', 'mean'],
    'weather_station_id': 'count'
}).round(2)
mapping_stats.columns = ['num_weather_stations',
                         'min_dist', 'max_dist', 'avg_dist', 'count']
print(f"Durchschnittlich {mapping_stats['num_weather_stations'].mean(
):.1f} Wetterstationen pro Luftstation")
print(f"Durchschnittliche minimale Distanz: {
      mapping_stats['min_dist'].mean():.2f} km")

# 5. Interpolierte Wetterdaten erstellen
print("\n5. Erstelle interpolierte Wetterdaten...")


def interpolate_weather_data(air_station_id, datetime_target):
    """Interpoliert Wetterdaten für eine Luftstation zu einem bestimmten Zeitpunkt"""

    # Relevante Wetterstationen für diese Luftstation
    relevant_mappings = mapping_df[mapping_df['air_station_id']
                                   == air_station_id]
    weather_station_ids = relevant_mappings['weather_station_id'].tolist()

    # Wetterdaten für diese Stationen zum Zielzeitpunkt
    weather_subset = weather_wide[
        (weather_wide['station_id'].isin(weather_station_ids)) &
        (weather_wide['datetime'] == datetime_target)
    ].copy()

    if len(weather_subset) == 0:
        return None

    # Merge mit Gewichten
    weather_subset = weather_subset.merge(
        relevant_mappings[['weather_station_id', 'weight_normalized']],
        left_on='station_id',
        right_on='weather_station_id'
    )

    # Interpolation für jede Wetterkomponente
    interpolated = {'air_station_id': air_station_id,
                    'datetime': datetime_target}

    weather_components = [col for col in weather_wide.columns
                          if col not in ['station_id', 'datetime', 'latitude', 'longitude']]

    for component in weather_components:
        if component in weather_subset.columns:
            # Gewichteter Durchschnitt (nur für nicht-NaN Werte)
            valid_data = weather_subset[weather_subset[component].notna()]
            if len(valid_data) > 0:
                interpolated[component] = (
                    valid_data[component] * valid_data['weight_normalized']).sum() / valid_data['weight_normalized'].sum()
            else:
                interpolated[component] = np.nan

    return interpolated


# Eindeutige Zeitpunkte aus Luftdaten
unique_times = sorted(air_data['datetime'].unique())
unique_air_stations = air_data['station_id'].unique()

print(f"Interpoliere für {len(unique_air_stations)} Luftstationen und {
      len(unique_times)} Zeitpunkte...")

# Batch-Verarbeitung für bessere Performance
interpolated_data = []
batch_size = 1000

for i in range(0, len(unique_times), batch_size):
    batch_times = unique_times[i:i+batch_size]

    for air_station in unique_air_stations:
        for time_point in batch_times:
            result = interpolate_weather_data(air_station, time_point)
            if result is not None:
                interpolated_data.append(result)

    if i % (batch_size * 10) == 0:
        print(f"Verarbeitet: {i}/{len(unique_times)} Zeitpunkte")

interpolated_weather = pd.DataFrame(interpolated_data)
print(f"\nInterpolierte Wetterdaten: {len(interpolated_weather):,} Zeilen")

# 6. Zusammenführen mit Luftdaten
print("\n6. Führe Luft- und Wetterdaten zusammen...")

# Merge
combined_data = air_data.merge(
    interpolated_weather,
    left_on=['station_id', 'datetime'],
    right_on=['air_station_id', 'datetime'],
    how='inner'
)

print(f"Kombinierte Daten: {len(combined_data):,} Zeilen")
print(f"Erfolgreich gemergete Luftmessungen: {
      len(combined_data)/len(air_data)*100:.1f}%")

# 7. Datenqualität prüfen
print("\n7. Prüfe Datenqualität der kombinierten Daten...")

weather_components = [col for col in interpolated_weather.columns
                      if col not in ['air_station_id', 'datetime']]

print("Missing Values in Wetterkomponenten:")
for component in weather_components:
    if component in combined_data.columns:
        missing_pct = combined_data[component].isnull().mean() * 100
        print(f"  {component}: {missing_pct:.1f}%")

# 8. Speichern
combined_data.to_csv('combined_air_weather_jan2016.csv', index=False)
mapping_df.to_csv('station_mapping.csv', index=False)

print(f"\n=== RÄUMLICHE ZUORDNUNG ABGESCHLOSSEN ===")
print(f"Kombinierte Daten: {len(combined_data):,} Zeilen")
print(f"Zeitraum: {combined_data['datetime'].min()} bis {
      combined_data['datetime'].max()}")
print(f"Luftstationen: {combined_data['station_id'].nunique()}")
print(f"Luftkomponenten: {', '.join(combined_data['component'].unique())}")
print(f"Wetterkomponenten: {', '.join(
    [c for c in weather_components if c in combined_data.columns])}")
print(f"\nGespeicherte Dateien:")
print(f"- combined_air_weather_jan2016.csv")
print(f"- station_mapping.csv")
