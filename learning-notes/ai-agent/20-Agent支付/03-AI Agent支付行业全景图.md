# AI Agent 支付行业全景图（2025–2026）

> 本文档梳理 AI Agent 支付领域的行业格局、主要玩家、协议标准和发展趋势，帮助你理解 AgentToken 所处的市场环境。建议先阅读 01-支付与Agent支付知识深度详解 打好基础后再看本文。

## 一、为什么 Agent 需要自己的支付体系？

传统支付系统是为人设计的：你打开网页、输入卡号、点击确认。但 AI Agent 不是人：

| 维度 | 人类支付 | Agent 支付 |
|------|---------|-----------|
| 交互方式 | 手动填写表单、点击按钮 | API 调用、程序化请求 |
| 频率 | 一天几笔 | 一天几百到几千笔 |
| 金额 | 通常 > $1 | 可能低至 $0.001（微支付） |
| 授权 | 每笔人工确认 | 需要预设策略自动授权 |
| 身份 | 有身份证、有银行账户 | 没有法律身份，需要代理 |
| 审计 | 看账单就行 | 需要追溯"谁授权了什么意图" |

核心矛盾：Agent 需要支付能力，但不能给它完整的卡号和无限权限。这就是 AgentToken 这类服务存在的意义——在"用户的钱"和"Agent 的行为"之间加一个可控的中间层。

## 二、行业数据速览

根据公开报道和行业分析（截至 2026 年初）：

