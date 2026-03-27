# AG2 / PydanticAI / Agno

> Author: Walter Wang

## 1. AG2（原 AutoGen）

AG2 是微软 AutoGen 项目的社区分支，专注于多 Agent 对话和协作。

```python
from autogen import ConversableAgent

# 定义 Agent
assistant = ConversableAgent(
    name="assistant",
    system_message="你是一个有帮助的AI助手，擅长编程和分析。",
    llm_config={"model": "gpt-4o", "api_key": "..."},
)

user_proxy = ConversableAgent(
    name="user_proxy",
    human_input_mode="NEVER",  # ALWAYS / TERMINATE / NEVER
    code_execution_config={"work_dir": "workspace", "use_docker": True},
    is_termination_msg=lambda msg: "TERMINATE" in msg.get("content", ""),
)

# 发起对话
result = user_proxy.initiate_chat(
    assistant,
    message="用 Python 分析 iris 数据集，画出分类散点图",
    max_turns=5,
)

# 群聊模式
from autogen import GroupChat, GroupChatManager

coder = ConversableAgent(name="coder", system_message="你是 Python 开发者")
reviewer = ConversableAgent(name="reviewer", system_message="你是代码审查员")

group_chat = GroupChat(
    agents=[user_proxy, coder, reviewer],
    messages=[],
    max_round=10,
    speaker_selection_method="auto",  # auto / round_robin / manual
)
manager = GroupChatManager(groupchat=group_chat, llm_config=llm_config)
user_proxy.initiate_chat(manager, message="开发一个 REST API")
```

## 2. PydanticAI

PydanticAI 是 Pydantic 团队推出的类型安全 Agent 框架，强调类型验证和结构化输出。

```python
from pydantic_ai import Agent
from pydantic import BaseModel

# 定义结构化输出
class CityInfo(BaseModel):
    name: str
    country: str
    population: int
    famous_for: list[str]

# 创建类型安全的 Agent
agent = Agent(
    model="openai:gpt-4o",
    result_type=CityInfo,  # 强制输出类型
    system_prompt="你是一个地理知识专家，提供准确的城市信息。",
)

# 同步运行
result = agent.run_sync("介绍一下东京")
print(result.data.name)        # "东京"
print(result.data.population)  # 13960000
print(result.data.famous_for)  # ["樱花", "寿司", ...]

# 带依赖注入的 Agent
from dataclasses import dataclass

@dataclass
class Deps:
    db_conn: any
    api_key: str

agent = Agent(model="openai:gpt-4o", deps_type=Deps)

@agent.tool
async def query_database(ctx, sql: str) -> str:
    """执行数据库查询"""
    result = await ctx.deps.db_conn.execute(sql)
    return str(result)

result = await agent.run(
    "查询上月销售额",
    deps=Deps(db_conn=db, api_key="xxx"),
)
```

## 3. Agno（原 Phidata）

Agno 是一个高性能 Agent 运行时，强调速度和轻量。

```python
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.yfinance import YFinanceTools

# 创建 Agent
agent = Agent(
    model=OpenAIChat(id="gpt-4o"),
    tools=[DuckDuckGoTools(), YFinanceTools(stock_price=True)],
    instructions="你是一个金融分析师，用中文回答。",
    show_tool_calls=True,
    markdown=True,
)

# 运行
agent.print_response("分析苹果公司最近的股价走势", stream=True)

# 团队模式
from agno.team import Team

web_agent = Agent(name="web", tools=[DuckDuckGoTools()])
finance_agent = Agent(name="finance", tools=[YFinanceTools()])

team = Team(
    agents=[web_agent, finance_agent],
    mode="coordinate",  # coordinate / route / collaborate
    model=OpenAIChat(id="gpt-4o"),
)
team.print_response("对比特斯拉和比亚迪的市场表现")
```

## 4. smolagents

HuggingFace 推出的极简 Agent 框架，代码量极少。

```python
from smolagents import CodeAgent, HfApiModel, tool

@tool
def get_weather(city: str) -> str:
    """获取城市天气信息"""
    return f"{city}: 25°C, 晴天"

agent = CodeAgent(
    tools=[get_weather],
    model=HfApiModel("Qwen/Qwen2.5-72B-Instruct"),
)

result = agent.run("北京今天天气怎么样？")
```

## 5. 框架对比

| 特性 | AG2 | PydanticAI | Agno | smolagents |
|------|-----|-----------|------|-----------|
| 核心理念 | 多 Agent 对话 | 类型安全 | 高性能运行时 | 极简轻量 |
| 类型验证 | 弱 | 强（Pydantic） | 中 | 弱 |
| 多 Agent | 原生群聊 | 手动编排 | Team 模式 | 有限 |
| 代码执行 | Docker 沙箱 | 无 | 无 | 原生 |
| 学习曲线 | 中 | 低 | 低 | 极低 |
| 模型支持 | 多模型 | 多模型 | 多模型 | HuggingFace |
| 适用场景 | 复杂多Agent | 生产级API | 快速开发 | 原型验证 |
