# Cómo funciona cada pieza (explicación de ingeniería, breve)

Para retomar sin repetir el curso. Nombre primero, código entre paréntesis.

## 1. Las cinco piezas

| Pieza | Qué es técnicamente | Dónde vive | Cómo se ejecuta |
|---|---|---|---|
| **Tu voz (harness)** | Script Python **sin dependencias y sin LLM**: gates deterministas (`check.py`, G-01..G-08) + reglas en markdown + tu corpus de 26 posts | `~/Documents/TheUnderdoc/harness` | `python3 checks/check.py <draft.md>` para revisar un borrador; `python3 -m unittest discover -s tests` para sus tests |
| **Brown (escritura)** | Paquete Python con **LangGraph**: nodos (escribir, revisar, editar, generar media) y flujos (`workflows/`). Prompts en pydantic + structured outputs | `lessons/writing_workflow/src/brown` | Por código (`build_generate_article_workflow`), por los scripts de eval, o como **servidor MCP** (`python -m brown.mcp.server`) |
| **Nova (investigación)** | **Servidor FastMCP** en Python: expone el pipeline de research como tools | `lessons/research_agent_part_2/mcp_server` (la versión desplegable es `part_3`) | `uv run -m src.server` (stdio o HTTP); lo monta un cliente MCP |
| **Tu MCP (Underdoc)** | Servidor FastMCP **propio** (capstone): voz + aprobación humana + borrador en Substack | **no existe todavía** (fase "Tu MCP" / S3) | — |
| **Evals (medición)** | Runner que genera y juzga artículos, con caché en disco, y registra todo en **Opik** | `lessons/writing_workflow/scripts/underdoc_run_eval.py` + `src/brown/evals/` | `uv run python -m scripts.underdoc_run_eval --config ... --experiment-name ...` |

## 2. Flujo de datos (con los archivos de por medio)

1. **Entradas de un post**: `article_guideline.md` (tu brief: ángulo, audiencia, 3-6 intenciones de sección, fuentes) + `research.md` (dossier de Nova) + los **perfiles** (tu voz).
2. Brown corre el flujo: `write_article` → `[generate_reviews → edit_based_on_reviews] × num_reviews` (3 por defecto) → renderiza markdown en la carpeta del post: `article_001.md`, `article_002.md`… y el final en `article.md`.
3. El **gate de slop** entra dentro de `generate_reviews`: lee el borrador, corre tu `check.py` y agrega cada hit como `Review(profile="mechanics", location=<sección>)`. El loop solo corta temprano si no hay ninguna review (ni del LLM ni del gate).
4. La **evaluación** toma ese `article.md`, lo juzga por métrica (criterios binarios por sección H2) y guarda `scores.json` + un experimento en Opik.
5. Vos editás y publicás a mano; las métricas online (secciones que sobreviven, tiempo de edición) cierran el círculo.

## 3. Los MCP, en concreto (esto es lo que se reutiliza en el capstone)

- **Nova** (`part_2/mcp_server`, routers `tools.py` / `prompts.py` / `resources.py`): 13 tools (instrucciones de research, generar queries, buscar en web y con Perplexity, scrapear, seleccionar fuentes, crear el `research.md`, procesar URLs de GitHub y archivos locales, transcribir YouTube), 1 prompt y 2 resources (`system://status`, `system://memory`).
- **Brown** (`src/brown/mcp/server.py`): 3 tools (`generate_article`, `edit_article`, `edit_selected_text`), 3 prompts (los mismos, con feedback humano) y resources (`resource://config/app`, `resource://profiles/character` y el resto de perfiles).
- **El cliente MCP** (Claude Code, Cursor, etc.) los monta desde `.mcp.json`, que hoy apunta a Nova, Brown y fija `ENV_FILE_PATH`.

Diferencia clave entre los dos: **Nova produce investigación; Brown produce texto**. Ninguno escribe en Substack. Ese es el trabajo de **tu MCP**: 7 tools portados de `substack-mcp` (crear borrador, cuerpo estructurado, subir imagen, editar, leer, listar, borrar) + el prompt de aprobación humana. `publish_draft` queda afuera por regla propia: publicás vos.

## 4. Contratos que hay que respetar (si esto se rompe, se rompe todo)

- **Config de Brown**: un YAML → `AppConfig` (pydantic). Define las URIs de contexto (guideline, research, perfiles, ejemplos), `num_reviews`, `max_reviews_per_iteration`, los **modelos por nodo** (`nodes`) y `slop_gate`. Cambiar de proveedor = cambiar el YAML, no el código.
- **Perfiles = copia, no dependencia**: `scripts/sync_underdoc_profiles.py` copia tus referencias del harness a `inputs/profiles/underdoc/`. Tocás el harness → corrés el sync → Brown ve lo nuevo.
- **Dataset de evals**: 26 muestras con `article_guideline.md`, `article_ground_truth.md` y (solo builds/explainers) `research.md`, más splits en `metadata.json`. Las guidelines son breves a propósito (control de leakage).
- **Juez**: un LLM con salida estructurada que puntúa criterios binarios (0/1) por sección H2 y agrega por criterio. La versión de la métrica es un hash de su rúbrica; si cambia, se re-juzga.
- **Cachés versionadas**: cada artículo y cada juicio guardan una etiqueta ("clave") con todo lo que puede cambiarlos (config, código, perfiles, ejemplos, guideline/research, reglas de voz). Clave distinta = se recalcula; etiqueta incompleta = el sistema te miente.

## 5. Acoples actuales (los dos son a propósito)

1. **Sync de perfiles** (copia en disco): mantiene tu harness como fuente canónica sin obligar a Brown a depender de él en runtime.
2. **Gate por ruta** (`UNDERDOC_HARNESS_PATH` → `checks/check.py`): única dependencia de runtime con el harness. En el monorepo (S0) se reemplaza por el paquete `voice/` y la ruta desaparece.

## 6. Qué falta construir

- **Nova lee builds (S2)**: una tool nueva (`process_local_build_tool`) que lea README, `docs/build-log/`, `git log` y el árbol del repo, citando cada afirmación.
- **Tu MCP (S3)**: el servidor del capstone: voz como resources, prompt HITL (aprobar ángulo y estructura como diff) y las 7 tools de Substack.
- **Deploy (S4)**: Docker + Cloud Run + auth, estilo curso.
