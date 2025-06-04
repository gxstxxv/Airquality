import pandas as pd
import numpy as np
from sklearn.neighbors import BallTree
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
import cartopy.crs as ccrs
import cartopy.feature as cfeature

PM2_CSV_PATH = "data/pm2_2024-01-01_2025-01-01.csv"
PREC_CSV_PATH = "data/prec_2024-01-01_2025-01-01.csv"

EARTH_RADIUS_KM = 6371.0


def read_data(path):
    return pd.read_csv(
        path,
        parse_dates=["datetime"],
        dtype={"longitude": float, "latitude": float, "value": float}
    )


def get_station_coords(data):
    return (
        data[["latitude", "longitude"]]
        .drop_duplicates()
        .reset_index(drop=True)
        .copy()
    )


def to_rad(coords):
    return np.deg2rad(coords[["latitude", "longitude"]].values)


def get_each_nearest_point(tree, coords):
    distances, indices = tree.query(coords, k=1)
    return ((distances.flatten()) * EARTH_RADIUS_KM), indices.flatten()


def assign_indices_to_data(data, coords):
    return data.merge(
        coords[["latitude", "longitude", "prec_index"]],
        on=["latitude", "longitude"],
        how="left"
    )


def merge_data(pm2_data, prec_data):
    return pd.merge(
        left=pm2_data,
        right=prec_data[["prec_index", "datetime", "prec"]],
        on=["prec_index", "datetime"],
        how="inner",
        suffixes=("_pm2", "_prec")
    )


def get_daily_mean(data, component, column_name):
    return (
        data
        .groupby([
            "latitude",
            "longitude",
            "prec_index",
            "date",
        ], as_index=False)[component]
        .mean()
        .rename(columns={component: column_name})
    )


def get_daily_sum(data, component, column_name):
    return (
        data
        .groupby([
            "latitude",
            "longitude",
            "prec_index",
            "date",
        ], as_index=False)[component]
        .sum()
        .rename(columns={component: column_name})
    )


def get_daily_combined_of(index, data):
    return data[data["prec_index"] == index]


def get_all_unique_indices(data):
    return data["prec_index"].drop_duplicates()


def combine_daily_data(pm2_data, prec_data):
    return pd.merge(
        pm2_data,
        prec_data,
        on=["latitude",
            "longitude",
            "prec_index",
            "date",
            ],
        how="inner"
    )


def get_aggregation_all_indices(data):
    return (
        data
        .groupby("date", as_index=False)
        .agg({
            "daily_mean_pm25": "mean",
            "daily_total_prec": "sum",
        })
    )


def display_combined_daily_data(data, title):
    dates = pd.to_datetime(data["date"])

    fig, ax1 = plt.subplots(figsize=(14, 6))

    ax1.plot(
        dates,
        data["daily_mean_pm25"],
        label="Daily Mean PM₂.₅ (µg/m³)",
        linewidth=1.5
    )
    ax1.set_xlabel("Date")
    ax1.set_ylabel("PM₂.₅ (µg/m³)")
    ax1.grid(True, which="both", linestyle="--", linewidth=0.5, alpha=0.7)

    ax2 = ax1.twinx()
    ax2.bar(
        dates,
        data["daily_total_prec"],
        width=0.8,
        alpha=0.3,
        label="Daily Total Precipitation (mm)"
    )
    ax2.set_ylabel("Precipitation (mm)")

    ax1.set_title(title)
    ax1.xaxis.set_tick_params(rotation=45)
    ax2.set_ylim(bottom=0)

    lines_1, labels_1 = ax1.get_legend_handles_labels()
    lines_2, labels_2 = ax2.get_legend_handles_labels()
    ax1.legend(lines_1 + lines_2, labels_1 + labels_2, loc="upper right")

    plt.tight_layout()
    plt.show()


def display_coords(data, title, label):
    latitude = data["latitude"]
    longitude = data["longitude"]

    plt.figure(figsize=(8, 10))
    ax = plt.axes(projection=ccrs.PlateCarree())

    ax.set_extent([5.5, 15.5, 47, 55], crs=ccrs.PlateCarree())

    ax.add_feature(cfeature.BORDERS)
    ax.add_feature(cfeature.COASTLINE)
    ax.add_feature(cfeature.STATES, linestyle=':')

    ax.set_aspect('auto')

    ax.scatter(longitude, latitude, color='red',
               s=20, transform=ccrs.PlateCarree(), label=label)

    plt.title(title)
    plt.legend(loc="upper right")
    plt.tight_layout()
    plt.show()


