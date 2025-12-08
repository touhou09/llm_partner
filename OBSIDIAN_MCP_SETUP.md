# Obsidian MCP 설정 가이드

## 개요

이 문서는 Obsidian Vault를 MCP (Model Context Protocol) filesystem capability로 연결하는 방법을 설명합니다.

## 설정 방법

### 1. Obsidian Vault 경로 확인

**WSL 환경에서 Windows 파일 시스템 접근:**

WSL에서 Windows 파일 시스템은 `/mnt/c/` 경로를 통해 접근합니다.

먼저 자신의 Obsidian Vault 폴더 경로를 확인하세요:

**Windows에서 Obsidian Vault 경로 확인 방법:**
1. Obsidian 앱을 열고 `설정 > 파일 및 링크 > Vault 위치`에서 확인
2. 일반적인 위치:
   - `C:\Users\<Windows사용자명>\Documents\ObsidianVault`
   - `C:\Users\<Windows사용자명>\AppData\Roaming\Obsidian\<Vault이름>`

**WSL에서 Windows 경로 변환:**
- Windows: `C:\Users\username\Documents\ObsidianVault`
- WSL: `/mnt/c/Users/username/Documents/ObsidianVault`

**iCloud Drive 경로 예시:**
- Windows: `C:\Users\yujin\iCloudDrive\iCloud~md~obsidian\Obsidian`
- WSL: `/mnt/c/Users/yujin/iCloudDrive/iCloud~md~obsidian/Obsidian`

### 2. MCP 설정 파일 수정

`mcp-obsidian-config.json` 파일을 열고 `root` 경로를 자신의 Obsidian Vault 경로로 수정하세요:

**현재 설정된 경로 (iCloud Drive 예시):**
```json
{
  "capabilities": {
    "filesystem": {
      "root": "/mnt/c/Users/yujin/iCloudDrive/iCloud~md~obsidian/Obsidian"
    }
  }
}
```

**다른 경로 예시:**
```json
{
  "capabilities": {
    "filesystem": {
      "root": "/mnt/c/Users/YOUR_WINDOWS_USERNAME/Documents/ObsidianVault"
    }
  }
}
```

**경로 확인 명령어 (WSL에서 실행):**
```bash
# Windows 사용자명 확인
echo $USER
# 또는
whoami

# Windows Documents 폴더 확인
ls /mnt/c/Users/*/Documents/ | grep -i obsidian

# Windows AppData 폴더 확인 (Obsidian 기본 위치)
ls /mnt/c/Users/*/AppData/Roaming/Obsidian/
```

### 3. Cursor에서 MCP 설정 적용

Cursor에서 MCP 설정을 적용하려면:

1. Cursor 설정 열기 (Ctrl+, 또는 Cmd+,)
2. MCP 설정 섹션으로 이동
3. `mcp-obsidian-config.json` 파일의 내용을 복사하여 설정에 추가

또는 Cursor의 MCP 설정 파일 위치에 직접 복사할 수 있습니다:
- Windows: `%APPDATA%\Cursor\User\globalStorage\mcp.json`
- macOS: `~/Library/Application Support/Cursor/User/globalStorage/mcp.json`
- Linux: `~/.config/Cursor/User/globalStorage/mcp.json`

## 사용 가능한 기능

MCP filesystem capability가 설정되면, ChatGPT나 MCP 클라이언트가 Obsidian Vault 안의 파일을:

- ✅ **읽기** - 노트 내용 읽기
- ✅ **쓰기** - 새 노트 생성
- ✅ **수정** - 기존 노트 수정
- ✅ **생성** - 새 파일/폴더 생성

## 활용 예시

- 📝 데일리 노트 생성 자동화
- 🏷️ 태그 재구성 및 정리
- 📋 Properties 정리
- 📑 Index 문서 자동 생성
- 🔗 링크 관계 분석 및 정리
- 📊 노트 통계 및 분석

## 참고사항

- Obsidian Vault는 기본적으로 로컬 폴더 기반이므로 MCP와 궁합이 좋습니다
- 설정 후 MCP 클라이언트를 재시작해야 변경사항이 적용됩니다
- 보안을 위해 중요한 Vault는 신중하게 설정하세요

## WSL 환경 특별 주의사항

- WSL에서 Windows 파일 시스템 접근 시 `/mnt/c/` 경로 사용 필수
- Windows 사용자명은 대소문자를 구분하지 않지만, 경로는 정확히 입력해야 합니다
- Windows 경로의 공백이 있으면 경로를 따옴표로 감싸거나 이스케이프 처리하세요
- 파일 권한 문제가 발생할 수 있으므로, 필요시 `chmod` 명령어로 권한을 확인하세요
