# Property Rental Management System - Testing Results

This folder contains Postman screenshots for testing the deployed FastAPI Property Rental Management System.

## Deployed URL

Frontend:

```text
https://fastapi-1-13ev.onrender.com/app
```

API base URL:

```text
https://fastapi-1-13ev.onrender.com
```

## Test Summary

| Step | Endpoint | Method | Status |
| --- | --- | --- | --- |
| 1 | `/` | `GET` | `200 OK` |
| 2 | `/signup` | `POST` | `201 Created` |
| 3 | `/login` | `POST` | `200 OK` |
| 4 | `/me` | `GET` | `200 OK` |
| 5 | `/rentals` | `POST` | `201 Created` |
| 6 | `/rentals` | `GET` | `200 OK` |
| 7 | `/rentals/{rental_id}` | `PUT` | `200 OK` |
| 8 | `/rentals/{rental_id}` | `DELETE` | `200 OK` |

## Authentication Note

Protected routes require a JWT token.

In Postman, after login:

1. Copy the `access_token`.
2. Open the protected request.
3. Go to **Authorization**.
4. Select **Bearer Token**.
5. Paste the token.

## 1. Health Check

Endpoint:

```http
GET /
```

Purpose: Confirms that the deployed API is running.

Expected result: `200 OK`

![Health Check](./Screenshot%202026-06-18%20133703.png)

## 2. Signup - Local Test

Endpoint:

```http
POST /signup
```

Body type: `raw JSON`

Sample body:

```json
{
  "username": "abhay",
  "password": "secret123",
  "full_name": "Abhayraj"
}
```

Expected result: `201 Created`

![Local Signup Test](./Screenshot%202026-06-18%20133312.png)

Additional signup screenshot:

![Local Signup Duplicate View](./Screenshot%202026-06-18%20133332.png)

## 3. Signup - Deployed Test

Endpoint:

```http
POST /signup
```

Purpose: Creates a user account on the deployed Render app.

Expected result: `201 Created`

![Deployed Signup Test](./Screenshot%202026-06-18%20134830.png)

## 4. Login - Initial Validation Issue

Endpoint:

```http
POST /login
```

Observed issue: Postman returned `422 Unprocessable Entity` because the login body was not received correctly by the backend.

The response showed:

```json
{
  "type": "missing",
  "loc": ["body", "username"],
  "msg": "Field required"
}
```

This was fixed by updating the backend login route to accept both:

- `application/json`
- `application/x-www-form-urlencoded`

Screenshots of the issue:

![Login Validation Issue 1](./Screenshot%202026-06-18%20134005.png)

![Login Validation Issue 2](./Screenshot%202026-06-18%20134356.png)

## 5. Login - Successful Test

Endpoint:

```http
POST /login
```

Body type: `raw JSON`

Sample body:

```json
{
  "username": "manager",
  "password": "secret123"
}
```

Expected result: `200 OK`

Response contains:

```json
{
  "access_token": "JWT_TOKEN",
  "token_type": "bearer"
}
```

![Successful Login](./Screenshot%202026-06-18%20134814.png)

## 6. Get Current User

Endpoint:

```http
GET /me
```

Authorization: Bearer Token required.

Purpose: Confirms that the JWT token is valid and returns the logged-in user profile.

Expected result: `200 OK`

![Get Current User](./Screenshot%202026-06-18%20135205.png)

## 7. Create Rental Record

Endpoint:

```http
POST /rentals
```

Authorization: Bearer Token required.

Body type: `raw JSON`

Sample body:

```json
{
  "property_name": "Green View Apartment",
  "property_address": "12 Park Street, Pune",
  "tenant_name": "Rahul Sharma",
  "tenant_phone": "9876543210",
  "start_date": "2026-07-01",
  "end_date": "2027-06-30",
  "monthly_rent": 25000,
  "payment_status": "Pending",
  "notes": "Deposit received"
}
```

Expected result: `201 Created`

![Create Rental Record](./Screenshot%202026-06-18%20135322.png)

## 8. Get Rental Records

Endpoint:

```http
GET /rentals
```

Authorization: Bearer Token required.

Purpose: Returns all rental records created by the logged-in user.

Expected result: `200 OK`

![Get Rental Records](./Screenshot%202026-06-18%20135427.png)

## 9. Update Rental Record

Endpoint:

```http
PUT /rentals/1
```

Authorization: Bearer Token required.

Sample update:

```json
{
  "property_name": "Green View Apartment",
  "property_address": "12 Park Street, Pune",
  "tenant_name": "Rahul Sharma",
  "tenant_phone": "9876543210",
  "start_date": "2026-07-01",
  "end_date": "2027-06-30",
  "monthly_rent": 26000,
  "payment_status": "Paid",
  "notes": "Rent paid for this month"
}
```

Expected result: `200 OK`

![Update Rental Record](./Screenshot%202026-06-18%20135506.png)

## 10. Delete Rental Record

Endpoint:

```http
DELETE /rentals/1
```

Authorization: Bearer Token required.

Expected result:

```json
{
  "message": "Rental record deleted"
}
```

Screenshots:

![Delete Rental Record 1](./Screenshot%202026-06-18%20135529.png)

![Delete Rental Record 2](./Screenshot%202026-06-18%20135537.png)

## Final Result

The deployed API was tested successfully using Postman for:

- Server health check
- User signup
- User login and JWT token generation
- Protected user profile route
- Rental record creation
- Rental record listing
- Rental record update
- Rental record deletion

The only issue observed during testing was the initial `/login` request format problem, which was resolved by allowing JSON login requests in addition to form-encoded login requests.
