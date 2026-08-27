/**
 * app.js — Controlador principal del panel de Finanzas AF (dashboard.html).
 *
 * Responsabilidades:
 *   1. Exigir sesión válida antes de mostrar la interfaz (guardián de acceso).
 *   2. Inicializar los módulos funcionales con el usuario autenticado.
 *   3. Gestionar la navegación lateral y la miga de pan.
 *   4. Controlar el menú responsive en móviles.
 */
(function (App) {
    "use strict";

    const Sesion = App.Sesion;

    let idUsuario = null;
    let vistaActiva = "panel";

    const TITULOS_VISTA = {
        panel: "Dashboard",
        movimientos: "Movimientos",
        categorias: "Categorías",
        analisis: "Análisis"
    };

    const CARGADORES = {
        panel: () => App.Dashboard.cargar(idUsuario),
        movimientos: () => App.Movimientos.cargar(idUsuario),
        categorias: () => App.Categorias.sincronizar(idUsuario),
        analisis: () => App.Analytics.cargar(idUsuario)
    };

    let nodos = {};

    function capturarNodos() {
        nodos = {
            cabecera: document.getElementById("cabecera-aplicacion"),
            contenido: document.getElementById("contenido"),
            pie: document.getElementById("pie-aplicacion"),
            tituloSeccion: document.getElementById("titulo-seccion-actual"),
            sesionUsuarioSidebar: document.getElementById("sesion-usuario-sidebar"),
            avatarUsuario: document.getElementById("avatar-usuario"),
            botonCerrarSesion: document.getElementById("boton-cerrar-sesion"),

            barraLateral: document.getElementById("barra-lateral"),
            sidebarBackdrop: document.getElementById("sidebar-backdrop"),
            botonMenuMovil: document.getElementById("boton-menu-movil"),
            botonCerrarSidebar: document.getElementById("boton-cerrar-sidebar"),

            enlaces: Array.prototype.slice.call(document.querySelectorAll(".menu-lateral__enlace")),
            vistas: Array.prototype.slice.call(document.querySelectorAll(".vista"))
        };
    }

    function usuarioActivo() {
        if (idUsuario === null) {
            throw new Error("No hay ninguna sesión activa.");
        }
        return idUsuario;
    }

    function abrirSidebar() {
        if (nodos.barraLateral) {
            nodos.barraLateral.classList.add("abierta");
        }
        if (nodos.sidebarBackdrop) {
            nodos.sidebarBackdrop.classList.add("activo");
        }
    }

    function cerrarSidebar() {
        if (nodos.barraLateral) {
            nodos.barraLateral.classList.remove("abierta");
        }
        if (nodos.sidebarBackdrop) {
            nodos.sidebarBackdrop.classList.remove("activo");
        }
    }

    function cambiarVista(nombre) {
        vistaActiva = nombre;

        nodos.vistas.forEach((vista) => {
            vista.hidden = vista.id !== "vista-" + nombre;
        });

        nodos.enlaces.forEach((enlace) => {
            if (enlace.dataset.vista === nombre) {
                enlace.setAttribute("aria-current", "page");
            } else {
                enlace.removeAttribute("aria-current");
            }
        });

        if (nodos.tituloSeccion) {
            nodos.tituloSeccion.textContent = TITULOS_VISTA[nombre] || nombre;
        }

        cerrarSidebar();
        return CARGADORES[nombre]();
    }

    function refrescarDatosDependientes() {
        return CARGADORES[vistaActiva]();
    }

    function mostrarAplicacion(usuario) {
        if (nodos.cabecera) nodos.cabecera.hidden = false;
        if (nodos.contenido) nodos.contenido.hidden = false;
        if (nodos.pie) nodos.pie.hidden = false;

        if (nodos.sesionUsuarioSidebar && usuario) {
            const nombre = (usuario.nombre || ("Usuario #" + idUsuario)).trim();
            nodos.sesionUsuarioSidebar.textContent = nombre;
        } else if (nodos.sesionUsuarioSidebar) {
            nodos.sesionUsuarioSidebar.textContent = "Usuario #" + idUsuario;
        }

        if (nodos.avatarUsuario) {
            nodos.avatarUsuario.textContent = inicialesUsuario(usuario);
        }
    }

    /** Extrae las iniciales del nombre del usuario para el avatar. */
    function inicialesUsuario(usuario) {
        const nombre = usuario && usuario.nombre;
        if (nombre && typeof nombre === "string") {
            const partes = nombre.trim().split(/\s+/).filter(Boolean);
            return partes
                .map((p) => p.charAt(0).toUpperCase())
                .slice(0, 2)
                .join("") || "AF";
        }
        return "AF";
    }

    function cerrarSesion() {
        Sesion.borrar();
        idUsuario = null;
        Sesion.irAlAcceso();
    }

    async function exigirSesion() {
        const guardado = Sesion.obtener();
        if (guardado === null) {
            Sesion.irAlAcceso();
            return null;
        }
        try {
            const usuario = await Sesion.verificarUsuario(guardado);
            idUsuario = guardado;
            return usuario;
        } catch (error) {
            Sesion.borrar();
            Sesion.irAlAcceso();
            return null;
        }
    }

    function registrarEventos() {
        if (nodos.botonCerrarSesion) {
            nodos.botonCerrarSesion.addEventListener("click", cerrarSesion);
        }
        if (nodos.botonMenuMovil) {
            nodos.botonMenuMovil.addEventListener("click", abrirSidebar);
        }
        if (nodos.botonCerrarSidebar) {
            nodos.botonCerrarSidebar.addEventListener("click", cerrarSidebar);
        }
        if (nodos.sidebarBackdrop) {
            nodos.sidebarBackdrop.addEventListener("click", cerrarSidebar);
        }
        nodos.enlaces.forEach((enlace) => {
            enlace.addEventListener("click", () => cambiarVista(enlace.dataset.vista));
        });
    }

    async function iniciar() {
        capturarNodos();

        const usuario = await exigirSesion();
        if (usuario === null) {
            return;
        }

        registrarEventos();
        App.Categorias.inicializar();
        App.Resumen.inicializar();
        App.Movimientos.inicializar();
        App.Analytics.inicializar();
        App.Dashboard.inicializar();

        mostrarAplicacion(usuario);
        await App.Categorias.sincronizar(idUsuario);
        await cambiarVista("panel");
    }

    App.usuarioActivo = usuarioActivo;
    App.refrescarDatosDependientes = refrescarDatosDependientes;
    App.cambiarVista = cambiarVista;

    document.addEventListener("DOMContentLoaded", iniciar);
})(window.App);
