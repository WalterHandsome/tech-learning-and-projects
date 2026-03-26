# Microsoft Agent Framework

## 1. 概述

Microsoft Agent Framework 是微软于 2026 年推出的统一 Agent 开发框架，由 Semantic Kernel（企业级 AI 编排）和 AutoGen（多 Agent 研究框架）合并而来。融合了 SK 的类型安全、遥测、安全能力与 AutoGen 的多 Agent 协作模式。

```
┌─────────────── Microsoft Agent Framework ───────────────┐
│                                                          │
│  Semantic Kernel 基因          AutoGen 基因               │
│  ├─ 类型安全 Skills/Plugins   ├─ 多 Agent 对话模式        │
│  ├─ 企业级遥测               ├─ 群聊编排                  │
│  ├─ 安全与合规               ├─ 代码执行沙箱              │
│  └─ Connector 生态           └─ 人机协作循环              │
│                                                          │
│  ┌──────────────────────────────────────────────────┐   │
│  │          Azure AI Foundry 集成部署                 │   │
│  └──────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

## 2. 核心概念

### 2.1 Agent 类型

```python
from microsoft.agents import (
    Agent,
    ChatCompletionAgent,
    OpenAIAssistantAgent,
    AzureAIAgent,
)

# ChatCompletionAgent — 最常用，基于 Chat Completions API
agent = ChatCompletionAgent(
    name="assistant",
    instructions="你是一个有帮助的助手。",
    model="gpt-4o",
    plugins=[search_plugin, math_plugin],
)

# OpenAIAssistantAgent — 基于 OpenAI Assistants API（支持文件、代码解释器）
assistant = OpenAIAssistantAgent(
    name="data_analyst",
    instructions="你是数据分析师，使用代码解释器分析数据。",
    model="gpt-4o",
    enable_code_interpreter=True,
)

# AzureAIAgent — Azure AI Foundry 托管 Agent
azure_agent = AzureAIAgent(
    name="enterprise_bot",
    project_endpoint="https://xxx.services.ai.azure.com",
    model="gpt-4o",
)
```

### 2.2 Skills/Plugins 系统（源自 Semantic Kernel）

```python
from microsoft.agents import plugin, skill

# 定义 Plugin（工具集合）
@plugin
class WeatherPlugin:
    """天气查询插件"""

    @skill
    def get_current_weather(self, city: str) -> str:
        """获取当前天气"""
        return f"{city}: 26°C, 多云"

    @skill
    def get_forecast(self, city: str, days: int = 3) -> str:
        """获取天气预报"""
        return f"{city} 未来{days}天：晴→多云→小雨"

# 注册到 Agent
agent = ChatCompletionAgent(
    name="weather_bot",
    instructions="你是天气助手。",
    plugins=[WeatherPlugin()],
)

response = await agent.invoke("北京明天天气怎么样？")
```

## 3. 图编排（AgentGroupChat / GraphFlow）

```python
from microsoft.agents import ChatCompletionAgent
from microsoft.agents.orchestration import AgentGroupChat, GraphFlow

# 定义多个 Agent
planner = ChatCompletionAgent(name="planner", instructions="你负责制定计划。")
coder = ChatCompletionAgent(name="coder", instructions="你负责编写代码。")
tester = ChatCompletionAgent(name="tester", instructions="你负责测试和审查。")

# 方式一：AgentGroupChat（自由讨论）
group_chat = AgentGroupChat(
    agents=[planner, coder, tester],
    max_rounds=10,
    termination_condition=lambda msg: "APPROVED" in msg.content,
)
result = await group_chat.invoke("开发一个用户注册 API")

# 方式二：GraphFlow（图结构编排）
flow = GraphFlow()
flow.add_node("plan", planner)
flow.add_node("code", coder)
flow.add_node("test", tester)
flow.add_edge("plan", "code")
flow.add_edge("code", "test")
flow.add_conditional_edge("test", lambda r: "code" if "bug" in r else "end")

result = await flow.run("开发一个用户注册 API")
```

## 4. MCP 支持

```python
from microsoft.agents import ChatCompletionAgent
from microsoft.agents.mcp import MCPToolProvider

# 通过 MCP 接入外部工具
mcp_tools = MCPToolProvider(
    server_command="npx",
    server_args=["-y", "@modelcontextprotocol/server-github"],
    env={"GITHUB_TOKEN": "ghp_xxx"},
)

agent = ChatCompletionAgent(
    name="dev_assistant",
    instructions="你是开发助手，可以操作 GitHub。",
    tools=await mcp_tools.get_tools(),
)
```

## 5. .NET 支持

```csharp
using Microsoft.Agents;

var agent = new ChatCompletionAgent
{
    Name = "assistant",
    Instructions = "你是一个有帮助的助手。",
    Model = "gpt-4o",
    Plugins = [new WeatherPlugin(), new SearchPlugin()],
};

var response = await agent.InvokeAsync("今天天气如何？");
Console.WriteLine(response.Content);
```

## 6. Azure AI Foundry 集成

```python
from microsoft.agents import AzureAIAgent

# 部署到 Azure AI Foundry
agent = AzureAIAgent.create(
    name="enterprise_agent",
    project_endpoint="https://myproject.services.ai.azure.com",
    model="gpt-4o",
    plugins=[crm_plugin, erp_plugin],
    guardrails=["content_safety", "pii_filter"],
)

# 生产环境调用
response = await agent.invoke(
    message="查询客户 C-001 的最近订单",
    session_id="session-abc",
)
```

## 7. 从 SK / AutoGen 迁移

```
Semantic Kernel 迁移：
  Kernel + Plugin       → Agent + Plugin（API 基本兼容）
  KernelFunction        → @skill 装饰器
  Planner               → GraphFlow
  ChatCompletionService → ChatCompletionAgent

AutoGen 迁移：
  AssistantAgent        → ChatCompletionAgent
  GroupChat             → AgentGroupChat
  UserProxyAgent        → HumanAgent
  Code Executor         → CodeInterpreterTool
```

## 8. 适用场景

| 场景 | 推荐方式 |
|------|---------|
| 企业内部 Bot | AzureAIAgent + Plugins |
| 多 Agent 协作 | AgentGroupChat / GraphFlow |
| 代码分析任务 | OpenAIAssistantAgent + Code Interpreter |
| 跨语言团队 | Python + .NET 混合开发 |
| 快速原型 | ChatCompletionAgent + @skill |
