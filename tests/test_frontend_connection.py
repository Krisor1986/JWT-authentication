"""Check authentication through Vite's real development proxy and Flask's build."""
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
from threading import Thread
import time
import unittest
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from werkzeug.serving import make_server

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from app import create_app
from api.models import db


class FrontendConnectionTests(unittest.TestCase):
    def test_authentication_from_frontend_origin(self):
        node = shutil.which("node")
        vite = ROOT / "node_modules/vite/bin/vite.js"
        self.assertTrue(node and vite.is_file(), "Install Node.js and run npm install first.")
        with tempfile.TemporaryDirectory(prefix="jwt-frontend-") as directory:
            app = create_app({
                "TESTING": True,
                "SQLALCHEMY_DATABASE_URI": f"sqlite:///{directory}/auth.db",
                "JWT_SECRET_KEY": "test-only-key-not-for-deployment-123456789",
            })
            with app.app_context():
                db.create_all()
            server = make_server("127.0.0.1", 0, app)
            thread = Thread(target=server.serve_forever, daemon=True)
            thread.start()
            backend = f"http://127.0.0.1:{server.server_port}"
            environment = {
                **os.environ, "BACKEND_URL": backend, "VITE_BACKEND_URL": "",
            }
            with tempfile.TemporaryFile(mode="w+") as output:
                process = subprocess.Popen(
                    [node, str(vite), "--host", "127.0.0.1", "--port", "0"],
                    cwd=ROOT, env=environment, stdout=output, stderr=subprocess.STDOUT,
                )
                try:
                    origin = None
                    deadline = time.monotonic() + 20
                    while time.monotonic() < deadline:
                        output.seek(0)
                        log = output.read()
                        match = re.search(r"http://127\.0\.0\.1:\d+", log)
                        if match:
                            origin = match.group(0)
                            try:
                                with urlopen(f"{origin}/api/health", timeout=1) as response:
                                    if response.status == 200:
                                        break
                            except (URLError, TimeoutError):
                                pass
                        self.assertIsNone(process.poll(), log)
                        time.sleep(0.1)
                    else:
                        self.fail(f"Vite did not start or proxy the backend: {log}")

                    def call(base, method, path, payload=None, token=None):
                        headers = {"Content-Type": "application/json"}
                        if token:
                            headers["Authorization"] = f"Bearer {token}"
                        request = Request(
                            f"{base}/api{path}", method=method, headers=headers,
                            data=json.dumps(payload).encode() if payload is not None else None,
                        )
                        try:
                            response = urlopen(request, timeout=5)
                        except HTTPError as error:
                            response = error
                        with response:
                            return response.status, json.loads(response.read())

                    self.assertNotEqual(origin, backend)
                    with urlopen(f"{origin}/login") as response:
                        self.assertIn(b"/src/front/main.jsx", response.read())
                    with urlopen(f"{origin}/src/front/hooks/useGlobalReducer.jsx") as response:
                        source = response.read().decode()
                        self.assertIn('"VITE_BACKEND_URL": ""', source)
                    credentials = {"email": "proxy@example.com", "password": "test-password"}
                    self.assertEqual(call(origin, "GET", "/private")[0], 401)
                    self.assertEqual(call(origin, "POST", "/signup", credentials)[0], 201)
                    status, data = call(origin, "POST", "/login", credentials)
                    self.assertEqual(status, 200)
                    status, private = call(origin, "GET", "/private", token=data["token"])
                    self.assertEqual(status, 200)
                    self.assertEqual(private["user"]["email"], credentials["email"])
                    self.assertEqual(call(origin, "GET", "/private", token="invalid")[0], 401)
                    if (ROOT / "dist/index.html").exists():
                        with urlopen(f"{backend}/login") as response:
                            self.assertIn(b"/assets/", response.read())
                        self.assertEqual(call(backend, "POST", "/login", credentials)[0], 200)
                finally:
                    process.terminate()
                    try:
                        process.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        process.kill()
                        process.wait()
                    server.shutdown()
                    thread.join()
                    server.server_close()
                    with app.app_context():
                        db.session.remove()
                        db.engine.dispose()
