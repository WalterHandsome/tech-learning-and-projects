# 支付与 Agent 支付知识深度详解

> 这份文档是最详细的入门读物。如果你是支付行业零基础，建议从这里开始。后续的术语指南（02）可以当字典随时查阅，行业全景图（03）帮你了解市场格局，产品分析（04）深入 AgentToken 的设计。
>
> 阅读顺序：01 打基础 → 02 当字典 → 03 看全局 → 04 看产品

---

## 第一章：一笔信用卡支付是怎么完成的？

在理解 AgentToken 之前，你必须先搞懂一笔最普通的信用卡支付是怎么跑通的。这是整个支付行业的地基。

### 1.1 四方模型：支付世界的基本架构

全球卡支付系统用的是一个叫"四方模型"（Four Party Model）的架构。顾名思义，一笔交易涉及四个角色：

```text
  持卡人（你）  -------- 刷卡/输入卡号 -------->  商户（星巴克）
      |                                              |
      | 你的卡是这家银行发的              商户签约的收单服务商
      |                                              |
      v                                              v
  发卡行（招商银行）  <--- 卡组织网络(Visa/MC) --->  收单机构（如银联商务）
```

> 注：发卡行和收单机构是不同的角色，不一定是同一家银行。发卡行由持卡人决定（你办了哪家银行的卡），收单机构由商户决定（商户和谁签了收单合同）。两者通过卡组织网络连接。

用一个真实场景来走一遍：

**场景：你在星巴克用招行 Visa 信用卡买了一杯 35 元的咖啡。**

1. 你把卡插入/靠近 POS 机（或在线输入卡号）
2. POS 机把交易信息发给星巴克的收单机构（如银联商务）
3. 收单机构通过 Visa 网络把请求转发给你的发卡行（招商银行）
4. 招行检查：卡是否有效？余额/额度够不够？有没有被挂失？是否触发风控？
5. 招行回复：批准（返回一个授权码）或拒绝
6. 批准信息原路返回 → POS 机显示"交易成功"
7. 后续结算：Visa 协调资金从招行转到收单机构，收单机构再结算给星巴克

**整个过程通常在 2-3 秒内完成。**

来源：[Four Corners Model - Cryptomathic](https://www.cryptomathic.com/blog/cardholder-merchant-issuer-acquirer-the-four-corners-model-for-payment-security-and-key-management) (Content was rephrased for compliance with licensing restrictions)

### 1.2 每个角色赚什么钱？

这是理解支付行业商业模式的关键：

| 角色 | 怎么赚钱 | 大概比例 |
|------|---------|---------|
| 卡组织（Visa/MC） | 每笔交易收"网络费"（Assessment Fee） | 约 0.13%–0.15% |
| 发卡行（招行） | 收"交换费"（Interchange Fee），从收单行那里拿 | 约 1.0%–2.5% |
| 收单机构（银联商务等） | 向商户收"手续费"（Merchant Discount Rate），扣除交换费和网络费后剩余的是利润 | 总费率约 1.5%–3.5% |

所以你在星巴克花 35 元，星巴克实际到手大约 33.5–34.5 元，差额就是这条链上各方的"过路费"。

**这就是为什么 AgentToken 文档里说虚拟卡不适合微支付**——如果 Agent 调用一个 API 只花 $0.005（约 3 分钱），光手续费就要 $0.01 以上，手续费比交易本身还贵，完全不划算。

### 1.3 授权、捕获、结算：一笔交易的三个阶段

之前的术语指南里提到了"预授权"，这里展开讲完整的交易生命周期：

**阶段一：授权（Authorization）**

```text
你刷卡 --> 收单行 --> 卡组织 --> 发卡行
                                  |
                      检查余额、风控、反欺诈
                                  |
                      批准，冻结 35 元（但不扣款）
                                  |
发卡行 --> 卡组织 --> 收单行 --> POS 机显示"成功"
```

这时候你的信用卡账单上会显示一笔"待处理"交易。钱被"冻住"了，但还没真正从你账户扣走。

**阶段二：捕获（Capture）**

商户确认要收这笔钱了（通常在当天营业结束时批量处理），向收单行发送"捕获"请求，把之前冻结的金额正式确认为扣款。

**阶段三：结算（Settlement）**

卡组织协调资金流转：发卡行把钱（扣除交换费后）转给收单行，收单行再（扣除自己的费用后）转给商户。通常 T+1 到 T+3 完成。

```text
时间线:
  |-- 第 0 秒:    授权（冻结资金）
  |-- 当天晚上:   捕获（确认扣款）
  |-- 1-3 天后:   结算（资金到商户账户）
```

**AgentToken 中的应用：** 当你创建一个 Token 并设置 $50 的 Spend Limit 时，系统会对你的信用卡做一个 $50 的预授权（Authorization Hold）。Agent 消费时是在这个预授权范围内进行捕获。如果 Agent 只花了 $30，剩余 $20 的冻结会在 Token 关闭时释放。

来源：[Authorization vs Capture - Stax Payments](https://staxpayments.com/blog/authorize-and-capture/) (Content was rephrased for compliance with licensing restrictions)


---

## 第二章：Tokenization 到底在干什么？

这是 AgentToken 名字里"Token"的来源，也是整个支付安全的核心技术。

### 2.1 问题：卡号太危险了

你的信用卡号（PAN）就像你家的钥匙。如果你把钥匙复制了 100 份分给 100 个人，任何一个人丢了钥匙，小偷就能进你家。

在支付世界里也一样：

- 你在淘宝买东西 → 淘宝存了你的卡号
- 你在京东买东西 → 京东存了你的卡号
- 你订了个 SaaS 服务 → 它也存了你的卡号

任何一家被黑客攻破，你的卡号就泄露了。历史上这种事发生过无数次（Target 2013 年泄露 4000 万张卡号、Equifax 2017 年泄露 1.47 亿人信息等）。

### 2.2 解决方案：用"假号"替代"真号"

Tokenization 的思路很简单：**不要把真钥匙给别人，给他们一个只在特定场景下有效的"电子门禁卡"。**

```text
真实卡号(PAN): 4242 4242 4242 4242
                   |
             Tokenization
                   |
                   v
Token:        tok_8x7k_2m9p_4q3r_1w5n

这个 Token:
  [OK] 看起来像卡号（16 位数字格式）
  [OK] 可以用来发起交易
  [NO] 被偷了也没用（只在特定商户/场景有效）
  [NO] 无法反推出真实卡号
```

### 2.3 Gateway Token vs Network Token：两个层级

之前的术语指南提到了这两种，这里用一个比喻讲清楚区别：

**Gateway Token（网关令牌）—— 像公司内部工牌**

```
场景：你通过 Stripe 在某商户网站存了卡。

Stripe 做的事：
1. 收到你的真实卡号 4242...
2. 在 Stripe 自己的系统里生成一个 Token：tok_stripe_abc123
3. 把 Token 给商户，商户存 Token 而不是卡号
4. 下次商户要扣款时，拿 Token 找 Stripe，Stripe 用真实卡号去发起交易

特点：
- 这个 Token 只在 Stripe 体系内有效
- 换一个支付网关（比如 Adyen），这个 Token 就没用了
- 如果你的卡过期换了新卡，商户需要让你重新绑卡
```

**Network Token（网络令牌）—— 像政府发的电子身份证**

```
场景：Visa 为你的卡生成一个 Network Token。

Visa 做的事：
1. 收到你的真实卡号 4242...
2. 在 Visa 的全球网络里生成一个 Token：4000 1234 5678 9010
3. 这个 Token 绑定了特定的商户和设备
4. 每次交易时，Token 附带一个一次性的 Cryptogram（动态密码）
5. 发卡行收到 Token + Cryptogram，验证后用真实卡号完成交易

特点：
- 全网络通用（只要是 Visa 网络都认）
- 卡过期/换卡时，Visa 自动更新 Token 对应的新卡号，商户无感知
- 每次交易有独立的 Cryptogram，即使 Token 被截获也无法重放
- 发卡行更信任 Network Token，所以交易成功率更高（据统计提升 2-5%）
```

**为什么 AgentToken 选择 Network Token？**

因为 AI Agent 的场景需要：
- 跨平台使用（不能绑死在一个网关上）
- 高安全性（Agent 可能在各种环境下运行）
- 自动处理卡更新（Agent 不会像人一样去更新卡信息）

来源：[Network tokenization guide - Akurateco](https://akurateco.com/blog/network-tokenization-guide) (Content was rephrased for compliance with licensing restrictions)

### 2.4 Cryptogram 是什么？为什么重要？

Cryptogram 是 Network Token 的"灵魂伴侣"。每次交易时动态生成，一次性使用。

```
类比：

普通 Token 就像一张门禁卡 —— 偷了就能用。

Network Token + Cryptogram 就像门禁卡 + 实时人脸识别：
  - 门禁卡（Token）：证明你有权限
  - 人脸识别（Cryptogram）：证明是你本人在用，而且是此时此刻在用

即使有人复制了你的门禁卡，没有你的脸也进不去。
即使有人截获了 Cryptogram，下一秒它就过期了。
```

技术上，Cryptogram 是用密钥对交易信息（金额、时间戳、商户等）进行加密签名生成的。发卡行用同样的密钥验证签名，确保交易没有被篡改。

---

## 第三章：虚拟卡是怎么回事？

### 3.1 虚拟卡的本质

虚拟卡不是什么高深技术，它就是一组数字：

```text
+-----------------------------------+
|           虚拟卡                    |
|                                   |
|  卡号:     4000 1234 5678 9010    |
|  有效期:   03/28                  |
|  CVV:      123                    |
|  持卡人:   AGENT USER             |
|                                   |
|  -- 附加限制 --                    |
|  消费上限:  $50.00                |
|  有效期限:  24 小时                |
|  允许商户:  仅航空类(MCC 4511)     |
|  使用次数:  1 次                   |
+-----------------------------------+
```

它和实体信用卡的区别：

| 维度 | 实体信用卡 | 虚拟卡 |
|------|-----------|--------|
| 物理形态 | 塑料卡片 | 只有数字，没有实体 |
| 有效期 | 通常 3-5 年 | 可以设为几小时到几个月 |
| 消费限制 | 整张卡共享信用额度 | 可以单独设定上限 |
| 使用次数 | 无限次 | 可以设为一次性 |
| 商户限制 | 通常无限制 | 可以限定特定商户/类别 |
| 发放速度 | 需要制卡、邮寄 | 秒级生成 |

### 3.2 虚拟卡在 Agent 场景的用法

```
场景：你让 AI Agent 帮你订一张从北京到上海的机票，预算 800 元。

传统做法（危险）：
  你 → 把信用卡号告诉 Agent → Agent 去携程订票
  问题：Agent 拿着你的卡号，理论上可以买任何东西

AgentToken 做法（安全）：
  你 → 告诉 Agent "帮我订机票，预算 800"
  Agent → 向 AgentToken 申请一张虚拟卡
  AgentToken → 检查策略（金额 OK、航空类商户 OK）
           → 发放一张虚拟卡：
              · 上限 800 元
              · 只能在航空类商户使用
              · 24 小时有效
              · 一次性
  Agent → 用这张虚拟卡在携程订票
  订票完成 → 虚拟卡自动作废

即使这张虚拟卡号泄露了：
  ✗ 不能买别的东西（只限航空类）
  ✗ 不能超过 800 元
  ✗ 不能再次使用（一次性）
  ✗ 24 小时后自动失效
```

### 3.3 虚拟卡的局限性

虚拟卡不是万能的，之前的文档提到了几个问题，这里展开：

**问题一：手续费太高，不适合微支付**

```
场景对比：

Agent 帮你订机票（$500）：
  手续费 ≈ $500 × 2.5% = $12.50
  手续费占比：2.5% → 完全可以接受

Agent 调用一个搜索 API（$0.005）：
  手续费 ≈ 最低 $0.10（卡网络有最低收费）
  手续费占比：2000% → 手续费是交易额的 20 倍！

结论：虚拟卡适合 $1 以上的交易，微支付场景需要用 IOU Token 或 x402。
```

**问题二：规模化管理困难**

```
推荐做法是"一任务一卡"（每个任务发一张新虚拟卡）。

如果你的 Agent 一天执行 10 个任务：
  → 发 10 张卡，管理 10 张卡的生命周期 → 没问题

如果你的 Agent 一天执行 1000 个任务：
  → 发 1000 张卡 → 跟踪每张卡的状态 → 关闭用完的卡 → 处理异常
  → 管理成本急剧上升
```

这就是为什么 AgentToken 不只提供虚拟卡，还提供 Network Token 和 X402 VC——不同场景用不同工具。

来源：[Virtual cards for businesses - Stripe](https://stripe.com/en-my/resources/more/what-is-a-virtual-card-number-and-how-can-you-get-one) (Content was rephrased for compliance with licensing restrictions)

---

## 第四章：KYC/KYB 合规到底要做什么？

### 4.1 为什么金融服务必须验证身份？

这不是支付公司想为难你，而是全球法律要求的。核心原因：

**反洗钱（AML）**：犯罪分子通过大量小额交易把"脏钱"变成"干净钱"。如果金融机构不验证客户身份，就会成为洗钱工具。

**反恐融资（CTF）**：防止资金流向恐怖组织。

**制裁合规**：各国政府维护制裁名单（如美国 OFAC 名单），金融机构必须确保不与名单上的人/实体交易。

如果一家支付公司不做 KYC/KYB，后果很严重：

```
轻则：被监管机构罚款（动辄数百万到数十亿美元）
重则：被吊销牌照、高管坐牢
案例：
  - 汇丰银行 2012 年因 AML 违规被罚 $19 亿
  - Wirecard 2020 年因合规问题破产
  - Binance 2023 年因 AML 违规被罚 $43 亿
```

### 4.2 KYC（个人）具体要做什么？

```
KYC 流程（以 AgentToken 个人用户为例）：

第一步：身份验证
  ├── 提交政府签发的身份证件（护照/身份证/驾照）
  ├── 活体检测（自拍照或视频，证明是本人）
  └── 证件真伪验证（OCR 识别 + 数据库比对）

第二步：地址验证
  ├── 提交地址证明（水电费账单/银行对账单/政府信件）
  └── 地址必须与证件上的信息一致或可关联

第三步：风险筛查
  ├── 对照全球制裁名单（OFAC、EU、UN 等）
  ├── 对照政治敏感人物名单（PEP，Politically Exposed Persons）
  └── 对照负面新闻数据库

第四步：风险评级
  ├── 低风险：普通个人，正常通过
  ├── 中风险：需要额外信息或定期复查
  └── 高风险：拒绝开户或需要高级审批

通过后 → 可以绑定支付方式、创建 Member、申请 Token
```

### 4.3 KYB（企业）具体要做什么？

企业验证比个人复杂得多，因为企业可以有复杂的股权结构来隐藏真实控制人。

```
KYB 流程（以 AgentToken 企业用户为例）：

第一步：企业身份验证
  ├── 公司注册证明（营业执照/公司章程）
  ├── 税务登记号
  └── 经营地址证明

第二步：股权结构穿透
  ├── 谁拥有这家公司？（股东名单）
  ├── 如果股东也是公司，继续穿透
  └── 找到最终受益人（UBO，Ultimate Beneficial Owner）
      └── 通常定义为持股 25% 以上的自然人

第三步：UBO 的 KYC
  ├── 对每个 UBO 做个人 KYC（身份证件、地址等）
  └── 这就是为什么 KYB 比 KYC 慢——要验证多个人

第四步：业务尽职调查
  ├── 公司做什么业务？
  ├── 预期交易量和金额？
  ├── 资金来源？
  └── 是否涉及高风险行业？（博彩、加密货币、军火等）

第五步：持续监控
  ├── 定期复查（通常每年一次）
  ├── 股权变更时重新审查
  └── 交易异常时触发复查
```

**AgentToken 中的应用：**
- 个人用户注册 → 走 KYC → 通过后可以添加个人信用卡
- 企业用户注册 → 走 KYB → 通过后可以添加企业账户、管理多个 Member

来源：[KYC vs KYB differences - Zyphe](https://www.zyphe.com/resources/blog/kyc-vs-kyb-differences) (Content was rephrased for compliance with licensing restrictions)


---

## 第五章：PCI DSS、Vault、HSM —— 怎么保护卡号数据？

### 5.1 PCI DSS 是什么？

PCI DSS（Payment Card Industry Data Security Standard）是卡组织联合制定的安全标准。只要你的系统会接触到卡号数据，就必须遵守。

把它想象成"支付行业的消防法规"——你开餐厅必须有灭火器和安全出口，你做支付就必须满足 PCI DSS。

PCI DSS 有 12 大类要求，核心思想是：

```
1. 尽量不碰卡号数据（能不存就不存）
2. 如果必须碰，要加密
3. 如果必须存，要严格限制谁能访问
4. 所有操作要有日志
5. 定期测试和审计
```

合规等级取决于你处理的交易量：

| 等级 | 年交易量 | 要求 |
|------|---------|------|
| Level 1 | > 600 万笔 | 每年由外部审计师现场审计（QSA） |
| Level 2 | 100-600 万笔 | 年度自评问卷 + 季度网络扫描 |
| Level 3 | 2-100 万笔 | 年度自评问卷 |
| Level 4 | < 2 万笔 | 年度自评问卷（简化版） |

### 5.2 Vault：卡号的保险柜

Vault 是一个专门用来存储敏感数据的安全系统。在支付场景中，它的工作方式是：

```
正常系统存卡号（危险）：
  数据库表：
  | user_id | card_number      | expiry | cvv |
  | 001     | 4242424242424242 | 03/28  | 123 |
  
  → 数据库被攻破 = 所有卡号泄露

使用 Vault（安全）：
  业务数据库：
  | user_id | vault_token          |
  | 001     | vlt_a8x7k2m9p4q3r1w5 |
  
  Vault（独立的加密存储）：
  | vault_token          | encrypted_data（加密后的卡号）|
  | vlt_a8x7k2m9p4q3r1w5 | AES256(4242424242424242)    |
  
  → 业务数据库被攻破 = 只拿到无意义的 vault_token
  → Vault 被攻破 = 只拿到加密后的数据，没有密钥也解不开
  → 密钥在哪？在 HSM 里，永远拿不出来
```

### 5.3 HSM：永远拿不出来的钥匙

HSM（Hardware Security Module）是一个专用硬件设备，长得像一个服务器模块。它的核心特性：

```
HSM 的铁律：
  1. 密钥在 HSM 内部生成
  2. 密钥永远不会以明文形式离开 HSM
  3. 所有加密/解密操作都在 HSM 内部完成
  4. 物理防篡改：如果有人试图拆开 HSM，密钥会自动销毁

工作方式：
  应用程序 → "请用密钥 A 加密这段数据" → HSM
  HSM → 在内部用密钥 A 加密 → 返回加密结果
  
  应用程序永远看不到密钥 A 本身，只能使用它的能力。
```

类比：

```
想象一个翻译官坐在一个密封的玻璃房间里：
  - 你可以通过话筒让他翻译文件
  - 他会把翻译结果通过窗口递出来
  - 但你永远不能进入房间
  - 如果有人试图砸碎玻璃，翻译官会立刻销毁所有文件

HSM 就是这个"密封的玻璃房间"，密钥就是"翻译官的知识"。
```

**AgentToken 中的应用：**
- 用户绑定信用卡时，卡号经过 Tokenization 后存入 Vault
- Vault 的加密密钥存在 HSM 中
- 当 Agent 需要用 Token 发起交易时，系统通过 HSM 解密获取真实卡号，完成交易后立即丢弃明文
- 整个过程中，AgentToken 的业务代码从不直接接触真实卡号


---

## 第六章：AI Agent 支付协议详解

之前的全景图文档列了四大协议，这里用具体场景把每个协议讲透。

### 6.1 x402：让 HTTP 请求自带付款功能

**背景故事：**

HTTP 协议在 1991 年设计时，就预留了一个状态码 402 "Payment Required"（需要付款）。但这个状态码沉睡了 30 多年，从来没有被正式使用过——因为当时没有一种方便的方式让程序自动付款。

2025 年，Coinbase 说："现在有稳定币了，我们可以让这个状态码活过来。"于是 x402 协议诞生了。

**完整工作流程：**

```
场景：Agent 想调用一个天气 API，每次查询收费 $0.003。

第一步：Agent 发送普通 HTTP 请求
  GET https://weather-api.com/forecast?city=beijing
  
第二步：服务器返回 HTTP 402（需要付款）
  HTTP/1.1 402 Payment Required
  X-Payment-Amount: 0.003
  X-Payment-Currency: USDC
  X-Payment-Address: 0xABC...（收款钱包地址）
  X-Payment-Network: base（Base 链）

第三步：Agent 看到 402，自动构造支付
  - 用自己的 USDC 钱包签名一笔 0.003 USDC 的转账
  - 把签名后的支付凭证放在请求头里，重新发送请求
  
  GET https://weather-api.com/forecast?city=beijing
  X-Payment-Proof: <签名后的支付凭证>

第四步：服务器验证支付
  - 检查签名是否有效
  - 检查金额是否正确
  - 确认链上转账（或通过 Facilitator 验证）
  
第五步：支付验证通过，返回数据
  HTTP/1.1 200 OK
  {"city": "beijing", "temperature": 28, "weather": "sunny"}
```

**为什么这对 Agent 很友好？**

```
传统 API 付费方式：
  1. 去网站注册账号
  2. 填写信用卡信息
  3. 选择订阅套餐
  4. 获取 API Key
  5. 在代码里配置 API Key
  6. 开始调用
  → 需要人工操作，Agent 做不了

x402 方式：
  1. Agent 有一个 USDC 钱包
  2. 直接调用 API
  3. 收到 402 → 自动付款 → 拿到数据
  → 全程无需人工，Agent 自主完成
```

来源：[x402 protocol for AI agents - Chainstack](https://chainstack.com/x402-protocol-for-ai-agents/) (Content was rephrased for compliance with licensing restrictions)

### 6.2 ACP：Agent 帮你在商户网站买东西

**场景：你让 ChatGPT 帮你买一双运动鞋。**

```
第一步：你告诉 ChatGPT
  "帮我在 Nike 官网买一双 Air Max，黑色，42 码，预算 $150 以内"

第二步：ChatGPT（通过 ACP 协议）与 Nike 网站交互
  - 搜索符合条件的鞋子
  - 找到一双 Air Max 90，黑色，42 码，$129.99

第三步：ChatGPT 把结果展示给你
  "找到了 Nike Air Max 90，黑色 42 码，$129.99。要下单吗？"

第四步：你确认
  "买吧"

第五步：ChatGPT 通过 Stripe 完成支付
  - 使用你之前在 ChatGPT 里绑定的支付方式
  - Stripe 处理实际的扣款

第六步：订单确认
  "已下单，订单号 #NK12345，预计 3-5 天送达。"
```

**ACP 和 AgentToken 的关系：**

ACP 解决的是"Agent 怎么和商户网站交互"（浏览商品、加入购物车、结账）。AgentToken 解决的是"Agent 用什么凭证付款"。两者可以配合使用：Agent 通过 ACP 协议与商户交互，用 AgentToken 发放的虚拟卡完成支付。

### 6.3 UCP：从搜索到收货的全流程

Google 的 UCP 比 ACP 野心更大，它想覆盖整个购物旅程：

```
ACP 覆盖的范围：
  [搜索商品] → [浏览详情] → [加入购物车] → [结账支付]
                                              ^^^^^^^^
                                              ACP 主要在这里

UCP 覆盖的范围：
  [搜索商品] → [比价] → [浏览详情] → [加入购物车] → [结账支付] → [物流跟踪] → [退换货]
  ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
                              UCP 想覆盖全部
```

UCP 的思路是：Agent 不只是帮你付款，而是帮你完成整个购物决策和售后。

### 6.4 AP2：Agent 之间怎么建立信任？

这是最"底层"的协议，解决的是信任问题。

```
问题场景：
  Agent A（你的购物助手）想在 Agent B（Nike 的销售 Agent）那里买鞋。
  
  Agent B 的疑问：
  - Agent A 真的代表一个真实用户吗？
  - 这个用户真的授权了这笔购买吗？
  - Agent A 有足够的支付能力吗？
  - 如果出了问题，谁负责？

AP2 的解决方案：
  使用 DID（去中心化标识符）和 VC（可验证凭证）

  Agent A 出示一组凭证:
  +-------------------------------------+
  | 可验证凭证 (VC)                      |
  |                                     |
  | 持有者: Agent A (DID: did:web:...)  |
  | 代表用户: Alice (已通过 KYC)         |
  | 授权范围: 购买运动鞋                 |
  | 金额上限: $200                      |
  | 有效期: 2026-04-03 ~ 2026-04-04    |
  | 签发者: AgentToken Service          |
  | 签名: <密码学签名>                   |
  +-------------------------------------+

  Agent B 验证这个凭证:
  [OK] 签名有效（确实是 AgentToken 签发的）
  [OK] 未过期
  [OK] 授权范围匹配（运动鞋）
  [OK] 金额在范围内
  --> 信任建立，可以交易
```

**AgentToken 中的 X402 VC 就是这种可验证凭证的一种实现。**


---

## 第七章：AgentToken 的层级模型详解

之前的产品分析文档提到了 User → Member → Token 的三层模型，这里用一个完整的故事讲清楚。

### 7.1 一个完整的使用场景

```
故事背景：
  "极速旅行"是一家旅游科技公司，他们开发了一个 AI 旅行助手，
  可以帮用户自动订机票、酒店、租车。

第一步：公司注册（User 层）
  
  极速旅行的 CTO 张三在 AgentToken 注册了一个企业用户：
  
  $ agent-token-admin users create
  ? Organization name: 极速旅行科技有限公司
  ? Billing email: billing@jisu-travel.com
  ✓ user created
    ID    org_jisu001
    Name  极速旅行科技有限公司
  
  → 走 KYB 流程：提交营业执照、股权结构、UBO 信息
  → 审核通过后，获得 API Key

第二步：添加成员（Member 层）

  公司有两个业务线，各有一个负责人：
  
  成员 A：李四（国内旅行业务负责人）
    → 绑定公司信用卡（额度 10 万/月）
    → 角色：Admin
  
  成员 B：王五（海外旅行业务负责人）
    → 绑定公司另一张信用卡（额度 50 万/月）
    → 角色：Admin

  $ agent-token-admin members add
  ? Select user: 极速旅行科技有限公司
  ? Member email: lisi@jisu-travel.com
  ✓ Member added
    Member ID mem_lisi001
    Pay_ID    pay_evo_xxx
    Role      admin

第三步：AI Agent 请求 Token（Token 层）

  用户小明对旅行助手说："帮我订明天北京到上海的机票，经济舱。"
  
  旅行助手（Agent）→ 调用 AgentToken API：
  
  POST /v1/tokens
  {
    "member_id": "mem_lisi001",     // 李四（国内业务）
    "type": "vcn",                   // 一次性虚拟卡
    "amount": 1500.00,               // 经济舱预算
    "currency": "CNY",
    "policy": {
      "merchant_categories": ["4511"],  // 仅航空公司
      "expires_in": "4h",              // 4 小时有效
      "single_use": true,              // 一次性
      "geography": "CN"                // 仅中国境内
    },
    "intent": "为用户小明订购北京-上海经济舱机票"  // 意图记录
  }

第四步：策略评估

  AgentToken 策略引擎检查：
  ✓ 李四的支付方式有效
  ✓ 1500 元在李四的可用额度内
  ✓ 航空类商户在允许范围内
  ✓ 请求频率正常
  ✓ 风险评分通过
  
  → 对李四的信用卡做 1500 元预授权
  → 发放虚拟卡

第五步：Agent 使用 Token 完成交易

  Agent 拿到虚拟卡信息：
    卡号：4000 8888 1234 5678
    有效期：04/26
    CVV：789
    
  Agent → 在携程/飞猪上用这张虚拟卡订票
  → 交易成功，扣款 980 元
  → 虚拟卡自动关闭（一次性）
  → 预授权中未使用的 520 元自动释放

第六步：审计记录

  AgentToken 自动记录完整审计链:
  
  +---------------------------------------------+
  | 审计记录 #audit_20260403_001                  |
  |                                             |
  | 意图:     为用户小明订购北京-上海经济舱机票    |
  | 请求方:   旅行助手 Agent                     |
  | 授权人:   李四 (mem_lisi001)                 |
  | 组织:     极速旅行科技有限公司 (org_jisu001)  |
  | Token:    一次性 VCN                         |
  | 发放金额: CNY 1,500                          |
  | 实际消费: CNY 980                            |
  | 商户:     携程旅行 (MCC 4511)                |
  | 时间:     2026-04-03 14:32:15 CST           |
  | 状态:     已完成, Token 已关闭               |
  +---------------------------------------------+
```

### 7.2 为什么要分三层？

```
如果只有一层（User 直接发 Token）：
  → 无法区分不同业务线的消费
  → 无法限制不同人的权限
  → 出了问题不知道是谁授权的

如果只有两层（User → Token，没有 Member）：
  → 所有 Token 都绑定在同一个支付方式上
  → 无法实现"国内业务用卡 A，海外业务用卡 B"
  → 合规上无法追溯到具体的授权人

三层模型的好处：
  User：管理层面（谁的公司、谁付费、API 权限）
  Member：责任层面（谁授权的、用谁的钱）
  Token：执行层面（具体的支付凭证、具体的限制）
```

---

## 第八章：策略引擎（Policy Engine）深度解析

策略引擎是 AgentToken 的"大脑"，决定了每个 Token 能做什么、不能做什么。

### 8.1 策略维度详解

| 策略维度 | 说明 | 示例 |
|---------|------|------|
| 金额控制 | 单笔上限、日累计上限、月累计上限 | 单笔 <= $500, 日累计 <= $2000 |
| 时间控制 | Token 有效期、可用时间段 | 24h 有效, 仅工作日 9:00-18:00 |
| 商户控制 | MCC 白名单/黑名单、特定商户 ID | 仅允许 MCC 4511(航空)和 7011(酒店), 禁止 7995(博彩) |
| 地理控制 | 允许/禁止的国家或地区 | 仅允许中国和日本 |
| 频率控制 | 单位时间内的最大交易次数 | 每小时最多 5 笔交易 |
| 使用次数 | 一次性 vs 可重复使用 | single_use = true |
| 货币控制 | 允许的交易货币 | 仅 CNY 和 USD |

### 8.2 策略组合示例

```
场景一：差旅订票 Agent
  {
    "amount_limit": 5000,
    "merchant_categories": ["4511", "7011", "7512"],  // 航空、酒店、租车
    "geography": ["CN", "JP", "US"],
    "expires_in": "72h",
    "single_use": false,        // 可能需要订多个服务
    "max_transactions": 10,     // 最多 10 笔
    "time_window": "weekdays"   // 仅工作日
  }

场景二：订阅管理 Agent
  {
    "amount_limit": 50,
    "merchant_categories": ["5734", "5817"],  // 软件、数字商品
    "single_use": false,
    "frequency": "1/month",     // 每月最多 1 笔（订阅续费）
    "expires_in": "365d"        // 一年有效
  }

场景三：紧急采购 Agent
  {
    "amount_limit": 200,
    "merchant_categories": ["5411", "5912"],  // 超市、药店
    "geography": ["CN"],
    "expires_in": "2h",         // 2 小时内必须完成
    "single_use": true          // 只能买一次
  }
```

### 8.3 策略冲突怎么处理？

当多个策略维度同时生效时，采用"最严格原则"：

```
Member 级别策略：月消费上限 $10,000
Token 请求策略：单笔上限 $500

实际生效：
  - 单笔不超过 $500（Token 级别限制）
  - 所有 Token 累计不超过 $10,000/月（Member 级别限制）
  - 两个限制同时生效，取更严格的那个
```

---

## 第九章：稳定币与加密支付基础

### 9.1 什么是稳定币？

```
普通加密货币（如比特币）：
  今天 1 BTC = $60,000
  明天 1 BTC = $55,000（跌了 8%）
  后天 1 BTC = $65,000（涨了 18%）
  → 价格波动太大，不适合做支付工具

稳定币（如 USDC）：
  今天 1 USDC = $1.00
  明天 1 USDC = $1.00
  后天 1 USDC = $1.00
  → 价格稳定，适合做支付工具

稳定的原因：
  USDC 由 Circle 公司发行，每发行 1 个 USDC，
  Circle 就在银行里存入 $1 的真实美元（或等值国债）作为储备。
  你随时可以把 USDC 换回真实美元。
```

### 9.2 为什么 Agent 支付要用稳定币？

```
传统支付（信用卡）的问题：
  ✗ 需要银行账户（Agent 没有）
  ✗ 需要 KYC（Agent 不是人）
  ✗ 手续费高（1.5-3.5%）
  ✗ 结算慢（T+1 到 T+3）
  ✗ 有最低交易额（不适合微支付）
  ✗ 跨境复杂（汇率、合规）

稳定币支付的优势：
  ✓ 只需要一个钱包地址（程序可以自动创建）
  ✓ 手续费极低（Base 链上 < $0.01）
  ✓ 结算快（几秒到几分钟）
  ✓ 无最低交易额（可以支付 $0.001）
  ✓ 天然跨境（全球通用）
  ✓ 可编程（可以在代码里自动执行支付逻辑）
```

### 9.3 AgentToken 中的 X402 VC

AgentToken 把 x402 协议包装成了一种令牌类型（X402 VC），让它融入统一的令牌管理体系：

```
不用 AgentToken 的 x402：
  Agent 自己管理钱包 → 自己签名支付 → 没有策略控制 → 没有审计

用 AgentToken 的 X402 VC：
  Agent → 向 AgentToken 申请 X402 VC
  AgentToken → 策略评估 → 发放一个有限制的 VC
  VC 内容：
    - 可用金额：$10
    - 有效期：1 小时
    - 用途：调用天气 API
  Agent → 用这个 VC 去调用 x402 API
  → 全程有策略控制、有审计记录
```

---

## 第十章：Webhook 和 API Key 详解

### 10.1 API Key 的工作原理

```
类比：API Key 就像一把特殊的钥匙

你家有一把万能钥匙（你的密码/登录凭证）：
  - 可以开所有的门
  - 丢了很危险

API Key 是一把"功能钥匙"：
  - 只能开特定的门（只能调用 API，不能登录管理后台）
  - 可以设置权限（只读 vs 读写）
  - 可以随时作废（revoke）并换一把新的
  - 可以有多把（不同用途用不同的 Key）
```

AgentToken 的 API Key 设计：

```
Key 格式：sk_test_a1b2c3d4e5f6...
          │  │
          │  └── test = 沙箱环境（不会真实扣款）
          │       live = 生产环境（真金白银）
          │
          └── sk = Secret Key（秘密密钥，不能暴露给前端）

安全规则：
  1. Key 只在创建时显示一次，之后再也看不到
  2. 只能看到 Key 的前缀（如 sk_test_a1b2），用于识别
  3. 如果 Key 泄露，立即 revoke 并创建新的
  4. 不同环境用不同的 Key（开发用 test，上线用 live）
```

### 10.2 Webhook 的工作原理

```
没有 Webhook 的世界（轮询模式）：

  你的服务器每 5 秒问一次 AgentToken：
    "Token cm3abc123 有新交易吗？" → "没有"
    "Token cm3abc123 有新交易吗？" → "没有"
    "Token cm3abc123 有新交易吗？" → "没有"
    "Token cm3abc123 有新交易吗？" → "有！刚消费了 $30"
  
  问题：浪费资源，99% 的请求都是无用的

有 Webhook 的世界（推送模式）：

  你告诉 AgentToken：
    "如果 Token 有任何交易，请通知 https://my-server.com/webhook"
  
  然后你就不用管了。当交易发生时：
  
  AgentToken → POST https://my-server.com/webhook
  {
    "event": "token.transaction.completed",
    "data": {
      "token_id": "cm3abc123",
      "amount": 30.00,
      "merchant": "携程旅行",
      "timestamp": "2026-04-03T14:32:15Z"
    }
  }
  
  你的服务器收到通知 → 处理业务逻辑（如通知用户、更新记录）
```

Webhook 在 AgentToken 中的典型用途：

```
1. 交易通知：Token 被使用时通知
2. 余额告警：Token 余额低于阈值时通知
3. 风险事件：检测到异常交易时通知
4. Token 过期：Token 即将过期时通知
5. 策略拒绝：Agent 的请求被策略拒绝时通知
```

---

## 第十一章：Mastercard Agent Pay 详解

这是目前最接近大规模落地的 Agent 支付方案，值得单独讲。

### 11.1 Mastercard 的思路

```
其他方案的思路：
  "现有支付系统不适合 Agent，我们要建一个全新的系统"
  → 需要商户改造、需要新的基础设施、落地慢

Mastercard 的思路：
  "现有支付系统已经覆盖全球数千万商户了，
   我们只需要在上面加一层 Agent 专用的机制"
  → 商户几乎不需要改造、利用现有基础设施、落地快
```

### 11.2 Agentic Token 是什么？

```
普通 Network Token：
  - 绑定到一个人（持卡人）
  - 绑定到一个设备或商户
  - 人发起交易

Mastercard Agentic Token：
  - 绑定到一个人（持卡人）+ 一个 Agent
  - Agent 代表人发起交易
  - 附带额外的元数据：
    · Agent 的身份标识
    · 用户的授权范围
    · 交易意图描述
  - 发卡行可以根据这些元数据做更精细的风控
```

### 11.3 为什么商户不需要改造？

```
从商户的角度看：

收到一笔普通 Network Token 交易：
  卡号：4000 1234 5678 9010
  Cryptogram：abc123...
  → 正常处理

收到一笔 Agentic Token 交易：
  卡号：4000 1234 5678 9010（看起来一样）
  Cryptogram：def456...
  Agent 元数据：{...}（商户可以忽略）
  → 正常处理（和普通交易一样走卡网络）

区别在哪？
  - 发卡行能看到 Agent 元数据，可以做更精细的风控
  - 商户不需要关心这些，照常收款就行
  - 这就是"向后兼容"的威力
```

来源：[Mastercard agentic commerce framework](https://www.mastercard.com/global/en/news-and-trends/stories/2025/agentic-commerce-momentum.html) (Content was rephrased for compliance with licensing restrictions)

---

## 第十二章：AgentToken 与 Stripe 的类比

如果你还是觉得 AgentToken 的定位很抽象，这个类比可能帮到你。

### 12.1 Stripe 当年解决了什么问题？

```
2010 年之前，如果你想在网站上收款：

  1. 去银行申请商户账号（几周到几个月）
  2. 签一堆合同
  3. 集成复杂的支付网关 API（文档几百页）
  4. 处理 PCI DSS 合规（花费数万到数十万美元）
  5. 自己处理退款、争议、对账...

Stripe 说："开发者不应该操心这些。"

  import stripe
  stripe.api_key = "sk_test_..."
  stripe.PaymentIntent.create(amount=1000, currency="usd")
  
  → 7 行代码搞定收款
  → Stripe 帮你处理合规、风控、对账、退款...
```

### 12.2 AgentToken 想解决什么问题？

```
2026 年，如果你想让 AI Agent 安全地付款：

  1. 对接 Visa Token Service（复杂的 API + 认证流程）
  2. 对接虚拟卡发卡商（又一套 API）
  3. 对接 x402 协议（需要理解加密货币）
  4. 自己建策略引擎（限额、商户限制、时间窗口...）
  5. 自己建审计系统（合规要求）
  6. 自己处理 KYC/KYB...

AgentToken 说："Agent 开发者不应该操心这些。"

  token = agent_token.create(
      member_id="mem_abc123",
      type="vcn",
      amount=50.00,
      policy={"merchant_categories": ["4511"], "single_use": True}
  )
  
  → 几行代码搞定 Agent 支付
  → AgentToken 帮你处理令牌发放、策略控制、合规、审计...
```

**本质上，AgentToken 想成为 AI Agent 支付领域的 Stripe。**

---

> 参考来源汇总：
> - [Four Corners Model - Cryptomathic](https://www.cryptomathic.com/blog/cardholder-merchant-issuer-acquirer-the-four-corners-model-for-payment-security-and-key-management) (Content was rephrased for compliance with licensing restrictions)
> - [Authorization vs Capture - Stax Payments](https://staxpayments.com/blog/authorize-and-capture/) (Content was rephrased for compliance with licensing restrictions)
> - [Network tokenization guide - Akurateco](https://akurateco.com/blog/network-tokenization-guide) (Content was rephrased for compliance with licensing restrictions)
> - [Virtual cards for businesses - Stripe](https://stripe.com/en-my/resources/more/what-is-a-virtual-card-number-and-how-can-you-get-one) (Content was rephrased for compliance with licensing restrictions)
> - [KYC vs KYB differences - Zyphe](https://www.zyphe.com/resources/blog/kyc-vs-kyb-differences) (Content was rephrased for compliance with licensing restrictions)
> - [x402 protocol for AI agents - Chainstack](https://chainstack.com/x402-protocol-for-ai-agents/) (Content was rephrased for compliance with licensing restrictions)
> - [Mastercard agentic commerce framework](https://www.mastercard.com/global/en/news-and-trends/stories/2025/agentic-commerce-momentum.html) (Content was rephrased for compliance with licensing restrictions)
> - [Agent payment protocols compared - ATXP](https://atxp.ai/blog/agent-payment-protocols-compared/) (Content was rephrased for compliance with licensing restrictions)
> - [Transaction lifecycle - PayAtlas](https://payatlas.com/glossary/transaction-lifecycle-3180) (Content was rephrased for compliance with licensing restrictions)
