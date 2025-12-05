"""
This module contains the pydantic model for the configurations of
different types of agents.
"""

import os
from pydantic import BaseModel, Field, model_validator
from typing import Dict, ClassVar, Optional, Literal, List
from .i18n import I18nMixin, Description
from .stateless_llm import StatelessLLMConfigs

# ======== Configurations for different Agents ========


class BasicMemoryAgentConfig(I18nMixin, BaseModel):
    """Configuration for the basic memory agent."""

    llm_provider: Literal[
        "stateless_llm_with_template",
        "openai_compatible_llm",
        "claude_llm",
        "llama_cpp_llm",
        "ollama_llm",
        "lmstudio_llm",
        "openai_llm",
        "gemini_llm",
        "zhipu_llm",
        "deepseek_llm",
        "groq_llm",
        "mistral_llm",
    ] = Field(..., alias="llm_provider")

    faster_first_response: Optional[bool] = Field(True, alias="faster_first_response")
    segment_method: Literal["regex", "pysbd"] = Field("pysbd", alias="segment_method")
    use_mcpp: Optional[bool] = Field(False, alias="use_mcpp")
    mcp_enabled_servers: Optional[List[str]] = Field([], alias="mcp_enabled_servers")

    DESCRIPTIONS: ClassVar[Dict[str, Description]] = {
        "llm_provider": Description(
            en="LLM provider to use for this agent",
            zh="Basic Memory Agent 智能体使用的大语言模型选项",
        ),
        "faster_first_response": Description(
            en="Whether to respond as soon as encountering a comma in the first sentence to reduce latency (default: True)",
            zh="是否在第一句回应时遇上逗号就直接生成音频以减少首句延迟（默认：True）",
        ),
        "segment_method": Description(
            en="Method for segmenting sentences: 'regex' or 'pysbd' (default: 'pysbd')",
            zh="分割句子的方法：'regex' 或 'pysbd'（默认：'pysbd'）",
        ),
        "use_mcpp": Description(
            en="Whether to use MCP (Model Context Protocol) for the agent (default: True)",
            zh="是否使用为智能体启用 MCP (Model Context Protocol) Plus（默认：False）",
        ),
        "mcp_enabled_servers": Description(
            en="List of MCP servers to enable for the agent",
            zh="为智能体启用 MCP 服务器列表",
        ),
    }


class Mem0VectorStoreConfig(I18nMixin, BaseModel):
    """Configuration for Mem0 vector store."""

    provider: str = Field(..., alias="provider")
    config: Dict = Field(..., alias="config")

    DESCRIPTIONS: ClassVar[Dict[str, Description]] = {
        "provider": Description(
            en="Vector store provider (e.g., qdrant)", zh="向量存储提供者（如 qdrant）"
        ),
        "config": Description(
            en="Provider-specific configuration", zh="提供者特定配置"
        ),
    }


class Mem0LLMConfig(I18nMixin, BaseModel):
    """Configuration for Mem0 LLM."""

    provider: str = Field(..., alias="provider")
    config: Dict = Field(..., alias="config")

    DESCRIPTIONS: ClassVar[Dict[str, Description]] = {
        "provider": Description(en="LLM provider name", zh="语言模型提供者名称"),
        "config": Description(
            en="Provider-specific configuration", zh="提供者特定配置"
        ),
    }


class Mem0EmbedderConfig(I18nMixin, BaseModel):
    """Configuration for Mem0 embedder."""

    provider: str = Field(..., alias="provider")
    config: Dict = Field(..., alias="config")

    DESCRIPTIONS: ClassVar[Dict[str, Description]] = {
        "provider": Description(en="Embedder provider name", zh="嵌入模型提供者名称"),
        "config": Description(
            en="Provider-specific configuration", zh="提供者特定配置"
        ),
    }


class Mem0Config(I18nMixin, BaseModel):
    """Configuration for Mem0."""

    vector_store: Mem0VectorStoreConfig = Field(..., alias="vector_store")
    llm: Mem0LLMConfig = Field(..., alias="llm")
    embedder: Mem0EmbedderConfig = Field(..., alias="embedder")

    DESCRIPTIONS: ClassVar[Dict[str, Description]] = {
        "vector_store": Description(en="Vector store configuration", zh="向量存储配置"),
        "llm": Description(en="LLM configuration", zh="语言模型配置"),
        "embedder": Description(en="Embedder configuration", zh="嵌入模型配置"),
    }


# =================================


class HumeAIConfig(I18nMixin, BaseModel):
    """Configuration for the Hume AI agent."""

    api_key: str = Field(..., alias="api_key")
    host: str = Field("api.hume.ai", alias="host")
    config_id: Optional[str] = Field(None, alias="config_id")
    idle_timeout: int = Field(15, alias="idle_timeout")

    DESCRIPTIONS: ClassVar[Dict[str, Description]] = {
        "api_key": Description(
            en="API key for Hume AI service", zh="Hume AI 服务的 API 密钥"
        ),
        "host": Description(
            en="Host URL for Hume AI service (default: api.hume.ai)",
            zh="Hume AI 服务的主机地址（默认：api.hume.ai）",
        ),
        "config_id": Description(
            en="Configuration ID for EVI settings", zh="EVI 配置 ID"
        ),
        "idle_timeout": Description(
            en="Idle timeout in seconds before disconnecting (default: 15)",
            zh="空闲超时断开连接的秒数（默认：15）",
        ),
    }


