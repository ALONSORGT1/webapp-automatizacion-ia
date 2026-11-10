const $ = (id) => document.getElementById(id);

export function marcarErrores(errores) {
  for (const campo of ["tema", "nivel", "pregunta"]) {
    const el = $(campo), msg = $(`${campo}-error`);
    const m = errores[campo];
    el.classList.toggle("is-invalid", Boolean(m));
    el.setAttribute("aria-invalid", m ? "true" : "false");
    msg.textContent = m || "";
  }
}

export function setCargando(on) {
  $("estado-carga").classList.toggle("d-none", !on);
  $("estado-carga").classList.toggle("d-flex", on);
  $("btn-consultar").disabled = on;
  $("btn-consultar").setAttribute("aria-busy", String(on));
  if (on) { $("area-error").classList.add("d-none"); $("resultado").classList.add("d-none"); $("vacio").classList.add("d-none"); }
}

export function mostrarError(mensaje) {
  $("mensaje-error").textContent = mensaje;
  $("area-error").classList.remove("d-none");
  $("vacio").classList.add("d-none");
}

const ETIQUETAS = { nativo: "Nodo OpenAI (nativo)", http: "HTTP Request (Responses API)" };

export function mostrarResultado(r) {
  $("res-tema").textContent = r.tema;
  $("res-nivel").textContent = r.nivel;
  $("res-integracion").textContent = ETIQUETAS[r.integracion] || r.integracion;
  $("res-texto").textContent = r.respuesta; // textContent: nunca HTML
  $("resultado").classList.remove("d-none");
  $("area-error").classList.add("d-none");
  $("vacio").classList.add("d-none");
}

export function limpiarTodo() {
  $("formulario").reset();
  marcarErrores({});
  $("resultado").classList.add("d-none");
  $("area-error").classList.add("d-none");
  $("vacio").classList.remove("d-none");
  actualizarContador();
}

export function actualizarContador() {
  $("contador").textContent = String($("pregunta").value.length);
}

export function leerFormulario() {
  return {
    tema: $("tema").value,
    nivel: $("nivel").value,
    pregunta: $("pregunta").value,
    integracion: document.querySelector('input[name="integracion"]:checked')?.value ?? "",
  };
}
