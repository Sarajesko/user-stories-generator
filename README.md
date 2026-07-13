# User Stories Generator (FastAPI) — Entregable 3

Aplicación web multi-archivo que genera **historias de usuario** y **tareas** a partir de un prompt, usando **Azure OpenAI + LangChain** con salidas estructuradas Pydantic. Los resultados se persisten en **MySQL** y se muestran con plantillas **Jinja2** y Bootstrap.

## Características

- Generación de historias de usuario desde un prompt libre (`UserStorySchema`).
- Generación de tareas asociadas a cada historia (`TasksSchema`).
- Dos llamadas encadenadas al LLM: primero la historia, luego las tareas usando el contexto de la historia.
- Modelos SQLAlchemy `UserStory` y `Task` con relación 1-N.
- Interfaz web con formulario, listado de historias y tabla de tareas.
- Tests automáticos con `pytest` (31 tests).

## Requisitos

- Python 3.11+ (probado con 3.14).
- MySQL local (XAMPP u otro) o MySQL en Azure.
- Recurso de **Azure OpenAI** con deployment activo.

## Estructura del proyecto

```
m4_proyectoEntregable_Pablo_garcia/
├── main.py                 # Arranque FastAPI
├── config.py               # Variables de entorno
├── database.py             # SQLAlchemy engine y sesión
├── templating.py           # Configuración Jinja2
├── models/
│   ├── user_story.py
│   └── task.py
├── schemas/
│   ├── user_story.py
│   └── task.py
├── services/
│   └── llm_service.py      # generar_historia / generar_tareas
├── routers/
│   └── user_stories.py
├── templates/
│   ├── base.html
│   ├── user-stories.html
│   └── tasks.html
├── tests/
├── requirements.txt
├── .env.example
└── pytest.ini
```

## Instalación

Desde la carpeta del proyecto (`m4_proyectoEntregable_Pablo_garcia`):

```bash
python -m venv venv
```

En Windows:

```bash
venv\Scripts\activate
```

Instalar dependencias:

```bash
pip install -r requirements.txt
```

## Configuración de MySQL

1. Arranca MySQL (en XAMPP: servicio **MySQL** en ejecución).
2. Crea la base de datos en phpMyAdmin o consola:

```sql
CREATE DATABASE user_stories_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

3. Copia `.env.example` a `.env` y ajusta la conexión:

```env
DATABASE_URL=mysql+pymysql://root@127.0.0.1:3306/user_stories_db
```

Si tu usuario `root` tiene contraseña:

```env
DATABASE_URL=mysql+pymysql://root:TU_PASSWORD@127.0.0.1:3306/user_stories_db
```

Las tablas `user_stories` y `tasks` se crean automáticamente al arrancar la aplicación.

## Configuración de Azure OpenAI

En el mismo `.env`, completa las credenciales de Azure:

```env
AZURE_OPENAI_ENDPOINT=https://TU-RECURSO.openai.azure.com/
AZURE_OPENAI_API_KEY=tu-api-key
AZURE_OPENAI_API_VERSION=2025-04-01-preview
AZURE_OPENAI_DEPLOYMENT=nombre-del-deployment
TEMPERATURE=0.1
MAX_TOKENS=2048
TOP_P=1.0
```

**Importante:**

- No incluyas `.env` en la entrega (contiene credenciales).
- `MAX_TOKENS` debe ser **al menos 1024** (recomendado **2048**) para generar varias tareas en JSON sin que se corte la respuesta.

## Ejecución

```bash
uvicorn main:app --reload --port 8003
```

Abre en el navegador:

- **Interfaz principal:** http://127.0.0.1:8003/user-stories
- **Health check:** http://127.0.0.1:8003/health
- **Swagger (opcional):** http://127.0.0.1:8003/docs

> Si el puerto 8000 está ocupado por otro proyecto, usa `--port 8003` u otro libre.

## Uso de la aplicación

1. En `/user-stories`, escribe un prompt en el textarea. Ejemplo:

   ```
   Sistema de reservas online para una peluquería. Los clientes reservan cita desde el móvil
   y la recepcionista ve el calendario del día y confirma las reservas.
   ```

2. Pulsa **Generar historia con IA**. La historia se guarda en MySQL y aparece en el listado.

3. En la card de la historia, pulsa **Generar tareas**. La IA descompone la historia en tareas y redirige a la vista de tareas.

4. Pulsa **Ver tareas** para consultar las tareas ya generadas.

## Endpoints

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/user-stories` | Formulario + listado de historias |
| POST | `/user-stories` | Genera historia con IA y persiste |
| POST | `/user-stories/{id}/generate-tasks` | Genera tareas con IA y persiste |
| GET | `/user-stories/{id}/tasks` | Muestra historia y sus tareas |
| GET | `/health` | Comprueba conexión a MySQL |

## Modelos de datos

### UserStory

- `id`, `project`, `role`, `goal`, `reason`, `description`
- `priority` (`baja`, `media`, `alta`, `bloqueante`)
- `story_points` (1–8), `effort_hours`, `created_at`

### Task

- `id`, `title`, `description`, `priority`, `effort_hours`
- `status` (`pendiente`, `en progreso`, `en revisión`, `completada`)
- `assigned_to`, `user_story_id`, `created_at`

## Tests

Ejecutar todos los tests:

```bash
python -m pytest -v
```

Por paso del entregable:

```bash
python -m pytest -m entregable3_paso2 -v   # Modelos y BD
python -m pytest -m entregable3_paso3 -v   # Schemas Pydantic
python -m pytest -m entregable3_paso4 -v   # Servicio IA (mocks)
python -m pytest -m entregable3_paso5 -v   # Endpoints y vistas
```

Los tests de IA usan mocks y **no consumen Azure** en pytest. Los tests de modelos usan SQLite en memoria.

## Entrega

Nombre del ZIP: `m4_proyectoEntregable_Pablo_garcia.zip`

Incluir:

- Todo el código fuente (`.py`, `.html`, `requirements.txt`, `.env.example`, `pytest.ini`, `tests/`)

Excluir:

- `venv/` o `.venv/`
- `__pycache__/`
- `.env` (credenciales)
- `.pytest_cache/`

## Stack técnico

- **FastAPI** + **Jinja2** + **Bootstrap 5**
- **SQLAlchemy** + **MySQL** (`pymysql`)
- **Pydantic v2** (schemas y salida estructurada)
- **LangChain** + **langchain-openai** (`AzureChatOpenAI`, `with_structured_output`)

## Autor

Pablo García — Programa Avanzado en Inteligencia Artificial para Programar (Entregable 3).
