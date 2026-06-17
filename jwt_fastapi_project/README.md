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
