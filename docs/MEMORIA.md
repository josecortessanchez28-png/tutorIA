# MEMORIA DEL PROYECTO: TutorIA

> **Versión:** 0.1.0 — Fase 0: Foundation  
> **Fecha:** 29 Julio 2026  
> **Autor:** Jose (josedell)  
> **Repositorio:** *pendiente de crear en GitHub*

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

## 2. DECISIÓN DE ARQUITECTURA

Se descartó completamente el enfoque local (Ollama + modelos cuantizados) por tres razones:

1. **Modelos locales inferiores**: Qwen 3B no puede competir con Llama 3.3 70B o GPT-OSS 120B en razonamiento y tool calling.
2. **Mantenimiento**: Actualizar modelos, gestionar descargas, dependencias del sistema, espacio en disco.
3. **Portabilidad**: El usuario debe poder acceder desde cualquier máquina sin depender de hardware concreto.

La arquitectura elegida es **cloud-first**:

- **LLM**: Groq API (principal) + OpenRouter (fallback) — ambos gratuitos, con tool calling nativo, modelos actualizados semanalmente.
- **STT**: Groq Whisper large-v3-turbo vía API — 2000 requests/día gratis, 20 RPM.
- **TTS**: edge-tts — llama a la API de Microsoft Edge, voces naturales, sin coste.
- **Screen Capture**: JavaScript Screen Capture API desde el navegador del usuario.
- **Servidor**: Python + FastAPI desplegado en Koyeb (1GB RAM, 0.5 CPU, sin sleep) o Render (512MB, 0.1 CPU).

## 3. STACK TECNOLÓGICO DETALLADO

### 3.1 Backend (Servidor Cloud)

| Componente | Tecnología | Versión | Justificación |
|---|---|---|---|
| Lenguaje | Python | 3.12+ | Ecosistema maduro para IA, librerías nativas |
| Framework web | FastAPI | Última | Rendimiento, WebSockets nativos, tipado |
| Servidor ASGI | Uvicorn | Última | Estándar para FastAPI, bajo overhead |
| Cliente LLM | groq (SDK oficial) | Última | OpenAI-compatible, tool calling nativo |
| Cliente HTTP | httpx | Última | Para OpenRouter y web scraping async |
| Web Search | duckduckgo_search | Última | Sin API key, sin límites de rate |
| TTS | edge-tts | Última | API Microsoft, voces naturales, gratis |
| Vector DB | chromadb | Última | Embeddings locales, persistente, gratis |
| Embeddings | sentence-transformers | Última | Modelos ligeros (all-MiniLM-L6-v2) |
| Procesamiento img | Pillow + numpy | Última | Análisis básico de capturas |

### 3.2 Frontend (Navegador)

| Componente | Tecnología |
|---|---|
| HTML/CSS/JS | Vanilla (sin framework) o SPA ligera |
| Screen Capture | Screen Capture API (getDisplayMedia) |
| Micrófono | getUserMedia (WebRTC) |
| WebSocket | nativo JS (WebSocket API) |
| Streaming audio | Web Audio API + MediaSource |

### 3.3 APIs Externas

| API | Uso | Modelos disponibles | Límites free tier |
|---|---|---|---|
| Groq | LLM principal + STT | Llama 3.3 70B, Llama 3.1 8B, Qwen, GPT-OSS, Whisper | 30 RPM, 6K TPM, 1K RPD |
| OpenRouter | LLM fallback | Nemotron 3 Ultra (1M ctx), Llama 70B, Qwen, GPT-OSS | 20 RPM, 50 RPD (sin pago) |
| Microsoft Edge | TTS (edge-tts) | ~322 voces naturales | Sin límite conocido |

## 4. INVESTIGACIÓN DE MERCADO (Julio 2026)

### 4.1 Render Free Tier
- RAM: 512 MB | CPU: 0.1 | Ancho banda: 100 GB/mes
- Sleep: 15 min inactividad, cold start 30-60s
- Horas: 750h/mes (suficiente para 1 app 24/7)
- PostgreSQL gratis: 256MB RAM, 1GB (expira 30 días)

