# AgentToken 后端工程落地指南

> Author: Walter Wang
>
> 这篇文档是给**要动手写代码的你**准备的。
> 前面 9 篇文档讲了"是什么"和"为什么"，这篇讲"怎么做"。
> 覆盖：整体架构、数据库设计（含预充值账户）、复式账本、API Key 管理、策略引擎、三种支付网关对接、Webhook 系统、REST API 设计、错误处理与幂等性、预充值业务逻辑、沙箱环境、监控告警、每日对账。
> 所有 Schema 和代码基于 PostgreSQL + Python/FastAPI，可适配其他技术栈。
>
> 前置阅读：
> - 07（数据模型和 CLI 设计）—— 理解 User/Developer/Member/Token 四层模型
> - 08（生命周期与错误处理）—— 理解每种支付的交易流程和异常场景
> - 09（X402 工程实战）—— X402 链上支付的具体实现

---

## 一、整体架构：你要建什么

```text
┌─────────────────────────────────────────────────────────────┐
│                      AgentToken 后端                         │
│                                                             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌────────────┐ │
│  │ API 层    │  │ 业务层    │  │ 账本层    │  │ 支付网关层  │ │
│  │ (FastAPI) │→ │ (核心逻辑)│→ │ (复式记账)│→ │ (对外对接)  │ │
│  └──────────┘  └──────────┘  └──────────┘  └────────────┘ │
│       │             │             │              │          │
│       │             │             │         ┌────┴────┐     │
│       │             │             │         │ VCN     │     │
│       │             │             │         │ Network │     │
│       │             │             │         │ X402    │     │
│       │             │             │         └─────────┘     │
│  ┌────┴─────────────┴─────────────┴──────────────────────┐ │
│  │                    PostgreSQL                          │ │
│  └───────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘

你要做的模块（CLI 不用你做）：
  ✅ 数据库 Schema（User/Developer/Member/Token/Ledger/PrefundedAccount）
  ✅ 三种支付网关对接（VCN/NetworkToken/X402）
  ✅ API Key 管理（生成/验证/轮换/撤销）
  ✅ 策略引擎（创建时评估 + 实时授权评估）
  ✅ 复式账本系统（每笔资金流动都有借贷记录）
  ✅ Webhook 系统（接收网关回调 + 发出事件通知）
  ✅ REST API 设计（给 CLI 和 SDK 调用）
  ✅ 错误处理 + 幂等性
  ✅ 预充值账户（高频小额场景的余额管理）
  ✅ 沙箱环境（测试与生产隔离）
  ✅ 日志 + 监控 + 告警
  ✅ 每日对账
```

---

## 二、数据库设计

### 2.1 核心原则

```text
支付系统数据库的铁律（来自 Stripe、Modern Treasury 等的最佳实践）：

1. 永远不要 UPDATE 金额字段
   → 所有金额变动通过 INSERT 新记录实现
   → 余额 = SUM(所有相关记录)
   → 这就是复式记账的基础

2. 所有表都要有 created_at，关键表要有 updated_at
   → 支付系统的时间线是审计的生命线

3. 软删除，不要硬删除
   → 支付记录永远不能物理删除（合规要求）
   → 用 status 字段标记状态

4. 每个写操作都要有 idempotency_key
   → 网络重试不会导致重复扣款
   → Stripe 的做法：客户端生成 UUID，服务端去重

5. 敏感数据（卡号、CVV）不存业务数据库
   → 存 Vault（加密存储），业务库只存 vault_token
   → 参见 01 文档第五章 PCI DSS / Vault / HSM
```

### 2.2 完整 Schema

