# Mem0 记忆层
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. 概述

Mem0 是为 AI Agent 设计的智能记忆层，可为任何 LLM 应用添加持久化记忆能力。Y Combinator 孵化，获得 $24M 融资。

```
┌─────────────────────────────────────────┐
│              AI 应用 / Agent             │
├─────────────────────────────────────────┤
│              Mem0 记忆层                 │
│  ┌──────────┐ ┌────────┐ ┌──────────┐  │
│  │自动提取   │ │语义搜索 │ │图记忆     │  │
│  │Memory    │ │Search  │ │Graph     │  │
│  │Extract   │ │        │ │Memory    │  │
│  └──────────┘ └────────┘ └──────────┘  │
├─────────────────────────────────────────┤
│  向量存储 │ 图数据库 │ KV 存储           │
└─────────────────────────────────────────┘
```

核心特性：
- 自动从对话中提取记忆（偏好、事实、关系）
- 语义搜索相关记忆
- 图记忆追踪实体关系
- 支持 user / agent / session 三级记忆

## 2. 快速开始

```bash
pip install mem0ai
```

```python
from mem0 import Memory

# 初始化（默认使用 OpenAI）
m = Memory()

# 添加记忆（自动提取关键信息）
m.add("我是一名 Python 后端开发者，喜欢用 FastAPI", user_id="alice")
m.add("我正在学习 AI Agent 开发，用的是 LangGraph", user_id="alice")
m.add("我的项目用 PostgreSQL 做数据库", user_id="alice")

# 搜索相关记忆
results = m.search("她用什么技术栈？", user_id="alice")
# → [{"memory": "Python 后端开发者，使用 FastAPI"},
#    {"memory": "使用 PostgreSQL 数据库"},
#    {"memory": "正在学习 LangGraph"}]

# 获取所有记忆
all_memories = m.get_all(user_id="alice")

# 更新记忆
m.update(memory_id="xxx", data="她已转向全栈开发")

# 删除记忆
m.delete(memory_id="xxx")
```

## 3. 自定义配置

```python
from mem0 import Memory

config = {
    "llm": {
        "provider": "openai",
        "config": {"model": "gpt-4o-mini", "temperature": 0}
    },
    "embedder": {
        "provider": "openai",
        "config": {"model": "text-embedding-3-small"}
    },
    "vector_store": {
        "provider": "qdrant",
        "config": {
            "host": "localhost",
            "port": 6333,
            "collection_name": "agent_memories",
        }
    },
    "graph_store": {
        "provider": "neo4j",
        "config": {
            "url": "bolt://localhost:7687",
            "username": "neo4j",
            "password": "password",
        }
    },
    "version": "v1.1",
}

m = Memory.from_config(config)
```

## 4. 图记忆（Graph Memory）

追踪实体间的关系，构建知识图谱。

```python
# 启用图记忆
config = {
    "graph_store": {
        "provider": "neo4j",
        "config": {"url": "bolt://localhost:7687", "username": "neo4j", "password": "pass"}
    },
    "version": "v1.1",
}
m = Memory.from_config(config)

# 添加包含关系的信息
m.add("张三是 AI 团队的负责人，他管理李四和王五", user_id="org")
m.add("李四负责 RAG 模块开发，王五负责 Agent 框架", user_id="org")
m.add("AI 团队属于技术部，技术部总监是赵六", user_id="org")

# 图记忆自动提取实体和关系：
# 张三 --[管理]--> 李四
# 张三 --[管理]--> 王五
# 李四 --[负责]--> RAG 模块
# AI 团队 --[属于]--> 技术部
# 赵六 --[总监]--> 技术部
```

## 5. 与 LangChain 集成

```python
from langchain_openai import ChatOpenAI
from mem0 import Memory

llm = ChatOpenAI(model="gpt-4o")
memory = Memory()

def chat_with_memory(user_input: str, user_id: str) -> str:
    # 检索相关记忆
    relevant = memory.search(user_input, user_id=user_id)
    memory_context = "\n".join(f"- {r['memory']}" for r in relevant)

    # 构建带记忆的提示
    messages = [
        {"role": "system", "content": f"你是智能助手。用户相关记忆：\n{memory_context}"},
        {"role": "user", "content": user_input},
    ]

    response = llm.invoke(messages).content

    # 保存新记忆
    memory.add(f"用户: {user_input}\n助手: {response}", user_id=user_id)

    return response

# 多轮对话自动积累记忆
chat_with_memory("我下周要去东京出差", user_id="bob")
chat_with_memory("帮我推荐东京的餐厅", user_id="bob")  # 自动关联出差上下文
```

## 6. 与 CrewAI 集成

```python
from crewai import Agent, Task, Crew
from mem0 import Memory

memory = Memory()

# 为 Agent 注入长期记忆
def create_agent_with_memory(role: str, user_id: str) -> Agent:
    # 获取历史记忆
    memories = memory.get_all(user_id=user_id)
    memory_str = "\n".join(f"- {m['memory']}" for m in memories)

    return Agent(
        role=role,
        goal=f"基于历史记忆提供个性化服务",
        backstory=f"你了解用户的以下信息：\n{memory_str}",
        llm="gpt-4o",
    )

assistant = create_agent_with_memory("个人助理", user_id="alice")
```

## 7. 记忆类型

```
Mem0 自动识别的记忆类型：

用户偏好（Preferences）
├─ "我喜欢简洁的代码风格"
├─ "我偏好 TypeScript 而非 JavaScript"
└─ "回答请用中文"

事实信息（Facts）
├─ "用户是高级工程师"
├─ "项目使用 AWS 部署"
└─ "团队有 5 个人"

关系（Relationships）
├─ "张三是用户的经理"
├─ "项目 A 依赖项目 B"
└─ "用户属于 AI 团队"

时间相关（Temporal）
├─ "下周三有产品评审"
├─ "上个月完成了 v2.0 发布"
└─ "每周五做代码审查"
```

## 8. 自托管 vs 云服务

```
自托管（Open Source）：
├─ 完全控制数据
├─ 需要自行管理向量数据库和图数据库
├─ 适合数据敏感场景
└─ pip install mem0ai

云服务（Mem0 Platform）：
├─ 托管基础设施
├─ API 访问
├─ 自动扩缩容
└─ from mem0 import MemoryClient
    client = MemoryClient(api_key="xxx")
```

```python
# 云服务用法
from mem0 import MemoryClient

client = MemoryClient(api_key="m0-xxx")
client.add("用户偏好深色主题", user_id="u1")
results = client.search("主题偏好", user_id="u1")
```

## 9. 与其他记忆方案对比

| 特性         | Mem0          | Letta/MemGPT  | Zep           | LangMem       |
|-------------|---------------|---------------|---------------|---------------|
| 记忆提取     | 自动           | Agent 自编辑   | 自动           | 手动/自动      |
| 图记忆       | ✅ Neo4j      | ❌             | ✅ 时序图      | ❌             |
| 语义搜索     | ✅             | ✅             | ✅             | ✅             |
| 多框架集成   | ✅ 广泛        | ✅ SDK         | ✅ LangChain  | ✅ LangGraph  |
| 自托管       | ✅             | ✅             | ✅             | ✅             |
| 云服务       | ✅             | ✅             | ✅             | ❌             |
| 学习曲线     | 低             | 中             | 低             | 中             |
| 适用场景     | 通用记忆层      | 有状态Agent    | 对话记忆       | LangGraph生态 |
