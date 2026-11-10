import { CONFIG } from "./config.js";

export class ApiError extends Error {
  constructor(mensaje, estado = 0) { super(mensaje); this.estado = estado; }
}

const MENSAJES = {
  400: "Revisa los campos e inténtalo de nuevo.",
  401: "El servicio no está autorizado en este momento.",
  403: "El servicio rechazó la solicitud.",
  429: "Hay demasiadas consultas. Espera un momento e inténtalo de nuevo.",
  500: "El servicio tuvo un error interno. Inténtalo más tarde.",
  502: "El asistente no respondió correctamente. Inténtalo de nuevo.",
  503: "El servicio no está disponible por ahora. Inténtalo más tarde.",
};

function construirPeticion(datos) {
  if (CONFIG.REQUEST_FORMAT === "form") {
    return {
      headers: { "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8" },
      body: new URLSearchParams(datos).toString(),
    };
  }
  return { headers: { "Content-Type": "application/json" }, body: JSON.stringify(datos) };
}

export async function consultar(datos) {
  if (!CONFIG.WEBHOOK_URL) throw new ApiError("La URL del Webhook aún no está configurada.");
  const ctrl = new AbortController();
  const t = setTimeout(() => ctrl.abort(), CONFIG.TIMEOUT_MS);
  let resp;
  try {
    resp = await fetch(CONFIG.WEBHOOK_URL, { method: "POST", signal: ctrl.signal, ...construirPeticion(datos) });
  } catch (e) {
    if (e.name === "AbortError") throw new ApiError("La consulta tardó demasiado. Inténtalo de nuevo.");
    throw new ApiError("No se pudo conectar con el servicio (red o permisos de origen). Inténtalo de nuevo.");
  } finally {
    clearTimeout(t);
  }

  let json = null;
  try { json = await resp.json(); } catch { /* cuerpo no JSON */ }

  if (!resp.ok || !json || json.ok !== true) {
    const msg = (json && typeof json.mensaje === "string" && json.mensaje) || MENSAJES[resp.status] || "No se pudo completar la consulta.";
    throw new ApiError(msg, resp.status);
  }
  if (typeof json.respuesta !== "string" || !json.respuesta.trim()) {
    throw new ApiError("La respuesta del servicio no tiene el formato esperado.", resp.status);
  }
  return json;
}
