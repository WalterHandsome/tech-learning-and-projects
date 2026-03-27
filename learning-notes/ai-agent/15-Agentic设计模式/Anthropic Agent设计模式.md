# Anthropic Agent 设计模式
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. Workflows vs Agents

Anthropic 在 "Building Effective Agents" 指南中将 Agentic 系统分为两大类：

```
┌─────────────────────────────────────────────────────┐
│              Agentic 系统                             │
├────────────────────────┬────────────────────────────┤
│      Workflows         │        Agents              │
│  预定义的编排流程        │  模型自主决策执行路径        │
│  LLM 按固定路径调用      │  LLM 动态选择工具和步骤     │
│  可预测、可控            │  灵活、适应性强             │
│  适合明确流程            │  适合开放式任务             │
└────────────────────────┴────────────────────────────┘
```

核心原则：**从简单开始，仅在必要时增加复杂度。**

## 2. Workflow 模式一：Prompt Chaining（提示链）

顺序调用 LLM，前一步输出作为后一步输入，中间可插入验证门控。

```python
from anthropic import Anthropic

client = Anthropic()

def prompt_chaining(topic: str) -> dict:
    """提示链：生成 → 验证 → 优化"""

    # 步骤1：生成初稿
    draft = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1024,
        messages=[{"role": "user", "content": f"写一篇关于 {topic} 的技术博客大纲"}]
    ).content[0].text

    # 门控：验证质量
    validation = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=256,
        messages=[{"role": "user", "content": f"评估大纲质量，回答 PASS 或 FAIL：\n{draft}"}]
    ).content[0].text

    if "FAIL" in validation.upper():
        return {"status": "rejected", "draft": draft}

    # 步骤2：扩展为完整文章
    article = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4096,
        messages=[{"role": "user", "content": f"基于大纲写完整文章：\n{draft}"}]
    ).content[0].text

    return {"status": "success", "article": article}
```

## 3. Workflow 模式二：Routing（路由分发）

对输入进行分类，路由到不同的专业处理器。

```python
def routing_workflow(user_input: str) -> str:
    """路由：分类 → 分发到专业处理器"""

    # 分类器
    category = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=50,
        messages=[{"role": "user", "content": f"""将以下请求分类为：code_help / general_qa / creative_writing
请求：{user_input}
只输出类别名称。"""}]
    ).content[0].text.strip()

    # 专业处理器
    handlers = {
        "code_help": "你是资深程序员，提供精确的代码解决方案。",
        "general_qa": "你是知识渊博的助手，提供准确简洁的回答。",
        "creative_writing": "你是创意写作专家，文笔优美富有想象力。",
    }

    system_prompt = handlers.get(category, handlers["general_qa"])
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=2048,
        system=system_prompt,
        messages=[{"role": "user", "content": user_input}]
    ).content[0].text

    return response
```

## 4. Workflow 模式三：Parallelization（并行化）

将任务拆分为独立子任务并行处理，或多次生成后投票。

```python
import asyncio
from anthropic import AsyncAnthropic

async_client = AsyncAnthropic()

async def parallel_sectioning(topic: str) -> dict:
    """并行分段：同时生成文章各部分"""
    sections = ["引言", "核心概念", "实践案例", "总结"]

    async def generate_section(section: str) -> str:
        resp = await async_client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1024,
            messages=[{"role": "user", "content": f"为 {topic} 文章写 {section} 部分"}]
        )
        return resp.content[0].text

    results = await asyncio.gather(*[generate_section(s) for s in sections])
    return dict(zip(sections, results))

async def parallel_voting(question: str, n_votes: int = 3) -> str:
    """并行投票：多次生成取多数"""
    async def get_answer() -> str:
        resp = await async_client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=100,
            messages=[{"role": "user", "content": f"{question}\n简短回答。"}]
        )
        return resp.content[0].text

    answers = await asyncio.gather(*[get_answer() for _ in range(n_votes)])
    # 简单多数投票（实际可用语义相似度聚类）
    from collections import Counter
    return Counter(answers).most_common(1)[0][0]
```

## 5. Workflow 模式四：Orchestrator-Workers（编排-工作者）

中央编排 LLM 动态分解任务，委派给工作者 LLM 执行。