### 4.2 Koyeb Free Tier
- RAM: 1 GB | CPU: 0.5 | Sin sleep (siempre activo)
- Mejor que Render para este proyecto (2x RAM, 5x CPU, no duerme)

### 4.3 Groq API
- Modelos gratuitos: Llama 3.3 70B, Llama 3.1 8B, GPT-OSS 20B/120B, Qwen 32B, Whisper
- Rate limits: 30 RPM, ~6K TPM, 1K RPD
- Whisper: 20 RPM, 2K audio requests/día
- Tool calling: Nativo, compatible con OpenAI format
- Velocidad: 280-1000 tokens/segundo (LPU hardware)

### 4.4 OpenRouter
- 25+ modelos gratuitos rotativos
- Rate limits: 20 RPM, 50 RPD (sin compra), 1K RPD (con 10$ comprados)
- Auto-router `openrouter/free`: elige el mejor modelo disponible
- Tool calling: Soporta function calling

## 5. ARQUITECTURA DEL SISTEMA

```
┌─────────────────────────────────────────────────┐
│              NAVEGADOR WEB (cliente)              │
│                                                   │
│  [Mic] → getUserMedia → Audio → WebSocket         │
│  [Screen] → getDisplayMedia → Frames → WebSocket │
│  [Speaker] ← Audio TTS ← WebSocket ←             │
│                                                   │
└─────────────────────┬───────────────────────────┘
                      │ WebSocket + HTTP
                      ▼
┌─────────────────────────────────────────────────┐
│              SERVIDOR (Koyeb/Render)              │
│                                                   │
│  ┌──────────┐  ┌──────────┐  ┌────────────────┐ │
│  │ FastAPI  │  │ WebSocket│  │  Agent Orch.   │ │
│  │ REST     │  │ Manager  │  │  (bucle ppal)  │ │
│  └──────────┘  └──────────┘  └───────┬────────┘ │
│                                       │          │
│  ┌────────────────────────────────────┘          │
│  │                                                │
│  ▼                                                │
│  ┌────────────────────────────────────────────┐  │
│  │            LLM ROUTER                        │  │
│  │  ┌──────────────┐  ┌──────────────────┐    │  │
│  │  │ Groq API     │  │ OpenRouter API   │    │  │
│  │  │ (Principal)  │  │ (Fallback)       │    │  │
│  │  └──────────────┘  └──────────────────┘    │  │
│  └────────────────────────────────────────────┘  │
│                                                   │
│  ┌──────────┐  ┌──────────┐  ┌────────────────┐ │
│  │ STT      │  │ TTS      │  │ Tools          │ │
│  │ (Whisper)│  │(edge-tts)│  │ Search, OCR,   │ │
│  └──────────┘  └──────────┘  │ YouTube, etc.  │ │
│                               └────────────────┘ │
│  ┌──────────┐  ┌──────────────────────────────┐  │
│  │ ChromaDB │  │ Session / Context Manager    │  │
│  │  (mem)   │  │ (historial + ventana tokens) │  │
│  └──────────┘  └──────────────────────────────┘  │
└─────────────────────────────────────────────────┘
```

## 6. FLUJO DE USO

### Paso a paso:

1. Usuario abre `tutoria.app` en su navegador
2. Hace clic en "Iniciar sesión" → concede permisos de micrófono y pantalla
3. El agente saluda y confirma que ve la pantalla y escucha
4. Usuario dice: *"Vale, tengo abierto Burp Suite, quiero interceptar una petición HTTPS"*
5. El audio viaja por WebSocket al servidor → Groq Whisper lo transcribe a texto
6. El servidor captura un frame de la pantalla → lo envía al LLM para análisis visual
7. El agente (orquestador) construye el prompt con: contexto visual + consulta del usuario + historial
8. LLM (Groq) procesa y decide si necesita herramientas:
   - ¿Buscar en web? → Ejecuta duckduckgo_search
   - ¿Ver documentación? → Scrapea docs oficiales
   - ¿Buscar tutorial? → YouTube transcript
