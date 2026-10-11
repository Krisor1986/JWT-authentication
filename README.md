# Star Wars Blog — JWT Authentication

[English](README.md) · [Español](README.es.md) · [Português](README.pt.md)

Final 4Geeks Academy authentication exercise, based on the official React + Flask template. It reuses the earlier Star Wars Blog and Star Wars API code in this separate repository.

## Required flow

- `/signup`: create a database user with an email and password, then redirect to `/login`.
- `/login`: validate credentials, store the JWT in `sessionStorage`, then redirect to `/private`.
- `/private`: validate the token with Flask before displaying the user's favorites. Revalidate every 30 seconds and when the window regains focus. Invalid or expired sessions redirect to `/login`.
- Navbar logout: remove the session token, clear favorites and redirect to `/login`.

The catalog and detail pages are public. Clicking a favorite star while logged out opens the login page. Favorites belong to the authenticated user and persist in the database. The backend derives the user from the signed JWT; `X-User-ID` cannot select another account. Passwords use Werkzeug hashes and are never returned by the API. Tokens expire after 30 minutes. Logout clears the browser session; this exercise does not implement server-side token revocation.

## Local setup

Use Python 3.13, Pipenv and Node.js 20.19+ or 22.12+. The local project already has dependencies, `.env`, migrations and catalog data configured. The following setup is for a fresh clone; keep your existing `.env` when resuming.

```bash
pipenv install
npm install
cp .env.example .env
python3 -c "import secrets; print(secrets.token_hex(32))"
```
Replace `JWT_SECRET_KEY` in `.env` with the random value printed by Python. Do not commit `.env`. SQLite is the local default; no separate database service is needed.

Start the backend in one terminal:

```bash
pipenv run upgrade
pipenv run flask seed
pipenv run start
```
Start React in a second terminal:

```bash
npm run start
```
Open [the frontend](http://localhost:3000). Flask runs at `http://127.0.0.1:3001`; `VITE_BACKEND_URL` points there. The seed command is repeatable and imports the same 10 characters, 10 planets and 10 vehicles used in the previous API exercise. Create your own account through `/signup`.

## API

| Method | Endpoint | Authentication |
| --- | --- | --- |
| POST | `/api/signup` | Public |
| POST | `/api/login` | Public |
| GET | `/api/private` | Bearer JWT |
| GET | `/api/people`, `/api/planets`, `/api/vehicles` | Public |
| GET | `/api/<category>/<id>` | Public |
| GET | `/api/users/favorites` | Bearer JWT |
| POST / DELETE | `/api/favorite/<category>/<id>` | Bearer JWT |

The category values are `people`, `planets` and `vehicles`. Route IDs are local database IDs; images use the separate `swapi_id`, without assuming those IDs match. Requests to signup and login send JSON with `email` and `password`.

## Validation

```bash
pipenv run test
npm run lint
npm run build
```
Tests exercise authentication, password hashes, invalid and expired tokens, migrations, repeatable imports, and favorites isolation. Integration tests start a real HTTP server with an isolated SQLite database; they do not mock API responses. The running frontend/backend flow was also checked in a browser. All 30 external image URLs returned image responses during verification; external availability can change.

## Sources and scope

- [Authentication assignment](https://github.com/breatheco-de/jwt-authentication-with-flask-react).
- [Official starter](https://github.com/4GeeksAcademy/react-flask-hello).
- Reused local exercises: Starwars-blog and Starwars-blog-api; the originals are unchanged.
- `data/starwars.json` preserves the earlier API's SWAPI.tech snapshot and resolved related names. The frontend reads the local Flask API at runtime, rather than requesting SWAPI.tech directly.
- Images come from the school's [swapi-images repository](https://github.com/breatheco-de/swapi-images).

The inherited unprotected admin panel and public user listing are not registered in this application. This is the authentication exercise, with no additional account recovery or production deployment scope. The backend can serve the React production build after `npm run build`.
