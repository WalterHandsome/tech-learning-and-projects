# Agent Payment API - MongoDB 数据库设计

> 最后更新: 2026-04-15

## 整体思路

Agent Payment API 的数据与现有 MySQL 业务完全隔离，全部存储在 MongoDB 中（复用现有 Motor 连接池）。所有 collection 统一加 `ap_` 前缀避免命名冲突。

ID 生成策略：使用带业务前缀的 ULID 作为 `_id`（如 `org_01HXYZ...`），兼顾可读性和全局唯一性。

## 对象层级

```
Organization (ap_organizations)
├── Developer (ap_developers)  ← 1:N
│   ├── API Key (ap_api_keys)  ← 1:1
│   └── Member (ap_members)    ← 1:N，可选
│
├── Payment Method (ap_payment_methods)  ← 通过 developer_id 关联
└── Token (ap_tokens)                    ← 通过 developer_id + reference_id 关联
```

辅助 collection：

```
ap_magic_links      ← 注册/登录的邮件验证流程
ap_refresh_tokens   ← access_token 刷新和登出失效
```

---

## Collection 1: `ap_organizations`

对应 API 第 1-2 节。

```json
{
  "_id": "org_01HXYZ...",
  "name": "Acme AI",
  "email": "ops@acme.ai",
  "status": "pending | active | disabled",
  "created_at": ISODate("2026-04-14T10:00:00Z"),
  "updated_at": ISODate("2026-04-14T10:00:00Z")
}
```

索引：

| 索引 | 类型 | 用途 |
|------|------|------|
| `email` | unique | 注册/登录时按邮箱查找 |
| `status` | 普通 | 按状态过滤 |

---

## Collection 2: `ap_magic_links`

对应 API 第 1.1-1.4 节，邮件验证流程。

```json
{
  "_id": "mlt_01HXYZ...",
  "organization_id": "org_01HXYZ...",
  "email": "ops@acme.ai",
  "purpose": "register | login",
  "status": "pending | consumed | expired",
  "access_token": null,
  "refresh_token": null,
  "token_expires_at": null,
  "is_new_organization": true,
  "created_at": ISODate("2026-04-14T10:00:00Z"),
  "expires_at": ISODate("2026-04-14T10:10:00Z"),
  "consumed_at": null
}
```

说明：

- `status=pending` 时 `access_token` / `refresh_token` 为 null
- 用户点击邮件链接后（consume），后端写入 token 并将 status 改为 `consumed`
- 调用方轮询此 collection 获取结果

索引：

| 索引 | 类型 | 用途 |
|------|------|------|
| `email, status` | 复合 | 查找某邮箱的待验证链接 |
| `organization_id` | 普通 | 按 org 查找 |
| `expires_at` | TTL (3600s) | 过期后 1 小时自动清理 |

---

## Collection 3: `ap_refresh_tokens`

对应 API 第 1.5-1.6 节，token 刷新和登出。

```json
{
  "_id": "rtk_01HXYZ...",
  "organization_id": "org_01HXYZ...",
  "token_hash": "sha256_hex_64chars",
  "is_revoked": false,
  "created_at": ISODate("2026-04-14T10:00:00Z"),
  "expires_at": ISODate("2026-05-14T10:00:00Z"),
  "revoked_at": null
}
```

说明：

- 存储 refresh_token 的 SHA-256 哈希，不存明文
- 登出时将 `is_revoked` 设为 true
- 刷新时验证 hash + 未吊销 + 未过期

索引：

| 索引 | 类型 | 用途 |
|------|------|------|
| `token_hash` | unique | 刷新时按 hash 查找 |
| `organization_id` | 普通 | 登出时批量吊销 |
| `expires_at` | TTL (0s) | 过期后自动删除 |

---

## Collection 4: `ap_developers`

对应 API 第 3 节。

```json
{
  "_id": "dev_01HXYZ...",
  "organization_id": "org_01HXYZ...",
  "name": "Acme Travel Agent",
  "email": "dev-team@acme.ai",
  "status": "active | disabled",
  "created_at": ISODate("2026-04-14T10:30:00Z"),
  "updated_at": ISODate("2026-04-14T10:30:00Z")
}
```

索引：

| 索引 | 类型 | 用途 |
|------|------|------|
| `organization_id` | 普通 | 列出某 org 下所有 developer |
| `organization_id, email` | unique | 同一 org 下邮箱唯一 |
| `status` | 普通 | 按状态过滤 |

