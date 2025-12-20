#!/usr/bin/env python3
"""
Gradio Client 패치 스크립트
gradio_client 라이브러리의 utils.py 파일에 bool 타입 처리 패치를 적용합니다.
"""

import os
import sys
import shutil
from pathlib import Path
from datetime import datetime


def find_gradio_client_path(venv_path: str) -> Path:
    """가상환경에서 gradio_client 경로를 찾습니다."""
    venv_path = Path(venv_path).resolve()
    
    # Python 버전 디렉토리 찾기
    lib_path = venv_path / "lib"
    if not lib_path.exists():
        raise FileNotFoundError(f"가상환경 lib 디렉토리를 찾을 수 없습니다: {lib_path}")
    
    # Python 버전 디렉토리 찾기 (예: python3.10)
    python_dirs = [d for d in lib_path.iterdir() if d.is_dir() and d.name.startswith("python")]
    if not python_dirs:
        raise FileNotFoundError(f"Python 버전 디렉토리를 찾을 수 없습니다: {lib_path}")
    
    python_version_dir = python_dirs[0]
    gradio_client_path = python_version_dir / "site-packages" / "gradio_client" / "utils.py"
    
    if not gradio_client_path.exists():
        raise FileNotFoundError(
            f"gradio_client를 찾을 수 없습니다: {gradio_client_path}\n"
            "gradio-client가 설치되어 있는지 확인하세요."
        )
    
    return gradio_client_path


def is_patched(content: str) -> bool:
    """패치가 이미 적용되었는지 확인합니다."""
    return "# 수정: schema가 dict가 아닌 경우" in content


def apply_patch(content: str) -> str:
    """패치를 적용합니다."""
    lines = content.splitlines(keepends=True)
    new_lines = []
    i = 0
    
    while i < len(lines):
        line = lines[i]
        
        # 패치 1: get_type() 함수 수정
        if line.strip() == "def get_type(schema: dict):":
            new_lines.append(line)
            i += 1
            # 다음 줄이 이미 패치된 내용인지 확인
            if i < len(lines) and "# 수정: schema가 dict가 아닌 경우" in lines[i]:
                # 이미 패치됨, 나머지 건너뛰기
                while i < len(lines) and (lines[i].strip().startswith("#") or 
                                          "isinstance(schema" in lines[i] or
                                          "return" in lines[i]):
                    new_lines.append(lines[i])
                    i += 1
                continue
            
            # 패치 추가
            new_lines.append("    # 수정: schema가 dict가 아닌 경우(예: bool)를 처리\n")
            new_lines.append("    if not isinstance(schema, dict):\n")
            new_lines.append("        if isinstance(schema, bool):\n")
            new_lines.append("            return \"boolean\"\n")
            new_lines.append("        return \"Any\"\n")
            continue
        
        # 패치 2: _json_schema_to_python_type() 함수 수정
        if line.strip().startswith("def _json_schema_to_python_type(schema: Any, defs) -> str:"):
            new_lines.append(line)
            i += 1
            
            # docstring 건너뛰기
            docstring_started = False
            while i < len(lines):
                if '"""' in lines[i]:
                    if docstring_started:
                        new_lines.append(lines[i])
                        i += 1
                        break
                    docstring_started = True
                new_lines.append(lines[i])
                i += 1
                if docstring_started and '"""' in lines[i-1]:
                    break
            
            # 다음 줄이 이미 패치된 내용인지 확인
            if i < len(lines) and "# 수정: schema가 bool 타입일 때 처리" in lines[i]:
                # 이미 패치됨, 나머지 그대로 복사
                while i < len(lines):
                    new_lines.append(lines[i])
                    i += 1
                continue
            
            # 패치 추가
            new_lines.append("    # 수정: schema가 bool 타입일 때 처리\n")
            new_lines.append("    if isinstance(schema, bool):\n")
            new_lines.append("        return \"bool\"\n")
            continue
        
        # 패치 3: additionalProperties 처리 수정
        if '"additionalProperties" in schema:' in line or "'additionalProperties' in schema:" in line:
            new_lines.append(line)
            i += 1
            
            # 다음 줄이 이미 패치된 내용인지 확인
            if i < len(lines) and "# 수정: additionalProperties가 bool 타입일 때 처리" in lines[i]:
                # 이미 패치됨, 나머지 건너뛰기
                while i < len(lines):
                    new_lines.append(lines[i])
                    i += 1
                continue
            
            # 기존 코드 블록 읽기 (des += [...] 까지)
            indent = len(line) - len(line.lstrip())
            old_block = []
            while i < len(lines):
                current_line = lines[i]
                # des += 로 시작하는 줄을 찾을 때까지
                if "des +=" in current_line:
                    old_block.append(current_line)
                    i += 1
                    # 닫는 대괄호까지 읽기
                    while i < len(lines) and "]" not in lines[i]:
                        old_block.append(lines[i])
                        i += 1
                    if i < len(lines):
                        old_block.append(lines[i])
                        i += 1
                    break
                old_block.append(current_line)
                i += 1
            
            # 패치된 코드 추가
            new_lines.append(" " * (indent + 4) + "# 수정: additionalProperties가 bool 타입일 때 처리\n")
            new_lines.append(" " * (indent + 4) + "additional_props = schema['additionalProperties']\n")
            new_lines.append(" " * (indent + 4) + "if isinstance(additional_props, bool):\n")
            new_lines.append(" " * (indent + 8) + "# bool 타입인 경우 (False는 추가 속성 불허, True는 허용)\n")
            new_lines.append(" " * (indent + 8) + "if additional_props:\n")
            new_lines.append(" " * (indent + 12) + "des += [\"str, Any\"]  # 추가 속성 허용\n")
            new_lines.append(" " * (indent + 8) + "# False인 경우는 추가하지 않음 (추가 속성 불허)\n")
            new_lines.append(" " * (indent + 4) + "else:\n")
            new_lines.append(" " * (indent + 8) + "# dict 타입인 경우 기존 로직 사용\n")
            new_lines.append(" " * (indent + 8) + "des += [\n")
            new_lines.append(" " * (indent + 12) + "f\"str, {_json_schema_to_python_type(additional_props, defs)}\"\n")
            new_lines.append(" " * (indent + 8) + "]\n")
            continue
        
        new_lines.append(line)
        i += 1
    
    return "".join(new_lines)


