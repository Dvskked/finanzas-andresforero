/**
 * resumen.js — Resumen financiero mensual y KPI cards de Finanzas AF.
 *
 * Endpoint:
 *   GET /api/resumen?id_usuario=&mes=
 *
 * Los importes (ingresos, gastos y balance) provienen de la API.
 */
(function (App) {
    "use strict";

    const Api = App.Api;
    const UI = App.UI;

    let nodos = {};

    function capturarNodos() {
        nodos = {
            formulario: document.getElementById("form-resumen"),
            mes: document.getElementById("entrada-mes"),
            estado: document.getElementById("estado-resumen"),
            indicadores: document.getElementById("indicadores-resumen"),
            ingresos: document.getElementById("valor-ingresos"),
            gastos: document.getElementById("valor-gastos"),
            balance: document.getElementById("valor-balance"),
            tarjetaBalance: document.getElementById("tarjeta-balance")
        };
    }

    function mesSeleccionado() {
        return (nodos.mes && nodos.mes.value) ? nodos.mes.value : UI.mesActual();
    }

    async function cargar(idUsuario, mes) {
        const periodo = mes || mesSeleccionado();
        if (nodos.mes) {
            nodos.mes.value = periodo;
        }

        UI.mostrarEstado(nodos.estado, "cargando", "Cargando resumen de " + UI.formatearMes(periodo) + "…");
        if (nodos.indicadores) {
            nodos.indicadores.hidden = true;
        }

        try {
            const resumen = await Api.resumen.obtener(idUsuario, periodo);
            renderizar(resumen);
        } catch (error) {
            UI.mostrarEstado(nodos.estado, "error", UI.mensajeDeExcepcion(error));
        }
    }

    function renderizar(resumen) {
        if (nodos.ingresos) nodos.ingresos.textContent = UI.formatearImporte(resumen.total_ingresos);
        if (nodos.gastos) nodos.gastos.textContent = UI.formatearImporte(resumen.total_gastos);
        if (nodos.balance) nodos.balance.textContent = UI.formatearImporte(resumen.balance);

        const balance = UI.aNumero(resumen.balance);
        if (nodos.tarjetaBalance) {
            nodos.tarjetaBalance.classList.toggle("es-negativo", balance !== null && balance < 0);
        }

        UI.ocultarEstado(nodos.estado);
        if (nodos.indicadores) nodos.indicadores.hidden = false;
    }

    function alEnviarFormulario(evento) {
        evento.preventDefault();
        if (!nodos.mes.value) {
            UI.mostrarEstado(nodos.estado, "error", "Selecciona un mes para consultar el resumen.");
            if (nodos.indicadores) nodos.indicadores.hidden = true;
            return;
        }
        cargar(App.usuarioActivo(), nodos.mes.value);
    }

    function inicializar() {
        capturarNodos();
        if (nodos.mes) nodos.mes.value = UI.mesActual();
        if (nodos.formulario) nodos.formulario.addEventListener("submit", alEnviarFormulario);
    }

    App.Resumen = {
        inicializar,
        cargar,
        mesSeleccionado
    };
})(window.App);
