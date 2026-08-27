/**
 * movimientos.js — Alta, consulta, edición, eliminación y filtrado de movimientos.
 *
 * Endpoints:
 *   GET    /api/movimientos?id_usuario=&desde=&hasta=&categoria=
 *   POST   /api/movimientos
 *   PUT    /api/movimientos/{id}
 *   DELETE /api/movimientos/{id}
 *
 * Las validaciones locales son de experiencia de uso; el backend vuelve a
 * validar cada campo y sigue siendo la autoridad.
 */
(function (App) {
    "use strict";

    const Api = App.Api;
    const UI = App.UI;

    let nodos = {};
    let movimientos = [];
    let idEnEdicion = null;
    let idPorEliminar = null;

    function capturarNodos() {
        nodos = {
            estado: document.getElementById("estado-movimientos"),
            tabla: document.getElementById("tabla-movimientos"),
            cuerpo: document.getElementById("cuerpo-movimientos"),
            contador: document.getElementById("contador-movimientos"),

            formFiltros: document.getElementById("form-filtros"),
            filtroDesde: document.getElementById("filtro-desde"),
            filtroHasta: document.getElementById("filtro-hasta"),
            filtroCategoria: document.getElementById("filtro-categoria"),
            errorFiltros: document.getElementById("error-filtros"),

            botonNuevo: document.getElementById("boton-nuevo-movimiento"),

            dialogo: document.getElementById("dialogo-movimiento"),
            tituloDialogo: document.getElementById("titulo-dialogo-movimiento"),
            formulario: document.getElementById("form-movimiento"),
            tipo: document.getElementById("movimiento-tipo"),
            categoria: document.getElementById("movimiento-categoria"),
            monto: document.getElementById("movimiento-monto"),
            fecha: document.getElementById("movimiento-fecha"),
            descripcion: document.getElementById("movimiento-descripcion"),
            error: document.getElementById("error-movimiento"),
            botonGuardar: document.getElementById("boton-guardar-movimiento"),
            botonCerrar: document.getElementById("boton-cerrar-movimiento"),
            botonCancelar: document.getElementById("boton-cancelar-movimiento"),

            dialogoConfirmar: document.getElementById("dialogo-confirmar"),
            textoConfirmar: document.getElementById("texto-confirmar"),
            botonConfirmarEliminar: document.getElementById("boton-confirmar-eliminar"),
            botonCancelarEliminar: document.getElementById("boton-cancelar-eliminar")
        };
    }

    function filtrosActivos() {
        return {
            desde: nodos.filtroDesde.value || null,
            hasta: nodos.filtroHasta.value || null,
            categoria: nodos.filtroCategoria.value || null
        };
    }

    async function cargar(idUsuario) {
        UI.mostrarEstado(nodos.estado, "cargando", "Cargando movimientos…");
        nodos.tabla.hidden = true;
        nodos.contador.textContent = "";

        try {
            movimientos = await Api.movimientos.listar(idUsuario, filtrosActivos());
            renderizar();
        } catch (error) {
            movimientos = [];
            UI.mostrarEstado(nodos.estado, "error", UI.mensajeDeExcepcion(error));
        }
    }

    function renderizar() {
        UI.vaciar(nodos.cuerpo);

        if (!movimientos.length) {
            nodos.tabla.hidden = true;
            UI.mostrarEstado(nodos.estado, "vacio", "No hay movimientos registrados para los criterios seleccionados.");
            return;
        }

        movimientos.forEach((movimiento) => {
            nodos.cuerpo.appendChild(crearFila(movimiento));
        });

        nodos.contador.textContent = movimientos.length === 1
            ? "1 movimiento"
            : movimientos.length + " movimientos";

        UI.ocultarEstado(nodos.estado);
        nodos.tabla.hidden = false;
    }

    function crearFila(movimiento) {
        const fila = document.createElement("tr");
        fila.dataset.id = movimiento.id_movimiento;

        fila.appendChild(UI.crearCelda(UI.formatearFecha(movimiento.fecha), "Fecha"));
        fila.appendChild(UI.crearCelda(movimiento.categoria, "Categoría"));

        const celdaTipo = UI.crearCelda("", "Tipo");
        celdaTipo.appendChild(UI.crearEtiquetaTipo(movimiento.tipo));
        fila.appendChild(celdaTipo);

        const claseMonto = "celda--numerica " + (movimiento.tipo === "ingreso" ? "celda--ingreso" : "celda--gasto");
        fila.appendChild(UI.crearCelda(UI.formatearImporte(movimiento.monto), "Monto", claseMonto));

        fila.appendChild(UI.crearCelda(movimiento.descripcion || "—", "Descripción"));

        const celdaAcciones = UI.crearCelda("", "Acciones", "celda--acciones");
        celdaAcciones.appendChild(crearBotonAccion("editar", "Editar", movimiento, "boton--secundario"));
        celdaAcciones.appendChild(crearBotonAccion("eliminar", "Eliminar", movimiento, "boton--peligro-sutil"));
        fila.appendChild(celdaAcciones);

        return fila;
    }

    function crearBotonAccion(accion, texto, movimiento, variante) {
        const boton = document.createElement("button");
        boton.type = "button";
        boton.className = "boton " + variante + " boton--pequeno";
        boton.textContent = texto;
        boton.dataset.accion = accion;
        boton.dataset.id = movimiento.id_movimiento;
        boton.setAttribute(
            "aria-label",
            texto + " movimiento de " + movimiento.categoria + " del " + UI.formatearFecha(movimiento.fecha)
        );
        return boton;
    }

    function buscarMovimiento(idMovimiento) {
        return movimientos.find((movimiento) => movimiento.id_movimiento === idMovimiento) || null;
    }

    function rellenarFiltroCategorias() {
        const seleccionPrevia = nodos.filtroCategoria.value;
        UI.vaciar(nodos.filtroCategoria);

        const opcionTodas = document.createElement("option");
        opcionTodas.value = "";
        opcionTodas.textContent = "Todas las categorías";
        nodos.filtroCategoria.appendChild(opcionTodas);

        App.Categorias.obtenerTodas().forEach((categoria) => {
            nodos.filtroCategoria.appendChild(crearOpcionCategoria(categoria, true));
        });

        nodos.filtroCategoria.value = seleccionPrevia;
    }

    function rellenarCategoriasDelFormulario(idCategoriaSeleccionada) {
        const disponibles = App.Categorias.obtenerPorTipo(nodos.tipo.value);
        UI.vaciar(nodos.categoria);

        if (!disponibles.length) {
            const vacia = document.createElement("option");
            vacia.value = "";
            vacia.textContent = "No hay categorías de este tipo";
            nodos.categoria.appendChild(vacia);
            nodos.categoria.disabled = true;
            return;
        }

        nodos.categoria.disabled = false;
        disponibles.forEach((categoria) => {
            nodos.categoria.appendChild(crearOpcionCategoria(categoria, false));
        });

        if (idCategoriaSeleccionada) {
            nodos.categoria.value = String(idCategoriaSeleccionada);
        }
    }

    function crearOpcionCategoria(categoria, conTipo) {
        const opcion = document.createElement("option");
        opcion.value = String(categoria.id_categoria);
        opcion.textContent = conTipo
            ? categoria.nombre + " (" + categoria.tipo + ")"
            : categoria.nombre;
        return opcion;
    }

    function abrirDialogoAlta() {
        idEnEdicion = null;
        nodos.formulario.reset();
        UI.limpiarErrorFormulario(nodos.error);
        nodos.tituloDialogo.textContent = "Nuevo movimiento";
        nodos.botonGuardar.textContent = "Registrar";
        nodos.fecha.value = UI.fechaHoy();
        rellenarCategoriasDelFormulario(null);
        UI.abrirDialogo(nodos.dialogo, nodos.tipo);
    }

    function abrirDialogoEdicion(movimiento) {
        idEnEdicion = movimiento.id_movimiento;
        UI.limpiarErrorFormulario(nodos.error);
        nodos.tituloDialogo.textContent = "Editar movimiento";
        nodos.botonGuardar.textContent = "Guardar cambios";
        nodos.tipo.value = movimiento.tipo;
        rellenarCategoriasDelFormulario(movimiento.id_categoria);
        nodos.monto.value = movimiento.monto;
        nodos.fecha.value = String(movimiento.fecha).slice(0, 10);
        nodos.descripcion.value = movimiento.descripcion || "";
        UI.abrirDialogo(nodos.dialogo, nodos.tipo);
    }

    function validarFormulario() {
        if (!nodos.categoria.value) {
            return "Selecciona una categoría. Si no existe ninguna del tipo elegido, créala primero.";
        }
        const monto = Number(nodos.monto.value);
        if (!Number.isFinite(monto) || monto <= 0) {
            return "El monto debe ser un número mayor que cero.";
        }
        if (!nodos.fecha.value) {
            return "La fecha del movimiento es obligatoria.";
        }
        return null;
    }

    function construirCuerpo() {
        const descripcion = nodos.descripcion.value.trim();
        return {
            id_usuario: App.usuarioActivo(),
            id_categoria: Number(nodos.categoria.value),
            tipo: nodos.tipo.value,
            monto: Number(nodos.monto.value).toFixed(2),
            fecha: nodos.fecha.value,
            descripcion: descripcion || null
        };
    }

    async function enviarFormulario(evento) {
        evento.preventDefault();
        UI.limpiarErrorFormulario(nodos.error);

        const problema = validarFormulario();
        if (problema) {
            UI.mostrarErrorFormulario(nodos.error, problema);
            return;
        }

        nodos.botonGuardar.disabled = true;
        try {
            if (idEnEdicion === null) {
                await Api.movimientos.crear(construirCuerpo());
                UI.notificar("Movimiento registrado correctamente.", "exito");
            } else {
                await Api.movimientos.actualizar(idEnEdicion, construirCuerpo());
                UI.notificar("Movimiento actualizado correctamente.", "exito");
            }
            UI.cerrarDialogo(nodos.dialogo);
            await App.refrescarDatosDependientes();
        } catch (error) {
            UI.mostrarErrorFormulario(nodos.error, UI.mensajeDeExcepcion(error));
        } finally {
            nodos.botonGuardar.disabled = false;
        }
    }

    function pedirConfirmacion(movimiento) {
        idPorEliminar = movimiento.id_movimiento;
        nodos.textoConfirmar.textContent =
            "¿Eliminar el movimiento de " + movimiento.categoria + " del " +
            UI.formatearFecha(movimiento.fecha) + " por " + UI.formatearImporte(movimiento.monto) +
            "? Esta acción no se puede deshacer.";
        UI.abrirDialogo(nodos.dialogoConfirmar, nodos.botonCancelarEliminar);
    }

    async function eliminarConfirmado() {
        if (idPorEliminar === null) {
            return;
        }
        nodos.botonConfirmarEliminar.disabled = true;
        try {
            await Api.movimientos.eliminar(idPorEliminar);
            UI.cerrarDialogo(nodos.dialogoConfirmar);
            UI.notificar("Movimiento eliminado correctamente.", "exito");
            await App.refrescarDatosDependientes();
        } catch (error) {
            UI.cerrarDialogo(nodos.dialogoConfirmar);
            UI.notificar(UI.mensajeDeExcepcion(error), "error");
        } finally {
            nodos.botonConfirmarEliminar.disabled = false;
            idPorEliminar = null;
        }
    }

    function alPulsarEnTabla(evento) {
        const boton = evento.target.closest("button[data-accion]");
        if (!boton) {
            return;
        }
        const movimiento = buscarMovimiento(Number(boton.dataset.id));
        if (!movimiento) {
            return;
        }
        if (boton.dataset.accion === "editar") {
            abrirDialogoEdicion(movimiento);
        } else {
            pedirConfirmacion(movimiento);
        }
    }

    function alFiltrar(evento) {
        evento.preventDefault();
        UI.limpiarErrorFormulario(nodos.errorFiltros);

        const desde = nodos.filtroDesde.value;
        const hasta = nodos.filtroHasta.value;
        if (desde && hasta && desde > hasta) {
            UI.mostrarErrorFormulario(nodos.errorFiltros, "La fecha inicial no puede ser posterior a la fecha final.");
            return;
        }
        cargar(App.usuarioActivo());
    }

    function alLimpiarFiltros() {
        UI.limpiarErrorFormulario(nodos.errorFiltros);
        window.setTimeout(() => cargar(App.usuarioActivo()), 0);
    }

    function inicializar() {
        capturarNodos();

        nodos.formFiltros.addEventListener("submit", alFiltrar);
        nodos.formFiltros.addEventListener("reset", alLimpiarFiltros);
        nodos.cuerpo.addEventListener("click", alPulsarEnTabla);

        nodos.botonNuevo.addEventListener("click", abrirDialogoAlta);
        nodos.formulario.addEventListener("submit", enviarFormulario);
        nodos.tipo.addEventListener("change", () => rellenarCategoriasDelFormulario(null));

        nodos.botonCerrar.addEventListener("click", () => UI.cerrarDialogo(nodos.dialogo));
        nodos.botonCancelar.addEventListener("click", () => UI.cerrarDialogo(nodos.dialogo));

        nodos.botonConfirmarEliminar.addEventListener("click", eliminarConfirmado);
        nodos.botonCancelarEliminar.addEventListener("click", () => {
            idPorEliminar = null;
            UI.cerrarDialogo(nodos.dialogoConfirmar);
        });

        document.addEventListener("categorias:actualizadas", () => {
            rellenarFiltroCategorias();
            rellenarCategoriasDelFormulario(null);
        });
    }

    App.Movimientos = {
        inicializar,
        cargar
    };
})(window.App);
