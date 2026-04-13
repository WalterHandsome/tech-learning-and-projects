# Agent 支付全生命周期、错误处理与费用结构

> 本文档补充 01-07 文档中缺失的关键维度：每种 Agent 支付协议的完整交易生命周期（从发起到结算）、
> 错误处理机制、退款/争议流程、以及手续费结构。建议在阅读完 01（支付基础）和 05（协议落地案例）后再看本文。

---

## 一、为什么需要这份文档？

前面的文档讲了"每个协议是什么"和"怎么用"，但没有回答三个关键问题：

1. 一笔 Agent 支付从发起到钱到账，中间经历了哪些步骤？每一步可能出什么错？
2. 如果支付失败、超时、或者买错了东西，怎么退款？谁承担损失？
3. 每笔交易的真实成本是多少？哪些场景用哪种协议最划算？

这三个问题直接决定了你在生产环境中选择哪种协议。

---

## 二、费用结构总览（先看结论）

| 协议 | 单笔手续费 | 最低可行交易额 | 结算速度 | 退款能力 |
|------|-----------|--------------|---------|---------|
| x402 | Gas ~$0.001-0.01 | $0.001 | 秒级（链上确认） | ❌ 链上不可逆 |
| MPP | 会话内 Gas 分摊，单笔趋近 $0 | $0.001 | 会话结束时批量结算 | ⚠️ 会话内可调整 |
| ACP (Stripe) | 2.9% + $0.30 | ~$10 | T+2（工作日） | ✅ 完整退款 |
| Mastercard Agent Pay | 1.5%-3.5% | ~$1 | T+1 到 T+3 | ✅ 卡组织争议 |
| Stripe Issuing | 无额外发卡费 | ~$1 | T+2 | ✅ Stripe 争议 |
| AP2 | 取决于底层支付方式 | 取决于底层 | 取决于底层 | ⚠️ Mandate 可追溯 |

核心结论：
- $0.001-$1 的微支付 → 只能用 x402 或 MPP（卡网络手续费会吃掉本金）
- $1-$50 的中等交易 → Mastercard Agent Pay 或 Stripe Issuing（卡网络手续费可接受）
- $50+ 的大额交易 → ACP/Stripe（完整的退款和争议保护值得 2.9% 的费率）
- 需要退款保护 → 必须走卡网络（x402/MPP 链上不可逆）

