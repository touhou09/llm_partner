# Repository Knowledge Base

## Overview
This repository bundles two main projects that are wired together locally:
- `Open-LLM-VTuber-1.2.1/`: the primary voice-interactive AI companion server (FastAPI + WebSocket + Live2D frontend).
- `Hololive-Style-Bert-VITS2/`: a Gradio-based Bert-VITS2 TTS server with bundled models and configs.

The root directory contains orchestration scripts, patches, and local helper docs for running both services together.

## Top-Level Layout
- `Open-LLM-VTuber-1.2.1/`: Python app, frontend, Live2D assets, configs, docs.
- `Hololive-Style-Bert-VITS2/`: TTS server, model assets, configs, text processing.
- `start_both.sh`: start TTS then Open-LLM-VTuber (auto-patches gradio client).
- `stop_all.sh`: stop all related processes and free common ports.
- `patch_gradio_client.py`: fixes `gradio_client` schema handling bug.
- `cache/`: generated artifacts (example: test audio output).
- `test_bert_vits2.py`, `test_tts_call.py`: ad-hoc test scripts.

## Running Locally
- Start both services (recommended): `./start_both.sh`
- Stop everything: `./stop_all.sh`
- Open-LLM-VTuber only: `uv run python Open-LLM-VTuber-1.2.1/run_server.py`
- Bert-VITS2 only: `python3 Hololive-Style-Bert-VITS2/app.py --server-name 0.0.0.0 --no-autolaunch --share`

The combined workflow expects Bert-VITS2 on port `7860` and Open-LLM-VTuber on `12393`.

## Open-LLM-VTuber Architecture (High Level)
- Entry point: `Open-LLM-VTuber-1.2.1/run_server.py`
- Server: `Open-LLM-VTuber-1.2.1/src/open_llm_vtuber/server.py` (FastAPI + WebSocket)
- WebSocket routing: `Open-LLM-VTuber-1.2.1/src/open_llm_vtuber/routes.py`
- Service container: `Open-LLM-VTuber-1.2.1/src/open_llm_vtuber/service_context.py`
- Conversations: `Open-LLM-VTuber-1.2.1/src/open_llm_vtuber/conversations/`
- Agents and LLM integrations: `Open-LLM-VTuber-1.2.1/src/open_llm_vtuber/agent/`
- ASR engines: `Open-LLM-VTuber-1.2.1/src/open_llm_vtuber/asr/`
- TTS engines: `Open-LLM-VTuber-1.2.1/src/open_llm_vtuber/tts/`
- VAD: `Open-LLM-VTuber-1.2.1/src/open_llm_vtuber/vad/`
- MCP tooling: `Open-LLM-VTuber-1.2.1/src/open_llm_vtuber/mcpp/`

Key design pattern: factories select concrete engines based on configuration (ASR, TTS, LLM, VAD). Each WebSocket connection gets its own service context instance.

## Open-LLM-VTuber Module Map (Focused)
- `src/open_llm_vtuber/server.py`: FastAPI app startup, static serving, and WebSocket endpoints.
- `src/open_llm_vtuber/websocket_handler.py`: message dispatch, client state, and routing for audio/text events.
- `src/open_llm_vtuber/message_handler.py`: higher-level message processing and state transitions.
- `src/open_llm_vtuber/service_context.py`: dependency wiring, runtime engine selection, per-session lifecycle.
- `src/open_llm_vtuber/routes.py`: HTTP and WebSocket routing table definitions.
- `src/open_llm_vtuber/conversations/`: conversation orchestration, single vs group handling, TTS streaming coordination.
- `src/open_llm_vtuber/agent/`: agent selection and stateless LLM adapters (Claude, OpenAI-compatible, Ollama).
- `src/open_llm_vtuber/asr/`: ASR backends and factory for configuration-driven selection.
- `src/open_llm_vtuber/tts/`: TTS backends, including Bert-VITS2 bridge and cloud TTS options.
- `src/open_llm_vtuber/vad/`: voice activity detection integration (Silero-based).
- `src/open_llm_vtuber/config_manager/`: typed config parsing and validation for each subsystem.
- `src/open_llm_vtuber/mcpp/`: MCP tool registry, JSON detection, and execution adapters.
- `frontend/`: static frontend assets (prebuilt).

## Execution Flow (Text Diagram)
```
Client UI
  -> WebSocket (frontend) / HTTP (static)
  -> server.py routes.py
  -> websocket_handler.py message dispatch
  -> service_context.py (engine wiring)
  -> conversation_handler.py (state + routing)
  -> agent/ (LLM) + asr/ (speech) + vad/ (speech gating)
  -> tts/ (audio generation)
  -> websocket_handler.py (audio stream back)
```

