# Backend — Local Food Waste Minimizer

Django REST Framework backend implementing custom user roles, inventory control, marketplace ordering, donation management, cross-module analytics, and rate-limited API endpoints.

---

## 🛠️ Requirements

- Python 3.10+ (Tested on Python 3.13)
- PostgreSQL (or SQLite for local development/testing)
- Redis & Celery (optional, for async task processing)

---

## 🚀 Setup & Execution

1. **Navigate to backend directory**:
   ```bash
   cd backend
   ```

2. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Environment Variables**:
   ```bash
   cp .env.example .env
   ```
   > **Note**: `DB_PASSWORD` is required in `.env` for PostgreSQL mode as hardcoded fallbacks have been removed for security.

4. **Run Database Migrations**:
   ```bash
   python manage.py migrate
   ```

5. **Start Development Server**:
   ```bash
   python manage.py runserver
   ```
   The backend API will be available at `http://localhost:8000/api/v1/`.

---

## 🧪 Testing & Verification

Run the automated test suite with SQLite:
```bash
DB_ENGINE=django.db.backends.sqlite3 DB_NAME=:memory: python manage.py test --noinput
```
Or via pytest:
```bash
DB_ENGINE=django.db.backends.sqlite3 DB_NAME=/tmp/test.sqlite3 pytest -v
```

Manual verification scripts are available in [`backend/scripts/`](file:///e:/Local%20Food%20Waste/Local-Food-Waste-Minimizer/backend/scripts/).

---

## 🔑 Environment Variables Reference

- `DEBUG`: Set to `True` for development; `False` enables production SSL/CSRF/HSTS security headers.
- `SECRET_KEY`: Django secret key string.
- `ALLOWED_HOSTS`: Comma-separated allowed hostnames.
- `DB_ENGINE`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`: Database connection parameters.
- `EMAIL_BACKEND`: Defaults to `django.core.mail.backends.console.EmailBackend` in development.
- `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_USE_TLS`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`: SMTP server credentials for production email delivery.