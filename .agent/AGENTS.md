# Repository Guidelines

## Project Structure & Module Organization
- `Open-LLM-VTuber-1.2.1/` is the main application. Core Python lives in `Open-LLM-VTuber-1.2.1/src/open_llm_vtuber/`, web assets in `Open-LLM-VTuber-1.2.1/frontend/`, and configuration templates in `Open-LLM-VTuber-1.2.1/config_templates/`.
- `Hololive-Style-Bert-VITS2/` provides the Bert-VITS2 TTS server, models, and configs (see `Hololive-Style-Bert-VITS2/configs/` and `Hololive-Style-Bert-VITS2/model_assets/`).
- Root scripts such as `start_both.sh` and `stop_all.sh` orchestrate local dev. Patch helpers live next to them (for example `patch_gradio_client.py`).
- Generated/audio artifacts are placed under `cache/`.

## Build, Test, and Development Commands
- `./start_both.sh` starts Bert-VITS2 in the background and then launches Open-LLM-VTuber (uses `uv run python run_server.py`).
- `./stop_all.sh` stops all related servers (Bert-VITS2, Open-LLM-VTuber, uvicorn, and gradio tunnels).
- `uv run python Open-LLM-VTuber-1.2.1/run_server.py` runs only the Open-LLM-VTuber backend.
- `python3 Hololive-Style-Bert-VITS2/app.py --server-name 0.0.0.0 --no-autolaunch --share` runs only the TTS server.

## Coding Style & Naming Conventions
- Python 3.10+ is expected. Use 4-space indentation, `snake_case` for functions/variables, and `CamelCase` for classes.
- Linting uses Ruff (see `Open-LLM-VTuber-1.2.1/pyproject.toml`). Example: `uv run ruff check Open-LLM-VTuber-1.2.1/src/open_llm_vtuber`.
- Keep configs in YAML/JSON under the `config_templates/` or `configs/` folders; avoid hardcoding paths.

## Testing Guidelines
- Ad-hoc tests live at repo root: `python3 test_tts_call.py` and `python3 test_bert_vits2.py`.
- When changing TTS/ASR/agent modules, add or update a small, reproducible test script using the `test_*.py` pattern.

## Commit & Pull Request Guidelines
- Commit messages are short, lowercase, and imperative (examples: “add mcp”, “fix context err”).
- PRs should include a concise summary, steps to run/validate, and note any config or model changes. Add screenshots or short clips for frontend/Live2D UI updates.

## Configuration & Assets
- Do not commit API keys or personal tokens. Use config templates and local overrides instead.
- Large model assets should stay under `Hololive-Style-Bert-VITS2/model_assets/` or documented download steps.