## Open-LLM-VTuber Config & Assets
- User config: `Open-LLM-VTuber-1.2.1/conf.yaml` (runtime)
- Defaults: `Open-LLM-VTuber-1.2.1/config_templates/conf.default.yaml` and `Open-LLM-VTuber-1.2.1/config_templates/conf.ZH.default.yaml`
- Characters: `Open-LLM-VTuber-1.2.1/characters/`
- Live2D assets: `Open-LLM-VTuber-1.2.1/live2d-models/`
- Frontend: `Open-LLM-VTuber-1.2.1/frontend/`

## Bert-VITS2 Notes
- Main app: `Hololive-Style-Bert-VITS2/app.py`
- Text processing: `Hololive-Style-Bert-VITS2/text/`
- Configs: `Hololive-Style-Bert-VITS2/configs/`
- Model assets: `Hololive-Style-Bert-VITS2/model_assets/`
- Common helpers: `Hololive-Style-Bert-VITS2/common/`

A local patch is applied to `gradio_client` via `patch_gradio_client.py`. This prevents schema parsing errors when `additionalProperties` is a boolean. The patch auto-runs from `start_both.sh` if a `.venv` exists.

## Dependency Expectations
- Open-LLM-VTuber: Python >= 3.10; dependencies defined in `Open-LLM-VTuber-1.2.1/pyproject.toml`.
- TTS env stability notes (from local fixes):
  - `numpy==1.26.4`, `transformers==4.37.0`, `gradio==4.36.1`, `gradio-client==1.0.1`, `torch==2.1.2`.

## Local Fixes & Known Issues
- A fix exists for empty/zero audio arrays in Bert-VITS2 (`Hololive-Style-Bert-VITS2/common/tts_model.py`, `Hololive-Style-Bert-VITS2/app.py`, `Hololive-Style-Bert-VITS2/infer.py`). See `BERT_VITS2_ERROR_FIX.md`.
- If Gradio schema errors recur, re-apply the patch or reinstall pinned versions (see `PATCH_README.md`).

## Testing & Linting
- Ad-hoc tests: `python3 test_tts_call.py`, `python3 test_bert_vits2.py`.
- Open-LLM-VTuber lint/format: `ruff check .` and `ruff format .` in `Open-LLM-VTuber-1.2.1/`.

## Obsidian MCP Integration
- Config template: `mcp-obsidian-config.json`.
- Instructions in `OBSIDIAN_MCP_SETUP.md` explain mapping a Windows Obsidian vault into WSL.

## Release/Update Notes
- Open-LLM-VTuber supports upgrades via `uv run upgrade.py`.
- CI, lint rules, and dependency metadata live in `Open-LLM-VTuber-1.2.1/pyproject.toml`.

## Quick Reference Commands
```bash
# Start both services
./start_both.sh

# Stop all servers
./stop_all.sh

# Open-LLM-VTuber only
cd Open-LLM-VTuber-1.2.1
uv run python run_server.py

# Bert-VITS2 only
cd Hololive-Style-Bert-VITS2
python3 app.py --server-name 0.0.0.0 --no-autolaunch --share
```

## Agent Working Rules (Shared)
- Scope: default to repo-wide impact; if unsure, verify file ownership and module boundaries before edits.
- Safety: never edit model binary assets or large artifacts; prefer config/templates and code-level changes.
- Config changes: update both default YAML templates when adding new settings, and note upgrade impact.
- Dependency changes: update `pyproject.toml` and lockfiles consistently; call out any pinning rationale.
- Tests: add or update `test_*.py` when touching TTS/ASR/agent flow, or explain why manual testing suffices.
- TTS patching: keep `patch_gradio_client.py` in sync if upstream schema handling changes.
- Documentation: when behavior changes, update this file and any relevant root docs.

## Change Impact Checklist
- Does the change touch runtime configs? Update `config_templates/` and note upgrade steps.
- Does it alter WebSocket message types or payloads? Update handler mapping and frontend expectations.
- Does it introduce a new engine (LLM/ASR/TTS/VAD)? Add to factory, config manager, and defaults.
- Does it modify audio flow? Validate with `test_tts_call.py` or a manual live run.
- Does it affect Live2D assets or UI? Capture a quick before/after note or screenshot reference.

## Recent Updates
- Added a shared repo knowledge base and agent working rules in `.agent/REPO_CONTEXT.md`.
- Updated `Open-LLM-VTuber-1.2.1/conf.yaml` persona prompt for Ame (English default, Japanese support, interview-style flow).
- Added `test_repo_context.py` to sanity-check required sections in the shared context doc.
