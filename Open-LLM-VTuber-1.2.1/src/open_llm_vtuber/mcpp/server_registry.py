"""MCP Server Manager for Open-LLM-Vtuber."""

import shutil
import json
import os

from pathlib import Path
from typing import Dict, Optional, Union, Any
from loguru import logger

from .types import MCPServer
from .utils.path import validate_file

DEFAULT_CONFIG_PATH = "mcp_servers.json"


class ServerRegistry:
    """MCP Server Manager for managing server files."""

    def __init__(self, config_path: str | Path = None) -> None:
        """Initialize the MCP Server Manager."""
        # 수정: 환경 변수에서 mcp_servers.json 경로 읽기
        if config_path is None:
            # MCP_SERVERS_CONFIG 환경 변수 확인
            env_config_path = os.getenv("MCP_SERVERS_CONFIG")
            if env_config_path:
                config_path = Path(env_config_path)
                # 상대 경로인 경우 최상단 디렉토리 기준으로 해석
                if not config_path.is_absolute():
                    # 현재 파일 위치에서 최상단 디렉토리 찾기
                    # src/open_llm_vtuber/mcpp/server_registry.py -> Open-LLM-VTuber-1.2.1 -> 최상단
                    current_file = Path(__file__)
                    top_level_dir = current_file.parent.parent.parent.parent.parent
                    config_path = top_level_dir / config_path
            else:
                config_path = DEFAULT_CONFIG_PATH
        
        try:
            config_path = validate_file(config_path, ".json")
        except ValueError:
            logger.error(
                f"MCPSR: File '{config_path}' does not exist, or is not a json file."
            )
            raise ValueError(
                f"MCPSR: File '{config_path}' does not exist, or is not a json file."
            )

        self.config: Dict[str, Union[str, dict]] = json.loads(
            config_path.read_text(encoding="utf-8")
        )

        self.servers: Dict[str, MCPServer] = {}

        self.npx_available = self._detect_runtime("npx")
        self.uvx_available = self._detect_runtime("uvx")
        self.node_available = self._detect_runtime("node")

        self.load_servers()

    def _detect_runtime(self, target: str) -> bool:
        """Check if a runtime is available in the system PATH."""
        founded = shutil.which(target)
        return True if founded else False

    def load_servers(self) -> None:
        """Load servers from the config file."""
        servers_config: Dict[str, Dict[str, Any]] = self.config.get("mcp_servers", {})
        if servers_config == {}:
            logger.warning("MCPSR: No servers found in the config file.")
            return

        for server_name, server_details in servers_config.items():
            if "command" not in server_details or "args" not in server_details:
                logger.warning(
                    f"MCPSR: Invalid server details for '{server_name}'. Ignoring."
                )
                continue

            command = server_details["command"]
            if command == "npx":
                if not self.npx_available:
                    logger.warning(
                        f"MCPSR: npx is not available. Cannot load server '{server_name}'."
                    )
                    continue
            elif command == "uvx":
                if not self.uvx_available:
                    logger.warning(
                        f"MCPSR: uvx is not available. Cannot load server '{server_name}'."
                    )
                    continue

            elif command == "node":
                if not self.node_available:
                    logger.warning(
                        f"MCPSR: node is not available. Cannot load server '{server_name}'."
                    )
                    continue

            # 수정: env 필드에서 환경 변수 참조 처리
            env_dict = server_details.get("env", None)
            if env_dict:
                # env 딕셔너리의 값이 "${VAR_NAME}" 형식이면 환경 변수에서 읽기
                processed_env = {}
                for key, value in env_dict.items():
                    if isinstance(value, str) and value.startswith("${") and value.endswith("}"):
                        # ${VAR_NAME} 형식에서 VAR_NAME 추출
                        env_var_name = value[2:-1]
                        env_value = os.getenv(env_var_name)
                        if env_value:
                            processed_env[key] = env_value
                        else:
                            logger.warning(
                                f"MCPSR: Environment variable '{env_var_name}' not found for server '{server_name}'. "
                                f"Using empty string."
                            )
                            processed_env[key] = ""
                    else:
                        processed_env[key] = value
                env_dict = processed_env
            
            self.servers[server_name] = MCPServer(
                name=server_name,
                command=command,
                args=server_details["args"],
                env=env_dict,
                cwd=server_details.get("cwd", None),
                timeout=server_details.get("timeout", None),
            )
            logger.debug(f"MCPSR: Loaded server: '{server_name}'.")

    def remove_server(self, server_name: str) -> None:
        """Remove a server from the available servers."""
        try:
            self.servers.pop(server_name)
            logger.info(f"MCPSR: Removed server: {server_name}")
        except KeyError:
            logger.warning(f"MCPSR: Server '{server_name}' not found. Cannot remove.")

    def get_server(self, server_name: str) -> Optional[MCPServer]:
        """Get the server by name."""
        return self.servers.get(server_name, None)
