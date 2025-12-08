# Obsidian Vault 통합 가이드

## 개요

Open-LLM-VTuber에 Obsidian Vault 통합 기능이 추가되었습니다. 이를 통해 AI가 Obsidian 노트를 읽고 쓸 수 있습니다.

## 설정 방법

### 1. 설정 파일에 Obsidian Vault 경로 추가

`conf.yaml` 파일의 `system_config` 섹션에 Obsidian Vault 경로를 추가하세요:

```yaml
system_config:
  # ... 기존 설정 ...
  obsidian_vault_path: '/mnt/c/Users/yujin/iCloudDrive/iCloud~md~obsidian/Obsidian'
```

**WSL 환경에서 Windows 경로 사용:**
- Windows 경로: `C:\Users\yujin\iCloudDrive\iCloud~md~obsidian\Obsidian`
- WSL 경로: `/mnt/c/Users/yujin/iCloudDrive/iCloud~md~obsidian/Obsidian`

### 2. 코드에서 사용하기

```python
from open_llm_vtuber.obsidian import ObsidianVaultManager
from open_llm_vtuber.config_manager import read_yaml, validate_config

# 설정 로드
config = validate_config(read_yaml("conf.yaml"))
system_config = config.system_config

# Obsidian Vault Manager 초기화
if system_config.obsidian_vault_path:
    vault_manager = ObsidianVaultManager(system_config.obsidian_vault_path)
    
    # 노트 읽기
    content = vault_manager.read_note("Daily Notes/2024-01-01.md")
    
    # 노트 쓰기
    vault_manager.write_note(
        "My Note.md",
        "# 제목\n\n내용입니다.",
        frontmatter={"tags": ["test"], "created": "2024-01-01"}
    )
    
    # 데일리 노트 생성
    note_path = vault_manager.create_daily_note(content="오늘의 일기")
    
    # 노트 검색
    results = vault_manager.search_notes("키워드")
    
    # 노트 목록 가져오기
    notes = vault_manager.list_notes("Daily Notes")
```

## 사용 가능한 기능

### ObsidianVaultManager 클래스

#### `read_note(note_path: str) -> str | None`
노트 파일을 읽습니다.

**매개변수:**
- `note_path`: Vault 루트 기준 상대 경로 (예: `"Daily Notes/2024-01-01.md"`)

**반환값:**
- 노트 내용 문자열 또는 `None` (파일이 없을 경우)

#### `write_note(note_path: str, content: str, frontmatter: Dict[str, Any] | None = None) -> bool`
노트 파일을 작성합니다.

**매개변수:**
- `note_path`: Vault 루트 기준 상대 경로
- `content`: 노트 본문 내용
- `frontmatter`: 선택적 YAML frontmatter 딕셔너리

**반환값:**
- 성공 시 `True`, 실패 시 `False`

#### `create_daily_note(date: datetime | None = None, content: str = "") -> str | None`
날짜 기반 데일리 노트를 생성합니다.

**매개변수:**
- `date`: 날짜 (기본값: 오늘)
- `content`: 초기 내용

**반환값:**
- 생성된 노트의 경로 또는 `None`

#### `list_notes(directory: str = "", pattern: str = "*.md") -> List[str]`
노트 목록을 가져옵니다.

**매개변수:**
- `directory`: 검색할 하위 디렉토리 (기본값: 루트)
- `pattern`: 파일 패턴 (기본값: `"*.md"`)

**반환값:**
- 노트 경로 리스트

#### `search_notes(query: str, directory: str = "") -> List[Dict[str, Any]]`
노트 내용을 검색합니다.

**매개변수:**
- `query`: 검색 쿼리 문자열
- `directory`: 검색할 하위 디렉토리

**반환값:**
- 매칭된 노트와 라인 정보를 포함한 딕셔너리 리스트

#### `get_note_tags(note_path: str) -> List[str]`
노트에서 태그를 추출합니다.

**매개변수:**
- `note_path`: 노트 경로

**반환값:**
- 태그 리스트 (예: `["tag1", "tag2/subtag"]`)

#### `append_to_note(note_path: str, content: str) -> bool`
기존 노트에 내용을 추가합니다.

**매개변수:**
- `note_path`: 노트 경로
- `content`: 추가할 내용

**반환값:**
- 성공 시 `True`, 실패 시 `False`

## 보안 고려사항

- 모든 파일 접근은 Vault 루트 디렉토리 내로 제한됩니다
- 경로 탐색 공격을 방지하기 위해 상대 경로 검증이 수행됩니다
- 존재하지 않는 디렉토리는 자동으로 생성됩니다

## 활용 예시

### 1. 대화 기록을 Obsidian에 저장

```python
async def save_conversation_to_obsidian(
    vault_manager: ObsidianVaultManager,
    conversation_history: List[Dict],
    date: datetime
):
    """대화 기록을 Obsidian 데일리 노트에 저장"""
    date_str = date.strftime("%Y-%m-%d")
    note_path = f"Conversations/{date_str}.md"
    
    content = f"# 대화 기록 - {date_str}\n\n"
    for msg in conversation_history:
        role = msg.get("role", "unknown")
        text = msg.get("content", "")
        content += f"## {role}\n\n{text}\n\n"
    
    vault_manager.write_note(
        note_path,
        content,
        frontmatter={
            "tags": ["conversation", "ai"],
            "date": date_str
        }
    )
```

### 2. 아이디어를 Obsidian에 기록

```python
def save_idea_to_obsidian(
    vault_manager: ObsidianVaultManager,
    idea: str,
    category: str = "Ideas"
):
    """아이디어를 Obsidian에 저장"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    note_path = f"{category}/{timestamp}.md"
    
    vault_manager.write_note(
        note_path,
        f"# 아이디어\n\n{idea}",
        frontmatter={
            "tags": ["idea", category.lower()],
            "created": datetime.now().isoformat()
        }
    )
```

### 3. 노트 검색 및 참조

```python
def find_relevant_notes(
    vault_manager: ObsidianVaultManager,
    query: str
) -> List[Dict]:
    """관련 노트 검색"""
    results = vault_manager.search_notes(query)
    
    for result in results:
        print(f"노트: {result['path']}")
        for match in result['matches']:
            print(f"  라인 {match['line_number']}: {match['content']}")
    
    return results
```

## 주의사항

1. **경로 형식**: WSL 환경에서는 Windows 경로를 `/mnt/c/` 형식으로 변환해야 합니다
2. **권한**: Obsidian Vault 디렉토리에 읽기/쓰기 권한이 있어야 합니다
3. **인코딩**: 모든 파일은 UTF-8 인코딩으로 처리됩니다
4. **성능**: 대량의 노트를 검색할 때는 시간이 걸릴 수 있습니다

## 향후 개선 계획

- MCP 도구로 Obsidian 기능 노출 (LLM이 직접 사용 가능)
- Obsidian 플러그인과의 통합
- 실시간 노트 동기화
- 태그 기반 자동 분류