---

## Collection 5: `ap_api_keys`

对应 API 第 4 节。每个 Developer 只有一个 Key。

```json
{
  "_id": "key_01HXYZ...",
  "developer_id": "dev_01HXYZ...",
  "organization_id": "org_01HXYZ...",
  "key_hash": "sha256_hex_64chars",
  "key_prefix": "dev_key_live_",
  "status": "active | disabled",
  "created_at": ISODate("2026-04-14T10:30:00Z"),
  "last_used_at": null,
  "rotated_at": null,
  "disabled_at": null
}
```

说明：

- `key_hash` 存储 API Key 的 SHA-256 哈希，完整 Key 只在创建/rotate 时返回一次
- rotate 时更新 `key_hash` + `rotated_at`，旧 Key 立即失效
- disable 时设置 `status=disabled` + `disabled_at`

索引：

| 索引 | 类型 | 用途 |
|------|------|------|
| `key_hash` | unique | 认证时按 hash 查找 |
| `developer_id` | unique | 每个 developer 只有一个 key |
| `organization_id` | 普通 | 按 org 查找 |
| `status` | 普通 | 过滤有效 key |

---

## Collection 6: `ap_members`

对应 API 第 5 节。可选能力，只禁用不删除。

```json
{
  "_id": "mem_01HXYZ...",
  "developer_id": "dev_01HXYZ...",
  "organization_id": "org_01HXYZ...",
  "name": "Alice",
  "email": "alice@example.com",
  "status": "active | disabled",
  "created_at": ISODate("2026-04-14T13:00:00Z"),
  "updated_at": ISODate("2026-04-14T13:00:00Z"),
  "disabled_at": null
}
```

索引：

| 索引 | 类型 | 用途 |
|------|------|------|
| `developer_id` | 普通 | 列出某 developer 下所有 member |
| `developer_id, email` | unique, partial (`email != null`) | 同一 developer 下邮箱唯一（email 非空时） |
| `organization_id` | 普通 | 按 org 查找 |
| `status` | 普通 | 按状态过滤 |

---

## Collection 7: `ap_payment_methods`

对应 API 第 6 节。静默绑卡。

### 绑卡策略

固定使用 `networkTokenOnly=false`（默认值）调用 Evo `POST paymentMethod`：

- Gateway Token **一定返回**，存入 `evo_gateway_token_value`
- Network Token **可能返回**（Visa/Mastercard 且发卡行支持时），有就存，没有则 `evo_nw_*` 字段为 null

### Evo 响应字段审核

```
paymentMethod
├── card                          ← 原始卡信息
│   ├── first6No: "520473"        ✅ 存 → card_first6（BIN 识别、风控）
│   ├── last4No: "4595"           ✅ 存 → last4（展示）
│   ├── fundingType: "debit"      ✅ 存 → funding_type（风控+展示）
│   ├── issuingBank: "NORTHERN.." ✅ 存 → issuing_bank（展示）
│   ├── issuingCountry: "USA"     ✅ 存 → issuing_country（风控）
│   └── paymentBrand: "Mastercard"✅ 存 → brand（展示+逻辑判断）
│
├── merchantTransInfo
│   ├── merchantTransID           ✅ 存 → evo_merchant_trans_id（获取 cryptogram 时作为 originalMerchantTxId）
│   └── merchantTransTime         ❌ 不存（可从 created_at 推导）
│
├── token                         ← Gateway Token 信息
│   ├── value                     ✅ 存 → evo_gateway_token_value（GW token，内部扣款用）
│   ├── fingerprint               ✅ 存 → evo_token_fingerprint（卡号指纹，判断是否重复绑卡）
│   ├── userReference             ❌ 不存（请求时传入的，已知）
│   ├── vaultID                   ❌ 不存（单独存 evo_vault_id）
│   ├── expiryDate                ❌ 不存（永久有效时不返回）
│   ├── status                    ❌ 不存（只有成功才写入）
│   ├── createTime                ❌ 不存（用 created_at）
│   └── updateTime                ❌ 不存
│
├── networkToken                  ← Network Token 信息（Visa/Mastercard 时自动返回）
│   ├── tokenID                   ✅ 存 → evo_nw_token_id（获取 cryptogram 的入参）
│   ├── value                     ✅ 存 → evo_nw_token_value（调用方自行支付时需要）
│   ├── expiryDate: "0529"        ✅ 存 → evo_nw_token_expiry_date（支付时必传）
│   ├── paymentBrand              ❌ 不存（与 card.paymentBrand 重复）
│   ├── status: "enabled"         ✅ 存 → evo_nw_token_status（判断 token 是否可用）
│   ├── first6No                  ❌ 不存（与 card.first6No 重复）
│   ├── last4No: "0694"           ✅ 存 → evo_nw_token_last4（token 化后的卡号后四位）
│   ├── tokenReferenceID          ✅ 存 → evo_nw_token_reference_id（Evo 侧引用）
│   ├── paymentAccountReference   ✅ 存 → evo_payment_account_reference（卡网络级别账户标识）
│   ├── supportDeviceBinding      ❌ 不存（功能未开放）
│   └── digitalCardData
│       └── artUri                ✅ 存 → evo_art_uri（卡面图片）
│
├── paymentAccountReference       ❌ 不存（与 networkToken 内的重复）
├── paymentMethodVariant          ❌ 不存（固定值）
└── status: "Success"             ❌ 不存（只有成功才写入）
```

