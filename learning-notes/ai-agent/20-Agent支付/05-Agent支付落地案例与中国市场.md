# Agent 支付落地案例、中国市场与多 Agent 协作支付

> 本文档补充前四篇文档中缺失的三个维度：真实落地案例与用户反馈、中国市场的 Agent 支付生态、以及多 Agent 链式协作支付场景。建议在阅读完 01-04 后再看本文。

---

## 第一章：真实落地案例

### 1.1 ChatGPT Instant Checkout（OpenAI + Stripe）

2025 年 9 月 29 日，OpenAI 和 Stripe 联合上线了 ChatGPT 的 Instant Checkout 功能，这是全球首个大规模 AI Agent 购物体验。

```
实际用户体验流程：

用户: "帮我推荐一款降噪耳机，预算 $100 以内"

ChatGPT:
  → 搜索并对比多个商家的产品
  → 展示推荐结果（含图片、价格、评分）
  → "Sony WH-CH720N，$89.99，4.5 星评价。要购买吗？"

用户: "买吧"

ChatGPT:
  → 在对话界面内弹出 Stripe 结账组件
  → 用户选择支付方式（支持 Link 一键支付、信用卡、Apple Pay 等）
  → 用户确认支付
  → "已下单，订单号 #xxx，预计 3-5 天送达。"

关键特点：
  ✓ 全程不离开 ChatGPT 对话界面
  ✓ Agent 不接触任何支付凭证（Stripe 处理）
  ✓ 商户保持客户关系（Merchant of Record）
  ✓ 支持 Stripe Link 加速结账（保存过支付信息的用户一键完成）
```

目前的局限性：

- 仅限美国用户
- 商户需要接入 Stripe 并支持 ACP 协议
- 用户必须手动确认每笔支付（不支持全自动）
- 退换货仍需跳转到商户网站处理

