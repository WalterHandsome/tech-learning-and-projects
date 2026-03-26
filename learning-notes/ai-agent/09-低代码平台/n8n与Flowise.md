# n8n 与 Flowise

## 1. n8n 概述

n8n 是一个开源的工作流自动化平台，内置 AI Agent 节点，可将 LLM 能力与 400+ 应用集成。

```
┌─────────────────────────────────────────┐
│              n8n 平台                     │
├──────────┬──────────┬──────────────────┤
│ 触发器    │ AI 节点   │  集成节点         │
├──────────┼──────────┼──────────────────┤
│ Webhook  │ AI Agent  │ Slack/Email      │
│ 定时任务  │ LLM Chain│ 数据库/API       │
│ 事件监听  │ RAG      │ GitHub/Jira      │
└──────────┴──────────┴──────────────────┘
```

## 2. n8n AI Agent 工作流

```python
# n8n 通过 API 触发工作流
import httpx

N8N_API = "http://localhost:5678/api/v1"
N8N_KEY = "n8n-api-key"

# 触发 Webhook 工作流
async def trigger_n8n_workflow(webhook_url: str, data: dict) -> dict:
    async with httpx.AsyncClient() as client:
        response = await client.post(webhook_url, json=data)
        return response.json()

# 示例：触发 AI 客服工作流
result = await trigger_n8n_workflow(
    "http://localhost:5678/webhook/customer-service",
    {"query": "我的订单什么时候发货？", "user_id": "user-123"},
)
```

```json
// n8n AI Agent 工作流配置示例
{
  "nodes": [
    {
      "type": "n8n-nodes-base.webhook",
      "name": "Webhook 触发",
      "parameters": {"path": "customer-service", "httpMethod": "POST"}
    },
    {
      "type": "@n8n/n8n-nodes-langchain.agent",
      "name": "AI Agent",
      "parameters": {
        "agent": "openAiFunctionsAgent",
        "text": "={{ $json.query }}",
        "options": {"systemMessage": "你是客服助手，帮助用户解决问题。"}
      }
    },
    {
      "type": "@n8n/n8n-nodes-langchain.toolHttpRequest",
      "name": "订单查询工具",
      "parameters": {
        "url": "https://api.example.com/orders",
        "description": "查询用户订单信息"
      }
    },
    {
      "type": "n8n-nodes-base.slack",
      "name": "发送 Slack 通知",
      "parameters": {"channel": "#customer-service"}
    }
  ]
}
```

## 3. n8n 自动化集成

```python
# n8n 工作流：文档更新 → 知识库同步 → 通知
# 通过 n8n API 管理工作流

async def create_workflow(workflow_data: dict) -> dict:
    """创建 n8n 工作流"""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{N8N_API}/workflows",
            headers={"X-N8N-API-KEY": N8N_KEY},
            json=workflow_data,
        )
        return response.json()

async def execute_workflow(workflow_id: str, data: dict = None) -> dict:
    """手动执行工作流"""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{N8N_API}/workflows/{workflow_id}/run",
            headers={"X-N8N-API-KEY": N8N_KEY},
            json={"data": data or {}},
        )
        return response.json()

# 查看执行历史
async def get_executions(workflow_id: str) -> list:
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{N8N_API}/executions",
            headers={"X-N8N-API-KEY": N8N_KEY},
            params={"workflowId": workflow_id, "limit": 10},
        )
        return response.json()["data"]
```

## 4. Flowise 概述

Flowise 是一个可视化的 LangChain/LlamaIndex 构建工具，通过拖拽节点创建 LLM 应用。

```
Flowise 核心特点：
├── 可视化 LangChain — 拖拽式构建 Chain/Agent
├── 内置组件丰富 — LLM、向量库、工具、记忆
├── API 一键发布 — 自动生成 REST API
└── 嵌入式部署 — 可嵌入到现有网站
```

## 5. Flowise API 调用

```python
# Flowise 自动生成 API 端点
FLOWISE_API = "http://localhost:3000/api/v1"

# 调用 Chatflow
async def chat_with_flowise(chatflow_id: str, question: str, session_id: str = "") -> str:
    async with httpx.AsyncClient() as client:
        payload = {
            "question": question,
            "overrideConfig": {
                "sessionId": session_id,  # 会话隔离
            },
        }
        response = await client.post(
            f"{FLOWISE_API}/prediction/{chatflow_id}",
            json=payload,
        )
        return response.json()["text"]

# 上传文档到 Flowise 向量库
async def upload_to_flowise(chatflow_id: str, file_path: str) -> dict:
    async with httpx.AsyncClient() as client:
        with open(file_path, "rb") as f:
            response = await client.post(
                f"{FLOWISE_API}/vector/upsert/{chatflow_id}",
                files={"files": f},
            )
        return response.json()

answer = await chat_with_flowise("chatflow-id", "什么是 RAG？")
```

## 6. 部署与对比

```bash
# n8n Docker 部署
docker run -d --name n8n -p 5678:5678 \
  -v n8n_data:/home/node/.n8n \
  -e N8N_AI_ENABLED=true \
  n8nio/n8n

# Flowise Docker 部署
docker run -d --name flowise -p 3000:3000 \
  -v flowise_data:/root/.flowise \
  flowiseai/flowise
```

| 特性 | n8n | Flowise |
|------|-----|---------|
| 定位 | 工作流自动化 + AI | 可视化 LangChain |
| AI 能力 | Agent 节点 | Chain/Agent 构建 |
| 集成数量 | 400+ 应用 | LangChain 组件 |
| 触发方式 | Webhook/定时/事件 | API 调用 |
| 适用场景 | 业务自动化 + AI | 纯 LLM 应用 |
| 学习曲线 | 中 | 低 |
