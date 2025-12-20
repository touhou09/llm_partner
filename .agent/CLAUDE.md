# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

This repository bundles two main projects wired together locally:
- **Open-LLM-VTuber-1.2.1/** - Voice-interactive AI companion server (FastAPI + WebSocket + Live2D frontend)
- **Hololive-Style-Bert-VITS2/** - Gradio-based Bert-VITS2 TTS server with bundled models

The root directory contains orchestration scripts, patches, and helper docs for running both services together.

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

# Lint/Format (Open-LLM-VTuber)
cd Open-LLM-VTuber-1.2.1
ruff check .
ruff format .
```

Combined workflow expects Bert-VITS2 on port `7860` and Open-LLM-VTuber on `12393`.

## Top-Level Layout

- `start_both.sh` - Start TTS then Open-LLM-VTuber (auto-patches gradio client)
- `stop_all.sh` - Stop all related processes and free common ports
- `patch_gradio_client.py` - Fixes `gradio_client` schema handling bug
- `cache/` - Generated artifacts (example: test audio output)
- `test_bert_vits2.py`, `test_tts_call.py` - Ad-hoc test scripts

## Execution Flow

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

## Open-LLM-VTuber Module Map

| File | Purpose |
|------|---------|
| `server.py` | FastAPI app startup, static serving, WebSocket endpoints |
| `websocket_handler.py` | Message dispatch, client state, audio/text event routing |
| `message_handler.py` | Higher-level message processing and state transitions |
| `service_context.py` | Dependency wiring, runtime engine selection, per-session lifecycle |
| `routes.py` | HTTP and WebSocket routing table definitions |
| `conversations/` | Conversation orchestration, single vs group handling, TTS streaming |
| `agent/` | Agent selection and stateless LLM adapters (Claude, OpenAI, Ollama) |
| `asr/` | ASR backends and factory for configuration-driven selection |
| `tts/` | TTS backends, including Bert-VITS2 bridge and cloud TTS options |
| `vad/` | Voice activity detection integration (Silero-based) |
| `config_manager/` | Typed config parsing and validation for each subsystem |
| `mcpp/` | MCP tool registry, JSON detection, and execution adapters |

Key design pattern: factories select concrete engines based on configuration. Each WebSocket connection gets its own service context instance.

## Open-LLM-VTuber Config & Assets

- User config: `conf.yaml` (runtime)
- Defaults: `config_templates/conf.default.yaml`, `config_templates/conf.ZH.default.yaml`
- Characters: `characters/`
- Live2D assets: `live2d-models/`
- Frontend: `frontend/`

## Bert-VITS2 Notes

- Main app: `app.py`
- Text processing: `text/`
- Configs: `configs/`
- Model assets: `model_assets/`
- Common helpers: `common/`

## Dependency Expectations

- Open-LLM-VTuber: Python >= 3.10; deps in `pyproject.toml`
- TTS env stability (pinned versions):
  - `numpy==1.26.4`, `transformers==4.37.0`, `gradio==4.36.1`, `gradio-client==1.0.1`, `torch==2.1.2`

## Local Fixes & Known Issues

| Issue | Solution |
|-------|----------|
| Gradio `additionalProperties` bool TypeError | `patch_gradio_client.py` (auto-applied by `start_both.sh`) |
| TTS zero-size array ValueError | Patched in `common/tts_model.py`, `app.py`, `infer.py` |
| Gradio schema errors | Re-apply patch or reinstall pinned versions |

See `BERT_VITS2_ERROR_FIX.md` and `PATCH_README.md` for details.

## Agent Working Rules

- **Scope**: Default to repo-wide impact; verify file ownership and module boundaries before edits
- **Safety**: Never edit model binary assets or large artifacts; prefer config/templates and code-level changes
- **Config changes**: Update both default YAML templates when adding new settings
- **Dependency changes**: Update `pyproject.toml` and lockfiles consistently; call out pinning rationale
- **Tests**: Add or update `test_*.py` when touching TTS/ASR/agent flow
- **TTS patching**: Keep `patch_gradio_client.py` in sync if upstream schema handling changes
- **Documentation**: When behavior changes, update this file and relevant root docs

## Change Impact Checklist

- [ ] Runtime configs touched? Update `config_templates/` and note upgrade steps
- [ ] WebSocket message types/payloads altered? Update handler mapping and frontend expectations
- [ ] New engine (LLM/ASR/TTS/VAD) introduced? Add to factory, config manager, and defaults
- [ ] Audio flow modified? Validate with `test_tts_call.py` or manual live run
- [ ] Live2D assets or UI affected? Capture before/after note or screenshot reference
