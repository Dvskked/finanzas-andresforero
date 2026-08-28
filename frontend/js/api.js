/**
 * Cliente HTTP para la API.
 *
 * Determina la URL base leyendo `window.location.origin` o la variable
 * global `window.API_BASE` si está definida. Esto permite que funcione
 * tanto en local (localhost) como cuando Flask sirve el frontend o cuando
 * la app está desplegada en un servidor remoto.
 *
 * Cuando la respuesta no contiene la clave `.datos`, se devuelve el JSON
 * completo como fallback para evitar lecturas `undefined`.
 */
(function (global) {
  "use strict";

  // URL base dinámica
  function obtenerBase() {
    if (global.API_BASE && global.API_BASE.length > 0) {
      return global.API_BASE.replace(/\/+$/, "");
    }
    return global.location.origin;
  }

  const API_BASE = obtenerBase();

  async function peticion(
    ruta,
    { metodo = "GET", datos = null, headers = {} } = {}
  ) {
    const opciones = {
      method: metodo,
      headers: {
        "Content-Type": "application/json",
        ...headers,
      },
    };

    if (datos && metodo !== "GET" && metodo !== "DELETE") {
      opciones.body = JSON.stringify(datos);
    }

    const respuesta = await fetch(`${API_BASE}${ruta}`, opciones);

    let json;
    try {
      json = await respuesta.json();
    } catch (e) {
      throw new Error(
        "La API no devolvió un JSON válido (status " + respuesta.status + ")"
      );
    }

    // Fallback: si no existe `.datos`, devolvemos el JSON completo.
    const cuerpo = json && typeof json.datos !== "undefined" ? json.datos : json;

    if (!respuesta.ok || (json && json.ok === false)) {
      const mensaje =
        (json && json.error) || "Error de la API (status " + respuesta.status + ")";
      throw new Error(mensaje);
    }

    return cuerpo;
  }

  // Exponer el cliente
  global.Api = {
    base: API_BASE,

    // Autenticación
    registrarUsuario: (datos) =>
      peticion("/api/usuarios", { metodo: "POST", datos }),
    iniciarSesion: (datos) =>
      peticion("/api/usuarios/login", { metodo: "POST", datos }),

    // Categorías
    listarCategorias: (tipo) =>
      peticion(
        "/api/categorias" + (tipo ? "?tipo=" + encodeURIComponent(tipo) : "")
      ),
    crearCategoria: (datos) =>
      peticion("/api/categorias", { metodo: "POST", datos }),

    // Movimientos
    listarMovimientos: (params) =>
      peticion("/api/movimientos" + _query(params)),
    crearMovimiento: (datos) =>
      peticion("/api/movimientos", { metodo: "POST", datos }),
    obtenerMovimiento: (id) => peticion("/api/movimientos/" + id),
    actualizarMovimiento: (id, datos) =>
      peticion("/api/movimientos/" + id, { metodo: "PUT", datos }),
    eliminarMovimiento: (id) =>
      peticion("/api/movimientos/" + id, { metodo: "DELETE" }),

    // Resumen
    resumen: (usuarioId) =>
      peticion(
        "/api/resumen" + (usuarioId ? "?usuario_id=" + usuarioId : "")
      ),

    // Analítica
    prediccion: (usuarioId) =>
      peticion("/api/analitica/prediccion?usuario_id=" + usuarioId),
    anomalias: (usuarioId) =>
      peticion("/api/analitica/anomalias?usuario_id=" + usuarioId),
  };

  function _query(params) {
    if (!params) return "";
    const claves = Object.keys(params).filter(
      (k) => params[k] !== undefined && params[k] !== null && params[k] !== ""
    );
    if (claves.length === 0) return "";
    const partes = claves.map(
      (k) => encodeURIComponent(k) + "=" + encodeURIComponent(params[k])
    );
    return "?" + partes.join("&");
  }
})(window);
