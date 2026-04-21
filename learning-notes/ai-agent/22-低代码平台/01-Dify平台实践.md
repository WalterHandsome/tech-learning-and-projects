# Dify 平台实践
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

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
## 6. 2026 版本演进

> 🔄 更新于 2026-04-21

<!-- version-check: Dify v1.13.2, checked 2026-04-21 -->

### Dify v1.13.x：Human Input 节点与工作流增强

Dify 于 2026-03 发布 v1.13.0，当前稳定版为 v1.13.2。核心新特性：

**Human Input 节点**（v1.13.0）：
- 在工作流关键决策点插入人工审核节点，暂停执行等待人类输入
- 审核者可查看 AI 输出、编辑变量、选择预定义决策路径
- 支持通过特定渠道（邮件、Slack 等）发送审核请求表单
- 适用场景：内容审核、合规检查、高风险操作确认

**工作流画布改进**（v1.13.1）：
- 边缘右键菜单支持直接删除连接
- 切换节点类型时保留现有连接
- 嵌入式聊天输入支持可配置发送键（Enter vs Shift+Enter）

### Dify 融资与生态

- **$3000 万 Pre-A 轮融资**（2026-03-10）：估值 $1.8 亿，由 HSG 领投
- 2,000+ 团队、280+ 企业使用
- GitHub Stars 持续增长（113K+）
- **Beehive 架构重构**：模块化设计，各模块独立运行，开发者可按需调整

### Dify 2.0 预览

Dify v2.0.0-beta.1 已在 GitHub Discussions 中发布，主题为"Orchestrating Knowledge, Powering Workflows"，预计将带来知识库编排和工作流能力的重大升级。

### 平台对比更新（2026）

| 特性 | Dify | n8n | Coze | FastGPT |
|------|------|-----|------|---------|
| 最新版本 | v1.13.2 | v2.x | v2.5 | 持续更新 |
| 定位 | LLM 应用开发平台 | 工作流自动化 + AI | AI Bot 构建平台 | 知识库问答系统 |
| Human-in-the-Loop | ✅（v1.13 原生） | ✅（Wait 节点） | 有限 | 有限 |
| 开源 | ✅ Apache 2.0 | ✅ 可持续许可 | ✅ Coze Studio | ✅ Apache 2.0 |
| 融资 | $3000 万 | $1.2 亿+ | 字节跳动 | 社区驱动 |

> 来源：[Dify Blog](https://dify.ai/blog)、[Dify GitHub Releases](https://github.com/langgenius/dify/releases)、[BusinessWire](https://www.businesswire.com/news/home/20260309511426/en/)

## 🎬 推荐视频资源

- [Dify Official - Getting Started](https://www.youtube.com/watch?v=1gNMnQH0vRc) — Dify官方入门教程
- [AI Jason - Dify Tutorial](https://www.youtube.com/watch?v=CgMd0zsz_BQ) — Dify平台实战讲解
