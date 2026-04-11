# Installation Guide

This guide covers getting OliveERP running locally or with Docker.

## Prerequisites

- Python 3.11+
- MySQL Server 8.0+
- Redis (for Celery)
- Git

## Getting Started

### Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd olive_erp
   ```

2. **Create and activate a virtual environment**:
   ```bash
   # Create a virtual environment
   python -m venv venv

   # Activate on macOS/Linux
   source venv/bin/activate

   # Activate on Windows
   venv\Scripts\activate

   # Deactivate
   deactivate
   
   ```

3. **Set up environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env with your database and secret key details
   ```

4. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

5. **Initialize Database**:
   ```bash
   python manage.py migrate
   python manage.py create_initial_data
   ```

   *Note: If the currency dropdown is empty during setup, ensure `create_initial_data` was run.*

6. **Create Admin User**:
   ```bash
   python manage.py createsuperuser
   ```

7. **Run the Server**:
   ```bash
   python manage.py runserver
   ```

### Docker Setup

```bash
docker-compose up --build
```

The Docker setup will:
- Build the Python 3.11+ application container
- Launch MySQL 8.0+ container
- Launch Redis container for Celery
- Apply database migrations
- Start the Django development server

## Configuration

### Environment Variables

Key environment variables required in `.env`:

| Variable | Description | Example |
|----------|-------------|---------|
| `SECRET_KEY` | Django secret key | Generate a secure random string |
| `DEBUG` | Debug mode | `True` or `False` |
| `DATABASE_URL` | MySQL connection | `mysql://user:pass@localhost:3306/olive_erp` |
| `REDIS_URL` | Redis connection | `redis://localhost:6379/0` |
| `EMAIL_HOST` | SMTP server | `smtp.gmail.com` |
| `EMAIL_PORT` | SMTP port | `587` |
| `EMAIL_USE_TLS` | Use TLS | `True` |
| `WAGTAIL_SITE_NAME` | Site name | `OliveERP` |

### Database Setup

The application uses Django migrations. After configuration:

```bash
python manage.py migrate
python manage.py create_initial_data
```

### Celery Setup

For background task processing:

```bash
# Start Redis (if running locally)
redis-server

# Start Celery worker
celery -A wagtailerp worker -l info

# Start Celery beat (for scheduled tasks)
celery -A wagtailerp beat -l info
```

## Troubleshooting

### Common Issues

**Currency dropdown empty:**
Run `python manage.py create_initial_data` to seed initial currencies.

**Database connection errors:**
Verify `DATABASE_URL` in `.env` matches your MySQL credentials.

**Redis connection errors:**
Ensure Redis is running on the port specified in `REDIS_URL`.

**Port conflicts:**
The default server runs on port 8000. Use `--port 8080` to change.

### Development Commands

```bash
# Run tests
python manage.py test

# Check system
python manage.py check

# Create migrations
python manage.py makemigrations

# Shell access
python manage.py shell
```

## Production Deployment

See [ARCHITECTURE.md](ARCHITECTURE.md) for production architecture details including:
- Web server configuration (Gunicorn)
- Database (PostgreSQL recommended)
- Static file handling (WhiteNoise)
- Render.com deployment blueprint