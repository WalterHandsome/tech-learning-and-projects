# Anthropic Claude Agent 能力
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. Claude 模型家族

```
┌─────────────────────────────────────────────────┐
│              Claude 模型家族（2025）               │
├──────────┬──────────┬──────────┬────────────────┤
│  Opus    │  Sonnet  │  Haiku   │  定位           │
│  最强推理 │  均衡     │  快速    │                 │
│  复杂Agent│  通用Agent│  简单任务│                 │
│  $15/M   │  $3/M    │  $0.25/M │  输入价格/1M    │
└──────────┴──────────┴──────────┴────────────────┘

Agent 场景推荐：
├─ 复杂推理/规划 → Claude Opus
├─ 通用 Agent → Claude Sonnet（性价比最优）
├─ 高吞吐简单任务 → Claude Haiku
└─ 代码生成 → Claude Sonnet（Coding 能力强）
```

## 2. Extended Thinking（扩展思考）

让 Claude 在回答前进行深度推理，类似 Chain-of-Thought。

```python
from anthropic import Anthropic

client = Anthropic()

response = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=16000,
    thinking={
        "type": "enabled",
        "budget_tokens": 10000,  # 思考预算（Token 数）
    },
    messages=[{
        "role": "user",
        "content": "设计一个支持 100 万并发用户的实时聊天系统架构"
    }],
)

# 查看思考过程和最终回答
for block in response.content:
    if block.type == "thinking":
        print(f"💭 思考过程:\n{block.thinking}")
    elif block.type == "text":
        print(f"\n📝 回答:\n{block.text}")
```

## 3. Tool Use（工具调用）

```python
from anthropic import Anthropic

client = Anthropic()

tools = [
    {
        "name": "get_stock_price",
        "description": "获取股票实时价格",
        "input_schema": {
            "type": "object",
            "properties": {
                "symbol": {"type": "string", "description": "股票代码，如 AAPL"},
            },
            "required": ["symbol"],
        },
    },
    {
        "name": "calculate",
        "description": "执行数学计算",
        "input_schema": {
            "type": "object",
            "properties": {
                "expression": {"type": "string", "description": "数学表达式"},
            },
            "required": ["expression"],
        },
    },
]

def execute_tool(name: str, input: dict) -> str:
    if name == "get_stock_price":
        return f'{{"symbol": "{input["symbol"]}", "price": 198.50, "change": "+2.3%"}}'
    elif name == "calculate":
        return str(eval(input["expression"]))

# Agent 循环
def claude_agent(task: str, max_turns: int = 10) -> str:
    messages = [{"role": "user", "content": task}]

    for _ in range(max_turns):
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4096,
            tools=tools,
            messages=messages,
        )

        if response.stop_reason == "end_turn":
            return next(b.text for b in response.content if b.type == "text")

        # 处理工具调用
        messages.append({"role": "assistant", "content": response.content})
        tool_results = []
        for block in response.content:
            if block.type == "tool_use":
                result = execute_tool(block.name, block.input)
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": result,
                })
        messages.append({"role": "user", "content": tool_results})

    return "达到最大轮次"

answer = claude_agent("AAPL 当前股价多少？如果我持有 100 股，总价值是多少？")
```

## 4. Computer Use（计算机操作）

```python
from anthropic import Anthropic

client = Anthropic()

# Computer Use：Claude 操作桌面环境
response = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=4096,
    tools=[
        {
            "type": "computer_20250124",
            "name": "computer",
            "display_width_px": 1920,
            "display_height_px": 1080,
            "display_number": 1,
        },
        {
            "type": "text_editor_20250124",
            "name": "str_replace_editor",
        },
        {
            "type": "bash_20250124",
            "name": "bash",
        },
    ],
    messages=[{
        "role": "user",
        "content": "打开浏览器，搜索 'AI Agent frameworks 2025'，截图第一页结果"
    }],
)

# Claude 会返回鼠标点击、键盘输入等操作指令
for block in response.content:
    if block.type == "tool_use":
        print(f"操作: {block.name} → {block.input}")
```

## 5. 多模态输入

