import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt

# Daten laden
print("Lade Datensätze...")
air_data = pd.read_csv('data/airquality_2016-01-01_2016-01-02.csv')
weather_data = pd.read_csv('data/wetterdaten_2016-01-01_2016-01-02.csv')

print(f"Ursprüngliche Datensätze:")
print(f"Luftdaten: {len(air_data):,} Zeilen")
print(f"Wetterdaten: {len(weather_data):,} Zeilen")

# 1. Zeitstempel konvertieren und standardisieren
print("\n1. Zeitstempel verarbeiten...")

# Luftdaten: Start Datetime verwenden
air_data['datetime'] = pd.to_datetime(air_data['Start Datetime'])
air_data['date'] = air_data['datetime'].dt.date
air_data['hour'] = air_data['datetime'].dt.hour

# Wetterdaten: ISO Format konvertieren und Timezone entfernen
weather_data['datetime'] = pd.to_datetime(
    weather_data['date'], utc=True).dt.tz_localize(None)
weather_data['date'] = weather_data['datetime'].dt.date
weather_data['hour'] = weather_data['datetime'].dt.hour

print("Zeitstempel erfolgreich konvertiert (Zeitzonen normalisiert).")

# 2. Auf Januar 2016 filtern
print("\n2. Filtere auf Januar 2016...")

start_date = datetime(2016, 1, 1)
end_date = datetime(2016, 2, 1)

# Filter anwenden
air_jan = air_data[
    (air_data['datetime'] >= start_date) &
    (air_data['datetime'] < end_date)
].copy()

weather_jan = weather_data[
    (weather_data['datetime'] >= start_date) &
    (weather_data['datetime'] < end_date)
].copy()

print(f"Nach Zeitfilter:")
print(f"Luftdaten: {len(air_jan):,} Zeilen")
print(f"Wetterdaten: {len(weather_jan):,} Zeilen")

# 3. Datenqualität analysieren
print("\n3. Datenqualität analysieren...")

# Luftdaten Analyse
print("\nLuftdaten - Missing Values:")
air_missing = air_jan[['Station ID', 'Component Name',
                       'Value', 'Data incomplete']].isnull().sum()
print(air_missing)

print(
    f"\nLuftdaten - Unvollständige Messungen: {air_jan['Data incomplete'].sum():,}")
print(f"Anteil unvollständiger Daten: {air_jan['Data incomplete'].mean():.2%}")

# Verfügbare Komponenten
print(f"\nVerfügbare Luftqualitätskomponenten:")
components = air_jan['Component Name'].value_counts()
print(components)

# Anzahl Stationen
print(f"\nAnzahl Luftqualitätsstationen: {air_jan['Station ID'].nunique()}")

# Wetterdaten Analyse
print(f"\nWetterdaten - Missing Values:")
weather_missing = weather_jan[['station_id',
                               'parameter', 'value', 'quality']].isnull().sum()
print(weather_missing)

# Verfügbare Parameter
print(f"\nVerfügbare Wetterparameter:")
weather_params = weather_jan['parameter'].value_counts()
print(weather_params)

print(f"\nAnzahl Wetterstationen: {weather_jan['station_id'].nunique()}")

# 4. Zeitliche Verteilung visualisieren
print("\n4. Erstelle Übersichtsplots...")

fig, axes = plt.subplots(2, 2, figsize=(15, 10))

# Luftdaten pro Tag
air_daily = air_jan.groupby('date').size()
axes[0, 0].plot(air_daily.index, air_daily.values,
                marker='o', linewidth=1, markersize=3)
axes[0, 0].set_title('Luftqualitätsmessungen pro Tag')
axes[0, 0].set_xlabel('Datum')
axes[0, 0].set_ylabel('Anzahl Messungen')
axes[0, 0].tick_params(axis='x', rotation=45)

# Wetterdaten pro Tag
weather_daily = weather_jan.groupby('date').size()
axes[0, 1].plot(weather_daily.index, weather_daily.values,
                marker='o', linewidth=1, markersize=3)
axes[0, 1].set_title('Wettermessungen pro Tag')
axes[0, 1].set_xlabel('Datum')
axes[0, 1].set_ylabel('Anzahl Messungen')
axes[0, 1].tick_params(axis='x', rotation=45)

# Luftkomponenten Verteilung
components.plot(kind='bar', ax=axes[1, 0])
axes[1, 0].set_title('Verteilung Luftqualitätskomponenten')
axes[1, 0].set_xlabel('Komponente')
axes[1, 0].set_ylabel('Anzahl Messungen')
axes[1, 0].tick_params(axis='x', rotation=45)

# Wetterparameter Verteilung
weather_params.plot(kind='bar', ax=axes[1, 1])
axes[1, 1].set_title('Verteilung Wetterparameter')
axes[1, 1].set_xlabel('Parameter')
axes[1, 1].set_ylabel('Anzahl Messungen')
axes[1, 1].tick_params(axis='x', rotation=45)

plt.tight_layout()
plt.show()

# 5. Geografische Verteilung
print("\n5. Geografische Verteilung:")

# Luftstationen
air_stations = air_jan[['Station ID', 'Station Longitude',
                        'Station Latitude', 'Station City']].drop_duplicates()
print(f"Luftstationen - Lat/Lon Bereich:")
print(f"Latitude: {air_stations['Station Latitude'].min():.2f} bis {
      air_stations['Station Latitude'].max():.2f}")