9. LLM genera respuesta → edge-tts la convierte en audio
10. Audio llega al navegador por WebSocket → se reproduce en cascos
11. El agente espera nueva intervención del usuario (o pregunta si el paso se ha completado)

### Cadena de fallback:

```
Groq LLM → ¿límite? → OpenRouter free → ¿límite? → "Modo texto, disculpa las molestias"
Groq Whisper → ¿límite? → "No puedo escuchar, escribe tu consulta"
edge-tts → ¿fallo? → pyttsx3 offline (local, última opción)
```

## 7. ESTRUCTURA DEL PROYECTO

```
D:\TutorIA\
├── agent/                  # Lógica del agente orquestador
│   ├── __init__.py
│   ├── orchestrator.py     # Bucle principal del agente
│   ├── session.py          # Gestión de contexto y sesiones
│   ├── tool_registry.py    # Registro y ejecución de herramientas
│   └── prompts.py          # System prompts y templates
├── server/                 # FastAPI server
│   ├── __init__.py
│   ├── main.py             # Punto de entrada FastAPI
│   ├── routes.py           # Endpoints REST
│   └── websocket.py        # Gestión WebSocket
├── tools/                  # Herramientas del agente
│   ├── __init__.py
│   ├── base.py             # Interfaz BaseTool
│   ├── web_search.py       # Búsqueda DuckDuckGo
│   ├── web_scrape.py       # Extracción de contenido
│   ├── youtube.py          # Transcripts YouTube
│   └── screen_analysis.py  # Análisis de capturas
├── voice/                  # Pipeline de voz
│   ├── __init__.py
│   ├── stt.py              # Cliente Groq Whisper
│   └── tts.py              # Cliente edge-tts
├── memory/                 # Base de conocimiento
│   ├── __init__.py
│   ├── vector_store.py     # ChromaDB wrapper
│   └── embeddings.py       # Embeddings
├── frontend/               # Cliente web
│   ├── index.html
│   ├── style.css
│   └── app.js              # Screen capture, mic, WebSocket
├── config/                 # Configuración
│   ├── __init__.py
│   ├── settings.py
│   └── default.yaml
├── docker/                 # Despliegue
│   ├── Dockerfile
│   └── docker-compose.yml
├── docs/                   # Documentación
│   ├── MEMORIA.md           # Este archivo
│   └── ARQUITECTURA.md
├── scripts/                # Scripts de utilidad
│   ├── install.sh
│   ├── run.sh
│   └── run.bat
├── tutoria.cm              # Contexto del proyecto
├── README.md
├── requirements.txt
├── setup.py
├── LICENSE
└── .gitignore
```

## 8. PLAN DE FASES DETALLADO

### FASE 0: Foundation (1-2 días)
- Crear estructura de directorios
- Configuración YAML con variables de entorno (API keys, modelos)
- requirements.txt con dependencias pinneadas
- scripts de instalación y arranque
- .gitignore, LICENSE
- Dockerfile + docker-compose.yml base

### FASE 1: Core Agent (3-4 días)
- FastAPI server con rutas básicas
- Cliente Groq API con tool calling
- Cliente OpenRouter como fallback
- System prompts para el rol de tutor
- Gestión de sesiones y contexto

### FASE 2: Voice Pipeline (2-3 días)
- Integración Groq Whisper (STT) vía API
- Integración edge-tts (TTS) vía API
- WebSocket para streaming de audio
- Cola de mensajes y buffer de audio

### FASE 3: Screen & Vision (2-3 días)
- Frontend con Screen Capture API
- Envío de frames por WebSocket al servidor
- Análisis de pantalla con LLM (Groq vision)
- Detección de cambios relevantes en pantalla

### FASE 4: Tools & Skills (3-4 días)
- Web search con duckduckgo_search
- Web scraping con httpx + trafilatura
- YouTube transcripts
- Sistema de herramientas tipo MCP
- Rate limiting y timeouts