```sql
-- ============================================================
-- 1. 用户与认证
-- ============================================================

-- 用户表（对应 07 文档的 User 层）
CREATE TABLE users (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email           VARCHAR(255) NOT NULL UNIQUE,
    -- 用户类型：个人需要 KYC，企业需要 KYB
    user_type       VARCHAR(20) NOT NULL CHECK (user_type IN ('individual', 'business')),
    -- KYC/KYB 状态：未开始 → 审核中 → 通过 → 拒绝
    kyc_status      VARCHAR(20) NOT NULL DEFAULT 'pending'
                    CHECK (kyc_status IN ('pending', 'in_review', 'approved', 'rejected')),
    kyc_provider_id VARCHAR(255),          -- 第三方 KYC 服务商的 ID（如 Onfido、Jumio）
    status          VARCHAR(20) NOT NULL DEFAULT 'active'
                    CHECK (status IN ('active', 'suspended', 'closed')),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- API Key 表
-- 设计参考 Stripe：Key 只在创建时返回明文，数据库只存哈希
CREATE TABLE api_keys (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID NOT NULL REFERENCES users(id),
    developer_id    UUID NOT NULL REFERENCES developers(id),
    -- 只存哈希，永远不存明文！
    -- 明文格式：sk_test_a1b2c3d4e5f6...（前缀 + 随机字符串）
    key_hash        VARCHAR(64) NOT NULL,  -- SHA-256 哈希
    key_prefix      VARCHAR(12) NOT NULL,  -- 如 "sk_test_a1b2"，用于识别
    name            VARCHAR(100),          -- 用户给 Key 起的名字，如 "production"
    environment     VARCHAR(10) NOT NULL CHECK (environment IN ('test', 'live')),
    status          VARCHAR(20) NOT NULL DEFAULT 'active'
                    CHECK (status IN ('active', 'revoked')),
    last_used_at    TIMESTAMPTZ,
    expires_at      TIMESTAMPTZ,           -- 可选：Key 过期时间
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    revoked_at      TIMESTAMPTZ
);

-- Key 前缀索引（用于快速查找）
CREATE INDEX idx_api_keys_prefix ON api_keys(key_prefix) WHERE status = 'active';

-- ============================================================
-- 2. 开发者与成员（对应 07 文档的 Developer/Member 层）
-- ============================================================

-- 开发者/应用表
CREATE TABLE developers (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID NOT NULL REFERENCES users(id),
    name            VARCHAR(255) NOT NULL,
    billing_email   VARCHAR(255) NOT NULL,
    status          VARCHAR(20) NOT NULL DEFAULT 'active'
                    CHECK (status IN ('active', 'suspended', 'closed')),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 成员表（绑定支付方式、承担支付责任的人）
CREATE TABLE members (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    developer_id    UUID NOT NULL REFERENCES developers(id),
    email           VARCHAR(255) NOT NULL,
    role            VARCHAR(20) NOT NULL DEFAULT 'member'
                    CHECK (role IN ('owner', 'admin', 'member')),
    -- 支付方式 ID（指向 Vault 中的加密卡信息，不是明文卡号！）
    pay_method_vault_token VARCHAR(255),
    -- 支付方式类型
    pay_method_type VARCHAR(20) CHECK (pay_method_type IN ('card', 'bank_account', 'wallet')),
    -- 支付方式的展示信息（如卡尾号 "****4242"）
    pay_method_display VARCHAR(50),
    kyc_status      VARCHAR(20) NOT NULL DEFAULT 'pending',
    status          VARCHAR(20) NOT NULL DEFAULT 'active'
                    CHECK (status IN ('active', 'invited', 'suspended', 'removed')),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(developer_id, email)
);

-- ============================================================
-- 3. Token（支付凭证）
-- ============================================================

-- Token 表（统一管理三种类型）
CREATE TABLE tokens (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    member_id       UUID NOT NULL REFERENCES members(id),
    developer_id    UUID NOT NULL REFERENCES developers(id),
    -- 三种类型对应 07 文档的 VCN/NetworkToken/X402
    token_type      VARCHAR(20) NOT NULL
                    CHECK (token_type IN ('vcn', 'network_token', 'x402')),
    -- 金额（美分存储，避免浮点精度问题！$50.00 存为 5000）
    amount_cents    BIGINT NOT NULL CHECK (amount_cents > 0),
    spent_cents     BIGINT NOT NULL DEFAULT 0 CHECK (spent_cents >= 0),
    currency        VARCHAR(3) NOT NULL DEFAULT 'USD',
    -- 状态：开放 → 冻结/已用完/已关闭/已过期
    status          VARCHAR(20) NOT NULL DEFAULT 'open'
                    CHECK (status IN ('open', 'frozen', 'exhausted', 'closed', 'expired')),
    -- 策略约束（JSON，对应 01 文档第八章策略引擎）
    policy          JSONB NOT NULL DEFAULT '{}',
    -- 凭证详情存 Vault（卡号/CVV 等敏感信息不存这里！）
    credential_vault_token VARCHAR(255),
    -- 展示信息
    display_last4   VARCHAR(4),
    display_expiry  VARCHAR(5),            -- "03/28"
    -- 意图记录（Agent 为什么要创建这个 Token）
    intent          TEXT,
    expires_at      TIMESTAMPTZ,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    closed_at       TIMESTAMPTZ
);

-- 按成员和状态查询
CREATE INDEX idx_tokens_member_status ON tokens(member_id, status);
-- 过期 Token 自动清理
CREATE INDEX idx_tokens_expires ON tokens(expires_at) WHERE status = 'open';

-- ============================================================
-- 4. 复式账本（这是支付系统的核心！）
-- ============================================================

-- 账户表（每个实体都有一个或多个账户）
CREATE TABLE ledger_accounts (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    -- 账户归属（可以是 user、member、system 等）
    owner_type      VARCHAR(20) NOT NULL,  -- 'user' | 'member' | 'system'
    owner_id        UUID NOT NULL,
    -- 账户类型
    account_type    VARCHAR(30) NOT NULL,
    -- 例如：'member_available'（成员可用余额）
    --       'member_held'（成员冻结金额）
    --       'system_revenue'（系统收入）
    --       'system_settlement'（待结算）
    currency        VARCHAR(3) NOT NULL DEFAULT 'USD',
    -- 余额（美分）—— 这是缓存字段，真实余额 = SUM(ledger_entries)
    -- 每次写入 entry 时同步更新，用于快速查询
    cached_balance_cents BIGINT NOT NULL DEFAULT 0,
    status          VARCHAR(20) NOT NULL DEFAULT 'active',
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE UNIQUE INDEX idx_ledger_accounts_owner
    ON ledger_accounts(owner_type, owner_id, account_type, currency);

-- 账本分录表（核心中的核心：每笔资金流动的记录）
-- 铁律：只 INSERT，永远不 UPDATE 或 DELETE
CREATE TABLE ledger_entries (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    -- 同一笔交易的所有分录共享一个 transaction_id
    transaction_id  UUID NOT NULL,
    account_id      UUID NOT NULL REFERENCES ledger_accounts(id),
    -- 借方（debit）或贷方（credit）
    entry_type      VARCHAR(6) NOT NULL CHECK (entry_type IN ('debit', 'credit')),
    amount_cents    BIGINT NOT NULL CHECK (amount_cents > 0),
    currency        VARCHAR(3) NOT NULL DEFAULT 'USD',
    -- 描述
    description     TEXT,
    -- 关联的业务对象
    reference_type  VARCHAR(30),           -- 'token_create' | 'token_spend' | 'token_close' | 'refund'
    reference_id    UUID,                  -- 关联的 token_id 或 transaction_id
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 按交易查询所有分录
CREATE INDEX idx_ledger_entries_txn ON ledger_entries(transaction_id);
-- 按账户查询余额历史
CREATE INDEX idx_ledger_entries_account ON ledger_entries(account_id, created_at);

-- 账本交易表（一组分录的元数据）
CREATE TABLE ledger_transactions (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    -- 幂等键：防止重复记账
    idempotency_key VARCHAR(255) NOT NULL UNIQUE,
    -- 交易类型
    transaction_type VARCHAR(30) NOT NULL,
    -- 'token_authorization'  创建 Token 时冻结资金
    -- 'token_capture'        Agent 消费时扣款
    -- 'token_release'        关闭 Token 时释放未用资金
    -- 'refund'               退款
    -- 'fee'                  手续费
    status          VARCHAR(20) NOT NULL DEFAULT 'completed',
    metadata        JSONB DEFAULT '{}',
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ============================================================
-- 5. 交易记录（外部支付网关的交易）
-- ============================================================

CREATE TABLE payment_transactions (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    token_id        UUID NOT NULL REFERENCES tokens(id),
    -- 幂等键
    idempotency_key VARCHAR(255) NOT NULL UNIQUE,
    -- 交易类型
    transaction_type VARCHAR(20) NOT NULL
                    CHECK (transaction_type IN ('authorization', 'capture', 'void', 'refund')),
    amount_cents    BIGINT NOT NULL,
    currency        VARCHAR(3) NOT NULL DEFAULT 'USD',
    -- 外部网关信息
    gateway         VARCHAR(20) NOT NULL,  -- 'agentcard' | 'evonet' | 'x402'
    gateway_txn_id  VARCHAR(255),          -- 网关返回的交易 ID
    gateway_status  VARCHAR(50),           -- 网关返回的状态
    -- 商户信息
    merchant_name   VARCHAR(255),
    merchant_mcc    VARCHAR(4),            -- 商户类别码
    -- 状态
    status          VARCHAR(20) NOT NULL DEFAULT 'pending'
                    CHECK (status IN ('pending', 'completed', 'failed', 'reversed')),
    error_code      VARCHAR(50),
    error_message   TEXT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    completed_at    TIMESTAMPTZ
);

-- ============================================================
-- 6. 审计日志（合规要求：所有操作都要记录）
-- ============================================================

CREATE TABLE audit_logs (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    -- 谁做的
    actor_type      VARCHAR(20) NOT NULL,  -- 'user' | 'api_key' | 'system' | 'webhook'
    actor_id        VARCHAR(255) NOT NULL,
    -- 做了什么
    action          VARCHAR(50) NOT NULL,  -- 'token.create' | 'member.add' | 'key.revoke' ...
    resource_type   VARCHAR(30) NOT NULL,  -- 'token' | 'member' | 'api_key' ...
    resource_id     UUID,
    -- 详情
    details         JSONB DEFAULT '{}',
    -- 请求上下文
    ip_address      INET,
    user_agent      TEXT,
    idempotency_key VARCHAR(255),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 按资源查询审计历史
CREATE INDEX idx_audit_resource ON audit_logs(resource_type, resource_id, created_at);
-- 按操作者查询
CREATE INDEX idx_audit_actor ON audit_logs(actor_type, actor_id, created_at);

-- ============================================================
-- 7. 预充值账户
-- ============================================================

-- 预充值账户表
CREATE TABLE prefunded_accounts (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID NOT NULL REFERENCES users(id) UNIQUE,
    currency        VARCHAR(3) NOT NULL DEFAULT 'USD',
    -- 可用余额（美分）
    available_balance_cents BIGINT NOT NULL DEFAULT 0 CHECK (available_balance_cents >= 0),
    -- 可提现余额（可能有冻结期）
    withdrawable_balance_cents BIGINT NOT NULL DEFAULT 0,
    status          VARCHAR(20) NOT NULL DEFAULT 'active',
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 充值/提现记录
CREATE TABLE prefund_transactions (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    account_id      UUID NOT NULL REFERENCES prefunded_accounts(id),
    idempotency_key VARCHAR(255) NOT NULL UNIQUE,
    -- 充值 / 提现 / Agent消费扣减 / 佣金入账
    transaction_type VARCHAR(20) NOT NULL
                    CHECK (transaction_type IN ('deposit', 'withdrawal', 'deduction', 'commission')),
    amount_cents    BIGINT NOT NULL,
    -- 充值来源 / 提现目标
    external_reference VARCHAR(255),  -- 如 Stripe PaymentIntent ID
    status          VARCHAR(20) NOT NULL DEFAULT 'completed',
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

### 2.3 为什么金额用美分（cents）而不是美元（dollars）

```text
错误做法：用 DECIMAL 或 FLOAT 存美元
  $10.00 + $0.10 = $10.10  ← 看起来没问题
  $0.10 + $0.20 = ?
  在某些浮点实现中 = 0.30000000000000004  ← 出事了

正确做法：用 BIGINT 存美分
  1000 + 10 = 1010  ← 永远精确
  10 + 20 = 30      ← 永远精确
  显示时再除以 100：30 / 100 = $0.30

