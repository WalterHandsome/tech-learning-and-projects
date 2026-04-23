#!/usr/bin/env python3
"""
简报工具集 — 为 Kiro hooks 提供确定性的采集、去重、状态查询能力。

子命令:
  collect   多源采集原始素材，输出 JSON
  dedup     对采集结果去重（URL hash + 标题相似度 + 跨简报）
  status    输出简报采集状态面板
  index     同步 README 索引

设计原则:
  - 纯标准库，零外部依赖
  - 确定性操作（采集、去重、文件管理）由脚本完成
  - 智能判断（评分、摘要、趋势）留给 Kiro agent

使用方式:
  python3 scripts/briefing-tools.py collect --topic ai-agent
  python3 scripts/briefing-tools.py dedup --input raw.json --topic ai-agent
  python3 scripts/briefing-tools.py status
  python3 scripts/briefing-tools.py index --topic ai-agent
"""

import argparse
import hashlib
import json
import re
import sys
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from pathlib import Path

# ============================================
# 配置
# ============================================

BASE_DIR = Path(__file__).resolve().parent.parent / "learning-notes" / "briefings"
INDEX_FILE = BASE_DIR / ".dedup-index.json"

# RSS 源配置（按主题分组）
RSS_SOURCES = {
    "ai-agent": [
        {"name": "LangChain Blog", "url": "https://blog.langchain.dev/feed/"},
        {"name": "Anthropic Research", "url": "https://www.anthropic.com/feed.xml"},
        {"name": "OpenAI Blog", "url": "https://openai.com/blog/rss.xml"},
        {"name": "Hacker News AI", "url": "https://hnrss.org/newest?q=AI+agent+OR+MCP+OR+LLM&points=30"},
        {"name": "arXiv AI", "url": "https://rss.arxiv.org/rss/cs.AI"},
    ],
    "china-tech": [
        {"name": "36氪", "url": "https://36kr.com/feed"},
        {"name": "InfoQ CN", "url": "https://www.infoq.cn/feed"},
    ],
    "global-tech": [
        {"name": "Hacker News Top", "url": "https://hnrss.org/frontpage?count=30"},
        {"name": "TechCrunch", "url": "https://techcrunch.com/feed/"},
        {"name": "The Verge", "url": "https://www.theverge.com/rss/index.xml"},
    ],
}

# Hacker News API 关键词
HN_KEYWORDS = {
    "ai-agent": [
        "AI agent", "MCP", "LangGraph", "CrewAI", "Claude",
        "LLM", "RAG", "function calling", "context engineering",
    ],
    "china-tech": ["DeepSeek", "Qwen", "Baidu AI", "China AI"],
    "global-tech": [
        "Rust", "TypeScript", "Kubernetes", "AWS", "security vulnerability",
    ],
}


# ============================================
# 工具函数
# ============================================

def url_hash(url: str) -> str:
    """URL 的短 hash，用于去重索引"""
    return hashlib.md5(url.encode()).hexdigest()[:12]


def title_similarity(a: str, b: str) -> float:
    """基于词集合的 Jaccard 相似度"""
    clean_fn = lambda s: set(re.sub(r"[^\w\s]", "", s.lower()).split())
    sa, sb = clean_fn(a), clean_fn(b)
    if not sa or not sb:
        return 0.0
    return len(sa & sb) / len(sa | sb)


def today_str() -> str:
    return datetime.now().strftime("%Y-%m-%d")


def now_str() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M")


def topic_dir(topic: str) -> Path:
    """获取主题的当日输出目录"""
    now = datetime.now()
    return BASE_DIR / topic / str(now.year) / f"{now.month:02d}"


def http_get(url: str, timeout: int = 10) -> str | None:
    """标准库 HTTP GET，带错误处理"""
    try:
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "BriefingTools/1.0 (Walter's Knowledge Base)"},
        )
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.read().decode("utf-8", errors="replace")
    except (urllib.error.URLError, TimeoutError, OSError) as e:
        log_error(f"HTTP GET 失败: {url} — {e}")
        return None


def log_error(msg: str):
    """追加错误到 .errors.log"""
    log_file = BASE_DIR / ".errors.log"
    log_file.parent.mkdir(parents=True, exist_ok=True)
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(f"[{now_str()}] {msg}\n")
    print(f"  ⚠️  {msg}", file=sys.stderr)


# ============================================
# 去重索引管理
# ============================================

def load_index() -> dict:
    if INDEX_FILE.exists():
        with open(INDEX_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"items": {}, "updated": ""}


def save_index(index: dict):
    index["updated"] = now_str()
    INDEX_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(INDEX_FILE, "w", encoding="utf-8") as f:
        json.dump(index, f, ensure_ascii=False, indent=2)


