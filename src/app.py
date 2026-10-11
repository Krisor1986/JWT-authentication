"""Flask application configuration for JWT authentication."""
import os
from datetime import timedelta
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from api.models import db
from api.routes import api
from api.catalog import catalog
from api.seed import register_seed_command

load_dotenv(Path(__file__).resolve().parents[1] / ".env")


def create_app(config=None):
    app = Flask(__name__, static_folder=None)
    app.url_map.strict_slashes = False
    app.config.update(
        SQLALCHEMY_DATABASE_URI=os.getenv("DATABASE_URL", "sqlite:///auth.db").replace("postgres://", "postgresql://", 1),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        JWT_SECRET_KEY=os.getenv("JWT_SECRET_KEY"),
        JWT_ACCESS_TOKEN_EXPIRES=timedelta(minutes=30),
        MAX_CONTENT_LENGTH=16384,
    )
    if config:
        app.config.update(config)
    if not app.config["JWT_SECRET_KEY"]:
        raise RuntimeError("Set JWT_SECRET_KEY in your .env file before starting the backend.")
    db.init_app(app)
    Migrate(app, db, compare_type=True)
    jwt = JWTManager(app)
    CORS(app, resources={r"/api/*": {"origins": os.getenv("FRONTEND_URL", "http://localhost:3000,http://127.0.0.1:3000").split(",")}})
    app.register_blueprint(api, url_prefix="/api")
    app.register_blueprint(catalog, url_prefix="/api")
    register_seed_command(app)

    @jwt.unauthorized_loader
    def missing_token(reason):
        return jsonify(message="Please log in to access this page."), 401

    @jwt.invalid_token_loader
    def invalid_token(reason):
        return jsonify(message="Invalid session. Please log in again."), 401

    @jwt.expired_token_loader
    def expired_token(header, payload):
        return jsonify(message="Your session expired. Please log in again."), 401

    @app.errorhandler(413)
    def too_large(error):
        return jsonify(message="Request is too large."), 413

    @app.get("/api/health")
    def health():
        return jsonify(status="ok"), 200

    @app.get("/")
    @app.get("/<path:path>")
    def frontend(path=""):
        if path.startswith("api/") or path == "api":
            return jsonify(message="Endpoint not found."), 404
        dist = Path(__file__).resolve().parents[1] / "dist"
        if not (dist / "index.html").exists():
            return jsonify(message="Backend is running. Open the React frontend at http://localhost:3000."), 200
        requested = dist / path
        filename = path if path and requested.is_file() else "index.html"
        return send_from_directory(dist, filename)

    return app


app = create_app()

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=3001)
