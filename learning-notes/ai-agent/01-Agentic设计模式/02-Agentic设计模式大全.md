# Agentic 设计模式大全
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. Augmented LLM（增强型 LLM）

所有 Agent 的基础构建块：LLM + 检索 + 工具 + 记忆。

```
┌─────────────────────────────────┐
│         Augmented LLM           │
│  ┌─────┐ ┌──────┐ ┌────────┐  │
│  │检索  │ │ 工具  │ │ 记忆   │  │
│  │RAG  │ │Tools │ │Memory │  │
│  └──┬──┘ └──┬───┘ └───┬────┘  │
│     └───────┼─────────┘        │
│          ┌──┴──┐               │
│          │ LLM │               │
│          └─────┘               │
└─────────────────────────────────┘
```

```python
from openai import OpenAI

client = OpenAI()

# 增强型 LLM = 模型 + 工具 + 上下文
response = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {"role": "system", "content": "你是助手。使用工具回答问题。"},
        {"role": "user", "content": "查询北京天气"},
    ],
    tools=[{
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "获取天气信息",
            "parameters": {"type": "object", "properties": {"city": {"type": "string"}}},
        }
    }],
)
```

## 2. ReAct（推理 + 行动）

LLM 交替进行推理（Thought）和行动（Action），观察结果后继续。

```
Thought → Action → Observation → Thought → Action → ... → Answer
```

```python
from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool

@tool
def search(query: str) -> str:
    """搜索互联网"""
    return f"搜索结果：{query} 的相关信息..."

llm = ChatOpenAI(model="gpt-4o")
agent = create_react_agent(llm, tools=[search])
result = agent.invoke({"messages": [("user", "2025年AI Agent发展趋势")]})
```

## 3. Plan-and-Execute（规划-执行）

先制定完整计划，再逐步执行，可根据执行结果修订计划。

```
┌──────────┐    ┌──────────┐    ┌──────────┐
│  Planner │───→│ Executor │───→│ Replanner│
│  制定计划 │    │ 执行步骤  │    │ 修订计划  │
└──────────┘    └──────────┘    └─────┬────┘
                                      │
                                      ↓ 循环直到完成
```

```python
from typing import TypedDict
from langgraph.graph import StateGraph, START, END

class PlanState(TypedDict):
    task: str
    plan: list[str]
    current_step: int
    results: list[str]

def planner(state: PlanState) -> dict:
    """制定执行计划"""
    resp = llm.invoke(f"为以下任务制定步骤计划（JSON数组）：{state['task']}")
    import json
    steps = json.loads(resp.content)
    return {"plan": steps, "current_step": 0}

def executor(state: PlanState) -> dict:
    """执行当前步骤"""
    step = state["plan"][state["current_step"]]
    result = llm.invoke(f"执行：{step}").content
    return {"results": state["results"] + [result], "current_step": state["current_step"] + 1}

def should_continue(state: PlanState) -> str:
    return "executor" if state["current_step"] < len(state["plan"]) else END

graph = StateGraph(PlanState)
graph.add_node("planner", planner)
graph.add_node("executor", executor)
graph.add_edge(START, "planner")
graph.add_edge("planner", "executor")
graph.add_conditional_edges("executor", should_continue)
plan_agent = graph.compile()
```

## 4. Reflection / Self-Critique（反思/自我批评）

Agent 审查自己的输出，发现问题后自我修正。

```python
def reflection_agent(task: str, max_rounds: int = 3) -> str:
    """反思模式：生成 → 批评 → 改进"""
    output = llm.invoke(f"完成任务：{task}").content

    for _ in range(max_rounds):
        critique = llm.invoke(
            f"批评以下输出，列出问题和改进建议：\n任务：{task}\n输出：{output}"
        ).content

        if "没有问题" in critique or "质量很好" in critique:
            break

        output = llm.invoke(
            f"根据反馈改进输出：\n原输出：{output}\n反馈：{critique}"
        ).content

    return output
```

## 5. Tool Use / Function Calling（工具使用）

