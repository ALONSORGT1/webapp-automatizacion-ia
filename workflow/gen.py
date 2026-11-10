import json
MODEL = "gpt-4.1-mini"

validar = r"""
const TEMAS = ['Inteligencia artificial','Redes','Programación','Bases de datos','Internet de las cosas (IoT)'];
const NIVELES = ['Básico','Intermedio','Avanzado'];
const INTEG = ['nativo','http'];
const CLAVES = ['tema','nivel','pregunta','integracion'];
let b = $input.first().json.body;
const fail = (m) => [{ json: { ok: false, status: 400, mensaje: m } }];
if (!b || typeof b !== 'object' || Array.isArray(b)) return fail('Revisa los campos e inténtalo de nuevo.');
if (Object.keys(b).some(k => !CLAVES.includes(k))) return fail('Revisa los campos e inténtalo de nuevo.');
for (const k of CLAVES) if (typeof b[k] !== 'string') return fail('Revisa los campos e inténtalo de nuevo.');
const pregunta = b.pregunta.normalize('NFC').replace(/\s+/g,' ').trim();
if (!pregunta || pregunta.length > 1000) return fail('La pregunta es obligatoria y no puede superar 1000 caracteres.');
if (!TEMAS.includes(b.tema) || !NIVELES.includes(b.nivel) || !INTEG.includes(b.integracion)) return fail('Revisa los campos e inténtalo de nuevo.');
return [{ json: { ok: true, tema: b.tema, nivel: b.nivel, pregunta, integracion: b.integracion } }];
"""

normalizar = r"""
const base = $('Normalizar entrada').first().json;
const r = $input.first().json || {};
function textos(o, out = []) {
  if (o == null) return out;
  if (typeof o === 'string') return out;
  if (Array.isArray(o)) { o.forEach(x => textos(x, out)); return out; }
  if (typeof o === 'object') {
    if ((o.type === 'output_text' || o.type === 'text') && typeof o.text === 'string') out.push(o.text);
    for (const v of Object.values(o)) if (typeof v === 'object') textos(v, out);
  }
  return out;
}
let t = '';
if (typeof r.output_text === 'string') t = r.output_text;
else if (typeof r.text === 'string') t = r.text;
else t = textos(r).join('\n');
t = (t || '').trim();
if (r.error || !t) return [{ json: { ok: false, status: 502, mensaje: 'El asistente no pudo generar una respuesta. Inténtalo de nuevo.' } }];
return [{ json: { ok: true, status: 200, respuesta: t, tema: base.tema, nivel: base.nivel, integracion: base.integracion } }];
"""

INSTR = ("Eres un asistente académico de Tecnologías de la Información. Responde en español de México. "
 "Ajusta la profundidad al nivel indicado. Estructura la respuesta con: Concepto, Funcionamiento, Ejemplo y Recomendación técnica. "
 "Sé conciso, claro y verificable; si no estás seguro de algo, dilo.")
user_expr = "Tema: {{ $json.tema }}\nNivel: {{ $json.nivel }}\nPregunta: {{ $json.pregunta }}"

def node(name, type_, tv, pos, params, **kw):
    n = {"parameters": params, "name": name, "type": type_, "typeVersion": tv, "position": pos}
    n.update(kw); return n

