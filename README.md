# Tech Learning & Projects

> 个人技术学习笔记与实践项目集合

## 📚 项目简介

本项目包含技术学习笔记和实际项目代码，涵盖 Java 后端开发、Python AI 工程化等领域。

## 📁 项目结构

```
.
├── learning-notes/              # 技术学习笔记
│   ├── java/                   # Java 技术栈学习笔记
│   ├── python/                 # Python 技术栈学习笔记
│   ├── frontend/               # 前端技术栈学习笔记
│   ├── ios/                    # iOS 技术栈学习笔记
│   ├── android/                # Android 技术栈学习笔记
│   ├── ai-agent/               # AI Agent 技术栈学习笔记
│   └── architecture/           # 架构设计相关
│
├── spring-boot-microservice-demo/  # Spring Boot 微服务项目
│   ├── common-lib/             # 公共库
│   ├── user-service/           # 用户服务
│   └── order-service/          # 订单服务
│
├── rag-llm-agent-platform/     # RAG + LLM Agent 平台
│   ├── app/                    # 应用代码
│   ├── tests/                  # 测试代码
│   └── k8s/                    # Kubernetes 配置
│
├── langgraph-mcp-agent-demo/   # LangGraph + MCP Agent 示例
│   ├── app/agent/              # LangGraph 工作流
│   ├── app/mcp_servers/        # MCP Server 实现
│   ├── app/rag/                # RAG 检索模块
│   └── app/api/                # FastAPI 接口
│
├── crewai-multi-agent-demo/    # CrewAI 多 Agent 协作示例
│   ├── app/agents/             # Agent 角色定义
│   ├── app/tasks/              # 任务定义
│   ├── app/crews/              # Crew 组装
│   └── app/tools/              # 自定义工具
│
└── scripts/                     # 工具脚本
```

## 🎯 核心内容

### 1. 学习笔记 (learning-notes)

**Java 技术栈**

- Java 基础（12个文档）
- Spring 框架系列（Spring、Spring Boot、Spring Cloud）
- 中间件（Kafka、RabbitMQ、Redis、Elasticsearch、Nginx）
- 容器化（Docker、Kubernetes）
- 设计模式、网络编程、数据库等

**Python 技术栈**

- Python 基础（16个文档）
- Web 开发（FastAPI、Django、Flask）
- 数据分析（NumPy、Pandas、数据可视化）
- 机器学习（RAG、机器学习基础）
- 并发编程、网络编程、爬虫、数据库操作等

**前端技术栈**

- HTML5/CSS3 基础、Flex/Grid 布局、响应式设计
- JavaScript 基础、ES6+、TypeScript
- React（Hooks、状态管理、Router、性能优化）
- Vue3（组合式API、Pinia、Vue Router、Nuxt3）
- 工程化（Webpack、Vite、ESLint、Monorepo）
- Node.js（Express、Koa、数据库操作）
- 测试、浏览器原理、性能优化、跨平台开发、数据可视化等

**iOS 技术栈**

- Swift 语言基础（语法、OOP、协议与泛型、并发、ARC）
- SwiftUI（布局、状态管理、导航、动画）
- UIKit（核心组件、AutoLayout、TableView/CollectionView）
- 数据持久化、网络编程、架构模式（MVVM、Combine、Clean Architecture）
- 系统框架、性能优化、工程化、面试准备等

**Android 技术栈**

- Kotlin 语言基础（语法、OOP、函数式编程、协程、Java互操作）
- Jetpack Compose（布局、状态管理、导航、动画）
- 传统View体系（RecyclerView、ConstraintLayout、自定义View）
- Jetpack组件、网络编程、架构模式（MVVM/MVI、Hilt、Clean Architecture）
- 系统能力、性能优化、工程化、面试准备等

**AI Agent 技术栈**

- Agent 核心概念、大语言模型基础、Prompt Engineering
- Agent 协议（MCP 模型上下文协议、A2A Agent间通信、ACP）
- Agent 框架（LangGraph、CrewAI、OpenAI Agents SDK、Google ADK）
- RAG 进阶（高级RAG策略、GraphRAG、向量数据库选型）
- 工具与 Function Calling、多Agent系统、记忆与状态
- 模型服务、可观测与评估、低代码平台、实战案例

### 2. Spring Boot 微服务项目

基于 Spring Boot 3.x 的微服务架构实践：

- ✅ 事件驱动架构（Kafka）
- ✅ 统一异常处理和响应格式
- ✅ 全链路追踪（TraceId）
- ✅ Docker 容器化部署
- ✅ Kubernetes 编排配置

**快速开始**: 查看 [项目 README](./spring-boot-microservice-demo/README.md)

### 3. RAG + LLM Agent 平台

企业级 AI Agent 平台：

- ✅ RAG 检索增强生成
- ✅ Function Calling 工具体系（30+ 工具）
- ✅ WebSocket 流式交互
- ✅ 向量数据库（PostgreSQL + pgvector）

**快速开始**: 查看 [项目 README](./rag-llm-agent-platform/README.md)

### 4. LangGraph + MCP Agent 示例

基于 LangGraph 工作流和 MCP 工具协议的智能 Agent：

- ✅ LangGraph 图结构工作流编排
- ✅ MCP 工具自动发现与调用
- ✅ RAG 知识库检索（ChromaDB）
- ✅ 人机交互节点（敏感操作审批）
- ✅ 会话记忆与状态持久化

**快速开始**: 查看 [项目 README](./langgraph-mcp-agent-demo/README.md)

### 5. CrewAI 多 Agent 协作示例

基于 CrewAI 的角色化多 Agent 协作内容创作流水线：

- ✅ 四角色 Agent 团队（研究员/作家/编辑/SEO优化师）
- ✅ 顺序执行与层级执行模式
- ✅ MCP 工具集成（网络搜索、网页抓取）
- ✅ 记忆系统（短期 + 长期 + 实体记忆）
- ✅ CLI + API 双模式运行

**快速开始**: 查看 [项目 README](./crewai-multi-agent-demo/README.md)

## 🛠️ 技术栈

### 后端开发

- **Java**: JDK 17+, Spring Boot 3.x, Spring Cloud
- **Python**: Python 3.10+, FastAPI
- **消息队列**: Kafka, RabbitMQ
- **数据库**: PostgreSQL, MongoDB, Redis, Elasticsearch
- **向量数据库**: PostgreSQL + pgvector

### AI & LLM

- **RAG**: LlamaIndex
- **LLM**: Amazon Bedrock (Claude), OpenAI API
- **Function Calling**: 自定义工具体系

### 工程化

- **容器化**: Docker, Docker Compose
- **编排**: Kubernetes
- **CI/CD**: GitHub Actions
- **监控**: Prometheus, Grafana

## 📖 文档导航

- [Java 学习笔记](./learning-notes/java/README.md)
- [Python 学习笔记](./learning-notes/python/README.md)
- [前端学习笔记](./learning-notes/frontend/README.md)
- [iOS 学习笔记](./learning-notes/ios/README.md)
- [Android 学习笔记](./learning-notes/android/README.md)
- [AI Agent 学习笔记](./learning-notes/ai-agent/README.md)
- [Spring Boot 微服务项目](./spring-boot-microservice-demo/README.md)
- [RAG LLM Agent 平台](./rag-llm-agent-platform/README.md)

## 📝 说明

- 学习笔记内容已移除所有敏感信息
- 项目代码为技术实践示例，不包含商业机密
- 所有配置使用环境变量，不包含硬编码密钥

## 📄 License

MIT License - 详见 [LICENSE](./LICENSE) 文件

---

**最后更新**: 2026年
