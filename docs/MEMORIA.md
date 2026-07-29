# MEMORIA DEL PROYECTO: TutorIA

> **Versión:** 2.0.0 — Reset post-audio  
> **Fecha:** 29 Julio 2026  
> **Autor:** Jose (josecortessanchez28-png)  
> **Repositorio:** https://github.com/josecortessanchez28-png/TutorIA

---

## 1. VISIÓN GENERAL

**TutorIA** es un agente de inteligencia artificial diseñado para actuar como tutor personal interactivo. Su propósito es guiar al usuario paso a paso en el aprendizaje y uso de aplicaciones con curva de aprendizaje alta, como Burp Suite (ciberseguridad), CapCut (edición de vídeo), y cualquier otra aplicación compleja.

### 1.1 Objetivos Principales

- **Enseñar mediante la práctica:** El agente ve lo que el usuario hace en pantalla y le guía verbalmente paso a paso.
- **Interacción natural por voz:** Conversación fluida usando micrófono y cascos simples. Sin necesidad de escribir.
- **Investigación activa:** El agente busca información actualizada en internet (foros, docs oficiales, YouTube) para mantener sus respuestas precisas.
- **Cero coste:** Todo el proyecto se sostiene sobre APIs gratuitas y servicios cloud free tier. Sin inversión económica.

### 1.2 Casos de Uso

| Aplicación | Campo | Qué enseña TutorIA |
|---|---|---|
| Burp Suite | Ciberseguridad | Interceptar peticiones, analizar tráfico, explotar vulnerabilidades |
| OWASP ZAP | Ciberseguridad | Escaneo de vulnerabilidades, proxy de pruebas |
| CapCut | Edición de vídeo | Cortar, fusionar, efectos, transiciones, exportar |
| Blender | Diseño 3D | Modelado básico, texturizado, renderizado |
| Metasploit | Ciberseguridad | Explotación, post-explotación, pivoting |

---

## 2. DECISIÓN DE ARQUITECTURA

Se descartó completamente el enfoque local (Ollama + modelos cuantizados) por:

1. **Modelos locales inferiores**: Qwen 3B no puede competir con Llama 3.3 70B o GPT-OSS 120B en razonamiento y tool calling.
2. **Mantenimiento**: Actualizar modelos, gestionar descargas, dependencias del sistema, espacio en disco.
3. **Portabilidad**: El usuario debe poder acceder desde cualquier máquina sin depender de hardware concreto.

La arquitectura elegida es **cloud-first**:

- **LLM**: Groq API (principal) + OpenRouter (fallback) — ambos gratuitos, con tool calling nativo, modelos actualizados semanalmente.
- **STT**: Groq Whisper large-v3-turbo vía API — 2000 requests/día gratis, 20 RPM.
- **TTS**: edge-tts — llama a la API de Microsoft Edge, voces naturales, sin coste.
- **Screen Capture**: JavaScript Screen Capture API desde el navegador del usuario.
- **Servidor**: Python + FastAPI desplegado en Render (512MB, 0.1 CPU) o Koyeb (1GB, 0.5 CPU).

---

## 3. STACK TECNOLÓGICO DETALLADO

### 3.1 Backend (Servidor Cloud)

| Componente | Tecnología | Versión | Justificación |
|---|---|---|---|
| Lenguaje | Python | 3.12+ | Ecosistema maduro para IA, librerías nativas |
| Framework web | FastAPI | Última | Rendimiento, WebSockets nativos, tipado |
| Servidor ASGI | Uvicorn | Última | Estándar para FastAPI, bajo overhead |
| Cliente LLM | groq (SDK oficial) | Última | OpenAI-compatible, tool calling nativo |
| Config | YAML + dotenv | - | Config editable sin tocar código |

### 3.2 Frontend (Navegador)

| Componente | Tecnología |
|---|---|
| HTML/CSS/JS | Vanilla (sin framework) |
| WebSocket | Nativo JS (WebSocket API) |
| Cache busting | `app.v{N}.js` (nombre único por versión) |

### 3.3 APIs Externas

| API | Uso | Modelos disponibles | Límites free tier |
|---|---|---|---|
| Groq | LLM principal + STT | Llama 3.3 70B, Whisper | 30 RPM, 6K TPM, 1K RPD |
| OpenRouter | LLM fallback | Múltiples modelos gratuitos | 20 RPM, 50 RPD |

---

## 4. ARQUITECTURA DEL SISTEMA (actual)

```
[CLIENTE - Navegador]
  └── Chat texto → WebSocket → [SERVIDOR - Render]
                                   ├── FastAPI /ws (streaming)
                                   ├── POST /chat (fallback)
                                   └── Groq API (LLM)
```

El flujo es:
1. Usuario escribe en el chat
2. Mensaje se envía por WebSocket (o POST si WS no conecta)
3. Servidor recibe, construye prompt con system config (YAML) + historial
4. Groq genera respuesta en streaming
5. Chunks llegan al cliente y se renderizan letra por letra
6. Al terminar, servidor envía `{"done": true}` y guarda en historial

---

## 5. HISTORIAL DE VERSIONES

### v2.0.0 — Reset post-audio + documentación de fallo (29 Jul 2026)
**Cambios:**
- Reset completo a estado texto puro
- Eliminado todo el código de audio (frontend, servidor, cliente LLM)
- Eliminado botón de micrófono del HTML y CSS
- Eliminado `app.v4.js` del repositorio
- Adoptada estrategia de cache busting: `app.v{N}.js` (nombre único por versión)
- Documentado el fallo del audio en .cm y MEMORIA.md
- Añadidas reglas 16, 17, 18 al .cm (cache busting, una feature a la vez, documento de diseño)

