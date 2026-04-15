#!/usr/bin/env python3
"""水印命令行工具 — 嵌入、提取、检测文件中的隐形作者水印

用法:
    # 单文件操作
    python -m shared.watermark_cli embed  -f article.md -a "Walter Wang"
    python -m shared.watermark_cli check  -f article.md
    python -m shared.watermark_cli strip  -f article.md

    # 批量操作（递归处理目录下所有 .md 文件）
    python -m shared.watermark_cli batch-embed -d learning-notes/ -a "Walter Wang"
    python -m shared.watermark_cli batch-check -d learning-notes/
"""

import argparse
import sys
from pathlib import Path

from shared.watermark import embed_watermark, extract_watermark, has_watermark, strip_watermark


def _find_md_files(directory: Path) -> list[Path]:
    """递归查找目录下所有 .md 文件"""
    return sorted(directory.rglob("*.md"))


def cmd_embed(args):
    path = Path(args.file)
    content = path.read_text(encoding="utf-8")
    if has_watermark(content):
        print(f"⚠️  文件已包含水印（作者: {extract_watermark(content)}），跳过")
        return
    result = embed_watermark(content, args.author)
    path.write_text(result, encoding="utf-8")
    print(f"✅ 已为 {path.name} 嵌入隐形水印（作者: {args.author}）")


def cmd_check(args):
    path = Path(args.file)
    content = path.read_text(encoding="utf-8")
    author = extract_watermark(content)
    if author:
        print(f"✅ 检测到隐形水印 — 原始作者: {author}")
    else:
        print("❌ 未检测到隐形水印")


def cmd_strip(args):
    path = Path(args.file)
    content = path.read_text(encoding="utf-8")
    if not has_watermark(content):
        print("文件中没有水印")
        return
    result = strip_watermark(content)
    path.write_text(result, encoding="utf-8")
    print(f"✅ 已移除 {path.name} 中的水印")


def cmd_batch_embed(args):
    directory = Path(args.dir)
    if not directory.is_dir():
        print(f"❌ 目录不存在: {directory}")
        return
    files = _find_md_files(directory)
    if not files:
        print("未找到 .md 文件")
        return

    embedded, skipped = 0, 0
    for f in files:
        content = f.read_text(encoding="utf-8")
        if has_watermark(content):
            skipped += 1
            continue
        result = embed_watermark(content, args.author)
        f.write_text(result, encoding="utf-8")
        embedded += 1
        print(f"  ✅ {f.relative_to(directory)}")

    print(f"\n完成: {embedded} 个文件已嵌入水印, {skipped} 个已有水印跳过")


def cmd_batch_check(args):
    directory = Path(args.dir)
    if not directory.is_dir():
        print(f"❌ 目录不存在: {directory}")
        return
    files = _find_md_files(directory)
    if not files:
        print("未找到 .md 文件")
        return

    found, missing = 0, 0
    for f in files:
        content = f.read_text(encoding="utf-8")
        author = extract_watermark(content)
        rel = f.relative_to(directory)
        if author:
            print(f"  ✅ {rel}  →  作者: {author}")
            found += 1
        else:
            print(f"  ❌ {rel}  →  无水印")
            missing += 1

    print(f"\n统计: {found} 个有水印, {missing} 个无水印")


def main():
    parser = argparse.ArgumentParser(description="隐形水印工具")
    sub = parser.add_subparsers(dest="command", required=True)

    # 单文件命令
    p_embed = sub.add_parser("embed", help="嵌入水印（单文件）")
    p_embed.add_argument("-f", "--file", required=True, help="目标文件路径")
    p_embed.add_argument("-a", "--author", default="Walter Wang", help="作者名")

    p_check = sub.add_parser("check", help="检测水印（单文件）")
    p_check.add_argument("-f", "--file", required=True, help="目标文件路径")

    p_strip = sub.add_parser("strip", help="移除水印（调试用）")
    p_strip.add_argument("-f", "--file", required=True, help="目标文件路径")

    # 批量命令
    p_batch_embed = sub.add_parser("batch-embed", help="批量嵌入水印（递归处理目录）")
    p_batch_embed.add_argument("-d", "--dir", required=True, help="目标目录路径")
    p_batch_embed.add_argument("-a", "--author", default="Walter Wang", help="作者名")

    p_batch_check = sub.add_parser("batch-check", help="批量检测水印（递归处理目录）")
    p_batch_check.add_argument("-d", "--dir", required=True, help="目标目录路径")

    args = parser.parse_args()
    cmds = {
        "embed": cmd_embed,
        "check": cmd_check,
        "strip": cmd_strip,
        "batch-embed": cmd_batch_embed,
        "batch-check": cmd_batch_check,
    }
    cmds[args.command](args)


if __name__ == "__main__":
    main()