### 文档结构

```json
{
  "_id": "pm_01HXYZ...",
  "reference_id": "ref_bind_01HXYZ...",
  "developer_id": "dev_01HXYZ...",
  "organization_id": "org_01HXYZ...",
  "member_id": null,

  // ── 卡面信息（API 可暴露）──
  "brand": "Mastercard",
  "last4": "4595",
  "exp_month": 12,
  "exp_year": 2027,
  "card_first6": "520473",
  "funding_type": "debit",
  "issuing_bank": "NORTHERN BANK &TRUST COMPANY",
  "issuing_country": "USA",

  // ── Evo 公共字段（内部，API 不暴露）──
  "evo_merchant_trans_id": "tok_1776224917",
  "evo_vault_id": "90451900",

  // ── Gateway Token（内部，用于 VCN/X402 扣款）──
  "evo_gateway_token_value": "pmt_9ab5560fb00c2fe9a56606593a8af294",
  "evo_token_fingerprint": "286fcea14de3eaf021f0304ca34d3f4c",

  // ── Network Token（内部，用于调用方自行支付）──
  // Visa/Mastercard 时有值，其他卡品牌为 null
  "evo_nw_token_id": "ch8CeiJ2Sh6sbFfwy6caNw000000000000US",
  "evo_nw_token_value": "5204731638380694",
  "evo_nw_token_expiry_date": "0529",
  "evo_nw_token_last4": "0694",
  "evo_nw_token_status": "enabled",
  "evo_nw_token_reference_id": "DM4MMC1US000000099d6f4252cc347569844b0d8d11d2029",
  "evo_payment_account_reference": "50012MOIQJ7EFDM0FSDAGZ2JU76DN",
  "evo_art_uri": "https://sbx.assets.mastercard.com/card-art/combined-image-asset/42d31eae-...",

  // ── 状态 ──
  "status": "active | disabled",
  "created_at": ISODate("2026-04-14T13:05:00Z"),
  "disabled_at": null
}
```

说明：

- 绑卡固定使用 `networkTokenOnly=false`，Gateway Token 一定有，Network Token 有就存没有就 null
- `reference_id` 是后续创建 VCN / X402 / Network Token 的必传参数
- 所有 `evo_` 前缀字段是内部存储，API 不暴露
- `member_id` 为 null 表示便捷模式，有值表示 Member 模式
- `last4` 是原始卡号后四位，`evo_nw_token_last4` 是 token 化后的卡号后四位，两者不同
- 调用方请求创建 Network Token 时，如果 `evo_nw_token_id` 为 null，返回错误码 `1005`

索引：

| 索引 | 类型 | 用途 |
|------|------|------|
| `reference_id` | unique | 创建 token 时按凭证查找 |
| `developer_id` | 普通 | 列出某 developer 的所有绑卡 |
| `developer_id, member_id` | 复合 | 查询某 member 的绑卡 |
| `organization_id` | 普通 | 按 org 查找 |
| `status` | 普通 | 过滤有效绑卡 |

---

## Collection 8: `ap_tokens`

对应 API 第 7-10 节。三种 Token 类型统一存储，通过 `type` 区分。

### 公共字段

```json
{
  "_id": "tok_01HXYZ...",
  "type": "vcn | network_token | x402",
  "reference_id": "ref_bind_01HXYZ...",
  "status": "active | closed | OPEN | FROZEN | CLOSED",
  "developer_id": "dev_01HXYZ...",
  "organization_id": "org_01HXYZ...",
  "member_id": "mem_01HXYZ..." | null,
  "payment_method_id": "pm_01HXYZ...",
  "idempotency_key": null,
  "created_at": ISODate("2026-04-14T14:00:00Z"),
  "closed_at": null
}
```

