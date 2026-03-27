# Agent 身份与权限
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. 概述

Agent 身份管理是 AI Agent 安全的基础。与传统用户身份不同，Agent 需要处理"代表谁行动"、"拥有什么权限"、"如何证明身份"等独特问题。

```
┌──────────── Agent 身份与权限体系 ────────────┐
│                                               │
│  ┌─────────┐  ┌──────────┐  ┌─────────────┐ │
│  │ 身份认证 │  │ 权限控制  │  │ 审计追踪    │ │
│  │ AuthN   │  │ AuthZ    │  │ Audit      │ │
│  ├─────────┤  ├──────────┤  ├─────────────┤ │
│  │ OAuth2  │  │ RBAC     │  │ 操作日志    │ │
│  │ API Key │  │ ABAC     │  │ 访问记录    │ │
│  │ mTLS    │  │ 最小权限  │  │ 异常检测    │ │
│  └─────────┘  └──────────┘  └─────────────┘ │
└──────────────────────────────────────────────┘
```

## 2. OAuth2 for Agents

```python
# Agent 使用 OAuth2 Client Credentials 获取访问令牌
import httpx

async def get_agent_token(client_id: str, client_secret: str) -> str:
    """Agent 获取 OAuth2 访问令牌"""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://auth.example.com/oauth2/token",
            data={
                "grant_type": "client_credentials",
                "client_id": client_id,
                "client_secret": client_secret,
                "scope": "agent:read agent:write",
            },
        )
        return response.json()["access_token"]

# Agent 代表用户操作（On-Behalf-Of 流程）
async def get_delegated_token(agent_token: str, user_token: str) -> str:
    """Agent 代表用户获取委托令牌"""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://auth.example.com/oauth2/token",
            data={
                "grant_type": "urn:ietf:params:oauth:grant-type:token-exchange",
                "subject_token": user_token,
                "actor_token": agent_token,
                "scope": "user:calendar user:email",
            },
        )
        return response.json()["access_token"]
```

## 3. API Key 管理与轮换

```python
import secrets
import hashlib
from datetime import datetime, timedelta

class AgentKeyManager:
    """Agent API Key 管理"""

    def create_key(self, agent_id: str, expires_days: int = 90) -> dict:
        """创建 API Key（带过期时间）"""
        raw_key = f"agent_{secrets.token_urlsafe(32)}"
        key_hash = hashlib.sha256(raw_key.encode()).hexdigest()
        return {
            "key": raw_key,           # 只返回一次，不存储明文
            "key_hash": key_hash,     # 存储哈希值
            "agent_id": agent_id,
            "expires_at": datetime.utcnow() + timedelta(days=expires_days),
            "created_at": datetime.utcnow(),
        }

    def rotate_key(self, agent_id: str) -> dict:
        """轮换 Key：创建新 Key，旧 Key 延长 24h 后失效"""
        new_key = self.create_key(agent_id)
        self.extend_old_key(agent_id, hours=24)  # 平滑过渡
        return new_key

    def validate_key(self, raw_key: str) -> bool:
        """验证 API Key"""
        key_hash = hashlib.sha256(raw_key.encode()).hexdigest()
        record = self.db.find_by_hash(key_hash)
        if not record:
            return False
        if record["expires_at"] < datetime.utcnow():
            return False
        return True
```

## 4. RBAC（基于角色的访问控制）

```python
from enum import Enum
from dataclasses import dataclass

class Permission(Enum):
    READ_DATA = "read:data"
    WRITE_DATA = "write:data"
    EXECUTE_CODE = "execute:code"
    SEND_EMAIL = "send:email"
    ACCESS_DATABASE = "access:database"
    MANAGE_USERS = "manage:users"

@dataclass
class AgentRole:
    name: str
    permissions: set[Permission]

# 预定义角色
ROLES = {
    "reader": AgentRole("reader", {
        Permission.READ_DATA,
    }),
    "worker": AgentRole("worker", {
        Permission.READ_DATA,
        Permission.WRITE_DATA,
        Permission.EXECUTE_CODE,
    }),
    "admin": AgentRole("admin", {
        Permission.READ_DATA,
        Permission.WRITE_DATA,
        Permission.EXECUTE_CODE,
        Permission.SEND_EMAIL,
        Permission.ACCESS_DATABASE,
        Permission.MANAGE_USERS,
    }),
}

def check_permission(agent_role: str, required: Permission) -> bool:
    """检查 Agent 是否有权限"""
    role = ROLES.get(agent_role)
    if not role:
        return False
    return required in role.permissions

# 使用示例
assert check_permission("worker", Permission.READ_DATA) == True
assert check_permission("reader", Permission.EXECUTE_CODE) == False
```