```python
import base64

# 图片分析
with open("architecture.png", "rb") as f:
    image_data = base64.standard_b64encode(f.read()).decode()

response = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=2048,
    messages=[{
        "role": "user",
        "content": [
            {
                "type": "image",
                "source": {"type": "base64", "media_type": "image/png", "data": image_data},
            },
            {
                "type": "text",
                "text": "分析这个系统架构图，指出潜在的性能瓶颈",
            },
        ],
    }],
)

# PDF 文档分析
response = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=4096,
    messages=[{
        "role": "user",
        "content": [
            {
                "type": "document",
                "source": {"type": "base64", "media_type": "application/pdf", "data": pdf_data},
            },
            {"type": "text", "text": "总结这份文档的核心要点"},
        ],
    }],
)
```

## 6. Batch API（批量处理）

```python
from anthropic import Anthropic

client = Anthropic()

# 批量处理：适合大规模数据处理，成本降低 50%
batch = client.messages.batches.create(
    requests=[
        {
            "custom_id": f"task-{i}",
            "params": {
                "model": "claude-sonnet-4-20250514",
                "max_tokens": 1024,
                "messages": [{"role": "user", "content": f"分析数据点 {i}: {data}"}],
            },
        }
        for i, data in enumerate(dataset)
    ]
)

# 查询批次状态
status = client.messages.batches.retrieve(batch.id)
print(f"状态: {status.processing_status}")
print(f"完成: {status.request_counts.succeeded}/{status.request_counts.processing}")

# 获取结果
if status.processing_status == "ended":
    for result in client.messages.batches.results(batch.id):
        print(f"{result.custom_id}: {result.result.message.content[0].text}")
```

## 7. Claude Code（终端 Agent）

```bash
# Claude Code：命令行 AI Agent
# 安装
npm install -g @anthropic-ai/claude-code

# 使用
claude  # 启动交互式会话

# 常用命令
claude "重构 src/utils.py，添加类型注解和错误处理"
claude "找到并修复项目中的安全漏洞"
claude "为 UserService 类编写单元测试"

# Claude Code 能力：
# ├─ 读写文件
# ├─ 执行终端命令
# ├─ 搜索代码库
# ├─ Git 操作
# ├─ 运行测试
# └─ 多步骤推理和规划
```

## 8. API 最佳实践

```python
# Token 优化策略
def optimized_agent_call(task: str) -> str:
    """优化 Token 使用的 Agent 调用"""

    # 1. 使用 system prompt 缓存（减少重复 Token）
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4096,
        system=[{
            "type": "text",
            "text": "你是 AI 助手...(长 system prompt)",
            "cache_control": {"type": "ephemeral"},  # 启用缓存
        }],
        messages=[{"role": "user", "content": task}],
    )

    # 2. 流式输出（减少等待时间）
    with client.messages.stream(
        model="claude-sonnet-4-20250514",
        max_tokens=4096,
        messages=[{"role": "user", "content": task}],
    ) as stream:
        for text in stream.text_stream:
            print(text, end="", flush=True)

    return response.content[0].text

# 3. 模型选择策略
def select_model(task_complexity: str) -> str:
    """根据任务复杂度选择模型"""
    models = {
        "simple": "claude-haiku-3-5",       # 简单分类/提取
        "medium": "claude-sonnet-4-20250514",  # 通用任务
        "complex": "claude-opus-4-20250514",   # 复杂推理
    }
    return models.get(task_complexity, "claude-sonnet-4-20250514")
```

## 9. 与其他模型对比（Agent 场景）

| 能力           | Claude Sonnet    | GPT-4o          | Gemini 2.5 Pro  |
|---------------|------------------|-----------------|-----------------|
| 工具调用       | ✅ 原生          | ✅ 原生         | ✅ 原生          |
| 扩展思考       | ✅ Extended      | ✅ o1/o3        | ✅ Thinking     |
| 计算机操作     | ✅ Computer Use  | ❌              | ❌              |
| 多模态         | ✅ 图片+PDF      | ✅ 图片+音频    | ✅ 全模态        |
| 上下文窗口     | 200K             | 128K            | 1M              |
| 批量 API      | ✅ 50% 折扣     | ✅ 50% 折扣    | ❌              |
| 代码能力       | ★★★★★          | ★★★★★         | ★★★★           |
| 指令遵循       | ★★★★★          | ★★★★           | ★★★★           |
## 🎬 推荐视频资源

### 🌐 YouTube
- [Anthropic - Claude 4 Capabilities](https://www.youtube.com/watch?v=hkhDdcM5V94) — Claude能力介绍
- [Anthropic - Extended Thinking](https://www.youtube.com/watch?v=hkhDdcM5V94) — Claude扩展思考

### 📖 官方文档
- [Anthropic Docs](https://docs.anthropic.com/) — Claude官方文档
