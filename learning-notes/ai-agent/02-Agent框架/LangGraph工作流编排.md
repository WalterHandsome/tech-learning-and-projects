# LangGraph 工作流编排
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. 概述

LangGraph 是 LangChain 团队推出的 Agent 工作流编排框架，基于图结构定义 Agent 的执行流程。2025 年 10 月发布 1.0 GA，是目前生产级 Agent 开发的行业标准。

核心优势：图结构控制流、模型无关、内置检查点、人机交互支持。

## 2. 核心概念

```python
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode
from typing import TypedDict, Annotated
from operator import add

# 1. 定义状态
class AgentState(TypedDict):
    messages: Annotated[list, add]  # 消息列表（累加）
    next_step: str

# 2. 定义节点（函数）
def call_model(state: AgentState) -> dict:
    response = llm.invoke(state["messages"])
    return {"messages": [response]}

def call_tools(state: AgentState) -> dict:
    last_message = state["messages"][-1]
    results = tool_executor.invoke(last_message.tool_calls)
    return {"messages": results}

# 3. 构建图
graph = StateGraph(AgentState)
graph.add_node("agent", call_model)
graph.add_node("tools", ToolNode(tools))

# 4. 定义边（路由）
def should_continue(state: AgentState) -> str:
    last_message = state["messages"][-1]
    if last_message.tool_calls:
        return "tools"
    return END

graph.add_edge(START, "agent")
graph.add_conditional_edges("agent", should_continue, {"tools": "tools", END: END})
graph.add_edge("tools", "agent")

# 5. 编译并运行
app = graph.compile()
result = app.invoke({"messages": [HumanMessage(content="北京今天天气怎么样？")]})
```

## 3. 检查点与状态持久化

```python
from langgraph.checkpoint.memory import MemorySaver
from langgraph.checkpoint.postgres import PostgresSaver

# 内存检查点（开发用）
memory = MemorySaver()
app = graph.compile(checkpointer=memory)

# PostgreSQL 检查点（生产用）
checkpointer = PostgresSaver.from_conn_string("postgresql://...")
app = graph.compile(checkpointer=checkpointer)

# 使用 thread_id 维护会话状态
config = {"configurable": {"thread_id": "user-123"}}
result = app.invoke({"messages": [HumanMessage("你好")]}, config)
# 后续对话自动恢复上下文
result = app.invoke({"messages": [HumanMessage("继续上面的话题")]}, config)
```

## 4. 人机交互（Human-in-the-Loop）

```python
from langgraph.graph import StateGraph
from langgraph.types import interrupt, Command

def sensitive_action(state: AgentState) -> dict:
    """需要人工审批的敏感操作"""
    action = state["pending_action"]

    # 中断执行，等待人工审批
    approval = interrupt({
        "action": action,
        "message": f"是否批准执行: {action['name']}？"
    })

    if approval == "approved":
        result = execute_action(action)
        return {"messages": [AIMessage(content=f"已执行: {result}")]}
    else:
        return {"messages": [AIMessage(content="操作已取消")]}

# 编译时启用中断
app = graph.compile(checkpointer=memory, interrupt_before=["sensitive_action"])

# 恢复执行
app.invoke(Command(resume="approved"), config)
```

## 5. 子图（Subgraph）

```python
# 将复杂流程拆分为子图
research_graph = StateGraph(ResearchState)
# ... 定义研究子图

writing_graph = StateGraph(WritingState)
# ... 定义写作子图

# 主图组合子图
main_graph = StateGraph(MainState)
main_graph.add_node("research", research_graph.compile())
main_graph.add_node("writing", writing_graph.compile())
main_graph.add_edge("research", "writing")
```

## 6. LangGraph Cloud

```python
# langgraph.json — 部署配置
{
    "graphs": {
        "my_agent": "./agent.py:app"
    },
    "dependencies": ["langchain-openai", "langchain-community"]
}

# 部署到 LangGraph Cloud
# langgraph deploy --config langgraph.json
```
## 🎬 推荐视频资源

- [DeepLearning.AI - AI Agents in LangGraph](https://www.deeplearning.ai/short-courses/ai-agents-in-langgraph/) — 吴恩达+LangChain联合出品（免费）
- [freeCodeCamp - How to Develop AI Agents Using LangGraph](https://www.youtube.com/watch?v=dcgRMOG605w) — LangGraph实战指南
- [LangChain Official - LangGraph Tutorial](https://www.youtube.com/watch?v=9BPCV5TYPmg) — 官方教程
