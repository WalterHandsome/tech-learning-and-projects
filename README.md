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
- [Spring Boot 微服务项目](./spring-boot-microservice-demo/README.md)
- [RAG LLM Agent 平台](./rag-llm-agent-platform/README.md)

## 📝 说明

- 学习笔记内容已移除所有敏感信息
- 项目代码为技术实践示例，不包含商业机密
- 所有配置使用环境变量，不包含硬编码密钥

## 📄 License

MIT License - 详见 [LICENSE](./LICENSE) 文件

---

**最后更新**: 2024年

