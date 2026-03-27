# 代码助手 Agent
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. 系统架构

```
┌─────────────────────────────────────────────────────┐
│                  代码助手 Agent                       │
├──────────┬──────────┬──────────┬───────────────────┤
│ 代码理解  │ 代码生成  │ 代码审查  │ 测试生成          │
├──────────┼──────────┼──────────┼───────────────────┤
│ 仓库索引  │ 需求→代码 │ 质量检查  │ 单测/集成测试     │
│ 符号分析  │ Bug修复  │ 安全扫描  │ 边界用例          │
│ 依赖分析  │ 重构建议  │ 性能建议  │ Mock 生成         │
└──────────┴──────────┴──────────┴───────────────────┘
         ↕ MCP 工具集成（文件系统、Git、终端）↕
```

## 2. 仓库理解 Agent

```python
from mcp.server.fastmcp import FastMCP
import ast
from pathlib import Path

mcp = FastMCP("code-assistant")

@mcp.tool()
def analyze_repository(repo_path: str) -> dict:
    """分析代码仓库结构"""
    structure = {"files": [], "languages": {}, "total_lines": 0}
    for file in Path(repo_path).rglob("*"):
        if file.is_file() and file.suffix in [".py", ".js", ".ts", ".java"]:
            lines = len(file.read_text(errors="ignore").splitlines())
            structure["files"].append({"path": str(file), "lines": lines})
            lang = file.suffix
            structure["languages"][lang] = structure["languages"].get(lang, 0) + lines
            structure["total_lines"] += lines
    return structure

@mcp.tool()
def extract_functions(file_path: str) -> list[dict]:
    """提取 Python 文件中的函数签名"""
    source = Path(file_path).read_text()
    tree = ast.parse(source)
    functions = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            args = [arg.arg for arg in node.args.args]
            docstring = ast.get_docstring(node) or ""
            functions.append({
                "name": node.name,
                "args": args,
                "docstring": docstring[:100],
                "line": node.lineno,
            })
    return functions

@mcp.tool()
def search_code(repo_path: str, pattern: str) -> list[dict]:
    """在代码库中搜索模式"""
    import re
    results = []
    for file in Path(repo_path).rglob("*.py"):
        content = file.read_text(errors="ignore")
        for i, line in enumerate(content.splitlines(), 1):
            if re.search(pattern, line):
                results.append({"file": str(file), "line": i, "content": line.strip()})
    return results[:20]
```

## 3. 代码生成与审查

```python
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-4o", temperature=0)

async def generate_code(requirement: str, context: str = "") -> str:
    """根据需求生成代码"""
    prompt = f"""根据以下需求生成 Python 代码。

需求：{requirement}

项目上下文：
{context}

要求：
1. 代码简洁、可读
2. 包含类型注解
3. 包含 docstring
4. 处理异常情况
"""
    return (await llm.ainvoke(prompt)).content

async def review_code(code: str) -> dict:
    """代码审查"""
    prompt = f"""审查以下代码，从以下维度评估：

```python
{code}
```

请输出 JSON：
{{
    "score": 0-10,
    "issues": [
        {{"severity": "high/medium/low", "line": 行号, "description": "问题描述", "suggestion": "修改建议"}}
    ],
    "summary": "总体评价"
}}"""

    result = (await llm.ainvoke(prompt)).content
    # 提取 JSON
    import json, re
    json_match = re.search(r'\{.*\}', result, re.DOTALL)
    return json.loads(json_match.group()) if json_match else {"score": 0, "issues": [], "summary": result}
```

## 4. Bug 修复 Agent

```python
from langgraph.graph import StateGraph, START, END
from typing import TypedDict

class BugFixState(TypedDict):
    error_message: str
    file_path: str
    code_context: str
    diagnosis: str
    fix: str

def diagnose_bug(state: BugFixState) -> dict:
    """诊断 Bug 原因"""
    prompt = f"""分析以下错误：

错误信息：{state['error_message']}
文件：{state['file_path']}
代码上下文：
{state['code_context']}

请诊断根本原因。"""
    diagnosis = llm.invoke(prompt).content
    return {"diagnosis": diagnosis}

def generate_fix(state: BugFixState) -> dict:
    """生成修复代码"""
    prompt = f"""基于以下诊断，生成修复代码：

诊断：{state['diagnosis']}
原始代码：
{state['code_context']}

只输出修复后的完整代码。"""
    fix = llm.invoke(prompt).content
    return {"fix": fix}

def verify_fix(state: BugFixState) -> str:
    """验证修复是否合理"""
    prompt = f"""验证以下修复是否正确：
原始错误：{state['error_message']}
修复代码：{state['fix']}
回答 yes 或 no。"""
    result = llm.invoke(prompt).content
    return END if "yes" in result.lower() else "diagnose"

graph = StateGraph(BugFixState)
graph.add_node("diagnose", diagnose_bug)
graph.add_node("fix", generate_fix)
graph.add_edge(START, "diagnose")
graph.add_edge("diagnose", "fix")
graph.add_conditional_edges("fix", verify_fix)
bugfix_agent = graph.compile()
```

## 5. 测试生成

```python
async def generate_tests(code: str, file_path: str) -> str:
    """为代码生成单元测试"""
    prompt = f"""为以下代码生成 pytest 单元测试：

文件：{file_path}
```python
{code}
```

要求：
1. 覆盖正常路径和边界情况
2. 使用 pytest 风格
3. 包含 mock（如有外部依赖）
4. 测试函数命名清晰
"""
    return (await llm.ainvoke(prompt)).content
```

## 6. MCP 工具集成

```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/workspace"]
    },
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {"GITHUB_TOKEN": "ghp_xxx"}
    },
    "code-assistant": {
      "command": "python",
      "args": ["code_assistant_mcp.py"]
    }
  }
}
```
