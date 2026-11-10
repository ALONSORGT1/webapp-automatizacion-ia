import { CONFIG } from "./config.js";

export const TEMAS = ["Inteligencia artificial", "Redes", "Programación", "Bases de datos", "Internet de las cosas (IoT)"];
export const NIVELES = ["Básico", "Intermedio", "Avanzado"];
export const INTEGRACIONES = ["nativo", "http"];

export function normalizarPregunta(texto) {
  return String(texto ?? "").normalize("NFC").replace(/\s+/g, " ").trim();
}

/** Devuelve { valido, errores: {campo: msg}, datos } */
export function validar({ tema, nivel, pregunta, integracion }) {
  const errores = {};
  if (!TEMAS.includes(tema)) errores.tema = "Selecciona un tema de la lista.";
  if (!NIVELES.includes(nivel)) errores.nivel = "Selecciona un nivel de la lista.";
  if (!INTEGRACIONES.includes(integracion)) errores.integracion = "Selecciona una integración válida.";
  const p = normalizarPregunta(pregunta);
  if (!p) errores.pregunta = "Escribe tu pregunta.";
  else if (p.length > CONFIG.MAX_PREGUNTA) errores.pregunta = `La pregunta no puede superar ${CONFIG.MAX_PREGUNTA} caracteres.`;
  return { valido: Object.keys(errores).length === 0, errores, datos: { tema, nivel, pregunta: p, integracion } };
}
