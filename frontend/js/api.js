/**
 * api.js — Cliente HTTP centralizado (patrón del repo de referencia).
 *
 * Usa AppConfig (config.js) para obtener la URL base y las rutas de la API.
 * Lee la respuesta como texto y la convierte a JSON de forma flexible, sin
 * colapsar por variantes de content-type. Siempre devuelve los datos (la
 * parte ".datos" si existe, o el JSON completo como fallback).
 */
(function (global) {
  "use strict";

  function base() {
    return global.AppConfig.API_BASE_URL;
  }

  async function peticion(ruta, { metodo = "GET", datos = null } = {}) {
    const opciones = {
      method: metodo,
      headers: {
        "Content-Type": "application/json",
      },
    };

    if (datos && metodo !== "GET" && metodo !== "DELETE") {
      opciones.body = JSON.stringify(datos);
    }

    const respuesta = await fetch(base() + ruta, opciones);
    const texto = await respuesta.text();

    let json;
    try {
      json = JSON.parse(texto);
    } catch (e) {
      throw new Error("El servidor devolvió texto no válido en lugar de JSON.");
    }

    if (!respuesta.ok || json.ok === false) {
      throw new Error(json.error || json.mensaje || "Error en la solicitud");
    }

    // Fallback: si no existe ".datos", devolver el JSON completo.
    return json && typeof json.datos !== "undefined" ? json.datos : json;
  }

  const R = global.AppConfig.RUTAS;

  global.Api = {
    // Autenticación
    registrarUsuario: (datos) =>
      peticion(R.USUARIOS, { metodo: "POST", datos }),
    iniciarSesion: (datos) => peticion(R.LOGIN, { metodo: "POST", datos }),

    // Categorías
    listarCategorias: (tipo) =>
      peticion(R.CATEGORIAS + (tipo ? "?tipo=" + encodeURIComponent(tipo) : "")),
    crearCategoria: (datos) =>
      peticion(R.CATEGORIAS, { metodo: "POST", datos }),

    // Movimientos
    listarMovimientos: (params) =>
      peticion(R.MOVIMIENTOS + _query(params)),
    crearMovimiento: (datos) =>
      peticion(R.MOVIMIENTOS, { metodo: "POST", datos }),
    obtenerMovimiento: (id) => peticion(R.MOVIMIENTOS + "/" + id),
    actualizarMovimiento: (id, datos) =>
      peticion(R.MOVIMIENTOS + "/" + id, { metodo: "PUT", datos }),
    eliminarMovimiento: (id) =>
      peticion(R.MOVIMIENTOS + "/" + id, { metodo: "DELETE" }),

    // Resumen
    resumen: (usuarioId) =>
      peticion(R.RESUMEN + (usuarioId ? "?usuario_id=" + usuarioId : "")),

    // Analítica
    prediccion: (usuarioId) =>
      peticion(R.PREDICCION + "?usuario_id=" + usuarioId),
    anomalias: (usuarioId) =>
      peticion(R.ANOMALIAS + "?usuario_id=" + usuarioId),
  };

  function _query(params) {
    if (!params) return "";
    const claves = Object.keys(params).filter(
      (k) => params[k] !== undefined && params[k] !== null && params[k] !== ""
    );
    if (claves.length === 0) return "";
    return (
      "?" +
      claves
        .map((k) => encodeURIComponent(k) + "=" + encodeURIComponent(params[k]))
        .join("&")
    );
  }
})(window);
