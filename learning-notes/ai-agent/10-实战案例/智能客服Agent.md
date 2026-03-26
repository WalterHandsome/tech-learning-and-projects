# 智能客服 Agent

## 1. 系统架构

```
┌─────────────────────────────────────────────────────┐
│                   智能客服系统                         │
├──────────┬──────────┬──────────┬───────────────────┤
│ 接入层    │ Agent 层  │ 工具层    │ 数据层            │
├──────────┼──────────┼──────────┼───────────────────┤
│ Web/App  │ 分诊Agent │ 知识库检索│ 向量数据库         │
│ 微信/钉钉│ 客服Agent │ 订单查询  │ 业务数据库         │
│ API      │ 工单Agent │ 工单创建  │ 工单系统           │
└──────────┴──────────┴──────────┴───────────────────┘
         ↕ 人工坐席（Human-in-the-Loop）↕
```

## 2. 分诊 Agent

```python
from agents import Agent, handoff, Runner

# 分诊 Agent：根据问题类型路由
triage_agent = Agent(
    name="triage",
    instructions="""你是智能客服分诊员。根据用户问题分类并转交：
    - 产品咨询 → product_agent
    - 订单问题 → order_agent
    - 投诉建议 → complaint_agent
    - 无法处理 → 转人工""",
    handoffs=["product_agent", "order_agent", "complaint_agent"],
)

product_agent = Agent(
    name="product_agent",
    instructions="你是产品咨询专家。基于知识库回答产品相关问题。",
    tools=[search_knowledge_base],
)

order_agent = Agent(
    name="order_agent",
    instructions="你是订单处理专家。帮助用户查询订单、处理退换货。",
    tools=[query_order, create_return_request],
)

complaint_agent = Agent(
    name="complaint_agent",
    instructions="你是投诉处理专家。安抚用户情绪，记录投诉并创建工单。",
    tools=[create_ticket, escalate_to_human],
)
```

## 3. 知识库检索工具

```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("customer-service-tools")

@mcp.tool()
async def search_knowledge_base(query: str, category: str = "all") -> str:
    """搜索客服知识库"""
    results = await vectorstore.similarity_search(
        query, k=3, filter={"category": category} if category != "all" else None,
    )
    return "\n\n".join(f"[{i+1}] {doc.page_content}" for i, doc in enumerate(results))

@mcp.tool()
def query_order(order_id: str) -> dict:
    """查询订单详情"""
    order = db.execute("SELECT * FROM orders WHERE id = ?", (order_id,)).fetchone()
    if not order:
        return {"error": "订单不存在"}
    return {
        "order_id": order["id"],
        "status": order["status"],
        "items": order["items"],
        "created_at": order["created_at"],
    }

@mcp.tool()
def create_ticket(title: str, description: str, priority: str = "medium") -> dict:
    """创建客服工单"""
    ticket_id = db.execute(
        "INSERT INTO tickets (title, description, priority) VALUES (?, ?, ?)",
        (title, description, priority),
    ).lastrowid
    return {"ticket_id": ticket_id, "message": f"工单 #{ticket_id} 已创建"}
```

## 4. 多轮对话管理

```python
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.postgres import PostgresSaver
from typing import TypedDict, Annotated
from operator import add

class CustomerServiceState(TypedDict):
    messages: Annotated[list, add]
    customer_id: str
    intent: str
    satisfaction: float

def detect_intent(state: CustomerServiceState) -> dict:
    """意图识别"""
    last_msg = state["messages"][-1]["content"]
    intent = llm.invoke(
        f"识别用户意图（product/order/complaint/chat）：{last_msg}"
    ).content.strip()
    return {"intent": intent}

def route_by_intent(state: CustomerServiceState) -> str:
    intent = state["intent"]
    routes = {"product": "product_qa", "order": "order_service", "complaint": "complaint_handler"}
    return routes.get(intent, "general_chat")

def check_satisfaction(state: CustomerServiceState) -> str:
    """检查用户满意度，决定是否转人工"""
    last_msg = state["messages"][-1]["content"]
    negative_signals = ["不满意", "投诉", "找人工", "经理"]
    if any(signal in last_msg for signal in negative_signals):
        return "human_handoff"
    return "continue"

graph = StateGraph(CustomerServiceState)
graph.add_node("detect_intent", detect_intent)
graph.add_node("product_qa", product_qa_node)
graph.add_node("order_service", order_service_node)
graph.add_node("complaint_handler", complaint_node)
graph.add_node("human_handoff", human_handoff_node)

graph.add_edge(START, "detect_intent")
graph.add_conditional_edges("detect_intent", route_by_intent)

app = graph.compile(checkpointer=PostgresSaver.from_conn_string("postgresql://..."))
```

## 5. 人工转接

```python
from langgraph.types import interrupt

def human_handoff_node(state: CustomerServiceState) -> dict:
    """转接人工坐席"""
    # 生成对话摘要
    summary = llm.invoke(
        f"请用 3 句话摘要以下客服对话的关键信息：\n{state['messages']}"
    ).content

    # 中断等待人工接入
    human_response = interrupt({
        "type": "human_handoff",
        "customer_id": state["customer_id"],
        "summary": summary,
        "message": "用户请求转接人工，请人工坐席接入",
    })

    return {"messages": [{"role": "assistant", "content": human_response}]}
```

## 6. 满意度评估

```python
class SatisfactionEvaluator:
    """客服满意度评估"""

    def __init__(self, llm):
        self.llm = llm

    async def evaluate(self, conversation: list[dict]) -> dict:
        prompt = f"""分析以下客服对话，评估用户满意度。

对话记录：
{self._format(conversation)}

请输出 JSON：
{{"score": 0.0-1.0, "resolved": true/false, "sentiment": "positive/neutral/negative", "improvement": "改进建议"}}"""

        result = (await self.llm.ainvoke(prompt)).content
        return eval(result)

    def _format(self, messages: list[dict]) -> str:
        return "\n".join(f"{m['role']}: {m['content']}" for m in messages)

evaluator = SatisfactionEvaluator(llm)
score = await evaluator.evaluate(conversation_messages)
# {"score": 0.85, "resolved": True, "sentiment": "positive", "improvement": "可以更主动提供相关信息"}
```
