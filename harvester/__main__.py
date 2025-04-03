import argparse
from pathlib import Path

from . import csv, db, wfs


def main():
    parser = argparse.ArgumentParser("harvester")
    parser.add_argument("path", help="path of the output directory", type=Path)
    args = parser.parse_args()

    session = db.Session(args.path)

    harvester = wfs.Harvester(wfs.Postcode, session)
    print("[1/7] finding queries to harvest postcodes...")
    harvester.find()

    print("[2/7] running queries to harvest postcodes...")
    harvester.run()

    harvester = wfs.Harvester(wfs.Street, session)
    print("[3/7] finding queries to harvest streets...")
    harvester.find()

    print("[4/7] running queries to harvest streets...")
    harvester.run()

    harvester = wfs.Harvester(wfs.Address, session)
    print("[5/7] finding queries to harvest addresses (takes a long time)...")
    harvester.find()

    print("[6/7] running queries to harvest addresses...")
    harvester.run()

    print("[7/7] dumping one csv file per postcode...")
    csv.dump_all(args.path, session)
    session.close()


if __name__ == "__main__":
    main()
