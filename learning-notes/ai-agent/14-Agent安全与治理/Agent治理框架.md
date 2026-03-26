# Agent 治理框架

## 1. 四大治理支柱

```
┌──────────────── Agent 治理框架 ────────────────┐
│                                                 │
│  ┌──────────┐  ┌──────────┐  ┌──────────────┐ │
│  │ 决策层    │  │ 人机协作  │  │ 审计追踪     │ │
│  │ Decision │  │ HITL     │  │ Audit Trail │ │
│  └──────────┘  └──────────┘  └──────────────┘ │
│                ┌──────────┐                     │
│                │ 回滚机制  │                     │
│                │ Rollback │                     │
│                └──────────┘                     │
│                                                 │
│  ┌─────────────────────────────────────────┐   │
│  │  成本治理 │ 合规 │ 监控告警 │ 生命周期    │   │
│  └─────────────────────────────────────────┘   │
└────────────────────────────────────────────────┘
```

### 决策层（Decision Layer）

```python
class DecisionPolicy:
    """Agent 决策策略"""

    def __init__(self):
        self.rules = []

    def add_rule(self, condition, action, requires_approval=False):
        self.rules.append({
            "condition": condition,
            "action": action,
            "requires_approval": requires_approval,
        })

    def evaluate(self, context: dict) -> dict:
        for rule in self.rules:
            if rule["condition"](context):
                if rule["requires_approval"]:
                    return {"action": "await_approval", "rule": rule}
                return {"action": "execute", "rule": rule}
        return {"action": "deny", "reason": "no matching rule"}

# 配置决策策略
policy = DecisionPolicy()
policy.add_rule(
    condition=lambda ctx: ctx["amount"] < 1000,
    action="auto_approve",
)
policy.add_rule(
    condition=lambda ctx: ctx["amount"] >= 1000,
    action="process_payment",
    requires_approval=True,  # 大额操作需人工审批
)
```

### Human-in-the-Loop

```python
from enum import Enum

class ApprovalLevel(Enum):
    AUTO = "auto"           # 自动执行
    NOTIFY = "notify"       # 执行后通知
    APPROVE = "approve"     # 执行前审批
    BLOCK = "block"         # 禁止执行

# 操作分级
OPERATION_LEVELS = {
    "read_data": ApprovalLevel.AUTO,
    "send_email": ApprovalLevel.NOTIFY,
    "modify_database": ApprovalLevel.APPROVE,
    "delete_production": ApprovalLevel.BLOCK,
}

async def execute_with_governance(operation: str, params: dict):
    level = OPERATION_LEVELS.get(operation, ApprovalLevel.APPROVE)

    if level == ApprovalLevel.BLOCK:
        raise PermissionError(f"操作 {operation} 被禁止")

    if level == ApprovalLevel.APPROVE:
        approved = await request_human_approval(operation, params)
        if not approved:
            return {"status": "rejected"}

    result = await execute_operation(operation, params)

    if level == ApprovalLevel.NOTIFY:
        await notify_admin(operation, params, result)

    return result
```

## 2. 合规要求

```
GDPR 合规：
├─ 数据最小化：Agent 只处理必要的个人数据
├─ 目的限制：明确 Agent 处理数据的目的
├─ 存储限制：设置数据保留期限，自动清理
├─ 用户权利：支持数据访问、删除、导出请求
└─ 数据保护影响评估（DPIA）

SOC2 合规：
├─ 访问控制：Agent 身份认证和授权
├─ 变更管理：Agent 配置变更审批流程
├─ 风险评估：定期评估 Agent 安全风险
├─ 监控告警：持续监控 Agent 行为
└─ 事件响应：Agent 安全事件处理流程
```

## 3. 成本治理

```python
class CostGovernor:
    """Agent 成本治理"""

    def __init__(self, daily_budget: float, monthly_budget: float):
        self.daily_budget = daily_budget
        self.monthly_budget = monthly_budget

    async def check_budget(self, agent_id: str, estimated_cost: float) -> bool:
        """检查是否超出预算"""
        daily_spent = await self.get_daily_spend(agent_id)
        monthly_spent = await self.get_monthly_spend(agent_id)

        if daily_spent + estimated_cost > self.daily_budget:
            await self.alert(f"Agent {agent_id} 接近日预算上限")
            return False
        if monthly_spent + estimated_cost > self.monthly_budget:
            await self.alert(f"Agent {agent_id} 接近月预算上限")
            return False
        return True

    async def track_usage(self, agent_id: str, usage: dict):
        """记录用量"""
        record = {
            "agent_id": agent_id,
            "input_tokens": usage["input_tokens"],
            "output_tokens": usage["output_tokens"],
            "cost_usd": usage["cost"],
            "model": usage["model"],
            "timestamp": datetime.utcnow(),
        }
        await self.db.insert("agent_usage", record)

# 使用
governor = CostGovernor(daily_budget=50.0, monthly_budget=1000.0)
```

