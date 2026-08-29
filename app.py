"""
Punto de entrada de la aplicación para Gunicorn y ejecución local.

- Producción (Render):  gunicorn app:app  (lo usa el Procfile con $PORT)
- Local:                python app.py
"""
import os

from backend.app import app

if __name__ == "__main__":
    puerto = int(os.getenv("PORT", "8000"))
    debug = os.getenv("DEBUG", "false").lower() in ("1", "true", "yes")
    app.run(host="0.0.0.0", port=puerto, debug=debug)