nodes = [
 node("Webhook","n8n-nodes-base.webhook",2,[0,300],{"httpMethod":"POST","path":"webapp-automatizacion-ia","responseMode":"responseNode","options":{"allowedOrigins":"*"}},webhookId="webapp-automatizacion-ia"),
 node("Validar entrada","n8n-nodes-base.code",2,[220,300],{"jsCode":validar.strip()}),
 node("¿Entrada válida?","n8n-nodes-base.if",2.2,[440,300],{"conditions":{"options":{"caseSensitive":True,"typeValidation":"strict"},"conditions":[{"id":"c1","leftValue":"={{ $json.ok }}","rightValue":True,"operator":{"type":"boolean","operation":"true","singleValue":True}}],"combinator":"and"}}),
 node("Normalizar entrada","n8n-nodes-base.set",3.4,[660,200],{"mode":"manual","assignments":{"assignments":[
   {"id":"a1","name":"tema","value":"={{ $json.tema }}","type":"string"},
   {"id":"a2","name":"nivel","value":"={{ $json.nivel }}","type":"string"},
   {"id":"a3","name":"pregunta","value":"={{ $json.pregunta }}","type":"string"},
   {"id":"a4","name":"integracion","value":"={{ $json.integracion }}","type":"string"}]},"options":{}}),
 node("Elegir integración","n8n-nodes-base.switch",3.2,[880,200],{"rules":{"values":[
   {"conditions":{"options":{"caseSensitive":True,"typeValidation":"strict"},"conditions":[{"id":"s1","leftValue":"={{ $json.integracion }}","rightValue":"nativo","operator":{"type":"string","operation":"equals"}}],"combinator":"and"},"renameOutput":True,"outputKey":"nativo"},
   {"conditions":{"options":{"caseSensitive":True,"typeValidation":"strict"},"conditions":[{"id":"s2","leftValue":"={{ $json.integracion }}","rightValue":"http","operator":{"type":"string","operation":"equals"}}],"combinator":"and"},"renameOutput":True,"outputKey":"http"}]},"options":{}}),
 node("OpenAI (nativo)","@n8n/n8n-nodes-langchain.openAi",1.8,[1120,100],{"resource":"text","operation":"response","modelId":{"__rl":True,"value":MODEL,"mode":"id"},
   "responses":{"values":[{"role":"user","content":user_expr}]},"options":{"instructions":INSTR,"maxTokens":700}},
   onError="continueRegularOutput",credentials={"openAiApi":{"id":"VINCULAR","name":"VINCULAR credencial OpenAI"}}),
 node("OpenAI (HTTP Request)","n8n-nodes-base.httpRequest",4.2,[1120,300],{"method":"POST","url":"https://api.openai.com/v1/responses",
   "authentication":"predefinedCredentialType","nodeCredentialType":"openAiApi","sendHeaders":True,
   "headerParameters":{"parameters":[{"name":"Content-Type","value":"application/json"}]},
   "sendBody":True,"specifyBody":"json",
   "jsonBody":"={{ JSON.stringify({ model: '"+MODEL+"', instructions: "+json.dumps(INSTR, ensure_ascii=False)+", input: 'Tema: ' + $json.tema + '\\nNivel: ' + $json.nivel + '\\nPregunta: ' + $json.pregunta, max_output_tokens: 700 }) }}",
   "options":{"timeout":50000}},
   onError="continueRegularOutput",credentials={"openAiApi":{"id":"VINCULAR","name":"VINCULAR credencial OpenAI"}}),
 node("Normalizar salida","n8n-nodes-base.code",2,[1360,200],{"jsCode":normalizar.strip()}),
 node("Responder","n8n-nodes-base.respondToWebhook",1.1,[1600,300],{"respondWith":"json","responseBody":"={{ (() => { const {status, ...rest} = $json; return JSON.stringify(rest); })() }}",
   "options":{"responseCode":"={{ $json.status || 200 }}","responseHeaders":{"entries":[{"name":"Content-Type","value":"application/json; charset=utf-8"}]}}}),
]
c = lambda *a: {"node":a[0],"type":"main","index":a[1] if len(a)>1 else 0}
conn = {
 "Webhook":{"main":[[c("Validar entrada")]]},
 "Validar entrada":{"main":[[c("¿Entrada válida?")]]},
 "¿Entrada válida?":{"main":[[c("Normalizar entrada")],[c("Responder")]]},
 "Normalizar entrada":{"main":[[c("Elegir integración")]]},
 "Elegir integración":{"main":[[c("OpenAI (nativo)")],[c("OpenAI (HTTP Request)")]]},
 "OpenAI (nativo)":{"main":[[c("Normalizar salida")]]},
 "OpenAI (HTTP Request)":{"main":[[c("Normalizar salida")]]},
 "Normalizar salida":{"main":[[c("Responder")]]},
}
wf = {"name":"3.4 Web app para automatización IA - API","nodes":nodes,"connections":conn,"settings":{"executionOrder":"v1"}}
json.dump(wf, open("3.4-webapp-ia-api.workflow.json","w"), ensure_ascii=False, indent=2)
print("ok", len(nodes))
