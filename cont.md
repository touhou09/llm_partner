[7 tools called]

- 두 프로젝트 모두 `uv` 기반으로 구성할 수 있음을 확인했습니다. 루트에서 `uv --version`을 실행해 0.9.5가 설치되어 있음을 확인했습니다.  
- `Open-LLM-VTuber-1.2.1` 디렉터리에서 `uv sync`를 실행해 `pyproject.toml/uv.lock`에 정의된 모든 의존성을 `.venv`에 설치했습니다. 이후부터는 `uv run python run_server.py` 형태로 실행하면 됩니다.  
- `Hololive-Style-Bert-VITS2`에도 `uv venv .venv`로 전용 가상환경을 만들고 `uv pip install -r requirements_local.txt`를 실행해 `numpy`를 포함한 의존성 문제를 해결했습니다. 이 디렉터리에서는 `uv run --python .venv/bin/python app.py --server-name …` 혹은 `source .venv/bin/activate` 후 `python app.py`를 사용하세요.  
- 다음 단계로는 `start_both.sh`를 `uv run` 기반으로 바꾸거나 환경 활성화를 추가하는 방법을 검토할 수 있습니다.