### type=vcn 时附带 `vcn` 字段

```json
{
  "vcn": {
    "id": "card_001",
    "last4": "0039",
    "expiry": "03/28",
    "spend_limit_cents": 2500,
    "balance_cents": 2500,
    "status": "OPEN | CLOSED",
    "created_at": ISODate("2026-04-14T14:00:00Z"),
    "full_card_number_encrypted": "enc_xxx",
    "cvv_encrypted": "enc_xxx"
  }
}
```

`full_card_number_encrypted` 和 `cvv_encrypted` 是内部加密存储字段，API 不暴露。

### type=network_token 时附带 `network_token` 字段

```json
{
  "network_token": {
    "payment_brand": "Mastercard",
    "eci": "06",
    "token_cryptogram": "AJ89n6XIUf2dAAG4aY/GAAADFA==",
    "expiry_date": "0529",
    "value": "5204731638380694",
    "first6_no": "520473",
    "last4_no": "0694",
    "funding_type": "debit",
    "issuing_bank": "NORTHERN BANK &TRUST COMPANY",
    "issuing_country": "USA"
  }
}
```

### type=x402 时附带 `x402` 字段

```json
{
  "x402": {
    "amount": 500,
    "spent": 0,
    "balance": 500,
    "currency": "USD",
    "chain": "base-mainnet",
    "wallet_address": "0x1234...abcd",
    "intent": "Agent needs to call weather API"
  }
}
```

### 索引

| 索引 | 类型 | 用途 |
|------|------|------|
| `type` | 普通 | 按类型过滤 |
| `developer_id` | 普通 | 列出某 developer 的所有 token |
| `developer_id, type` | 复合 | 按 developer + 类型查询 |
| `member_id` | 普通 | 按 member 过滤 |
| `reference_id` | 普通 | 按绑卡凭证过滤 |
| `payment_method_id` | 普通 | 按绑卡记录查找 |
| `organization_id` | 普通 | 按 org 查找 |
| `status` | 普通 | 按状态过滤 |
| `idempotency_key` | unique, sparse | X402 幂等控制 |
| `created_at` | 降序 | 按时间排序 |

---

## 汇总

| Collection | 文档数量级 | _id 前缀 | 说明 |
|------------|-----------|----------|------|
| `ap_organizations` | 千级 | `org_` | 组织账户 |
| `ap_magic_links` | 临时，TTL 自动清理 | `mlt_` | 邮件验证流程 |
| `ap_refresh_tokens` | 万级，TTL 自动清理 | `rtk_` | 刷新凭证 |
| `ap_developers` | 万级 | `dev_` | 开发者 |
| `ap_api_keys` | 万级 | `key_` | API Key（1:1 对应 developer） |
| `ap_members` | 十万级 | `mem_` | 终端用户 |
| `ap_payment_methods` | 十万级 | `pm_` | 绑卡记录，`reference_id` 前缀 `ref_bind_` |
| `ap_tokens` | 百万级 | `tok_` | VCN / Network Token / X402 统一存储 |

---

## 设计要点

1. **三种 Token 统一存储**：`ap_tokens` 用 `type` 字段区分，各自详情嵌套在对应子文档中。GET /tokens 列表查询只需查一个 collection，简化实现。

2. **安全字段隔离**：`evo_` 前缀字段（`evo_token_id`、`evo_token_value` 等）和 `full_card_number_encrypted`、`cvv_encrypted` 等内部字段存储在 MongoDB 中但 API 层不暴露。

3. **TTL 自动清理**：`ap_magic_links` 和 `ap_refresh_tokens` 使用 MongoDB TTL 索引自动清理过期数据，无需额外定时任务。

4. **幂等控制**：`ap_tokens` 的 `idempotency_key` 使用 unique + sparse 索引，只有 X402 类型会设置此字段。

5. **partial unique index**：`ap_members` 的 `developer_id + email` 唯一索引加了 `email != null` 条件，允许 email 为空的 member 不受唯一约束。

6. **与现有业务隔离**：所有 collection 使用 `ap_` 前缀，与现有的 `shopping_orders`、`agno_sessions`、`shopping_sessions`、`vcn_audit_log` 等 collection 互不干扰。