# =================================


class LettaConfig(I18nMixin, BaseModel):
    """Configuration for the Letta agent."""

    host: str = Field("localhost", alias="host")
    port: int = Field(8283, alias="port")
    id: str = Field(..., alias="id")
    faster_first_response: Optional[bool] = Field(True, alias="faster_first_response")
    segment_method: Literal["regex", "pysbd"] = Field("pysbd", alias="segment_method")

    DESCRIPTIONS: ClassVar[Dict[str, Description]] = {
        "host": Description(
            en="Host address for the Letta server", zh="Letta服务器的主机地址"
        ),
        "port": Description(
            en="Port number for the Letta server (default: 8283)",
            zh="Letta服务器的端口号（默认：8283）",
        ),
        "id": Description(
            en="Agent instance ID running on the Letta server",
            zh="指定Letta服务器上运行的Agent实例id",
        ),
    }


class AgentSettings(I18nMixin, BaseModel):
    """Settings for different types of agents."""

    basic_memory_agent: Optional[BasicMemoryAgentConfig] = Field(
        None, alias="basic_memory_agent"
    )
    mem0_agent: Optional[Mem0Config] = Field(None, alias="mem0_agent")
    hume_ai_agent: Optional[HumeAIConfig] = Field(None, alias="hume_ai_agent")
    letta_agent: Optional[LettaConfig] = Field(None, alias="letta_agent")

    DESCRIPTIONS: ClassVar[Dict[str, Description]] = {
        "basic_memory_agent": Description(
            en="Configuration for basic memory agent", zh="基础记忆代理配置"
        ),
        "mem0_agent": Description(en="Configuration for Mem0 agent", zh="Mem0代理配置"),
        "hume_ai_agent": Description(
            en="Configuration for Hume AI agent", zh="Hume AI 代理配置"
        ),
        "letta_agent": Description(
            en="Configuration for Letta agent", zh="Letta 代理配置"
        ),
    }


class AgentConfig(I18nMixin, BaseModel):
    """This class contains all of the configurations related to agent."""

    conversation_agent_choice: Literal[
        "basic_memory_agent", "mem0_agent", "hume_ai_agent", "letta_agent"
    ] = Field(..., alias="conversation_agent_choice")
    agent_settings: AgentSettings = Field(..., alias="agent_settings")
    llm_configs: StatelessLLMConfigs = Field(..., alias="llm_configs")

    @model_validator(mode="before")
    @classmethod
    def load_mcp_from_env(cls, data: dict) -> dict:
        """환경 변수에서 MCP 설정을 로드합니다."""
        # 수정: .env 파일에서 MCP 설정 읽기
        if isinstance(data, dict):
            agent_settings = data.get("agent_settings", {})
            basic_memory_agent = agent_settings.get("basic_memory_agent", {})
            
            # USE_MCPP 환경 변수 확인 (true/false, 1/0, yes/no 등)
            use_mcpp_env = os.getenv("USE_MCPP") or os.getenv("MCP_ENABLED")
            if use_mcpp_env is not None:
                use_mcpp_value = use_mcpp_env.lower() in ("true", "1", "yes", "on")
                # 환경 변수가 있으면 덮어쓰기
                if "agent_settings" not in data:
                    data["agent_settings"] = {}
                if "basic_memory_agent" not in data["agent_settings"]:
                    data["agent_settings"]["basic_memory_agent"] = {}
                data["agent_settings"]["basic_memory_agent"]["use_mcpp"] = use_mcpp_value
            
            # MCP_ENABLED_SERVERS 환경 변수 확인 (쉼표로 구분된 문자열)
            mcp_servers_env = os.getenv("MCP_ENABLED_SERVERS")
            if mcp_servers_env is not None:
                # 쉼표로 구분된 문자열을 리스트로 변환
                servers_list = [s.strip() for s in mcp_servers_env.split(",") if s.strip()]
                # 환경 변수가 있으면 덮어쓰기
                if "agent_settings" not in data:
                    data["agent_settings"] = {}
                if "basic_memory_agent" not in data["agent_settings"]:
                    data["agent_settings"]["basic_memory_agent"] = {}
                data["agent_settings"]["basic_memory_agent"]["mcp_enabled_servers"] = servers_list
        
        return data

    DESCRIPTIONS: ClassVar[Dict[str, Description]] = {
        "conversation_agent_choice": Description(
            en="Type of conversation agent to use", zh="要使用的对话代理类型"
        ),
        "agent_settings": Description(
            en="Settings for different agent types", zh="不同代理类型的设置"
        ),
        "llm_configs": Description(
            en="Pool of LLM provider configurations", zh="语言模型提供者配置池"
        ),
        "faster_first_response": Description(
            en="Whether to respond as soon as encountering a comma in the first sentence to reduce latency (default: True)",
            zh="是否在第一句回应时遇上逗号就直接生成音频以减少首句延迟（默认：True）",
        ),
        "segment_method": Description(
            en="Method for segmenting sentences: 'regex' or 'pysbd' (default: 'pysbd')",
            zh="分割句子的方法：'regex' 或 'pysbd'（默认：'pysbd'）",
        ),
    }
