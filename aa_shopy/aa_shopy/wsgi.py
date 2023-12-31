"""
WSGI config for aa_shopy project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/wsgi/
"""

import os
import sys

# Assuming your virtual environment is located at /home/ubuntu/django_ecommerce_website/env
venv_path = '/home/ubuntu/django_ecommerce_website/env'
sys.path.append(venv_path)

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'aa_shopy.settings')

application = get_wsgi_application()
