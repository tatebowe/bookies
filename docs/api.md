# Bookies API

## Authentication

### POST /auth/login

Authenticate a user.

#### Request (form)

| Field | Type | Required |
|------|------|----------|
| username | string | Yes |
| password | string | Yes |

#### Response

```json
{
  "access_token": "...",
  "token_type": "bearer"
}
```

---

## Users

### POST /users

Register a new account.

#### Request

```json
{
  "username": "tate",
  "email": "tate@example.com",
  "password": "BookClub123"
}
```

#### Response

```json
{
  "id": 1,
  "username": "tate",
  "email": "tate@example.com"
}
```

---

### GET /users/me

Returns the currently authenticated user.

Requires:

Authorization: Bearer <token>