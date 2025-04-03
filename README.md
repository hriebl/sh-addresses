# sh-addresses

![Kartendarstellung der Adressen](assets/map.png)

Dieses Repository enthält
- die [amtlichen Adressen für Schleswig-Holstein](data) pro Postleitzahl im CSV-Format, sowie
- den [dazugehörigen Harvester](harvester), der in Python implementiert ist.

Die Daten wurden heruntergeladen aus dem INSPIRE WFS-Downloaddienst des Landesamtes für Vermessung und Geoinformation Schleswig-Holstein. Sie stehen unter der CC-BY-4.0-Lizenz (© GeoBasis-DE/LVermGeo SH/CC BY 4.0).

Der Harvester teilt die Abfragen so auf, dass die Obergrenze an Ergebnissen pro Abfrage eingehalten wird, wie vom WFS-Dienst vorgegeben. Die Ergebnisse werden erst in einer SQLite-Datenbank zwischengespeichert und anschließend in mehrere CSV-Dateien geschrieben.

Die Adressen sind georeferenziert im Koordinatenreferenzsystem [EPSG:4326](https://epsg.io/4326).

## Installation

```
git clone https://github.com/hriebl/sh-addresses
cd sh-addresses
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Harvesting

```
rm -rf data
mkdir data
python -m harvester data
```
