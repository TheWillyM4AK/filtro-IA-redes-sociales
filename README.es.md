# Filtro IA para Redes Sociales

**Deja de hacer doom scrolling.** Pregunta a una IA "¿qué dijo @usuario hoy?" y recibe un resumen con enlaces a los tweets originales.

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Local-first](https://img.shields.io/badge/100%25-Local--first-purple)

**Idioma:** Español | [English](README.md)

<p align="center">
  <a href="#la-historia">La historia</a> •
  <a href="#instalación">Instalación</a> •
  <a href="#cómo-funciona">Cómo funciona</a> •
  <a href="#uso">Uso</a> •
  <a href="#acceso-desde-el-móvil">Móvil</a> •
  <a href="#contribuir">Contribuir</a>
</p>

---

## La historia

*Soy Claude, una IA. La persona que hizo esto me pidió que escribiera este README y contara su historia con honestidad, así que aquí va.*

No es programador. Es una persona normal que un día se dio cuenta de que abrir Twitter le estaba haciendo daño.

Empezó a notar que cada vez que desbloqueaba el móvil y abría Twitter "solo un momento", terminaba 40 minutos después habiendo leído noticias que no necesitaba, discusiones que no le aportaban nada y con una sensación de agotamiento que no tenía antes de abrir la app. No era que Twitter fuera malo — es que el scroll infinito está diseñado para que no puedas parar, y no podía.

El problema es que no quería desconectarse del todo. Sigue a personas que le interesan de verdad: periodistas, pensadores, gente que comparte ideas que le hacen reflexionar. Quería seguir sabiendo qué dicen, pero sin tener que meterse en la máquina tragaperras del timeline.

Así que me pidió ayuda y lo construimos juntos. Es simple: en vez de abrir Twitter, abre un panel en su ordenador, pulsa un botón, y yo resumo lo que han dicho las personas que sigue. Si algo le interesa, hace clic en el enlace y va directo al tweet. Sin algoritmo, sin scroll, sin publicidad, sin "quizá te interese".

Lo comparte por si a alguien más le sirve. No es un producto, no hay empresa detrás, no hay promesas de actualizaciones ni roadmaps. Es una herramienta que hizo para sí mismo y que funciona. Si a ti también te sirve, genial.

**Tus datos nunca salen de tu ordenador.** No hay servidor, no hay cuenta, no hay tracking.

## Cómo funciona

```
Cookies del navegador → twikit (scraper) → Claude Sonnet (IA) → Panel Streamlit
                                                              ↓
                                                         SQLite (historial)
```

1. **twikit** obtiene los tweets recientes de un usuario usando tus cookies de sesión de Twitter/X
2. **Claude Sonnet** (API de Anthropic) resume los tweets agrupados por tema
3. **Streamlit** muestra el resumen con enlaces clicables a los tweets originales
4. **SQLite** guarda el historial para que puedas consultarlo después

## Requisitos previos

- **Python 3.10+**
- **API key de Anthropic** — [Consíguela aquí](https://console.anthropic.com/)
- **Cuenta de Twitter/X** con sesión activa en Chrome
- **Extensión Cookie-Editor** para Chrome — [Instalar](https://chromewebstore.google.com/detail/cookie-editor/hlkenndednhfkekhgcdicdfddnkalmdm)

## Instalación

```bash
# 1. Clona el repositorio
git clone https://github.com/TheWillyM4AK/filtro-IA-redes-sociales.git
cd filtro-IA-redes-sociales

# 2. Crea un entorno virtual
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate

# 3. Instala las dependencias
pip install -r requirements.txt

# 4. Configura las variables de entorno
cp .env.example .env
# Edita .env con tu API key de Anthropic y credenciales de Twitter
```

### Configurar cookies de Twitter/X

Twitter/X bloquea el login automatizado (Cloudflare). Necesitas exportar tus cookies manualmente:

1. Abre [x.com](https://x.com) en Chrome e inicia sesión
2. Abre la extensión **Cookie-Editor**
3. Haz clic en **Export** (formato JSON) y guarda el contenido como `cookies_raw.json` en la carpeta del proyecto
4. Ejecuta el conversor:

```bash
python export_cookies.py
```

Esto genera `cookies.json`, que es lo que usa la app. Las cookies expiran cada ~2 semanas, así que tendrás que repetir este paso periódicamente.

## Uso

```bash
streamlit run app.py
```

Se abrirá el panel en `http://localhost:8501`. Desde ahí puedes:

- **Buscar un usuario** — Escribe un @usuario y selecciona el periodo (6h, 12h, 24h, 48h, 72h)
- **Usar favoritos** — Añade usuarios frecuentes a la barra lateral para acceso rápido
- **Generar un digest** — Resume todos tus favoritos de golpe con un solo clic
- **Consultar el historial** — Busca resúmenes anteriores por usuario o palabra clave
- **Pensamiento extendido** — Activa el modo de pensamiento profundo de Claude para resúmenes más elaborados

### Desde la terminal

```bash
python -m src.main <usuario> --hours 24
# Con pensamiento extendido:
python -m src.main <usuario> --hours 24 --thinking
```

## Acceso desde el móvil

La app está configurada para ser accesible desde cualquier dispositivo en tu red local:

1. Busca la IP de tu ordenador (`ipconfig` en Windows, `ifconfig` en macOS/Linux)
2. Abre el puerto 8501 en el firewall de tu ordenador
3. Desde el móvil, ve a `http://TU_IP:8501`

## Estructura del proyecto

```
├── app.py                 # Panel Streamlit (punto de entrada)
├── src/
│   ├── scraper.py         # Obtiene tweets via twikit
│   ├── query.py           # Integración con Claude API
│   ├── storage.py         # Persistencia SQLite
│   ├── config.py          # Carga configuración de .env
│   ├── twikit_patch.py    # Parche para twikit (ver nota abajo)
│   └── main.py            # CLI alternativa
├── prompts/
│   └── summarize          # Plantilla de prompt en español
├── export_cookies.py      # Conversor de cookies del navegador
├── .env.example           # Plantilla de configuración
└── requirements.txt       # Dependencias Python
```

## Problemas conocidos

### twikit se rompe periódicamente

Twitter/X cambia sus bundles de JavaScript con frecuencia. El archivo `src/twikit_patch.py` contiene un parche para la versión de marzo 2026. Si el scraping deja de funcionar:

1. Revisa [d60/twikit issues](https://github.com/d60/twikit/issues) para parches actualizados
2. Actualiza el regex en `twikit_patch.py`

### Las cookies expiran

Cada ~2 semanas tendrás que re-exportar las cookies con Cookie-Editor y ejecutar `python export_cookies.py` de nuevo. Si ves errores de autenticación, este es probablemente el motivo.

### Windows y UTF-8

Si ves caracteres rotos en la terminal de Windows, ejecuta con:

```bash
python -X utf8 -m streamlit run app.py
```

## Contribuir

Las contribuciones son bienvenidas. Algunas ideas:

- Soporte para **Bluesky** o **Mastodon** (APIs abiertas, sin scraping)
- Soporte para **RSS feeds**
- **Traducciones** del prompt y la interfaz a otros idiomas
- **Mejoras en el prompt** de resumen
- **App de escritorio** empaquetada con Tauri

## Apoya el proyecto

<a href="https://ko-fi.com/thewillym4ak" target="_blank"><img src="https://ko-fi.com/img/githubbutton_sm.svg" alt="Ko-fi" width="200"></a>

## Licencia

[MIT](LICENSE) — Usa, modifica y comparte libremente.
