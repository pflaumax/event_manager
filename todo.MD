# Event Management System – MVP & Development Roadmap

## MVP Goal:
Build a basic Django web application where users can:
- Register and log in
- Create events with basic details
- View a list of their own events
- Browse upcoming events created by other users
- Register as participants for events
- Use PostgreSQL as the database

---

## Setup Phase (Initial Environment)

- [x] Set up a Python virtual environment
- [x] Install Django and psycopg2-binary
- [x] Create Django project: `event_manager`
- [x] Configure PostgreSQL connection in `settings.py`
- [x] Create `.env` file for environment variables
- [x] Add `.gitignore` and initialize Git repository

---

## Database and Models

- [x] Create `users` app with a custom user model (email-based login)
- [ ] Create `events` app:
    - [ ] `Event` model (title, description, date, location, created_by)
    - [ ] `Registration` model (user, event, timestamp)
- [ ] Run migrations
- [ ] Add initial data via fixtures or admin panel

---

## User Authentication

- [ ] Implement Django authentication
- [ ] Add registration, login, logout functionality
- [ ] Protect event creation for logged-in users only

---

## Templates and Frontend

- [ ] Create Django templates for:
    - [ ] Home page (event list)
    - [ ] Login / Register pages
    - [ ] Create event page
    - [ ] My events
    - [ ] Event detail with "Join" functionality
    - [ ] Display feedback via Django messages

---

## Email Notifications

- [ ] Use Django console email backend
- [ ] Send confirmation email on successful event registration

---

## Post-MVP Goals

- [ ] Add Docker support (Dockerfile + docker-compose)
- [ ] Add pagination for event listing
- [ ] Add real-time chat using Django Channels
- [ ] Calendar integration (ICS download or Google Calendar link)
- [ ] Event image upload
- [ ] Event filtering and search
- [ ] Payment gateway (Stripe/PayPal)
- [ ] Deploy to production (Render/Fly.io/DigitalOcean)

---

## Optional Enhancements

- [ ] Create REST API using Django REST Framework
- [ ] Add responsive frontend design
- [ ] Export registrations as CSV
- [ ] Create dashboard for analytics

---

## Deployment Plan

1. Local deployment using PostgreSQL
2. Dockerize application
3. Deploy to a hosting platform

