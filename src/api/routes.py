"""Registration, login and JWT-protected user endpoints."""
import re

from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required
from sqlalchemy.exc import IntegrityError
from api.models import User, db

api = Blueprint("api", __name__)


def credentials():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return None, None
    email, password = data.get("email"), data.get("password")
    if not isinstance(email, str) or not isinstance(password, str):
        return None, None
    return email.strip().lower(), password


@api.post("/signup")
def signup():
    email, password = credentials()
    if not email or len(email) > 120 or not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", email):
        return jsonify(message="Enter a valid email address."), 400
    if not password or not 8 <= len(password) <= 128:
        return jsonify(message="Password must contain between 8 and 128 characters."), 400
    user = User(email=email, is_active=True)
    user.set_password(password)
    db.session.add(user)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify(message="An account with this email already exists."), 409
    return jsonify(message="Account created. Please log in.", user=user.serialize()), 201


@api.post("/login")
def login():
    email, password = credentials()
    if not email or not password or len(password) > 128:
        return jsonify(message="Email and password are required."), 400
    user = db.session.execute(db.select(User).filter_by(email=email)).scalar_one_or_none()
    if user is None or not user.is_active or not user.check_password(password):
        return jsonify(message="Invalid email or password."), 401
    token = create_access_token(identity=str(user.id))
    return jsonify(token=token, user=user.serialize()), 200


@api.get("/private")
@jwt_required()
def private():
    identity = get_jwt_identity()
    if not isinstance(identity, str) or not identity.isdecimal():
        return jsonify(message="Invalid session. Please log in again."), 401
    user = db.session.get(User, int(identity))
    if user is None or not user.is_active:
        return jsonify(message="Invalid session. Please log in again."), 401
    return jsonify(message="You have access to this private page.", user=user.serialize()), 200