这是 Stripe、Square、Adyen 等所有主流支付平台的标准做法。
Stripe 的 API 文档明确说：amount 字段单位是 cents。
```

---

## 三、复式账本系统

### 3.1 为什么需要复式记账

```text
单式记账（危险）：
  Token cm3abc 余额：$50.00
  Agent 消费 $30.00
  → UPDATE tokens SET spent_cents = 3000 WHERE id = 'cm3abc'
  → 如果这条 UPDATE 执行了两次（网络重试）？余额就错了
  → 如果中途崩溃？不知道钱去哪了

复式记账（安全）：
  每笔资金流动 = 一组分录（至少一借一贷，总额必须相等）
  余额 = 所有分录的累计
  → 任何时候都可以从分录重算余额
  → 借贷不平 = 一定有 bug，立刻告警
  → 天然幂等：同一个 idempotency_key 不会重复插入
```

来源：[Modern Treasury: How to Scale a Ledger](https://www.moderntreasury.com/journal/how-to-scale-a-ledger-part-iii) (Content was rephrased for compliance with licensing restrictions)
来源：[Alita Software: Database Design for Financial Transactions](https://alita-software.com/blog/database-design-financial-transactions) (Content was rephrased for compliance with licensing restrictions)

### 3.2 Token 生命周期的账本分录

```text
场景：用户创建一个 $50 的 VCN Token，Agent 消费了 $30，然后关闭 Token。

── 步骤 1：创建 Token（冻结 $50）──

  交易类型：token_authorization
  分录：
    借方（debit）：member_held 账户    +$50.00（冻结资金增加）
    贷方（credit）：member_available   -$50.00（可用余额减少）

  效果：
    member_available: $1000 → $950（可用余额减少 $50）
    member_held:      $0    → $50 （冻结金额增加 $50）

── 步骤 2：Agent 消费 $30 ──

  交易类型：token_capture
  分录：
    借方（debit）：system_settlement   +$30.00（待结算给商户）
    贷方（credit）：member_held        -$30.00（冻结资金减少）

  效果：
    member_held:       $50 → $20（冻结金额减少 $30）
    system_settlement: $0  → $30（待结算增加 $30）

── 步骤 3：关闭 Token（释放剩余 $20）──

  交易类型：token_release
  分录：
    借方（debit）：member_available    +$20.00（可用余额恢复）
    贷方（credit）：member_held        -$20.00（冻结资金释放）

  效果：
    member_held:      $20 → $0  （冻结清零）
    member_available: $950 → $970（可用余额恢复 $20）

── 验证：借贷永远平衡 ──

  总借方：$50 + $30 + $20 = $100
  总贷方：$50 + $30 + $20 = $100  ✓ 平衡
```

### 3.3 账本核心代码

```python
from uuid import uuid4
from datetime import datetime
from dataclasses import dataclass

@dataclass
class LedgerEntry:
    account_id: str
    entry_type: str  # 'debit' | 'credit'
    amount_cents: int
    description: str

async def record_ledger_transaction(
    db,
    idempotency_key: str,
    transaction_type: str,
    entries: list[LedgerEntry],
    reference_type: str = None,
    reference_id: str = None,
) -> str:
    """记录一笔账本交易（原子操作）"""

    # 1. 幂等检查：同一个 key 不会重复记账
    existing = await db.fetchone(
        "SELECT id FROM ledger_transactions WHERE idempotency_key = $1",
        idempotency_key,
    )
    if existing:
        return existing["id"]  # 已存在，直接返回

    # 2. 验证借贷平衡
    total_debit = sum(e.amount_cents for e in entries if e.entry_type == "debit")
    total_credit = sum(e.amount_cents for e in entries if e.entry_type == "credit")
    if total_debit != total_credit:
        raise ValueError(
            f"借贷不平衡！debit={total_debit} credit={total_credit}"
        )

    # 3. 在一个数据库事务中完成所有操作
    txn_id = str(uuid4())
    async with db.transaction():
        # 插入交易记录
        await db.execute(
            """INSERT INTO ledger_transactions (id, idempotency_key, transaction_type)
               VALUES ($1, $2, $3)""",
            txn_id, idempotency_key, transaction_type,
        )

        # 插入所有分录
        for entry in entries:
            await db.execute(
                """INSERT INTO ledger_entries
                   (id, transaction_id, account_id, entry_type,
                    amount_cents, description, reference_type, reference_id)
                   VALUES ($1, $2, $3, $4, $5, $6, $7, $8)""",
                str(uuid4()), txn_id, entry.account_id, entry.entry_type,
                entry.amount_cents, entry.description, reference_type, reference_id,
            )

        # 更新账户缓存余额
        for entry in entries:
            delta = entry.amount_cents if entry.entry_type == "debit" else -entry.amount_cents
            await db.execute(
                """UPDATE ledger_accounts
                   SET cached_balance_cents = cached_balance_cents + $1
                   WHERE id = $2""",
                delta, entry.account_id,
            )

    return txn_id
```

---

## 四、API Key 管理

### 4.1 生产级实现

```python
import hashlib
import secrets
from datetime import datetime

class APIKeyManager:
    """API Key 管理器（参考 Stripe 的设计）"""

    # Key 格式：sk_{env}_{random}
    # 例如：sk_test_a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6
    KEY_LENGTH = 32  # 随机部分的长度

    def create_key(self, user_id: str, developer_id: str, environment: str, name: str) -> dict:
        """创建新的 API Key"""
        # 1. 生成随机 Key
        random_part = secrets.token_urlsafe(self.KEY_LENGTH)
        raw_key = f"sk_{environment}_{random_part}"
        prefix = raw_key[:12]  # 如 "sk_test_a1b2"

        # 2. 哈希存储（永远不存明文！）
        key_hash = hashlib.sha256(raw_key.encode()).hexdigest()

        # 3. 存入数据库
        key_id = db.insert("api_keys", {
            "user_id": user_id,
            "developer_id": developer_id,
            "key_hash": key_hash,
            "key_prefix": prefix,
            "name": name,
            "environment": environment,
            "status": "active",
        })

        # 4. 返回明文（只这一次！之后再也拿不到）
        return {
            "id": key_id,
            "key": raw_key,       # ⚠️ 只在创建时返回
            "prefix": prefix,
            "name": name,
        }

    def verify_key(self, raw_key: str) -> dict | None:
        """验证 API Key（每次 API 请求都会调用）"""
        # 1. 哈希
        key_hash = hashlib.sha256(raw_key.encode()).hexdigest()

        # 2. 查数据库
        key_record = db.fetchone(
            "SELECT * FROM api_keys WHERE key_hash = $1 AND status = 'active'",
            key_hash,
        )
        if not key_record:
            return None

        # 3. 更新最后使用时间（异步，不阻塞请求）
        db.execute_async(
            "UPDATE api_keys SET last_used_at = NOW() WHERE id = $1",
            key_record["id"],
        )

        return key_record

    def rotate_key(self, old_key_id: str) -> dict:
        """轮换 Key（旧 Key 立即失效，生成新 Key）"""
        old_key = db.fetchone("SELECT * FROM api_keys WHERE id = $1", old_key_id)

        # 1. 撤销旧 Key
        db.execute(
            "UPDATE api_keys SET status = 'revoked', revoked_at = NOW() WHERE id = $1",
            old_key_id,
        )

        # 2. 创建新 Key（继承旧 Key 的配置）
        return self.create_key(
            user_id=old_key["user_id"],
            developer_id=old_key["developer_id"],
            environment=old_key["environment"],
            name=old_key["name"],
        )
```

### 4.2 API 认证中间件

```python
from fastapi import Request, HTTPException, Depends

async def authenticate_api_key(request: Request) -> dict:
    """FastAPI 中间件：验证 API Key"""
    # 1. 从 Header 或 Query 中提取 Key
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        raw_key = auth_header[7:]
    else:
        raise HTTPException(status_code=401, detail="Missing API Key")

    # 2. 验证
    key_manager = APIKeyManager()
    key_record = key_manager.verify_key(raw_key)
    if not key_record:
        raise HTTPException(status_code=401, detail="Invalid API Key")

    # 3. 检查环境匹配
    # 生产 API 不接受测试 Key，反之亦然
    expected_env = "live" if request.url.path.startswith("/v1/") else "test"
    if key_record["environment"] != expected_env:
        raise HTTPException(status_code=403, detail="Environment mismatch")

    return key_record