LLM 选择并调用外部工具，获取结果后继续推理。

```python
tools_registry = {
    "calculator": lambda expr: str(eval(expr)),
    "web_search": lambda q: f"搜索结果: {q}",
    "code_exec": lambda code: exec(code) or "执行完成",
}

def tool_use_agent(query: str) -> str:
    """工具使用模式"""
    messages = [{"role": "user", "content": query}]
    response = client.chat.completions.create(
        model="gpt-4o", messages=messages,
        tools=[{"type": "function", "function": {"name": k, "description": k,
                "parameters": {"type": "object", "properties": {"input": {"type": "string"}}}}}
               for k in tools_registry],
    )
    if response.choices[0].message.tool_calls:
        for tc in response.choices[0].message.tool_calls:
            result = tools_registry[tc.function.name](tc.function.arguments)
            messages.append({"role": "tool", "tool_call_id": tc.id, "content": result})
        return client.chat.completions.create(model="gpt-4o", messages=messages).choices[0].message.content
    return response.choices[0].message.content
```

## 6. Multi-Agent Delegation（多Agent委派）

主 Agent 将子任务委派给专业 Agent。

```python
from crewai import Agent, Task, Crew

researcher = Agent(role="研究员", goal="深度调研", llm="gpt-4o")
writer = Agent(role="作者", goal="撰写报告", llm="gpt-4o")

research_task = Task(description="调研 AI Agent 趋势", agent=researcher)
write_task = Task(description="撰写调研报告", agent=writer)

crew = Crew(agents=[researcher, writer], tasks=[research_task, write_task])
result = crew.kickoff()
```

## 7. Supervisor Pattern（监督者模式）

监督者 Agent 协调多个工作者，决定谁来处理下一步。

```
         ┌────────────┐
         │ Supervisor │
         └─────┬──────┘
        ┌──────┼──────┐
        ↓      ↓      ↓
    ┌──────┐┌──────┐┌──────┐
    │Worker││Worker││Worker│
    │  A   ││  B   ││  C   │
    └──────┘└──────┘└──────┘
```

```python
from langgraph.prebuilt import create_react_agent
from langgraph_supervisor import create_supervisor

research_agent = create_react_agent(llm, tools=[search_tool], name="researcher")
code_agent = create_react_agent(llm, tools=[code_tool], name="coder")

supervisor = create_supervisor(
    agents=[research_agent, code_agent],
    model=llm,
    prompt="根据任务类型分配给合适的 Agent。"
)
app = supervisor.compile()
```

## 8. Hierarchical Agent Teams（层级Agent团队）

多层监督者形成树状结构，处理复杂任务。

```
              ┌──────────┐
              │ Top Lead │
              └────┬─────┘
         ┌─────────┼─────────┐
    ┌────┴────┐         ┌────┴────┐
    │Research │         │Engineer │
    │  Lead   │         │  Lead   │
    └────┬────┘         └────┬────┘
    ┌────┼────┐         ┌────┼────┐
    │Web ││Doc│         │Code││Test│
    └────┘└───┘         └────┘└───┘
```

## 9. Map-Reduce for Agents

将大任务拆分（Map），各 Agent 并行处理，最后合并（Reduce）。

```python
import asyncio

async def map_reduce_agent(documents: list[str], question: str) -> str:
    """Map-Reduce：并行处理文档，合并结果"""

    # Map：每个文档独立分析
    async def analyze_doc(doc: str) -> str:
        resp = await async_llm.ainvoke(f"从文档中提取与 '{question}' 相关的信息：\n{doc}")
        return resp.content

    partial_results = await asyncio.gather(*[analyze_doc(d) for d in documents])

    # Reduce：合并所有结果
    combined = "\n---\n".join(partial_results)
    final = await async_llm.ainvoke(f"综合以下信息回答 '{question}'：\n{combined}")
    return final.content
```

## 10. Human-in-the-Loop（人机协作）

关键决策点暂停执行，等待人工审批。