**Lecciones aprendidas del fallo de audio:**
1. **Una feature a la vez**: audio se implementó sobre streaming WS que tenía minutos de vida.
2. **Cache JS**: el navegador servía código viejo, haciendo que los fixes parecieran no funcionar.
3. **Race condition**: `getUserMedia` asíncrono + interacción del usuario crearon un bucle de errores.
4. **Múltiples enfoques**: push-to-talk → toggle → versiones híbridas sin validar entre cambios.
5. **Solución adoptada**: reset completo. El audio se re-implementará desde cero con enfoque push-to-talk probado.

### v1.3.0 — WebSocket streaming + memoria conversación (29 Jul 2026)
- Endpoint WebSocket /ws con streaming chunk-by-chunk
- `AsyncGroq` reemplazado por `Groq` síncrono + `ThreadPoolExecutor` + `asyncio.Queue`
- Memoria de conversación por sesión WS (history)
- Frontend conecta WS, renderiza chunks en tiempo real
- Eliminado timeout de 2s (fallback a POST) que causaba race conditions

### v1.2.0 — Config YAML + Concision (29 Jul 2026)
- Nuevo sistema de configuración externa: `agent/agent_config.yaml`
- System prompt se construye dinámicamente desde el YAML
- Respuestas optimizadas para conversación fluida

### v1.1.0 — Frontend visual + paleta ELJOSE (29 Jul 2026)
- Frontend web completo: index.html + style.css + app.js
- Paleta oscura neón con gradiente morado-rosa
- Chat visual con burbujas, typing indicator, scroll automático

### v1.0.0 — Primer deploy (29 Jul 2026)
- FastAPI server con /health y POST /chat
- Cliente Groq API real con llama-3.3-70b-versatile
- Dockerfile + render.yaml para deploy en Render
- Despliegue en https://tutoria-v1n7.onrender.com

---

## 6. ESTRUCTURA DEL PROYECTO

```
D:\TutorIA\
├── agent/                  # Config YAML, cliente Groq, prompts
│   ├── agent_config.yaml
│   ├── llm_client.py
│   └── prompts.py
├── server/                 # FastAPI server + endpoints
│   └── main.py
├── frontend/               # Cliente web
│   ├── index.html
│   ├── style.css
│   └── app.js
├── config/                 # Configuración YAML
│   ├── default.yaml
│   └── settings.py
├── docs/                   # Documentación
│   └── MEMORIA.md
├── tutoria.cm              # Contexto del proyecto
├── Dockerfile
├── render.yaml
├── requirements.txt
└── .gitignore
```

---

## 7. DECISIONES TÉCNICAS

### 7.1 Estrategia de Cache Busting (NUEVA)
**Problema detectado en v2.0:** El navegador cacheaba `app.js` incluso con `Cache-Control: no-cache`. Los cambios en el JS no se reflejaban en el cliente.
**Solución:** Cada versión de JS usa un nombre único: `app.v{N}.js`. El HTML siempre apunta al nuevo nombre. El navegador NO PUEDE tener el archivo en caché porque nunca ha visto ese nombre antes.

### 7.2 ¿Por qué push-to-talk y no toggle? (NUEVA)
**Problema:** El toggle (clic para grabar, clic para parar) introdujo una race condition irresoluble: `getUserMedia` es asíncrono, y el segundo clic podía ocurrir antes de que `getUserMedia` resolviera.
**Solución:** Push-to-talk (mantener presionado, soltar para enviar). El tiempo de pulsación proporciona un buffer natural para que `getUserMedia` resuelva.

### 7.3 Streaming asíncrono con Groq
Se intentó `AsyncGroq` pero falló en Render por problemas de compatibilidad con el event loop.
Solución actual: `Groq` síncrono + `ThreadPoolExecutor` + `asyncio.Queue`. Funciona correctamente en producción.

### 7.4 ¿Por qué navegador como cliente?
- Sin instalación: funciona en cualquier máquina con navegador
- APIs nativas para screen capture y mic (getDisplayMedia, getUserMedia)
- WebSocket para comunicación bidireccional en tiempo real
- Portabilidad total

---

## 8. PLAN DE FASES (post-reset)

### FASE 0: Foundation — ✅ Completa
### FASE 1: Core Agent — ✅ Completa (texto + streaming + memoria)
### FASE 2: Voice Pipeline — ❌ Pendiente de re-implementación
  - [ ] Implementar push-to-talk con getUserMedia único al cargar página
  - [ ] Cache busting: app.v5.js para el JS con audio
  - [ ] Validar funcionamiento durante 7 días antes de siguiente fase
### FASE 3-8: Pendientes

---

## 9. VARIABLES DE ENTORNO

```bash
GROQ_API_KEY=          # Obligatoria
TUTORIA_MODEL=         # Opcional (default: llama-3.3-70b-versatile)
TUTORIA_WHISPER=       # Opcional (default: whisper-large-v3-turbo)
```

---

## 10. DEPENDENCIAS PYTHON

```
fastapi>=0.115
uvicorn[standard]>=0.34
pydantic>=2
pyyaml>=6
python-dotenv>=1
groq>=0.18
websockets>=14
```

---

## 11. GLOSARIO

| Término | Definición |
|---|---|
| LLM | Large Language Model — Modelo de lenguaje grande |
| STT | Speech-to-Text — Conversión de voz a texto |
| TTS | Text-to-Speech — Conversión de texto a voz |
| VAD | Voice Activity Detection — Detección de actividad vocal |
| RPM | Requests Per Minute — Peticiones por minuto |
| RPD | Requests Per Day — Peticiones por día |
| TPM | Tokens Per Minute — Tokens por minuto |
