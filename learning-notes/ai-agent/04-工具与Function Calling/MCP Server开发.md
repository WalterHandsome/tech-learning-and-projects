# MCP Server 开发
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. Python SDK 完整示例

```python
from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.utilities.types import Image
import httpx
import json

mcp = FastMCP(
    name="business-tools",
    version="1.0.0",
    description="企业业务工具集",
)

# ===== 工具注册 =====
@mcp.tool()
def query_orders(user_id: str, status: str = "all") -> list[dict]:
    """查询用户订单列表

    Args:
        user_id: 用户ID
        status: 订单状态过滤（all/pending/completed/cancelled）
    """
    orders = db.execute(
        "SELECT * FROM orders WHERE user_id = ? AND (? = 'all' OR status = ?)",
        (user_id, status, status),
    ).fetchall()
    return [dict(row) for row in orders]

@mcp.tool()
async def search_knowledge_base(query: str, top_k: int = 5) -> str:
    """搜索知识库（支持语义搜索）"""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/search",
            json={"query": query, "top_k": top_k},
        )
        results = response.json()
    return json.dumps(results, ensure_ascii=False, indent=2)

# ===== 资源注册 =====
@mcp.resource("db://schema")
def get_database_schema() -> str:
    """获取数据库表结构"""
    tables = db.execute(
        "SELECT sql FROM sqlite_master WHERE type='table'"
    ).fetchall()
    return "\n\n".join(row[0] for row in tables)

@mcp.resource("config://app/{env}")
def get_config(env: str) -> str:
    """获取应用配置（dev/staging/prod）"""
    config = load_config(env)
    return json.dumps(config, indent=2)

# ===== 提示模板注册 =====
@mcp.prompt()
def analyze_data(dataset: str, goal: str) -> str:
    """数据分析提示模板"""
    return f"""请分析以下数据集，目标是：{goal}

数据集：{dataset}

请按以下步骤进行：
1. 数据概览和质量检查
2. 关键指标统计
3. 趋势和异常分析
4. 结论和建议"""

if __name__ == "__main__":
    mcp.run(transport="stdio")
```

## 2. TypeScript SDK 完整示例

```typescript
import { McpServer, ResourceTemplate } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";

const server = new McpServer({
  name: "project-tools",
  version: "1.0.0",
});

// 工具注册
server.tool(
  "create_ticket",
  {
    title: z.string().describe("工单标题"),
    description: z.string().describe("问题描述"),
    priority: z.enum(["low", "medium", "high"]).default("medium"),
  },
  async ({ title, description, priority }) => {
    const ticket = await ticketService.create({ title, description, priority });
    return {
      content: [{ type: "text", text: `工单已创建: ${ticket.id}` }],
    };
  }
);

// 资源注册
server.resource(
  "logs",
  new ResourceTemplate("logs://{service}/{date}", { list: undefined }),
  async (uri, { service, date }) => ({
    contents: [{ uri: uri.href, mimeType: "text/plain", text: await getLogs(service, date) }],
  })
);

// 启动
const transport = new StdioServerTransport();
await server.connect(transport);
```

## 3. 传输层实现

```python
# stdio 传输（本地 IDE 集成）
if __name__ == "__main__":
    mcp.run(transport="stdio")

# SSE 传输（远程 HTTP 服务）
if __name__ == "__main__":
    mcp.run(transport="sse", host="0.0.0.0", port=8080)

# Streamable HTTP（新一代传输）
if __name__ == "__main__":
    mcp.run(transport="streamable-http", host="0.0.0.0", port=8080)
```

## 4. 认证与安全

```python
from mcp.server.fastmcp import FastMCP
import os

mcp = FastMCP("secure-tools")

# 环境变量传递密钥
API_KEY = os.environ.get("API_KEY")
DB_URL = os.environ.get("DATABASE_URL")

@mcp.tool()
def secure_query(sql: str) -> str:
    """安全的数据库查询（只读）"""
    # 输入验证
    forbidden = ["DROP", "DELETE", "UPDATE", "INSERT", "ALTER"]
    if any(kw in sql.upper() for kw in forbidden):
        raise ValueError("只允许 SELECT 查询")

    # 参数化查询防止 SQL 注入
    result = db.execute(sql).fetchall()
    return json.dumps([dict(r) for r in result], ensure_ascii=False)
```

```json
// mcp.json 配置认证
{
  "mcpServers": {
    "secure-tools": {
      "command": "python",
      "args": ["server.py"],
      "env": {
        "API_KEY": "${env:MY_API_KEY}",
        "DATABASE_URL": "${env:DB_URL}"
      }
    }
  }
}
```

## 5. 测试与调试

```bash
# 使用 MCP Inspector 调试
npx @modelcontextprotocol/inspector python server.py

# 命令行测试
echo '{"jsonrpc":"2.0","id":1,"method":"tools/list"}' | python server.py
```

```python
# 单元测试
import pytest
from mcp.server.fastmcp import FastMCP

@pytest.fixture
def mcp_server():
    mcp = FastMCP("test")

    @mcp.tool()
    def add(a: int, b: int) -> int:
        """加法"""
        return a + b

    return mcp

async def test_tool_call(mcp_server):
    """测试工具调用"""
    result = await mcp_server.call_tool("add", {"a": 1, "b": 2})
    assert result == 3

async def test_tool_list(mcp_server):
    """测试工具列表"""
    tools = await mcp_server.list_tools()
    assert len(tools) == 1
    assert tools[0].name == "add"
```
