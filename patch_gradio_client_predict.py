#!/usr/bin/env python3
"""
gradio_client의 _predict 메서드를 패치하여 HTTP 모드에서도 올바르게 작동하도록 수정
"""

import os
import sys
import shutil
from pathlib import Path

def find_gradio_client_path():
    """gradio_client 패키지 경로 찾기 - 모든 가상환경 확인"""
    found_paths = []
    
    # 먼저 import로 찾기 시도
    try:
        import gradio_client
        package_path = Path(gradio_client.__file__).parent
        client_py = package_path / "client.py"
        if client_py.exists():
            found_paths.append(str(client_py))
    except Exception as e:
        print(f"⚠️  gradio_client import 실패: {e}")
    
    # 대체 경로 시도 (모든 가능한 경로 확인)
    possible_paths = []
    
    # 현재 작업 디렉토리 기준으로 찾기
    base_dirs = [
        os.path.expanduser("~"),
        "/home/yujin/llm_partner",
        os.getcwd(),
    ]
    
    for base_dir in base_dirs:
        # Python 버전별로 찾기
        for py_version in ["3.10", "3.11", "3.12"]:
            possible_paths.extend([
                os.path.join(base_dir, f"Hololive-Style-Bert-VITS2/.venv/lib/python{py_version}/site-packages/gradio_client/client.py"),
                os.path.join(base_dir, f"Open-LLM-VTuber-1.2.1/.venv/lib/python{py_version}/site-packages/gradio_client/client.py"),
            ])
    
    # 직접 경로도 추가
    possible_paths.extend([
        "/home/yujin/llm_partner/Hololive-Style-Bert-VITS2/.venv/lib/python3.10/site-packages/gradio_client/client.py",
        "/home/yujin/llm_partner/Open-LLM-VTuber-1.2.1/.venv/lib/python3.10/site-packages/gradio_client/client.py",
    ])
    
    for path in possible_paths:
        if os.path.exists(path) and path not in found_paths:
            found_paths.append(path)
    
    # 모든 경로 반환 (여러 가상환경에 패치 적용)
    return found_paths if found_paths else None

def patch_gradio_client_predict():
    """gradio_client의 _predict 메서드 패치 - 모든 가상환경에 적용"""
    client_py_paths = find_gradio_client_path()
    
    if not client_py_paths:
        print("❌ gradio_client/client.py를 찾을 수 없습니다.")
        return False
    
    # 여러 경로가 있을 수 있으므로 모두 패치
    if isinstance(client_py_paths, str):
        client_py_paths = [client_py_paths]
    
    success_count = 0
    for client_py_path in client_py_paths:
        print(f"📂 gradio_client 경로: {client_py_path}")
    
    # 백업 파일 생성
    backup_path = client_py_path + ".backup_predict"
    if not os.path.exists(backup_path):
        try:
            shutil.copy2(client_py_path, backup_path)
            print(f"✅ 백업 파일 생성: {backup_path}")
        except Exception as e:
            print(f"⚠️  백업 파일 생성 실패: {e}")
            return False
    
    # 파일 읽기
    try:
        with open(client_py_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"❌ 파일 읽기 실패: {e}")
        return False
    
    # 패치가 이미 적용되었는지 확인
    if 'if result is None:' in content and '# 수정: HTTP 모드에서 result가 None인 경우 처리' in content:
        print("✅ 패치가 이미 적용되어 있습니다.")
        return True
    
    # _predict 메서드 찾기 및 패치
    # KeyError: 'data' 발생 지점 수정
    old_pattern = """            try:
                output = result["data"]
            except KeyError as ke:
                is_public_space = (
                    self.client.space_id
                    and not huggingface_hub.space_info(self.client.space_id).private
                )
                if "error" in result and "429" in result["error"] and is_public_space:"""
    
    new_pattern = """            # 수정: HTTP 모드에서 result가 None인 경우 처리
            if result is None:
                raise ValueError("Server returned None result. This may indicate a connection issue or server error.")
            
            try:
                output = result["data"]
            except KeyError as ke:
                is_public_space = (
                    self.client.space_id
                    and not huggingface_hub.space_info(self.client.space_id).private
                )
                # 수정: result가 None이거나 dict가 아닌 경우 처리
                if result is None:
                    raise ValueError("Server returned None result. This may indicate a connection issue or server error.")
                if not isinstance(result, dict):
                    raise ValueError(f"Unexpected result type: {type(result)}, value: {result}")
                if "error" in result and result.get("error") is not None and "429" in str(result["error"]) and is_public_space:"""
    
    if old_pattern in content:
        content = content.replace(old_pattern, new_pattern)
        print("✅ _predict 메서드 패치 적용")
    else:
        # 대체 패턴 시도
        old_pattern2 = """            try:
                output = result["data"]
            except KeyError as ke:
                is_public_space = (
                    self.client.space_id
                    and not huggingface_hub.space_info(self.client.space_id).private
                )
                if "error" in result and "429" in result["error"] and is_public_space:"""
        
        if old_pattern2 in content:
            content = content.replace(old_pattern2, new_pattern)
            print("✅ _predict 메서드 패치 적용 (대체 패턴)")
        else:
            # 더 유연한 패턴 매칭
            import re
            pattern = r'(try:\s+output = result\["data"\]\s+except KeyError as ke:.*?if "error" in result)'
            replacement = r'''# 수정: HTTP 모드에서 result가 None인 경우 처리
            if result is None:
                raise ValueError("Server returned None result. This may indicate a connection issue or server error.")
            
            \1'''
            
            if re.search(pattern, content, re.DOTALL):
                content = re.sub(pattern, replacement, content, flags=re.DOTALL)
                print("✅ _predict 메서드 패치 적용 (정규식 패턴)")
            else:
                print("⚠️  패치할 패턴을 찾을 수 없습니다. 수동으로 확인이 필요합니다.")
                print("찾고 있는 패턴:")
                print("  try:")
                print('    output = result["data"]')
                print("  except KeyError as ke:")
                return False
    
        # 파일 쓰기
        try:
            with open(client_py_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ 패치 완료: {client_py_path}")
            success_count += 1
        except Exception as e:
            print(f"❌ 파일 쓰기 실패 ({client_py_path}): {e}")
            # 백업에서 복원 시도
            try:
                if os.path.exists(backup_path):
                    shutil.copy2(backup_path, client_py_path)
                    print("✅ 백업에서 복원 완료")
            except:
                pass
    
    return success_count > 0

if __name__ == "__main__":
    print("🔧 gradio_client _predict 메서드 패치 시작...")
    success = patch_gradio_client_predict()
    if success:
        print("✅ 패치 완료!")
        sys.exit(0)
    else:
        print("❌ 패치 실패!")
        sys.exit(1)

