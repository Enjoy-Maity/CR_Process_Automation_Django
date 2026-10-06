#!/usr/bin/env python3
import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent / 'cr_process_automation'
sys.path.insert(0, str(BASE_DIR))

from cr_process_automation.wsgi import application

if __name__ == '__main__':
    from django.core.wsgi import get_wsgi_application
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cr_process_automation.settings')
    app = get_wsgi_application()
    import gc
    gc.freeze()
    gc.collect()
    from waitress import serve
    host = os.getenv('WSGI_HOST', '0.0.0.0')
    port = int(os.getenv('WSGI_PORT', '8000'))
    serve(app, host=host, port=port)
