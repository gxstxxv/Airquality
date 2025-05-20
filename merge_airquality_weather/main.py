import pandas as pd
import geopandas as gpd
import numpy as np
from shapely.geometry import Point

# --- 1) Pfade zu deinen CSV-Dateien ---
air_quality_csv = "air_quality.csv"
weather_csv = "weather.csv"

# --- 2) Einlesen und Vorverarbeitung ---
# Luftqualitätsdaten
air_df = pd.read_csv(
    air_quality_csv,
    parse_dates=["Start Datetime", "End Datetime"],
    dayfirst=False,
)


# Wetterdaten
def parse_iso(iso_str):
    # Entfernt Zeitzone, falls vorhanden und konvertiert zu naive datetime
    return pd.to_datetime(iso_str).tz_convert(None)


weather_df = pd.read_csv(weather_csv, parse_dates=[
                         "date"], date_parser=parse_iso)

# Zeitstempel vereinheitlichen
air_df["datetime"] = air_df["Start Datetime"]
weather_df["datetime"] = weather_df["date"]

# --- 3) GeoDataFrames erstellen (EPSG:4326) ---
air_gdf = gpd.GeoDataFrame(
    air_df,
    geometry=gpd.points_from_xy(
        air_df["Station Longitude"], air_df["Station Latitude"]
    ),
    crs="EPSG:4326",
)
weather_gdf = gpd.GeoDataFrame(
    weather_df,
    geometry=gpd.points_from_xy(
        weather_df["longitude"], weather_df["latitude"]),
    crs="EPSG:4326",
)

# --- 4) In Meter-Projektion transformieren (für Puffer und Distanzmessung) ---
air_gdf = air_gdf.to_crs(epsg=3857)
weather_gdf = weather_gdf.to_crs(epsg=3857)

# --- 5) Buffer und Punktgeometrie speichern ---
buffer_radius = 20000  # Puffer-Radius in Metern (z.B. 20 km)
# Originalpunkt speichern
air_gdf["geometry_point"] = air_gdf.geometry
# Buffer-Geometrie als neue aktive Geometry
air_gdf["geometry"] = air_gdf["geometry_point"].buffer(buffer_radius)

# --- 6) Spatial Join: Wetterpunkte innerhalb der Buffer ---
joined = gpd.sjoin(
    weather_gdf,
    air_gdf.set_geometry("geometry")[["geometry", "geometry_point"]],
    how="inner",
    predicate="within",
)

# --- 7) Distanz und Gewichtungen berechnen ---
# Distanz (Meter) zwischen Wetterpunkt (joined.geometry) und Luftstation-Punkt (geometry_point)
joined["distance_m"] = joined.geometry.distance(joined["geometry_point"])
# Gewicht als inverse Distanz (mit kleinem Epsilon, um Division durch Null zu vermeiden)
epsilon = 1e-3
joined["weight"] = 1.0 / (joined["distance_m"] + epsilon)

# --- 8) Weighted Aggregation pro Luftstation & Stunde ---
# Beispiel für eine Spalte 'value' (z.B. wind_speed, precipitation_height, etc.)
joined["weighted_value"] = joined["value"] * joined["weight"]
agg = (
    joined.groupby(["index_right", "datetime"])
    .agg(weather_weighted_mean=("weighted_value", "sum"), weight_sum=("weight", "sum"))
    .reset_index()
)
# Finalen gewichteten Mittelwert berechnen
agg["weather_weighted_mean"] = agg["weather_weighted_mean"] / agg["weight_sum"]

# --- 9) Merge zurück mit Luftqualitätsdaten ---
result = (
    air_df.reset_index()
    .merge(
        agg[["index_right", "datetime", "weather_weighted_mean"]],
        left_on=["index", "datetime"],
        right_on=["index_right", "datetime"],
        how="left",
    )
    .drop(columns=["index_right"])
)

# --- 10) Ergebnis speichern ---
result.to_csv("air_weather_merged_weighted.csv", index=False)
print("Weighted Merge abgeschlossen: 'air_weather_merged_weighted.csv' erstellt.")
