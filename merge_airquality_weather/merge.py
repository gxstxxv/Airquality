import pandas as pd
import geopandas as gpd

airquality_csv = "data/airquality_2016-01-01_2016-01-02_clean_short.csv"
weather_csv = "data/wetterdaten_2016-01-01_2016-01-02_clean_short.csv"

print("Einlesen und Vorverarbeitung")
weather_cols = [
    'station_id',
    'component',
    'value',
    'latitude',
    'longitude',
    'datetime',
]
weather_dtypes = {
    'station_id':       'category',
    'component':        'category',
    'value':            'float32',
    'latitude':         'float32',
    'longitude':        'float32'
}
weather_df = pd.read_csv(
    weather_csv,
    usecols=weather_cols,
    dtype=weather_dtypes,
    parse_dates=['datetime'],
    low_memory=False,
    on_bad_lines='warn',
)

air_cols = [
    'station-id',
    'longitude',
    'latitude',
    'datetime',
    'component',
    'value',
]
air_dtypes = {
    'station-id':       'int32',
    'longitude':        'float32',
    'latitude':         'float32',
    'component':        'category',
    'value':            'float32'
}
air_df = pd.read_csv(
    airquality_csv,
    usecols=air_cols,
    dtype=air_dtypes,
    parse_dates=['datetime'],
    low_memory=False,
    on_bad_lines='warn',
)

print("GeoDataFrames erstellen (EPSG:4326)")
air_gdf = gpd.GeoDataFrame(
    air_df,
    geometry=gpd.points_from_xy(
        air_df["longitude"], air_df["latitude"]
    ),
    crs="EPSG:4326",
)
weather_gdf = gpd.GeoDataFrame(
    weather_df,
    geometry=gpd.points_from_xy(
        weather_df["longitude"], weather_df["latitude"]),
    crs="EPSG:4326",
)

print("In Meter-Projektion transformieren")
air_gdf = air_gdf.to_crs(epsg=3857)
weather_gdf = weather_gdf.to_crs(epsg=3857)

print("Buffer und Punktgeometrie speichern")
buffer_radius = 20000
air_gdf["geometry_point"] = air_gdf.geometry
air_gdf["geometry"] = air_gdf["geometry_point"].buffer(buffer_radius)

print("Spatial Join")
joined = gpd.sjoin(
    weather_gdf,
    air_gdf.set_geometry("geometry")[["geometry", "geometry_point"]],
    how="inner",
    predicate="within",
)

print("Distanz und Gewichtungen berechnen")
joined["distance_m"] = joined.geometry.distance(joined["geometry_point"])
epsilon = 1e-3
joined["weight"] = 1.0 / (joined["distance_m"] + epsilon)

print("Weighted Aggregation pro Luftstation & Stunde")
weather_vars = [
    'temperature_air',
    'cloudiness',
    'moisture',
    'precipitation',
    'sun',
    'visibility',
    'wind'
]
to_agg = {}
for var in weather_vars:
    joined[f'weighted_{var}'] = joined[var] * joined['weight']
    to_agg[f'weighted_{var}'] = 'sum'
to_agg['weight'] = 'sum'

agg = (
    joined
    .groupby(['index_right', 'datetime'])
    .agg(to_agg)
    .reset_index()
)

for var in weather_vars:
    agg[f'{var}_wmean'] = agg[f'weighted_{var}'] / agg['weight']


print("Merge")
result = (
    air_df.reset_index()
    .merge(
        agg[['index_right', 'datetime'] +
            [f'{var}_wmean' for var in weather_vars]],
        left_on=['index', 'datetime'],
        right_on=['index_right', 'datetime'],
        how='left'
    )
    .drop(columns=["index_right"])
)

print("Speichern")
result.to_csv("air_weather_merged_weighted.csv", index=False)
print("Weighted Merge abgeschlossen: "
      + "'air_weather_merged_weighted.csv' erstellt.")
