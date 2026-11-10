import { CONFIG } from "./config.js";
import { validar } from "./validation.js";
import { consultar } from "./api.js";
import * as ui from "./ui.js";

const form = document.getElementById("formulario");
let enCurso = false;

document.getElementById("limite").textContent = String(CONFIG.MAX_PREGUNTA);
document.getElementById("pregunta").addEventListener("input", ui.actualizarContador);
document.getElementById("btn-limpiar").addEventListener("click", ui.limpiarTodo);

async function enviar() {
  if (enCurso) return;
  const { valido, errores, datos } = validar(ui.leerFormulario());
  ui.marcarErrores(errores);
  if (!valido) {
    document.querySelector(".is-invalid")?.focus();
    return;
  }
  enCurso = true;
  ui.setCargando(true);
  try {
    ui.mostrarResultado(await consultar(datos));
  } catch (e) {
    ui.mostrarError(e.message || "No se pudo completar la consulta.");
  } finally {
    enCurso = false;
    ui.setCargando(false);
  }
}

form.addEventListener("submit", (e) => { e.preventDefault(); enviar(); });
document.getElementById("btn-reintentar").addEventListener("click", enviar);