来源：[WorkOS: x402 vs Stripe MPP](https://workos.com/blog/x402-vs-stripe-mpp-how-to-choose-payment-infrastructure-for-ai-agents-and-mcp-tools-in-2026) (Content was rephrased for compliance with licensing restrictions)

---

## 三、x402 协议：完整生命周期

### 3.1 正常支付流程

```text
Agent（调用方）                    Facilitator（验证方）              服务方（API 提供者）
    │                                    │                              │
    │  1. GET /api/data                  │                              │
    ├───────────────────────────────────────────────────────────────────>│
    │                                    │                              │
    │  2. HTTP 402 Payment Required      │                              │
    │     Headers:                       │                              │
    │       X-Payment-Amount: 0.003      │                              │
    │       X-Payment-Currency: USDC     │                              │
    │       X-Payment-Address: 0xABC...  │                              │
    │       X-Payment-Network: base      │                              │
    │       X-Payment-Facilitator: url   │                              │
    │<──────────────────────────────────────────────────────────────────┤
    │                                    │                              │
    │  3. 构造支付 payload               │                              │
    │     签名 USDC 转账                  │                              │
    │                                    │                              │
    │  4. POST /verify (支付凭证)         │                              │
    ├───────────────────────────────────>│                              │
    │                                    │  5. 验证签名                  │
    │                                    │     提交链上交易               │
    │                                    │     等待确认                   │
    │  6. 验证通过，返回 receipt          │                              │
    │<───────────────────────────────────┤                              │
    │                                    │                              │
    │  7. GET /api/data + X-Payment-Receipt                             │
    ├───────────────────────────────────────────────────────────────────>│
    │                                    │                              │
    │  8. HTTP 200 OK + 数据             │                              │
    │<──────────────────────────────────────────────────────────────────┤

整个过程耗时：~200ms-2s（取决于链上确认速度）
```

### 3.2 错误处理

```text
x402 可能遇到的错误及处理方式：

错误 1：Agent 钱包余额不足
  触发时机：Agent 构造支付 payload 时发现 USDC 余额 < 请求金额
  Agent 行为：
    → 返回错误给调用方："Insufficient USDC balance"
    → 不发起链上交易（省 Gas）
  恢复方式：充值 USDC 到 Agent 钱包

错误 2：Gas 费不足
  触发时机：Agent 有足够 USDC 但没有足够 ETH 付 Gas
  Agent 行为：
    → 交易构造失败
    → 返回 "Insufficient gas" 错误
  恢复方式：充值少量 ETH 到 Agent 钱包（Base L2 上 ~$0.01 够用很久）

错误 3：Facilitator 验证失败
  触发时机：签名无效、金额不匹配、过期等
  Facilitator 返回：HTTP 400 + 错误原因
  Agent 行为：
    → 检查错误原因
    → 如果是过期 → 重新获取 402 响应，重新签名
    → 如果是签名错误 → 检查钱包配置

错误 4：链上交易失败
  触发时机：链上拥堵、nonce 冲突、合约异常
  表现：交易提交后长时间未确认，或 revert
  Agent 行为：
    → 等待超时（通常 30s）
    → 重试（增加 Gas price）或放弃
  注意：如果交易已提交但未确认，不要重复提交（可能导致双重支付）

错误 5：服务方不认 receipt
  触发时机：receipt 格式错误、服务方验证逻辑 bug
  表现：带 receipt 的请求仍返回 402
  Agent 行为：
    → 钱已经付了但没拿到服务 → 需要联系服务方
    → 这是 x402 最大的风险点（见退款部分）
```

### 3.3 退款机制

```text
x402 的退款现实：链上交易不可逆，没有原生退款机制。

场景 1：Agent 付了钱但服务方没返回数据
  → 钱已经在链上转走了
  → 没有"退款"按钮
  → 只能联系服务方协商退款（服务方主动发起一笔反向转账）
  → 如果服务方不配合 → 钱就没了

场景 2：Agent 买错了东西
  → 同上，链上不可逆
  → 但 x402 主要用于微支付（$0.001-$0.01），单笔损失极小

场景 3：服务方跑路
  → 没有卡组织的争议机制保护
  → 没有 Stripe 的退款保障
  → 纯粹的交易对手风险

行业应对方案：
  1. Facilitator 托管模式：钱先到 Facilitator，服务交付后再释放给服务方
     （类似支付宝的担保交易，但 x402 目前没有标准化实现）
  2. 信誉系统：基于链上历史记录评估服务方可信度
  3. 小额容忍：微支付场景下，单笔损失 $0.003 不值得追讨
```

### 3.4 费用明细

```text
x402 单笔交易的真实成本（Base L2，2026 年数据）：

  交易金额：$0.003（一次 API 调用）
  ├── USDC 转账 Gas 费：~$0.001-0.005（Base L2 极低）
  ├── Facilitator 手续费：通常 0%（Coinbase 目前不收）
  └── 总成本：$0.001-0.005

  对比传统卡支付：
  ├── Stripe 手续费：2.9% × $0.003 + $0.30 = $0.300087
  └── 手续费是交易额的 100 倍 → 完全不可行

  x402 的经济可行区间：
  ├── $0.001-$1.00：Gas 费占比 0.1%-10%，完全可行
  ├── $1.00-$10.00：Gas 费占比 <0.1%，非常划算
  └── $10.00+：Gas 费可忽略，但缺乏退款保护成为主要风险

来源：[Laevitas x402 Pay-Per-Request](https://apiv2.laevitas.ch/x402) (Content was rephrased for compliance with licensing restrictions)
来源：[x402 Payment Rails - Alea Research](https://alearesearch.substack.com/p/x402-payment-rails-for-the-agent) (Content was rephrased for compliance with licensing restrictions)
```

---

## 四、MPP 协议：完整生命周期

### 4.1 正常支付流程

MPP 和 x402 的关键区别：x402 是"每次请求独立付款"，MPP 是"先开会话再流式扣款"。

```text
Agent                              服务方                          Stripe/Tempo
  │                                  │                                │
  │  1. POST /mpp/session/create     │                                │
  │     { budget: $1.00 }            │                                │
  ├─────────────────────────────────>│                                │
  │                                  │  2. 创建支付会话                │
  │                                  │     预授权 $1.00                │
  │                                  ├───────────────────────────────>│
  │                                  │     session_id + token          │
  │                                  │<───────────────────────────────┤
  │  3. { session_id, token }        │                                │
  │<─────────────────────────────────┤                                │
  │                                  │                                │
  │  ─── 会话内多次调用 ───           │                                │
  │                                  │                                │
  │  4. GET /api/data-1              │                                │
  │     Authorization: MPP {token}   │                                │
  ├─────────────────────────────────>│  扣 $0.003                     │
  │  5. 200 OK + 数据                │                                │
  │<─────────────────────────────────┤                                │
  │                                  │                                │
  │  6. GET /api/data-2              │                                │
  │     Authorization: MPP {token}   │                                │
  ├─────────────────────────────────>│  扣 $0.005                     │
  │  7. 200 OK + 数据                │                                │
  │<─────────────────────────────────┤                                │
  │                                  │                                │
  │  ... 重复 N 次 ...               │                                │
  │                                  │                                │
  │  8. POST /mpp/session/close      │                                │
  ├─────────────────────────────────>│                                │
  │                                  │  9. 结算实际消费 $0.010         │
  │                                  │     释放剩余 $0.990             │
  │                                  ├───────────────────────────────>│
  │  10. { settled: $0.010 }         │                                │
  │<─────────────────────────────────┤                                │

关键优势：N 次 API 调用只需 1 次链上结算，Gas 费被 N 次调用分摊
```

### 4.2 错误处理

```text
MPP 特有的错误场景：

错误 1：会话预算耗尽
  触发时机：累计消费达到会话预算上限（如 $1.00）
  服务方返回：HTTP 402 + "Session budget exhausted"
  Agent 行为：
    → 关闭当前会话
    → 开启新会话（更高预算）
    → 或停止调用

错误 2：会话超时
  触发时机：会话空闲时间超过服务方设定的 TTL
  表现：下一次请求返回 401 "Session expired"
  Agent 行为：
    → 已消费部分自动结算
    → 未消费部分自动释放
    → 需要开启新会话继续

错误 3：服务方宕机（会话中途）
  触发时机：Agent 已开启会话并消费了部分金额，服务方突然不可用
  风险：预授权的资金被锁定，无法释放
  处理：
    → Stripe/Tempo 有会话超时机制（通常 24h）
    → 超时后自动结算已消费部分，释放剩余
    → Agent 不会永久丢失资金

错误 4：结算失败
  触发时机：会话关闭时链上结算交易失败
  处理：
    → Stripe 会自动重试结算
    → 如果持续失败，预授权最终会过期释放
    → Agent 可能需要等待 24-48h
```

### 4.3 退款机制

```text
MPP 的退款比 x402 稍好，但仍然有限：

会话内调整（结算前）：
  → 如果服务方发现某次调用有问题，可以在会话内"退回"该笔扣款
  → 最终结算时只结算净消费金额
  → 这相当于"会话内退款"，但需要服务方主动配合

结算后退款：
  → 链上结算完成后，和 x402 一样不可逆
  → 需要服务方主动发起反向转账
  → Stripe 的 MPP 结算层可能提供争议机制（待确认，目前文档未明确）

Stripe 基础设施的优势：
  → MPP 通过 Stripe 结算时，Stripe 提供 Dashboard、收据、争议解决、税务报告
  → 这比纯 x402 的"链上裸奔"要好得多
  → 但具体的争议流程和退款政策尚未公开

来源：[Cred Protocol: Stripe MPP on Tempo](https://credprotocol.com/blog/stripe-mpp-tempo-crypto-deposits) (Content was rephrased for compliance with licensing restrictions)
```

### 4.4 费用明细

```text
MPP 单次会话的真实成本：

  场景：Agent 在一个任务中调用 50 次 API，每次 $0.003

  x402 方式（每次独立付款）：
  ├── 50 次链上交易
  ├── Gas 费：50 × $0.003 = $0.15
  ├── API 费用：50 × $0.003 = $0.15
  └── 总成本：$0.30（Gas 占 50%）

  MPP 方式（会话模式）：
  ├── 1 次开启会话（链上预授权）：~$0.005
  ├── 50 次 API 调用（链下记账，无 Gas）：$0
  ├── 1 次关闭会话（链上结算）：~$0.005
  ├── API 费用：50 × $0.003 = $0.15
  └── 总成本：$0.16（Gas 占 6%）

  节省：$0.30 → $0.16，省了 47%

  MPP 的经济优势在高频场景下更明显：
  ├── 10 次调用：x402 Gas $0.03 vs MPP Gas $0.01 → 省 67%
  ├── 100 次调用：x402 Gas $0.30 vs MPP Gas $0.01 → 省 97%
  └── 1000 次调用：x402 Gas $3.00 vs MPP Gas $0.01 → 省 99.7%

来源：[WorkOS: x402 vs Stripe MPP](https://workos.com/blog/x402-vs-stripe-mpp-how-to-choose-payment-infrastructure-for-ai-agents-and-mcp-tools-in-2026) (Content was rephrased for compliance with licensing restrictions)
```


---

## 五、ACP 协议（Stripe + OpenAI）：完整生命周期

### 5.1 正常支付流程

ACP 的核心思路：Agent 充当"购物助手"，在用户和商家之间协调结账流程，支付通过 Stripe 的 SharedPaymentToken（SPT）完成。

```text
用户                    Agent（如 ChatGPT）              商家（Seller）              Stripe
  │                          │                              │                        │
  │  1. "帮我买这个商品"      │                              │                        │
  ├─────────────────────────>│                              │                        │
  │                          │                              │                        │
  │                          │  2. CreateCheckoutRequest     │                        │
  │                          │     { sku, quantity }         │                        │
  │                          ├─────────────────────────────>│                        │
  │                          │                              │                        │
  │                          │  3. CheckoutResponse          │                        │
  │                          │     { cart, total, shipping   │                        │
  │                          │       options, payment_methods}│                       │
  │                          │<─────────────────────────────┤                        │
  │                          │                              │                        │
  │  4. 展示购物车和选项      │                              │                        │
  │     "总计 $49.99，选配送？"│                              │                        │
  │<─────────────────────────┤                              │                        │
  │                          │                              │                        │
  │  5. "用标准配送，确认购买" │                              │                        │
  ├─────────────────────────>│                              │                        │
  │                          │                              │                        │
  │                          │  6. UpdateCheckoutRequest     │                        │
  │                          │     { shipping: standard }    │                        │
  │                          ├─────────────────────────────>│                        │
  │                          │                              │                        │
  │                          │  7. 用户确认支付意图           │                        │
  │                          │     Agent 向 Stripe 申请 SPT  │                        │
  │                          ├──────────────────────────────────────────────────────>│
  │                          │                              │                        │
  │                          │  8. Stripe 返回 SPT           │                        │
  │                          │     (一次性、限额、限商家)      │                        │
  │                          │<──────────────────────────────────────────────────────┤
  │                          │                              │                        │
  │                          │  9. CompleteCheckoutRequest   │                        │
  │                          │     { spt, amount }           │                        │
  │                          ├─────────────────────────────>│                        │
  │                          │                              │  10. 商家用 SPT 创建    │
  │                          │                              │      PaymentIntent      │
  │                          │                              ├───────────────────────>│
  │                          │                              │                        │
  │                          │                              │  11. 支付确认            │
  │                          │                              │<───────────────────────┤
  │                          │                              │                        │
  │                          │  12. 订单确认 + 订单号        │                        │
  │                          │<─────────────────────────────┤                        │
  │                          │                              │                        │
  │  13. "购买成功！订单号 xxx" │                             │                        │
  │<─────────────────────────┤                              │                        │

整个过程耗时：~5-30s（取决于用户交互速度）
结算到商家账户：T+2 工作日
```

### 5.2 错误处理

```text
ACP 可能遇到的错误及处理方式：

错误 1：商家 API 不可用
  触发时机：Agent 发送 CreateCheckoutRequest 但商家服务器无响应
  Agent 行为：
    → 重试 2-3 次（指数退避）
    → 如果持续失败 → 告知用户"商家暂时不可用"
    → 没有资金风险（还没到支付环节）

错误 2：SPT 创建失败
  触发时机：用户的支付方式无效、余额不足、或 Stripe 风控拦截
  Stripe 返回：错误码 + 原因（如 card_declined、insufficient_funds）
  Agent 行为：
    → 告知用户具体原因
    → 建议更换支付方式
    → 没有资金损失（SPT 未创建成功 = 没有扣款）

错误 3：SPT 过期
  触发时机：SPT 有时间限制（通常几分钟），用户犹豫太久
  表现：CompleteCheckoutRequest 返回 "token_expired"
  Agent 行为：
    → 重新申请 SPT
    → 如果用户仍想购买 → 重新走 Complete 流程

错误 4：商家处理 PaymentIntent 失败
  触发时机：商家端 Stripe 集成有 bug，或库存已售罄
  表现：CompleteCheckoutRequest 返回错误
  Agent 行为：
    → SPT 未被消费 → 自动失效，不会扣款
    → 告知用户"商家处理订单失败"
    → 建议稍后重试

错误 5：支付成功但商家未确认订单
  触发时机：PaymentIntent 成功但商家系统未生成订单
  风险：钱已扣但没有订单
  处理：
    → Stripe 有完整的交易记录
    → 用户可以通过 Stripe 发起退款
    → 商家有义务处理（否则面临 chargeback）

错误 6：网络中断（支付过程中）
  触发时机：Agent 发送 CompleteCheckoutRequest 后网络断开
  风险：不确定支付是否成功
  处理：
    → SPT 是幂等的（同一个 SPT 不会被重复扣款）
    → Agent 重连后查询订单状态
    → 如果已支付 → 获取订单确认
    → 如果未支付 → SPT 过期后重新发起
```

### 5.3 退款机制

```text
ACP 的退款是所有协议中最完善的（因为底层是 Stripe + 卡网络）：

场景 1：用户主动退款（商品不满意）
  流程：
    → 用户通过 Agent 或商家网站发起退款请求
    → 商家在 Stripe Dashboard 处理退款
    → Stripe 将资金退回用户的原始支付方式
    → 退款到账时间：5-10 个工作日
  费用：Stripe 不退还原始交易的手续费（2.9% + $0.30）

场景 2：商品未收到
  流程：
    → 用户联系商家 → 商家不配合
    → 用户联系发卡行发起 chargeback（争议）
    → 卡组织介入仲裁
    → 通常 30-90 天解决
  保护：用户几乎 100% 受保护（卡组织偏向持卡人）

场景 3：欺诈交易（Agent 被劫持）
  流程：
    → 用户发现未授权的交易
    → 联系发卡行报告欺诈
    → 发卡行立即临时退款（provisional credit）
    → 调查期间商家承担举证责任
  保护：Regulation Z（美国）保护消费者，最多承担 $50

场景 4：部分退款
  → Stripe 支持部分退款
  → 商家可以退还部分金额（如退运费但不退商品费）
  → Agent 可以代用户协商部分退款

ACP 退款的核心优势：
  1. Stripe 提供完整的退款 API 和 Dashboard
  2. 卡组织（Visa/Mastercard）提供争议仲裁机制
  3. 消费者保护法律（如 Regulation Z）提供法律保障
  4. 所有交易都有完整的审计记录

来源：[Stripe ACP 文档](https://docs.stripe.com/agentic-commerce/protocol) (Content was rephrased for compliance with licensing restrictions)
来源：[Crossmint: Agentic Payments Protocols Compared](https://www.crossmint.com/learn/agentic-payments-protocols-compared) (Content was rephrased for compliance with licensing restrictions)
```

### 5.4 费用明细

```text
ACP 单笔交易的真实成本：

  场景：Agent 帮用户在商家购买 $49.99 的商品

  费用分解（商家承担）：
  ├── Stripe 手续费：2.9% × $49.99 + $0.30 = $1.75
  ├── ACP 协议费：$0（ACP 本身不收费）
  ├── 卡组织交换费：已包含在 Stripe 费率中
  └── 商家实收：$49.99 - $1.75 = $48.24

  如果发生退款：
  ├── 退款金额：$49.99（全额退给用户）
  ├── Stripe 手续费：不退还（$1.75 商家损失）
  ├── 争议费：$15.00（如果走 chargeback 流程）
  └── 商家总损失：$49.99 + $1.75 + $15.00 = $66.74

  ACP 的经济可行区间：
  ├── $0.01-$10：手续费占比 6%-33%（$0.30 固定费用占比高）
  │   → 不适合微支付
  ├── $10-$100：手续费占比 3.2%-3.5%（合理区间）
  ├── $100+：手续费趋近 2.9%（大额交易最划算）
  └── 退款保护的价值：对于高客单价商品，2.9% 的费率换来完整的退款保护是值得的

  对比 x402：
  ├── $0.003 的 API 调用：ACP 手续费 $0.30 vs x402 Gas $0.003
  │   → ACP 完全不可行
  ├── $50 的商品购买：ACP 手续费 $1.75 vs x402 Gas $0.003
  │   → ACP 提供退款保护，值得多付 $1.75

来源：[Stripe 定价页面](https://stripe.com/pricing) (Content was rephrased for compliance with licensing restrictions)
来源：[ATXP: Agent Payment Protocols Compared](https://atxp.ai/blog/agent-payment-protocols-compared/) (Content was rephrased for compliance with licensing restrictions)
```


---

## 六、Mastercard Agent Pay：完整生命周期

### 6.1 正常支付流程

Mastercard Agent Pay 的核心创新：通过 Know Your Agent（KYA）身份验证 + Agentic Token（代理令牌）+ Purchase Intent（购买意图），让 Agent 在现有卡网络上完成交易，商家无需大幅改造。

```text
用户                Agent              KYA 验证服务          商家              发卡行/卡网络
  │                  │                    │                   │                   │
  │  1. 授权 Agent   │                    │                   │                   │
  │     代为购物      │                    │                   │                   │
  ├─────────────────>│                    │                   │                   │
  │                  │                    │                   │                   │
  │                  │  2. 提交 Agent 身份 │                   │                   │
  │                  │     请求 KYA 验证   │                   │                   │
  │                  ├───────────────────>│                   │                   │
  │                  │                    │                   │                   │
  │                  │  3. KYA 验证通过    │                   │                   │
  │                  │     返回验证等级     │                   │                   │
  │                  │     (Basic/Enhanced │                   │                   │
  │                  │      /Premium/      │                   │                   │
  │                  │      Enterprise)    │                   │                   │
  │                  │<───────────────────┤                   │                   │
  │                  │                    │                   │                   │
  │                  │  4. 申请 Agentic Token                 │                   │
  │                  │     (绑定用户卡、限额、限商家类别)        │                   │
  │                  ├──────────────────────────────────────────────────────────>│
  │                  │                    │                   │                   │
  │                  │  5. 发卡行签发 Agentic Token            │                   │
  │                  │     类型：SingleUse / SessionBound / Recurring             │
  │                  │<──────────────────────────────────────────────────────────┤
  │                  │                    │                   │                   │
  │                  │  6. 构造 Purchase Intent                │                   │
  │                  │     { 商品、金额、商家、用户授权证明 }    │                   │
  │                  │                    │                   │                   │
  │                  │  7. 提交支付请求（Agentic Token + Intent）│                  │
  │                  ├───────────────────────────────────────>│                   │
  │                  │                    │                   │                   │
  │                  │                    │                   │  8. 商家发起授权   │
  │                  │                    │                   │     请求到卡网络   │
  │                  │                    │                   ├──────────────────>│
  │                  │                    │                   │                   │
  │                  │                    │                   │  9. 卡网络验证：   │
  │                  │                    │                   │     - Token 有效性 │
  │                  │                    │                   │     - KYA 等级     │
  │                  │                    │                   │     - 限额检查     │
  │                  │                    │                   │     - 商家类别匹配 │
  │                  │                    │                   │                   │
  │                  │                    │                   │  10. 授权通过      │
  │                  │                    │                   │<──────────────────┤
  │                  │                    │                   │                   │
  │                  │  11. 支付成功 + 收据 │                  │                   │
  │                  │<───────────────────────────────────────┤                   │
  │                  │                    │                   │                   │
  │  12. "购买成功！" │                    │                   │                   │
  │<─────────────────┤                    │                   │                   │

整个过程耗时：~2-10s（和普通刷卡一样快）
结算到商家：T+1 到 T+3（标准卡网络结算周期）
```

### 6.2 Agentic Token 三种类型

```text
SingleUse（一次性令牌）：
  → 只能用于一笔交易
  → 交易完成后自动失效
  → 最安全，适合单次购买
  → 类似 Stripe Issuing 的一次性虚拟卡

SessionBound（会话绑定令牌）：
  → 在一个购物会话内可多次使用
  → 会话结束后失效
  → 适合"帮我买完这一单"的场景（可能涉及多个商家）
  → 有会话级别的总限额

Recurring（循环令牌）：
  → 可重复使用，有时间和金额限制
  → 适合订阅管理、定期采购
  → 需要更高的 KYA 验证等级（Premium 或 Enterprise）
  → 用户可随时撤销
```

### 6.3 错误处理

```text
Mastercard Agent Pay 的错误场景：

错误 1：KYA 验证失败
  触发时机：Agent 身份无法通过 Know Your Agent 验证
  原因：Agent 未注册、凭证过期、控制者 KYC 不足
  Agent 行为：
    → 无法获取 Agentic Token → 无法发起支付
    → 提示用户检查 Agent 注册状态
  资金风险：无（还没到支付环节）

错误 2：Agentic Token 被拒
  触发时机：发卡行拒绝签发 Token
  原因：用户卡状态异常、超出授权范围、风控拦截
  Agent 行为：
    → 告知用户"无法获取支付授权"
    → 建议用户检查卡状态或联系发卡行

错误 3：交易授权被拒
  触发时机：商家发起授权请求，卡网络拒绝
  原因：
    → 超出 Token 限额
    → 商家类别（MCC）不在允许范围内
    → KYA 等级不足以支持该交易金额
    → 地理位置限制
  Agent 行为：
    → 解析拒绝原因码
    → 如果是限额问题 → 告知用户需要提高授权额度
    → 如果是 MCC 限制 → 告知用户该商家类别不在授权范围内

错误 4：Token 过期
  触发时机：SingleUse Token 超时未使用，或 SessionBound Token 会话过期
  Agent 行为：
    → 重新申请新的 Token
    → 如果用户授权仍有效 → 自动重新申请
    → 如果用户授权已过期 → 需要用户重新授权

错误 5：商家不支持 Agentic Token
  触发时机：商家的 POS/支付网关不识别 Agentic Token 格式
  处理：
    → Mastercard 的设计是向后兼容的（Agentic Token 在卡网络层面和普通 Token 类似）
    → 但如果商家有额外的验证逻辑，可能会拒绝
    → Agent 需要回退到其他支付方式
```

### 6.4 退款机制

```text
Mastercard Agent Pay 的退款走标准卡网络争议流程：

场景 1：商品退货
  流程：
    → Agent 或用户联系商家发起退货
    → 商家处理退款 → 资金通过卡网络退回
    → 退款到账：5-10 个工作日
  和普通信用卡退款完全一样

场景 2：未授权交易（Agent 越权）
  这是 Mastercard Agent Pay 特有的场景：
    → 用户发现 Agent 购买了未授权的商品
    → 用户联系发卡行，提供 Purchase Intent 记录
    → 发卡行对比 Intent 和实际交易
    → 如果 Agent 确实越权 → 按欺诈处理，用户全额退款
  KYA + Purchase Intent 的审计记录在这里发挥关键作用：
    → 每笔交易都有"Agent 为什么买这个"的记录
    → 可以追溯 Agent 的决策是否符合用户授权

场景 3：标准 chargeback
  → 和普通信用卡 chargeback 流程完全一致
  → 用户 → 发卡行 → 卡网络 → 收单行 → 商家
  → 30-90 天解决
  → 用户受卡组织规则保护

Mastercard Agent Pay 退款的独特优势：
  1. Purchase Intent 提供了比普通卡交易更丰富的审计信息
  2. KYA 验证记录可以帮助判断责任归属
  3. Agentic Token 的限制条件（限额、限商家）本身就减少了争议发生的概率
  4. 完全兼容现有卡组织争议机制，不需要新的基础设施

来源：[Mastercard Agent Pay 官方页面](https://www.mastercard.com/global/en/business/artificial-intelligence/mastercard-agent-pay.html) (Content was rephrased for compliance with licensing restrictions)
来源：[Mastercard Agentic Token Framework](https://www.mastercard.com/us/en/news-and-trends/stories/2025/agentic-commerce-framework.html) (Content was rephrased for compliance with licensing restrictions)
来源：[Tenzro: Payments with Mastercard Agent Pay](https://www.tenzro.com/tutorials/payments-with-mastercard-agent-pay) (Content was rephrased for compliance with licensing restrictions)
```

### 6.5 费用明细

```text
Mastercard Agent Pay 的费用结构（和普通卡交易类似）：

  场景：Agent 帮用户购买 $49.99 的商品

  费用分解（商家承担）：
  ├── 交换费（Interchange）：~1.5%-2.1%（取决于卡类型和 MCC）
  │   → 消费信用卡：~1.65% + $0.10
  │   → 商务信用卡：~2.10% + $0.10
  ├── 卡组织费（Mastercard Assessment）：~0.13%-0.14%
  ├── 收单行加价（Acquirer Markup）：~0.2%-1.0%
  └── 商家总费率：~1.5%-3.5%

  具体到 $49.99 的交易：
  ├── 低端（消费借记卡）：$49.99 × 1.5% = $0.75
  ├── 中端（消费信用卡）：$49.99 × 2.5% = $1.25
  ├── 高端（商务信用卡）：$49.99 × 3.5% = $1.75
  └── 商家实收：$48.24 - $49.24

  Agentic Token 额外费用：
  ├── KYA 验证费：目前 Mastercard 未公开单独收费
  ├── Token 签发费：包含在标准 Token 服务费中
  └── 预计不会显著增加商家成本（Mastercard 的策略是向后兼容）

  对比 ACP/Stripe：
  ├── Mastercard Agent Pay：~1.5%-3.5%（取决于卡类型）
  ├── ACP/Stripe：2.9% + $0.30（固定费率）
  └── 对于 $50+ 的交易，Mastercard 可能更便宜（没有 $0.30 固定费用）

来源：[Mastercard Interchange Rates](https://merchantcostconsulting.com/lower-credit-card-processing-fees/mastercard-interchange-rates/) (Content was rephrased for compliance with licensing restrictions)
```


---

## 七、Stripe Issuing（虚拟卡方案）：完整生命周期

### 7.1 正常支付流程

Stripe Issuing 的思路和前面的协议不同：不是定义新协议，而是给 Agent 发一张虚拟信用卡，让 Agent 像人一样刷卡购物。

```text
平台/企业                Agent                  Stripe Issuing           商家              卡网络
  │                       │                        │                      │                 │
  │  1. 创建 Cardholder   │                        │                      │                 │
  │     (Agent 的身份)     │                        │                      │                 │
  ├──────────────────────────────────────────────>│                      │                 │
  │                       │                        │                      │                 │
  │  2. 为 Agent 创建虚拟卡 │                       │                      │                 │
  │     设置限额和控制规则   │                       │                      │                 │
  │     { spending_limit: $500,                    │                      │                 │
  │       allowed_mccs: [5411, 5812],              │                      │                 │
  │       cancel_after: { payment_count: 1 } }     │                      │                 │
  ├──────────────────────────────────────────────>│                      │                 │
  │                       │                        │                      │                 │
  │  3. 返回虚拟卡信息     │                        │                      │                 │
  │     { card_number, exp, cvc }                  │                      │                 │
  │<──────────────────────────────────────────────┤                      │                 │
  │                       │                        │                      │                 │
  │  4. 将卡信息交给 Agent │                        │                      │                 │
  ├──────────────────────>│                        │                      │                 │
  │                       │                        │                      │                 │
  │                       │  5. Agent 在商家网站下单 │                      │                 │
  │                       │     填入虚拟卡信息       │                      │                 │
  │                       ├───────────────────────────────────────────────>│                │
  │                       │                        │                      │                 │
  │                       │                        │  6. 商家发起授权请求   │                 │
  │                       │                        │<─────────────────────┤                 │
  │                       │                        │                      │                 │
  │                       │                        │  7. Stripe 实时检查：  │                 │
  │                       │                        │     - 限额             │                │
  │                       │                        │     - MCC 限制         │                │
  │                       │                        │     - 地理限制         │                 │
  │                       │                        │     - Webhook 审批     │                │
  │                       │                        │                      │                 │
  │  ← 8. Webhook: issuing_authorization.request → │                      │                │
  │     平台可实时批准/拒绝                          │                      │                │
  │                       │                        │                      │                 │
  │                       │                        │  9. 授权通过           │                │
  │                       │                        ├─────────────────────>│                 │
  │                       │                        │                      │                 │
  │                       │  10. 支付成功            │                      │                │
  │                       │<──────────────────────────────────────────────┤                 │
  │                       │                        │                      │                 │
  │                       │                        │  11. 如果是一次性卡：  │                 │
  │                       │                        │      自动取消卡        │                │

整个过程耗时：~2-10s（和普通网购刷卡一样）
结算到 Stripe Issuing 余额：T+2
```

### 7.2 错误处理

```text
Stripe Issuing 的错误场景：

错误 1：授权被 Webhook 拒绝
  触发时机：平台的 Webhook 处理逻辑决定拒绝这笔交易
  原因：超出任务预算、商家不在白名单、异常交易模式
  处理：
    → Stripe 自动拒绝授权
    → Agent 收到支付失败
    → 平台记录拒绝原因
  资金风险：无（授权被拒 = 没有扣款）

错误 2：Webhook 超时
  触发时机：平台的 Webhook 端点响应超时（Stripe 要求 2s 内响应）
  处理：
    → Stripe 按默认策略处理（通常是拒绝）
    → 可配置超时时的默认行为（批准或拒绝）
  建议：Webhook 处理逻辑要极简，避免超时

错误 3：虚拟卡信息泄露
  触发时机：Agent 将卡信息传给了不可信的商家，或卡信息被中间人截获
  风险：卡被盗刷
  处理：
    → 一次性卡：用完自动失效，风险窗口极小
    → 限额控制：即使被盗，损失上限 = 卡的限额
    → 实时 Webhook：可以在盗刷发生时立即拒绝
    → 立即取消卡：API 调用一次即可

错误 4：商家重复扣款
  触发时机：商家系统 bug 导致同一笔订单扣款两次
  处理：
    → 一次性卡：第二次扣款自动被拒（卡已取消）
    → 限额卡：如果第二次超出限额也会被拒
    → 如果两次都在限额内 → 需要发起争议

错误 5：Agent 超出预算
  触发时机：Agent 找到的商品价格超出虚拟卡限额
  处理：
    → 授权自动被拒
    → Agent 需要通知平台/用户调整预算
    → 或者 Agent 寻找更便宜的替代品

错误 6：高频创建虚拟卡（规模化问题）
  触发时机：大量 Agent 并发创建虚拟卡
  风险：
    → Stripe API 速率限制
    → 卡网络的 BIN 范围耗尽
    → 合规审查触发
  处理：
    → 使用卡池（预创建一批卡，按需分配）
    → 但卡池模式增加了管理复杂度
    → 这是虚拟卡方案在高频场景下的核心瓶颈

来源：[ATXP: Why Per-Task Virtual Cards Don't Scale](https://atxp.ai/blog/virtual-cards-dont-scale-agent-payments) (Content was rephrased for compliance with licensing restrictions)
```

### 7.3 退款机制

```text
Stripe Issuing 的退款/争议流程：

作为发卡方（Issuer），Stripe Issuing 的争议流程和普通信用卡持卡人发起争议类似，
但角色反转了——你的平台是"持卡人"，商家是"被争议方"。

争议发起流程：
  1. 发现问题（欺诈、未收到商品、商品不符等）
  2. 在 Stripe Dashboard 或通过 API 创建争议
  3. 选择争议原因：
     → Fraudulent（欺诈）：Agent 未授权的交易
     → Not Received（未收到）：付了钱但没收到商品/服务
     → Duplicate（重复扣款）：同一笔交易被扣了两次
     → Merchandise Not As Described（商品不符）
     → Canceled（已取消但仍被扣款）
     → Other（其他）
  4. 提交证据（解释、截图、通信记录等）
  5. 争议提交后不可修改，不可追加证据

争议处理时间线：
  ├── 创建争议：交易后 110 天内（Visa/Mastercard 规则）
  ├── 提交争议：创建后尽快提交
  ├── 商家响应：≤30 天
  ├── 如果商家反驳：Stripe 代表你回应，≤30 天
  ├── 如果进入仲裁：卡网络最终裁决，≤30 天
  └── 总时长：30-90 天

争议结果：
  ├── Won（胜诉）：资金退回 Issuing 余额
  ├── Lost（败诉）：不退款
  └── Expired（过期）：超过 110 天未提交

Agent 场景下的特殊考虑：
  → 一次性卡大幅减少了欺诈争议的需求（卡用完即废）
  → 实时 Webhook 审批减少了"未授权交易"的可能性
  → 但"未收到商品"和"商品不符"的争议仍然会发生
  → 平台需要保留 Agent 的购买决策日志作为争议证据

来源：[Stripe Issuing Disputes 文档](https://docs.stripe.com/issuing/purchases/disputes) (Content was rephrased for compliance with licensing restrictions)
```

### 7.4 费用明细

```text
Stripe Issuing 的费用结构：

  基础费用（平台/企业承担）：
  ├── 虚拟卡创建费：$0（Stripe 不收发卡费）
  ├── 每笔交易费：$0（Stripe 不收交易手续费）
  │   → 注意：这是 Issuing 端的费用，商家端仍然要付收单手续费
  ├── 月费/年费：$0（无固定费用）
  └── 争议费：$0（Stripe Issuing 不收争议处理费）

  但有隐性成本：
  ├── 资金预充值：需要在 Issuing 余额中预存资金
  │   → 这笔资金的机会成本（不能用于其他投资）
  ├── 跨币种交易：Stripe 收取 ~1% 的汇率加价
  ├── 合规成本：KYC/KYB 审核、反洗钱监控
  └── 开发成本：Webhook 集成、卡管理逻辑

  场景对比：Agent 购买 $49.99 的商品

  Stripe Issuing 方式：
  ├── 发卡费：$0
  ├── 交易费（Issuing 端）：$0
  ├── 商家端手续费：商家承担（和平台无关）
  └── 平台总成本：$0（但需要预存资金）

  ACP/Stripe 方式：
  ├── 手续费：$1.75（商家承担）
  └── 平台总成本：$0（商家承担手续费）

  关键区别：
  ├── Stripe Issuing：平台是"持卡人"，商家是"收款方"
  │   → 平台不付手续费，但需要预存资金
  │   → 平台有完整的交易控制权
  ├── ACP：商家是"收款方"，用户是"付款方"
  │   → 商家付手续费
  │   → Agent 只是中间协调者

  Stripe Issuing 的经济优势：
  ├── 适合企业采购场景（企业给 Agent 发卡，Agent 代为采购）
  ├── 适合需要精细控制的场景（限额、限商家、限次数）
  └── 不适合 C2B 场景（消费者不会用 Stripe Issuing）

来源：[Stripe Issuing for Agents 文档](https://docs.stripe.com/issuing/agents) (Content was rephrased for compliance with licensing restrictions)
来源：[Crossmint: Agent Card Payments Compared](https://www.crossmint.com/learn/agent-card-payments-compared) (Content was rephrased for compliance with licensing restrictions)
```


---

## 八、AP2 协议（Google）：完整生命周期

### 8.1 正常支付流程

AP2 的核心不是"怎么付钱"，而是"怎么证明 Agent 有权付钱"。它通过三层 Mandate（授权合约）建立从用户意图到最终支付的可验证信任链。

```text
用户              用户 Agent (UA)        商家端点 (ME)        凭证提供方 (CP)      支付网络
  │                   │                     │                    │                  │
  │  ═══ 阶段一：Intent Mandate（意图授权）═══                    │                  │
  │                   │                     │                    │                  │
  │  1. "帮我找一双    │                     │                    │                  │
  │     $100 以内的    │                     │                    │                  │
  │     跑步鞋"        │                     │                    │                  │
  ├──────────────────>│                     │                    │                  │
  │                   │                     │                    │                  │
  │  2. 构造 Intent Mandate                 │                    │                  │
  │     {                                   │                    │                  │
  │       type: "IntentMandate",            │                    │                  │
  │       constraints: {                    │                    │                  │
  │         category: "running_shoes",      │                    │                  │
  │         max_price: 100.00,              │                    │                  │
  │         currency: "USD"                 │                    │                  │
  │       },                                │                    │                  │
  │       user_signature: ECDSA(...)        │                    │                  │
  │     }                                   │                    │                  │
  │                   │                     │                    │                  │
  │  3. 用户签名确认   │                     │                    │                  │
  │     (密码学签名)   │                     │                    │                  │
  │<──────────────────┤                     │                    │                  │
  │  ✓ 签名           │                     │                    │                  │
  ├──────────────────>│                     │                    │                  │
  │                   │                     │                    │                  │
  │  ═══ 阶段二：Agent 搜索和比价 ═══        │                    │                  │
  │                   │                     │                    │                  │
  │                   │  4. 搜索商品         │                    │                  │
  │                   ├────────────────────>│                    │                  │
  │                   │  5. 返回商品列表     │                    │                  │
  │                   │<────────────────────┤                    │                  │
  │                   │                     │                    │                  │
  │  ═══ 阶段三：Cart Mandate（购物车授权）═══                    │                  │
  │                   │                     │                    │                  │
  │                   │  6. 选定商品后，构造 Cart Mandate          │                  │
  │                   │     {                │                    │                  │
  │                   │       type: "CartMandate",               │                  │
  │                   │       items: [{ name: "Nike Air", price: 89.99 }],          │
  │                   │       merchant: "nike.com",              │                  │
  │                   │       total: 89.99,  │                    │                  │
  │                   │       intent_ref: <IntentMandate hash>,  │                  │
  │                   │       agent_signature: ECDSA(...)        │                  │
  │                   │     }                │                    │                  │
  │                   │                     │                    │                  │
  │  7. 展示购物车     │                     │                    │                  │
  │     请求用户确认   │                     │                    │                  │
  │<──────────────────┤                     │                    │                  │
  │                   │                     │                    │                  │
  │  8. 用户签名确认   │                     │                    │                  │
  │     Cart Mandate  │                     │                    │                  │
  ├──────────────────>│                     │                    │                  │
  │                   │                     │                    │                  │
  │  ═══ 阶段四：Payment Mandate（支付授权）═══                   │                  │
  │                   │                     │                    │                  │
  │                   │  9. 向凭证提供方请求支付凭证               │                  │
  │                   │     附带 Cart Mandate │                   │                  │
  │                   ├─────────────────────────────────────────>│                  │
  │                   │                     │                    │                  │
  │                   │                     │  10. CP 验证 Mandate 链               │
  │                   │                     │      签发 Payment Mandate             │
  │                   │                     │      {                                │
  │                   │                     │        type: "PaymentMandate",        │
  │                   │                     │        cart_ref: <CartMandate hash>,  │
  │                   │                     │        payment_token: "...",          │
  │                   │                     │        cp_signature: ECDSA(...)       │
  │                   │                     │      }                                │
  │                   │                     │<───────────────────┤                  │
  │                   │                     │                    │                  │
  │                   │  11. 提交支付        │                    │                  │
  │                   │      (Payment Mandate + 支付凭证)         │                  │
  │                   ├────────────────────>│                    │                  │
  │                   │                     │                    │                  │
  │                   │                     │  12. 商家验证 Mandate 链              │
  │                   │                     │      发起支付请求   │                  │
  │                   │                     ├──────────────────────────────────────>│
  │                   │                     │                    │                  │
  │                   │                     │  13. 支付网络处理   │                  │
  │                   │                     │      验证 Payment Mandate             │
  │                   │                     │<──────────────────────────────────────┤
  │                   │                     │                    │                  │
  │                   │  14. 支付成功 + 收据 │                    │                  │
  │                   │<────────────────────┤                    │                  │
  │                   │                     │                    │                  │
  │  15. "购买成功！"  │                     │                    │                  │
  │<──────────────────┤                     │                    │                  │

信任链：Intent Mandate → Cart Mandate → Payment Mandate
每一层都有密码学签名，形成不可篡改的授权证据链
```

**阶段四详解：凭证提供方（CP）的角色和 Payment Mandate**

```text
阶段一到三完成后，Agent 手里有了 Intent Mandate 和 Cart Mandate，
但 Agent 没有钱——它只有两份"授权证明"，没有"支付能力"。

阶段四就是把"授权证明"变成"支付能力"。

凭证提供方（CP）是谁？
  → 就是用户的"钱在哪里"的那个机构
  → 如果用户用信用卡付款 → CP 是发卡银行（如 Chase、招商银行）
  → 如果用户用数字钱包 → CP 是钱包提供商（如 Google Pay、Apple Pay）
  → 如果用户用稳定币 → CP 是钱包服务（如 Coinbase）

类比：
  你写了一张授权书让助理去买东西（Cart Mandate）
  → 助理拿授权书去银行（CP）
  → 银行验证授权书是你签的 ✓
  → 银行确认你账户有钱 ✓
  → 银行给助理开了一张支票（Payment Mandate + payment_token）
  → 助理拿支票去商家付款

CP 在步骤 10 中做了三件事：

  第一件：验证 Mandate 链的完整性
    → Cart Mandate 里有 intent_ref（指向 Intent Mandate 的哈希）
    → 验证：Intent Mandate 的签名是用户的吗？✓
    → 验证：Cart Mandate 的金额 $89.99 ≤ Intent 的限额 $100？✓
    → 验证：商品类别符合 Intent 的约束？✓
    → 验证：Cart Mandate 有用户的签名确认？✓
    → 全部通过 → 授权链完整有效

  第二件：检查用户的支付能力
    → 用户的信用卡额度够不够？
    → 用户的账户是否正常？
    → 风控检查通过？

  第三件：签发 Payment Mandate
    → CP 用自己的私钥签名
    → 生成 payment_token（类似一次性支票，商家拿它可以向支付网络请求扣款）
    → payment_token 是限额的、限商家的、有时效的

为什么需要 CP 这个角色？
  → Agent 不持有任何资金（它是软件程序，没有银行账户）
  → 资金在用户那里，但用户不在现场
  → 需要一个"中间人"来验证授权、确认资金、签发凭证
  → 这和 AgentToken 的设计理念一致：Agent 不碰真实资金，只拿受限凭证

AgentToken 和 AP2 的关系：
  → 如果 AgentToken 未来对接 AP2 协议，AgentToken 的角色就是凭证提供方（CP）
  → Agent 拿着 Mandate 链来找 AgentToken
  → AgentToken 验证 Mandate 链后签发 Token（VCN / NetworkToken / X402）
  → Agent 拿着 Token 去付款
  → 这让 AP2 的授权框架和 AgentToken 的凭证发放能力完美互补
```

### 8.2 两种交易模式

```text
模式 A：实时购买（Human-Present）
  → 用户全程在线
  → 每一步都需要用户确认/签名
  → Intent Mandate → 用户签名 → Cart Mandate → 用户签名 → 支付
  → 适合高价值交易、首次购买

模式 B：委托购买（Human-Not-Present / Delegated）
  → 用户预先签署 Intent Mandate，设定约束条件
  → Agent 在约束范围内自主行动
  → 不需要用户逐步确认
  → 适合：
    → "每周帮我买一次咖啡豆，预算 $30 以内"
    → "监控这个商品，降到 $50 以下就买"
  → 风险更高，但 Mandate 的约束条件提供了安全边界
```

### 8.3 错误处理

```text
AP2 的错误场景：

错误 1：Intent Mandate 签名验证失败
  触发时机：用户签名无效或被篡改
  处理：
    → 凭证提供方拒绝签发支付凭证
    → Agent 需要重新请求用户签名
  资金风险：无（还没到支付环节）

错误 2：Cart Mandate 违反 Intent Mandate 约束
  触发时机：Agent 选的商品超出了 Intent Mandate 的约束
  例如：Intent 说"$100 以内"，Cart 里的商品 $120
  处理：
    → 凭证提供方验证时发现不匹配 → 拒绝
    → Agent 需要重新选择符合约束的商品
  这是 AP2 的核心安全机制：Mandate 链的一致性验证

错误 3：凭证提供方不可用
  触发时机：数字钱包或银行的 API 宕机
  处理：
    → Agent 无法获取支付凭证 → 无法完成支付
    → 等待恢复后重试
    → Mandate 本身不过期（除非设置了有效期）

错误 4：支付网络拒绝 Payment Mandate
  触发时机：支付网络不认识 AP2 的 Mandate 格式
  处理：
    → 这是 AP2 当前最大的落地挑战
    → 需要支付网络（Visa、Mastercard 等）升级支持
    → 目前 Mastercard 已加入 AP2 联盟，正在适配

错误 5：委托模式下 Agent 越权
  触发时机：Agent 在 Intent Mandate 约束范围内行动，但用户事后认为不合理
  例如：Intent 说"买跑步鞋 $100 以内"，Agent 买了一双 $99 的但用户不喜欢
  处理：
    → 从 Mandate 角度看，Agent 没有越权（$99 < $100）
    → 但用户可能不满意
    → 这不是协议层面的错误，而是"Agent 决策质量"的问题
    → 退款需要走底层支付方式的退款流程

错误 6：Mandate 链断裂
  触发时机：中间某个 Mandate 丢失或损坏
  处理：
    → 无法验证完整的授权链 → 支付被拒
    → 需要从断裂点重新构建 Mandate
    → 所有 Mandate 应该持久化存储（不能只放内存）
```

### 8.4 退款机制

```text
AP2 的退款取决于底层支付方式，但 Mandate 提供了额外的追溯能力：

AP2 本身不处理退款（它是授权层，不是支付层）。
退款走底层支付方式的流程：
  → 如果底层是卡支付 → 走卡组织争议流程（同 Mastercard Agent Pay）
  → 如果底层是 x402 → 链上不可逆（同 x402 退款机制）
  → 如果底层是银行转账 → 走银行的退款流程

AP2 Mandate 在退款中的价值：

  1. 争议举证：
     → Intent Mandate 证明"用户确实授权了这类购买"
     → Cart Mandate 证明"Agent 确实选了这些商品"
     → Payment Mandate 证明"支付确实经过了授权"
     → 这些密码学签名的记录比传统的"交易记录"更有证明力

  2. 责任划分：
     → 如果 Agent 在 Mandate 约束内行动 → Agent 开发者无责
     → 如果 Agent 超出 Mandate 约束 → Agent 开发者有责
     → 如果 Mandate 本身有漏洞 → 需要看谁设计的约束条件
     → 这为未来的"Agent 责任法"提供了技术基础

  3. 可追溯性：
     → 每个 Mandate 都有哈希链接到前一个 Mandate
     → 形成完整的决策审计链
     → 监管机构可以追溯任何一笔交易的完整授权路径

来源：[Google AP2 Protocol](https://curateclick.com/blog/ap2-protocol) (Content was rephrased for compliance with licensing restrictions)
来源：[Briqpay: AP2 Explained](https://briqpay.com/blog/Agents-to-Payments-AP2) (Content was rephrased for compliance with licensing restrictions)
来源：[PayPal: Agent Payments Protocol](https://developer.paypal.com/community/blog/PayPal-Agent-Payments-Protocol/) (Content was rephrased for compliance with licensing restrictions)
```

### 8.5 费用明细

```text
AP2 本身不收费（它是开放协议），费用完全取决于底层支付方式：

  场景 1：AP2 + 卡支付（Mastercard）
  ├── AP2 协议费：$0
  ├── 卡网络手续费：1.5%-3.5%（同 Mastercard Agent Pay）
  └── 总费率：1.5%-3.5%

  场景 2：AP2 + x402（A2A x402 扩展）
  ├── AP2 协议费：$0
  ├── x402 Gas 费：~$0.001-0.005
  └── 总费率：趋近 $0

  场景 3：AP2 + 银行转账
  ├── AP2 协议费：$0
  ├── 银行转账费：取决于银行（通常 $0-$0.25）
  └── 总费率：$0-$0.25

  AP2 的额外成本（非手续费）：
  ├── Mandate 签名计算：CPU 成本极低（ECDSA 签名 ~1ms）
  ├── Mandate 存储：需要持久化存储所有 Mandate（审计需要）
  │   → 每个 Mandate ~1-2KB
  │   → 1000 笔交易 ~2MB → 存储成本可忽略
  ├── 凭证提供方集成：开发成本（一次性）
  └── 合规审计：Mandate 链的验证和报告

  AP2 的经济优势：
  ├── 协议本身零成本
  ├── 可以选择最便宜的底层支付方式
  ├── Mandate 的审计能力可能降低争议率 → 间接降低成本
  └── 但需要支付网络支持 → 目前生态还在建设中

来源：[ATXP: Agent Payment Protocols Compared](https://atxp.ai/blog/agent-payment-protocols-compared/) (Content was rephrased for compliance with licensing restrictions)
来源：[Crossmint: Agentic Payments Protocols Compared](https://www.crossmint.com/learn/agentic-payments-protocols-compared) (Content was rephrased for compliance with licensing restrictions)
```


---

## 九、六种协议的综合对比

### 9.1 全生命周期对比

```text
                    x402        MPP         ACP         MC Agent Pay   Stripe Issuing   AP2
                    ────        ───         ───         ────────────   ──────────────   ───
发起支付前准备
  需要钱包？         ✅ 需要     ✅ 需要     ❌ 不需要    ❌ 不需要       ❌ 不需要        ❌ 不需要
  需要 KYC？         ❌ 不需要   ❌ 不需要    ❌ 不需要    ✅ KYA 验证     ✅ KYB 审核      ⚠️ 取决于底层
  需要预存资金？     ✅ USDC     ✅ 预授权    ❌ 不需要    ❌ 不需要       ✅ Issuing 余额  ⚠️ 取决于底层
  Agent 身份验证？   ❌ 无       ❌ 无        ❌ 无        ✅ KYA 4级      ⚠️ Cardholder   ✅ Mandate 签名

支付过程
  交互次数（最少）   2 次        3 次        4+ 次       3+ 次          2 次             6+ 次
  需要用户参与？     ❌ 不需要   ❌ 不需要    ✅ 需要确认  ⚠️ 首次授权    ❌ 不需要        ✅ 签名确认
  支持离线/委托？    ✅ 完全自主 ✅ 会话内自主 ❌ 需要用户  ✅ Recurring    ✅ 完全自主      ✅ Intent 委托

结算
  结算速度           秒级        会话结束时   T+2         T+1 到 T+3     T+2              取决于底层
  结算确定性         ✅ 链上确认 ✅ 链上确认  ⚠️ 可退款   ⚠️ 可争议      ⚠️ 可争议       取决于底层

安全与控制
  限额控制           ❌ 无       ✅ 会话预算  ✅ SPT 限额  ✅ Token 限额   ✅ 精细控制      ✅ Mandate 约束
  商家限制           ❌ 无       ❌ 无        ✅ SPT 限商家 ✅ MCC 限制    ✅ MCC 限制      ✅ Mandate 约束
  实时审批           ❌ 无       ❌ 无        ❌ 无        ❌ 无           ✅ Webhook       ❌ 无
  审计记录           ✅ 链上     ✅ 链上      ✅ Stripe    ✅ 卡网络       ✅ Stripe        ✅ Mandate 链
```

### 9.2 错误恢复能力对比

```text
                    x402        MPP         ACP         MC Agent Pay   Stripe Issuing   AP2
                    ────        ───         ───         ────────────   ──────────────   ───
余额不足             自行检测    会话创建时   SPT 创建时   授权时拒绝     授权时拒绝       取决于底层
网络中断             可能双付    会话保护     SPT 幂等     卡网络幂等     卡网络幂等       Mandate 可重放
服务方宕机           钱可能丢    会话超时释放  SPT 过期     授权未捕获     授权未捕获       无资金风险
支付后未交付         无保护      有限保护     完整保护     完整保护       完整保护         取决于底层
```

### 9.3 退款能力对比

```text
                    x402        MPP         ACP         MC Agent Pay   Stripe Issuing   AP2
                    ────        ───         ───         ────────────   ──────────────   ───
主动退款             ❌ 不可逆   ⚠️ 会话内   ✅ Stripe    ✅ 商家退款    ✅ 商家退款      取决于底层
争议/Chargeback      ❌ 无       ⚠️ 有限     ✅ 卡组织    ✅ 卡组织      ✅ 卡组织        取决于底层
欺诈保护             ❌ 无       ⚠️ 有限     ✅ Reg Z     ✅ 卡组织规则  ✅ 卡组织规则    ✅ Mandate 审计
争议解决时间         N/A         N/A         30-90 天     30-90 天       30-90 天         取决于底层
消费者保护法适用     ❌ 不适用   ❌ 不适用    ✅ 适用      ✅ 适用        ✅ 适用          取决于底层
```

---

## 十、生产环境选型决策树

```text
你的 Agent 需要做什么？
│
├── 调用付费 API / 机器对机器微支付
│   ├── 单次调用频率低（<10 次/任务）
│   │   └── → x402（简单直接，每次独立付款）
│   ├── 单次调用频率高（>10 次/任务）
│   │   └── → MPP（会话模式，Gas 费分摊）
│   └── 需要法币结算？
│       └── → MPP（支持 Stripe SPT 法币结算）
│
├── 帮用户在商家购物（电商场景）
│   ├── 用户全程在线？
│   │   ├── 是 → ACP（标准化结账流程，Stripe 生态）
│   │   └── 否（委托购买）
│   │       ├── 需要企业级审计？
│   │       │   └── → AP2 + Mastercard Agent Pay
│   │       └── 不需要审计？
│   │           └── → Mastercard Agent Pay（Recurring Token）
│   └── 在 Google/Shopify 生态内？
│       └── → 考虑 UCP（Google 的全链路商务协议）
│
├── 企业采购（Agent 代企业采购）
│   ├── 需要精细的支出控制？
│   │   └── → Stripe Issuing（限额、限商家、实时审批）
│   ├── 需要审计和合规？
│   │   └── → AP2 + Stripe Issuing（Mandate 审计 + 支出控制）
│   └── 简单采购？
│       └── → Stripe Issuing（一次性虚拟卡）
│
├── Agent 对 Agent 支付
│   ├── 微支付（<$1）
│   │   └── → x402 或 MPP（卡网络手续费不可行）
│   └── 大额支付（>$1）
│       └── → x402（简单）或 MPP（高频场景更省）
│
└── 混合场景（既要调 API 又要帮用户购物）
    └── → 多协议组合：
        ├── API 调用 → x402 / MPP
        ├── 用户购物 → ACP / Mastercard Agent Pay
        ├── 企业采购 → Stripe Issuing
        └── 授权管理 → AP2（作为上层授权框架）
```

### 10.1 按交易金额选型

```text
交易金额          推荐协议                    原因
─────────        ────────                    ────
$0.001-$0.01     x402                        Gas 费 ~$0.001，卡网络完全不可行
$0.01-$1.00      x402 或 MPP                 Gas 费占比可接受，卡网络 $0.30 固定费太高
$1.00-$10.00     MPP 或 Mastercard Agent Pay  MPP 适合高频，卡网络适合低频
$10.00-$50.00    ACP 或 Mastercard Agent Pay  卡网络手续费占比合理，有退款保护
$50.00-$500.00   ACP                         完整退款保护值得 2.9% 费率
$500.00+         ACP + AP2                   大额交易需要完整的授权审计和退款保护
```

### 10.2 按风险偏好选型

```text
风险偏好          推荐协议                    原因
────────         ────────                    ────
零容忍（企业）    Stripe Issuing + AP2        实时审批 + Mandate 审计 + 卡组织保护
低风险（消费者）  ACP / Mastercard Agent Pay   卡组织争议机制 + 消费者保护法
中等风险（开发者）MPP                         会话保护 + Stripe 基础设施
高风险容忍（微支付）x402                      链上不可逆但单笔损失极小
```

---

## 十一、总结：2026 年 Agent 支付的现实

```text
1. 没有"一个协议统治所有场景"的银弹
   → 每个协议解决不同层次的问题
   → 生产环境大概率需要 2-3 个协议组合使用

2. 协议之间是互补的，不是竞争的
   → AP2 是授权层（谁有权付钱）
   → ACP 是结账层（怎么和商家交互）
   → x402/MPP 是结算层（钱怎么转移）
   → Mastercard Agent Pay / Stripe Issuing 是凭证层（用什么付钱）

3. 退款保护是最被低估的选型因素
   → 微支付场景可以容忍"链上不可逆"
   → 但任何涉及实物商品的交易，退款保护都是刚需
   → 卡网络的争议机制是 50 年积累的基础设施，短期内无法被替代

4. 费用结构决定了协议的适用边界
   → $0.30 的固定费用让卡网络无法处理微支付
   → Gas 费让链上支付在大额交易中缺乏退款保护
   → 这个"费用鸿沟"短期内不会消失

5. 身份层是所有协议的共同缺失
   → x402 不知道 Agent 是谁
   → ACP 不管 Agent 从哪来
   → 只有 Mastercard Agent Pay（KYA）和 AP2（Mandate 签名）在尝试解决身份问题
   → Agent 身份标准化是下一个需要解决的大问题

来源：[ATXP: Every Agent Payment Protocol Compared](https://atxp.ai/blog/agent-payment-protocols-compared/) (Content was rephrased for compliance with licensing restrictions)
来源：[Crossmint: Agentic Payments Protocols Compared](https://www.crossmint.com/learn/agentic-payments-protocols-compared) (Content was rephrased for compliance with licensing restrictions)
来源：[Chainstack: The Agentic Payments Landscape](https://chainstack.com/the-agentic-payments-landscape/) (Content was rephrased for compliance with licensing restrictions)
```