```

---

## 五、策略引擎详细设计

### 5.1 策略评估流程

```text
Agent 请求创建 Token 时：

  请求参数：
    member_id, token_type, amount, policy（可选）

  策略评估链（按顺序，任何一步失败则拒绝）：

  1. 用户级检查
     → 用户 KYC 是否通过？
     → 用户是否被暂停？

  2. 成员级检查
     → 成员是否有绑定的支付方式？
     → 成员的累计消费是否超过月限额？
     → 成员的角色是否允许创建此类型 Token？

  3. Token 级检查（来自请求中的 policy 参数）
     → 金额是否在允许范围内？
     → 商户类别是否在白名单中？
     → 时间窗口是否合理？

  4. 风控检查
     → 请求频率是否异常？（同一成员短时间内大量创建 Token）
     → 金额模式是否异常？（突然从 $10 跳到 $5000）
     → IP 地址是否异常？

  全部通过 → 发放 Token
  任何一步失败 → 拒绝 + 记录原因 + 触发 policy.violation Webhook
```

### 5.2 实时授权时的策略评估

```text
Agent 用 Token 在商户消费时（Webhook: issuing_authorization.request）：

  策略评估（必须在 2 秒内完成！）：

  1. Token 状态检查
     → Token 是否 open？是否过期？

  2. 余额检查
     → Token 剩余额度 >= 本次交易金额？

  3. 商户检查
     → 商户 MCC 是否在 Token 的 allowed_categories 中？
     → 商户是否在黑名单中？

  4. 频率检查
     → 一次性 Token 是否已经用过？
     → 本小时内交易次数是否超限？

  5. 地理检查（如果 policy 中有 geography 限制）
     → 商户所在国家是否在允许列表中？

  通过 → 批准授权
  失败 → 拒绝授权 + 记录原因
```

---

## 六、三种支付网关对接

### 6.1 对接架构：统一接口 + 多网关适配

```text
不要让业务代码直接调用各个支付网关的 API。
用一个统一接口隔离，切换网关时业务代码不用改。

业务层调用：
  gateway.create_credential(token_type="vcn", amount=5000, ...)
  gateway.authorize(credential_id, amount=3000, ...)
  gateway.capture(authorization_id)
  gateway.void(authorization_id)

统一接口内部路由：
  token_type == "vcn"           → VCNGateway（对接 AgentCard.sh，底层 Stripe Issuing）
  token_type == "network_token" → NetworkTokenGateway（对接 EvoNet，底层 Visa/MC TSP）
  token_type == "x402"          → X402Gateway（对接链上合约，详见 09 文档）
```

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional

@dataclass
class PaymentCredential:
    """统一的支付凭证（不含敏感信息，敏感信息在 Vault）"""
    credential_id: str
    token_type: str
    vault_token: str       # 指向 Vault 中的敏感数据
    display_last4: str
    display_expiry: str
    amount_cents: int
    currency: str

@dataclass
class AuthorizationResult:
    success: bool
    authorization_id: Optional[str]
    gateway_txn_id: str
    error_code: Optional[str] = None
    error_message: Optional[str] = None

class PaymentGateway(ABC):
    """支付网关统一接口"""

    @abstractmethod
    async def create_credential(
        self, member_vault_token: str, amount_cents: int, currency: str, policy: dict
    ) -> PaymentCredential:
        """创建支付凭证（VCN/NetworkToken/X402）"""
        ...

    @abstractmethod
    async def authorize(
        self, credential_id: str, amount_cents: int, merchant_mcc: str
    ) -> AuthorizationResult:
        """授权（冻结资金）"""
        ...

    @abstractmethod
    async def capture(self, authorization_id: str, amount_cents: int) -> bool:
        """捕获（确认扣款）"""
        ...

    @abstractmethod
    async def void(self, authorization_id: str) -> bool:
        """撤销授权（释放冻结资金）"""
        ...

    @abstractmethod
    async def close_credential(self, credential_id: str) -> bool:
        """关闭凭证"""
        ...
```

### 6.2 VCN 对接（通过 AgentCard.sh）

```text
AgentToken 的 VCN 通过 AgentCard.sh 对接，AgentCard.sh 底层基于 Stripe Issuing。
AgentToken 不直接调用 Stripe Issuing API，而是通过 AgentCard.sh 的 REST API。

底层 API：https://api.agentcard.sh/api/v1
底层文档：https://docs.agentcard.sh/

对接流程：
  1. 创建 Cardholder（对应你的 Member）→ POST /api/v1/cardholders
  2. 绑定支付方式 → POST /api/v1/cardholders/{id}/payment-method/setup
  3. 创建 Card（虚拟卡，对应你的 Token）→ POST /api/v1/cards
  4. 获取卡详情（PAN/CVV）→ GET /api/v1/cards/{id}/details
  5. 关卡 → DELETE /api/v1/cards/{id}

AgentCard.sh 内部通过 Stripe Issuing 实现：
  → Spending Controls（对应你的 Policy）
  → Webhook 实时授权（issuing_authorization.request）
  → 预付模式（PaymentIntent Hold）

关键 Webhook 事件（来自 Stripe Issuing，通过 AgentCard.sh 透传）：
  issuing_authorization.request  → 实时授权请求（你可以批准或拒绝）
  issuing_authorization.created  → 授权已创建
  issuing_transaction.created    → 交易已完成
  issuing_card.updated           → 卡状态变更
```

```python
import stripe

class VCNGateway(PaymentGateway):
    """VCN 网关（通过 AgentCard.sh 对接，底层 Stripe Issuing）
    
    注意：下面的代码示例直接使用了 Stripe Issuing SDK，
    这是因为 AgentCard.sh 底层就是 Stripe Issuing。
    实际生产中有两种对接方式：
      方式 1：调用 AgentCard.sh REST API（POST /api/v1/cards）
      方式 2：直接调用 Stripe Issuing SDK（如果你有 Stripe Issuing 权限）
    AgentCard.sh 本质上是 Stripe Issuing 的薄封装，两种方式效果一样。
    """

    def __init__(self, api_key: str):
        stripe.api_key = api_key

    async def create_credential(
        self, member_vault_token: str, amount_cents: int, currency: str, policy: dict
    ) -> PaymentCredential:
        # 1. 从 Vault 获取 Member 的 Cardholder ID
        cardholder_id = await vault.get_metadata(member_vault_token, "stripe_cardholder_id")

        # 2. 创建虚拟卡
        card = stripe.issuing.Card.create(
            cardholder=cardholder_id,
            type="virtual",
            currency=currency.lower(),
            status="active",
            spending_controls={
                "spending_limits": [{
                    "amount": amount_cents,
                    "interval": "all_time",  # 总额限制
                }],
                # 商户类别限制（来自 policy）
                "allowed_categories": policy.get("merchant_categories", []),
            },
        )

        # 3. 敏感信息存 Vault
        card_details = stripe.issuing.Card.retrieve(card.id, expand=["number", "cvc"])
        vault_token = await vault.store({
            "pan": card_details.number,
            "cvc": card_details.cvc,
            "exp_month": card_details.exp_month,
            "exp_year": card_details.exp_year,
        })

        return PaymentCredential(
            credential_id=card.id,
            token_type="vcn",
            vault_token=vault_token,
            display_last4=card.last4,
            display_expiry=f"{card.exp_month:02d}/{card.exp_year % 100:02d}",
            amount_cents=amount_cents,
            currency=currency,
        )

    async def close_credential(self, credential_id: str) -> bool:
        stripe.issuing.Card.modify(credential_id, status="canceled")
        return True
```

### 6.3 Network Token 对接（通过 EvoNet）