def display_multiple_coords(data_1, data_2, title, label_1, label_2):
    latitude_1 = data_1["latitude"]
    longitude_1 = data_1["longitude"]
    latitude_2 = data_2["latitude"]
    longitude_2 = data_2["longitude"]

    plt.figure(figsize=(8, 10))
    ax = plt.axes(projection=ccrs.PlateCarree())

    ax.set_extent([5.5, 15.5, 47, 55], crs=ccrs.PlateCarree())

    ax.add_feature(cfeature.BORDERS)
    ax.add_feature(cfeature.COASTLINE)
    ax.add_feature(cfeature.STATES, linestyle=':')

    ax.set_aspect('auto')

    ax.scatter(longitude_1, latitude_1, color='red',
               s=20, transform=ccrs.PlateCarree(),
               label=label_1)

    ax.scatter(longitude_2, latitude_2, color='blue',
               s=20, transform=ccrs.PlateCarree(),
               label=label_2)

    plt.title(title)
    plt.legend(loc="upper right")
    plt.tight_layout()
    plt.show()


def filter_coords_by_prec_index(prec_coords, pm2_coords):
    indices = pm2_coords["prec_index"].unique()

    return prec_coords_deg.loc[indices]


def save_data_frame(data, path):
    try:
        data.to_csv("output_frames/"+path, index=False)
        print(f"[INFO] created {path}")
    except Exception as e:
        print(f"[ERROR] {e}")


pm2_data, prec_data = (
    read_data(PM2_CSV_PATH).rename(columns={"value": "pm25"}),
    read_data(PREC_CSV_PATH).rename(columns={"value": "prec"}),
)

pm2_coords_deg, prec_coords_deg = (
    get_station_coords(pm2_data),
    get_station_coords(prec_data),
)
display_coords(
    pm2_coords_deg,
    "All PM₂.₅ Measurement Points Mapped on a Map of Germany",
    "PM₂.₅ Measurement Point",
)
save_data_frame(pm2_coords_deg, "pm2_station_coordinates.csv")

display_coords(
    prec_coords_deg,
    "All Precipitation Measurement Points Mapped on a Map of Germany",
    "Precipitation Measurement Point",
)
save_data_frame(prec_coords_deg, "prec_station_coordinates.csv")

pm2_coords_rad, prec_coords_rad = (
    to_rad(pm2_coords_deg),
    to_rad(prec_coords_deg),
)

tree = BallTree(prec_coords_rad, metric="haversine")

shortest_distances, nearest_point_indices = get_each_nearest_point(
    tree,
    pm2_coords_rad,
)

pm2_coords_deg["prec_index"] = nearest_point_indices
pm2_coords_deg["distance"] = shortest_distances

nearest_prec_points = filter_coords_by_prec_index(
    prec_coords_deg, pm2_coords_deg)

display_coords(
    nearest_prec_points,
    "Every Precipitation Measurement Point That's "
    + "Closest to a PM₂.₅ Measurement Point",
    "Precipitation Measurement Point",
)
save_data_frame(nearest_prec_points, "nearest_prec_station_coordinates.csv")

display_multiple_coords(
    pm2_coords_deg,
    nearest_prec_points,
    "Every PM₂.₅ Measurement Point and it's "
    + "Nearest Precipitation Measurement Point",
    "PM₂.₅ Measurement Point",
    "Precipitation Measurement Point",
)

prec_coords_deg = prec_coords_deg.reset_index().rename(
    columns={"index": "prec_index"})


pm2_data, prec_data = (
    assign_indices_to_data(pm2_data, pm2_coords_deg),
    assign_indices_to_data(prec_data, prec_coords_deg),
)

merged_data = merge_data(pm2_data, prec_data)
save_data_frame(merged_data, "merged_pm2_and_prec.csv")

merged_data["date"] = merged_data["datetime"].dt.date
pm2_daily_mean = get_daily_mean(
    merged_data,
    "pm25",
    "daily_mean_pm25",
)
prec_daily_sum = get_daily_sum(
    merged_data,
    "prec",
    "daily_total_prec",
)

daily_combined = combine_daily_data(pm2_daily_mean, prec_daily_sum)
save_data_frame(daily_combined, "daily_mean_pm2_and_sum_prec.csv")

prec_indices = get_all_unique_indices(daily_combined)

daily_all = get_aggregation_all_indices(daily_combined)

station_id = 728
filtered_daily_combined = get_daily_combined_of(station_id, daily_combined)

display_combined_daily_data(
    daily_all, "Time Series (2024): Daily Mean PM₂.₅ vs. "
    + "Daily Total Precipitation (Aggregation of all Stations)")
display_combined_daily_data(
    filtered_daily_combined, "Time Series (2024): Daily Mean PM₂.₅ vs. "
    + f"Daily Total Precipitation (Station: {station_id})")
