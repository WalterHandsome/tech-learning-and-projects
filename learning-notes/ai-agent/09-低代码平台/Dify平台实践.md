# Dify 平台实践

## 1. Dify 概述

Dify 是一个开源的 LLM 应用开发平台，支持可视化编排 Agent 工作流、知识库管理和 API 发布。

```
┌─────────────────────────────────────────┐
│              Dify 平台                    │
├──────────┬──────────┬──────────────────┤
│ Workflow  │ Knowledge│  Agent Mode      │
│ 工作流编排 │ 知识库   │  Agent 模式      │
├──────────┼──────────┼──────────────────┤
│ 可视化拖拽│ 文档导入  │ ReAct/FC        │
│ 条件分支  │ 自动分块  │ 工具调用         │
│ 代码节点  │ 向量检索  │ 多轮对话         │
└──────────┴──────────┴──────────────────┘
```

## 2. 工作流编排

```python
# Dify Workflow 通过 API 调用
import httpx

DIFY_API = "http://localhost/v1"
API_KEY = "app-xxx"

# 执行工作流
async def run_workflow(inputs: dict) -> dict:
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{DIFY_API}/workflows/run",
            headers={"Authorization": f"Bearer {API_KEY}"},
            json={
                "inputs": inputs,
                "response_mode": "blocking",  # blocking / streaming
                "user": "user-123",
            },
        )
        return response.json()

result = await run_workflow({"query": "分析上月销售数据"})
print(result["data"]["outputs"])

# 流式执行
async def run_workflow_stream(inputs: dict):
    async with httpx.AsyncClient() as client:
        async with client.stream(
            "POST", f"{DIFY_API}/workflows/run",
            headers={"Authorization": f"Bearer {API_KEY}"},
            json={"inputs": inputs, "response_mode": "streaming", "user": "user-123"},
        ) as response:
            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    print(line[6:])
```

## 3. 知识库管理

```python
# 创建知识库
async def create_knowledge_base(name: str) -> dict:
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{DIFY_API}/datasets",
            headers={"Authorization": f"Bearer {API_KEY}"},
            json={"name": name},
        )
        return response.json()

# 上传文档到知识库
async def upload_document(dataset_id: str, file_path: str) -> dict:
    async with httpx.AsyncClient() as client:
        with open(file_path, "rb") as f:
            response = await client.post(
                f"{DIFY_API}/datasets/{dataset_id}/document/create_by_file",
                headers={"Authorization": f"Bearer {API_KEY}"},
                files={"file": f},
                data={
                    "data": '{"indexing_technique":"high_quality","process_rule":{"mode":"automatic"}}',
                },
            )
        return response.json()

# 检索知识库
async def search_knowledge(dataset_id: str, query: str) -> list:
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{DIFY_API}/datasets/{dataset_id}/retrieve",
            headers={"Authorization": f"Bearer {API_KEY}"},
            json={"query": query, "top_k": 5, "score_threshold": 0.5},
        )
        return response.json()["records"]
```

## 4. Agent 模式

```python
# Dify Agent 对话 API
async def chat_with_agent(query: str, conversation_id: str = "") -> dict:
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{DIFY_API}/chat-messages",
            headers={"Authorization": f"Bearer {API_KEY}"},
            json={
                "inputs": {},
                "query": query,
                "response_mode": "blocking",
                "conversation_id": conversation_id,  # 空字符串=新对话
                "user": "user-123",
            },
        )
        data = response.json()
        return {
            "answer": data["answer"],
            "conversation_id": data["conversation_id"],
        }

# 多轮对话
r1 = await chat_with_agent("你好，我想了解退货政策")
r2 = await chat_with_agent("具体流程是什么？", r1["conversation_id"])
```

## 5. 私有部署

```yaml
# docker-compose.yaml（Dify 私有部署）
version: '3'
services:
  api:
    image: langgenius/dify-api:latest
    environment:
      - SECRET_KEY=your-secret-key
      - DB_USERNAME=postgres
      - DB_PASSWORD=difypassword
      - REDIS_HOST=redis
      - OPENAI_API_KEY=sk-xxx
    ports:
      - "5001:5001"

  web:
    image: langgenius/dify-web:latest
    ports:
      - "3000:3000"

  db:
    image: postgres:15
    environment:
      - POSTGRES_PASSWORD=difypassword
      - POSTGRES_DB=dify

  redis:
    image: redis:7

  weaviate:
    image: semitechnologies/weaviate:latest
```

```bash
# 启动 Dify
docker compose up -d

# 访问 http://localhost:3000 进入管理界面
# 首次访问需要设置管理员账号
```
