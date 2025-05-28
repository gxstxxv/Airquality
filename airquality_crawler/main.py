import requests
import csv

BASE_URL = "https://www.umweltbundesamt.de/api/air_data/v3"
AIRQUALITY_ENDPOINT = "airquality"
META_ENDPOINT = "meta"
OUTPUT_FILENAME = "airquality_.csv"

# Define CSV headers
headers = [
    "Station ID",
    "Station Shortname",
    "Station City",
    "Station Street",
    "Station Postcode",
    "Station Longitude",
    "Station Latitude",
    "Urbanization Type",
    "Start Datetime",
    "End Datetime",
    "Airquality index (All components)",
    "Data incomplete",
    "Component ID",
    "Component Name",
    "Value",
    "Airquality index (Component)",
    "Decimal Airquality index (Component)"
]


def get_metadata():
    res = requests.get(f"{BASE_URL}/{META_ENDPOINT}/json",
                       params={"use": "airquality",
                               "lang": "de",
                               "date_from": "2019-01-01",
                               "date_to": "2019-01-01",
                               "time_from": "0",
                               "time_to": "0"
                               })
    res.raise_for_status()
    return res.json()


meta = get_metadata()


def get_airquality_data(station_id: int):
    res = requests.get(f"{BASE_URL}/{AIRQUALITY_ENDPOINT}/json",
                       params={"date_from": "2024-01-01",
                               "date_to": "2025-01-01",
                               "time_from": "0",
                               "time_to": "0",
                               "station": station_id
                               })
    res.raise_for_status()
    return res.json()

# Create safe dictionary mappings


def safe_get(lst, idx):
    return lst[idx] if idx < len(lst) else ""


def map_data(airquality_data, metadata):
    components_mapping = metadata["components"]
    stations_mapping = metadata["stations"]

    # Map component IDs to names
    id_to_component_name = {
        int(comp_id): comp_info[1]
        for comp_id, comp_info in components_mapping.items()
    }

    station_id_to_info = {
        str(station_id): {
            "Station Shortname": safe_get(station_info, 1),
            "Station City": safe_get(station_info, 3),
            "Station Street": safe_get(station_info, 17),
            "Station Postcode": safe_get(station_info, 19),
            "Station Longitude": safe_get(station_info, 7),
            "Station Latitude": safe_get(station_info, 8),
            # or 15 for the shorter term
            "Urbanization Type": safe_get(station_info, 14)
        }
        for station_id, station_info in stations_mapping.items()
    }

    # Prepare CSV rows
    csv_rows = []

    # Parse the data
    for station_id, station_data in airquality_data["data"].items():
        station_info = station_id_to_info.get(station_id, {
            "Station Shortname": "",
            "Station City": "",
            "Station Street": "",
            "Station Postcode": "",
            "Station Longitude": "",
            "Station Latitude": "",
            "Urbanization Type": ""
        })

        for start_time, measurements in station_data.items():
            end_time = measurements[0]
            airquality_index_all = measurements[1]
            data_incomplete = measurements[2]
            components = measurements[3:]

            for comp in components:
                component_id, value, component_index, decimal_index = comp

            row = {
                "Station ID": station_id,
                "Station Shortname": station_info["Station Shortname"],
                "Station City": station_info["Station City"],
                "Station Street": station_info["Station Street"],
                "Station Postcode": station_info["Station Postcode"],
                "Station Longitude": station_info["Station Longitude"],
                "Station Latitude": station_info["Station Latitude"],
                "Urbanization Type": station_info["Urbanization Type"],
                "Start Datetime": start_time,
                "End Datetime": end_time,
                "Airquality index (All components)": airquality_index_all,
                "Data incomplete": data_incomplete,
                "Component ID": component_id,
                "Component Name": id_to_component_name.get(component_id, f"Unknown-{component_id}"),
                "Value": value,
                "Airquality index (Component)": component_index,
                "Decimal Airquality index (Component)": decimal_index
            }
            csv_rows.append(row)

    return csv_rows


def init_csv():
    """Initialize the CSV file by overwriting and writing the header."""
    with open(OUTPUT_FILENAME, "w", newline="", encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=headers)
        writer.writeheader()


def write_to_csv(mapped_data):
    """Append data rows to the CSV file, without rewriting the header."""
    with open(OUTPUT_FILENAME, "a", newline="", encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=headers)
        for row in mapped_data:
            writer.writerow(row)


init_csv()
try:
    # Loop and append data to CSV
    print(len(list(meta["stations"])))
    for key in list(meta["stations"]):
        airquality_response = get_airquality_data(key)
        mapped_data = map_data(airquality_response, meta)
        write_to_csv(mapped_data)
        print(f"Successfully written data of station: {key} to CSV!")
except Exception as e:
    print(f"An error occurred: {e}")
