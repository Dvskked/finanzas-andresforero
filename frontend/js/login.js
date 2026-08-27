/**
 * login.js — Lógica de la pantalla de acceso de Finanzas AF (index.html).
 *
 * Flujo:
 *   - Iniciar sesión: valida correo y contraseña contra POST /api/usuarios/login.
 *   - Crear cuenta:   registra vía POST /api/usuarios (la API cifra con bcrypt).
 *
 * En ambos casos, al validar se guarda la sesión y se navega al panel.
 */
(function (App) {
    "use strict";

    const UI = App.UI;
    const Sesion = App.Sesion;

    let nodos = {};

    function capturarNodos() {
        nodos = {
            pestanas: Array.prototype.slice.call(document.querySelectorAll(".pestanas__boton")),
            paneles: Array.prototype.slice.call(document.querySelectorAll(".acceso__panel")),

            formIngreso: document.getElementById("form-ingreso"),
            ingresoCorreo: document.getElementById("ingreso-correo"),
            ingresoContrasena: document.getElementById("ingreso-contrasena"),
            errorIngreso: document.getElementById("error-ingreso"),
            botonIngresar: document.getElementById("boton-ingresar"),

            formRegistro: document.getElementById("form-registro"),
            registroNombre: document.getElementById("registro-nombre"),
            registroCorreo: document.getElementById("registro-correo"),
            registroContrasena: document.getElementById("registro-contrasena"),
            errorRegistro: document.getElementById("error-registro"),
            botonRegistrar: document.getElementById("boton-registrar")
        };
    }

    /** Alterna entre el panel de inicio de sesión y el de registro. */
    function cambiarPanel(nombre) {
        nodos.paneles.forEach((panel) => {
            panel.hidden = panel.id !== "panel-" + nombre;
        });
        nodos.pestanas.forEach((pestana) => {
            if (pestana.dataset.panel === nombre) {
                pestana.setAttribute("aria-current", "page");
            } else {
                pestana.removeAttribute("aria-current");
            }
        });
        if (nombre === "ingreso" && nodos.ingresoCorreo) {
            nodos.ingresoCorreo.focus();
        } else if (nombre === "registro" && nodos.registroNombre) {
            nodos.registroNombre.focus();
        }
    }

    function entrar(usuario) {
        Sesion.guardar(usuario.id_usuario);
        Sesion.irAlPanel();
    }

    async function alIniciarSesion(evento) {
        evento.preventDefault();
        UI.limpiarErrorFormulario(nodos.errorIngreso);

        const correo = nodos.ingresoCorreo.value.trim();
        const contrasena = nodos.ingresoContrasena.value;

        if (!correo || !correo.includes("@")) {
            nodos.ingresoCorreo.setAttribute("aria-invalid", "true");
            UI.mostrarErrorFormulario(nodos.errorIngreso, "Introduce un correo electrónico válido.");
            nodos.ingresoCorreo.focus();
            return;
        }
        nodos.ingresoCorreo.removeAttribute("aria-invalid");

        if (!contrasena) {
            nodos.ingresoContrasena.setAttribute("aria-invalid", "true");
            UI.mostrarErrorFormulario(nodos.errorIngreso, "Introduce tu contraseña.");
            nodos.ingresoContrasena.focus();
            return;
        }
        nodos.ingresoContrasena.removeAttribute("aria-invalid");

        nodos.botonIngresar.disabled = true;
        try {
            const usuario = await Sesion.autenticar(correo, contrasena);
            entrar(usuario);
        } catch (error) {
            UI.mostrarErrorFormulario(nodos.errorIngreso, UI.mensajeDeExcepcion(error));
        } finally {
            nodos.botonIngresar.disabled = false;
        }
    }

    async function alRegistrar(evento) {
        evento.preventDefault();
        UI.limpiarErrorFormulario(nodos.errorRegistro);

        const nombre = nodos.registroNombre.value.trim();
        const correo = nodos.registroCorreo.value.trim();
        const contrasena = nodos.registroContrasena.value;

        if (nombre.length < 2) {
            UI.mostrarErrorFormulario(nodos.errorRegistro, "El nombre debe tener al menos 2 caracteres.");
            nodos.registroNombre.focus();
            return;
        }
        if (!correo || !correo.includes("@")) {
            UI.mostrarErrorFormulario(nodos.errorRegistro, "Introduce un correo electrónico válido.");
            nodos.registroCorreo.focus();
            return;
        }
        if (contrasena.length < 8) {
            UI.mostrarErrorFormulario(nodos.errorRegistro, "La contraseña debe tener al menos 8 caracteres.");
            nodos.registroContrasena.focus();
            return;
        }

        nodos.botonRegistrar.disabled = true;
        try {
            const usuario = await App.Api.registrar({ nombre, correo, contrasena });
            nodos.formRegistro.reset();
            entrar(usuario);
        } catch (error) {
            UI.mostrarErrorFormulario(nodos.errorRegistro, UI.mensajeDeExcepcion(error));
        } finally {
            nodos.botonRegistrar.disabled = false;
        }
    }

    /** Si ya había una sesión válida en esta pestaña, continúa al panel. */
    async function continuarSiHaySesion() {
        const guardado = Sesion.obtener();
        if (guardado === null) {
            return;
        }
        try {
            await Sesion.verificarUsuario(guardado);
            Sesion.irAlPanel();
        } catch (error) {
            Sesion.borrar();
        }
    }

    function iniciar() {
        capturarNodos();

        nodos.formIngreso.addEventListener("submit", alIniciarSesion);
        nodos.formRegistro.addEventListener("submit", alRegistrar);
        nodos.pestanas.forEach((pestana) => {
            pestana.addEventListener("click", () => cambiarPanel(pestana.dataset.panel));
        });

        return continuarSiHaySesion();
    }

    document.addEventListener("DOMContentLoaded", iniciar);
})(window.App);
