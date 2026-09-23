import importlib
import logging
from typing import Dict, Any

from .config import settings
from .logger import get_logger

logger = get_logger(__name__)

# Mapping of mode -> intent -> tool module and function name
ROUTING_TABLE = {
    "Developer": {
        "analyze_code": ("tools.github_tools", "analyze_code"),
        "generate_patch": ("tools.github_tools", "generate_patch"),
    },
    "DevOps": {
        "server_health": ("tools.server_tools", "server_health"),
        "restart_service": ("tools.server_tools", "restart_service"),
    },
    "Content": {
        "blog_status": ("tools.blog_tools", "blog_status"),
        "publish_blog_post": ("tools.blog_tools", "publish_blog_post"),
        "threads_status": ("tools.threads_tools", "threads_status"),
        "generate_card_news": ("tools.card_tools", "generate_card_news"),
    },
    "Manager": {
        "plan_task": ("tools.manager_tools", "plan_task"),  # placeholder
    },
}

def route_request(payload: Dict[str, Any]) -> Any:
    mode = payload.get("mode")
    intent = payload.get("intent")
    params = payload.get("parameters", {})
    logger.info(f"Routing request: mode={mode}, intent={intent}, params={params}")
    if not mode or not intent:
        raise ValueError("Payload must include 'mode' and 'intent'")
    mode_table = ROUTING_TABLE.get(mode)
    if not mode_table:
        raise ValueError(f"Unsupported mode: {mode}")
    tool_info = mode_table.get(intent)
    if not tool_info:
        raise ValueError(f"Unsupported intent '{intent}' for mode '{mode}'")
    module_path, func_name = tool_info
    module = importlib.import_module(module_path, package=__package__)
    func = getattr(module, func_name)
    logger.debug(f"Invoking {module_path}.{func_name} with params={params}")
    return func(**params)