```python
import json

def orchestrator_workers(task: str) -> dict:
    """编排者动态分解任务，工作者并行执行"""

    # 编排者：分解任务
    plan = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1024,
        messages=[{"role": "user", "content": f"""将以下任务分解为子任务，输出 JSON 数组：
任务：{task}
格式：[{{"id": 1, "subtask": "描述", "type": "research|code|write"}}]"""}]
    ).content[0].text

    subtasks = json.loads(plan)

    # 工作者：执行各子任务
    results = {}
    for st in subtasks:
        worker_resp = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2048,
            messages=[{"role": "user", "content": f"执行以下任务：{st['subtask']}"}]
        ).content[0].text
        results[st["id"]] = worker_resp

    # 编排者：合并结果
    synthesis = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4096,
        messages=[{"role": "user", "content": f"合并以下子任务结果为完整输出：\n{json.dumps(results, ensure_ascii=False)}"}]
    ).content[0].text

    return {"plan": subtasks, "result": synthesis}
```

## 6. Workflow 模式五：Evaluator-Optimizer（评估-优化）

一个 LLM 生成，另一个评估，循环迭代直到满足标准。

```python
def evaluator_optimizer(task: str, max_iterations: int = 3) -> str:
    """生成-评估循环"""
    current_output = ""

    for i in range(max_iterations):
        # 生成器
        gen_prompt = f"任务：{task}" if i == 0 else f"任务：{task}\n上次输出：{current_output}\n改进建议：{feedback}\n请改进。"
        current_output = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2048,
            messages=[{"role": "user", "content": gen_prompt}]
        ).content[0].text

        # 评估器
        eval_resp = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=512,
            messages=[{"role": "user", "content": f"""评估输出质量（1-10分），给出改进建议。
任务：{task}
输出：{current_output}
格式：SCORE: X\nFEEDBACK: ..."""}]
        ).content[0].text

        score = int(eval_resp.split("SCORE:")[1].split("\n")[0].strip())
        feedback = eval_resp.split("FEEDBACK:")[1].strip() if "FEEDBACK:" in eval_resp else ""

        if score >= 8:
            break

    return current_output
```

## 7. 自主 Agent 模式（ReAct 循环）

Agent 在循环中自主决定使用工具，直到完成任务。

```python
import anthropic

tools = [
    {"name": "search", "description": "搜索信息",
     "input_schema": {"type": "object", "properties": {"query": {"type": "string"}}}},
    {"name": "calculator", "description": "数学计算",
     "input_schema": {"type": "object", "properties": {"expression": {"type": "string"}}}},
]

def autonomous_agent(task: str, max_turns: int = 10) -> str:
    """自主 Agent：ReAct 循环"""
    messages = [{"role": "user", "content": task}]

    for _ in range(max_turns):
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4096,
            tools=tools,
            messages=messages,
        )

        # 无工具调用 → 任务完成
        if response.stop_reason == "end_turn":
            return next(b.text for b in response.content if b.type == "text")

        # 执行工具调用
        messages.append({"role": "assistant", "content": response.content})
        tool_results = []
        for block in response.content:
            if block.type == "tool_use":
                result = execute_tool(block.name, block.input)
                tool_results.append({
                    "type": "tool_result", "tool_use_id": block.id, "content": result
                })
        messages.append({"role": "user", "content": tool_results})

    return "达到最大轮次限制"
```

## 8. 决策框架：何时用 Workflow vs Agent

```
需求明确、流程固定？ ──→ YES ──→ Workflow
        │
        NO
        ↓
需要动态决策？ ──→ YES ──→ Agent
        │
        NO
        ↓
从最简单的 Prompt Chaining 开始

选择 Workflow 模式：
├─ 线性流程 → Prompt Chaining
├─ 输入分类 → Routing
├─ 可并行   → Parallelization
├─ 动态分解 → Orchestrator-Workers
└─ 需迭代   → Evaluator-Optimizer
```

| 维度       | Workflow           | Agent              |
|-----------|--------------------|--------------------|
| 可预测性   | 高                 | 低                 |
| 灵活性     | 低                 | 高                 |
| 调试难度   | 简单               | 复杂               |
| 成本控制   | 容易               | 需要限制轮次        |
| 适用场景   | 明确流程、高可靠性   | 开放式、探索性任务   |
## 🎬 推荐视频资源

- [DeepLearning.AI - Agentic AI with Andrew Ng](https://www.deeplearning.ai/courses/agentic-ai/) — Agentic设计模式全面讲解（免费）
- [DeepLearning.AI - AI Agentic Design Patterns with AutoGen](https://www.deeplearning.ai/short-courses/ai-agentic-design-patterns-with-autogen/) — 设计模式实战（免费）
### 📺 B站（Bilibili）
- [吴恩达 - Agentic AI设计模式中文字幕](https://www.bilibili.com/video/BV1Bz421B7bG) — Agentic设计模式讲解

### 🎓 DeepLearning.AI（免费）
- [Agentic AI with Andrew Ng](https://www.deeplearning.ai/courses/agentic-ai/) — Agentic AI完整课程
