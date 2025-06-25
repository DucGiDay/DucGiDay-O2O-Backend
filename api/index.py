import sys
import os

# Thêm đường dẫn project vào sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "django_postgresql"))

from django_postgresql.wsgi import application

def handler(environ, start_response):
    return application(environ, start_response)