```text
AgentToken 的 Network Token 通过 EvoNet（EVO Payment）对接，
EvoNet 底层对接 Visa Token Service (VTS) 和 Mastercard MDES。

底层 API：https://docs.everonet.com
底层文档：https://docs.everonet.com/en-us/gateway/developer-portal/online/network-token-management

对接流程：
  1. 申请网络令牌：POST /paymentMethod（networkTokenOnly: true）
     → EvoNet 向 Visa/MC TSP 请求 Token 化
     → 返回 token_id（替代卡号）
  2. 获取动态密码：POST /cryptogram
     → 每次交易都要重新获取（一次性密码）
     → 返回 cryptogram
  3. Agent 用 token_id + cryptogram 发起交易
  4. 删除令牌：DELETE /paymentMethod?networkTokenID=xxx
  5. 异步通知：
     → tokenUpdate：令牌状态变更（换卡、过期）
     → paymentMethod：令牌申请成功/失败
     → Cryptogram：动态密码生成完成

与 VCN 的关键区别：
  → VCN 通过 AgentCard.sh 创建虚拟卡，Agent 拿到静态卡号
  → NetworkToken 通过 EvoNet 申请网络令牌，Agent 拿到 token_id + 动态密码
  → NetworkToken 更安全：即使 token_id 泄露，没有 cryptogram 也无法交易
```

### 6.4 X402 对接

X402 的工程实现已经在 09 文档中详细覆盖了，这里只列出与统一网关接口的对接要点：

```text
与 VCN/NetworkToken 的关键区别：
  1. 没有"授权→捕获"两步，而是一步完成（链上转账）
  2. 没有"退款"概念（链上交易不可逆，需要对方主动退回）
  3. 需要管理钱包和 Gas 费（详见 09 文档第三节）
  4. 结算是即时的（不需要 T+1 到 T+3）

对接 09 文档的映射：
  create_credential → 生成 X402 可验证凭证（VC）
  authorize         → 不适用（X402 没有预授权概念）
  capture           → 链上转账 + Facilitator 验证
  void              → 不适用
  close_credential  → 标记 VC 为已使用
```

### 6.5 资金池管理（VCN + X402 共用逻辑）

不管是 VCN 还是 X402，AgentToken 都需要维护一个资金池。
设计理念详见 07 文档 2.7 节，这里讲工程实现。

```text
两种资金池的形态：
  VCN  → Stripe Issuing Balance（法币/美元余额）
  X402 → 链上主钱包（USDC 余额）

两种资金池的运作模式完全一样：
  总池子 → 创建临时凭证 → Agent 使用 → 回收剩余 → 销毁凭证
```

#### 6.5.1 VCN 资金池（Stripe Issuing Balance）

```python
class IssuingBalanceManager:
    """Stripe Issuing Balance 资金池管理"""

    # 最低水位线：低于这个值就告警并自动补充
    MIN_BALANCE_CENTS = 500_000  # $5,000
    # 每次补充的目标余额
    TARGET_BALANCE_CENTS = 2_000_000  # $20,000

    async def get_balance(self) -> int:
        """查询当前 Issuing Balance（美分）"""
        balance = stripe.Balance.retrieve()
        # Issuing Balance 在 balance.issuing.available 中
        issuing = next(
            (b for b in balance.issuing.available if b.currency == "usd"),
            None,
        )
        return issuing.amount if issuing else 0

    async def check_and_topup(self):
        """检查水位线，不足时自动补充
        
        补充来源（按优先级）：
          1. PrefundedAccount 中的企业预充值资金
          2. Stripe 其他产品的余额（如 Connect 收入）
          3. 银行转账（需要人工触发，T+1 到账）
        """
        current = await self.get_balance()
        if current < self.MIN_BALANCE_CENTS:
            shortfall = self.TARGET_BALANCE_CENTS - current

            # 尝试从 PrefundedAccount 补充
            available_prefund = await get_total_prefunded_balance()
            if available_prefund >= shortfall:
                await topup_from_prefunded(shortfall)
                await audit_log("issuing_balance.topup", "system", details={
                    "source": "prefunded", "amount_cents": shortfall,
                })
            else:
                # 余额不足，发告警
                await alert("issuing_balance.low", {
                    "current_cents": current,
                    "min_required_cents": self.MIN_BALANCE_CENTS,
                    "shortfall_cents": shortfall,
                })

    async def daily_reconcile(self):
        """每日对账：Issuing Balance vs 内部账本"""
        stripe_balance = await self.get_balance()
        # 内部账本中所有 open 状态 VCN Token 的冻结总额
        internal_held = await db.fetchval(
            """SELECT COALESCE(SUM(amount_cents - spent_cents), 0)
               FROM tokens WHERE token_type = 'vcn' AND status = 'open'"""
        )
        diff = stripe_balance - internal_held
        if abs(diff) > 100:  # 差异超过 $1 就告警
            await alert("issuing_balance.mismatch", {
                "stripe_balance_cents": stripe_balance,
                "internal_held_cents": internal_held,
                "diff_cents": diff,
            })
```

```text
VCN 资金池的三种充值方式：

方式 A：AgentToken 自己垫资
  → stripe.Topup.create(amount=2000000, currency="usd", source="bank_account")
  → 从 AgentToken 的银行账户转入 Issuing Balance
  → 到账时间：T+1（银行转账）
  → 适合：初期启动，资金量不大时

方式 B：实时从 Member 扣款
  → 创建 Token 时先从 Member 的卡扣款（PaymentIntent）
  → 扣款成功后资金自动进入 Stripe 余额
  → 再从余额转入 Issuing Balance
  → 适合：个人用户，按需扣款

方式 C：PrefundedAccount 预充值（推荐企业客户）
  → 企业先充值到 PrefundedAccount
  → 创建 Token 时从 PrefundedAccount 扣减
  → 定期批量将 PrefundedAccount 资金转入 Issuing Balance
  → 适合：企业客户，资金已在平台内
```

#### 6.5.2 X402 资金池（链上钱包）

```text
X402 资金池的工程实现详见 09 文档第二章（钱包服务）和第五章（资金管理）。
这里只列出与 AgentToken Token 管理的联动逻辑。

推荐方案：临时钱包模式（和 VCN 的虚拟卡思路一致）

创建 X402 Token 时：
  1. 调用钱包服务创建临时钱包（新的链上地址 + 密钥对）
  2. 从运营钱包转入指定金额的 USDC 到临时钱包
  3. 将临时钱包的私钥存入 Vault/HSM
  4. 内部账本记录：member_available → member_held

Agent 使用 Token 时：
  1. 从 Vault 获取临时钱包的签名能力
  2. 用临时钱包的私钥签名 x402 支付
  3. 链上转账 USDC 给服务方
  4. 内部账本记录：member_held → system_settlement

关闭 X402 Token 时：
  1. 将临时钱包剩余 USDC 转回运营钱包
  2. 销毁临时钱包的私钥（从 Vault 中删除）
  3. 内部账本记录：member_held → member_available（释放剩余）
```

```python
class X402FundingManager:
    """X402 资金池管理（和 09 文档的钱包服务联动）"""

    async def create_temp_wallet(self, amount_cents: int) -> dict:
        """创建临时钱包并充值"""
        amount_usdc = amount_cents / 100  # 美分转美元（USDC 1:1 美元）

        # 1. 创建临时钱包（调用 09 文档的钱包服务）
        wallet = await wallet_service.create_wallet()

        # 2. 从运营钱包转 USDC 到临时钱包
        tx_hash = await chain_service.transfer_usdc(
            from_address=OPERATIONS_WALLET_ADDRESS,
            to_address=wallet.address,
            amount=amount_usdc,
        )
        await chain_service.wait_for_confirmation(tx_hash)

        # 3. 私钥存 Vault
        vault_token = await vault.store({
            "private_key": wallet.private_key,
            "address": wallet.address,
            "chain": "base-mainnet",
        })

        return {
            "address": wallet.address,
            "vault_token": vault_token,
            "amount_usdc": amount_usdc,
            "funding_tx": tx_hash,
        }

    async def close_temp_wallet(self, vault_token: str) -> dict:
        """关闭临时钱包，回收剩余 USDC"""
        # 1. 从 Vault 获取钱包信息
        wallet_info = await vault.retrieve(vault_token)

        # 2. 查询剩余余额
        balance = await chain_service.get_usdc_balance(wallet_info["address"])

        # 3. 如果有剩余，转回运营钱包
        if balance > 0:
            tx_hash = await chain_service.transfer_usdc(
                from_address=wallet_info["address"],
                to_address=OPERATIONS_WALLET_ADDRESS,
                amount=balance,
                private_key=wallet_info["private_key"],
            )
            await chain_service.wait_for_confirmation(tx_hash)

        # 4. 销毁私钥
        await vault.delete(vault_token)

        return {"recovered_usdc": balance, "recovery_tx": tx_hash if balance > 0 else None}
```

