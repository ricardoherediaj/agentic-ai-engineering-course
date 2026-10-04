ifeq (,$(wildcard .env))
$(error .env file is missing. Please create one based on .env.example. Run: "cp .env.example .env" and fill in the missing values.)
endif

include .env
export

export UV_PROJECT_ENVIRONMENT=.venv
export PYTHONPATH = ./src/

.PHONY: tests

# --- Default Values ---

QA_FOLDERS := src/ tests/ scripts/
DIR_PATH ?= inputs/tests/00_debug
HUMAN_FEEDBACK ?=
TRANSPORT_ARG := $(if $(TRANSPORT),--transport $(TRANSPORT),)

# --- Utilities ---DIR_PATH

help: # Display this help message with a list of available commands.
	@grep -E '^[a-zA-Z0-9 -]+:.*#'  Makefile | sort | while read -r l; do printf "\033[1;32m$$(echo $$l | cut -f 1 -d':')\033[00m:$$(echo $$l | cut -f 2- -d'#')\n"; done

build: # Build the project.
	uv sync

# --- Agents ---

brown-generate-article: # Run the Brown MCP client to generate an article.
	uv run python scripts/brown_mcp_cli.py generate-article --dir-path $(DIR_PATH)

brown-edit-article: # Run the Brown MCP client to edit an article.
	uv run python scripts/brown_mcp_cli.py edit-article --dir-path $(DIR_PATH) --human-feedback $(HUMAN_FEEDBACK)

brown-edit-selected-text: # Run the Brown MCP client to a selected text section of an article.
	uv run python scripts/brown_mcp_cli.py edit-text --dir-path $(DIR_PATH) --human-feedback $(HUMAN_FEEDBACK) --first-line $(FIRST_LINE) --last-line $(LAST_LINE)


# --- Evals ---

brown-create-eval-dataset: # Create the evaluation dataset for Brown.
	uv run python -m scripts.brown_create_eval_dataset \
		--input-dir inputs/evals/dataset \
		--name brown-course-lessons \
		--description "Evaluation dataset on course lessons format."

brown-run-eval-flash: # Run the evaluation for Brown generating the articles with Gemini 3.7 Flash (low/medium thinking).
	CONFIG_FILE=./configs/course-gemini-flash.yaml uv run python -m scripts.brown_run_eval \
		--dataset-name brown-course-lessons \
		--metrics follows_gt \
		--metrics user_intent \
		--split test \
		--cache-dir outputs/evals-flash \
		--workers 1 \
		--read-from-cache

brown-run-eval-pro: # Run the evaluation for Brown generating the articles with Gemini 3.7 Flash on high thinking (formerly Gemini Pro).
	CONFIG_FILE=./configs/course-gemini-pro.yaml uv run python -m scripts.brown_run_eval \
		--dataset-name brown-course-lessons \
		--metrics follows_gt \
		--metrics user_intent \
		--split val \
		--cache-dir outputs/evals-pro \
		--workers 1 \
		--read-from-cache

# --- S1 protocol (Underdoc voice experiment, OpenCode Go fallback) ---

S1_JUDGE ?= opencode_go:gpt-6-luna
S1_REPEATS ?= 3
S1_RUN = uv run python -m scripts.underdoc_run_eval --judge-model $(S1_JUDGE)

s1-baseline: # S1: old (course) voice on the test split.
	$(S1_RUN) --config configs/course-fallback.yaml --split test --experiment-name s1-baseline

s1-new: # S1: new (Underdoc) voice on the test split.
	$(S1_RUN) --config configs/underdoc-fallback.yaml --split test --experiment-name s1-new

s1-noise-baseline: # S1: baseline repeats on the noise subset.
	$(S1_RUN) --config configs/course-fallback.yaml --split test --noise-subset --repeats $(S1_REPEATS) --experiment-name s1-noise-baseline

s1-noise-new: # S1: new-voice repeats on the noise subset.
	$(S1_RUN) --config configs/underdoc-fallback.yaml --split test --noise-subset --repeats $(S1_REPEATS) --experiment-name s1-noise-new

s1-summary: # S1: baseline vs new vs noise table from outputs/s1/*/scores.json.
	uv run python -m scripts.s1_summary \
		--baseline outputs/s1/s1-baseline-r1 --new outputs/s1/s1-new-r1 \
		$(foreach d,$(wildcard outputs/s1/s1-noise-baseline-r*),--noise-baseline $(d)) \
		$(foreach d,$(wildcard outputs/s1/s1-noise-new-r*),--noise-new $(d))

# --- Tests & QA ---

tests: # Run tests.
	CONFIG_FILE=configs/debug.yaml uv run pytest

pre-commit: # Run pre-commit hooks.
	uv run pre-commit run --all-files

format-fix: # Auto-format Python code using ruff formatter.
	uv run ruff format $(QA_FOLDERS)

lint-fix: # Auto-fix linting issues using ruff linter.
	uv run ruff check --fix $(QA_FOLDERS)

format-check: # Check code formatting without making changes using ruff formatter.
	uv run ruff format --check $(QA_FOLDERS) 

lint-check: # Check code for linting issues without fixing them using ruff linter.
	uv run ruff check $(QA_FOLDERS)
