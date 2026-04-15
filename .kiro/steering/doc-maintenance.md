---
inclusion: fileMatch
fileMatchPattern: "learning-notes/**/*.md"
---

# 文档维护规范

## 文档格式标准

### 文件头部
每个文档必须包含：
```markdown
# 标题

> Author: Walter Wang
```

### 更新标记
对现有文档做增量更新时，在新增内容前标注：
```markdown
> 🔄 更新于 YYYY-MM-DD
```

对于不确定的内容，标注待确认：
```markdown
> ⚠️ 待确认：xxx
```

### 内容时效性标记
文档中涉及版本号、API、工具时，使用以下格式方便后续检查：
```markdown
<!-- version-check: LangGraph 1.0.10, checked 2026-04-15 -->
```

### 代码块规范
- 所有代码块必须标注语言（python、typescript、bash、yaml 等）
- 代码注释使用中文
- import 路径使用完整路径

### 内部链接
引用其他文档时使用相对路径：
```markdown
详见 → [MCP模型上下文协议](../02-Agent协议/02-MCP模型上下文协议.md)
```

### ASCII 图表
使用等宽字符绘制，确保中英文混排时对齐。

## 内容质量标准

1. 技术准确性：版本号、API、安装命令必须与官方文档一致
2. 来源引用：关键信息需标注来源链接
3. 增量更新：不删除旧内容，标注为历史版本
4. 中文优先：正文使用中文，技术术语可用英文
