/**
 * config.js — Configuración única del frontend (patrón del proyecto de referencia).
 *
 * La URL base de la API se declara en un solo sitio. Prioridad:
 *   1. window.API_BASE_URL  (definido por script/host)
 *   2. window.API_BASE      (compatibilidad con versiones anteriores)
 *   3. <meta name="api-base-url" content="...">
 *   4. window.location.origin  (misma app servida por Flask)
 *   5. file://            -> http://localhost:8000 (abrir index.html directo)
 *
 * Concentra también las rutas de los endpoints para que ningún otro archivo
 * repita URLs de la API.
 */
(function (global) {
  "use strict";

  function limpiar(url) {
    return (url || "").replace(/\/+$/, "");
  }

  /** Puerto por defecto del servidor local Flask (python app.py). */
  var PUERTO_LOCAL = window.APP_LOCAL_PORT || 8000;

  function leerUrlBase() {
    if (typeof global.API_BASE_URL === "string" && global.API_BASE_URL.trim()) {
      return limpiar(global.API_BASE_URL);
    }
    if (typeof global.API_BASE === "string" && global.API_BASE.trim()) {
      return limpiar(global.API_BASE);
    }
    var meta = document.querySelector('meta[name="api-base-url"]');
    var valor = meta && meta.content ? meta.content.trim() : "";
    if (valor) {
      return limpiar(valor);
    }

    // Fallback robusto: si la página se abrió como archivo local (file://),
    // location.origin vale "null" y no sirve para hacer fetch. Se asume que
    // el backend corre en el servidor local de Flask por defecto.
    if (!global.location || global.location.protocol === "file:" || !global.location.origin || global.location.origin === "null") {
      return "http://localhost:" + PUERTO_LOCAL;
    }
    return limpiar(global.location.origin);
  }

  global.AppConfig = Object.freeze({
    /** Raíz de la API REST, sin barra final. */
    API_BASE_URL: leerUrlBase(),

    /** Rutas relativas de los endpoints existentes en el backend. */
    RUTAS: Object.freeze({
      USUARIOS: "/api/usuarios",
      LOGIN: "/api/usuarios/login",
      CATEGORIAS: "/api/categorias",
      MOVIMIENTOS: "/api/movimientos",
      RESUMEN: "/api/resumen",
      PREDICCION: "/api/analitica/prediccion",
      ANOMALIAS: "/api/analitica/anomalias",
    }),

    /** Clave de sesión en localStorage. */
    CLAVE_SESION: "finanzas_sesion",
  });
})(window);
