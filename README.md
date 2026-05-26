# Hulu Farm — Backend API

Django 5 + PostgreSQL + JWT backend for **auth** and **community forum**.

---

## Stack

| Layer | Tech |
|-------|------|
| Framework | Django 5 + Django REST Framework |
| Database | PostgreSQL 16 |
| Auth | JWT via `djangorestframework-simplejwt` |
| Docs | OpenAPI 3 via `drf-spectacular` (Swagger + ReDoc) |

---

## Quick Start (local)

### 1. Clone & enter

```bash
git clone <your-repo>
cd hulu_farm_backend
```

### 2. Create virtual env & install deps

```bash
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configure environment

```bash
cp .env.example .env
# Edit .env — set DB_PASSWORD and SECRET_KEY
```

### 4. Create the database

```bash
# Make sure PostgreSQL is running, then:
createdb hulu_farm
```

### 5. Run migrations

```bash
python manage.py migrate
python manage.py createsuperuser
```

### 6. Start the server

```bash
python manage.py runserver
```

API: http://localhost:8000/api/v1/  
Swagger docs: http://localhost:8000/api/docs/  
Admin: http://localhost:8000/admin/

---

## Docker (optional)

```bash
cp .env.example .env
# set DB_HOST=db in .env
docker compose up --build
```

---

## API Reference

### Auth  `POST /api/v1/auth/`

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/register/` | Public | Register new user, returns tokens |
| POST | `/login/` | Public | Login, returns access + refresh tokens |
| POST | `/logout/` | Bearer | Blacklist refresh token |
| POST | `/token/refresh/` | Public | Rotate access token |
| GET  | `/me/` | Bearer | Get current user profile |
| PATCH | `/me/` | Bearer | Update profile (username, bio, avatar…) |
| POST | `/change-password/` | Bearer | Change password |
| GET  | `/users/<username>/` | Public | Public profile |

#### Register

```json
POST /api/v1/auth/register/
{
  "email": "abebe@example.com",
  "username": "abebe",
  "full_name": "Abebe Bikila",
  "password": "strongpass123",
  "password2": "strongpass123"
}
```

Response `201`:
```json
{
  "user": { "id": "...", "email": "...", "username": "abebe", ... },
  "tokens": { "access": "eyJ...", "refresh": "eyJ..." }
}
```

#### Login

```json
POST /api/v1/auth/login/
{ "email": "abebe@example.com", "password": "strongpass123" }
```

#### Using the token

```
Authorization: Bearer <access_token>
```

---

### Forum  `GET|POST /api/v1/forum/`

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/categories/` | Public | List all categories |
| GET | `/posts/` | Public | List published posts |
| POST | `/posts/` | Bearer | Create post |
| GET | `/posts/<slug>/` | Public | Post detail + comments |
| PATCH | `/posts/<slug>/` | Owner | Edit post |
| DELETE | `/posts/<slug>/` | Owner | Delete post |
| POST | `/posts/<slug>/like/` | Bearer | Toggle like on post |
| GET | `/posts/<slug>/comments/` | Public | Top-level comments |
| POST | `/posts/<slug>/comments/` | Bearer | Add comment / reply |
| GET | `/comments/<id>/` | Public | Single comment |
| PATCH | `/comments/<id>/` | Owner | Edit comment |
| DELETE | `/comments/<id>/` | Owner | Delete comment |
| POST | `/comments/<id>/like/` | Bearer | Toggle like on comment |
| GET | `/my-posts/` | Bearer | Current user's posts |

#### Query params for `GET /posts/`

| Param | Example | Notes |
|-------|---------|-------|
| `search` | `?search=tomato` | searches title, body, author |
| `category` | `?category=3` | filter by category id |
| `author__username` | `?author__username=abebe` | |
| `ordering` | `?ordering=-views_count` | `-created_at`, `views_count` |
| `page` | `?page=2` | 20 per page |
| `page_size` | `?page_size=10` | max 100 |

#### Create post

```json
POST /api/v1/forum/posts/
Authorization: Bearer <token>
{
  "title": "Best crops for highland Ethiopia",
  "body": "...",
  "category_id": 1,
  "status": "published"
}
```

#### Nested reply

```json
POST /api/v1/forum/posts/<slug>/comments/
{
  "body": "Great post!",
  "parent": null           // omit or null for top-level
}

// Reply to a comment
{
  "body": "I agree!",
  "parent": "uuid-of-parent-comment"
}
```

---

## Project Structure

```
hulu_farm_backend/
├── config/
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── apps/
│   ├── core/           # shared pagination, permissions
│   ├── accounts/       # User model, auth endpoints
│   └── forum/          # Category, Post, Comment, Like
├── manage.py
├── requirements.txt
├── Dockerfile
└── docker-compose.yml
```
