"""Verify migrated catalog and JWT isolation through a real HTTP server."""
import json
import sys
import tempfile
import unittest
from pathlib import Path
from threading import Thread
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from flask_migrate import upgrade
from werkzeug.serving import make_server

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from app import create_app
from api.models import db


class LiveIntegrationTests(unittest.TestCase):
    def test_catalog_and_per_user_favorites_over_http(self):
        with tempfile.TemporaryDirectory(prefix="jwt-integration-") as directory:
            app = create_app({"TESTING": True, "SQLALCHEMY_DATABASE_URI": f"sqlite:///{directory}/auth.db",
                              "JWT_SECRET_KEY": "test-only-key-not-for-deployment-123456789"})
            with app.app_context():
                upgrade(directory=str(ROOT / "migrations"))
            for _ in range(2):
                result = app.test_cli_runner().invoke(args=["seed"])
                self.assertEqual(result.exit_code, 0, result.output)
            server = make_server("127.0.0.1", 0, app)
            thread = Thread(target=server.serve_forever, daemon=True)
            thread.start()

            def call(method, path, payload=None, token=None, extra=None):
                headers = {"Content-Type": "application/json", **(extra or {})}
                if token:
                    headers["Authorization"] = f"Bearer {token}"
                request = Request(f"http://127.0.0.1:{server.server_port}/api{path}",
                                  data=json.dumps(payload).encode() if payload is not None else None,
                                  headers=headers, method=method)
                try:
                    response = urlopen(request, timeout=10)
                except HTTPError as problem:
                    response = problem
                with response:
                    return response.status, json.loads(response.read())

            try:
                tokens = []
                for email in ("first@example.com", "second@example.com"):
                    payload = {"email": email, "password": "test-password"}
                    self.assertEqual(call("POST", "/signup", payload)[0], 201)
                    status, data = call("POST", "/login", payload)
                    self.assertEqual(status, 200)
                    tokens.append(data["token"])
                self.assertEqual(call("GET", "/users/favorites")[0], 401)
                for category in ("people", "planets", "vehicles"):
                    status, records = call("GET", f"/{category}")
                    self.assertEqual(status, 200)
                    self.assertEqual(len(records), 10)
                    record = records[0]
                    self.assertEqual(call("GET", f"/{category}/{record['id']}")[0], 200)
                    path = f"/favorite/{category}/{record['id']}"
                    self.assertEqual(call("POST", path)[0], 401)
                    self.assertEqual(call("POST", path, token=tokens[0])[0], 201)
                    self.assertEqual(call("POST", path, token=tokens[0])[0], 409)
                    self.assertEqual(len(call("GET", "/users/favorites", token=tokens[0])[1][category]), 1)
                    self.assertEqual(call("GET", "/users/favorites", token=tokens[1], extra={"X-User-ID": "1"})[1][category], [])
                    self.assertEqual(call("DELETE", path, token=tokens[1])[0], 404)
                    self.assertEqual(call("DELETE", path, token=tokens[0])[0], 200)
                    self.assertEqual(call("GET", "/users/favorites", token=tokens[0])[1][category], [])
            finally:
                server.shutdown()
                thread.join()
                server.server_close()
                with app.app_context():
                    db.session.remove()
                    db.engine.dispose()


if __name__ == "__main__":
    unittest.main()
