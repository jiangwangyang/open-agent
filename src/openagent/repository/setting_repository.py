import json
import os
import pathlib
from typing import TypedDict

import anyio
from fastapi import APIRouter

router = APIRouter()
SETTING_FILE = str(pathlib.Path.home() / ".openagent" / "settings.json")


# 模型提供商配置
class ModelProvider(TypedDict):
    base_url: str
    api_key: str
    models: list[str]


# MCP 服务配置
class McpServer(TypedDict, total=False):
    type: str
    url: str
    headers: dict[str, str]
    command: str
    args: list[str]
    description: str


# 全局配置
class Setting(TypedDict, total=False):
    model_provider: str
    model: str
    model_providers: dict[str, ModelProvider]
    mcp_servers: dict[str, McpServer]


async def init_settings():
    # 查询现有配置
    settings_file = anyio.Path(SETTING_FILE)
    content = await settings_file.read_text(encoding="utf-8") if await settings_file.exists() else ""
    settings = json.loads(content) if content else Setting()
    model_providers = settings.get("model_providers", {})
    # 增加 DeepSeek
    if "deepseek" not in model_providers and os.getenv("DEEPSEEK_API_KEY", ""):
        model_providers["deepseek"] = ModelProvider(
            base_url="https://api.deepseek.com/anthropic",
            api_key=os.getenv("DEEPSEEK_API_KEY", ""),
            models=[
                "deepseek-v4-pro",
                "deepseek-v4-flash",
            ]
        )
    # 增加 Zhipu
    if "bigmodel" not in model_providers and os.getenv("BIGMODEL_API_KEY", ""):
        model_providers["bigmodel"] = ModelProvider(
            base_url="https://open.bigmodel.cn/api/anthropic",
            api_key=os.getenv("BIGMODEL_API_KEY", ""),
            models=[
                "glm-5.2",
                "glm-5.1",
                "glm-5-turbo",
                "glm-5",
                "glm-4.7",
                "glm-4.7-flash",
            ]
        )
    # 增加 Kimi
    if "moonshot" not in model_providers and os.getenv("MOONSHOT_API_KEY", ""):
        model_providers["moonshot"] = ModelProvider(
            base_url="https://api.moonshot.cn/anthropic",
            api_key=os.getenv("MOONSHOT_API_KEY", ""),
            models=[
                "kimi-k3",
                "kimi-k2.7-code",
                "kimi-k2.6",
                "kimi-k2.5",
            ]
        )
    if "kimi" not in model_providers and os.getenv("KIMI_API_KEY", ""):
        model_providers["kimi"] = ModelProvider(
            base_url="https://api.kimi.com/coding",
            api_key=os.getenv("KIMI_API_KEY", ""),
            models=[
                "kimi-k3",
                "kimi-k2.7-code",
                "kimi-k2.6",
                "kimi-k2.5",
            ]
        )
    # 增加 MiniMax
    if "minimaxi" not in model_providers and os.getenv("MINIMAXI_API_KEY", ""):
        model_providers["minimaxi"] = ModelProvider(
            base_url="https://api.minimaxi.com/anthropic",
            api_key=os.getenv("MINIMAXI_API_KEY", ""),
            models=[
                "MiniMax-M3",
                "MiniMax-M2.7",
            ]
        )
    if "minimax" not in model_providers and os.getenv("MINIMAX_API_KEY", ""):
        model_providers["minimax"] = ModelProvider(
            base_url="https://api.minimax.io/anthropic",
            api_key=os.getenv("MINIMAX_API_KEY", ""),
            models=[
                "MiniMax-M3",
                "MiniMax-M2.7",
            ]
        )
    # 保存配置
    if not "model_provider" in settings and model_providers:
        settings["model_provider"] = next(iter(model_providers))
    if not "model" in settings and "model_provider" in settings:
        settings["model"] = model_providers[settings["model_provider"]]["models"][0]
    settings["model_providers"] = model_providers
    await settings_file.parent.mkdir(parents=True, exist_ok=True)
    await settings_file.write_text(json.dumps(settings, ensure_ascii=False, indent=4), encoding="utf-8")


async def get_settings() -> Setting:
    settings_file = anyio.Path(SETTING_FILE)
    content = await settings_file.read_text(encoding="utf-8") if await settings_file.exists() else ""
    return json.loads(content) if content else Setting()


async def save_settings(content: Setting):
    settings_file = anyio.Path(SETTING_FILE)
    await settings_file.parent.mkdir(parents=True, exist_ok=True)
    file_content = json.dumps(content, ensure_ascii=False, indent=4)
    await settings_file.write_text(file_content, encoding="utf-8")
