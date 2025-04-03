# sh-addresses

Amtliche Adressen für Schleswig-Holstein [pro Postleitzahl im CSV-Format](data), heruntergeladen aus dem INSPIRE WFS-Downloaddienst des Landesamtes für Vermessung und Geoinformation Schleswig-Holstein. Die Daten stehen unter der CC-BY-4.0-Lizenz (© GeoBasis-DE/LVermGeo SH/CC BY 4.0).

Der Harvester ist in Python geschrieben. Er splittet die Queries, um nur so viele Ergebnisse abzufragen, wie der WFS-Dienst pro Query erlaubt. Die Ergebnisse werden in einer SQLite-Datenbank zwischengespeichert und abschließend in je eine CSV-Datei pro Postleitzahl geschrieben.

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
