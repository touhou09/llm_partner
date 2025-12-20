"""Internal MCP tools for Open-LLM-VTuber (not from external MCP servers)."""

from typing import Dict, Any, List
from loguru import logger

from .types import FormattedTool


def get_obsidian_tools(obsidian_vault_manager) -> Dict[str, FormattedTool]:
    """Get Obsidian Vault tools as FormattedTool objects.

    Args:
        obsidian_vault_manager: ObsidianVaultManager instance or None.

    Returns:
        Dictionary of tool names to FormattedTool objects.
    """
    if not obsidian_vault_manager:
        return {}

    tools = {}

    # obsidian_read_note tool
    tools["obsidian_read_note"] = FormattedTool(
        input_schema={
            "type": "object",
            "properties": {
                "note_path": {
                    "type": "string",
                    "description": "Relative path to the note file from vault root (e.g., 'Daily Notes/2024-01-01.md')",
                }
            },
            "required": ["note_path"],
        },
        related_server="__internal__obsidian",  # 특별한 서버 이름으로 내부 도구 표시
        description="Read a note from the Obsidian Vault",
        generic_schema=None,
    )

    # obsidian_write_note tool
    tools["obsidian_write_note"] = FormattedTool(
        input_schema={
            "type": "object",
            "properties": {
                "note_path": {
                    "type": "string",
                    "description": "Relative path to the note file from vault root",
                },
                "content": {
                    "type": "string",
                    "description": "Content of the note (body text)",
                },
                "tags": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Optional list of tags to add to frontmatter",
                },
            },
            "required": ["note_path", "content"],
        },
        related_server="__internal__obsidian",
        description="Write or create a note in the Obsidian Vault",
        generic_schema=None,
    )

    # obsidian_create_daily_note tool
    tools["obsidian_create_daily_note"] = FormattedTool(
        input_schema={
            "type": "object",
            "properties": {
                "content": {
                    "type": "string",
                    "description": "Initial content for the daily note",
                },
                "date": {
                    "type": "string",
                    "description": "Date in YYYY-MM-DD format (optional, defaults to today)",
                },
            },
            "required": [],
        },
        related_server="__internal__obsidian",
        description="Create a daily note with date-based naming in the Obsidian Vault",
        generic_schema=None,
    )

    # obsidian_search_notes tool
    tools["obsidian_search_notes"] = FormattedTool(
        input_schema={
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search query string to find in note contents",
                },
                "directory": {
                    "type": "string",
                    "description": "Optional subdirectory to search in (relative to vault root)",
                },
            },
            "required": ["query"],
        },
        related_server="__internal__obsidian",
        description="Search notes by content in the Obsidian Vault",
        generic_schema=None,
    )

    # obsidian_list_notes tool
    tools["obsidian_list_notes"] = FormattedTool(
        input_schema={
            "type": "object",
            "properties": {
                "directory": {
                    "type": "string",
                    "description": "Optional subdirectory to list notes from (relative to vault root)",
                },
            },
            "required": [],
        },
        related_server="__internal__obsidian",
        description="List all notes in the Obsidian Vault",
        generic_schema=None,
    )

    # obsidian_append_to_note tool
    tools["obsidian_append_to_note"] = FormattedTool(
        input_schema={
            "type": "object",
            "properties": {
                "note_path": {
                    "type": "string",
                    "description": "Relative path to the note file",
                },
                "content": {
                    "type": "string",
                    "description": "Content to append to the note",
                },
            },
            "required": ["note_path", "content"],
        },
        related_server="__internal__obsidian",
        description="Append content to an existing note in the Obsidian Vault",
        generic_schema=None,
    )

    return tools


