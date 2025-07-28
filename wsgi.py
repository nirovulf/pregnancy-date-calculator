"""
WSGI entry point for production deployment with gunicorn
"""
from main import app

if __name__ == "__main__":
    app.run()
