# 浏览器自动化 Agent 详解
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. 概述

浏览器自动化 Agent 从传统 DOM 脚本演进到视觉驱动的自主 Agent。

```
演进路径：Selenium 脚本 → MCP 工具集成 → 独立 Agent 框架（视觉+自主决策）
```

## 2. Browser-Use — 最推荐，基准最高

开源浏览器自动化框架，WebVoyager 基准测试领先，支持多 LLM 后端。

```python
from browser_use import Agent, Controller
from langchain_openai import ChatOpenAI

# 基本用法
agent = Agent(
    task="去 GitHub Trending，筛选 Python，提取前 5 个项目名称和 Star 数",
    llm=ChatOpenAI(model="gpt-4o"),
    max_actions_per_step=5,
)
result = await agent.run()

# 自定义 Action + Claude 后端
controller = Controller()

@controller.action("保存结果到文件")
def save_to_file(content: str, filename: str):
    with open(filename, "w") as f:
        f.write(content)

agent = Agent(
    task="搜索 AI Agent 框架，对比特点，保存到 report.md",
    llm=ChatAnthropic(model="claude-sonnet-4-20250514"),
    controller=controller,
)
```

## 3. Skyvern — 视觉驱动，适合复杂网站

使用计算机视觉而非 DOM 解析，不怕 UI 变化，能处理 CAPTCHA。

```
工作原理：浏览器截图 → 视觉模型理解页面 → 生成操作指令 → 执行并验证
```

```python
client = skyvern.Skyvern(api_key="your-api-key")
task = client.tasks.create(
    url="https://example.com/apply",
    goal="填写申请表单，姓名 John Doe，邮箱 john@example.com",
)
```

## 4. Agent-Browser — Vercel 出品，轻量 CLI

TypeScript 编写，极简 API，适合轻量级 Agent 场景。

```typescript
import { createBrowser } from "@anthropic-ai/agent-browser";
const browser = await createBrowser();
const page = await browser.newPage();
await page.act("导航到 Hacker News");
const title = await page.extract("提取文章标题");
```

## 5. Agent-S — GUI Agent，超越人类表现

通用计算机使用 Agent，OSWorld 基准测试超越人类，不仅限于浏览器。

```
架构：经验学习 + 自主探索 → 多模态推理 → OS 级控制（鼠标/键盘/窗口）
```

## 6. Page-Agent — 阿里巴巴，网站 AI 原生化

将任何网站变成 AI 原生应用，Agent 直接与网页交互而非通过 API。

## 7. 综合对比表

| 工具 | 方式 | 语言 | 最佳场景 | Stars | 自托管 | 云端 |
|------|------|------|----------|-------|--------|------|
| Browser-Use | DOM+视觉混合 | Python | 通用浏览器自动化 | 60k+ | ✅ | ✅ |
| Skyvern | 纯视觉驱动 | Python | 复杂动态网站 | 20k+ | ✅ | ✅ |
| Agent-Browser | DOM 操作 | TypeScript | 轻量级 Agent | 3k+ | ✅ | ❌ |
| Agent-S | GUI/截图 | Python | 通用计算机操作 | 5k+ | ✅ | ❌ |
| Page-Agent | 网页 AI 化 | TypeScript | 网站 AI 原生化 | 2k+ | ✅ | ❌ |

与已有工具对比（详见 → Computer Use与浏览器Agent.md）：

| 工具 | 类型 | 适用场景 |
|------|------|----------|
| Claude Computer Use | 通用 GUI | 任何桌面应用 |
| Nova Act SDK | 浏览器专用 | 语义化浏览器工作流 |
| Playwright/Puppeteer MCP | MCP 工具 | Agent 调用浏览器 |
| Browserbase / Steel | 云基础设施 | 云端浏览器实例 |

## 8. 选型决策树

```
需要浏览器自动化？
├─ 已有 MCP 环境？ → Playwright MCP（最简集成）
├─ 需要通用计算机操作？ → Claude Computer Use / Agent-S
├─ 目标网站复杂（CAPTCHA/动态）？ → Skyvern
├─ TypeScript 项目？ → Agent-Browser
├─ 需要云端大规模运行？ → Browser-Use + Browserbase
└─ 通用推荐 → Browser-Use（基准最高，生态最好）
```

## 9. 安全注意事项

```
├─ 沙箱隔离：始终在容器中运行浏览器
├─ URL 白名单：限制可访问域名
├─ 凭证管理：使用 Vault，不硬编码
├─ 超时控制：设置最大执行时间
└─ 人工兜底：关键操作（支付/删除）需确认
```
