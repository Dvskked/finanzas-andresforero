/**
 * charts.js — Visualizaciones Chart.js (dona y líneas).
 */
(function (global) {
  "use strict";

  const COLORS = [
    "#EF4444",
    "#F59E0B",
    "#8B5CF6",
    "#06B6D4",
    "#10B981",
    "#3B82F6",
    "#EC4899",
    "#F97316",
  ];

  let dona = null;
  let lineas = null;

  function destruir(chart) {
    if (chart) chart.destroy();
  }

  function renderizarDona(elemento, datos) {
    destruir(dona);
    if (!elemento || !datos || datos.length === 0) return;
    const etiquetas = datos.map((d) => d.categoria || "Sin categoría");
    const valores = datos.map((d) => d.total);
    const colores = datos.map((d, i) => d.color || COLORS[i % COLORS.length]);

    dona = new Chart(elemento, {
      type: "doughnut",
      data: {
        labels: etiquetas,
        datasets: [
          { data: valores, backgroundColor: colores, borderWidth: 2, borderColor: "#fff" },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { position: "bottom" },
          tooltip: {
            callbacks: {
              label: (ctx) => {
                const total = ctx.dataset.data.reduce((a, b) => a + b, 0) || 1;
                const pct = ((ctx.parsed / total) * 100).toFixed(1);
                return ` ${ctx.label}: $${ctx.parsed.toFixed(2)} (${pct}%)`;
              },
            },
          },
        },
      },
    });
  }

  function renderizarLineas(elemento, puntos) {
    destruir(lineas);
    if (!elemento || !puntos || puntos.length === 0) return;
    const etiquetas = puntos.map((p) => p.mesLabel || "?");
    const gastos = puntos.map((p) => p.gastos || 0);
    const ingresos = puntos.map((p) => p.ingresos || 0);

    lineas = new Chart(elemento, {
      type: "line",
      data: {
        labels: etiquetas,
        datasets: [
          {
            label: "Gastos",
            data: gastos,
            borderColor: "#EF4444",
            backgroundColor: "rgba(239,68,68,0.1)",
            fill: true,
            tension: 0.3,
          },
          {
            label: "Ingresos",
            data: ingresos,
            borderColor: "#22C55E",
            backgroundColor: "rgba(34,197,94,0.1)",
            fill: true,
            tension: 0.3,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { position: "top" } },
        scales: { y: { beginAtZero: true } },
      },
    });
  }

  global.ChartsApp = { renderizarDona, renderizarLineas };
})(window);
