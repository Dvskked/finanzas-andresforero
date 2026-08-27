/**
 * ui.js — Utilidades de presentación de Finanzas AF (Andres Forero).
 *
 * Formateo monetario en COP, fechas y meses, estados de interfaz,
 * notificaciones toast, diálogos modales y protección contra inyección HTML.
 */
(function (App) {
    "use strict";

    const CONFIG = App.CONFIG;

    /** Formateador monetario: Peso Colombiano (COP). */
    const formateadorMoneda = new Intl.NumberFormat(CONFIG.LOCALIZACION, {
        style: "currency",
        currency: CONFIG.MONEDA,
        currencyDisplay: "code",
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    });

    const formateadorDecimal = new Intl.NumberFormat(CONFIG.LOCALIZACION, {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    });

    const NOMBRES_MES = [
        "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
        "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
    ];

    function elemento(selector) {
        return document.querySelector(selector);
    }

    function vaciar(nodo) {
        while (nodo && nodo.firstChild) {
            nodo.removeChild(nodo.firstChild);
        }
    }

    function aNumero(valor) {
        const numero = Number(valor);
        return Number.isFinite(numero) ? numero : null;
    }

    /** Formatea un importe en pesos colombianos: e.g. "COP 1.500.000,00". */
    function formatearImporte(valor) {
        const numero = aNumero(valor);
        return numero === null ? "—" : formateadorMoneda.format(numero);
    }

    function formatearDecimal(valor) {
        const numero = aNumero(valor);
        return numero === null ? "—" : formateadorDecimal.format(numero);
    }

    /** Formatea una fecha ISO (YYYY-MM-DD) a DD/MM/AAAA sin desfases de zona. */
    function formatearFecha(iso) {
        if (typeof iso !== "string") {
            return "—";
        }
        const partes = iso.slice(0, 10).split("-");
        if (partes.length !== 3) {
            return iso;
        }
        return partes[2] + "/" + partes[1] + "/" + partes[0];
    }

    /** Convierte "2026-08" en "Agosto de 2026". */
    function formatearMes(mes) {
        if (typeof mes !== "string" || mes.length < 7) {
            return "—";
        }
        const anio = mes.slice(0, 4);
        const indice = Number(mes.slice(5, 7)) - 1;
        if (indice < 0 || indice > 11) {
            return mes;
        }
        return NOMBRES_MES[indice] + " de " + anio;
    }

    /** Devuelve el periodo mensual actual en formato YYYY-MM. */
    function mesActual() {
        const hoy = new Date();
        return hoy.getFullYear() + "-" + String(hoy.getMonth() + 1).padStart(2, "0");
    }

    /** Devuelve la fecha actual en formato YYYY-MM-DD. */
    function fechaHoy() {
        const hoy = new Date();
        return [
            hoy.getFullYear(),
            String(hoy.getMonth() + 1).padStart(2, "0"),
            String(hoy.getDate()).padStart(2, "0")
        ].join("-");
    }

    /** Muestra un estado de interfaz sobre su elemento contenedor. */
    function mostrarEstado(nodo, tipo, mensaje) {
        if (!nodo) {
            return;
        }
        nodo.className = "estado estado--" + tipo;
        nodo.textContent = mensaje;
        nodo.hidden = false;
    }

    function ocultarEstado(nodo) {
        if (nodo) {
            nodo.hidden = true;
        }
    }

    function mostrarErrorFormulario(nodo, mensaje) {
        if (!nodo) {
            return;
        }
        nodo.textContent = mensaje;
        nodo.hidden = false;
    }

    function limpiarErrorFormulario(nodo) {
        if (!nodo) {
            return;
        }
        nodo.textContent = "";
        nodo.hidden = true;
    }

    function crearCelda(texto, etiqueta, clase) {
        const celda = document.createElement("td");
        celda.textContent = texto;
        if (etiqueta) {
            celda.dataset.etiqueta = etiqueta;
        }
        if (clase) {
            celda.className = clase;
        }
        return celda;
    }

    function crearEtiquetaTipo(tipo) {
        const etiqueta = document.createElement("span");
        etiqueta.className = "etiqueta etiqueta--" + (tipo === "ingreso" ? "ingreso" : "gasto");
        etiqueta.textContent = tipo === "ingreso" ? "Ingreso" : "Gasto";
        return etiqueta;
    }

    function notificar(mensaje, tipo) {
        const contenedor = document.getElementById("notificaciones");
        if (!contenedor) {
            return;
        }
        const aviso = document.createElement("p");
        aviso.className = "notificacion notificacion--" + (tipo || "exito");
        aviso.textContent = mensaje;
        contenedor.appendChild(aviso);
        window.setTimeout(() => aviso.remove(), 4500);
    }

    function abrirDialogo(dialogo, elementoFoco) {
        if (!dialogo) {
            return;
        }
        if (typeof dialogo.showModal === "function") {
            dialogo.showModal();
        } else {
            dialogo.setAttribute("open", "");
        }
        if (elementoFoco) {
            elementoFoco.focus();
        }
    }

    function cerrarDialogo(dialogo) {
        if (!dialogo) {
            return;
        }
        if (typeof dialogo.close === "function") {
            dialogo.close();
        } else {
            dialogo.removeAttribute("open");
        }
    }

    function mensajeDeExcepcion(error) {
        if (error && error.esErrorApi && error.message) {
            return error.message;
        }
        return App.Api.MENSAJE_RED;
    }

    App.UI = {
        elemento,
        vaciar,
        aNumero,
        formatearImporte,
        formatearDecimal,
        formatearFecha,
        formatearMes,
        mesActual,
        fechaHoy,
        mostrarEstado,
        ocultarEstado,
        mostrarErrorFormulario,
        limpiarErrorFormulario,
        crearCelda,
        crearEtiquetaTipo,
        notificar,
        abrirDialogo,
        cerrarDialogo,
        mensajeDeExcepcion
    };
})(window.App);
