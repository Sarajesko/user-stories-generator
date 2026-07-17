# User Stories Generator — Entregable 3

Aplicación web con **FastAPI**, **Jinja2** y **Bootstrap** que genera **historias de usuario** y **tareas** a partir de un prompt, usando **Azure OpenAI + LangChain** con salidas estructuradas Pydantic. Todo se persiste en **MySQL**.

**Repositorio:** [github.com/Sarajesko/user-stories-generator](https://github.com/Sarajesko/user-stories-generator)

---

## Índice

1. [¿Para qué sirve?](#para-qué-sirve)
2. [Qué incluye](#qué-incluye)
3. [Arquitectura](#arquitectura)
4. [Estructura](#estructura)
5. [Requisitos](#requisitos)
6. [Arranque rápido](#arranque-rápido)
7. [Uso de la aplicación](#uso-de-la-aplicación)
8. [Modelos de datos](#modelos-de-datos)
9. [API / rutas](#api--rutas)
10. [Tests](#tests)
11. [Stack](#stack)
12. [Solución de problemas](#solución-de-problemas)
13. [Roadmap](#roadmap)
14. [Licencia](#licencia)

---

## ¿Para qué sirve?

Acelerar el diseño de product backlog:

- escribes un prompt libre (p. ej. “sistema de reservas para peluquería”);
- la IA genera una historia de usuario estructurada (rol, objetivo, razón, puntos…);
- desde esa historia genera un conjunto de tareas;
- todo queda guardado en MySQL y visible en la UI.

Dos llamadas encadenadas al LLM: primero la historia, luego las tareas con el contexto de la historia.

---

## Qué incluye

| Área | Estado |
|------|--------|
| Generación de historias (`UserStorySchema`) | Listo |
| Generación de tareas asociadas (`TasksSchema`) | Listo |
| UI Jinja2 + Bootstrap (formulario, listado, tareas) | Listo |
| Persistencia MySQL (SQLAlchemy, relación 1-N) | Listo |
| Health check de base de datos | Listo |
| Tests pytest por pasos (mocks de IA) | Listo |

---

## Arquitectura

```mermaid
flowchart LR
  browser[Navegador] --> ui[Jinja2 / Bootstrap]
  ui --> api[FastAPI]
  api --> llm[LangChain + Azure OpenAI]
  api --> db[(MySQL user_stories_db)]
```

---

## Estructura

```
user-stories-generator/
├── main.py                 Arranque FastAPI
├── config.py               Variables de entorno
├── database.py             Engine / sesión SQLAlchemy
├── templating.py           Jinja2
├── models/
│   ├── user_story.py
│   └── task.py
├── schemas/
│   ├── user_story.py       Salida estructurada LLM
│   └── task.py
├── services/
│   └── llm_service.py      generar_historia / generar_tareas
├── routers/
│   └── user_stories.py
├── templates/
│   ├── base.html
│   ├── user-stories.html
│   └── tasks.html
├── tests/
├── .env.example
├── pytest.ini
├── requirements.txt
├── LICENSE
└── README.md
```

---

## Requisitos

| Herramienta | Para qué |
|-------------|----------|
| **Python 3.11+** | Runtime |
| **MySQL** (XAMPP u otro) | Persistencia |
| **Azure OpenAI** | Generación de historias y tareas |

---

## Arranque rápido

```powershell
cd m4_proyectoEntregable_Pablo_garcia
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
```

Crea la base:

```sql
CREATE DATABASE user_stories_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

Edita `.env`:

```env
DATABASE_URL=mysql+pymysql://root@127.0.0.1:3306/user_stories_db
AZURE_OPENAI_ENDPOINT=https://TU-RECURSO.openai.azure.com/
AZURE_OPENAI_API_KEY=tu-api-key
AZURE_OPENAI_API_VERSION=2025-04-01-preview
AZURE_OPENAI_DEPLOYMENT=nombre-del-deployment
TEMPERATURE=0.1
MAX_TOKENS=2048
TOP_P=1.0
```

Si `root` tiene contraseña: `mysql+pymysql://root:TU_PASSWORD@127.0.0.1:3306/user_stories_db`.

Las tablas se crean al arrancar la app.

```powershell
uvicorn main:app --reload --port 8003
```

| Recurso | Valor |
|---------|--------|
| UI | [http://127.0.0.1:8003/user-stories](http://127.0.0.1:8003/user-stories) |
| Health | [http://127.0.0.1:8003/health](http://127.0.0.1:8003/health) |
| Swagger | [http://127.0.0.1:8003/docs](http://127.0.0.1:8003/docs) |

> Puerto **8003** por defecto para no chocar con otros proyectos en 8000.

`MAX_TOKENS` debe ser **≥ 1024** (recomendado **2048**) para no cortar el JSON de tareas.

---

## Uso de la aplicación

1. Abre `/user-stories` y escribe un prompt. Ejemplo:

   ```text
   Sistema de reservas online para una peluquería. Los clientes reservan cita desde el móvil
   y la recepcionista ve el calendario del día y confirma las reservas.
   ```

2. Pulsa **Generar historia con IA** → se guarda en MySQL y aparece en el listado.
3. En la card, pulsa **Generar tareas** → la IA descompone la historia y redirige a la vista de tareas.
4. Pulsa **Ver tareas** para consultar las ya generadas.

---

## Modelos de datos

### UserStory

| Campo | Notas |
|-------|--------|
| `project`, `role`, `goal`, `reason`, `description` | Texto estructurado |
| `priority` | `baja` · `media` · `alta` · `bloqueante` |
| `story_points` | 1–8 |
| `effort_hours` | > 0 |
| `created_at` | Timestamp |

### Task

| Campo | Notas |
|-------|--------|
| `title`, `description`, `assigned_to` | Texto |
| `priority` | Mismos valores que la historia |
| `status` | `pendiente` · `en progreso` · `en revisión` · `completada` |
| `effort_hours` | > 0 |
| `user_story_id` | FK → historia |

Relación **1-N** con cascade delete.

---

## API / rutas

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/` | Mensaje de salud JSON |
| GET | `/health` | Comprueba MySQL |
| GET | `/user-stories` | Formulario + listado (HTML) |
| POST | `/user-stories` | Genera historia (form `prompt`) → redirect |
| POST | `/user-stories/{id}/generate-tasks` | Genera tareas → redirect |
| GET | `/user-stories/{id}/tasks` | Vista historia + tareas |

Errores habituales: **400** (prompt vacío), **404** (historia inexistente), **502** (fallo LLM).

---

## Tests

```powershell
python -m pytest -v
python -m pytest -m entregable3_paso2 -v   # Modelos y BD
python -m pytest -m entregable3_paso3 -v   # Schemas Pydantic
python -m pytest -m entregable3_paso4 -v   # Servicio IA (mocks)
python -m pytest -m entregable3_paso5 -v   # Endpoints y vistas
```

Los tests de IA usan mocks (no consumen Azure). Los de modelos pueden usar SQLite en memoria.

---

## Stack

| Capa | Tecnología |
|------|------------|
| View | Jinja2 + Bootstrap 5 |
| API | FastAPI + python-multipart |
| Model | SQLAlchemy 2 + MySQL (pymysql) |
| IA | LangChain + langchain-openai (`AzureChatOpenAI`, `with_structured_output`) |
| Validación | Pydantic v2 |
| Tests | pytest + httpx |

---

## Solución de problemas

| Problema | Qué revisar |
|----------|-------------|
| `/health` falla | MySQL arrancado; `DATABASE_URL` correcta; BD creada |
| 502 al generar | Deployment Azure; `MAX_TOKENS` ≥ 2048 |
| JSON de tareas cortado | Subir `MAX_TOKENS` |
| Puerto ocupado | Otro `--port` o liberar 8003 |

---

## Roadmap

- Edición manual de historias/tareas desde la UI.
- Export CSV / JSON del backlog.
- Docker Compose (MySQL + API).

---

## Licencia

[MIT](LICENSE) — software libre: puedes usar, modificar y redistribuir con la atribución correspondiente.

---

## Autor

**Pablo García Márquez**