def cleanup_index(index: dict, days: int = 30) -> dict:
    cutoff = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
    index["items"] = {
        k: v for k, v in index["items"].items()
        if v.get("date", "") >= cutoff
    }
    return index


# ============================================
# RSS 解析（纯标准库）
# ============================================

def parse_rss(xml_text: str, source_name: str) -> list[dict]:
    """用标准库解析 RSS/Atom feed"""
    items = []
    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError as e:
        log_error(f"RSS 解析失败 ({source_name}): {e}")
        return []

    ns = {"atom": "http://www.w3.org/2005/Atom"}

    # RSS 2.0
    for item in root.iter("item"):
        title = _text(item, "title") or ""
        link = _text(item, "link") or ""
        pub_date = _text(item, "pubDate") or ""
        description = _text(item, "description") or ""
        if title and link:
            items.append({
                "title": title.strip(),
                "url": link.strip(),
                "published": pub_date.strip(),
                "description": _clean_html(description)[:500],
                "source": source_name,
            })

    # Atom
    if not items:
        for entry in root.iter(f"{{{ns['atom']}}}entry"):
            title = _text(entry, f"{{{ns['atom']}}}title") or ""
            link_el = entry.find(f"{{{ns['atom']}}}link[@rel='alternate']")
            if link_el is None:
                link_el = entry.find(f"{{{ns['atom']}}}link")
            link = link_el.get("href", "") if link_el is not None else ""
            pub_date = (
                _text(entry, f"{{{ns['atom']}}}published")
                or _text(entry, f"{{{ns['atom']}}}updated")
                or ""
            )
            summary = _text(entry, f"{{{ns['atom']}}}summary") or ""
            if title and link:
                items.append({
                    "title": title.strip(),
                    "url": link.strip(),
                    "published": pub_date.strip(),
                    "description": _clean_html(summary)[:500],
                    "source": source_name,
                })

    return items


def _text(el, tag, ns=None):
    child = el.find(tag, ns) if ns else el.find(tag)
    return child.text if child is not None and child.text else None


def _clean_html(text: str) -> str:
    return re.sub(r"<[^>]+>", "", text).strip()


# ============================================
# Hacker News API 采集
# ============================================

def fetch_hn_top(keywords: list[str], limit: int = 15) -> list[dict]:
    items = []
    data = http_get("https://hacker-news.firebaseio.com/v0/topstories.json")
    if not data:
        return []
    try:
        story_ids = json.loads(data)[:80]
    except json.JSONDecodeError:
        return []

    kw_lower = [k.lower() for k in keywords]
    for sid in story_ids:
        if len(items) >= limit:
            break
        story_data = http_get(
            f"https://hacker-news.firebaseio.com/v0/item/{sid}.json"
        )
        if not story_data:
            continue
        try:
            story = json.loads(story_data)
        except json.JSONDecodeError:
            continue
        title = story.get("title", "")
        if not title:
            continue
        if any(kw in title.lower() for kw in kw_lower):
            items.append({
                "title": title,
                "url": story.get(
                    "url",
                    f"https://news.ycombinator.com/item?id={sid}",
                ),
                "published": "",
                "description": (
                    f"Score: {story.get('score', 0)}, "
                    f"Comments: {story.get('descendants', 0)}"
                ),
                "source": "Hacker News",
                "hn_score": story.get("score", 0),
            })
    return items


# ============================================
# 采集主入口
# ============================================

def collect_topic(topic: str) -> list[dict]:
    all_items = []

    # RSS 源
    for src in RSS_SOURCES.get(topic, []):
        print(f"  📡 采集 {src['name']}...")
        xml_text = http_get(src["url"], timeout=15)
        if xml_text:
            items = parse_rss(xml_text, src["name"])
            all_items.extend(items[:10])
            print(f"     → {len(items)} 条")
        else:
            print(f"     → 失败")

    # Hacker News API
    hn_kw = HN_KEYWORDS.get(topic, [])
    if hn_kw:
        print(f"  📡 采集 Hacker News (关键词: {len(hn_kw)} 个)...")
        hn_items = fetch_hn_top(hn_kw)
        all_items.extend(hn_items)
        print(f"     → {len(hn_items)} 条")

    return all_items


# ============================================
# 去重
# ============================================

