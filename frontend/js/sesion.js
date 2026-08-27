/**
 * sesion.js — Gestión de sesión de Finanzas AF (Andres Forero).
 *
 * - index.html la crea tras un login o registro correctos.
 * - dashboard.html la exige; si no hay sesión, redirige al acceso.
 *
 * La sesión se guarda en sessionStorage (muere al cerrar la pestaña) y solo
 * contiene el id del usuario: nunca el correo ni la contraseña.
 */
(function (App) {
    "use strict";

    const Api = App.Api;
    const CONFIG = App.CONFIG;

    const PAGINA_ACCESO = "index.html";
    const PAGINA_PANEL = "dashboard.html";

    /** Devuelve el id del usuario con sesión activa, o null. */
    function obtener() {
        try {
            const valor = Number(window.sessionStorage.getItem(CONFIG.CLAVE_SESION));
            return Number.isInteger(valor) && valor > 0 ? valor : null;
        } catch (error) {
            return null;
        }
    }

    function guardar(idUsuario) {
        try {
            window.sessionStorage.setItem(CONFIG.CLAVE_SESION, String(idUsuario));
        } catch (error) {
            /* Modo privado sin almacenamiento: la navegación seguirá funcionando. */
        }
    }

    function borrar() {
        try {
            window.sessionStorage.removeItem(CONFIG.CLAVE_SESION);
        } catch (error) {
            /* Nada que borrar. */
        }
    }

    /**
     * Autentica un usuario por correo y contraseña contra POST /api/usuarios/login.
     * @returns {Promise<Object>} datos del usuario autenticado.
     */
    function autenticar(correo, contrasena) {
        return Api.login({ correo, contrasena });
    }

    /**
     * Revalida una sesión existente consultando el usuario por su id.
     * @returns {Promise<Object>} datos del usuario si la sesión es válida.
     */
    function verificarUsuario(idUsuario) {
        return Api.obtenerUsuario(idUsuario);
    }

    function irAlPanel() {
        window.location.href = PAGINA_PANEL;
    }

    function irAlAcceso() {
        window.location.href = PAGINA_ACCESO;
    }

    App.Sesion = {
        PAGINA_ACCESO: PAGINA_ACCESO,
        PAGINA_PANEL: PAGINA_PANEL,
        obtener,
        guardar,
        borrar,
        autenticar,
        verificarUsuario,
        irAlPanel,
        irAlAcceso
    };
})(window.App);
