# 技术学习笔记

> 本文件夹包含从 private-notes 中提取的技术学习内容，已移除所有敏感信息。

## 📚 内容说明

这些笔记是从个人学习过程中整理的技术内容，包括：

- ✅ 技术概念和原理
- ✅ 最佳实践和设计模式
- ✅ 代码示例和实现
- ✅ 学习路径和总结

**注意**：所有内容已移除：
- ❌ 项目机密信息
- ❌ 密码、Token、密钥
- ❌ 个人隐私信息
- ❌ 公司内部文档

## 📁 目录结构

```
learning-notes/
├── java/                          # Java 技术栈（按类别组织）
│   ├── 00-Java基础/               # Java 语言基础
│   │   └── Java新特性8-17.md
│   │
│   ├── 01-框架/                   # Spring 生态框架
│   │   ├── Spring基础01.md
│   │   ├── Spring基础02.md
│   │   ├── Spring基础03.md
│   │   ├── SpringBoot基础.md
│   │   ├── spring高级50讲.md
│   │   ├── SpringMVC基础01.md
│   │   ├── SpringMVC基础02.md
│   │   ├── SpringCloud01.md
│   │   ├── SpringCloud02.md
│   │   ├── MyBatisPlus.md
│   │   ├── 微服务保护-Sentinel.md
│   │   ├── 分布式事务.md
│   │   ├── spring-boot-best-practices.md
│   │   └── microservices-patterns.md
│   │
│   ├── 02-中间件/                 # 中间件技术
│   │   ├── RabbitMQ.md
│   │   ├── RabbitMQ高级篇.md
│   │   ├── Elasticsearch基础.md
│   │   ├── Elasticsearch进阶.md
│   │   ├── Elasticsearch高级.md
│   │   ├── Nginx简介.md
│   │   ├── Nginx常用配置.md
│   │   ├── Caffeine缓存.md
│   │   ├── Redis分布式缓存.md
│   │   ├── 多级缓存.md
│   │   └── kafka-event-driven-architecture.md
│   │
│   ├── 03-容器化/                 # 容器化与编排
│   │   ├── Docker实用篇.md
│   │   ├── docker-basics.md
│   │   ├── Kubernetes第1天.md
│   │   ├── Kubernetes第2天.md
│   │   ├── Kubernetes第3天.md
│   │   ├── Kubernetes第4天.md
│   │   ├── Kubernetes第5天.md
│   │   └── kubernetes-overview.md
│   │
│   ├── 04-设计模式/               # 设计模式
│   │   ├── 设计模式.md
│   │   └── design-patterns-summary.md
│   │
│   ├── 05-网络编程/               # 网络编程
│   │   ├── Netty01-nio.md
│   │   ├── Netty02-入门.md
│   │   ├── Netty03-进阶.md
│   │   ├── Netty04-优化与源码.md
│   │   └── gRPC-Java.md
│   │
│   ├── 06-构建工具/               # 构建工具
│   │   ├── Maven基础.md
│   │   ├── Maven高级.md
│   │   └── Gradle基础.md
│   │
│   ├── 07-数据库/                 # 数据库
│   │   ├── MySQL基础.md
│   │   ├── MySQL中级.md
│   │   └── MySQL高级.md
│   │
│   ├── 08-部署与运维/             # 部署与运维
│   │   ├── Nacos安装指南.md
│   │   ├── Nacos集群搭建.md
│   │   ├── RabbitMQ部署指南.md
│   │   ├── Elasticsearch安装指南.md
│   │   ├── CentOS7安装Docker.md
│   │   ├── Sentinel规则持久化.md
│   │   ├── Seata部署和集成.md
│   │   ├── Redis集群部署.md
│   │   ├── Canal安装配置.md
│   │   └── OpenResty安装配置.md
│   │
│   ├── 09-源码分析/               # 源码分析
│   │   ├── Nacos源码分析.md
│   │   └── Sentinel源码分析.md
│   │
│   ├── 10-工具与测试/             # 工具与测试
│   │   └── Jmeter快速入门.md
│   │
│   ├── 11-面试准备/               # 面试准备
│   │   └── 微服务常见面试题.md
│   │
│   └── README.md                  # Java 技术栈索引
│
├── python/                        # Python 技术栈
│   ├── 浅谈机器学习.md             # 机器学习概述
│   ├── 数据分析概述.md             # 数据分析基础
│   ├── fastapi-tutorial.md
│   └── rag-implementation.md
│
└── architecture/                  # 架构设计
    └── event-driven-architecture.md
```

