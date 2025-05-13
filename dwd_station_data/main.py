from wetterdienst.provider.dwd.observation import (
    DwdObservationRequest,
    DwdObservationMetadata,
)
from wetterdienst import Settings
import csv

# station_meta_data = "../dwd_station_meta_data/data/station_meta_data.csv"
station_meta_data = "../dwd_station_meta_data/data/station_meta_data_head.csv"

station_id_list: list[str] = []

with open(station_meta_data, newline="", encoding="latin1") as csvfile:
    reader = csv.reader(csvfile, delimiter=";")
    _ = next(reader)
    for row in reader:
        station_id_list.append(row[0])

station_ids = tuple(station_id_list)

parameters = [
    ("hourly", "air_temperature", "temperature_air_mean_2m"),
    # ("hourly", "cloudiness", "cloud_cover_total"),
    # ("hourly", "moisture", "humidity_absolute"),
    # ("hourly", "precipitation", "precipitation_height"),
    # ("hourly", "sun", "sunshine_duration"),
    # ("hourly", "visibility", "visibility_range"),
    # ("hourly", "wind", "wind_speed"),
]

request = DwdObservationRequest(
    parameters=parameters,
    start_date="2024-05-11",
    end_date="2024-05-12",
)

stations = request.filter_by_station_id(station_id=station_ids)

for result in stations.values.query():
    print(result.to_csv())
