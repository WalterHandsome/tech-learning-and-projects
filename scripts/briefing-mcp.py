#!/usr/bin/env python3
"""
简报工具 MCP Server — FastMCP 实现。
通过 uv run --with mcp 启动，零手动安装。
"""

import json
import os
import importlib.util

# 动态导入 briefing-tools.py
_tools_path = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "briefing-tools.py"
)
_spec = importlib.util.spec_from_file_location("briefing_tools", _tools_path)
bt = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(bt)

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("briefing-tools")


@mcp.tool()
def briefing_collect(topic: str) -> str:
    """采集指定主题的原始素材（RSS + Hacker News API），返回 JSON 格式的条目列表。

    Args:
        topic: 简报主题，可选 ai-agent / china-tech / global-tech
    """
    items = bt.collect_topic(topic)
    return json.dumps({
        "topic": topic,
        "collected_at": bt.now_str(),
        "total": len(items),
        "items": items,
    }, ensure_ascii=False, indent=2)


@mcp.tool()
def briefing_dedup(topic: str, items_json: str) -> str:
    """对采集结果去重：URL hash + 标题相似度 + 跨简报去重。

    Args:
        topic: 简报主题，可选 ai-agent / china-tech / global-tech
        items_json: 待去重的条目列表 JSON 字符串（来自 briefing_collect）
    """
    raw = json.loads(items_json)
    items = raw.get("items", raw) if isinstance(raw, dict) else raw
    kept, removed = bt.dedup_items(items, topic)
    return json.dumps({
        "topic": topic,
        "kept": len(kept),
        "removed": len(removed),
        "items": kept,
        "removed_items": removed,
    }, ensure_ascii=False, indent=2)


@mcp.tool()
def briefing_status() -> str:
    """查看三个简报主题的采集状态：最近采集日期、距今天数、本周/本月统计。"""
    return bt.format_status(bt.get_status())


@mcp.tool()
def briefing_index(topic: str = "all") -> str:
    """同步指定主题（或全部）的 README.md 索引。

    Args:
        topic: 要同步的主题，默认 all。可选 ai-agent / china-tech / global-tech / all
    """
    topics = [topic] if topic != "all" else ["ai-agent", "china-tech", "global-tech"]
    lines = []
    for t in topics:
        bt.sync_readme_index(t)
        lines.append(f"✅ {t} 索引已同步")
    return "\n".join(lines)


if __name__ == "__main__":
    mcp.run()