## 4. 速率限制与配额

```python
import time
from collections import defaultdict

class RateLimiter:
    """Agent 速率限制"""

    def __init__(self):
        self.limits = {
            "requests_per_minute": 60,
            "tokens_per_minute": 100000,
            "tool_calls_per_hour": 500,
        }
        self.counters = defaultdict(list)

    def check_limit(self, agent_id: str, limit_type: str) -> bool:
        now = time.time()
        window = 60 if "minute" in limit_type else 3600
        key = f"{agent_id}:{limit_type}"

        # 清理过期记录
        self.counters[key] = [t for t in self.counters[key] if now - t < window]

        if len(self.counters[key]) >= self.limits[limit_type]:
            return False  # 超出限制

        self.counters[key].append(now)
        return True
```

## 5. Agent 生命周期管理

```
┌─────────────────────────────────────────────┐
│            Agent 生命周期                      │
│                                               │
│  开发 → 测试 → 审批 → 部署 → 监控 → 退役      │
│                                               │
│  开发阶段：                                    │
│  ├─ 定义 Agent 目标和权限范围                   │
│  ├─ 开发和单元测试                             │
│  └─ 安全审查                                   │
│                                               │
│  部署阶段：                                    │
│  ├─ 灰度发布（金丝雀部署）                      │
│  ├─ A/B 测试                                  │
│  └─ 生产环境监控                               │
│                                               │
│  运行阶段：                                    │
│  ├─ 持续监控性能和成本                          │
│  ├─ 定期审查权限和行为                          │
│  └─ 版本更新和回滚                             │
│                                               │
│  退役阶段：                                    │
│  ├─ 数据归档和清理                             │
│  ├─ 权限回收                                   │
│  └─ 文档归档                                   │
└─────────────────────────────────────────────┘
```

## 6. 监控与告警

```python
# Agent 监控指标
METRICS = {
    "performance": [
        "response_latency_p50",    # 响应延迟 P50
        "response_latency_p99",    # 响应延迟 P99
        "task_completion_rate",    # 任务完成率
        "tool_call_success_rate",  # 工具调用成功率
    ],
    "cost": [
        "tokens_per_request",      # 每请求 Token 数
        "cost_per_task",           # 每任务成本
        "daily_total_cost",        # 日总成本
    ],
    "safety": [
        "guardrail_trigger_rate",  # 护栏触发率
        "error_rate",              # 错误率
        "unauthorized_access",     # 未授权访问次数
    ],
}

# 告警规则
ALERTS = [
    {"metric": "error_rate", "threshold": 0.05, "action": "notify"},
    {"metric": "daily_total_cost", "threshold": 100, "action": "throttle"},
    {"metric": "unauthorized_access", "threshold": 1, "action": "block_and_alert"},
    {"metric": "response_latency_p99", "threshold": 30000, "action": "notify"},
]
```

## 7. 事件响应

```
Agent 事件响应流程：
├─ 检测：监控系统发现异常
├─ 分类：判断严重程度（P0-P3）
├─ 响应：
│   ├─ P0（紧急）：立即停止 Agent，通知 On-Call
│   ├─ P1（严重）：限制 Agent 权限，1h 内响应
│   ├─ P2（一般）：记录问题，24h 内处理
│   └─ P3（低）：下个迭代处理
├─ 修复：定位根因，修复问题
├─ 恢复：验证修复，恢复服务
└─ 复盘：事后分析，更新策略
```

## 8. 企业部署检查清单

```
□ 身份与认证
  □ Agent 使用独立 Service Account
  □ API Key 定期轮换（≤90天）
  □ OAuth2 Token 短期有效（≤1h）

□ 权限控制
  □ 最小权限原则已实施
  □ 敏感操作需人工审批
  □ 权限定期审查（季度）

□ 数据安全
  □ PII 检测和脱敏
  □ 数据加密（传输+存储）
  □ 数据保留策略已配置

□ 监控与审计
  □ 操作审计日志已启用
  □ 性能监控已配置
  □ 成本告警已设置

□ 应急响应
  □ 回滚机制已测试
  □ 紧急停止开关已就绪
  □ 事件响应流程已文档化

□ 合规
  □ GDPR/隐私合规已评估
  □ 安全审查已通过
  □ 第三方依赖已审计
```
