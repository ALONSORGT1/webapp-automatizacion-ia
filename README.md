# 3.4 Web app para automatización IA

Web estática (HTML5, CSS3, Bootstrap 5, JS ES Modules) que envía `tema`, `nivel`, `pregunta` e `integracion` por `POST` a un Webhook de n8n Cloud, el cual consulta a OpenAI (nodo nativo o HTTP Request a `/v1/responses`) y devuelve JSON uniforme.

Web → Webhook n8n → validación → Switch (`nativo` | `http`) → OpenAI → normalización → Respond to Webhook → UI.

## Estructura
- `index.html`, `css/styles.css`, `assets/favicon.svg`
- `js/config.js` (solo datos públicos: Production URL), `validation.js`, `api.js`, `ui.js`, `main.js`

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

## Workflow n8n
`3.4 Web app para automatización IA - API` (n8n Cloud): Webhook POST (único) → Validar entrada → ¿válida? (si no, 400) → Normalizar entrada (Set) → Switch por `integracion` → OpenAI nativo **o** HTTP Request a `/v1/responses` (ambos con la credencial gestionada en n8n, modelo `gpt-4o-mini`, máx. 900 tokens) → Normalizar salida → Respond to Webhook. Si OpenAI falla, la salida es un 502 genérico sin detalles internos.

## Pruebas ejecutadas (curl contra la Production URL)
| Caso | Entrada | Esperado | Observado | Cumple |
|---|---|---|---|---|
| Nativo, Básico | Redes / ¿Qué es una dirección IP? | 200 + contrato | 200, `ok:true`, 4 secciones | Sí |
| HTTP, Intermedio | misma pregunta | 200 + mismo contrato | 200, `ok:true`, respuesta distinta y más técnica | Sí |
| Pregunta vacía | espacios | 400 sin llamar a OpenAI | 400 `{"ok":false,"mensaje":"Escribe tu pregunta."}` | Sí |
| Preflight CORS | OPTIONS con Origin de Pages | 204 + cabeceras CORS | 204, `access-control-allow-origin` del origen, `allow-headers: content-type` | Sí |
| Navegador en Pages | Bases de datos / Avanzado / http, y campos vacíos | Respuesta renderizada sin recargar; errores visibles | Respuesta de 2 869 caracteres con tema, nivel e integración; spinner y botón deshabilitado; errores de validación; sin errores en consola ni scroll horizontal | Sí |
| Ejecuciones | n8n Executions | una rama por petición | 5 ejecuciones exitosas registradas | Sí |

Pendientes de ejecutar: cambio de tema consecutivo, falla de red/timeout y vista móvil.

## Entrega
- Repositorio: https://github.com/ALONSORGT1/webapp-automatizacion-ia
- Webhook (Production URL, pública): https://cloudfloww.app.n8n.cloud/webhook/webapp-automatizacion-ia
- GitHub Pages: https://alonsorgt1.github.io/webapp-automatizacion-ia/ (publicado desde `main` y `/(root)`).
