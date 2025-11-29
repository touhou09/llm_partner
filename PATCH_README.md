# Gradio Client 패치 가이드

## 개요

이 프로젝트는 `gradio_client` 라이브러리의 버그를 수정하기 위한 패치를 포함합니다.

**문제**: `gradio_client` 라이브러리에서 `additionalProperties`가 bool 타입일 때 `TypeError: argument of type 'bool' is not iterable` 에러가 발생합니다.

**해결**: `gradio_client/utils.py` 파일에 bool 타입 처리를 추가하는 패치를 적용합니다.

## 자동 패치 적용

`start_both.sh` 스크립트를 실행하면 자동으로 패치가 적용됩니다:

```bash
./start_both.sh
```

## 수동 패치 적용

가상환경을 재생성한 후 수동으로 패치를 적용하려면:

```bash
# Bert-VITS2 가상환경에 패치 적용
python3 patch_gradio_client.py /path/to/Hololive-Style-Bert-VITS2/.venv
```

## 패치 내용

다음 세 가지 함수가 수정됩니다:

1. **`get_type()` 함수**: `schema`가 dict가 아닌 경우(예: bool)를 처리
2. **`_json_schema_to_python_type()` 함수**: `schema`가 bool 타입일 때를 처리
3. **`additionalProperties` 처리**: `additionalProperties`가 bool 타입일 때를 처리

## 패치 확인

패치가 이미 적용되어 있는지 확인하려면:

```bash
python3 patch_gradio_client.py /path/to/.venv
```

이미 패치가 적용되어 있으면 "✅ 패치가 이미 적용되어 있습니다." 메시지가 표시됩니다.

## 백업

패치 적용 전에 자동으로 백업이 생성됩니다:
- 백업 파일 위치: `utils.py.backup.YYYYMMDD_HHMMSS.py`
- 패치 실패 시 자동으로 백업에서 복원됩니다

## 주의사항

- 이 패치는 가상환경 내의 라이브러리 파일을 직접 수정합니다
- 가상환경을 재생성하면 패치가 사라지므로 다시 적용해야 합니다
- `start_both.sh`를 사용하면 자동으로 패치가 적용됩니다

## 문제 해결

패치 적용 중 오류가 발생하면:

1. 백업 파일이 자동으로 생성되었는지 확인
2. 가상환경이 올바르게 설정되어 있는지 확인
3. `gradio-client`가 설치되어 있는지 확인

```bash
# gradio-client 설치 확인
.venv/bin/pip list | grep gradio-client
```

