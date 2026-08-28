"""
Punto de entrada de la aplicación para Gunicorn y para ejecución local.

- Para producción (Render):   gunicorn app:app
- Para desarrollo local:      python app.py   (usa el puerto 5000/8000 según PORT)
"""
import os

from backend.app import app

if __name__ == "__main__":
    # En desarrollo usamos un puerto por defecto 5000 (o PORT si está definido).
    puerto = int(os.getenv("PORT", "5000"))
    debug = os.getenv("FLASK_DEBUG", "1") == "1"
    # host=0.0.0.0 permite acceder desde otros dispositivos / contenedores.
    app.run(host="0.0.0.0", port=puerto, debug=debug)