async def execute_obsidian_tool(
    tool_name: str, tool_args: Dict[str, Any], obsidian_vault_manager
) -> Dict[str, Any]:
    """Execute an Obsidian tool and return the result.

    Args:
        tool_name: Name of the tool to execute.
        tool_args: Arguments for the tool.
        obsidian_vault_manager: ObsidianVaultManager instance.

    Returns:
        Dictionary with metadata and content_items.
    """
    if not obsidian_vault_manager:
        return {
            "metadata": {},
            "content_items": [
                {
                    "type": "error",
                    "text": "Obsidian Vault Manager is not initialized. Please configure obsidian_vault_path in system_config.",
                }
            ],
        }

    try:
        if tool_name == "obsidian_read_note":
            note_path = tool_args.get("note_path")
            if not note_path:
                raise ValueError("note_path is required")
            content = obsidian_vault_manager.read_note(note_path)
            if content is None:
                return {
                    "metadata": {},
                    "content_items": [
                        {"type": "text", "text": f"Note not found: {note_path}"}
                    ],
                }
            return {
                "metadata": {"note_path": note_path},
                "content_items": [{"type": "text", "text": content}],
            }

        elif tool_name == "obsidian_write_note":
            note_path = tool_args.get("note_path")
            content = tool_args.get("content")
            tags = tool_args.get("tags", [])
            if not note_path or not content:
                raise ValueError("note_path and content are required")

            frontmatter = {}
            if tags:
                frontmatter["tags"] = tags

            success = obsidian_vault_manager.write_note(note_path, content, frontmatter)
            if success:
                return {
                    "metadata": {"note_path": note_path},
                    "content_items": [
                        {"type": "text", "text": f"Successfully wrote note: {note_path}"}
                    ],
                }
            else:
                return {
                    "metadata": {},
                    "content_items": [
                        {"type": "error", "text": f"Failed to write note: {note_path}"}
                    ],
                }

        elif tool_name == "obsidian_create_daily_note":
            content = tool_args.get("content", "")
            date_str = tool_args.get("date")

            from datetime import datetime

            date = None
            if date_str:
                try:
                    date = datetime.strptime(date_str, "%Y-%m-%d")
                except ValueError:
                    return {
                        "metadata": {},
                        "content_items": [
                            {
                                "type": "error",
                                "text": f"Invalid date format: {date_str}. Use YYYY-MM-DD format.",
                            }
                        ],
                    }

            note_path = obsidian_vault_manager.create_daily_note(date, content)
            if note_path:
                return {
                    "metadata": {"note_path": note_path},
                    "content_items": [
                        {"type": "text", "text": f"Created daily note: {note_path}"}
                    ],
                }
            else:
                return {
                    "metadata": {},
                    "content_items": [
                        {"type": "error", "text": "Failed to create daily note"}
                    ],
                }

        elif tool_name == "obsidian_search_notes":
            query = tool_args.get("query")
            directory = tool_args.get("directory", "")
            if not query:
                raise ValueError("query is required")

            results = obsidian_vault_manager.search_notes(query, directory)
            if not results:
                return {
                    "metadata": {},
                    "content_items": [
                        {"type": "text", "text": f"No notes found matching: {query}"}
                    ],
                }

            result_text = f"Found {len(results)} note(s) matching '{query}':\n\n"
            for result in results[:10]:  # 최대 10개만 표시
                result_text += f"- {result['path']}\n"
                for match in result.get("matches", [])[:3]:  # 각 노트당 최대 3개 라인
                    result_text += f"  Line {match['line_number']}: {match['content']}\n"
                result_text += "\n"

            return {
                "metadata": {"result_count": len(results)},
                "content_items": [{"type": "text", "text": result_text}],
            }

        elif tool_name == "obsidian_list_notes":
            directory = tool_args.get("directory", "")
            notes = obsidian_vault_manager.list_notes(directory)
            if not notes:
                return {
                    "metadata": {},
                    "content_items": [
                        {"type": "text", "text": f"No notes found in: {directory or 'root'}"}
                    ],
                }

            result_text = f"Found {len(notes)} note(s):\n\n"
            for note in notes[:50]:  # 최대 50개만 표시
                result_text += f"- {note}\n"

            return {
                "metadata": {"note_count": len(notes)},
                "content_items": [{"type": "text", "text": result_text}],
            }

        elif tool_name == "obsidian_append_to_note":
            note_path = tool_args.get("note_path")
            content = tool_args.get("content")
            if not note_path or not content:
                raise ValueError("note_path and content are required")

            success = obsidian_vault_manager.append_to_note(note_path, content)
            if success:
                return {
                    "metadata": {"note_path": note_path},
                    "content_items": [
                        {
                            "type": "text",
                            "text": f"Successfully appended to note: {note_path}",
                        }
                    ],
                }
            else:
                return {
                    "metadata": {},
                    "content_items": [
                        {"type": "error", "text": f"Failed to append to note: {note_path}"}
                    ],
                }

        else:
            return {
                "metadata": {},
                "content_items": [
                    {"type": "error", "text": f"Unknown Obsidian tool: {tool_name}"}
                ],
            }

    except Exception as e:
        logger.exception(f"Error executing Obsidian tool '{tool_name}': {e}")
        return {
            "metadata": {},
            "content_items": [
                {"type": "error", "text": f"Error executing {tool_name}: {str(e)}"}
            ],
        }