```python
from langgraph.types import interrupt

def sensitive_operation(state: dict) -> dict:
    approval = interrupt({"message": f"是否批准操作：{state['action']}？"})
    if approval == "yes":
        return {"result": execute(state["action"])}
    return {"result": "操作已取消"}
```

## 11. Guardrails Pattern（护栏模式）

在 Agent 输入/输出处设置安全检查。

```python
def guardrailed_agent(user_input: str) -> str:
    # 输入护栏
    if contains_pii(user_input):
        return "请勿输入个人敏感信息"
    if is_prompt_injection(user_input):
        return "检测到异常输入"

    response = llm.invoke(user_input).content

    # 输出护栏
    if contains_harmful_content(response):
        return "抱歉，无法提供该内容"
    if exceeds_scope(response):
        return "该问题超出服务范围"

    return response
```

## 12. Fallback / Escalation（降级/升级）

失败时降级到备选方案，或升级给人工处理。

```python
async def fallback_agent(query: str) -> str:
    try:
        return await primary_agent(query)          # 主 Agent
    except Exception:
        try:
            return await simplified_agent(query)   # 简化 Agent
        except Exception:
            return await escalate_to_human(query)  # 升级人工
```

## 13. Caching / Memoization（缓存模式）

缓存相似查询结果，减少重复 LLM 调用。

```python
from functools import lru_cache
import hashlib

class SemanticCache:
    def __init__(self, similarity_threshold=0.95):
        self.cache = {}
        self.threshold = similarity_threshold

    def get(self, query: str) -> str | None:
        query_emb = get_embedding(query)
        for key_emb, value in self.cache.items():
            if cosine_similarity(query_emb, key_emb) > self.threshold:
                return value
        return None

    def set(self, query: str, response: str):
        self.cache[tuple(get_embedding(query))] = response
```

## 14. Streaming / Progressive Response（流式响应）

逐步返回结果，提升用户体验。

```python
async def streaming_agent(query: str):
    """流式输出 Agent 思考和结果"""
    async for event in agent.astream_events(
        {"messages": [("user", query)]}, version="v2"
    ):
        kind = event["event"]
        if kind == "on_chat_model_stream":
            print(event["data"]["chunk"].content, end="", flush=True)
        elif kind == "on_tool_start":
            print(f"\n🔧 调用工具: {event['name']}")
        elif kind == "on_tool_end":
            print(f"✅ 工具结果: {event['data'].content[:100]}")
```

## 15. Swarm Intelligence（群体智能）

多个平等 Agent 通过 handoff 机制协作，无中央控制。

```python
from openai import OpenAI
from openai.types.beta import Agent as SwarmAgent

client = OpenAI()

triage = SwarmAgent(name="triage", instructions="根据问题类型转交给专业Agent")
sales = SwarmAgent(name="sales", instructions="处理销售相关问题")
support = SwarmAgent(name="support", instructions="处理技术支持问题")

# Agent 间通过 handoff 转交控制权
triage.handoffs = [sales, support]
```

## 16. 模式选型速查

| 模式               | 复杂度 | 适用场景                 |
|-------------------|--------|------------------------|
| Augmented LLM     | ★      | 单轮工具调用              |
| ReAct             | ★★     | 通用推理+行动             |
| Plan-and-Execute  | ★★★    | 复杂多步骤任务            |
| Reflection        | ★★     | 需要高质量输出            |
| Multi-Agent       | ★★★    | 专业分工协作              |
| Supervisor        | ★★★    | 需要协调控制              |
| Map-Reduce        | ★★     | 大规模并行处理            |
| Human-in-the-Loop | ★★     | 高风险操作               |
| Guardrails        | ★      | 安全合规要求              |
| Fallback          | ★      | 高可用性要求              |
## 🎬 推荐视频资源

- [Andrew Ng - What's Next for AI Agentic Workflows](https://www.youtube.com/watch?v=sal78ACtGTc) — 吴恩达讲Agentic工作流
- [DeepLearning.AI - Agentic AI with Andrew Ng](https://www.deeplearning.ai/courses/agentic-ai/) — Agentic AI完整课程（免费）
