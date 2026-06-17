# Beginner Property Rental Management Project

A simple property rental management website using FastAPI, JWT login, SQLite, HTML, CSS, and JavaScript.

You can manage property listings, tenant details, rental agreement dates, monthly rent, payment status, and notes.

## Setup

```powershell
cd jwt_fastapi_project
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Run

```powershell
uvicorn main:app --reload
```

Open:

- API: http://127.0.0.1:8000
- Frontend: http://127.0.0.1:8000/app
- Swagger docs: http://127.0.0.1:8000/docs

## Deploy On Render Free

Push this `jwt_fastapi_project` folder to GitHub, then create a new Render Web Service.

Render settings:

- Build command: `pip install -r requirements.txt`
- Start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
- Root directory: `jwt_fastapi_project` if this folder is inside a bigger GitHub repo

Environment variables:

- `JWT_SECRET_KEY`: any long random secret value
- `JWT_ALGORITHM`: `HS256`
- `ACCESS_TOKEN_EXPIRE_MINUTES`: `30`

This project uses SQLite, which is fine for a free demo. On free hosting, saved records may disappear after redeploys or restarts.

## Flow

Create a user:

```powershell
curl -X POST http://127.0.0.1:8000/signup `
  -H "Content-Type: application/json" `
  -d "{\"username\":\"abhay\",\"password\":\"secret123\",\"full_name\":\"Abhayraj\"}"
```

Login and receive a JWT:

```powershell
curl -X POST http://127.0.0.1:8000/login `
  -H "Content-Type: application/x-www-form-urlencoded" `
  -d "username=abhay&password=secret123"
```

Use the returned token:

```powershell
curl http://127.0.0.1:8000/me `
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## Endpoints

- `POST /signup`
- `POST /login`
- `GET /me`
- `GET /protected`
- `GET /rentals`
- `POST /rentals`
- `PUT /rentals/{rental_id}`
- `DELETE /rentals/{rental_id}`
