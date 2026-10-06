# CR Process Automation Django

This is a Django-based web application for automating Change Request (CR) processes.

## Deployment

### Environment Variables

Create a `.env` file in `cr_process_automation/dashboard/` or set environment variables. Common variables:

- `DJANGO_SECRET_KEY` - Secret key for Django
- `DJANGO_DEBUG` - `False` for production
- `DJANGO_ALLOWED_HOSTS` - Comma-separated list of allowed hosts (e.g. `example.com,localhost`)
- `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT` - PostgreSQL settings (master)
- `DB_NAME_REPLICA`, `DB_USER_REPLICA`, `DB_PASSWORD_REPLICA`, `DB_HOST_REPLICA`, `DB_PORT_REPLICA` - Replica DB (optional)

### Static Files

Collect static files before deployment:

```bash
cd cr_process_automation
../.venv/bin/python manage.py collectstatic --noinput
```

### Database Migrations

```bash
cd cr_process_automation
../.venv/bin/python manage.py migrate
../.venv/bin/python manage.py migrate --database=replica
```

### WSGI Deployment

#### Using Gunicorn (Linux/Unix)

```bash
cd cr_process_automation
gunicorn --bind 0.0.0.0:8000 cr_process_automation.wsgi:application
```

With preloading (recommended for memory optimization):

```bash
gunicorn --preload --bind 0.0.0.0:8000 cr_process_automation.wsgi:application
```

#### Using Waitress (Cross-platform: Windows/Linux)

Waitress is included as a WSGI server option. Install if not present: `pip install waitress`.

```bash
cd /home/enjoymaity/Projects/Python_projects/CR_Process_Automation_Django
python wsgi_app.py
```

Or directly:

```bash
waitress-serve --host 0.0.0.0 --port 8000 cr_process_automation.cr_process_automation.wsgi:application
```

#### Using uWSGI (Linux)

```bash
uwsgi --http :8000 --module cr_process_automation.wsgi:application --master --processes 4 --threads 2
```

### Reverse Proxy

For production, use a reverse proxy (Nginx/Apache) in front of the WSGI server. Configure SSL and serve static files from `staticfiles/` directory.

### Cross-platform Notes

- The application is WSGI-compatible and works on both Windows and Linux.
- Use Waitress on Windows; Gunicorn/uWSGI on Linux.
- File paths use `pathlib.Path` for cross-platform compatibility.
- Environment variables control all deployment-specific settings.
