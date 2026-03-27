# AI Agent 概述与发展
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. 什么是 AI Agent

AI Agent 是一个能够感知环境、自主决策并执行动作来完成目标的智能系统。与传统 Chatbot 的核心区别在于：

```
Chatbot：用户提问 → 模型回答（单轮/多轮对话）
AI Agent：用户设定目标 → 规划 → 使用工具 → 执行 → 验证 → 反馈（自主循环）
```

## 2. Agent 核心能力

```
┌─────────────────────────────────────┐
│            AI Agent                  │
├──────────┬──────────┬───────────────┤
│  感知     │  决策     │  执行         │
│ Perception│ Reasoning │ Action        │
├──────────┼──────────┼───────────────┤
│ 用户输入  │ 任务分解  │ 工具调用       │
│ 环境状态  │ 规划推理  │ API 请求       │
│ 工具反馈  │ 工具选择  │ 代码执行       │
│ 记忆检索  │ 反思纠错  │ 文件操作       │
└──────────┴──────────┴───────────────┘
         ↕ 记忆系统（Memory）↕
```

## 3. Agent 范式演进

### 3.1 ReAct（Reasoning + Acting）

```
思考 → 行动 → 观察 → 思考 → 行动 → ... → 最终答案

Thought: 我需要查询用户的订单信息
Action: query_orders(user_id="123")
Observation: [订单列表...]
Thought: 用户有3个订单，最近一个是...
Answer: 您最近的订单是...
```

### 3.2 Plan-and-Execute

```
1. 制定计划（将复杂任务分解为子任务）
2. 逐步执行每个子任务
3. 根据执行结果调整计划
4. 汇总结果
```

### 3.3 Tool Use（Function Calling）

```
用户请求 → LLM 判断需要调用哪些工具 → 调用工具 → 获取结果 → LLM 生成回答
```

## 4. 2025-2026 行业趋势

### 4.1 协议标准化

- MCP（Model Context Protocol）：Anthropic 提出，Agent 连接工具和数据的标准协议
- A2A（Agent-to-Agent）：Google 提出，Agent 间通信协作的标准协议
- ACP（Agent Communication Protocol）：IBM 提出，轻量级 Agent 消息协议

### 4.2 框架成熟

- LangGraph 1.0 GA：图结构工作流编排，生产级 Agent 框架
- CrewAI：角色化多 Agent 协作，44K+ GitHub Stars
- OpenAI Agents SDK：OpenAI 官方 Agent 开发工具包

### 4.3 多 Agent 系统

- 从单 Agent 到多 Agent 协作
- Supervisor / Hierarchical / Swarm 等架构模式
- Agent 间任务委派与交接（Handoff）

### 4.4 Agentic RAG

- RAG 从被动检索到主动决策
- Agent 自主判断何时检索、检索什么、如何验证
- GraphRAG 知识图谱增强

## 5. Agent 分类

| 类型 | 特点 | 典型场景 |
|------|------|---------|
| 对话型 Agent | 多轮对话，上下文理解 | 智能客服、助手 |
| 任务型 Agent | 目标导向，工具调用 | 数据分析、代码生成 |
| 自主型 Agent | 自主规划，持续执行 | 研究助手、自动化运维 |
| 多 Agent 系统 | 多角色协作 | 软件开发团队、内容创作 |
## 🎬 推荐视频资源

- [Andrej Karpathy - Intro to Large Language Models](https://www.youtube.com/watch?v=zjkBMFhNj_g) — 1小时LLM入门概述，前Tesla AI总监讲解
- [Andrew Ng - AI For Everyone](https://www.coursera.org/learn/ai-for-everyone) — 吴恩达非技术角度理解AI全貌（免费）
- [DeepLearning.AI - Agentic AI with Andrew Ng](https://www.deeplearning.ai/courses/agentic-ai/) — Agentic AI全面讲解（免费）
- [IBM Technology - What are AI Agents?](https://www.youtube.com/watch?v=F8NKVhkZZWI) — 5分钟快速理解AI Agent
### 📺 B站（Bilibili）
- [李沐 - 动手学深度学习](https://www.bilibili.com/video/BV1if4y147hS) — 亚马逊首席科学家，中文AI教育天花板
- [跟李沐学AI - GPT/Transformer论文精读](https://space.bilibili.com/1567748478) — 论文精读系列，深入理解大模型

### 🎓 Coursera / edX
- [Andrew Ng - AI For Everyone](https://www.coursera.org/learn/ai-for-everyone) — 非技术角度理解AI（免费旁听）
