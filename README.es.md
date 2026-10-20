# Star Wars Blog — Autenticación JWT

[English](README.md) · [Español](README.es.md) · [Português](README.pt.md)

Ejercicio final de autenticación de 4Geeks Academy, basado en el template oficial React + Flask. Reutiliza el código del Star Wars Blog y la Star Wars API en este repositorio independiente.

## Flujo requerido

- `/signup`: crea un usuario con correo y contraseña y redirige a `/login`.
- `/login`: valida las credenciales, guarda el JWT en `sessionStorage` y redirige a `/private`.
- `/private`: valida el token con Flask antes de mostrar los favoritos. Revalida cada 30 segundos y al recuperar el foco de la ventana. Una sesión inválida o caducada redirige a `/login`.
- Logout en la navbar: elimina el token, limpia los favoritos y redirige a `/login`.

El catálogo y los detalles son públicos. Pulsar una estrella sin iniciar sesión abre el login. Los favoritos pertenecen al usuario autenticado y se guardan en la base de datos. El backend obtiene el usuario del JWT firmado; `X-User-ID` no permite elegir otra cuenta. Las contraseñas se almacenan como hashes de Werkzeug y nunca se devuelven. Los tokens caducan tras 30 minutos. Logout elimina la sesión del navegador; este ejercicio no implementa revocación del token en el servidor.

## Configuración local

Usa Python 3.13, Pipenv y Node.js 20.19+ o 22.12+. Este proyecto local ya tiene dependencias, `.env`, migraciones y catálogo configurados. Estos pasos son para un clon nuevo; conserva tu `.env` al continuar.

```bash
pipenv install
npm install
cp .env.example .env
python3 -c "import secrets; print(secrets.token_hex(32))"
```
Sustituye `JWT_SECRET_KEY` en `.env` por el valor aleatorio generado. No subas `.env`. SQLite es la base local predeterminada; no necesita un servicio independiente.

Backend en un terminal:

```bash
pipenv run upgrade
pipenv run flask seed
pipenv run start
```
React en otro terminal:

```bash
npm run start
```
Abre [el frontend](http://localhost:3000). Flask funciona en `http://127.0.0.1:3001`. Deja `VITE_BACKEND_URL` vacío: React solicita `/api` en la dirección del sitio actual y Vite reenvía las peticiones a `BACKEND_URL` (por defecto: `http://127.0.0.1:3001`). El navegador no necesita acceder a su propio localhost para alcanzar un backend remoto.

Al actualizar un `.env` existente, elimina el valor anterior `VITE_BACKEND_URL=http://127.0.0.1:3001`, añade `BACKEND_URL=http://127.0.0.1:3001` y reinicia Vite. En Codespaces, abre el puerto reenviado **3000**; solo el puerto del frontend necesita acceso desde el navegador. La dirección interna del backend sigue igual.

Después de `npm run build`, Flask sirve React y `/api` desde su propia dirección sin cambiar la URL del frontend. Solo si publicas frontend y backend por separado, configura `VITE_BACKEND_URL` con la URL HTTPS pública del backend antes de compilar (con o sin `/api`) y `FRONTEND_URL` con el origen del frontend para CORS. Vite incorpora los valores `VITE_*` al iniciar/compilar; cambiar solo el entorno de Flask no actualiza un build existente. El comando seed puede repetirse e importa los mismos 10 personajes, 10 planetas y 10 vehículos del ejercicio anterior. Crea tu cuenta en `/signup`.

## API

| Método | Endpoint | Autenticación |
| --- | --- | --- |
| POST | `/api/signup` | Público |
| POST | `/api/login` | Público |
| GET | `/api/private` | Bearer JWT |
| GET | `/api/people`, `/api/planets`, `/api/vehicles` | Público |
| GET | `/api/<category>/<id>` | Público |
| GET | `/api/users/favorites` | Bearer JWT |
| POST / DELETE | `/api/favorite/<category>/<id>` | Bearer JWT |

Las categorías son `people`, `planets` y `vehicles`. Las rutas usan IDs locales del banco; las imágenes usan el `swapi_id` separado, sin asumir que coinciden. Registro y login reciben JSON con `email` y `password`.

## Validación

```bash
pipenv run test
npm run lint
npm run build
```
Las pruebas verifican autenticación, hashes, tokens inválidos y caducados, migraciones, importación repetible y aislamiento de favoritos. La integración utiliza servidores HTTP reales y SQLite aislado, sin simular respuestas. Ejecuta `npm install` antes de las pruebas: la prueba de regresión de conexión inicia Vite en un puerto temporal y verifica registro, login y acceso privado mediante su proxy `/api`. Ejecuta `npm run build` antes de las pruebas para comprobar también el frontend servido por Flask. También se verificó el flujo con frontend y backend en el navegador. Las 30 URLs de imágenes externas respondieron con imágenes durante la comprobación; su disponibilidad puede cambiar.

## Fuentes y alcance

- [Enunciado de autenticación](https://github.com/breatheco-de/jwt-authentication-with-flask-react).
- [Template oficial](https://github.com/4GeeksAcademy/react-flask-hello).
- Ejercicios reutilizados: Starwars-blog y Starwars-blog-api; los originales siguen intactos.
- `data/starwars.json` conserva la captura de SWAPI.tech y los nombres relacionados del ejercicio anterior. El frontend consulta la API Flask local, no SWAPI.tech directamente.
- Las imágenes proceden del [repositorio swapi-images de la escuela](https://github.com/breatheco-de/swapi-images).

No se registran el panel admin sin protección ni la lista pública de usuarios del template. El alcance es la autenticación, sin recuperación de cuentas ni despliegue de producción adicional. El backend puede servir el build de React después de `npm run build`.
