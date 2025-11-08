"""WSGI entrypoint for Eleven Views Opportunity Engine."""

from dashboard import app as application

# Vercel and other WSGI hosts look for a module-level `app` or `application`
app = application

if __name__ == "__main__":
    app.run()