def main():
    """메인 함수"""
    if len(sys.argv) < 2:
        print("사용법: python3 patch_gradio_client.py <venv_path>")
        print("예시: python3 patch_gradio_client.py /path/to/.venv")
        sys.exit(1)
    
    venv_path = sys.argv[1]
    
    try:
        # gradio_client 경로 찾기
        gradio_client_path = find_gradio_client_path(venv_path)
        print(f"🔍 패치 대상 파일: {gradio_client_path}")
        
        # 파일 읽기
        with open(gradio_client_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 이미 패치되었는지 확인
        if is_patched(content):
            print("✅ 패치가 이미 적용되어 있습니다.")
            return 0
        
        # 백업 생성
        backup_path = gradio_client_path.with_suffix(
            f".backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}.py"
        )
        shutil.copy2(gradio_client_path, backup_path)
        print(f"📦 백업 생성: {backup_path}")
        
        # 패치 적용
        print("🔧 패치 적용 중...")
        patched_content = apply_patch(content)
        
        # 파일 쓰기
        with open(gradio_client_path, 'w', encoding='utf-8') as f:
            f.write(patched_content)
        
        # 패치 확인
        with open(gradio_client_path, 'r', encoding='utf-8') as f:
            new_content = f.read()
        
        if is_patched(new_content):
            print("✅ 패치가 성공적으로 적용되었습니다.")
            return 0
        else:
            print("❌ 패치 적용에 실패했습니다. 백업에서 복원합니다...")
            shutil.copy2(backup_path, gradio_client_path)
            return 1
            
    except FileNotFoundError as e:
        print(f"❌ {e}")
        return 1
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
