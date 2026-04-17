# 微服务架构模式
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

> 从 private-notes 提取的技术学习笔记

## 微服务架构概述

微服务架构是一种将单一应用程序开发为一组小型服务的方法，每个服务运行在自己的进程中，并通过轻量级机制（通常是 HTTP RESTful API）进行通信。

## 核心模式

### 1. 服务拆分

**拆分原则**：
- 按业务领域拆分
- 单一职责原则
- 高内聚、低耦合

**拆分策略**：
- 按功能拆分
- 按数据拆分
- 按团队拆分

### 2. 服务通信

**同步通信**：
- REST API
- gRPC
- GraphQL

**异步通信**：
- 消息队列（Kafka、RabbitMQ）
- 事件驱动

### 3. 服务发现

**服务注册中心**：
- Eureka
- Consul
- Nacos

### 4. 配置管理

**配置中心**：
- Spring Cloud Config
- Nacos Config
- Apollo

### 5. 负载均衡

**负载均衡算法**：
- 轮询（Round Robin）
- 随机（Random）
- 加权轮询（Weighted Round Robin）
- 最少连接（Least Connections）

### 6. 熔断降级

**熔断器模式**：
- Hystrix
- Sentinel
- Resilience4j

### 7. 分布式事务

**解决方案**：
- 2PC（两阶段提交）
- TCC（Try-Confirm-Cancel）
- Saga 模式
- 最终一致性

## 最佳实践

1. **API 设计**：遵循 RESTful 规范
2. **数据管理**：每个服务独立数据库
3. **监控**：全链路追踪和监控
4. **测试**：单元测试、集成测试、契约测试
5. **部署**：容器化、CI/CD

## 技术栈

> 🔄 更新于 2026-04-18

<!-- version-check: Spring Cloud 2025.1, checked 2026-04-18 -->

### 当前推荐技术栈（2026）

- **服务框架**：Spring Boot 4.0 / Spring Boot 3.5.x
- **服务发现**：Nacos 2.x（国内首选）、Consul
- **配置中心**：Nacos Config、Spring Cloud Config
- **网关**：Spring Cloud Gateway
- **负载均衡**：Spring Cloud LoadBalancer（替代 Ribbon）
- **熔断降级**：Sentinel（国内首选）、Resilience4j
- **消息队列**：Kafka、RabbitMQ
- **监控**：Prometheus + Grafana、OpenTelemetry、Micrometer
- **链路追踪**：Micrometer Tracing（替代 Sleuth）+ Zipkin/Jaeger
- **HTTP 客户端**：RestClient / HTTP Interface Client（替代 RestTemplate/Feign）

### 已废弃/不推荐的技术

| 旧技术 | 替代方案 | 说明 |
|--------|---------|------|
| Eureka | Nacos / Consul | Netflix OSS 已停止维护 |
| Ribbon | Spring Cloud LoadBalancer | Ribbon 已进入维护模式 |
| Hystrix | Sentinel / Resilience4j | Hystrix 已停止维护 |
| Zuul | Spring Cloud Gateway | Zuul 1.x 已停止维护 |
| Sleuth | Micrometer Tracing | Sleuth 已合并到 Micrometer |
| RestTemplate | RestClient | RestTemplate 进入维护模式 |
| OpenFeign | HTTP Interface Client | Spring Cloud 2025.1 中 OpenFeign 支持已移除 |

### Spring Cloud 版本对应关系

| Spring Cloud | Spring Boot | 代号 | 状态 |
|-------------|-------------|------|------|
| 2025.1 | 4.0.x | Oakwood | 最新 |
| 2024.0 | 3.4.x | Moorgate | 稳定 |
| 2023.0 | 3.2.x/3.3.x | Leyton | 维护中 |
| 2022.0 | 3.0.x/3.1.x | Kilburn | EOL |
| Hoxton | 2.2.x/2.3.x | — | EOL |

> 来源：[Spring Cloud 官方](https://spring.io/projects/spring-cloud/)

## 参考资料

- [微服务架构模式](https://microservices.io/patterns/)
- [Spring Cloud 官方文档](https://spring.io/projects/spring-cloud)
- [Spring Boot 4.0 Release Highlights](https://spring.io/projects/release-highlights)