def dedup_items(
    items: list[dict], topic: str
) -> tuple[list[dict], list[dict]]:
    """
    去重:
    1. URL hash 精确去重（跨天）
    2. 标题相似度 > 0.6（同一事件不同报道）
    3. 跨简报去重（今天其他主题已收录的）
    """
    index = cleanup_index(load_index())

    # 加载今天其他主题的标题
    other_titles = []
    for ot in ["ai-agent", "china-tech", "global-tech"]:
        if ot == topic:
            continue
        today_file = topic_dir(ot) / f"{today_str()}.md"
        if today_file.exists():
            content = today_file.read_text(encoding="utf-8")
            other_titles.extend(
                re.findall(r"^### (.+)$", content, re.MULTILINE)
            )

    kept, removed, seen_titles = [], [], []

    for item in items:
        uh = url_hash(item["url"])
        reason = None

        # URL 精确去重
        if uh in index["items"]:
            reason = (
                f"URL 重复 (首次: {index['items'][uh].get('date', '?')})"
            )

        # 标题相似度（历史索引）
        if not reason:
            for entry in index["items"].values():
                if title_similarity(item["title"], entry.get("title", "")) > 0.6:
                    reason = f"标题相似: {entry['title'][:40]}..."
                    break

        # 批次内去重
        if not reason:
            for st in seen_titles:
                if title_similarity(item["title"], st) > 0.6:
                    reason = f"批次内重复: {st[:40]}..."
                    break

        # 跨简报去重
        if not reason:
            for ot in other_titles:
                if title_similarity(item["title"], ot) > 0.5:
                    reason = f"跨简报重复: {ot[:40]}..."
                    break

        if reason:
            item["dedup_reason"] = reason
            removed.append(item)
        else:
            kept.append(item)
            seen_titles.append(item["title"])
            index["items"][uh] = {
                "title": item["title"],
                "source": item.get("source", ""),
                "topic": topic,
                "date": today_str(),
            }

    save_index(index)
    return kept, removed


# ============================================
# 状态面板
# ============================================

def get_status() -> dict:
    today = datetime.now()
    report = {"date": today_str(), "topics": {}}

    for topic in ["ai-agent", "china-tech", "global-tech"]:
        topic_base = BASE_DIR / topic
        if not topic_base.exists():
            report["topics"][topic] = {
                "status": "🆕", "latest": None,
                "total": 0, "this_week": 0, "this_month": 0,
            }
            continue

        md_files = sorted(
            [f for f in topic_base.rglob("*.md") if f.name != "README.md"],
            reverse=True,
        )
        dates = []
        for f in md_files:
            match = re.match(r"(\d{4}-\d{2}-\d{2})", f.stem)
            if match:
                dates.append(match.group(1))

        latest = dates[0] if dates else None
        days_ago = None
        status = "🆕"
        if latest:
            try:
                days_ago = (today - datetime.strptime(latest, "%Y-%m-%d")).days
                status = "✅" if days_ago == 0 else ("⚠️" if days_ago == 1 else "❌")
            except ValueError:
                pass

        week_start = (today - timedelta(days=today.weekday())).strftime("%Y-%m-%d")
        month_start = today.strftime("%Y-%m-01")

        report["topics"][topic] = {
            "status": status,
            "latest": latest,
            "days_ago": days_ago,
            "total": len(dates),
            "this_week": sum(1 for d in dates if d >= week_start),
            "this_month": sum(1 for d in dates if d >= month_start),
        }

    if INDEX_FILE.exists():
        idx = load_index()
        report["index_size"] = len(idx.get("items", {}))
        report["index_updated"] = idx.get("updated", "")
    else:
        report["index_size"] = 0
        report["index_updated"] = "未创建"

    return report


def format_status(report: dict) -> str:
    names = {"ai-agent": "AI Agent", "china-tech": "国内科技", "global-tech": "国际科技"}
    lines = [f"## 📊 简报采集状态 — {report['date']}\n"]
    lines.append("| 主题 | 最近采集 | 距今 | 状态 | 本周/本月/总计 |")
    lines.append("|------|----------|------|------|---------------|")
    for topic, info in report["topics"].items():
        n = names.get(topic, topic)
        latest = info["latest"] or "从未采集"
        days = f"{info['days_ago']} 天" if info["days_ago"] is not None else "-"
        counts = f"{info['this_week']}/{info['this_month']}/{info['total']}"
        lines.append(f"| {n} | {latest} | {days} | {info['status']} | {counts} |")
    lines.append(f"\n去重索引: {report['index_size']} 条 (更新于 {report['index_updated']})")
    lines.append("\n### 💡 建议")
    for topic, info in report["topics"].items():
        n = names.get(topic, topic)
        if info["status"] in ("❌", "🆕"):
            lines.append(f"- 🔴 **{n}** 需要采集")
        elif info["status"] == "⚠️":
            lines.append(f"- 🟡 **{n}** 建议今天更新")
    return "\n".join(lines)


# ============================================
# 索引同步
# ============================================

