# OpenAI 与 Claude API
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. OpenAI Chat Completions API

```python
from openai import OpenAI

client = OpenAI()  # 自动读取 OPENAI_API_KEY

# 基础调用
response = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {"role": "system", "content": "你是一个有帮助的助手"},
        {"role": "user", "content": "解释什么是 RAG"},
    ],
    temperature=0.7,
    max_tokens=1000,
)
print(response.choices[0].message.content)
print(f"Token 用量: {response.usage.prompt_tokens} + {response.usage.completion_tokens}")

# 流式响应
stream = client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": "写一首关于编程的诗"}],
    stream=True,
)
for chunk in stream:
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="", flush=True)
```

## 2. Anthropic Messages API

```python
import anthropic

client = anthropic.Anthropic()  # 自动读取 ANTHROPIC_API_KEY

# 基础调用
response = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=1024,
    system="你是一个专业的技术顾问",
    messages=[{"role": "user", "content": "对比 MCP 和 A2A 协议"}],
)
print(response.content[0].text)
print(f"Token: {response.usage.input_tokens} + {response.usage.output_tokens}")

# 流式响应
with client.messages.stream(
    model="claude-sonnet-4-20250514",
    max_tokens=1024,
    messages=[{"role": "user", "content": "解释 Transformer 架构"}],
) as stream:
    for text in stream.text_stream:
        print(text, end="", flush=True)
```

## 3. 多模态输入

```python
import base64

# OpenAI 图片输入
with open("chart.png", "rb") as f:
    image_data = base64.standard_b64encode(f.read()).decode()

response = client.chat.completions.create(
    model="gpt-4o",
    messages=[{
        "role": "user",
        "content": [
            {"type": "text", "text": "分析这张图表的趋势"},
            {"type": "image_url", "image_url": {
                "url": f"data:image/png;base64,{image_data}"
            }},
        ],
    }],
)

# Claude 图片输入
response = anthropic_client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=1024,
    messages=[{
        "role": "user",
        "content": [
            {"type": "image", "source": {
                "type": "base64",
                "media_type": "image/png",
                "data": image_data,
            }},
            {"type": "text", "text": "描述这张图片"},
        ],
    }],
)
```

## 4. Batch API（批量处理）

```python
# OpenAI Batch API：大批量请求，成本降低 50%
import json

# 1. 准备批量请求文件
requests = []
for i, question in enumerate(questions):
    requests.append({
        "custom_id": f"req-{i}",
        "method": "POST",
        "url": "/v1/chat/completions",
        "body": {
            "model": "gpt-4o-mini",
            "messages": [{"role": "user", "content": question}],
            "max_tokens": 500,
        },
    })

# 写入 JSONL 文件
with open("batch_input.jsonl", "w") as f:
    for req in requests:
        f.write(json.dumps(req) + "\n")

# 2. 上传并创建批量任务
batch_file = client.files.create(file=open("batch_input.jsonl", "rb"), purpose="batch")
batch = client.batches.create(
    input_file_id=batch_file.id,
    endpoint="/v1/chat/completions",
    completion_window="24h",
)

# 3. 查询状态
status = client.batches.retrieve(batch.id)
print(f"状态: {status.status}")  # validating → in_progress → completed

# 4. 获取结果
if status.status == "completed":
    result_file = client.files.content(status.output_file_id)
    results = [json.loads(line) for line in result_file.text.strip().split("\n")]
```

## 5. 成本优化策略

```python
# 策略 1：模型分级使用
def select_model(task_complexity: str) -> str:
    models = {
        "simple": "gpt-4o-mini",       # $0.15/1M input — 简单任务
        "medium": "gpt-4o",            # $2.50/1M input — 常规任务
        "complex": "claude-sonnet-4-20250514",  # 复杂推理
    }
    return models.get(task_complexity, "gpt-4o-mini")

# 策略 2：Prompt 缓存（Claude）
# 对于重复的 system prompt，Claude 自动缓存，节省 90% 输入成本
response = anthropic_client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=1024,
    system=[{
        "type": "text",
        "text": "很长的系统提示...",
        "cache_control": {"type": "ephemeral"},  # 启用缓存
    }],
    messages=[{"role": "user", "content": "问题"}],
)

# 策略 3：Token 用量监控
class TokenTracker:
    def __init__(self):
        self.total_input = 0
        self.total_output = 0

    def track(self, usage):
        self.total_input += usage.prompt_tokens
        self.total_output += usage.completion_tokens

    @property
    def estimated_cost(self) -> float:
        # GPT-4o 价格
        return (self.total_input * 2.5 + self.total_output * 10) / 1_000_000
```
