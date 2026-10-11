"""Exercise authentication against Flask and a real SQLite database."""
import sys
import unittest
from datetime import timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from app import create_app
from api.models import User, db
from flask_jwt_extended import create_access_token


class AuthenticationTests(unittest.TestCase):
    def setUp(self):
        self.app = create_app({"TESTING": True, "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
                               "JWT_SECRET_KEY": "test-only-secret-key-not-for-deployment-123456"})
        self.context = self.app.app_context()
        self.context.push()
        db.create_all()
        self.client = self.app.test_client()
        self.credentials = {"email": "alice@example.com", "password": "test-password"}

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        db.engine.dispose()
        self.context.pop()

    def signup(self):
        return self.client.post("/api/signup", json=self.credentials)

    def test_complete_authentication_flow(self):
        self.assertEqual(self.signup().status_code, 201)
        user = db.session.execute(db.select(User)).scalar_one()
        self.assertNotEqual(user.password, self.credentials["password"])
        self.assertTrue(user.check_password(self.credentials["password"]))
        response = self.client.post("/api/login", json=self.credentials)
        self.assertEqual(response.status_code, 200)
        token = response.json["token"]
        response = self.client.get("/api/private", headers={"Authorization": f"Bearer {token}"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["user"]["email"], self.credentials["email"])
        self.assertNotIn("password", response.json["user"])
        self.assertEqual(self.client.get("/api/private").status_code, 401)

    def test_duplicate_email_is_case_insensitive(self):
        self.signup()
        response = self.client.post("/api/signup", json={**self.credentials, "email": " ALICE@EXAMPLE.COM "})
        self.assertEqual(response.status_code, 409)

    def test_invalid_registration_payloads(self):
        for payload in [None, [], {"email": "wrong", "password": "password"},
                        {"email": "alice@example.com", "password": "short"},
                        {"email": 123, "password": "password"}]:
            with self.subTest(payload=payload):
                self.assertEqual(self.client.post("/api/signup", json=payload).status_code, 400)

    def test_wrong_credentials(self):
        self.signup()
        response = self.client.post("/api/login", json={**self.credentials, "password": "wrong-password"})
        self.assertEqual(response.status_code, 401)
        self.assertNotIn("token", response.json)

    def test_invalid_and_expired_tokens(self):
        expired = create_access_token(identity="1", expires_delta=timedelta(seconds=-1))
        for token in ["not-a-token", expired]:
            self.assertEqual(self.client.get("/api/private", headers={"Authorization": f"Bearer {token}"}).status_code, 401)

    def test_inactive_or_deleted_user_is_denied(self):
        self.signup()
        response = self.client.post("/api/login", json=self.credentials)
        token = response.json["token"]
        user = db.session.execute(db.select(User)).scalar_one()
        user.is_active = False
        db.session.commit()
        self.assertEqual(self.client.post("/api/login", json=self.credentials).status_code, 401)
        self.assertEqual(self.client.get("/api/private", headers={"Authorization": f"Bearer {token}"}).status_code, 401)
        db.session.delete(user)
        db.session.commit()
        self.assertEqual(self.client.get("/api/private", headers={"Authorization": f"Bearer {token}"}).status_code, 401)


if __name__ == "__main__":
    unittest.main()
