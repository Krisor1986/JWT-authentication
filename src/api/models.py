from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import JSON, Boolean, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


def image_url(category, swapi_id):
    if swapi_id is None:
        return None
    return (
        "https://raw.githubusercontent.com/breatheco-de/swapi-images/master/"
        f"public/images/{category}/{swapi_id}.jpg"
    )


class User(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean(), nullable=False)

    favorite_planets: Mapped[list["FavoritePlanet"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )
    favorite_characters: Mapped[list["FavoriteCharacter"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )

    favorite_vehicles: Mapped[list["FavoriteVehicle"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def __str__(self):
        return self.email

    def serialize(self):
        return {
            "id": self.id,
            "email": self.email,
            "is_active": self.is_active,
            # do not serialize the password, its a security breach
        }


class Planet(db.Model):
    __tablename__ = "planet"

    id: Mapped[int] = mapped_column(primary_key=True)
    swapi_id: Mapped[str | None] = mapped_column(String(20), unique=True)
    properties: Mapped[dict | None] = mapped_column(JSON, default=dict)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    climate: Mapped[str | None] = mapped_column(String(100))
    terrain: Mapped[str | None] = mapped_column(String(100))
    population: Mapped[str | None] = mapped_column(String(30))

    characters: Mapped[list["Character"]] = relationship(back_populates="homeworld")
    favorites: Mapped[list["FavoritePlanet"]] = relationship(
        back_populates="planet",
        cascade="all, delete-orphan",
    )

    def __str__(self):
        return self.name

    def serialize(self):
        return {
            "id": self.id,
            "swapi_id": self.swapi_id,
            "image_url": image_url("planets", self.swapi_id),
            "properties": self.properties or {},
            "name": self.name,
            "climate": self.climate,
            "terrain": self.terrain,
            "population": self.population,
        }


class Character(db.Model):
    __tablename__ = "character"

    id: Mapped[int] = mapped_column(primary_key=True)
    swapi_id: Mapped[str | None] = mapped_column(String(20), unique=True)
    properties: Mapped[dict | None] = mapped_column(JSON, default=dict)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    gender: Mapped[str | None] = mapped_column(String(30))
    height: Mapped[str | None] = mapped_column(String(30))
    mass: Mapped[str | None] = mapped_column(String(30))
    birth_year: Mapped[str | None] = mapped_column(String(30))

    planet_id: Mapped[int | None] = mapped_column(ForeignKey("planet.id"))

    homeworld: Mapped["Planet | None"] = relationship(back_populates="characters")
    favorites: Mapped[list["FavoriteCharacter"]] = relationship(
        back_populates="character",
        cascade="all, delete-orphan",
    )

    def __str__(self):
        return self.name

    def serialize(self):
        return {
            "id": self.id,
            "swapi_id": self.swapi_id,
            "image_url": image_url("people", self.swapi_id),
            "properties": self.properties or {},
            "name": self.name,
            "gender": self.gender,
            "height": self.height,
            "mass": self.mass,
            "birth_year": self.birth_year,
            "planet_id": self.planet_id,
            "homeworld": (
                self.homeworld.name
                if self.homeworld
                else (self.properties or {}).get("homeworld")
            ),
        }


class FavoritePlanet(db.Model):
    __tablename__ = "favorite_planet"

    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), primary_key=True)
    planet_id: Mapped[int] = mapped_column(ForeignKey("planet.id"), primary_key=True)

    user: Mapped["User"] = relationship(back_populates="favorite_planets")
    planet: Mapped["Planet"] = relationship(back_populates="favorites")


class FavoriteCharacter(db.Model):
    __tablename__ = "favorite_character"

    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), primary_key=True)
    character_id: Mapped[int] = mapped_column(
        ForeignKey("character.id"), primary_key=True
    )

    user: Mapped["User"] = relationship(back_populates="favorite_characters")
    character: Mapped["Character"] = relationship(back_populates="favorites")


class Vehicle(db.Model):
    __tablename__ = "vehicle"

    id: Mapped[int] = mapped_column(primary_key=True)
    swapi_id: Mapped[str | None] = mapped_column(String(20), unique=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    model: Mapped[str | None] = mapped_column(String(200))
    manufacturer: Mapped[str | None] = mapped_column(String(255))
    passengers: Mapped[str | None] = mapped_column(String(30))
    properties: Mapped[dict | None] = mapped_column(JSON, default=dict)
    favorites: Mapped[list["FavoriteVehicle"]] = relationship(
        back_populates="vehicle", cascade="all, delete-orphan"
    )

    def __str__(self):
        return self.name

    def serialize(self):
        return {
            "id": self.id,
            "swapi_id": self.swapi_id,
            "image_url": image_url("vehicles", self.swapi_id),
            "name": self.name,
            "model": self.model,
            "manufacturer": self.manufacturer,
            "passengers": self.passengers,
            "properties": self.properties or {},
        }


class FavoriteVehicle(db.Model):
    __tablename__ = "favorite_vehicle"

    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), primary_key=True)
    vehicle_id: Mapped[int] = mapped_column(ForeignKey("vehicle.id"), primary_key=True)
    user: Mapped["User"] = relationship(back_populates="favorite_vehicles")
    vehicle: Mapped["Vehicle"] = relationship(back_populates="favorites")
