/**
 * analytics.js — Módulo analítico de Finanzas AF: predicción y anomalías.
 *
 * Endpoints (ejecutados en el backend):
 *   GET /api/analitica/prediccion?id_usuario=
 *   GET /api/analitica/anomalias?id_usuario=
 *
 * La predicción usa regresión lineal y la detección de anomalías usa Z-Score;
 * ambos modelos corren en el backend, no en el navegador.
 */
(function (App) {
    "use strict";

    const Api = App.Api;
    const UI = App.UI;

    let nodos = {};

    function capturarNodos() {
        nodos = {
            botonRecargar: document.getElementById("boton-recargar-analisis"),

            estadoPrediccion: document.getElementById("estado-prediccion"),
            detallePrediccion: document.getElementById("detalle-prediccion"),
            prediccionMes: document.getElementById("prediccion-mes"),
            prediccionValor: document.getElementById("prediccion-valor"),
            prediccionConfianza: document.getElementById("prediccion-confianza"),
            prediccionMeses: document.getElementById("prediccion-meses"),
            prediccionRazon: document.getElementById("prediccion-razon"),

            estadoAnomalias: document.getElementById("estado-anomalias"),
            contadorAnomalias: document.getElementById("contador-anomalias"),
            tablaAnomalias: document.getElementById("tabla-anomalias"),
            cuerpoAnomalias: document.getElementById("cuerpo-anomalias"),

            panelPrediccionValor: document.getElementById("panel-prediccion-valor"),
            panelPrediccionMes: document.getElementById("panel-prediccion-mes")
        };
    }

    function traducirConfianza(valor) {
        const etiquetas = {
            alta: "Alta",
            media: "Media",
            baja: "Baja"
        };
        const texto = etiquetas[valor] || valor || "—";
        return texto.charAt(0).toUpperCase() + texto.slice(1);
    }

    async function cargarPrediccion() {
        const idUsuario = App.usuarioActivo();
        UI.mostrarEstado(nodos.estadoPrediccion, "cargando", "Calculando predicción…");
        if (nodos.detallePrediccion) nodos.detallePrediccion.hidden = true;
        if (nodos.panelPrediccionValor) nodos.panelPrediccionValor.textContent = "—";

        try {
            const prediccion = await Api.analitica.prediccion(idUsuario);
            renderizarPrediccion(prediccion);
        } catch (error) {
            UI.mostrarEstado(nodos.estadoPrediccion, "error", UI.mensajeDeExcepcion(error));
            if (nodos.panelPrediccionValor) nodos.panelPrediccionValor.textContent = "—";
        }
    }

    function renderizarPrediccion(prediccion) {
        const mes = prediccion.mes_predicho;
        const confianza = prediccion.confianza;

        if (prediccion.gasto_estimado === null || prediccion.gasto_estimado === undefined) {
            UI.mostrarEstado(nodos.estadoPrediccion, "vacio", "No hay datos suficientes para predecir el gasto.");
            if (nodos.detallePrediccion) nodos.detallePrediccion.hidden = true;
            if (nodos.panelPrediccionValor) nodos.panelPrediccionValor.textContent = "—";
            if (nodos.panelPrediccionMes) nodos.panelPrediccionMes.textContent = "Sin datos";
            return;
        }

        const valorFormateado = UI.formatearImporte(prediccion.gasto_estimado);

        if (nodos.prediccionMes) nodos.prediccionMes.textContent = UI.formatearMes(mes);
        if (nodos.prediccionValor) nodos.prediccionValor.textContent = valorFormateado;
        if (nodos.prediccionConfianza) nodos.prediccionConfianza.textContent = traducirConfianza(confianza);
        if (nodos.prediccionMeses) nodos.prediccionMeses.textContent = String(prediccion.meses_procesados);
        if (nodos.prediccionRazon) nodos.prediccionRazon.textContent = prediccion.razon || "—";

        if (nodos.panelPrediccionValor) nodos.panelPrediccionValor.textContent = valorFormateado;
        if (nodos.panelPrediccionMes) nodos.panelPrediccionMes.textContent =
            "Proyección " + UI.formatearMes(mes);

        UI.ocultarEstado(nodos.estadoPrediccion);
        if (nodos.detallePrediccion) nodos.detallePrediccion.hidden = false;
    }

    async function cargarAnomalias() {
        const idUsuario = App.usuarioActivo();
        UI.mostrarEstado(nodos.estadoAnomalias, "cargando", "Analizando patrones de gasto…");
        if (nodos.contadorAnomalias) nodos.contadorAnomalias.textContent = "";
        if (nodos.tablaAnomalias) nodos.tablaAnomalias.hidden = true;
        UI.vaciar(nodos.cuerpoAnomalias);

        try {
            const respuesta = await Api.analitica.anomalias(idUsuario);
            renderizarAnomalias(respuesta);
        } catch (error) {
            UI.mostrarEstado(nodos.estadoAnomalias, "error", UI.mensajeDeExcepcion(error));
        }
    }

    function renderizarAnomalias(respuesta) {
        const anomalias = respuesta.anomalias || [];
        if (nodos.contadorAnomalias) {
            nodos.contadorAnomalias.textContent = anomalias.length === 1
                ? "1 anomalía"
                : anomalias.length + " anomalías";
        }

        if (!anomalias.length) {
            if (nodos.tablaAnomalias) nodos.tablaAnomalias.hidden = true;
            UI.mostrarEstado(nodos.estadoAnomalias, "vacio", "Sin anomalías detectadas. Tu gasto se mantiene dentro de lo habitual.");
            return;
        }

        anomalias.forEach((anomalia) => {
            const fila = document.createElement("tr");
            fila.appendChild(UI.crearCelda(UI.formatearFecha(anomalia.fecha), "Fecha"));
            fila.appendChild(UI.crearCelda(UI.formatearImporte(anomalia.monto), "Monto (COP)", "celda--numerica"));

            const nombreCategoria = App.Categorias.nombreDe(anomalia.id_categoria);
            fila.appendChild(UI.crearCelda(nombreCategoria, "Categoría"));

            fila.appendChild(UI.crearCelda(UI.formatearDecimal(anomalia.z_score), "Z-Score", "celda--numerica"));
            fila.appendChild(UI.crearCelda(anomalia.descripcion || "—", "Descripción"));
            nodos.cuerpoAnomalias.appendChild(fila);
        });

        UI.ocultarEstado(nodos.estadoAnomalias);
        if (nodos.tablaAnomalias) nodos.tablaAnomalias.hidden = false;
    }

    async function cargar(idUsuario) {
        const idActivo = idUsuario || App.usuarioActivo();
        return Promise.all([
            cargarPrediccionConUsuario(idActivo),
            cargarAnomaliasConUsuario(idActivo)
        ]);
    }

    /** Versiones de los cargadores que aceptan un idUsuario explícito. */
    async function cargarPrediccionConUsuario(idUsuario) {
        UI.mostrarEstado(nodos.estadoPrediccion, "cargando", "Calculando predicción…");
        if (nodos.detallePrediccion) nodos.detallePrediccion.hidden = true;
        if (nodos.panelPrediccionValor) nodos.panelPrediccionValor.textContent = "—";
        try {
            const prediccion = await Api.analitica.prediccion(idUsuario);
            renderizarPrediccion(prediccion);
        } catch (error) {
            UI.mostrarEstado(nodos.estadoPrediccion, "error", UI.mensajeDeExcepcion(error));
            if (nodos.panelPrediccionValor) nodos.panelPrediccionValor.textContent = "—";
        }
    }

    async function cargarAnomaliasConUsuario(idUsuario) {
        UI.mostrarEstado(nodos.estadoAnomalias, "cargando", "Analizando patrones de gasto…");
        if (nodos.contadorAnomalias) nodos.contadorAnomalias.textContent = "";
        if (nodos.tablaAnomalias) nodos.tablaAnomalias.hidden = true;
        UI.vaciar(nodos.cuerpoAnomalias);
        try {
            const respuesta = await Api.analitica.anomalias(idUsuario);
            renderizarAnomalias(respuesta);
        } catch (error) {
            UI.mostrarEstado(nodos.estadoAnomalias, "error", UI.mensajeDeExcepcion(error));
        }
    }

    /** Carga solo la KPI de predicción para la vista de panel (Dashboard). */
    function cargarPrediccionPanel(idUsuario) {
        return cargarPrediccionConUsuario(idUsuario);
    }

    function inicializar() {
        capturarNodos();
        if (nodos.botonRecargar) {
            nodos.botonRecargar.addEventListener("click", () => cargar(App.usuarioActivo()));
        }
    }

    App.Analytics = {
        inicializar,
        cargar,
        cargarPrediccionPanel
    };
})(window.App);
