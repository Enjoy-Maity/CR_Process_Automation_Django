"""
WSGI config for cr_process_automation project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/6.0/howto/deployment/wsgi/

Copy-on-Write (CoW) Optimization:
- Use with Gunicorn: gunicorn --preload cr_process_automation.wsgi:application
- The --preload flag loads this module in the master process BEFORE forking workers
- gc.freeze() then moves all loaded objects to a permanent generation, preventing
  Python's ref-count updates from triggering unnecessary memory page copies
- Typical memory savings: 10-30% per worker process
"""

import os
import gc
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cr_process_automation.settings')

application = get_wsgi_application()

gc.freeze()
gc.collect()
