# Tech Learning & Projects

> 个人技术学习笔记与实践项目集合

## 📚 项目简介

本项目包含技术学习笔记和实际项目代码，涵盖 Java 后端、Python AI、前端、iOS/Android 移动端、AI Agent 等领域。

## 📁 项目结构

```
.
├── learning-notes/              # 技术学习笔记
│   ├── java/                   # Java 技术栈（12个分类）
│   ├── python/                 # Python 技术栈（16个分类）
│   ├── frontend/               # 前端技术栈（16个分类）
│   ├── ios/                    # iOS 技术栈（11个分类）
│   ├── android/                # Android 技术栈（11个分类）
│   ├── ai-agent/               # AI Agent 技术栈（23个分类，85个文档）
│   └── architecture/           # 架构设计
│
├── spring-boot-microservice-demo/  # Spring Boot 微服务项目
├── rag-llm-agent-platform/         # RAG + LLM Agent 平台
├── langgraph-mcp-agent-demo/       # LangGraph + MCP Agent 示例
├── crewai-multi-agent-demo/        # CrewAI 多 Agent 协作示例
└── scripts/                        # 工具脚本
```

## 🎯 核心内容

### 学习笔记

| 技术栈 | 分类数 | 核心内容 |
|--------|--------|---------|
| [Java](./learning-notes/java/README.md) | 12 | Spring 全家桶、中间件、容器化、网络编程、数据库 |
| [Python](./learning-notes/python/README.md) | 16 | Web 开发、数据分析、机器学习、并发、爬虫 |
| [前端](./learning-notes/frontend/README.md) | 16 | React/Vue、TypeScript、Node.js、工程化、性能优化 |
| [iOS](./learning-notes/ios/README.md) | 11 | Swift、SwiftUI/UIKit、架构模式、系统框架 |
| [Android](./learning-notes/android/README.md) | 11 | Kotlin、Jetpack Compose、Jetpack 组件、架构模式 |
| [AI Agent](./learning-notes/ai-agent/README.md) | 23 | Agent 协议/框架/RAG/工具/Voice/Harness Engineering（85个文档） |

### 实战项目

| 项目 | 技术栈 | 核心功能 |
|------|--------|---------|
| [Spring Boot 微服务](./spring-boot-microservice-demo/README.md) | Java, Spring Cloud, Kafka, K8s | 事件驱动、全链路追踪、容器化部署 |
| [RAG LLM Agent 平台](./rag-llm-agent-platform/README.md) | Python, FastAPI, LlamaIndex, pgvector | RAG 检索、30+ Function Calling、流式交互 |
| [LangGraph + MCP Agent](./langgraph-mcp-agent-demo/README.md) | Python, LangGraph, MCP, ChromaDB | 图工作流、MCP 工具、RAG、人机交互 |
| [CrewAI 多 Agent 协作](./crewai-multi-agent-demo/README.md) | Python, CrewAI, FastAPI | 四角色 Agent 团队、顺序/层级执行、记忆系统 |

## 🛠️ 技术栈

### 后端开发
- **Java**: JDK 17+, Spring Boot 3.x, Spring Cloud
- **Python**: Python 3.12+, FastAPI
- **消息队列**: Kafka, RabbitMQ
- **数据库**: PostgreSQL, MongoDB, Redis, Elasticsearch
- **向量数据库**: PostgreSQL + pgvector, ChromaDB

### AI Agent
- **框架**: LangGraph, CrewAI, OpenAI Agents SDK
- **协议**: MCP, A2A, AG-UI
- **RAG**: LlamaIndex, LangChain, ChromaDB
- **LLM**: OpenAI GPT-4o, Anthropic Claude, Gemini, Qwen
- **工程化**: Harness Engineering, LangSmith, LangFuse

### 前端
- **框架**: React, Vue3, Next.js, Nuxt3
- **语言**: TypeScript, JavaScript
- **工程化**: Vite, Webpack, pnpm, ESLint

### 移动端
- **iOS**: Swift, SwiftUI, UIKit
- **Android**: Kotlin, Jetpack Compose

### 工程化
- **容器化**: Docker, Docker Compose
- **编排**: Kubernetes
- **CI/CD**: GitHub Actions
- **监控**: Prometheus, Grafana

## 📝 说明

- 学习笔记内容已移除所有敏感信息
- 项目代码为技术实践示例，不包含商业机密
- 所有配置使用环境变量，不包含硬编码密钥

## 📄 License

MIT License - 详见 [LICENSE](./LICENSE) 文件