- Visa 已发放超过 126 亿个 Network Token（来源：[Dwayne Gefferie](https://dwaynegefferie.substack.com/p/future-proof)）
- 稳定币年链上交易量达 $26 万亿
- Mastercard 承诺 2030 年前欧洲电商 100% Token 化
- x402 协议已处理超过 1 亿笔支付（跨链合计）（来源：[rnwy.com](https://rnwy.com/blog/erc-8004-x402-identity-payment-stack)）
- Agentic Economy 预计 2030 年达到 $3–5 万亿规模（来源：[nevermined.ai](https://nevermined.ai/blog/ai-agent-payment-statistics)）

Content was rephrased for compliance with licensing restrictions.

## 三、主要玩家与布局

### 卡组织

| 玩家 | 动作 | 意义 |
|------|------|------|
| Mastercard | 推出 Agent Pay 框架 + Agentic Token | 让现有卡网络直接支持 Agent 交易，Citi、US Bank 持卡人已可使用 |
| Visa | 推出 Visa Intelligent Commerce 平台 + 大规模推进 Network Tokenization | 100+ 合作伙伴接入，30+ 在沙箱测试，2026 年进入主流落地阶段 |

Mastercard 的策略很聪明：不另起炉灶，而是在现有卡网络上加一层 Agent 专用的 Token 机制，商户几乎不需要改造。

来源：[Mastercard agentic commerce](https://www.mastercard.com/global/en/news-and-trends/stories/2025/agentic-commerce-momentum.html) (Content was rephrased for compliance with licensing restrictions)

### 科技巨头

| 玩家 | 协议/产品 | 定位 |
|------|----------|------|
| OpenAI + Stripe | ACP（Agentic Commerce Protocol） | Agent 在商户网站结账 |
| Google + Shopify | UCP（Universal Commerce Protocol） | 从商品发现到履约的全链路 |
| Google | AP2（Agent Payments Protocol） | Agent 间授权与信任 |
| Coinbase | x402 | HTTP 原生的稳定币微支付 |

### 支付基础设施

| 玩家 | 角色 |
|------|------|
| Stripe | ACP 协议制定者 + 支付处理 |
| Adyen | 企业级支付处理，支持 Token 化 |
| Circle | USDC 发行方，x402 生态核心 |
| EVO Payments | AgentToken 笔记中提到的底层支付处理商 |

## 四、四大协议对比


| 协议 | 主导方 | 层级 | 是否需要加密货币 | 开源 | 适用场景 |
|------|--------|------|-----------------|------|---------|
| x402 | Coinbase | HTTP 支付层 | 是（USDC） | 是 | API 微支付、Agent-to-Agent |
| ACP | Stripe + OpenAI | 商户结账层 | 否 | 是（开放规范） | Agent 代用户在商户购物 |
| UCP | Google + Shopify | 全链路商务 | 否 | 部分 | 从搜索到购买到履约 |
| AP2 | Google | 授权信任层 | 否 | 部分 | Agent 身份验证、授权链 |
| MPP | Stripe + Tempo | 会话支付层 | 是（USDC）+ 法币 | 是 | 高频微支付、Agent 工具调用 |

来源：[Agent payment protocols compared](https://atxp.ai/blog/agent-payment-protocols-compared/) (Content was rephrased for compliance with licensing restrictions)

### 各协议详解

#### x402：HTTP 原生支付

最"程序员友好"的协议。工作流程：

```
Agent → 请求 API
         ← 服务器返回 HTTP 402 + 价格（如 0.003 USDC）
Agent → 签名稳定币支付 + 重新请求
         ← 服务器验证支付 → 返回数据
```

优势：
- 无需注册、无需 API Key
- 支持亚美分级微支付
- 完全去中心化

局限：
- 需要加密货币钱包
- 不适合传统商户（他们不接受 USDC）
- 目前主要在 Base 链上

#### ACP：Agent 代购

Stripe 和 OpenAI 的方案，已在 ChatGPT 中运行。流程：

```
用户 → 告诉 Agent "帮我买 XX"
Agent → 通过 ACP 与商户交互
Agent → 展示商品信息给用户确认
用户 → 确认购买
Agent → 通过 Stripe 完成支付
```

优势：
- 利用 Stripe 现有商户网络
- 用户体验好（有确认环节）
- 不需要加密货币

局限：
- 依赖 Stripe 生态
- 不适合高频微支付

#### UCP：全链路商务

Google 的野心最大——不只是支付，而是从"Agent 帮你搜索商品"到"下单、支付、物流跟踪"的全流程。

#### AP2：信任与授权

解决的是"Agent A 怎么证明自己有权代表用户 B 向商户 C 付款"这个信任问题。使用去中心化标识符（DID）和可验证凭证（VC）。

## 五、三种 Agent 支付模型

根据 [ATXP 的分析](https://atxp.ai/blog/agent-payment-models-virtual-cards-iou-crypto)，目前有三种给 Agent 付款能力的架构（Content was rephrased for compliance with licensing restrictions）：

### 1. 虚拟预付卡

给 Agent 发一张有额度限制的虚拟 Visa/Mastercard。

```
用户 → 充值 $100 到虚拟卡
Agent → 用虚拟卡在商户网站购物
余额用完 → 卡自动失效
```

- 适合：SaaS 订阅、在线购物、需要真实卡号的场景
- 不适合：微支付（手续费 1.5%–3.5%，$0.005 的交易手续费比本金还高）
- 规模问题：推荐"一任务一卡"，但日均 1000+ 任务时管理成本很高

AgentToken 的 VCN 就属于这个模型。

### 2. IOU Token（预付余额）

开发者预充值一个账户余额，Agent 每次调用工具时按量扣费。

```
开发者 → 充值 $50 到 IOU 账户
Agent → 调用搜索 API（扣 $0.003）
Agent → 调用图片生成（扣 $0.04）
余额归零 → Agent 停止
```

- 适合：高频工具调用、亚美分微支付
- 不适合：需要真实卡号的商户场景
- 无卡网络依赖，手续费极低

### 3. x402 加密支付

Agent 直接用稳定币按次付费，嵌入在 HTTP 请求中。

- 适合：API-to-API 微支付、去中心化场景
- 不适合：传统商户、不接受加密货币的场景

## 六、AgentToken 在全景图中的位置

AgentToken 的定位是一个"协议无关的令牌中间层"：

```text
                    AI Agent
      (通过 MCP/ACP/UCP 等协议发起支付请求)
                       |
                       v
                 AgentToken 服务
      策略评估 -> 令牌发放 -> 审计日志 -> 风控
      支持多种令牌类型:
        - Network Token (卡组织令牌)
        - One-time VCN (一次性虚拟卡)
        - X402 VC (稳定币凭证)
        - Super-app Token (超级应用令牌)
                       |
                       v
                 底层支付网络
      Visa / Mastercard / 稳定币链 / 超级应用
```

它的差异化价值：
- 不绑定单一协议或支付网络
- 统一接口屏蔽底层复杂性
- 策略引擎提供细粒度控制
- 完整审计链满足合规要求

## 七、趋势判断

1. 卡组织会主导传统商户场景：Mastercard Agent Pay 这类方案对商户改造最小，落地最快
2. x402 会主导 Agent-to-Agent 微支付：HTTP 原生、无需注册、亚美分级，天然适合机器间交易
3. 协议会长期共存：不同场景需要不同协议，"一统天下"不现实
4. 中间层服务有价值：正因为协议碎片化，AgentToken 这类"协议翻译器 + 策略引擎"才有存在空间
5. 合规是硬门槛：无论哪种模型，KYC/KYB/AML 都是绕不过去的，这也是 AgentToken 强调"Token 持有者必须是人"的原因

## 八、2026 年重大进展

> 🔄 更新于 2026-04-21

<!-- version-check: Agent Payment Landscape 2026-04, checked 2026-04-21 -->

### 协议层面

**x402 Foundation 成立**（2026-04-02）：Coinbase 与 Linux Foundation 联合成立 X402 Foundation，将 x402 协议提升为开放治理标准。协议现已支持区块链无关的稳定币和 ERC-20 Token 结算，初始支持 Base 链。截至 2026 年初，x402 已处理超过 1.15 亿笔交易，年化支付量达 $6 亿。来源：[KuCoin News](https://www.kucoin.com/news/flash/coinbase-and-linux-foundation-launch-x402-a-native-http-crypto-payment-standard)

**Agentic.Market 上线**（2026-04-20）：Coinbase x402 团队推出 Agent 服务市场，AI Agent 可以自主发现、比较和购买服务，无需 API Key。来源：[Blockchain News](https://blockchain.news/news/coinbase-x402-agentic-market-ai-agent-marketplace)

**ACP v2026-01-30 重大更新**：引入 Capability Negotiation（Agent 与商户协商支持的功能）、Payment Handlers Framework（Breaking Change，结构化支付处理器替代简单支付方式标识符）、Extensions Framework（可组合扩展机制）。来源：[ACP Changelog](https://agenticcommerce.dev/docs/changelog)

**Stripe MPP + Tempo 主网上线**（2026-03-18）：Stripe 与 Paradigm 孵化的支付专用 L1 区块链 Tempo 正式上线主网，同步发布 Machine Payments Protocol（MPP）开放标准。设计合作伙伴包括 OpenAI、Anthropic、Visa、Mastercard、Deutsche Bank。MPP 让 AI Agent 使用 USDC 在 Tempo 链上完成自主支付，无需人工审批。来源：[Forbes](https://www.forbes.com/sites/ninabambysheva/2026/03/18/paradigm-and-stripe-roll-out-new-payment-standard-for-ai-agents-with-visas-support/)

### 卡组织进展

**Visa Intelligent Commerce Connect**（2026-04-08）：Visa 发布开发者平台，AI Agent 可通过单一集成完成商品发现、目录浏览和支付。支持 Visa 和非 Visa 卡，兼容四大 Agent 协议。试点合作伙伴包括 AWS 和 Highnote，预计 2026 年 6 月 GA。来源：[Visa Newsroom](https://investor.visa.com/news/news-details/2026/Visa-Opens-the-Door-to-AI-Driven-Shopping-for-Businesses-Worldwide/default.aspx)

**Mastercard Agent Suite 全球扩展**（2026-03）：Mastercard 发布 Agent Suite，包含 Agent Pay、Agentic Pay for Developers 等产品。已在拉美（17 家处理商/发卡行参与实际交易）、澳大利亚（首笔认证 Agent 交易）、新加坡/马来西亚完成实际部署。与 Google 合作新协议，与 Microsoft Copilot Checkout 集成。来源：[Mastercard Newsroom](https://www.mastercard.com/us/en/news-and-trends/stories/2026/agentic-commerce-rules-of-the-road.html)

### 更新后的协议对比表

| 协议 | 主导方 | 层级 | 是否需要加密货币 | 开源 | 适用场景 | 成熟度（2026-04） |
|------|--------|------|-----------------|------|---------|------------------|
| x402 | Coinbase + Linux Foundation | HTTP 支付层 | 是（USDC） | 是 | API 微支付、Agent-to-Agent | 高（Foundation 成立） |
| ACP | Stripe + OpenAI | 商户结账层 | 否 | 是（开放规范） | Agent 代用户在商户购物 | 高（v2026-01-30） |
| MPP | Stripe + Tempo | 自主支付层 | 是（USDC） | 是 | 高频微支付、Agent 自主交易 | 中（主网刚上线） |
| UCP | Google + Shopify | 全链路商务 | 否 | 部分 | 从搜索到购买到履约 | 中 |
| AP2 | Google | 授权信任层 | 否 | 部分 | Agent 身份验证、授权链 | 中 |

### Agentic Commerce 成熟度等级

根据 ATXP 的分析，2026 年大多数生产部署处于 Level 2-3：

```
Level 1: 人工审批每笔交易
Level 2: 预设参数内自主执行，异常人工介入  ← 当前主流
Level 3: 策略驱动的自主执行，人工设定策略  ← 当前主流
Level 4: Agent 间协商和交易
Level 5: 完全自主的 Agent 经济
```

来源：[ATXP - Stripe ACP Explained](https://atxp.ai/blog/stripe-acp-explained)

---

> 参考来源：
> - 本仓库相关文档：`02-Agent协议/05-Agent支付协议.md`（四大协议的技术细节）
> - [Agent payment protocols compared - ATXP](https://atxp.ai/blog/agent-payment-protocols-compared/) (Content was rephrased for compliance with licensing restrictions)
> - [Virtual cards, IOU tokens, and crypto - ATXP](https://atxp.ai/blog/agent-payment-models-virtual-cards-iou-crypto) (Content was rephrased for compliance with licensing restrictions)
> - [Mastercard agentic commerce momentum](https://www.mastercard.com/global/en/news-and-trends/stories/2025/agentic-commerce-momentum.html) (Content was rephrased for compliance with licensing restrictions)
> - [x402 protocol architecture - Chainstack](https://chainstack.com/x402-protocol-for-ai-agents/) (Content was rephrased for compliance with licensing restrictions)
> - [AI agent payment statistics - Nevermined](https://nevermined.ai/blog/ai-agent-payment-statistics) (Content was rephrased for compliance with licensing restrictions)
> - [Future Proof - Dwayne Gefferie](https://dwaynegefferie.substack.com/p/future-proof) (Content was rephrased for compliance with licensing restrictions)
