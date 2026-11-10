// Solo datos públicos. NUNCA pongas claves de OpenAI aquí.
export const CONFIG = {
  // Production URL del Webhook de n8n (workflow activo en n8n Cloud).
  WEBHOOK_URL: "https://cloudfloww.app.n8n.cloud/webhook/webapp-automatizacion-ia",
  // "json" (Content-Type: application/json, requiere preflight CORS) o
  // "form" (application/x-www-form-urlencoded, evita preflight por ese encabezado).
  REQUEST_FORMAT: "json",
  TIMEOUT_MS: 60000,
  MAX_PREGUNTA: 1000,
};
