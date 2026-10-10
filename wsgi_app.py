#!/usr/bin/env python3
import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent / 'cr_process_automation'
sys.path.insert(0, str(BASE_DIR))

# Sets DJANGO_SETTINGS_MODULE and builds the WSGI application (module-level
# ``application`` in cr_process_automation/wsgi.py). Import it once and reuse it.
from cr_process_automation.wsgi import application

if __name__ == '__main__':
    from django.conf import settings

    # ``django.contrib.staticfiles`` only serves assets automatically through
    # runserver. When serving through a real WSGI server (waitress/gunicorn)
    # during development, wrap the app so /static/... keeps working.
    # In production (DEBUG=False) static files must come from collectstatic
    # via a reverse proxy or a static-serving middleware.
    if settings.DEBUG:
        from django.contrib.staticfiles.handlers import StaticFilesHandler
        app = StaticFilesHandler(application)
    else:
        app = application

    import gc
    gc.freeze()
    gc.collect()

    from waitress import serve

    host = os.getenv('WSGI_HOST', '0.0.0.0')
    try:
        port = int(os.getenv('WSGI_PORT', '8000'))
    except ValueError:
        raise SystemExit(f"Invalid WSGI_PORT value: {os.getenv('WSGI_PORT')!r}")

    print(f"Serving CR Process Automation on http://{host}:{port} "
          f"(DEBUG={settings.DEBUG})", flush=True)
    serve(app, host=host, port=port)
