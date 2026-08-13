"""
ASGI config for cr_process_automation project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/6.0/howto/deployment/asgi/

Copy-on-Write (CoW) Optimization:
- Use with Uvicorn: uvicorn --workers 4 cr_process_automation.asgi:application
- Or with Gunicorn + Uvicorn workers: gunicorn -k uvicorn.workers.UvicornWorker --preload cr_process_automation.asgi:application
- gc.freeze() prevents Python's ref-count updates from triggering memory page
  copies when the master process forks multiple worker processes
"""

import os
import gc
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cr_process_automation.settings')

application = get_asgi_application()

gc.freeze()
gc.collect()
