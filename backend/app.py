"""
Fábrica de aplicación Flask.

Configura CORS (incluido preflight OPTIONS para /api/*), inicializa la base
de datos al arrancar y registra los blueprints de las rutas.
"""
import os

import werkzeug
from flask import Flask, jsonify, request
from flask_cors import CORS

from .config import Config, load_env_file
from .conexion import inicializar_bd


def crear_app():
    """Crea y configura la instancia de la aplicación Flask."""
    load_env_file()

    app = Flask(__name__, static_folder="../frontend", static_url_path="/")

    # Habilitar CORS globalmente para todas las rutas /api/* aceptando
    # cualquier origen, y manejar el preflight OPTIONS automáticamente.
    CORS(
        app,
        resources={r"/api/*": {"origins": "*"}},
        methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["Content-Type", "Authorization"],
        supports_credentials=True,
    )

    # Registro de blueprints
    from .rutas.auth import auth_bp
    from .rutas.categorias import categorias_bp
    from .rutas.movimientos import movimientos_bp
    from .rutas.analitica import analitica_bp

    app.register_blueprint(auth_bp, url_prefix="/api")
    app.register_blueprint(categorias_bp, url_prefix="/api/categorias")
    app.register_blueprint(movimientos_bp, url_prefix="/api")
    app.register_blueprint(analitica_bp, url_prefix="/api/analitica")

    # Manejador global de errores de base de datos / servidor.
    # @app.errorhandler(Exception) NO captura las HTTPException de Werkzeug
    # (404, 405, etc.), por lo que también registramos un manejador genérico
    # para garantizar que NINGÚN error devuelva HTML.
    @app.errorhandler(Exception)
    def _manejar_excepcion(exc):
        """Captura cualquier excepción no controlada y devuelve JSON 500."""
        app.logger.error("Error no controlado: %s", exc, exc_info=True)
        return jsonify({"ok": False, "error": str(exc)}), 500

    @app.errorhandler(404)
    def _no_encontrado(error):
        return jsonify({"ok": False, "error": "Ruta no encontrada"}), 404

    @app.errorhandler(405)
    def _metodo_no_permitido(error):
        return jsonify(
            {"ok": False, "error": "Método no permitido para esta ruta"}
        ), 405

    @app.errorhandler(werkzeug.exceptions.HTTPException)
    def _http_exception(error):
        """Convierte cualquier otra HTTPException de Werkzeug a JSON."""
        return jsonify({"ok": False, "error": error.description}), error.code

    # Inicializar base de datos (DDL + seed) al arrancar
    try:
        inicializar_bd()
    except Exception as exc:  # noqa: BLE001
        # No detenemos el arranque; la app intentará reconectarse en cada request
        app.logger.error("No se pudo inicializar la base de datos: %s", exc)

    return app


app = crear_app()
