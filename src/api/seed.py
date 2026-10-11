"""Import the checked-in SWAPI snapshot without duplicating existing records."""

import json
from pathlib import Path

import click

from api.models import Character, Planet, Vehicle, db


def register_seed_command(app):
    @app.cli.command("seed")
    def seed():
        snapshot = json.loads((Path(__file__).resolve().parents[2] / "data" / "starwars.json").read_text())
        definitions = [
            ("planets", Planet, ("name", "climate", "terrain", "population")),
            ("people", Character, ("name", "gender", "height", "mass", "birth_year")),
            ("vehicles", Vehicle, ("name", "model", "manufacturer", "passengers")),
        ]
        try:
            for category, model, fields in definitions:
                records = db.session.execute(db.select(model)).scalars().all()
                for entry in snapshot["categories"][category]:
                    properties = entry["properties"]
                    record = next((item for item in records if item.swapi_id == entry["swapi_id"]), None)
                    if record is None:
                        matches = [item for item in records if item.name.casefold() == properties["name"].casefold()]
                        if len(matches) > 1:
                            raise ValueError(f"Ambiguous existing name: {properties['name']}")
                        record = matches[0] if matches else model()
                        if not matches:
                            db.session.add(record)
                            records.append(record)
                    record.swapi_id = entry["swapi_id"]
                    record.properties = properties
                    for field in fields:
                        setattr(record, field, properties.get(field))
                    if category == "people":
                        record.homeworld = db.session.execute(
                            db.select(Planet).where(Planet.swapi_id == entry.get("homeworld_swapi_id"))
                        ).scalar_one_or_none()
                db.session.flush()
                click.echo(f"Imported {len(snapshot['categories'][category])} {category}")
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise
