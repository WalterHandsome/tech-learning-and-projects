# DDD 领域驱动设计
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

<!-- version-check: DDD 设计模式, checked 2026-04-21 -->

## 1. 概述

DDD（Domain-Driven Design）是一种以业务领域为核心的软件设计方法论。核心思想：软件的复杂性来自业务本身，代码结构应该反映业务结构。

```
┌──────────── DDD 分层架构 ────────────┐
│                                       │
│  ┌─────────────────────────────────┐ │
│  │  Interface Layer（接口层）        │ │
│  │  Controller / API / DTO          │ │
│  └──────────────┬──────────────────┘ │
│  ┌──────────────┴──────────────────┐ │
│  │  Application Layer（应用层）      │ │
│  │  Service / Command / Query       │ │
│  │  编排领域对象，不含业务逻辑        │ │
│  └──────────────┬──────────────────┘ │
│  ┌──────────────┴──────────────────┐ │
│  │  Domain Layer（领域层）⭐ 核心    │ │
│  │  Entity / Value Object /         │ │
│  │  Aggregate / Domain Service /    │ │
│  │  Domain Event / Repository       │ │
│  └──────────────┬──────────────────┘ │
│  ┌──────────────┴──────────────────┐ │
│  │  Infrastructure Layer（基础设施） │ │
│  │  DB / MQ / Cache / External API  │ │
│  └─────────────────────────────────┘ │
└───────────────────────────────────────┘
```

## 2. 战略设计

### 2.1 限界上下文（Bounded Context）

```
┌─────────── 电商系统限界上下文 ───────────┐
│                                           │
│  ┌──────────┐  ┌──────────┐  ┌─────────┐│
│  │ 用户上下文 │  │ 订单上下文 │  │ 支付上下文││
│  │           │  │           │  │          ││
│  │ User      │  │ Order     │  │ Payment  ││
│  │ Address   │  │ OrderItem │  │ Refund   ││
│  │ Profile   │  │ Shipping  │  │ Account  ││
│  └─────┬────┘  └─────┬────┘  └────┬─────┘│
│        │              │             │      │
│        └──── 上下文映射（Context Map）────┘ │
│                                           │
│  同一个概念在不同上下文中含义不同：          │
│  "User" 在用户上下文 = 完整用户信息         │
│  "User" 在订单上下文 = 只有 userId + name  │
│  "User" 在支付上下文 = 只有 payerId        │
└───────────────────────────────────────────┘
```

### 2.2 上下文映射关系

```
上下文间的协作模式：
├─ 合作关系（Partnership）
│   两个团队紧密合作，共同演进
├─ 共享内核（Shared Kernel）
│   共享一小部分模型代码
├─ 客户-供应商（Customer-Supplier）
│   上游提供，下游消费，上游优先
├─ 防腐层（Anti-Corruption Layer, ACL）⭐
│   下游通过适配器隔离上游模型变化
├─ 开放主机服务（Open Host Service）
│   上游提供标准化 API
└─ 发布语言（Published Language）
    用标准格式（JSON Schema / Protobuf）通信
```

```python
# 防腐层示例：隔离外部支付系统的模型变化
class PaymentACL:
    """防腐层：将外部支付系统的模型转换为领域模型"""

    def __init__(self, external_client):
        self.client = external_client

    def create_payment(self, order: Order) -> Payment:
        # 外部系统的数据结构
        external_result = self.client.charge({
            "merchant_id": "xxx",
            "amount_cents": order.total_amount.cents,
            "currency": "CNY",
            "reference": str(order.id),
        })

        # 转换为领域模型
        return Payment(
            payment_id=PaymentId(external_result["txn_id"]),
            order_id=order.id,
            amount=Money(external_result["amount_cents"], Currency.CNY),
            status=self._map_status(external_result["status"]),
        )

    def _map_status(self, external_status: str) -> PaymentStatus:
        mapping = {
            "succeeded": PaymentStatus.COMPLETED,
            "pending": PaymentStatus.PROCESSING,
            "failed": PaymentStatus.FAILED,
        }
        return mapping.get(external_status, PaymentStatus.UNKNOWN)
```

## 3. 战术设计

### 3.1 实体（Entity）

有唯一标识，生命周期内标识不变。

```python
from dataclasses import dataclass, field
from uuid import uuid4

@dataclass
class Order:
    """订单实体：有唯一标识，包含业务逻辑"""
    id: str = field(default_factory=lambda: str(uuid4()))
    user_id: str = ""
    items: list = field(default_factory=list)
    status: str = "draft"

    def add_item(self, product_id: str, quantity: int, price: int):
        """业务逻辑在实体内部"""
        if self.status != "draft":
            raise DomainError("只有草稿状态的订单可以添加商品")
        if quantity <= 0:
            raise DomainError("数量必须大于 0")
        self.items.append(OrderItem(product_id, quantity, price))

    def place(self) -> list:
        """下单：返回领域事件"""
        if not self.items:
            raise DomainError("订单不能为空")
        self.status = "placed"
        return [OrderPlaced(order_id=self.id, items=self.items)]

    @property
    def total_amount(self) -> int:
        return sum(item.quantity * item.price for item in self.items)
```

### 3.2 值对象（Value Object）

无唯一标识，通过属性值判断相等，不可变。

```python
from dataclasses import dataclass

@dataclass(frozen=True)  # frozen=True 保证不可变
class Money:
    """值对象：通过值判断相等"""
    amount: int       # 分为单位
    currency: str

    def __post_init__(self):
        if self.amount < 0:
            raise ValueError("金额不能为负")

    def add(self, other: "Money") -> "Money":
        if self.currency != other.currency:
            raise ValueError("币种不同不能相加")
        return Money(self.amount + other.amount, self.currency)

# 值对象通过值比较
assert Money(100, "CNY") == Money(100, "CNY")  # True
assert Money(100, "CNY") != Money(200, "CNY")  # True

@dataclass(frozen=True)
class Address:
    """地址值对象"""
    province: str
    city: str
    district: str
    street: str
    zip_code: str
```

