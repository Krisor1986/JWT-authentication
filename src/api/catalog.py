"""Star Wars catalog and user favorites, adapted from the earlier API exercise."""
from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from sqlalchemy.exc import IntegrityError
from api.models import (db, User, Character, Planet, Vehicle,
                        FavoriteCharacter, FavoritePlanet, FavoriteVehicle)

catalog = Blueprint("catalog", __name__)
RESOURCES = {
    "people": (Character, FavoriteCharacter, "character_id"),
    "planets": (Planet, FavoritePlanet, "planet_id"),
    "vehicles": (Vehicle, FavoriteVehicle, "vehicle_id"),
}


def current_user():
    identity = get_jwt_identity()
    if not isinstance(identity, str) or not identity.isdecimal():
        return None
    user = db.session.get(User, int(identity))
    return user if user and user.is_active else None


@catalog.get("/<category>")
def list_resources(category):
    if category not in RESOURCES:
        return jsonify(message="Resource not found."), 404
    model = RESOURCES[category][0]
    records = db.session.execute(db.select(model).order_by(model.id)).scalars()
    return jsonify([record.serialize() for record in records]), 200


@catalog.get("/<category>/<int:resource_id>")
def resource_details(category, resource_id):
    if category not in RESOURCES:
        return jsonify(message="Resource not found."), 404
    record = db.session.get(RESOURCES[category][0], resource_id)
    if record is None:
        return jsonify(message="Resource not found."), 404
    return jsonify(record.serialize()), 200


@catalog.get("/users/favorites")
@jwt_required()
def favorites():
    user = current_user()
    if user is None:
        return jsonify(message="Invalid session. Please log in again."), 401
    return jsonify(
        people=[favorite.character.serialize() for favorite in user.favorite_characters],
        planets=[favorite.planet.serialize() for favorite in user.favorite_planets],
        vehicles=[favorite.vehicle.serialize() for favorite in user.favorite_vehicles],
    ), 200


@catalog.route("/favorite/<category>/<int:resource_id>", methods=["POST", "DELETE"])
@jwt_required()
def manage_favorite(category, resource_id):
    user = current_user()
    if user is None:
        return jsonify(message="Invalid session. Please log in again."), 401
    if category not in RESOURCES:
        return jsonify(message="Resource not found."), 404
    model, favorite_model, id_field = RESOURCES[category]
    if db.session.get(model, resource_id) is None:
        return jsonify(message="Resource not found."), 404
    keys = {"user_id": user.id, id_field: resource_id}
    favorite = db.session.get(favorite_model, keys)
    if request.method == "POST":
        if favorite is not None:
            return jsonify(message="Favorite already exists."), 409
        db.session.add(favorite_model(**keys))
        status = 201
    else:
        if favorite is None:
            return jsonify(message="Favorite not found."), 404
        db.session.delete(favorite)
        status = 200
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify(message="Could not save favorite."), 409
    return jsonify(message="Favorite saved."), status
