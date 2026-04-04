# CQRS 与事件溯源
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. CQRS 概述

CQRS（Command Query Responsibility Segregation）将读操作和写操作分离为不同的模型，各自独立优化。

```
┌──────────── 传统 vs CQRS ────────────┐
│                                       │
│  传统 CRUD：                           │
│  客户端 ──→ Service ──→ 同一个数据库   │
│  （读写用同一个模型，互相制约）         │
│                                       │
│  CQRS：                               │
│  ┌──────────┐     ┌──────────────┐   │
│  │ Command   │     │ Query        │   │
│  │ (写模型)  │     │ (读模型)      │   │
│  └─────┬────┘     └──────┬───────┘   │
│        │                  │           │
│  ┌─────┴────┐     ┌──────┴───────┐   │
│  │ 写数据库  │ ──→ │ 读数据库      │   │
│  │ (规范化)  │ 同步 │ (反规范化)    │   │
│  └──────────┘     └──────────────┘   │
│                                       │
│  写模型：保证数据一致性，规范化存储     │
│  读模型：优化查询性能，反规范化/物化视图│
└───────────────────────────────────────┘
```

## 2. CQRS 实现

```python
# --- Command 端（写）---
from dataclasses import dataclass

@dataclass
class CreateOrderCommand:
    user_id: str
    items: list[dict]

@dataclass
class CancelOrderCommand:
    order_id: str
    reason: str

class OrderCommandHandler:
    """命令处理器：处理写操作"""

    def __init__(self, repo, event_bus):
        self.repo = repo
        self.event_bus = event_bus

    def handle_create(self, cmd: CreateOrderCommand):
        order = Order(user_id=cmd.user_id)
        for item in cmd.items:
            order.add_item(item["product_id"], item["quantity"], item["price"])
        events = order.place()

        self.repo.save(order)                    # 写入写数据库
        for event in events:
            self.event_bus.publish(event)         # 发布事件，同步到读数据库

    def handle_cancel(self, cmd: CancelOrderCommand):
        order = self.repo.find_by_id(cmd.order_id)
        events = order.cancel(cmd.reason)
        self.repo.save(order)
        for event in events:
            self.event_bus.publish(event)


# --- Query 端（读）---
class OrderQueryService:
    """查询服务：从读优化的数据库查询"""

    def __init__(self, read_db):
        self.read_db = read_db

    def get_order_detail(self, order_id: str) -> dict:
        """直接查反规范化的视图，无需 JOIN"""
        return self.read_db.find_one({"order_id": order_id})

    def list_user_orders(self, user_id: str, page: int = 1) -> list:
        return self.read_db.find(
            {"user_id": user_id},
            sort=[("created_at", -1)],
            skip=(page - 1) * 20,
            limit=20,
        )


# --- 读模型同步（事件消费者）---
class OrderReadModelUpdater:
    """监听事件，更新读数据库"""

    def on_order_placed(self, event: OrderPlaced):
        self.read_db.insert({
            "order_id": event.order_id,
            "user_id": event.user_id,
            "user_name": self._get_user_name(event.user_id),  # 反规范化
            "items": event.items,
            "total_amount": event.total_amount,
            "status": "placed",
            "created_at": event.occurred_at,
        })

    def on_order_cancelled(self, event: OrderCancelled):
        self.read_db.update(
            {"order_id": event.order_id},
            {"$set": {"status": "cancelled", "cancel_reason": event.reason}},
        )
```

## 3. 事件溯源（Event Sourcing）

不存储当前状态，而是存储所有状态变更事件。当前状态通过重放事件得到。

```
┌──────────── 传统 vs 事件溯源 ────────────┐
│                                           │
│  传统存储（只存最新状态）：                 │
│  orders 表：                               │
│  | id  | status    | amount | updated_at | │
│  | 123 | cancelled | 9900   | 2025-04-04 | │
│  （历史状态丢失，不知道中间发生了什么）      │
│                                           │
│  事件溯源（存储所有事件）：                  │
│  event_store 表：                          │
│  | seq | aggregate_id | type           |   │
│  | 1   | order-123    | OrderCreated   |   │
│  | 2   | order-123    | ItemAdded      |   │
│  | 3   | order-123    | OrderPlaced    |   │
│  | 4   | order-123    | PaymentReceived|   │
│  | 5   | order-123    | OrderCancelled |   │
│  （完整历史，可审计，可重放）               │
└───────────────────────────────────────────┘
```

