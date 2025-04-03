from datetime import datetime
from inspect import cleandoc

import pandas as pd
from sqlalchemy import select

from . import db


def dump_code(code, path, session):
    stmt = (
        select(
            db.Address.id.label("uri"),
            db.Postcode.code.label("plz"),
            db.Postcode.city.label("stadt"),
            db.Street.name.label("strasse"),
            db.Address.number.label("nummer"),
            db.Address.extension.label("zusatz"),
            db.Address.lat.label("lat"),
            db.Address.lon.label("lon"),
        )
        .join(db.Postcode)
        .join(db.Street)
        .where(db.Postcode.code == code)
        .order_by(db.Address.id.asc())
    )

    df = pd.read_sql_query(stmt, session.bind)

    title = f"""
    # Amtliche Adressen für die Postleitzahl {code}
    #
    # Heruntergeladen aus dem INSPIRE WFS-Downloaddienst des Landesamtes für
    # Vermessung und Geoinformation Schleswig-Holstein. Die Daten stehen unter
    # der CC-BY-4.0-Lizenz.
    #
    # Datenquelle: © GeoBasis-DE/LVermGeo SH/CC BY 4.0
    # Mehr Informationen: https://github.com/hriebl/sh-addresses
    # Stichtag: {datetime.today().strftime('%d.%m.%Y')}
    """

    with open(path / f"{code}.csv", "w") as file:
        file.write(cleandoc(title) + "\n")

    df.to_csv(path / f"{code}.csv", index=False, mode="a")


def dump_all(path, session):
    stmt = select(db.Postcode.code.distinct())

    for code in session.scalars(stmt):
        dump_code(code, path, session)
