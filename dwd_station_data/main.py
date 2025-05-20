from wetterdienst.provider.dwd.observation import DwdObservationRequest
from wetterdienst import Settings
import csv

station_meta_data = "../dwd_station_meta_data/data/station_meta_data.csv"
# station_meta_data = "../dwd_station_meta_data/data/station_meta_data_head.csv"

station_meta = {}

with open(station_meta_data, newline="", encoding="latin1") as f:
    reader = csv.reader(f, delimiter=";")
    header = next(reader)
    for row in reader:
        station_id, latitude, longitude = row[0], row[4], row[5]
        station_meta[station_id] = (latitude, longitude)

station_ids = tuple(station_meta.keys())

settings = Settings(
    cache_disable=True,
    fsspec_client_kwargs={"trust_env": True},
    ts_skip_empty=True,
)

parameters = [
    ("hourly", "air_temperature", "temperature_air_mean_2m"),
    ("hourly", "cloudiness", "cloud_cover_total"),
    ("hourly", "moisture", "humidity_absolute"),
    ("hourly", "precipitation", "precipitation_height"),
    ("hourly", "sun", "sunshine_duration"),
    ("hourly", "visibility", "visibility_range"),
    ("hourly", "wind", "wind_speed"),
]

request = DwdObservationRequest(
    parameters=parameters,
    # start_date="2016-01-01",
    # end_date="2025-05-12",
    start_date="2025-01-01",
    end_date="2025-02-01",
    settings=settings,
)

stations = request.filter_by_station_id(station_id=station_ids)

output_file = "wetterdaten.csv"

with open(output_file, "w", encoding="utf-8", newline="") as f:
    first = True

    for result in stations.values.query():
        csv_str = result.to_csv()

        lines = [line.strip() for line in csv_str.splitlines() if line.strip()]
        if len(lines) < 2:
            continue

        print(f"{lines[1][:5]}")

        station_id = lines[1].split(",")[0]
        latitude, longitude = station_meta.get(station_id, ("", ""))

        if first:
            header_line = lines[0] + ",latitude,longitude"
            f.write(header_line)
            first = False

        for line in lines[1:]:
            f.write("\n" + line + f",{latitude},{longitude}")


print(f"CSV-Datei '{output_file}' wurde erfolgreich erstellt.")
