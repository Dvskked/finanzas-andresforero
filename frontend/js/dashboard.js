/**
 * dashboard.js — Vista principal de Finanzas AF: resumen, KPI y gráficos.
 *
 * Consolida la información del usuario a través de la API:
 *   - Resumen mensual y KPI cards (delegado en resumen.js)
 *   - Gráfico de gastos por categoría (Chart.js)
 *   - Gráfico de tendencia mensual ingresos vs gastos (Chart.js)
 *   - Últimos movimientos
 *   - Predicción de gasto para el panel
 */
(function (App) {
    "use strict";

    const Api = App.Api;
    const UI = App.UI;
    const CONFIG = App.CONFIG;

    let nodos = {};
    let chartCategorias = null;
    let chartTendencia = null;

    /** Paleta esmeralda/teal coherente con la marca Finanzas AF. */
    const PALETA_GRAFICOS = [
        "#10b981", "#2dd4bf", "#34d399", "#14b8a6", "#0d9488",
        "#22c55e", "#60a5fa", "#a7f3d0", "#34a853", "#06b6d4"
    ];

    function capturarNodos() {
        nodos = {
            estadoUltimos: document.getElementById("estado-ultimos"),
            tablaUltimos: document.getElementById("tabla-ultimos"),
            cuerpoUltimos: document.getElementById("cuerpo-ultimos"),
            botonVerTodos: document.getElementById("boton-ver-todos-movimientos"),

            estadoGraficoCategorias: document.getElementById("estado-grafico-categorias"),
            contenedorGraficoCategorias: document.getElementById("contenedor-grafico-categorias"),
            canvasCategorias: document.getElementById("canvas-grafico-categorias"),

            estadoGraficoTendencia: document.getElementById("estado-grafico-tendencia"),
            contenedorGraficoTendencia: document.getElementById("contenedor-grafico-tendencia"),
            canvasTendencia: document.getElementById("canvas-grafico-tendencia")
        };
    }

    async function cargarUltimosMovimientos(idUsuario) {
        UI.mostrarEstado(nodos.estadoUltimos, "cargando", "Cargando movimientos recientes…");
        if (nodos.tablaUltimos) {
            nodos.tablaUltimos.hidden = true;
        }

        try {
            const lista = await Api.movimientos.listar(idUsuario);
            renderizarUltimos(lista.slice(0, CONFIG.MOVIMIENTOS_EN_PANEL));
            renderizarGraficos(lista);
        } catch (error) {
            UI.mostrarEstado(nodos.estadoUltimos, "error", UI.mensajeDeExcepcion(error));
            if (nodos.estadoGraficoCategorias) {
                UI.mostrarEstado(nodos.estadoGraficoCategorias, "error", "No fue posible cargar datos para el gráfico.");
            }
            if (nodos.estadoGraficoTendencia) {
                UI.mostrarEstado(nodos.estadoGraficoTendencia, "error", "No fue posible cargar datos para la tendencia.");
            }
        }
    }

    function renderizarUltimos(lista) {
        UI.vaciar(nodos.cuerpoUltimos);

        if (!lista.length) {
            if (nodos.tablaUltimos) nodos.tablaUltimos.hidden = true;
            UI.mostrarEstado(nodos.estadoUltimos, "vacio", "No hay movimientos registrados.");
            return;
        }

        lista.forEach((movimiento) => {
            const fila = document.createElement("tr");
            fila.appendChild(UI.crearCelda(UI.formatearFecha(movimiento.fecha), "Fecha"));
            fila.appendChild(UI.crearCelda(movimiento.categoria, "Categoría"));

            const celdaTipo = UI.crearCelda("", "Tipo");
            celdaTipo.appendChild(UI.crearEtiquetaTipo(movimiento.tipo));
            fila.appendChild(celdaTipo);

            const claseMonto = "celda--numerica " + (movimiento.tipo === "ingreso" ? "celda--ingreso" : "celda--gasto");
            fila.appendChild(UI.crearCelda(UI.formatearImporte(movimiento.monto), "Monto (COP)", claseMonto));

            nodos.cuerpoUltimos.appendChild(fila);
        });

        UI.ocultarEstado(nodos.estadoUltimos);
        if (nodos.tablaUltimos) nodos.tablaUltimos.hidden = false;
    }

    function renderizarGraficos(movimientos) {
        if (typeof Chart === "undefined") {
            if (nodos.estadoGraficoCategorias) {
                UI.mostrarEstado(nodos.estadoGraficoCategorias, "error", "Librería de gráficos no disponible.");
            }
            if (nodos.estadoGraficoTendencia) {
                UI.mostrarEstado(nodos.estadoGraficoTendencia, "error", "Librería de gráficos no disponible.");
            }
            return;
        }
        renderizarGraficoCategorias(movimientos);
        renderizarGraficoTendencia(movimientos);
    }

    /** Gráfico 1: Gastos por Categoría (Doughnut). */
    function renderizarGraficoCategorias(movimientos) {
        if (!nodos.canvasCategorias) {
            return;
        }
        if (chartCategorias) {
            chartCategorias.destroy();
            chartCategorias = null;
        }

        const gastosPorCat = {};
        movimientos.forEach((m) => {
            if (m.tipo === "gasto") {
                const monto = UI.aNumero(m.monto) || 0;
                const nombre = m.categoria || "Sin categoría";
                gastosPorCat[nombre] = (gastosPorCat[nombre] || 0) + monto;
            }
        });

        const etiquetas = Object.keys(gastosPorCat);
        const valores = Object.values(gastosPorCat);

        if (!etiquetas.length) {
            UI.mostrarEstado(nodos.estadoGraficoCategorias, "vacio", "No hay gastos registrados para generar el gráfico.");
            if (nodos.contenedorGraficoCategorias) nodos.contenedorGraficoCategorias.hidden = true;
            return;
        }

        UI.ocultarEstado(nodos.estadoGraficoCategorias);
        if (nodos.contenedorGraficoCategorias) nodos.contenedorGraficoCategorias.hidden = false;

        const ctx = nodos.canvasCategorias.getContext("2d");
        chartCategorias = new Chart(ctx, {
            type: "doughnut",
            data: {
                labels: etiquetas,
                datasets: [{
                    data: valores,
                    backgroundColor: PALETA_GRAFICOS.slice(0, etiquetas.length),
                    borderWidth: 2,
                    borderColor: getComputedStyle(document.documentElement).getPropertyValue("--color-surface").trim() || "#101726"
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: "bottom",
                        labels: {
                            boxWidth: 12,
                            padding: 14,
                            color: "#b6c2d6",
                            font: { family: "inherit", size: 12 }
                        }
                    },
                    tooltip: {
                        callbacks: {
                            label: (context) => " " + context.label + ": " + UI.formatearImporte(context.raw || 0)
                        }
                    }
                },
                cutout: "68%"
            }
        });
    }

    /** Gráfico 2: Tendencia Mensual Ingresos vs Gastos (Bar). */
    function renderizarGraficoTendencia(movimientos) {
        if (!nodos.canvasTendencia) {
            return;
        }
        if (chartTendencia) {
            chartTendencia.destroy();
            chartTendencia = null;
        }

        if (!movimientos.length) {
            UI.mostrarEstado(nodos.estadoGraficoTendencia, "vacio", "No hay movimientos registrados para mostrar la tendencia.");
            if (nodos.contenedorGraficoTendencia) nodos.contenedorGraficoTendencia.hidden = true;
            return;
        }

        const datosPorMes = {};
        movimientos.forEach((m) => {
            const periodo = (m.fecha || "").slice(0, 7);
            if (periodo && periodo.length === 7) {
                if (!datosPorMes[periodo]) {
                    datosPorMes[periodo] = { ingresos: 0, gastos: 0 };
                }
                const monto = UI.aNumero(m.monto) || 0;
                if (m.tipo === "ingreso") {
                    datosPorMes[periodo].ingresos += monto;
                } else {
                    datosPorMes[periodo].gastos += monto;
                }
            }
        });

        let mesesOrdenados = Object.keys(datosPorMes).sort();
        if (mesesOrdenados.length > 6) {
            mesesOrdenados = mesesOrdenados.slice(-6);
        }

        const etiquetas = mesesOrdenados.map((m) => UI.formatearMes(m));
        const datosIngresos = mesesOrdenados.map((m) => datosPorMes[m].ingresos);
        const datosGastos = mesesOrdenados.map((m) => datosPorMes[m].gastos);

        UI.ocultarEstado(nodos.estadoGraficoTendencia);
        if (nodos.contenedorGraficoTendencia) nodos.contenedorGraficoTendencia.hidden = false;

        const ctx = nodos.canvasTendencia.getContext("2d");
        chartTendencia = new Chart(ctx, {
            type: "bar",
            data: {
                labels: etiquetas,
                datasets: [
                    { label: "Ingresos", data: datosIngresos, backgroundColor: "#10b981", borderRadius: 6 },
                    { label: "Gastos", data: datosGastos, backgroundColor: "#f87171", borderRadius: 6 }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: "top",
                        labels: {
                            boxWidth: 12,
                            padding: 12,
                            color: "#b6c2d6",
                            font: { family: "inherit", size: 12 }
                        }
                    },
                    tooltip: {
                        callbacks: {
                            label: (context) => " " + context.dataset.label + ": " + UI.formatearImporte(context.raw)
                        }
                    }
                },
                scales: {
                    x: { grid: { display: false }, ticks: { color: "#7d8aa0" } },
                    y: {
                        beginAtZero: true,
                        grid: { color: "#1f2c44" },
                        ticks: {
                            color: "#7d8aa0",
                            callback: (val) => UI.formatearImporte(val)
                        }
                    }
                }
            }
        });
    }

    function cargar(idUsuario) {
        return Promise.all([
            App.Resumen.cargar(idUsuario),
            cargarUltimosMovimientos(idUsuario),
            App.Analytics.cargarPrediccionPanel(idUsuario)
        ]);
    }

    function inicializar() {
        capturarNodos();
        if (nodos.botonVerTodos) {
            nodos.botonVerTodos.addEventListener("click", () => App.cambiarVista("movimientos"));
        }
    }

    App.Dashboard = {
        inicializar,
        cargar
    };
})(window.App);
