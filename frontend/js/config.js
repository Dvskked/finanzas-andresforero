/**
 * config.js — Configuración única del frontend de Finanzas AF (Andres Forero).
 *
 * La URL de la API se declara en un solo sitio. Cualquier otra página puede
 * sobrescribirla añadiendo <meta name="api-base-url" content="..."> en su <head>.
 *
 * Este archivo no guarda secretos: ni contraseñas, ni claves, ni credenciales.
 */
(function (global) {
    "use strict";

    const URL_API_POR_DEFECTO = "http://127.0.0.1:8000";

    function leerUrlBase() {
        const meta = document.querySelector('meta[name="api-base-url"]');
        const valor = meta && meta.content ? meta.content.trim() : "";
        const url = valor || URL_API_POR_DEFECTO;
        return url.replace(/\/+$/, "");
    }

    global.App = global.App || {};

    global.App.CONFIG = Object.freeze({
        ATRIBUCION: "Andres Forero",
        MARCA: "Finanzas AF",

        API_BASE_URL: leerUrlBase(),

        RUTAS: Object.freeze({
            USUARIOS: "/api/usuarios",
            LOGIN: "/api/usuarios/login",
            CATEGORIAS: "/api/categorias",
            MOVIMIENTOS: "/api/movimientos",
            RESUMEN: "/api/resumen",
            PREDICCION: "/api/analitica/prediccion",
            ANOMALIAS: "/api/analitica/anomalias"
        }),

        LOCALIZACION: "es-CO",
        MONEDA: "COP",
        CLAVE_SESION: "finanzasaf.sesion",
        MOVIMIENTOS_EN_PANEL: 5
    });
})(window);