### FASE 5: Knowledge Base (2-3 días)
- ChromaDB para persistencia
- Embeddings con sentence-transformers
- Caché de búsquedas web
- Memoria de sesiones anteriores

### FASE 6: Frontend Completo (2-3 días)
- Interfaz web con chat visual
- Botón de inicio de sesión (screen + mic)
- Indicadores de estado (escuchando, procesando, hablando)
- Modo oscuro/claro

### FASE 7: Docker & Deploy (1-2 días)
- Dockerfile optimizado (multi-stage)
- Docker Compose con servicios
- Deploy a Koyeb o Render
- GitHub Actions para CI/CD

### FASE 8: Documentation & Release (1-2 días)
- README completo (ES + EN)
- tutoria.cm finalizado
- MEMORIA.md completa
- Ejemplos de uso
- GitHub release v1.0.0

## 9. DECISIONES TÉCNICAS

### 9.1 ¿Por qué no Ollama local?
- Modelos locales (Qwen 3B) son inferiores a Llama 70B o GPT-OSS 120B vía API
- Mantenimiento continuo de descargas y actualizaciones
- Dependencia de hardware específico
- El usuario no puede acceder desde cualquier máquina

### 9.2 ¿Por qué Groq como principal?
- Tool calling nativo (función crítica para el orquestador)
- Velocidad LPU (hasta 1000 tokens/s)
- Whisper incluido (un solo API key para LLM + STT)
- OpenAI-compatible (fácil migración si es necesario)
- Gratuito, sin tarjeta de crédito

### 9.3 ¿Por qué OpenRouter como fallback?
- 25+ modelos gratuitos rotativos
- Auto-router que selecciona el mejor disponible
- Diferente pool de rate limits (no compite con Groq)

### 9.4 ¿Por qué edge-tts para voz?
- Gratuito, sin límites de uso conocidos
- ~322 voces naturales (más que cualquier alternativa gratuita)
- No necesita GPU ni hardware especial
- Streaming de audio en tiempo real

### 9.5 ¿Por qué navegador como cliente?
- Sin instalación: funciona en cualquier máquina con navegador
- APIs nativas para screen capture y mic (getDisplayMedia, getUserMedia)
- WebSocket para comunicación bidireccional en tiempo real
- Portabilidad total: torre, portátil, tablet

## 10. ANEXOS

### 10.1 Variables de Entorno Necesarias

```bash
GROQ_API_KEY=          # Obligatoria
OPENROUTER_API_KEY=    # Obligatoria
TUTORIA_MODEL=         # Opcional (default: llama-3.3-70b-versatile)
TUTORIA_FALLBACK=      # Opcional (default: openrouter/free)
TUTORIA_TTS_VOICE=     # Opcional (default: es-ES-ElviraNeural)
```

### 10.2 Dependencias Python

```
fastapi>=0.115
uvicorn>=0.34
websockets>=14
groq>=0.18
httpx>=0.28
duckduckgo_search>=7
edge-tts>=7
chromadb>=1
sentence-transformers>=3
numpy>=2
pillow>=11
pyyaml>=6
pydantic>=2
```

### 10.3 Glosario

| Término | Definición |
|---|---|
| LLM | Large Language Model — Modelo de lenguaje grande |
| STT | Speech-to-Text — Conversión de voz a texto |
| TTS | Text-to-Speech — Conversión de texto a voz |
| Tool Calling | Capacidad del LLM de invocar funciones externas |
| MCP | Model Context Protocol — Protocolo para conectar LLM con herramientas |
| VAD | Voice Activity Detection — Detección de actividad vocal |
| Orb | Orquestador — Bucle principal del agente |
| RPM | Requests Per Minute — Peticiones por minuto |
| RPD | Requests Per Day — Peticiones por día |
| TPM | Tokens Per Minute — Tokens por minuto |
| LPU | Language Processing Unit — Hardware de inferencia de Groq |
