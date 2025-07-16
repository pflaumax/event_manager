# Event Management System

A Django-based event management platform that brings people together! Whether you're organizing a tech meetup, workshop, or conference, this system makes it easy to create, manage, and attend events.

## Table of Contents

- [What This Project Does](#what-this-project-does)
- [Key Features](#key-features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Screenshots](#screenshots)
- [Getting Started](#getting-started)
- [How to Use](#how-to-use)
- [API Endpoints](#api-endpoints)
- [Running Tests](#running-tests)
- [Models Overview](#models-overview)
- [Development Progress](#development-progress)
- [Email Configuration](#email-configuration)
- [Contributing](#contributing)
- [License](#license)
- [Design Decisions](#design-decisions)
- [Known Issues](#known-issues)
- [Support](#support)
- [Acknowledgments](#acknowledgments)

## What This Project Does

Think of this as a simplified version of Eventbrite or Meetup. It's designed around two types of users:
- **Event Creators** who can organize and manage events
- **Visitors** who can discover and register for events

Your role determines what you can do in the system. Creators focus on organizing, while visitors focus on attending - no confusion, no overlap!

## Key Features

### For Event Creators
- Create and manage your own events with detailed information
- View only the events you've created
- Edit event details when plans change
- Cancel events if needed (automatically notifies all registered participants)
- Export participant lists as CSV files for easy management

### For Visitors  
- Browse all available public events with filtering and search
- View detailed event information with registration status
- Register for events you're interested in
- Cancel your registration if you can't make it
- View all events you've signed up for in one place

### Smart System Features
- **Role-based access**: You can only do what your role allows
- **Email notifications**: Get confirmations and updates about events
- **Event filtering**: Search by status, date, or other criteria
- **Image uploads**: Add photos to make events more attractive
- **Automatic status updates**: Events automatically become "completed" after their date
- **Email authentication**: Login with your email instead of a username
- **Responsive design**: Works great on mobile and desktop

## Tech Stack

- **Backend**: Django (Python web framework)
- **Database**: PostgreSQL
- **Authentication**: Custom user model with email login and token verification
- **API**: Django REST Framework for mobile/integration support
- **Frontend**: Django templates for responsive design
- **Containerization**: Docker support for easy deployment
- **Testing**: Comprehensive unit tests for models and views

## Project Structure

```
event_management/
├── apps/
│   ├── events/          # Everything related to events and registrations
│   └── users/           # User authentication and role management
├── templates/           # HTML templates for the web interface
├── static/             # CSS, JavaScript, and other static files
├── media/              # Uploaded files (like event images)
├── tests/              # Test files to ensure everything works
├── docker-compose.yml  # Docker configuration
├── dockerfile         # Container setup
└── event_manager/      # Main Django project settings
```

## Screenshots

*[I will add screenshots here - suggested shots:]*
- Registration page showing role selection
- Event creator dashboard with event management
- Event listing page for visitors with search/filter
- Event detail page with registration button
- Event creation form with image upload
- My registrations page for visitors

## Getting Started

### Prerequisites
- Python 3.8+
- PostgreSQL
- Git
- Docker (optional, for containerized deployment)

### Quick Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/pflaumax/event_manager
   cd event_manager
   ```

2. **Set up your virtual environment**
   ```bash
   python -m venv event_venv
   source event_venv/bin/activate  
   # On Windows: event_venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your database credentials
   ```

5. **Set up your database**
   ```bash
   # Make sure PostgreSQL is running
   python manage.py migrate
   ```

6. **Create a superuser (optional)**
   ```bash
   python manage.py createsuperuser
   ```

7. **Start the development server**
   ```bash
   python manage.py runserver
   ```

Visit `http://localhost:8000` and you're ready to go!

### Using Docker

For a containerized setup:

```bash
# Build and run with Docker Compose
cd event_manager
docker compose up --build

# Or run individual commands
docker build -t event_manager .
docker run -p 8000:8000 event_manager
```

## How to Use

### Getting Started as a User

1. **Sign up**: Choose whether you're an Event Creator or Visitor during registration
2. **Verify email**: Check your email for a confirmation token
3. **Log in**: Use your email and password
4. **Explore**: Your dashboard will show different options based on your role

### For Event Creators
- Click "Create Event" to add a new event with description, date, location, and images
- Use "My Events" to view and manage all your created events
- Edit event details or cancel events when needed
- Export participant lists as CSV files for offline management
- Cancelled events automatically notify all registered participants

### For Visitors
- Browse the event list with filtering options (status, date, location)
- Use the search functionality to find specific events
- Click "Register" on events you want to attend
- View your registrations in "My Events" section
- Cancel registrations if your plans change

## API Endpoints

The system includes a full REST API built with Django REST Framework:

### Authentication
- `POST /api/users/register/` - Register User
- `POST /api/users/login/` - Login
- `POST /api/token/` - Get authentication token

### User Profile
- `GET /api/users/profile/` - Get Profile
- `PUT /api/users/profile/` - Update Profile (PUT)
- `PATCH /api/users/profile/` - Update Profile (PATCH)
- `GET /api/users/my_registrations/` - Get My Registrations

### Events
- `GET /api/events/` - List All Events
- `GET /api/events/?status=published` - List Events with Filters
- `GET /api/events/?search=test` - Search Events
- `GET /api/events/?ordering=date` - Order Events
- `POST /api/events/` - Create Event
- `GET /api/events/{id}/` - Get Event Details
- `PUT /api/events/{id}/` - Update Event (PUT)
- `PATCH /api/events/{id}/` - Update Event (PATCH)
- `DELETE /api/events/{id}/` - Delete Event

### Event Custom Actions
- `GET /api/events/my_events/` - Get My Events (Creator Only)
- `GET /api/events/upcoming/` - Get Upcoming Events
- `POST /api/events/{id}/cancel/` - Cancel Event
- `GET /api/events/{id}/registrations/` - Get Event Registrations (Creator Only)
- `GET /api/events/stats/` - Get Event Statistics (Creator Only)

### Event Registrations
- `GET /api/registrations/` - List My Registrations
- `POST /api/registrations/` - Register for Event
- `GET /api/registrations/{id}/` - Get Registration Details
- `DELETE /api/registrations/{id}/` - Cancel Registration
- `GET /api/registrations/upcoming/` - Get Upcoming Registrations

### User Management (Admin)
- `GET /api/users/` - List All Users
- `GET /api/users/{id}/` - Get User Details
- `PUT /api/users/{id}/` - Update User
- `DELETE /api/users/{id}/` - Delete User

### API Documentation
**Full API documentation is available via Postman collection:**

1. **Import the collection**: Download the `Event Management API.postman_collection.json` file from the repository
2. **Open Postman**: Import the collection file into your Postman workspace
3. **Set environment variables**: 
   - `base_url`: Your API base URL (e.g., `http://localhost:8000`)
   - `access_token`: Will be automatically set after login
4. **Authentication**: Use the "TOKEN" request to get your access token, which will be automatically saved for other requests

The Postman collection includes:
- Pre-configured requests for all endpoints
- Request examples with sample data
- Environment variable management
- Automatic token handling

**Alternative**: You can also view the API documentation by visiting `/api/docs/` when running the server (if DRF documentation is enabled).

## Running Tests

The project includes comprehensive tests to ensure everything works correctly:

```bash
# Run all tests
python manage.py test

# Run tests for specific app
python manage.py test apps.events
python manage.py test apps.users

# Run with coverage
coverage run manage.py test
coverage report
```

## Models Overview

### User Model
- Email-based authentication with token verification
- Role field (Creator/Visitor)
- Standard Django user fields

### Event Model
- Title, description, date, location
- Creator (foreign key to User)
- Status (published, completed, cancelled)
- Image upload capability
- Automatic status updates

### Registration Model
- Links users to events
- Timestamps for registration/cancellation
- Status tracking

## Development Progress

### ✅ MVP Completed
- **Setup Phase**: Virtual environment, Django setup, PostgreSQL configuration
- **Database & Models**: Custom user model, Event and Registration models
- **Authentication**: Email-based login, registration with role selection
- **Templates & Frontend**: Complete web interface for all user roles
- **Email Notifications**: Account verification, registration confirmations, cancellation alerts

### ✅ Post-MVP Features Completed
- **Enhanced Features**: Event filtering, search, image uploads, event editing
- **Data Export**: CSV export for participant lists
- **Testing**: Comprehensive unit tests for models and views
- **Containerization**: Docker support for easy deployment
- **API**: Full REST API with Django REST Framework
- **Responsive Design**: Bootstrap integration for mobile-friendly interface

### 🔄 Current Focus
- Performance optimization
- UI/UX improvements

### 📋 Future Enhancements
- Event categories and tags
- Attendee limits and waiting lists
- Social features (comments, ratings)
- Payment integration
- Calendar integration

## Email Configuration

The system uses Django's email backend for notifications:
- Development: Console backend (emails appear in terminal)
- Production: Configure SMTP settings in `settings.py` and `.env`

Email notifications include:
- Account verification tokens
- Event registration confirmations
- Event cancellation notifications to all participants

## Contributing

This is a portfolio project, but feedback and suggestions are welcome! If you spot a bug or have ideas for improvements:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new features
5. Submit a pull request

## License

This project is open source and available under the [MIT License](LICENSE).

## Design Decisions

### Why Role-Based Access?
Instead of giving everyone all permissions, the system uses clear roles. This makes the interface cleaner and prevents confusion - creators focus on creating, visitors focus on attending.

### Why Email Authentication?
Email is more intuitive than usernames for most people, and it's required for notifications anyway.

### Why Separate Apps?
The `users` and `events` apps keep related functionality organized and make the codebase easier to maintain and extend.

### Why Docker?
Containerization ensures consistent deployment across different environments and makes it easy for others to run the project.

## Known Issues

- Event timezone handling needs improvement
- File upload need configuration

## Support

If you run into issues:
1. Check the test files for usage examples
2. Look at the `tests_model_logic.MD` file for model behavior
3. Check the `todo.MD` file for known limitations
4. Review the API documentation in Postman

## Acknowledgments

Built as a portfolio project to demonstrate:
- Django best practices
- Role-based access control
- RESTful API design
- Test-driven development
- Clean code architecture
- Full-stack development skills

---

*Happy event organizing!*