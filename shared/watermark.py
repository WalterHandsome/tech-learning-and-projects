"""
隐形水印工具 — 在文本中嵌入/提取不可见的作者标识

使用零宽字符将作者信息编码为二进制，嵌入文本中，肉眼完全不可见。

用法:
    from shared.watermark import embed_watermark, extract_watermark

    marked = embed_watermark("你的文章内容", "Walter Wang")
    author = extract_watermark(marked)  # -> "Walter Wang"
"""

__author__ = "Walter Wang"

# 零宽字符映射
_ZERO = "\u200b"  # 零宽空格 -> 0
_ONE = "\u200c"   # 零宽非连接符 -> 1
_SEP = "\u200d"   # 零宽连接符 -> 分隔符
_MARKER = f"{_SEP}{_SEP}"  # 双分隔符作为水印边界标记


def _text_to_zwc(text: str) -> str:
    """将文本转为零宽字符序列"""
    binary = "".join(format(ord(c), "016b") for c in text)
    return "".join(_ZERO if b == "0" else _ONE for b in binary)


def _zwc_to_text(zwc: str) -> str:
    """将零宽字符序列还原为文本"""
    binary = zwc.replace(_ZERO, "0").replace(_ONE, "1")
    chars = []
    for i in range(0, len(binary) - 15, 16):
        code = int(binary[i : i + 16], 2)
        if code > 0:
            chars.append(chr(code))
    return "".join(chars)


def embed_watermark(content: str, author: str) -> str:
    """在文本中嵌入隐形作者水印

    水印被插入到第一个换行符之后（通常是标题行后面），
    如果没有换行符则追加到末尾。

    Args:
        content: 原始文本内容
        author: 作者标识字符串

    Returns:
        嵌入水印后的文本（外观与原文完全相同）
    """
    watermark = _MARKER + _text_to_zwc(author) + _MARKER

    pos = content.find("\n")
    if pos == -1:
        return content + watermark
    return content[: pos + 1] + watermark + content[pos + 1 :]


def extract_watermark(content: str) -> str:
    """从文本中提取隐藏的作者水印

    Args:
        content: 可能包含水印的文本

    Returns:
        作者标识字符串，未找到水印时返回空字符串
    """
    start = content.find(_MARKER)
    if start == -1:
        return ""
    end = content.find(_MARKER, start + len(_MARKER))
    if end == -1:
        return ""
    zwc_data = content[start + len(_MARKER) : end]
    return _zwc_to_text(zwc_data)


def has_watermark(content: str) -> bool:
    """检测文本中是否包含水印"""
    return _MARKER in content


def strip_watermark(content: str) -> str:
    """移除文本中的水印（仅供调试用）"""
    start = content.find(_MARKER)
    if start == -1:
        return content
    end = content.find(_MARKER, start + len(_MARKER))
    if end == -1:
        return content
    return content[:start] + content[end + len(_MARKER) :]