## 5. 最小权限原则

```python
# 工具级别的权限声明
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("secure-tools")

@mcp.tool(permissions=["read:database"])
def query_data(sql: str) -> list:
    """只读查询（最小权限）"""
    if not sql.strip().upper().startswith("SELECT"):
        raise PermissionError("只允许 SELECT 查询")
    return db.execute(sql)

@mcp.tool(permissions=["write:database"], requires_approval=True)
def modify_data(sql: str) -> str:
    """写操作需要人工审批"""
    return db.execute(sql)
```

```
最小权限实践：
├─ 只授予 Agent 完成任务所需的最小权限集
├─ 读写分离：默认只读，写操作需额外授权
├─ 时间限制：临时权限自动过期
├─ 范围限制：限制可访问的数据范围
└─ 操作限制：限制单次操作的影响范围
```

## 6. Agent-to-Agent 认证（A2A Auth）

```python
# A2A 协议中的认证机制
# Agent Card 中声明认证要求
agent_card = {
    "name": "data-agent",
    "url": "https://data-agent.example.com",
    "authentication": {
        "schemes": ["bearer", "oauth2"],
        "oauth2": {
            "token_url": "https://auth.example.com/token",
            "scopes": ["agent:invoke"],
        },
    },
}

# Agent 间调用时携带认证信息
import httpx

async def call_remote_agent(task: dict, auth_token: str):
    """调用远程 Agent（带认证）"""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://data-agent.example.com/tasks",
            json=task,
            headers={"Authorization": f"Bearer {auth_token}"},
        )
        return response.json()
```

## 7. 审计日志

```python
import json
from datetime import datetime

class AgentAuditLogger:
    """Agent 操作审计日志"""

    def log(self, event: dict):
        record = {
            "timestamp": datetime.utcnow().isoformat(),
            "agent_id": event["agent_id"],
            "action": event["action"],
            "resource": event["resource"],
            "result": event["result"],
            "user_context": event.get("on_behalf_of"),
            "ip_address": event.get("ip"),
            "metadata": event.get("metadata", {}),
        }
        # 写入审计日志（不可篡改）
        self.append_to_audit_log(record)

# 使用
logger = AgentAuditLogger()
logger.log({
    "agent_id": "agent-data-001",
    "action": "database.query",
    "resource": "orders_table",
    "result": "success",
    "on_behalf_of": "user-123",
    "metadata": {"rows_returned": 42, "query_time_ms": 150},
})
```

## 8. 云厂商身份方案

| 维度 | AWS IAM | Azure AD | GCP IAM |
|------|---------|----------|---------|
| Agent 身份 | IAM Role | Service Principal | Service Account |
| 认证方式 | STS AssumeRole | OAuth2 Client Credentials | Workload Identity |
| 权限模型 | Policy-based | RBAC + Conditional | IAM Roles |
| 临时凭证 | ✅ STS Token | ✅ Managed Identity | ✅ Short-lived Token |
| 跨服务 | Cross-account Role | Cross-tenant | Cross-project |
| Agent 专用 | Bedrock Agent Role | AI Foundry Identity | Vertex AI SA |
## 🎬 推荐视频资源

### 🌐 YouTube
- [DeepLearning.AI - Quality and Safety for LLM Applications](https://www.deeplearning.ai/short-courses/quality-safety-llm-applications/) — 包含权限控制章节（免费）
- [OWASP - LLM Security Top 10](https://www.youtube.com/watch?v=4YOpILi9Oxs) — LLM安全风险

### 📖 官方文档
- [OWASP LLM Top 10](https://owasp.org/www-project-top-10-for-large-language-model-applications/) — OWASP LLM安全指南
