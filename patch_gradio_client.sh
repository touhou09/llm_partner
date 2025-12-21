#!/bin/bash

# Gradio Client 패치 스크립트
# gradio_client 라이브러리의 utils.py 파일에 bool 타입 처리 패치를 적용합니다.

# 사용법: ./patch_gradio_client.sh [venv_path]
# venv_path가 지정되지 않으면 현재 디렉토리의 .venv를 사용합니다

VENV_PATH="${1:-.venv}"
VITS2_DIR="${2:-/home/yujin/llm_partner/Hololive-Style-Bert-VITS2}"

# 가상환경 경로 확인
if [ ! -d "$VENV_PATH" ]; then
    echo "❌ 가상환경을 찾을 수 없습니다: $VENV_PATH"
    exit 1
fi

# Python 버전 확인
PYTHON_VERSION=$(basename "$VENV_PATH/lib" 2>/dev/null | head -1)
if [ -z "$PYTHON_VERSION" ]; then
    # 다른 구조 시도
    PYTHON_VERSION=$(ls -1 "$VENV_PATH/lib" 2>/dev/null | head -1)
fi

if [ -z "$PYTHON_VERSION" ]; then
    echo "❌ Python 버전을 확인할 수 없습니다."
    exit 1
fi

# gradio_client 경로 찾기
GRADIO_CLIENT_PATH="$VENV_PATH/lib/$PYTHON_VERSION/site-packages/gradio_client/utils.py"

if [ ! -f "$GRADIO_CLIENT_PATH" ]; then
    echo "❌ gradio_client를 찾을 수 없습니다: $GRADIO_CLIENT_PATH"
    echo "   gradio-client가 설치되어 있는지 확인하세요."
    exit 1
fi

echo "🔍 패치 대상 파일: $GRADIO_CLIENT_PATH"

# 패치가 이미 적용되었는지 확인
if grep -q "# 수정: schema가 dict가 아닌 경우" "$GRADIO_CLIENT_PATH" 2>/dev/null; then
    echo "✅ 패치가 이미 적용되어 있습니다."
    exit 0
fi

# 백업 생성
BACKUP_PATH="${GRADIO_CLIENT_PATH}.backup.$(date +%Y%m%d_%H%M%S)"
cp "$GRADIO_CLIENT_PATH" "$BACKUP_PATH"
echo "📦 백업 생성: $BACKUP_PATH"

# 패치 1: get_type() 함수 수정
echo "🔧 패치 적용 중: get_type() 함수..."
sed -i '/^def get_type(schema: dict):$/,/^    elif schema\.get("oneOf"):$/ {
    /^def get_type(schema: dict):$/ {
        a\
    # 수정: schema가 dict가 아닌 경우(예: bool)를 처리\
    if not isinstance(schema, dict):\
        if isinstance(schema, bool):\
            return "boolean"\
        return "Any"
    }
}' "$GRADIO_CLIENT_PATH"

# sed로는 복잡하므로 Python 스크립트 사용
python3 << 'PYTHON_PATCH'
import sys
import re

file_path = sys.argv[1]

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 패치 1: get_type() 함수 수정
get_type_pattern = r'(def get_type\(schema: dict\):\s*\n)'
replacement = r'\1    # 수정: schema가 dict가 아닌 경우(예: bool)를 처리\n    if not isinstance(schema, dict):\n        if isinstance(schema, bool):\n            return "boolean"\n        return "Any"\n'
if not re.search(r'# 수정: schema가 dict가 아닌 경우', content):
    content = re.sub(get_type_pattern, replacement, content, count=1)

# 패치 2: _json_schema_to_python_type() 함수 수정
json_schema_pattern = r'(def _json_schema_to_python_type\(schema: Any, defs\) -> str:\s*\n\s*""".*?"""\s*\n)'
if not re.search(r'# 수정: schema가 bool 타입일 때 처리', content):
    json_schema_replacement = r'\1    # 수정: schema가 bool 타입일 때 처리\n    if isinstance(schema, bool):\n        return "bool"\n'
    content = re.sub(json_schema_pattern, json_schema_replacement, content, count=1, flags=re.DOTALL)

# 패치 3: additionalProperties 처리 수정
additional_props_pattern = r'(\s+if "additionalProperties" in schema:\s*\n\s+des \+= \[\s*\n\s+f"str, \{_json_schema_to_python_type\(schema\[\'additionalProperties\'\], defs\)\}"\s*\n\s+\])'
if not re.search(r'# 수정: additionalProperties가 bool 타입일 때 처리', content):
    additional_props_replacement = r'''\1
            # 수정: additionalProperties가 bool 타입일 때 처리
            additional_props = schema['additionalProperties']
            if isinstance(additional_props, bool):
                # bool 타입인 경우 (False는 추가 속성 불허, True는 허용)
                if additional_props:
                    des += ["str, Any"]  # 추가 속성 허용
                # False인 경우는 추가하지 않음 (추가 속성 불허)
            else:
                # dict 타입인 경우 기존 로직 사용
                des += [
                    f"str, {_json_schema_to_python_type(additional_props, defs)}"
                ]'''
    content = re.sub(additional_props_pattern, additional_props_replacement, content, count=1)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ 패치 적용 완료!")
PYTHON_PATCH
"$GRADIO_CLIENT_PATH"

# 패치 적용 확인
if grep -q "# 수정: schema가 dict가 아닌 경우" "$GRADIO_CLIENT_PATH" 2>/dev/null; then
    echo "✅ 패치가 성공적으로 적용되었습니다."
else
    echo "❌ 패치 적용에 실패했습니다. 백업에서 복원합니다..."
    cp "$BACKUP_PATH" "$GRADIO_CLIENT_PATH"
    exit 1
fi

