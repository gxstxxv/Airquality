# Ursprüngliche Datensätze:

Luftdaten: 308,453 Zeilen
Wetterdaten: 2,263,648 Zeilen

# Nach Zeitfilter:

Luftdaten: 301,842 Zeilen
Wetterdaten: 2,260,838 Zeilen

# Luftdaten

## Missing Values:

Station ID 0
Component Name 0
Value 0
Data incomplete 0

## Unvollständige Messungen:

Anzahl unvollständiger Daten: 259,697
Anteil unvollständiger Daten: 86.04%

## Verfügbare Luftqualitätskomponenten:

Data incomplete      0       1
Component Name
NO2                  0  186054
O3                   0   16053
PM10                 0    3369
PM2              42145   54221

### Vollständigkeitsraten:

                total_records  incomplete_flag  total_values  missing_values  complete_rate  value_availability
Component Name
NO2                    186054           186054        186054               0          0.000                 1.0
O3                      16053            16053         16053               0          0.000                 1.0
PM10                     3369             3369          3369               0          0.000                 1.0
PM2                     96366            54221         96366               0          0.437                 1.0

## Luftdaten nach gelockerten Kriterien:

Anzahl: 301,842 Zeilen

## Qualitätsprüfungen nach Lockerung:

Negative Werte: 0 (0.00%)
PM2 - 99.9% Quantil: 99.0, Extreme Ausreißer: 49
NO2 - 99.9% Quantil: 130.0, Extreme Ausreißer: 185
O3 - 99.9% Quantil: 91.0, Extreme Ausreißer: 12
PM10 - 99.9% Quantil: 141.6, Extreme Ausreißer: 4

## Entferne nur extreme Ausreißer :

PM2: 49 extreme Ausreißer entfernt (>99.8)
NO2: 94 extreme Ausreißer entfernt (>143.0)
O3: 3 extreme Ausreißer entfernt (>92.0)
PM10: 2 extreme Ausreißer entfernt (>142.3)

## Finale Luftdaten:

Anzahl: 301,694 Zeilen

## Luftqualitätsstationen:

Anzahl: 415

# Wetterdaten

## Missing Values:

station_id 0
parameter 0
value 0
quality 0

## Verfügbare Wetterparameter:

precipitation_height 851202
temperature_air_mean_2m 371810
humidity_absolute 370288
wind_speed 210850
sunshine_duration 166132
visibility_range 146843
cloud_cover_total 143713

## Wetterstationen:

Anzahl: 1251

# Geographische Verteilung

## Luftstationen - Lat/Lon Bereich:

Latitude: 47.48 bis 54.92
Longitude: 6.09 bis 14.97

## Wetterstationen - Lat/Lon Bereich:

Latitude: 47.40 bis 55.01
Longitude: 6.02 bis 14.95

# Zeitliche Abdeckung:

Luftdaten: 2016-01-01 15:00:00 bis 2016-01-31 23:00:00
Wetterdaten: 2016-01-01 00:00:00 bis 2016-01-31 23:00:00