来源：[Stripe powers Instant Checkout in ChatGPT](https://stripe.com/in/newsroom/news/stripe-openai-instant-checkout) (Content was rephrased for compliance with licensing restrictions)

### 1.2 Mastercard Agent Pay（Citi + US Bank）

2025 年 9 月，Mastercard 宣布 Agent Pay 框架，Citi 和 US Bank 成为首批试点银行。

```
落地时间线：

2025 年 9 月:  Citi 和 US Bank 持卡人率先体验
2025 年 11 月: 全美 Mastercard 持卡人开放
2026 年初:    全球逐步推广

已集成的 Agent 平台：
  - ChatGPT（OpenAI）
  - Microsoft Copilot
  - 更多平台陆续接入中

实际使用场景：
  用户在银行 App 中授权 → "允许 ChatGPT 使用我的 Mastercard"
  → 银行生成 Agentic Token（绑定 Agent ID + 消费限额）
  → Agent 购物时使用 Token 支付
  → 商户只看到 Token，不看到真实卡号
  → Mastercard 网络验证 Token（Agent ID 匹配？限额内？有效期？）
  → 交易完成，用户收到银行 App 推送通知
```

Mastercard 的差异化在于"向后兼容"——全球数千万已接入 Mastercard 的商户无需任何改造，Agent 交易和普通卡交易走同一条通道。发卡行能看到额外的 Agent 元数据做风控，但商户端完全透明。

来源：[Mastercard agentic commerce momentum](https://www.mastercard.com/am/en/news-and-trends/stories/2025/agentic-commerce-momentum.html) (Content was rephrased for compliance with licensing restrictions)

### 1.3 MPP：Machine Payments Protocol（Stripe + Tempo，2026 年 3 月）

这是前四篇文档中没有覆盖的新协议。2026 年 3 月 18 日，Stripe 和 Paradigm 孵化的区块链项目 Tempo 联合推出了 MPP，被称为"OAuth for Money"。

```
MPP 的核心设计：

传统支付（每笔独立交易）：
  Agent → 调用 API 1 → 支付 $0.003
  Agent → 调用 API 2 → 支付 $0.005
  Agent → 调用 API 3 → 支付 $0.002
  → 每笔都要独立签名、验证、结算 → 开销大

MPP（会话模式）：
  Agent → 开启支付会话（预授权 $1.00）
  Agent → 调用 API 1（从会话余额扣 $0.003）
  Agent → 调用 API 2（从会话余额扣 $0.005）
  Agent → 调用 API 3（从会话余额扣 $0.002）
  Agent → 关闭会话（结算实际消费 $0.010，退还 $0.990）
  → 只需一次链上结算 → 效率高

支持的支付方式：
  - 稳定币（USDC，在 Tempo 链上结算）
  - 法币（通过 Stripe 处理）

支持者：Visa、OpenAI、Mastercard、Shopify
```

MPP 和 x402 的区别：x402 是"每次请求独立付款"，MPP 是"先开会话再流式扣款"。MPP 更适合高频微支付场景（如 Agent 在一个任务中连续调用几十个 API）。

来源：[Stripe and Tempo launch Machine Payments Protocol](https://thepaypers.com/payments/news/paradigm-and-stripe-launch-machine-payments-protocol-for-ai-agent-transactions) (Content was rephrased for compliance with licensing restrictions)

### 1.4 协议落地进度汇总（截至 2026 年 4 月）

| 协议 | 发布时间 | 当前状态 | 交易量 |
| --- | --- | --- | --- |
| x402 | 2025 年 5 月 | 已上线，早期阶段 | 累计超 1 亿笔（跨链合计） |
| AP2 | 2025 年 9 月 | 已发布，60+ 合作伙伴 | 未公开 |
| ACP | 2025 年 9 月 | 已上线（ChatGPT Instant Checkout） | 未公开 |
| Mastercard Agent Pay | 2025 年 9 月 | 已上线，全美覆盖，全球推广中 | 未公开 |
| UCP | 2026 年 1 月 | 已发布（Google + Shopify） | 未公开 |
| MPP | 2026 年 3 月 | 已上线（Tempo 主网） | 早期阶段 |

---

## 第二章：中国市场的 Agent 支付生态

中国在 Agent 支付领域的进展远超大多数人的认知。与海外"协议先行、落地在后"的路径不同，中国走的是"超级应用驱动、场景先行"的路线。

### 2.1 支付宝 AI Pay

支付宝是目前全球 Agent 支付落地规模最大的平台，没有之一。

```
关键数据（2026 年 2 月）：
  - 单周交易量突破 1.2 亿笔
  - 注意：这不是浏览量或对话量，而是实际完成的购买交易
  - 2025 年上线，2026 年初爆发式增长

已落地的场景：
  ├── 零售：瑞幸咖啡等连锁品牌的小程序内 Agent 点单
  ├── 即时配送：淘宝即时零售（Agent 帮你下单买菜/日用品）
  ├── 智能硬件：Rokid AR 眼镜通过语音 Agent 完成支付
  ├── AI 原生应用：通义千问 App 内直接调用支付宝完成购买
  └── 更多场景持续扩展中
```

来源：[Alipay AI Pay surpasses 120 million weekly transactions](https://www.theasianbanker.com/press-releases/alipay-ai-pay-surpasses-120-million-weekly-transactions-as-agentic-commerce-expands-in-china) (Content was rephrased for compliance with licensing restrictions)

### 2.2 支付宝 Agentic Commerce Trust Protocol

2026 年 1 月，支付宝发布了"Agentic Commerce Trust Protocol"（Agent 商务信任协议），这是中国首个开放的 Agent 商务技术框架。

```
协议核心设计：

问题：每个 AI 应用要对接每个商户，N×M 的集成复杂度
  AI 应用 A ──→ 商户 1
  AI 应用 A ──→ 商户 2
  AI 应用 B ──→ 商户 1
  AI 应用 B ──→ 商户 2
  → 4 条集成线路

解决方案：通过协议统一接口，降为 N+M
  AI 应用 A ──→ ┌──────────────────┐ ──→ 商户 1
  AI 应用 B ──→ │ Trust Protocol   │ ──→ 商户 2
                └──────────────────┘
  → 每方只需接入协议一次

首批接入方：
  - 通义千问 App（首个采用该协议的平台，2026 年 1 月 15 日）
  - 淘宝即时零售
  - Rokid（AR 眼镜）
  - 大麦（票务）
  - 阿里云百炼平台

协议能力：
  ✓ 商户一次接入，对接所有 AI Agent
  ✓ 支付安全（Agent 不接触用户支付凭证）
  ✓ 跨设备支持（手机、眼镜、智能音箱等）
  ✓ 跨平台支持（不同 AI 应用共享商户接口）
```

来源：[Alipay launches Agentic Commerce Trust Protocol](https://thepaypers.com/payments/news/alipay-rolls-out-the-agentic-commerce-trust-protocol-in-china) (Content was rephrased for compliance with licensing restrictions)

### 2.3 微信支付与小程序生态

微信支付虽然没有像支付宝那样高调发布 Agent 支付协议，但其小程序生态天然适合 Agent 商务：

```
微信的 Agent 支付路径：

现有基础设施：
  - 小程序：轻量级应用，无需下载安装
  - 微信支付：覆盖几乎所有中国商户
  - 公众号/服务号：消息推送和交互

Agent 集成方式：
  AI Agent → 调用小程序（搜索商品、下单）
          → 触发微信支付（用户在微信内确认）
          → 完成交易

优势：
  ✓ 商户生态已经建好（数千万小程序商户）
  ✓ 支付闭环在微信内完成
  ✓ 用户习惯已经养成

与支付宝的差异：
  支付宝：自上而下，发布开放协议，主动推动 Agent 生态
  微信：自下而上，依托小程序生态自然演进
```

### 2.4 数字人民币（e-CNY）与 Agent 支付的结合可能性

数字人民币在 2026 年 1 月 1 日正式从试点转为全面运营，其可编程特性为 Agent 支付提供了独特的基础设施。

```
e-CNY 基本数据（截至 2025 年 11 月）：
  - 累计交易笔数：34.8 亿笔
  - 累计交易金额：16.7 万亿元
  - 个人钱包用户：2.3 亿
  - 企业钱包用户：1900 万

e-CNY 的可编程特性（与 Agent 支付相关）：

1. 智能合约能力
   - 支持条件触发的自动支付
   - 例如："当机票价格低于 800 元时自动购买"
   - Agent 可以设置条件，e-CNY 智能合约自动执行

2. 分层钱包体系
   ┌─────────────────────────────────────────┐
   │ 钱包等级  │ 实名要求  │ 单笔限额  │ 日限额  │
   │ 一类      │ 柜面核验  │ 无限制    │ 无限制  │
   │ 二类      │ 实名认证  │ 5 万元    │ 50 万元 │
   │ 三类      │ 手机号    │ 2000 元   │ 5000 元 │
   │ 四类      │ 无需实名  │ 500 元    │ 1000 元 │
   └─────────────────────────────────────────┘
   
   Agent 场景可以使用低等级钱包（三/四类），
   无需完整 KYC，天然适合小额自动支付。

3. 离线支付能力
   - 支持无网络环境下的 NFC 支付
   - 对 IoT 设备上的 Agent 有价值

4. 与 Agent 支付结合的想象空间
   - Agent 持有四类钱包（小额、无需实名）
   - 用户通过一类/二类钱包向 Agent 钱包充值
   - Agent 在限额内自主消费
   - 智能合约确保资金用途合规
   - 央行可追溯所有交易（监管友好）
```

目前 e-CNY 尚未正式推出 Agent 支付功能，但其技术架构（可编程、分层钱包、智能合约）与 Agent 支付的需求高度契合。这可能是中国在 Agent 支付领域的"杀手锏"——一个由央行背书的、原生支持可编程支付的数字货币。

来源：[China digital yuan enters new era](https://www.kucoin.com/news/flash/china-tightens-crypto-oversight-expands-digital-yuan-in-2026) (Content was rephrased for compliance with licensing restrictions)

### 2.5 中国 vs 海外：Agent 支付路径对比

```
┌──────────────────────────────────────────────────────────┐
│                  中国 vs 海外 Agent 支付路径               │
├──────────────────────────┬───────────────────────────────┤
│         中国              │           海外                │
├──────────────────────────┼───────────────────────────────┤
│ 超级应用驱动              │ 协议标准驱动                   │
│ (支付宝/微信先落地再标准化) │ (先定协议再推落地)             │
├──────────────────────────┼───────────────────────────────┤
│ 移动支付为主              │ 卡支付为主                     │
│ (二维码、小程序)           │ (虚拟卡、Network Token)        │
├──────────────────────────┼───────────────────────────────┤
│ 央行数字货币(e-CNY)       │ 稳定币(USDC)                  │
│ 国家背书、可编程           │ 市场驱动、去中心化             │
├──────────────────────────┼───────────────────────────────┤
│ 场景丰富                  │ 协议完善                       │
│ (外卖、零售、票务、硬件)    │ (ACP/AP2/x402/MPP/UCP)       │
├──────────────────────────┼───────────────────────────────┤
│ 监管明确                  │ 监管滞后                       │
│ (央行主导、牌照制)         │ (各国法律尚未跟上)             │
├──────────────────────────┼───────────────────────────────┤
│ 落地规模大                │ 技术创新多                     │
│ (单周 1.2 亿笔)           │ (协议多样性丰富)               │
└──────────────────────────┴───────────────────────────────┘
```

---

## 第三章：多 Agent 链式协作支付

当前大部分讨论集中在"单个 Agent 代用户付款"，但未来更复杂的场景是多个 Agent 协作完成一个任务，涉及链式支付。

### 3.1 问题场景

```
场景：用户说"帮我规划一次东京 5 日游，预算 1.5 万元"

涉及的 Agent 链：

用户
  └→ 旅行规划 Agent（主 Agent）
       ├→ 机票 Agent → 调用携程 API → 支付机票 ¥3,200
       ├→ 酒店 Agent → 调用 Booking API → 支付酒店 ¥4,500
       ├→ 景点 Agent → 调用大麦 API → 支付门票 ¥800
       ├→ 交通 Agent → 调用 Suica API → 充值交通卡 ¥500
       └→ 餐饮 Agent → 调用 Tabelog API → 预订餐厅 ¥1,200

总计：¥10,200（在 ¥15,000 预算内）

支付链路问题：
  1. 谁来分配预算？（主 Agent 还是各子 Agent 自行决定？）
  2. 子 Agent 的支付凭证从哪来？（每个子 Agent 单独申请 Token？）
  3. 如果机票 Agent 花超了，酒店 Agent 的预算怎么调整？
  4. 如果某个子 Agent 被 prompt injection 攻击，怎么限制损失？
  5. 审计链怎么追溯？（用户 → 主 Agent → 子 Agent → 商户）
```

### 3.2 解决方案：层级 Token 委托模型

```
方案一：主 Agent 统一管理（中心化）

用户 → 授权主 Agent（总预算 ¥15,000）
主 Agent → 为每个子 Agent 申请独立 Token：
  ├── 机票 Token：¥4,000 上限，航空类商户，24h 有效
  ├── 酒店 Token：¥5,000 上限，酒店类商户，48h 有效
  ├── 景点 Token：¥1,500 上限，娱乐类商户，72h 有效
  ├── 交通 Token：¥1,000 上限，交通类商户，5 天有效
  └── 餐饮 Token：¥2,000 上限，餐饮类商户，5 天有效

优点：预算分配清晰，每个子 Agent 权限隔离
缺点：预算分配不灵活（机票便宜了，省下的钱不能自动给酒店）

方案二：动态预算池（弹性分配）

用户 → 授权主 Agent（总预算 ¥15,000）
主 Agent → 维护一个预算池
  ├── 机票 Agent 请求 ¥3,200 → 主 Agent 批准 → 池剩余 ¥11,800
  ├── 酒店 Agent 请求 ¥4,500 → 主 Agent 批准 → 池剩余 ¥7,300
  ├── 景点 Agent 请求 ¥800  → 主 Agent 批准 → 池剩余 ¥6,500
  └── ...

优点：预算动态调整，更灵活
缺点：主 Agent 成为瓶颈和单点故障

方案三：AP2 + 可验证凭证链（去中心化）

用户 → 签发根凭证给主 Agent
  VC_root: {
    holder: "旅行规划 Agent",
    budget: ¥15,000,
    scope: "东京旅行",
    valid: "5 天"
  }

主 Agent → 签发子凭证给各子 Agent
  VC_flight: {
    holder: "机票 Agent",
    parent: VC_root,
    budget: ¥4,000,
    scope: "航空",
    valid: "24h"
  }

商户验证链：
  商户 → 验证 VC_flight 签名 → 追溯到 VC_root → 追溯到用户授权
  → 信任链完整，可审计

优点：去中心化，不依赖主 Agent 在线
缺点：实现复杂，目前没有成熟方案
```

### 3.3 Agent-to-Agent 支付（A2A 微支付）

除了"Agent 代用户付款给商户"，还有一种场景是 Agent 之间互相付费：

```
场景：你的个人助手 Agent 需要调用一个专业的法律咨询 Agent

你的 Agent → 发现法律 Agent（通过 A2A 协议）
你的 Agent → 查询价格：$0.50/次咨询
你的 Agent → 检查预算：OK
你的 Agent → 通过 x402/MPP 支付 $0.50
法律 Agent → 收到支付确认
法律 Agent → 提供法律建议
你的 Agent → 整合建议，回复给你

这里的支付可以用：
  - x402：每次调用独立付款
  - MPP：开启会话，多次调用流式扣款
  - AP2 + VC：带授权凭证的支付
```

### 3.4 多 Agent 支付的核心挑战

```
1. 授权链管理
   用户 → Agent A → Agent B → Agent C
   每一层委托都需要明确的授权范围和限额
   任何一层被攻破，损失应被限制在该层的授权范围内

2. 原子性问题
   "订机票 + 订酒店"应该是原子操作吗？
   如果机票订成功了但酒店没房了，要不要回滚机票？
   传统数据库有事务机制，但跨 Agent 跨商户的"分布式事务"很难实现

3. 结算与对账
   多个 Agent 分别在不同商户消费
   最终需要汇总到一个账单给用户
   不同商户的结算周期不同（T+1 到 T+3）
   需要一个统一的对账层

4. 责任归属
   Agent A 委托 Agent B 买了一个错误的商品
   是 Agent A 的责任（委托方）还是 Agent B 的责任（执行方）？
   还是用户的责任（最终授权人）？
   目前法律上没有明确答案
```

---

> 参考来源：
> - [Stripe powers Instant Checkout in ChatGPT](https://stripe.com/in/newsroom/news/stripe-openai-instant-checkout) (Content was rephrased for compliance with licensing restrictions)
> - [Mastercard agentic commerce momentum](https://www.mastercard.com/am/en/news-and-trends/stories/2025/agentic-commerce-momentum.html) (Content was rephrased for compliance with licensing restrictions)
> - [Stripe and Tempo launch Machine Payments Protocol](https://thepaypers.com/payments/news/paradigm-and-stripe-launch-machine-payments-protocol-for-ai-agent-transactions) (Content was rephrased for compliance with licensing restrictions)
> - [Alipay AI Pay surpasses 120 million weekly transactions](https://www.theasianbanker.com/press-releases/alipay-ai-pay-surpasses-120-million-weekly-transactions-as-agentic-commerce-expands-in-china) (Content was rephrased for compliance with licensing restrictions)
> - [Alipay launches Agentic Commerce Trust Protocol](https://thepaypers.com/payments/news/alipay-rolls-out-the-agentic-commerce-trust-protocol-in-china) (Content was rephrased for compliance with licensing restrictions)
> - [China digital yuan enters new era](https://www.kucoin.com/news/flash/china-tightens-crypto-oversight-expands-digital-yuan-in-2026) (Content was rephrased for compliance with licensing restrictions)
> - [Agentic payments protocols compared - Crossmint](https://www.crossmint.com/learn/agentic-payments-protocols-compared) (Content was rephrased for compliance with licensing restrictions)
> - [A2A with x402 micropayments - arXiv](https://arxiv.org/html/2507.19550v1) (Content was rephrased for compliance with licensing restrictions)