## 🎯 内容分类

### Java 技术栈

**01-框架**
- **Spring 系列**：Spring 基础（IOC、DI、AOP）、Spring Boot、SpringMVC、Spring 高级特性
- **Spring Cloud**：微服务架构、服务发现、配置中心、网关等
- **微服务高级**：微服务保护（Sentinel）、分布式事务（Seata）
- **MyBatis Plus**：MyBatis 增强工具，简化开发
- **最佳实践**：统一异常处理、响应格式、全链路追踪、微服务架构模式

**02-中间件**
- **消息队列**：RabbitMQ（基础、高级篇）、Kafka 事件驱动架构
- **搜索引擎**：Elasticsearch（基础、进阶、高级）
- **Web 服务器**：Nginx（简介、常用配置）
- **缓存**：Caffeine 本地缓存、Redis 分布式缓存、多级缓存架构

**03-容器化**
- **Docker**：容器化部署、镜像构建、Docker Compose
- **Kubernetes**：容器编排、Pod、Service、Deployment 等核心概念（5天完整教程）

**04-设计模式**
- **设计模式**：23 种设计模式详解（创建型、结构型、行为型）

**05-网络编程**
- **Netty**：NIO 基础、入门、进阶、优化与源码分析
- **gRPC**：高性能 RPC 框架、Protobuf、HTTP/2

**06-构建工具**
- **Maven**：Maven 基础、Maven 高级（分模块、聚合、继承、私服）
- **Gradle**：Gradle 构建工具基础

**07-数据库**
- **MySQL**：MySQL 基础、MySQL 中级、MySQL 高级（索引、优化、锁等）

**08-部署与运维**
- **服务注册**：Nacos安装、集群搭建
- **消息队列**：RabbitMQ部署（单机、集群）
- **搜索引擎**：Elasticsearch安装
- **容器化**：Docker安装
- **微服务组件**：Sentinel规则持久化、Seata部署
- **缓存**：Redis集群、Canal、OpenResty

**09-源码分析**
- **Nacos源码分析**：服务注册发现、配置管理源码
- **Sentinel源码分析**：限流、熔断、降级源码

**10-工具与测试**
- **Jmeter**：性能测试工具快速入门

**11-面试准备**
- **微服务面试题**：Spring Cloud、Nacos、Sentinel等常见面试题

### Python 技术栈

- **浅谈机器学习**：机器学习概述、应用领域、算法分类
- **数据分析概述**：数据分析流程、工具库、技能栈
- **FastAPI 快速入门**：现代 Web 框架使用指南
- **RAG 检索增强生成**：RAG 实现和优化策略

### 架构设计

- **事件驱动架构**：EDA 模式和实践

## 📖 如何使用

1. **按需阅读**：根据技术栈选择相关内容
2. **实践应用**：结合项目实践应用所学
3. **持续更新**：根据学习进度更新内容

## 🔄 更新说明

这些笔记会持续更新，添加新的学习内容和实践经验。

## 📝 注意事项

- 这些是个人学习笔记，仅供参考
- 部分内容可能不够深入，建议结合官方文档学习
- 代码示例仅作参考，实际使用时需要根据场景调整

---

**提示**：如果想查看原始学习笔记（包含更多内容），请查看 `private-notes` 文件夹（本地，不上传到 GitHub）。
