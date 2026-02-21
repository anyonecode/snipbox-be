# SnipBox

> A short note saving app — save text snippets and group them with tags.  
> Built with **Django REST Framework** + **JWT Authentication**.

---

## Features

- Save snippets (title + note) with automatic timestamps
- Organize snippets with reusable tags (deduplicated — one tag per unique title)
- JWT-based authentication (login + token refresh)
- Full CRUD for snippets with input validation and error handling
- Tag list and tag-to-snippets lookup
- Django Admin for managing snippets and tags

---

## Tech Stack

| Component | Technology |
|---|---|
| Backend | Django 4.2 |
| REST API | Django REST Framework 3.15 |
| Auth | djangorestframework-simplejwt 5.3 |
| Database | SQLite |
| Server | Gunicorn |
| Container | Docker + Docker Compose |

---

## Prerequisites

- Python 3.10+
- pip
- (Optional) Docker & Docker Compose

---

## Local Installation

### 1. Clone the repository

```bash
git clone https://github.com/<your-username>/snipbox.git
cd snipbox
```

### 2. Create and activate a virtual environment

```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# macOS / Linux
python -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run database migrations

```bash
python manage.py migrate
```

### 5. Create a superuser

```bash
python manage.py createsuperuser
```

### 6. Start the development server

```bash
python manage.py runserver
```

The API is now available at **http://127.0.0.1:8000/**  
The Django Admin is available at **http://127.0.0.1:8000/admin/**

---

## Running Tests

```bash
python manage.py test snippets
```

---

## Docker Deployment

```bash
docker-compose up --build
```

This will:
1. Run Django migrations automatically
2. Create a superuser (`admin` / `admin123`)
3. Start the Gunicorn server on port **8000**

To stop:
```bash
docker-compose down
```

---

## API Endpoints

### Authentication

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/v1/token/` | Login — returns `access` + `refresh` tokens |
| POST | `/api/v1/token/refresh/` | Get a new access token using refresh token |

> All CRUD endpoints require the header: `Authorization: Bearer <access_token>`

### Snippets

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/v1/snippets/` | Overview — total count + list with detail links |
| POST | `/api/v1/snippets/` | Create a new snippet |
| GET | `/api/v1/snippets/<id>/` | Get snippet detail (owner only) |
| PUT | `/api/v1/snippets/<id>/` | Full update |
| PATCH | `/api/v1/snippets/<id>/` | Partial update |
| DELETE | `/api/v1/snippets/<id>/` | Delete snippet; returns remaining list |

### Tags

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/v1/tags/` | List all tags |
| GET | `/api/v1/tags/<id>/` | Tag detail + linked snippets (current user) |

---

## Sample Request — Create Snippet

```bash
# 1. Login
curl -X POST http://127.0.0.1:8000/api/v1/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'

# 2. Create a snippet (replace <token> with the access token from step 1)
curl -X POST http://127.0.0.1:8000/api/v1/snippets/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "My First Snippet",
    "note": "This is a quick note.",
    "tags": [{"title": "django"}, {"title": "python"}]
  }'
```

> **Tag deduplication**: If a tag with the same title already exists, it is reused — no duplicate tags are created.

See [`postman_collection.json`](postman_collection.json) for the full Postman API collection.

---

## Error Handling

All endpoints return structured error responses:

| Status | Meaning |
|---|---|
| `400` | Validation error — missing fields, bad tag format, empty body |
| `401` | Unauthenticated — missing or invalid token |
| `404` | Snippet / tag not found or not owned by current user |
| `500` | Unexpected server error |

---

## Database Schema

See [`schema.md`](schema.md) for the full ER diagram.

---

## Project Structure

```
snipbox
├── Dockerfile
├── README.md
├── db.sqlite3
├── docker-compose.yml
├── manage.py
├── postman_collection.json
├── requirements.txt
├── schema.md
├── snipbox
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
└── snippets
    ├── __init__.py
    ├── admin.py
    ├── apps.py
    ├── migrations
    │   └── __init__.py
    ├── models.py
    ├── serializers.py
    ├── tests.py
    ├── urls.py
    └── views.py
```

---

## Standards

- Follows **PEP-8** coding standards
- All endpoints return JSON
- Access token lifetime: **60 minutes**
- Refresh token lifetime: **1 day**