```python
class EventSourcedOrder:
    """事件溯源的订单聚合"""

    def __init__(self):
        self.id = None
        self.status = None
        self.items = []
        self.total_amount = 0
        self._uncommitted_events = []  # 未提交的新事件

    # --- 命令方法：产生事件 ---
    def create(self, order_id: str, user_id: str):
        self._apply(OrderCreated(order_id=order_id, user_id=user_id))

    def add_item(self, product_id: str, quantity: int, price: int):
        self._apply(ItemAdded(
            order_id=self.id,
            product_id=product_id,
            quantity=quantity,
            price=price,
        ))

    def place(self):
        if not self.items:
            raise DomainError("订单不能为空")
        self._apply(OrderPlaced(order_id=self.id, total=self.total_amount))

    # --- 事件处理：更新状态 ---
    def _on_order_created(self, event: OrderCreated):
        self.id = event.order_id
        self.status = "draft"

    def _on_item_added(self, event: ItemAdded):
        self.items.append({"product_id": event.product_id, "quantity": event.quantity})
        self.total_amount += event.quantity * event.price

    def _on_order_placed(self, event: OrderPlaced):
        self.status = "placed"

    # --- 基础设施 ---
    def _apply(self, event):
        """应用事件：更新状态 + 记录未提交事件"""
        handler = getattr(self, f"_on_{self._event_name(event)}")
        handler(event)
        self._uncommitted_events.append(event)

    @classmethod
    def from_events(cls, events: list) -> "EventSourcedOrder":
        """从事件流重建聚合状态"""
        order = cls()
        for event in events:
            handler = getattr(order, f"_on_{cls._event_name(event)}")
            handler(event)
        return order


class EventStore:
    """事件存储"""

    def save(self, aggregate_id: str, events: list, expected_version: int):
        """保存事件（乐观并发控制）"""
        current_version = self._get_version(aggregate_id)
        if current_version != expected_version:
            raise ConcurrencyError("并发冲突，请重试")

        for i, event in enumerate(events):
            self.db.insert({
                "aggregate_id": aggregate_id,
                "version": expected_version + i + 1,
                "event_type": type(event).__name__,
                "data": event.to_dict(),
                "timestamp": datetime.utcnow(),
            })

    def load(self, aggregate_id: str) -> list:
        """加载聚合的所有事件"""
        rows = self.db.find(
            {"aggregate_id": aggregate_id},
            sort=[("version", 1)],
        )
        return [self._deserialize(row) for row in rows]
```

## 4. 快照优化

事件太多时，重放很慢。定期保存快照。

```
事件流：[e1, e2, e3, ..., e1000, e1001, e1002]

无快照：重放 1002 个事件 → 慢
有快照：加载快照(v1000) + 重放 2 个事件 → 快

快照策略：
├─ 每 N 个事件保存一次（如每 100 个）
├─ 定时保存（如每小时）
└─ 按需保存（聚合被频繁访问时）
```

## 5. CQRS + 事件溯源 组合

```
┌─────── CQRS + Event Sourcing ───────┐
│                                      │
│  Command ──→ 聚合 ──→ Event Store    │
│  (写端)      (领域逻辑)  (事件存储)   │
│                            │         │
│                       事件发布        │
│                            │         │
│                    ┌───────┴──────┐  │
│                    │ 投影器        │  │
│                    │ (Projector)  │  │
│                    └───────┬──────┘  │
│                            │         │
│  Query ──→ 读数据库 ←──── 更新       │
│  (读端)   (物化视图)                  │
│                                      │
│  写端：Event Store（追加写入，不可变） │
│  读端：任意数据库（按查询需求优化）    │
│  ├─ PostgreSQL（关系查询）            │
│  ├─ Elasticsearch（全文搜索）         │
│  ├─ Redis（热点数据缓存）             │
│  └─ MongoDB（灵活文档查询）           │
└──────────────────────────────────────┘
```

## 6. 适用场景与权衡

| 维度 | CQRS | 事件溯源 | CQRS + ES |
|------|------|---------|-----------|
| 复杂度 | 中 | 高 | 很高 |
| 适用场景 | 读写比例悬殊 | 需要审计追踪 | 复杂领域 + 高性能读 |
| 一致性 | 最终一致 | 强一致（事件流） | 写强一致，读最终一致 |
| 查询灵活性 | 高（读模型自由设计） | 低（需投影） | 高 |
| 历史回溯 | ❌ | ✅ | ✅ |
| 运维成本 | 中（两套数据库） | 高（事件存储 + 快照） | 很高 |

```
什么时候用：
├─ CQRS：读写比例 > 10:1，读写模型差异大
├─ 事件溯源：金融/审计场景，需要完整历史
├─ CQRS + ES：复杂业务 + 高性能 + 审计
└─ 都不用：简单 CRUD，别过度设计
```

## 7. 与现有笔记的关联

```
CQRS/ES 涉及的知识点：
├─ 事件驱动 → 本目录/01-事件驱动架构.md
├─ DDD 领域事件 → 本目录/03-DDD领域驱动设计.md
├─ 微服务数据管理 → 本目录/02-微服务架构模式.md
├─ Agent 记忆系统 → ai-agent/10-记忆与状态/（类似事件溯源思想）
└─ Kafka 事件流 → 本目录/01-事件驱动架构.md
```

## 📖 参考资料

- [Martin Fowler - CQRS](https://martinfowler.com/bliki/CQRS.html)
- [Greg Young - CQRS and Event Sourcing](https://cqrs.files.wordpress.com/2010/11/cqrs_documents.pdf)
- [Microsoft - CQRS Pattern](https://learn.microsoft.com/en-us/azure/architecture/patterns/cqrs)
