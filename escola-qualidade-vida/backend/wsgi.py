"""WSGI entrypoint used by Docker/Gunicorn.

Importing main keeps the existing startup routine that waits for the database,
creates missing tables, and can prepare the first user when configured.
"""

from main import app
