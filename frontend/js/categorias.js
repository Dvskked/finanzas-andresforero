/**
 * categorias.js — Gestión de categorías de Finanzas AF.
 *
 * Endpoints:
 *   GET  /api/categorias?id_usuario=
 *   POST /api/categorias
 *
 * Mantiene la caché de categorías del usuario activo, que reutilizan los
 * desplegables de movimientos y la tabla de anomalías.
 */
(function (App) {
    "use strict";

    const Api = App.Api;
    const UI = App.UI;

    let categorias = [];
    let nodos = {};

    function capturarNodos() {
        nodos = {
            estado: document.getElementById("estado-categorias"),
            tabla: document.getElementById("tabla-categorias"),
            cuerpo: document.getElementById("cuerpo-categorias"),
            contador: document.getElementById("contador-categorias"),
            formulario: document.getElementById("form-categoria"),
            nombre: document.getElementById("categoria-nombre"),
            tipo: document.getElementById("categoria-tipo"),
            error: document.getElementById("error-categoria")
        };
    }

    function obtenerTodas() {
        return categorias.slice();
    }

    function obtenerPorTipo(tipo) {
        return categorias.filter((categoria) => categoria.tipo === tipo);
    }

    function nombreDe(idCategoria) {
        const encontrada = categorias.find((categoria) => categoria.id_categoria === idCategoria);
        return encontrada ? encontrada.nombre : "Categoría " + idCategoria;
    }

    function anunciarCambio() {
        document.dispatchEvent(new CustomEvent("categorias:actualizadas"));
    }

    async function sincronizar(idUsuario) {
        UI.mostrarEstado(nodos.estado, "cargando", "Cargando categorías…");
        nodos.tabla.hidden = true;
        nodos.contador.textContent = "";

        try {
            categorias = await Api.categorias.listar(idUsuario);
            renderizar();
        } catch (error) {
            categorias = [];
            UI.mostrarEstado(nodos.estado, "error", UI.mensajeDeExcepcion(error));
        }

        anunciarCambio();
    }

    function renderizar() {
        UI.vaciar(nodos.cuerpo);

        if (!categorias.length) {
            nodos.tabla.hidden = true;
            nodos.contador.textContent = "";
            UI.mostrarEstado(nodos.estado, "vacio", "No hay categorías registradas para este usuario.");
            return;
        }

        categorias.forEach((categoria) => {
            const fila = document.createElement("tr");
            fila.appendChild(UI.crearCelda(String(categoria.id_categoria), "ID", "celda--numerica"));
            fila.appendChild(UI.crearCelda(categoria.nombre, "Nombre"));

            const celdaTipo = UI.crearCelda("", "Tipo");
            celdaTipo.appendChild(UI.crearEtiquetaTipo(categoria.tipo));
            fila.appendChild(celdaTipo);

            nodos.cuerpo.appendChild(fila);
        });

        nodos.contador.textContent = categorias.length === 1
            ? "1 categoría"
            : categorias.length + " categorías";

        UI.ocultarEstado(nodos.estado);
        nodos.tabla.hidden = false;
    }

    async function enviarFormulario(evento) {
        evento.preventDefault();
        UI.limpiarErrorFormulario(nodos.error);

        const nombre = nodos.nombre.value.trim();
        if (nombre.length < 2) {
            nodos.nombre.setAttribute("aria-invalid", "true");
            UI.mostrarErrorFormulario(nodos.error, "El nombre de la categoría debe tener al menos 2 caracteres.");
            nodos.nombre.focus();
            return;
        }
        nodos.nombre.removeAttribute("aria-invalid");

        const boton = nodos.formulario.querySelector('button[type="submit"]');
        boton.disabled = true;

        try {
            await Api.categorias.crear({
                nombre,
                tipo: nodos.tipo.value,
                id_usuario: App.usuarioActivo()
            });
            nodos.formulario.reset();
            UI.notificar("Categoría creada correctamente.", "exito");
            await sincronizar(App.usuarioActivo());
        } catch (error) {
            UI.mostrarErrorFormulario(nodos.error, UI.mensajeDeExcepcion(error));
        } finally {
            boton.disabled = false;
        }
    }

    function inicializar() {
        capturarNodos();
        nodos.formulario.addEventListener("submit", enviarFormulario);
    }

    App.Categorias = {
        inicializar,
        sincronizar,
        obtenerTodas,
        obtenerPorTipo,
        nombreDe
    };
})(window.App);