#### 6.5.3 资金池与内部账本的联动

```text
不管是 VCN 还是 X402，内部账本的记账方式完全一样：

  创建 Token（冻结资金）：
    借方：member_held      +$50（冻结增加）
    贷方：member_available  -$50（可用减少）
    同时：VCN → Stripe 创建虚拟卡 / X402 → 创建临时钱包并充值

  Agent 消费（扣款）：
    借方：system_settlement +$30（待结算增加）
    贷方：member_held       -$30（冻结减少）
    同时：VCN → Stripe 从 Issuing Balance 扣款 / X402 → 临时钱包链上转账

  关闭 Token（释放剩余）：
    借方：member_available  +$20（可用恢复）
    贷方：member_held       -$20（冻结释放）
    同时：VCN → Stripe 释放冻结 / X402 → 临时钱包剩余转回运营钱包

  这就是 07 文档 2.7.3 节说的"统一模型"在代码层面的体现。
  账本层不关心底层是 Stripe 还是链上，它只管记录资金流动。
  底层差异由支付网关层（第六章 6.1-6.4）封装。
```


---

## 七、Webhook 系统设计

### 7.1 你需要接收的 Webhook

```text
来自 AgentCard.sh / Stripe Issuing（VCN 场景）：
  （AgentCard.sh 底层是 Stripe Issuing，Webhook 由 Stripe 发出，
   可以通过 AgentCard.sh 透传，也可以直接接收 Stripe 的 Webhook）
  issuing_authorization.request   → 实时授权请求（你必须在 2 秒内回复批准/拒绝）
  issuing_authorization.created   → 授权已创建（Agent 刷卡成功）
  issuing_authorization.updated   → 授权更新（金额变更、部分捕获）
  issuing_transaction.created     → 交易完成（资金已结算）
  issuing_dispute.created         → 争议（持卡人对交易提出异议）

来自 EvoNet（NetworkToken 场景）：
  tokenUpdate                     → 令牌状态变更（换卡、过期）
  paymentMethod                   → 令牌申请成功/失败
  Cryptogram                      → 动态密码生成完成

来自链上监控（X402 场景）：
  x402.payment.confirmed          → 链上支付已确认
  x402.payment.failed             → 链上支付失败

你需要发出的 Webhook（通知你的客户）：
  token.created                   → Token 创建成功
  token.transaction.authorized    → Agent 使用 Token 发起了一笔交易
  token.transaction.completed     → 交易完成
  token.transaction.declined      → 交易被拒绝
  token.closed                    → Token 已关闭
  token.expired                   → Token 已过期
  policy.violation                → 策略违规（Agent 尝试了不允许的操作）
  balance.low                     → 余额低于阈值
```

### 7.2 Webhook 处理的铁律

```text
来自主流支付平台（Stripe、Marqeta、Adyen）的最佳实践：

铁律 1：先回复 200，再处理业务
  → 支付网关期望你在 2-5 秒内回复 HTTP 200
  → 如果超时，网关会重试（导致重复事件）
  → 正确做法：收到 Webhook → 立即回复 200 → 放入队列 → 异步处理

铁律 2：用事件 ID 去重（幂等）
  → 网关会重试，你一定会收到重复事件
  → 每个事件有唯一 ID（如 Stripe 的 evt_xxx）
  → 处理前先查：这个事件 ID 处理过了吗？
  → 处理过 → 跳过；没处理过 → 处理并记录

铁律 3：验证签名
  → 网关在 Header 中附带签名（如 Stripe-Signature）
  → 你必须用 Webhook Secret 验证签名
  → 防止攻击者伪造 Webhook 触发虚假交易

铁律 4：处理乱序
  → 事件可能不按时间顺序到达
  → 例如：先收到 transaction.completed，后收到 authorization.created
  → 你的代码必须能处理这种情况（用状态机，不要假设顺序）
```

