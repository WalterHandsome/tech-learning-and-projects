# MCP 模型上下文协议
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. MCP 概述

MCP（Model Context Protocol）是 Anthropic 于 2024 年底提出的开放协议，用于标准化 AI 模型与外部工具、数据源之间的连接。类比为"AI 应用的 USB-C 接口"。

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   MCP Host    │     │  MCP Client  │     │  MCP Server  │
│  (IDE/App)    │────>│  (协议层)     │────>│  (工具/数据)  │
│  Claude Desktop│     │              │     │  GitHub API  │
│  Cursor/Kiro  │     │              │     │  数据库       │
│  自定义应用    │     │              │     │  文件系统     │
└──────────────┘     └──────────────┘     └──────────────┘
```

## 2. 核心概念

### 2.1 三大原语

```python
# 1. Tools（工具）— 模型可调用的函数
@mcp.tool()
def search_database(query: str, limit: int = 10) -> list[dict]:
    """搜索数据库中的记录"""
    return db.search(query, limit=limit)

# 2. Resources（资源）— 模型可读取的数据
@mcp.resource("file://{path}")
def read_file(path: str) -> str:
    """读取文件内容"""
    return Path(path).read_text()

# 3. Prompts（提示模板）— 预定义的交互模板
@mcp.prompt()
def code_review(code: str, language: str) -> str:
    """代码审查提示模板"""
    return f"请审查以下 {language} 代码:\n\n{code}"
```

### 2.2 传输层

```
stdio    — 本地进程通信（最常用，IDE集成）
SSE      — HTTP Server-Sent Events（远程服务）
Streamable HTTP — 新一代 HTTP 传输（替代 SSE）
```

## 3. MCP Server 开发（Python）

```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("my-tools")

@mcp.tool()
def get_weather(city: str) -> str:
    """获取城市天气信息"""
    # 调用天气 API
    response = requests.get(f"https://api.weather.com/{city}")
    data = response.json()
    return f"{city}: {data['temp']}°C, {data['condition']}"

@mcp.tool()
def query_database(sql: str) -> list[dict]:
    """执行 SQL 查询（只读）"""
    if not sql.strip().upper().startswith("SELECT"):
        raise ValueError("只允许 SELECT 查询")
    return db.execute(sql).fetchall()

@mcp.resource("config://app")
def get_app_config() -> str:
    """获取应用配置"""
    return json.dumps(config, indent=2)

if __name__ == "__main__":
    mcp.run(transport="stdio")
```

## 4. MCP Server 开发（TypeScript）

```typescript
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";

const server = new McpServer({ name: "my-tools", version: "1.0.0" });

server.tool("search_docs", { query: z.string(), limit: z.number().default(5) },
  async ({ query, limit }) => {
    const results = await searchIndex(query, limit);
    return { content: [{ type: "text", text: JSON.stringify(results) }] };
  }
);

const transport = new StdioServerTransport();
await server.connect(transport);
```

## 5. 配置与使用

```json
// mcp.json（IDE 配置）
{
  "mcpServers": {
    "my-tools": {
      "command": "python",
      "args": ["my_mcp_server.py"],
      "env": { "DATABASE_URL": "postgresql://..." }
    },
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": { "GITHUB_TOKEN": "ghp_xxx" }
    }
  }
}
```

## 6. MCP 生态

```
官方 Server：
- filesystem    — 文件系统操作
- github        — GitHub API
- postgres      — PostgreSQL 查询
- slack         — Slack 消息
- puppeteer     — 浏览器自动化
- memory        — 知识图谱记忆

社区 Server：1000+ 开源实现
```
