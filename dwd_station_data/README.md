## 2.1 Wetterdatenbeschaffung über die DWD-API

Um mögliche Hypothesen eines Zusammenhangs zwischen Wetterereignissen und Veränderungen von Luftqualitätsdaten zu untersuchen, wurden stündliche Wetterdaten des Deutschen Wetterdienstes (DWD) herangezogen. Das Vorgehen gliedert sich in folgende Schritte:

### 2.1.1 Datenquelle und Auflösung

Die Daten stammen aus dem Climate Data Center (CDC) des DWD, das Klimadaten für Deutschland bereitstellt. Zur Verfügung stehen sieben Auflösungen – u. a. 10-Minuten, stündlich, täglich und monatlich – wobei jede Auflösung unterschiedliche Parameter abdeckt. Da die Luftqualitätsdaten in stündlicher Auflösung vorliegen, wurde für alle meteorologischen Größen die stündliche („hourly“) Auflösung gewählt ([dwd.de][1]).

### 2.1.2 Metadatenakquise und Stationsauswahl

Über die frei zugängliche FTP-Schnittstelle des DWD wurden zunächst alle Metadaten zu den stündlichen Messstationen aus den Unterverzeichnissen der einzelnen Klimaparameter ausgelesen. Ein typischer Metadatensatz enthält:

```
Stations_id;von_datum;bis_datum;Stationshoehe;geoBreite;geoLaenge;Stationsname;Bundesland;Abgabe
```

(Beispiel: `00003;19500401;20110401;202;50.7827;6.0941;Aachen;Nordrhein-Westfalen;Frei`).
Insgesamt ergab sich dadurch ein Pool von **2341 Stationen** deutschlandweit, die mindestens einen der interessierenden Parameter erfassten.

### 2.1.3 Parameterauswahl

Um eine breite Basis für spätere Hypothesentests zu schaffen, wurden folgende stündlichen Parameter abgefragt:

- **temperature_air_mean_2m** (Lufttemperatur in 2 m, °C)
- **cloud_cover_total** (Gesamtbedeckungsgrad, Achtel)
- **humidity_absolute** (Absolute Feuchte, g/m³)
- **precipitation_height** (Niederschlagshöhe, mm)
- **sunshine_duration** (Sonnenscheindauer, Minuten)
- **visibility_range** (Sichtweite, m)
- **wind_speed** (Windgeschwindigkeit, m/s)

Diese Parameter wurden mittels der Python-Bibliothek **wetterdienst** (Version 0.108.0) in einem einzigen Request je Monat und allen relevanten Stations-IDs abgefragt ([wetterdienst.readthedocs.io][2]).

### 2.1.4 Datenabruf und -verarbeitung

- **Zeitraum**: 01.01.2024–01.01.2025 (für einzelne Hypothesen wurden in Ausnahmefällen abweichende Zeiträume genutzt).
- **Batch-Downloads**: Pro Monat wurde eine CSV–Datei erzeugt (jeweils \~200 MB, \~2,2 Mio. Einträge).
- **Dateiformat**: Jede Zeile enthält die Felder

  ```
  station_id, resolution, dataset, parameter, date, value, quality, latitude, longitude
  ```

  (Beispiel: `00011,hourly,wind,wind_speed,2024-04-01T00:00:00+00:00,4.2,10.0,47.9736,8.5205`).

- **Konsolidierung**: Mit einem einfachen Python-Skript wurden alle Monats-CSVs zeilenweise aneinandergereiht, sodass eine Gesamttabelle mit \~28 Mio. Einträgen (2,4 GB) entstand.

### 2.1.5 Qualitäts- und Zeitstempel-Handling

- **Quality-Flags**: Das Feld `quality` (QUALITAETS_NIVEAU) beschreibt automatisierte und manuelle Prüfverfahren (u. a. Konsistenz- und statistische Tests) – es wurde im Vorfeld entschieden, sämtliche Messwerte ohne zusätzliche Filterung zu verwenden, da die Qualitätskontrolle des DWD bereits den Großteil offensichtlicher Ausreißer entfernt ([opendata.dwd.de][3]).
- **Zeitzonen**: Die DWD-Timestamps liegen in UTC („+00:00“). Eine Umrechnung in Mitteleuropäische Sommerzeit (MESZ, UTC+2) erfolgte dort, wo die Zuordnung zu Luftqualitätsdaten in lokaler Zeit nötig war; andernfalls blieben die Zeitstempel in UTC.

### 2.1.6 Unsicherheiten

Die DWD-Messnetze folgen heute WMO-Standards, womit lokale Effekte minimiert werden. Historisch betrachtet variieren jedoch Prüfroutinen und Standardisierung (z. B. vor 1990 unterschiedliche Vorschriften in Ost-/Westdeutschland). Daher sollte für jede Hypothese geprüft werden, inwieweit lokale Besonderheiten oder Lücken in den Stationsreihen die Ergebnisse beeinflussen können.

---

_Quellen:_

- DWD Climate Data Center (CDC): Index der stündlichen Klimadaten und Metadaten ([opendata.dwd.de][3])
- Wetterdienst Python API (Version 0.108.0) ([wetterdienst.readthedocs.io][2])

[1]: https://www.dwd.de/EN/ourservices/cdc/cdc_ueberblick-klimadaten_en.html?utm_source=chatgpt.com "Wetter und Klima - Our services - Climate data for direct download"
[2]: https://wetterdienst.readthedocs.io/en/latest/usage/python-api/?utm_source=chatgpt.com "Python API - Wetterdienst - Read the Docs"
[3]: https://opendata.dwd.de/climate_environment/CDC/observations_germany/climate/hourly/?utm_source=chatgpt.com "of /climate_environment/CDC/observations_germany/climate/hourly"