### 3.3 聚合与聚合根（Aggregate & Aggregate Root）

```
┌─────────── 聚合边界 ───────────┐
│                                 │
│  Order（聚合根）                 │
│  ├─ OrderItem（实体）           │
│  ├─ OrderItem（实体）           │
│  └─ ShippingAddress（值对象）   │
│                                 │
│  规则：                          │
│  ├─ 外部只能引用聚合根           │
│  ├─ 聚合内保证事务一致性         │
│  ├─ 聚合间通过领域事件通信       │
│  └─ 聚合尽量小                  │
└─────────────────────────────────┘
```

```python
class OrderRepository:
    """仓储：只对聚合根操作"""

    def save(self, order: Order):
        """保存整个聚合（订单 + 订单项 + 地址）"""
        self.db.orders.upsert(order.to_dict())

    def find_by_id(self, order_id: str) -> Order:
        """加载整个聚合"""
        data = self.db.orders.find_one({"id": order_id})
        return Order.from_dict(data)

    # ❌ 错误：不应该直接操作聚合内部的实体
    # def save_order_item(self, item: OrderItem): ...
```

### 3.4 领域事件（Domain Event）

```python
from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class DomainEvent:
    """领域事件基类"""
    event_id: str = field(default_factory=lambda: str(uuid4()))
    occurred_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())

@dataclass
class OrderPlaced(DomainEvent):
    """订单已下单事件"""
    order_id: str = ""
    user_id: str = ""
    total_amount: int = 0

@dataclass
class PaymentCompleted(DomainEvent):
    """支付完成事件"""
    payment_id: str = ""
    order_id: str = ""
    amount: int = 0

# 领域事件处理
class OrderPlacedHandler:
    def handle(self, event: OrderPlaced):
        # 触发下游动作
        self.inventory_service.reserve(event.order_id)
        self.notification_service.send_confirmation(event.user_id)
```

### 3.5 领域服务（Domain Service）

当业务逻辑不属于任何一个实体时，放在领域服务中。

```python
class PricingService:
    """定价领域服务：跨多个实体的业务逻辑"""

    def calculate_discount(self, order: Order, user: User) -> Money:
        """计算折扣：涉及订单和用户两个聚合"""
        discount = Money(0, "CNY")

        # VIP 用户 9 折
        if user.is_vip:
            discount = discount.add(
                Money(int(order.total_amount * 0.1), "CNY")
            )

        # 满 500 减 50
        if order.total_amount >= 50000:
            discount = discount.add(Money(5000, "CNY"))

        return discount
```

## 4. 项目结构示例

```
order-service/
├── interfaces/              # 接口层
│   ├── rest/
│   │   ├── order_controller.py
│   │   └── dto.py           # 数据传输对象
│   └── event/
│       └── order_event_consumer.py
├── application/             # 应用层
│   ├── order_service.py     # 应用服务（编排）
│   ├── commands.py          # 命令对象
│   └── queries.py           # 查询对象
├── domain/                  # 领域层 ⭐
│   ├── model/
│   │   ├── order.py         # 聚合根
│   │   ├── order_item.py    # 实体
│   │   └── money.py         # 值对象
│   ├── event/
│   │   └── order_events.py  # 领域事件
│   ├── service/
│   │   └── pricing_service.py
│   └── repository/
│       └── order_repository.py  # 仓储接口
└── infrastructure/          # 基础设施层
    ├── persistence/
    │   └── order_repository_impl.py  # 仓储实现
    ├── messaging/
    │   └── kafka_publisher.py
    └── external/
        └── payment_acl.py   # 防腐层
```

## 5. DDD vs 传统三层架构

| 维度 | 传统三层 | DDD |
|------|---------|-----|
| 核心 | 数据库表结构 | 业务领域模型 |
| 业务逻辑 | Service 层（贫血模型） | Entity/Domain Service（充血模型） |
| 数据模型 | 一个全局模型 | 每个上下文独立模型 |
| 复杂度管理 | 靠经验 | 限界上下文 + 聚合 |
| 适用场景 | CRUD 为主 | 复杂业务逻辑 |
| 学习成本 | 低 | 高 |

```
什么时候用 DDD：
├─ 业务逻辑复杂（不是简单 CRUD）
├─ 团队需要统一语言（业务和技术对齐）
├─ 系统需要长期演进
└─ 微服务拆分需要指导

什么时候不用：
├─ 简单 CRUD 应用
├─ 原型 / MVP
├─ 团队对 DDD 不熟悉且项目紧急
└─ 业务逻辑简单明确
```

## 6. 与现有笔记的关联

```
DDD 涉及的知识点：
├─ 微服务拆分 → 本目录/02-微服务架构模式.md
├─ 事件驱动 → 本目录/01-事件驱动架构.md
├─ CQRS → 本目录/04-CQRS与事件溯源.md
├─ Agent 多系统设计 → ai-agent/09-多Agent系统/
└─ Spring Boot 实现 → java/Spring Boot/
```

## 📖 参考资料

- [Eric Evans - Domain-Driven Design](https://www.domainlanguage.com/ddd/)
- [Vaughn Vernon - Implementing Domain-Driven Design](https://www.informit.com/store/implementing-domain-driven-design-9780321834577)
- [Martin Fowler - Bounded Context](https://martinfowler.com/bliki/BoundedContext.html)
