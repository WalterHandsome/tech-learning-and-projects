# 🚀 Tech Learning & Projects

> 全栈技术学习笔记与 AI Agent 实战项目集合

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](./LICENSE)
[![AI Agent](https://img.shields.io/badge/AI-Agent-orange)](./learning-notes/ai-agent/)
[![Java](https://img.shields.io/badge/Java-17+-red)](./learning-notes/java/)
[![Python](https://img.shields.io/badge/Python-3.12+-green)](./learning-notes/python/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.x-blue)](./learning-notes/frontend/)

---

## 👋 关于这个项目

这是我的个人技术学习与实践仓库，涵盖全栈开发和 AI Agent 领域。包含体系化的学习笔记（90+ 篇 AI Agent 文档）和多个可运行的实战项目。

> 📌 本仓库为私有仓库，如需查看完整代码和笔记内容，请联系我获取访问权限。

## 📊 内容概览

```
📁 learning-notes/          200+ 篇技术笔记
│
├── 🤖 ai-agent/            24 个分类 · 90 篇文档
│   Agent 协议 · 框架对比 · RAG · MCP · 多Agent · 记忆系统
│   Harness Engineering · Voice Agent · Agent 支付 · 云厂商方案
│
├── ☕ java/                 12 个分类
│   Spring 全家桶 · 微服务 · 中间件 · JVM · 设计模式
│
├── 🐍 python/              16 个分类
│   FastAPI · 数据分析 · 机器学习 · 并发 · 爬虫
│
├── 🌐 frontend/            16 个分类
│   React · Vue3 · TypeScript · Node.js · 工程化 · 性能优化
│
├── 🍎 ios/                 11 个分类
│   Swift · SwiftUI · UIKit · 架构模式 · 系统框架
│
├── 🤖 android/             11 个分类
│   Kotlin · Jetpack Compose · 架构模式 · 性能优化
│
└── 🏗️ architecture/        架构设计
    事件驱动架构
```

## 🎯 实战项目

### LangGraph + MCP 智能 Agent

基于 LangGraph 工作流编排 + MCP 工具协议的生产级 Agent 示例。

| 特性 | 说明 |
|------|------|
| 工作流编排 | LangGraph 图结构，条件路由，状态持久化 |
| MCP 工具 | 文件系统、数据库查询等 MCP Server |
| RAG 检索 | ChromaDB 向量存储，混合检索 + Reranker |
| 记忆管理 | LangGraph State + Mem0 长期记忆 |
| 人机协作 | 敏感操作审批节点 |

```
用户请求 → 意图路由 → RAG检索 / MCP工具 / 人工审批 → LLM生成 → 响应
```

### CrewAI 多 Agent 协作

四角色 Agent 团队协作完成技术博客内容创作流水线。

| 角色 | 职责 |
|------|------|
| 🔍 高级研究员 | 深度调研主题，收集权威资料 |
| ✍️ 技术作家 | 基于研究成果撰写技术文章 |
| 📝 内容编辑 | 审校质量，优化结构与表达 |
| 📈 SEO 优化师 | 关键词优化，搜索引擎友好化 |

```
主题输入 → 研究 → 写作 → 编辑 → SEO优化 → 成品文章
```

## 🛠️ 技术栈全景


| 领域 | 技术 |
|------|------|
| 后端 | Java 17+, Spring Boot 3.x, Spring Cloud, Python 3.12+, FastAPI |
| AI Agent | LangGraph, CrewAI, OpenAI Agents SDK, MCP, A2A, AG-UI |
| RAG | LlamaIndex, LangChain, ChromaDB, pgvector |
| LLM | GPT-4o, Claude, Gemini, Qwen |
| 前端 | React, Vue3, Next.js, TypeScript |
| 移动端 | Swift/SwiftUI, Kotlin/Jetpack Compose |
| 数据库 | PostgreSQL, MongoDB, Redis, Elasticsearch |
| 工程化 | Docker, Kubernetes, GitHub Actions, Prometheus |

## 🤖 AI Agent 笔记亮点

这是目前最完整的部分，覆盖 AI Agent 全生态：

- Agent 协议生态：MCP / A2A / ACP / ANP / AG-UI 全面解析 + 协议转换工具
- 8 大主流框架对比：LangGraph / CrewAI / OpenAI SDK / Google ADK / AWS Strands / Spring AI / Vercel AI SDK / Dapr Agents
- RAG 进阶：架构设计 → 向量数据库选型 → 高级 RAG → GraphRAG
- 记忆框架：Mem0 / Letta(MemGPT) / Zep / LangMem
- Harness Engineering：完整指南 + Context Engineering + CI/CD 集成
- 实战案例：客服 / 代码 / 数据 / 研究 / 运维 / 内容创作 Agent

## 📬 联系方式

如果你对以下内容感兴趣，欢迎联系我获取访问权限：

- 📖 完整的技术学习笔记
- 💻 实战项目源码
- 🤝 技术交流与讨论

> 联系方式：[请通过 GitHub Issues 或邮件联系]

---

## 📄 License

MIT License - 详见 [LICENSE](./LICENSE) 文件

