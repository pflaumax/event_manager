# Event Management System – MVP & Development Roadmap

## MVP Goal:
Build a basic Django web application where users can:
- Register with role choice: visitor or creator, and log in / log out

- Create events with basic details (creators)
- View a list of their own events with all details (creators)
- Cancel their own events with all its visitors registrations (creators)

- Browse published (and search bu status) events (visitors)
- View all event details with reg. button or reg. status (visitors)
- Register as participants for events and cancellation (visitors)

- Use PostgreSQL as the database
- Wrap into Docker container in the end of MVP part

---

## Setup Phase (Initial Environment)

- [x] Set up a Python virtual environment
- [x] Install Django and psycopg2-binary pips
- [x] Create Django project
- [x] Configure PostgreSQL connection in `settings.py`
- [x] Create `.env` file for environment variables
- [x] Add `.gitignore` and initialize Git repository

---

## Database and Models

- [x] Create `users` app with a custom user model (email-based login)
- [x] Create `events` app:
    - [x] `Event` model (title, description, date, location, created_by)
    - [x] `Registration` model for registration for event (user, event, timestamp)
- [x] Run migrations
- [x] Add initial data via fixtures or admin panel

---

## User Authentication

- [x] Implement Django authentication
- [x] Add registration, login, logout functionality
- [x] Protect event manipulation for logged-in users only (as per role)
- [x] Make Django shell function user registration tests 
 
---

## Templates and Frontend

- [x] Create Django templates and implement functionality for:
    - [x] Start page (index)
    - [x] Login / Sign up pages
    - [x] Home page: create event, my own events, browse events, my registrations

    - [x] Create new event page (creator)
    - [x] My own events (creator)
    - [x] Cancel my own created event (creator)

    - [x] Browse events (visitor)
    - [x] Event details with registration or its status (visitor)
    - [x] My registrations for events with cancel function (visitor)

    - [x] Display feedback via Django messages

---

## Email Notifications

- [x] Use Django console email backend
- [x] Send email confirmation for account registration (token)
- [x] Send confirmation email on successful event registration 
- [x] Send notification emails for all registered visitors on cancelled event by creator
---

## Post-MVP Goals (Priority check)

- [x] Event filtering and search
- [x] Event image upload
- [x] Add edit feature for events 
- [x] Export registrations as CSV
- [x] Unit tests (event, registrations, users: models, views)
- [ ] Add Docker support (Dockerfile + docker-compose)
- [ ] Add API (Django REST framework) for all pages
- [ ] Add responsive frontend design (bootstrap/tailwind)
- [ ] Set image upload into production (railway + whitenoise/staticfiles)
- [ ] Deploy to production with Docker and Postgres

## After all: ideas to add

- [ ] Implement API payment gateway (PayPal)