来源：[Sandorian: Webhook Handling for Payment Systems](https://sandorian.com/fintech/kb/webhook-handling-payment-systems) (Content was rephrased for compliance with licensing restrictions)
来源：[Stripe: Issuing Real-time Authorizations](https://docs.stripe.com/issuing/controls/real-time-authorizations) (Content was rephrased for compliance with licensing restrictions)

### 7.3 实时授权决策（Stripe Issuing 的杀手级功能）

```text
这是 VCN 场景中最关键的 Webhook：issuing_authorization.request

当 Agent 用虚拟卡在商户刷卡时：
  1. 商户 → 收单行 → 卡组织 → Stripe
  2. Stripe → 发 Webhook 到你的服务器
  3. 你的服务器在 2 秒内决定：批准还是拒绝
  4. 你的决策 → Stripe → 卡组织 → 收单行 → 商户

你可以在这 2 秒内做什么：
  ├─ 检查策略（金额、商户类别、地理位置、时间窗口）
  ├─ 检查余额（Token 剩余额度够不够）
  ├─ 检查频率（这个 Token 今天已经用了几次）
  ├─ 检查 Agent 意图（这笔消费是否符合 Token 创建时的 intent）
  └─ 记录审计日志

这就是"policy evaluation"在运行时的体现。
Marqeta 叫这个功能 "JIT Funding"（Just-in-Time Funding）——
在交易发生的那一刻实时决定是否放行。
```

```python
from fastapi import Request, Response
import stripe

@router.post("/webhooks/stripe-issuing")
async def handle_issuing_webhook(request: Request):
    """处理 Stripe Issuing Webhook（包括实时授权）"""
    payload = await request.body()
    sig_header = request.headers.get("Stripe-Signature")

    # 1. 验证签名
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, WEBHOOK_SECRET
        )
    except stripe.error.SignatureVerificationError:
        return Response(status_code=400)

    # 2. 事件去重
    if await is_event_processed(event["id"]):
        return Response(status_code=200)  # 已处理，直接返回

    # 3. 实时授权决策（必须在 2 秒内回复！）
    if event["type"] == "issuing_authorization.request":
        authorization = event["data"]["object"]
        decision = await evaluate_authorization(authorization)

        # 记录事件
        await mark_event_processed(event["id"])

        # 直接在 Webhook 响应中返回决策
        return Response(
            content=json.dumps({"approved": decision.approved}),
            status_code=200,
            headers={"Stripe-Version": "2024-12-18.acacia"},
        )

    # 4. 其他事件放入队列异步处理
    await enqueue_webhook_event(event)
    await mark_event_processed(event["id"])
    return Response(status_code=200)

async def evaluate_authorization(auth: dict) -> dict:
    """实时授权策略评估（必须快！）"""
    token = await get_token_by_card_id(auth["card"]["id"])
    if not token:
        return {"approved": False, "reason": "unknown_token"}

    # 策略检查
    amount_cents = auth["pending_request"]["amount"]
    merchant_mcc = auth["merchant_data"]["category_code"]

    # 金额检查
    if token.spent_cents + amount_cents > token.amount_cents:
        return {"approved": False, "reason": "insufficient_balance"}

    # 商户类别检查
    allowed_mcc = token.policy.get("merchant_categories", [])
    if allowed_mcc and merchant_mcc not in allowed_mcc:
        return {"approved": False, "reason": "merchant_not_allowed"}

    # 一次性检查
    if token.policy.get("single_use") and token.spent_cents > 0:
        return {"approved": False, "reason": "single_use_exhausted"}

    return {"approved": True}
```

---

## 八、REST API 设计

### 8.1 API 结构

```text
所有 API 遵循 RESTful 设计，参考 Stripe 的 API 风格：

认证：Bearer Token（API Key）
格式：JSON
版本：URL 路径（/v1/）
幂等：POST 请求通过 Idempotency-Key Header 实现
分页：cursor-based（不用 offset，大数据量下性能更好）

核心端点：
  POST   /v1/tokens              创建 Token
  GET    /v1/tokens               列出 Token
  GET    /v1/tokens/{id}          获取 Token 摘要
  GET    /v1/tokens/{id}/details  获取 Token 敏感信息
  POST   /v1/tokens/{id}/close   关闭 Token

  POST   /v1/members             添加成员
  GET    /v1/members              列出成员
  DELETE /v1/members/{id}         移除成员

  POST   /v1/developers          创建开发者
  GET    /v1/developers           列出开发者

  POST   /v1/keys                创建 API Key
  GET    /v1/keys                 列出 API Key
  POST   /v1/keys/{id}/rotate    轮换 Key
  DELETE /v1/keys/{id}            撤销 Key
```

### 8.2 创建 Token API 示例

```python
from fastapi import APIRouter, Depends, Header
from pydantic import BaseModel, Field
from typing import Optional

router = APIRouter(prefix="/v1")

class CreateTokenRequest(BaseModel):
    member_id: str
    token_type: str = Field(..., pattern="^(vcn|network_token|x402)$")
    amount: float = Field(..., gt=0, le=50000)  # 美元，API 层用美元，内部转美分
    currency: str = Field(default="USD", pattern="^[A-Z]{3}$")
    policy: Optional[dict] = None
    intent: Optional[str] = None  # Agent 的意图描述

class TokenResponse(BaseModel):
    id: str
    token_type: str
    display_last4: str
    display_expiry: str
    amount: float
    spent: float
    status: str
    created_at: str

@router.post("/tokens", response_model=TokenResponse)
async def create_token(
    req: CreateTokenRequest,
    idempotency_key: str = Header(..., alias="Idempotency-Key"),
    api_key: dict = Depends(authenticate_api_key),
):
    """创建支付 Token"""
    amount_cents = int(req.amount * 100)

    # 1. 验证成员存在且有支付方式
    member = await get_member(req.member_id, api_key["developer_id"])
    if not member or not member.pay_method_vault_token:
        raise HTTPException(400, "Member not found or no payment method")

    # 2. 策略检查
    policy = req.policy or {}
    validate_policy(policy, member, amount_cents)

    # 3. 创建支付凭证（调用对应的网关）
    gateway = get_gateway(req.token_type)
    credential = await gateway.create_credential(
        member.pay_method_vault_token, amount_cents, req.currency, policy,
    )

    # 4. 账本记录（冻结资金）
    await record_ledger_transaction(
        db, idempotency_key=f"token_auth_{idempotency_key}",
        transaction_type="token_authorization",
        entries=[
            LedgerEntry(member.held_account_id, "debit", amount_cents, "Token 冻结"),
            LedgerEntry(member.available_account_id, "credit", amount_cents, "Token 冻结"),
        ],
        reference_type="token_create", reference_id=credential.credential_id,
    )

    # 5. 保存 Token 记录
    token = await save_token(credential, member, amount_cents, req.currency, policy, req.intent)

    # 6. 审计日志
    await audit_log("token.create", "token", token.id, api_key, details={
        "amount": req.amount, "type": req.token_type, "intent": req.intent,
    })

    return TokenResponse(...)
```

---

## 九、错误处理与幂等性

### 9.1 幂等性设计

```text
支付系统的第一铁律：同一个操作执行两次，结果必须和执行一次一样。

为什么？
  Agent 调用 API 创建 Token → 网络超时 → Agent 不知道是否成功 → 重试
  如果没有幂等性 → 创建了两个 Token → 冻结了两倍的钱 → 出事了

实现方式（参考 Stripe）：
  1. 客户端在 Header 中传 Idempotency-Key（UUID）
  2. 服务端收到请求后，先查这个 Key 是否已处理过
  3. 如果已处理 → 直接返回之前的结果（不重复执行）
  4. 如果未处理 → 正常执行，保存结果和 Key 的映射
  5. Key 的有效期通常 24-48 小时（之后自动清理）
```

### 9.2 错误码设计

```text
参考 Stripe 的错误码体系：

HTTP 状态码：
  200  成功
  400  请求参数错误（客户端问题）
  401  认证失败（API Key 无效）
  403  权限不足（Key 环境不匹配、成员无权限）
  404  资源不存在
  409  冲突（幂等键冲突、状态冲突）
  429  请求过多（限流）
  500  服务器内部错误

业务错误码（在 JSON body 中）：
  insufficient_funds     余额不足
  policy_violation       策略违规（超限额、商户不在白名单等）
  member_not_verified    成员未完成 KYC
  token_expired          Token 已过期
  token_closed           Token 已关闭
  gateway_error          支付网关错误
  gateway_timeout        支付网关超时
```

---

## 十、预充值账户（Prefunded Account）

### 10.1 为什么需要预充值

```text
默认模式（信用卡扣款）：
  Agent 创建 Token → 冻结用户信用卡额度 → Agent 消费 → 从信用卡扣款
  问题：每次都要走卡网络，有手续费，有失败风险

预充值模式：
  用户先充值 $500 到 AgentToken 账户
  → Agent 创建 Token → 从预充值余额扣减（内部操作，无手续费）
  → Agent 消费 → 从预充值余额结算

适用场景：
  ├─ 高频小额：Agent 每天调用几十次 API，每次 $0.01-$1
  │   → 走信用卡手续费比交易本身还贵
  │   → 预充值后内部扣减，零手续费
  ├─ 企业批量：公司给 100 个 Agent 分配预算
  │   → 充值 $10,000 → 分配给各 Agent
  └─ 佣金收取：平台从 Agent 交易中抽取佣金
      → 佣金进入平台的预充值账户
```

> 预充值账户的数据库 Schema（prefunded_accounts 和 prefund_transactions 表）已包含在第二章「数据库设计」的 2.2 节中。

---

## 十一、沙箱环境设计

```text
沙箱环境 vs 生产环境：

  沙箱（sk_test_*）：
  ├─ 不会真实扣款
  ├─ 使用测试卡号（如 Stripe 的 4242424242424242）
  ├─ 可以模拟各种错误场景（余额不足、网络超时、卡被拒）
  ├─ Webhook 事件也是模拟的
  └─ 数据完全隔离（沙箱数据不会出现在生产中）

  生产（sk_live_*）：
  ├─ 真实扣款
  ├─ 需要完成 KYC/KYB
  ├─ 需要 PCI DSS 合规
  └─ 完整的审计日志

  实现方式：
  ├─ 数据库层面：同一个数据库，用 environment 字段隔离
  │   → 所有查询都带 WHERE environment = 'test'/'live'
  ├─ API Key 层面：sk_test_* 只能访问沙箱数据
  ├─ 网关层面：
  │   → VCN：沙箱用 AgentCard.sh 的测试模式（底层 Stripe 测试模式）
  │   → NetworkToken：沙箱用 EvoNet 的测试环境
  │   → X402：沙箱用测试链（如 Base Sepolia）
  └─ Webhook 层面：沙箱和生产用不同的 Webhook 端点
```

---

## 十二、监控与告警

### 12.1 关键指标

```text
业务指标：
  token.created.count        Token 创建数量（按类型分）
  token.created.amount       Token 创建金额
  token.spent.amount         实际消费金额
  token.utilization_rate     Token 使用率（spent / created）
  authorization.success_rate 授权成功率
  authorization.latency_p99  授权延迟 P99

安全指标：
  auth.failed.count          认证失败次数（可能是 Key 泄露）
  policy.rejected.count      策略拒绝次数（可能是 Agent 被劫持）
  token.anomaly.count        异常 Token 使用（频率/金额/商户异常）

系统指标：
  api.latency_p99            API 延迟 P99
  api.error_rate             API 错误率
  ledger.balance_mismatch    账本余额不一致（最严重的告警！）
  gateway.timeout_rate       网关超时率
```

### 12.2 告警规则

```text
P0（立即响应）：
  ledger.balance_mismatch > 0     → 账本借贷不平衡，可能有资金问题
  auth.failed.count > 100/min     → 可能有人在暴力破解 API Key
  gateway.error_rate > 50%        → 支付网关可能宕机

P1（1 小时内响应）：
  authorization.success_rate < 80% → 授权成功率异常下降
  policy.rejected.count > 50/hour  → 大量策略拒绝，可能有 Agent 被劫持
  token.anomaly.count > 10/hour    → 异常 Token 使用模式

P2（24 小时内响应）：
  token.utilization_rate < 20%     → Token 使用率过低，可能有产品问题
  api.latency_p99 > 5s             → API 延迟过高
```

---

## 十三、每日对账

```text
对账是支付系统的"体检"——每天检查内部记录和外部网关是否一致。

每日对账流程：
  1. 从各支付网关拉取昨日所有交易记录
  2. 与内部 payment_transactions 表逐笔比对
  3. 与 ledger_entries 表比对金额
  4. 检查 ledger_accounts 的 cached_balance 是否等于 SUM(entries)
  5. 生成对账报告
  6. 差异 > 0 → 自动告警 → 人工介入

常见差异原因：
  → 网络超时导致的重复记录
  → 退款/争议处理中的时间差
  → Bug（最不想看到的原因）
```

---

## 十四、实施路线图

```text
如果你从零开始，建议按这个顺序：

Phase 1（Week 1-2）：基础骨架
  □ 数据库 Schema 建表（含 prefunded_accounts）
  □ User/Developer/Member CRUD API
  □ API Key 管理（创建/验证/轮换/撤销）
  □ 基础认证中间件
  □ 审计日志
  □ 沙箱环境隔离（environment 字段）

Phase 2（Week 3-4）：账本 + VCN
  □ 复式账本核心（ledger_accounts + ledger_entries）
  □ VCN 网关对接（AgentCard.sh）
  □ Token 创建/查询/关闭 API
  □ Webhook 接收 + 签名验证 + 事件去重
  □ 实时授权决策（issuing_authorization.request）
  □ 幂等性实现

Phase 3（Week 5-6）：策略 + Network Token + 预充值
  □ 策略引擎（创建时评估 + 实时授权评估）
  □ Network Token 网关对接（EvoNet）
  □ 预充值账户（充值/扣减/提现）
  □ 每日对账脚本
  □ 监控指标 + 告警规则

Phase 4（Week 7-8）：X402 + 生产加固
  □ X402 网关对接（参考 09 文档）
  □ 限流（Rate Limiting）
  □ 错误码体系完善
  □ API 文档（OpenAPI/Swagger）
  □ 沙箱环境完整测试
  □ 安全审查（PCI DSS 自评）
  □ 发出 Webhook（通知客户交易状态）
```

---

## 十五、阅读顺序指南

```text
你要做 AgentToken 后端，建议按这个顺序读文档：

═══════════════════════════════════════════════════
第一步：理解支付行业基础（1-2 天）
═══════════════════════════════════════════════════

  01-支付与Agent支付知识深度详解.md
  ├─ 重点读：第一章（四方模型）、第二章（Tokenization）、
  │         第四章（KYC/KYB）、第五章（PCI DSS/Vault/HSM）
  └─ 目的：理解你在做的事情的行业背景

  02-支付行业术语小白指南.md
  └─ 当字典用，遇到不懂的术语来查

═══════════════════════════════════════════════════
第二步：理解产品设计（半天）
═══════════════════════════════════════════════════

  ExportBlock 文件夹中的原始设计文档
  └─ 这是产品蓝图，理解"要做什么"

  07-AgentToken-CLI设计规范与数据模型.md
  └─ 这是对原始设计的学习笔记整理，更通俗

═══════════════════════════════════════════════════
第三步：理解交易生命周期和错误处理（1 天）
═══════════════════════════════════════════════════

  08-Agent支付全生命周期与费用结构.md
  ├─ 重点读：每种支付协议的完整交易流程
  ├─ 重点读：错误处理章节（网络超时、余额不足、重复支付）
  └─ 目的：知道每种 Token 从创建到结算的完整链路

═══════════════════════════════════════════════════
第四步：开始写代码（参考本文档）
═══════════════════════════════════════════════════

  10-AgentToken后端工程落地指南.md（本文档）
  ├─ 按 Phase 1-4 的顺序实施
  ├─ 数据库 Schema → 账本 → VCN 对接 → 策略引擎 → ...
  └─ 遇到具体问题时回头查 01/08 的对应章节

═══════════════════════════════════════════════════
第五步：X402 链上支付（当你做到 Phase 4 时）
═══════════════════════════════════════════════════

  09-X402链上支付基础设施工程实战.md
  └─ 完整的 X402 工程实现，直接参考

═══════════════════════════════════════════════════
按需查阅（不需要按顺序读）
═══════════════════════════════════════════════════

  03-AI Agent支付行业全景图.md     → 了解竞品和市场格局
  04-AgentToken产品设计分析.md     → 深入理解产品定位和竞品对比
  05-Agent支付落地案例.md          → 看别人怎么做的
  06-Agent支付风控与经济学.md      → 做风控和安全时参考
  15-Agent安全与治理/01.md 第4.2节 → API Key 为什么是反模式
```

```text
一句话总结：
  01（行业基础）→ 原始设计文档（产品蓝图）→ 07（数据模型）
  → 08（交易生命周期）→ 10（本文档，动手写代码）→ 09（X402 实现）
```

---

## 十六、相关文档

```text
本文涉及的知识点在其他文档中的位置：

支付基础（四方模型、Tokenization、KYC）
  → 01-支付与Agent支付知识深度详解.md

数据模型和 CLI 设计
  → 07-AgentToken-CLI设计规范与数据模型.md

各协议的交易生命周期和错误处理
  → 08-Agent支付全生命周期与费用结构.md

X402 链上支付的完整工程实现
  → 09-X402链上支付基础设施工程实战.md

Agent 支付风控（Prompt Injection 防御、私钥安全）
  → 06-Agent支付风控与经济学.md

API Key 安全（为什么静态 Key 是反模式）
  → 15-Agent安全与治理/01-Agent身份与权限.md 第 4.2 节
```

## 📖 参考资料

- [Modern Treasury: How to Scale a Ledger](https://www.moderntreasury.com/journal/how-to-scale-a-ledger-part-iii) — 复式账本设计权威指南
- [Modern Treasury: Accounting for Developers](https://www.moderntreasury.com/journal/accounting-for-developers-part-ii) — 开发者会计入门
- [Alita Software: Database Design for Financial Transactions](https://alita-software.com/blog/database-design-financial-transactions) — 金融交易数据库设计模式
- [Stripe: API Keys Best Practices](https://docs.stripe.com/keys-best-practices) — Stripe API Key 管理最佳实践
- [Stripe: Idempotent Requests](https://docs.stripe.com/plan-integration/get-started/server-side-integration) — Stripe 幂等性设计
- [Stripe Issuing: Virtual Cards](https://docs.stripe.com/issuing) — Stripe 虚拟卡发卡文档
- [AgentCard.sh: API Reference](https://docs.agentcard.sh/api-reference/overview) — VCN 底层 API（基于 Stripe Issuing）
- [EvoNet: Network Token Management](https://docs.everonet.com/en-us/gateway/developer-portal/online/network-token-management) — NetworkToken 底层 API
- [freeCodeCamp: Build a Bank Ledger in Go](https://www.freecodecamp.org/news/build-a-bank-ledger-in-go-with-postgresql-using-the-double-entry-accounting-principle/) — 复式账本实战教程
- [Sandorian: Webhook Handling for Payment Systems](https://sandorian.com/fintech/kb/webhook-handling-payment-systems) — 支付 Webhook 最佳实践
- [Marqeta: JIT Funding](https://www.marqeta.com/docs/developer-guides/configuring-gateway-jit-funding) — 实时授权决策（JIT Funding）
- [Apidog: Payment Webhook Best Practices](https://apidog.com/blog/payment-webhook-best-practices/) — Webhook 幂等性和重试