print(f"Longitude: {air_stations['Station Longitude'].min():.2f} bis {
      air_stations['Station Longitude'].max():.2f}")

# Wetterstationen
weather_stations = weather_jan[['station_id',
                                'longitude', 'latitude']].drop_duplicates()
print(f"\nWetterstationen - Lat/Lon Bereich:")
print(f"Latitude: {weather_stations['latitude'].min():.2f} bis {
      weather_stations['latitude'].max():.2f}")
print(f"Longitude: {weather_stations['longitude'].min():.2f} bis {
      weather_stations['longitude'].max():.2f}")

# 6. Analyse der Datenqualität im Detail
print("\n6. Detaillierte Datenqualitätsanalyse...")

# Vollständigkeit pro Komponente
incomplete_analysis = air_jan.groupby(
    ['Component Name', 'Data incomplete']).size().unstack(fill_value=0)
print("Vollständige vs. unvollständige Daten pro Komponente:")
print(incomplete_analysis)

completeness = air_jan.groupby('Component Name').agg({
    'Data incomplete': ['count', 'sum'],
    'Value': ['count', lambda x: x.isnull().sum()]
}).round(3)
completeness.columns = ['total_records',
                        'incomplete_flag', 'total_values', 'missing_values']
completeness['complete_rate'] = (
    (completeness['total_records'] - completeness['incomplete_flag']) / completeness['total_records']).round(3)
completeness['value_availability'] = (
    (completeness['total_values'] - completeness['missing_values']) / completeness['total_values']).round(3)

print("\nVollständigkeitsraten:")
print(completeness)

# 7. Gelockerte Bereinigung
print("\n7. Gelockerte Datenbereinigung...")

# Strategie: Behalte alle Daten wo Value nicht null ist, unabhängig vom incomplete flag
air_jan_clean = air_jan[air_jan['Value'].notnull()].copy()

print(f"Luftdaten nach gelockerten Kriterien: {len(air_jan_clean):,} Zeilen")

# Zusätzliche Qualitätsprüfungen
print("\nQualitätsprüfungen nach Lockerung:")

# Negative Werte prüfen (könnten Messfehler sein)
negative_values = air_jan_clean[air_jan_clean['Value'] < 0]
print(f"Negative Werte: {len(negative_values)} ({
      len(negative_values)/len(air_jan_clean)*100:.2f}%)")

# Extreme Ausreißer prüfen (> 99.9 Percentile)
for component in air_jan_clean['Component Name'].unique():
    comp_data = air_jan_clean[air_jan_clean['Component Name']
                              == component]['Value']
    p99_9 = comp_data.quantile(0.999)
    outliers = comp_data[comp_data > p99_9]
    print(f"{component} - 99.9% Quantil: {p99_9:.1f}, Extreme Ausreißer: {len(outliers)}")

# Optional: Extreme Ausreißer entfernen (sehr konservativ)
print("\nEntferne nur extreme Ausreißer (>99.95% Quantil pro Komponente)...")
air_jan_final = air_jan_clean.copy()

for component in air_jan_clean['Component Name'].unique():
    mask = air_jan_final['Component Name'] == component
    comp_data = air_jan_final.loc[mask, 'Value']
    threshold = comp_data.quantile(0.9995)  # Sehr konservativ
    outlier_mask = (air_jan_final['Component Name'] == component) & (
        air_jan_final['Value'] > threshold)
    removed = outlier_mask.sum()
    air_jan_final = air_jan_final[~outlier_mask]
    if removed > 0:
        print(f"  {component}: {
              removed} extreme Ausreißer entfernt (>{threshold:.1f})")

print(f"\nFinale Luftdaten: {len(air_jan_final):,} Zeilen")

# Speichern
air_jan_final.to_csv('airquality_jan2016_clean.csv', index=False)
weather_jan.to_csv('weather_jan2016.csv', index=False)

print("\nDatenvorverarbeitung abgeschlossen!")
print("Gespeicherte Dateien:")
print("- airquality_jan2016_clean.csv")
print("- weather_jan2016.csv")

# Finale Zusammenfassung
print(f"\n=== FINALE ZUSAMMENFASSUNG ===")
print(f"Zeitraum: Januar 2016")
print(f"Luftdaten: {len(air_jan_final):,} bereinigte Messungen")
print(f"Wetterdaten: {len(weather_jan):,} Messungen")
print(f"Luftstationen: {air_jan_final['Station ID'].nunique()}")
print(f"Wetterstationen: {weather_jan['station_id'].nunique()}")

# Detaillierte Komponentenverteilung
print(f"\nLuftkomponenten nach Bereinigung:")
final_components = air_jan_final['Component Name'].value_counts()
for comp, count in final_components.items():
    percentage = count / len(air_jan_final) * 100
    print(f"  {comp}: {count:,} Messungen ({percentage:.1f}%)")

print(f"\nVerfügbare Wetterparameter: {
      ', '.join(weather_jan['parameter'].unique())}")

# Zeitliche Abdeckung prüfen
print(f"\nZeitliche Abdeckung:")
print(f"Luftdaten: {air_jan_final['datetime'].min()} bis {
      air_jan_final['datetime'].max()}")
print(f"Wetterdaten: {weather_jan['datetime'].min()} bis {
      weather_jan['datetime'].max()}")
