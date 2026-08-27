/**
 * api.js — Capa centralizada de acceso a la API REST de Finanzas AF.
 *
 * Responsabilidades:
 *   - construir URLs a partir de App.CONFIG;
 *   - ejecutar todas las peticiones fetch;
 *   - fijar cabeceras;
 *   - convertir fallos en ErrorApi con mensaje comprensible;
 *   - devolver siempre JSON parseado.
 */
(function (App) {
    "use strict";

    const CONFIG = App.CONFIG;

    const MENSAJES_POR_ESTADO = {
        400: "La solicitud contiene datos inválidos.",
        401: "Credenciales incorrectas o sesión no válida.",
        404: "El recurso solicitado no existe.",
        409: "El recurso ya existe o entra en conflicto.",
        422: "Algún dato del formulario no tiene el formato esperado.",
        500: "Error interno del servidor. Inténtalo de nuevo más tarde."
    };

    const MENSAJE_RED = "No fue posible conectar con el servidor. Comprueba que la API esté en ejecución.";

    function ErrorApi(mensaje, estado) {
        const error = new Error(mensaje);
        error.name = "ErrorApi";
        error.estado = estado || 0;
        error.esErrorApi = true;
        return error;
    }

    /** Compone la URL final de un endpoint con sus parámetros (descarta vacíos). */
    function construirUrl(ruta, parametros) {
        const url = CONFIG.API_BASE_URL + ruta;
        const consulta = new URLSearchParams();

        Object.keys(parametros || {}).forEach((clave) => {
            const valor = parametros[clave];
            if (valor !== null && valor !== undefined && valor !== "") {
                consulta.append(clave, valor);
            }
        });

        const cadena = consulta.toString();
        return cadena ? url + "?" + cadena : url;
    }

    /** Traduce el cuerpo de una respuesta de error a un mensaje presentable. */
    function mensajeDeError(estado, cuerpo) {
        if (estado >= 500) {
            return MENSAJES_POR_ESTADO[500];
        }
        if (cuerpo && typeof cuerpo.detail === "string" && cuerpo.detail.trim()) {
            const detalle = cuerpo.detail.trim();
            if (estado === 422 && Array.isArray(cuerpo.errors) && cuerpo.errors.length) {
                return detalle + ": " + cuerpo.errors.join("; ");
            }
            return detalle;
        }
        return MENSAJES_POR_ESTADO[estado] || "No fue posible completar la operación.";
    }

    /**
     * Ejecuta una petición contra la API y devuelve el JSON parseado.
     */
    async function solicitar(ruta, opciones) {
        const config = opciones || {};
        const metodo = config.metodo || "GET";
        const peticion = {
            method: metodo,
            headers: { Accept: "application/json" }
        };

        if (config.cuerpo !== undefined && config.cuerpo !== null) {
            peticion.headers["Content-Type"] = "application/json";
            peticion.body = JSON.stringify(config.cuerpo);
        }

        let respuesta;
        try {
            respuesta = await fetch(construirUrl(ruta, config.parametros), peticion);
        } catch (fallo) {
            throw ErrorApi(MENSAJE_RED, 0);
        }

        let datos = null;
        try {
            datos = await respuesta.json();
        } catch (fallo) {
            datos = null;
        }

        if (!respuesta.ok) {
            throw ErrorApi(mensajeDeError(respuesta.status, datos), respuesta.status);
        }

        return datos;
    }

    App.Api = {
        ErrorApi,
        MENSAJE_RED,

        /** POST /api/usuarios · registro */
        registrar: (datos) => solicitar(CONFIG.RUTAS.USUARIOS, { metodo: "POST", cuerpo: datos }),

        /** POST /api/usuarios/login · autenticación por correo y contraseña */
        login: (datos) => solicitar(CONFIG.RUTAS.LOGIN, { metodo: "POST", cuerpo: datos }),

        /** Obtiene el usuario por ID para revalidar una sesión existente. */
        obtenerUsuario: (idUsuario) => solicitar(CONFIG.RUTAS.USUARIOS + "/" + idUsuario),

        categorias: {
            listar: (idUsuario) => solicitar(CONFIG.RUTAS.CATEGORIAS, { parametros: { id_usuario: idUsuario } }),
            crear: (datos) => solicitar(CONFIG.RUTAS.CATEGORIAS, { metodo: "POST", cuerpo: datos })
        },

        movimientos: {
            listar: (idUsuario, filtros) =>
                solicitar(CONFIG.RUTAS.MOVIMIENTOS, {
                    parametros: Object.assign({ id_usuario: idUsuario }, filtros || {})
                }),
            crear: (datos) => solicitar(CONFIG.RUTAS.MOVIMIENTOS, { metodo: "POST", cuerpo: datos }),
            actualizar: (idMovimiento, datos) =>
                solicitar(CONFIG.RUTAS.MOVIMIENTOS + "/" + idMovimiento, { metodo: "PUT", cuerpo: datos }),
            eliminar: (idMovimiento) => solicitar(CONFIG.RUTAS.MOVIMIENTOS + "/" + idMovimiento, { metodo: "DELETE" })
        },

        resumen: {
            obtener: (idUsuario, mes) =>
                solicitar(CONFIG.RUTAS.RESUMEN, { parametros: { id_usuario: idUsuario, mes } })
        },

        analitica: {
            prediccion: (idUsuario) => solicitar(CONFIG.RUTAS.PREDICCION, { parametros: { id_usuario: idUsuario } }),
            anomalias: (idUsuario) => solicitar(CONFIG.RUTAS.ANOMALIAS, { parametros: { id_usuario: idUsuario } })
        }
    };
})(window.App);
