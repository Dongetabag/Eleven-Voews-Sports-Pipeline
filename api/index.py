"""Vercel serverless entrypoint for the Eleven Views Flask app."""

from dashboard import app as application  # Vercel looks for `app` or `application`

# Alias required by Vercel's Python runtime
app = application
