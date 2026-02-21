# SnipBox

> A short note saving app — save text snippets and group them with tags.  
> Built with **Django REST Framework** + **JWT Authentication**.

---

## Features

- Save snippets (title + note) with automatic timestamps
- Organize snippets with reusable tags (deduplicated — one tag per unique title)
- JWT-based authentication (login + token refresh)
- Full CRUD for snippets
- Tag list and tag-to-snippets lookup

---

## Tech Stack

| Component | Technology |
|---|---|
| Backend | Django 4.2 |
| REST API | Django REST Framework 3.15 |
| Auth | djangorestframework-simplejwt |
| Database (local) | SQLite |
| Database (Docker) | PostgreSQL 15 |
| Server | Gunicorn |

---

## Prerequisites

- Python 3.8+
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

### 5. Create a superuser (optional but recommended for Django Admin)

```bash
python manage.py createsuperuser
```

### 6. Start the development server

```bash
python manage.py runserver
```

The API is now available at **http://127.0.0.1:8000/**

---

## Running Tests

```bash
python manage.py test snippets
```

---

## Docker Deployment

### Prerequisites
- Docker
- Docker Compose

### Start with Docker Compose

```bash
docker-compose up --build
```

This will:
1. Start a PostgreSQL 15 database
2. Run Django migrations automatically
3. Create a superuser (`admin` / `admin123`)
4. Start the Gunicorn server on port **8000**

### Stop

```bash
docker-compose down
```

To remove the database volume as well:

```bash
docker-compose down -v
```

### Environment Variables (Docker)

| Variable | Default | Description |
|---|---|---|
| `USE_POSTGRES` | `False` | Set to `True` to use PostgreSQL |
| `POSTGRES_DB` | `snipbox` | Database name |
| `POSTGRES_USER` | `snipbox` | Database user |
| `POSTGRES_PASSWORD` | `snipbox` | Database password |
| `POSTGRES_HOST` | `db` | Database host |
| `POSTGRES_PORT` | `5432` | Database port |

---

## API Endpoints

| Method | Endpoint | Description | Auth |
|---|---|---|---|
| POST | `/api/v1/token/` | Login — get access + refresh tokens 
| POST | `/api/v1/token/refresh/` | Get new access token via refresh 
| GET | `/api/v1/snippets/` | Overview: total count + snippet list 
| POST | `/api/v1/snippets/` | Create a new snippet 
| GET | `/api/v1/snippets/<id>/` | Get snippet detail (own only) 
| PUT | `/api/v1/snippets/<id>/` | Full update of snippet 
| PATCH | `/api/v1/snippets/<id>/` | Partial update of snippet 
| DELETE | `/api/v1/snippets/<id>/` | Delete snippet; returns remaining list 
| GET | `/api/v1/tags/` | List all tags 
| GET | `/api/v1/tags/<id>/` | Tag detail + linked snippets 

> **Auth**: All CRUD endpoints require `Authorization: Bearer <access_token>` header.

See [`postman_collection.json`](postman_collection.json) for ready-to-import API test collection.

---

## Database Schema

See [`schema.md`](schema.md) for the full ER diagram.

---

## Project Structure

```
snipbox-be/
snipbox
    ├── Dockerfile
    ├── README.md
    ├── README_local.md
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
- Access token lifetime: 60 minutes
- Refresh token lifetime: 1 day
