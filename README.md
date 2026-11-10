# 3.4 Web app para automatización IA

Web estática (HTML5, CSS3, Bootstrap 5, JS ES Modules) que envía `tema`, `nivel`, `pregunta` e `integracion` por `POST` a un Webhook de n8n Cloud, el cual consulta a OpenAI (nodo nativo o HTTP Request a `/v1/responses`) y devuelve JSON uniforme.

Web → Webhook n8n → validación → Switch (`nativo` | `http`) → OpenAI → normalización → Respond to Webhook → UI.

## Estructura
- `index.html`, `css/styles.css`, `assets/favicon.svg`
- `js/config.js` (solo datos públicos: Production URL), `validation.js`, `api.js`, `ui.js`, `main.js`
- `workflow/3.4-webapp-ia-api.workflow.json`: workflow importable en n8n (sin credenciales)

## Contrato
Solicitud: `{ "tema", "nivel", "pregunta", "integracion" }` (`nativo` | `http`, pregunta ≤ 1000 caracteres).
Éxito (200): `{ "ok": true, "respuesta", "tema", "nivel", "integracion" }`.
Error: `{ "ok": false, "mensaje" }` con 400 (entrada inválida) o 502 (fallo del proveedor).

## Ejecutar localmente
`python -m http.server 8000` y abrir `http://localhost:8000` (no `file://`). Pon la Production URL en `js/config.js`.

## Sitio y repositorio
- Sitio: https://alonsorgt1.github.io/webapp-automatizacion-ia/
- Repositorio: https://github.com/ALONSORGT1/webapp-automatizacion-ia

## Despliegue en GitHub Pages
El sitio no necesita compilación ni instalación de dependencias. En **Settings → Pages**, selecciona **Deploy from a branch**, la rama `main` y la carpeta `/ (root)`. Cada cambio enviado a `main` se publica automáticamente.

## Configurar las consultas de IA
1. Importa `workflow/3.4-webapp-ia-api.workflow.json` en n8n.
2. Vincula tu credencial de OpenAI a los nodos correspondientes y activa el workflow.
3. Copia la **Production URL** del Webhook en `WEBHOOK_URL` dentro de `js/config.js`.
4. Configura el origen permitido de n8n para `https://alonsorgt1.github.io` y comprueba las solicitudes CORS, incluido el preflight si usas JSON.
5. Envía el cambio a `main` y prueba una consulta desde el sitio publicado.

GitHub Pages aloja la interfaz; las consultas dependen del workflow activo en n8n. Mientras `WEBHOOK_URL` esté vacía, la página se puede abrir, pero muestra un aviso al intentar consultar.

## Seguridad
La clave de OpenAI vive solo en Credentials de n8n. La URL del Webhook es pública y CORS no es autenticación; desactiva el Webhook tras la evaluación.

## Estado
La interfaz está preparada para GitHub Pages. Pendiente: configurar la Production URL del Webhook, vincular las credenciales en n8n y completar las pruebas de integración y conclusiones.
