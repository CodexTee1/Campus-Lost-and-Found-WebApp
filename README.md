# BBSF Lost & Found Portal

A Django-based campus Lost & Found web application that helps students report missing/found items, search listings, and submit retrieval claims.

## Project Overview

This system provides:

- Student signup/login using matric number format
- Admin/superuser login support (e.g. `admin`, `admin2`)
- Public homepage with item listings, category filter, and global search
- Item reporting form with optional image upload
- Retrieval workflow with claim notes
- Admin claim visibility through Django admin and API endpoints

## Tech Stack

- Python
- Django
- SQLite (default)
- Tailwind (CDN in templates)
- Django messages framework

## Folder Structure

- `core/`:
  - Authentication + homepage views
  - Core templates (`base`, `index`, `login`, `signup`, `contact`)
- `item/`:
  - Item models
  - Reporting/retrieval views
  - Claim APIs
  - Admin registrations
- `LOSTandFOUND/settings.py`:
  - App settings and `.env` secret key loading

## Features

### 1. Authentication

- Signup (`/signup/`) validates:
  - Matric format: `BU23CSC1109` style (`BU + 2 digits + 3 uppercase letters + 4 digits`)
  - Password minimum length
  - Unique matric number
  - Password not previously used
- Login (`/login/`) supports:
  - Matric-number users
  - Admin/superuser usernames
- Logout (`/logout/`) clears session and redirects to login.

### 2. Homepage

- Shows:
  - Available item count
  - Category count
  - Recent reports
  - Lost and found sections
- Supports:
  - Category filtering (`?category=<id>`)
  - Search across all items (`?q=<term>`)

### 3. Report Item

- Route: `/items/report/`
- Requires login
- Saves:
  - category, name, description, location, date, status, image
  - `reported_by` auto-set to current user

### 4. Retrieve Item

- Route: `/items/retrieve/`
- Requires login
- Shows retrievable items (`FOUND` + public)
- Accepts claim note and creates claim request
- Prevents duplicate pending claims by same user for same item

### 5. Claim Request Tracking

- `ClaimRequest` model tracks:
  - item
  - claimed_by
  - note
  - status (`pending/approved/rejected`)
  - timestamps

### 6. Admin Capabilities

- Django admin can manage:
  - Categories
  - Items
  - Claim requests
- Superusers can view claim records in admin list views.

## API Endpoints

### Submit Claim

- **POST** `/api/claims/submit/`
- Auth: logged-in user session
- Body (`x-www-form-urlencoded`):
  - `item_id`
  - `claim_note`
- Response:
  - `201` on success
  - `400/404` for validation or unavailable item

### Admin Claims List

- **GET** `/api/admin/claims/`
- Auth: staff/superuser session
- Response:
  - JSON array of claim requests

## URL Map

- `/` → Home
- `/contact/` → Contact page
- `/login/` and `/signin/` → Login
- `/signup/` → Signup
- `/logout/` → Logout
- `/items/report/` → Report item
- `/items/retrieve/` → Retrieve item
- `/api/claims/submit/` → Submit claim API
- `/api/admin/claims/` → Admin claim API
- `/admin/` → Django admin

## Environment Variables

Secrets are managed with `.env`.

Required:

- `DJANGO_SECRET_KEY`

`settings.py` loads `.env` from project root.

## Setup Instructions

1. Create and activate virtual environment
2. Install dependencies
3. Add `.env` file:

```env
DJANGO_SECRET_KEY=your-secret-key
```

4. Run migrations:

```bash
python manage.py migrate
```

5. Create superuser:

```bash
python manage.py createsuperuser
```

6. Start server:

```bash
python manage.py runserver
```

## Postman Testing (Session + CSRF)

For endpoints protected by Django session auth:

1. `GET /login/` to receive `csrftoken`
2. `POST /login/` with:
   - `matric_number`
   - `password`
   - `csrfmiddlewaretoken`
3. Include headers on POST:
   - `X-CSRFToken: <csrftoken>`
   - `Referer: http://127.0.0.1:8000/login/`
4. Reuse same cookie jar/session for API calls

## Data Models Summary

### Category

- `name`

### Item

- `category`
- `name`
- `description`
- `location`
- `date_lost_or_found`
- `status` (`lost/found/claimed/returned/archived`)
- `image`
- `reported_by`
- `claim_notes`
- `is_verified`
- `is_public`
- `created_at`, `updated_at`

### ClaimRequest

- `item`
- `claimed_by`
- `note`
- `status` (`pending/approved/rejected`)
- `created_at`, `updated_at`

## Known Notes

- Current project uses SQLite and template-driven UI for quick deployment.
- Authentication is session-based for web routes and current claim APIs.
- JWT setup exists in settings footprint but session auth is primary for current API routes.

## Future Improvements

- Add dedicated claim approval/rejection action endpoint for admins
- Add email notifications to admins on new claim request
- Add user dashboard ("My Reports", "My Claims")
- Add pagination and sort options
- Harden production settings (`DEBUG`, `ALLOWED_HOSTS`, security headers)