def sync_readme_index(topic: str):
    topic_base = BASE_DIR / topic
    readme = topic_base / "README.md"
    if not topic_base.exists():
        print(f"  目录不存在: {topic_base}")
        return

    entries = []
    for year_dir in sorted(topic_base.iterdir(), reverse=True):
        if not year_dir.is_dir() or year_dir.name.startswith("."):
            continue
        for month_dir in sorted(year_dir.iterdir(), reverse=True):
            if not month_dir.is_dir():
                continue
            for md_file in sorted(month_dir.iterdir(), reverse=True):
                if md_file.suffix == ".md" and md_file.name != "README.md":
                    rel = md_file.relative_to(topic_base)
                    entries.append({
                        "date": md_file.stem,
                        "path": str(rel),
                        "is_weekly": "weekly" in md_file.stem.lower(),
                    })

    names = {
        "ai-agent": "AI Agent 简报",
        "china-tech": "国内科技简报",
        "global-tech": "国际科技简报",
    }
    lines = [
        f"# 📰 {names.get(topic, topic)}",
        "",
        f"> 共 {len(entries)} 篇 | 最近更新: {entries[0]['date'] if entries else '无'}",
        "",
        "| 日期 | 类型 | 链接 |",
        "|------|------|------|",
    ]
    for e in entries:
        t = "📅 周报" if e["is_weekly"] else "📰 日报"
        lines.append(f"| {e['date']} | {t} | [{e['date']}]({e['path']}) |")

    readme.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"  ✅ 已更新 {readme} ({len(entries)} 条)")


# ============================================
# CLI
# ============================================

def cmd_collect(args):
    print(f"📡 开始采集: {args.topic}")
    items = collect_topic(args.topic)
    print(f"\n📊 采集完成: {len(items)} 条原始素材")
    output = {
        "topic": args.topic,
        "collected_at": now_str(),
        "total": len(items),
        "items": items,
    }
    if args.output:
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
        print(f"💾 已保存到: {args.output}")
    else:
        print(json.dumps(output, ensure_ascii=False, indent=2))


def cmd_dedup(args):
    if args.input:
        with open(args.input, "r", encoding="utf-8") as f:
            data = json.load(f)
    else:
        data = json.load(sys.stdin)
    items = data.get("items", [])
    print(f"🔍 去重: {len(items)} 条输入 (主题: {args.topic})")
    kept, removed = dedup_items(items, args.topic)
    print(f"  ✅ 保留: {len(kept)} 条")
    print(f"  ❌ 去重: {len(removed)} 条")
    if removed:
        print("\n  去重详情:")
        for item in removed:
            print(f"    - {item['title'][:50]}... → {item.get('dedup_reason', '?')}")
    output = {
        "topic": args.topic,
        "deduped_at": now_str(),
        "kept": len(kept),
        "removed": len(removed),
        "items": kept,
        "removed_items": removed,
    }
    if args.output:
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
        print(f"💾 已保存到: {args.output}")
    else:
        print(json.dumps(output, ensure_ascii=False, indent=2))


def cmd_status(args):
    report = get_status()
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(format_status(report))


def cmd_index(args):
    topics = (
        [args.topic]
        if args.topic != "all"
        else ["ai-agent", "china-tech", "global-tech"]
    )
    for t in topics:
        print(f"📋 同步索引: {t}")
        sync_readme_index(t)

    # 顶层 README
    names = {
        "ai-agent": "AI Agent 简报",
        "china-tech": "国内科技简报",
        "global-tech": "国际科技简报",
    }
    lines = ["# 📰 简报中心", "", "| 主题 | 目录 |", "|------|------|"]
    for t in ["ai-agent", "china-tech", "global-tech"]:
        lines.append(f"| {names[t]} | [{t}/]({t}/) |")
    (BASE_DIR / "README.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"  ✅ 已更新顶层 README")


def main():
    parser = argparse.ArgumentParser(description="简报工具集")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("collect", help="多源采集原始素材")
    p.add_argument("--topic", required=True, choices=["ai-agent", "china-tech", "global-tech"])
    p.add_argument("--output", "-o")
    p.set_defaults(func=cmd_collect)

    p = sub.add_parser("dedup", help="对采集结果去重")
    p.add_argument("--topic", required=True, choices=["ai-agent", "china-tech", "global-tech"])
    p.add_argument("--input", "-i")
    p.add_argument("--output", "-o")
    p.set_defaults(func=cmd_dedup)

    p = sub.add_parser("status", help="简报采集状态面板")
    p.add_argument("--json", action="store_true")
    p.set_defaults(func=cmd_status)

    p = sub.add_parser("index", help="同步 README 索引")
    p.add_argument("--topic", default="all", choices=["ai-agent", "china-tech", "global-tech", "all"])
    p.set_defaults(func=cmd_index)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
