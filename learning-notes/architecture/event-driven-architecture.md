# 事件驱动架构

> 从 private-notes 提取的技术学习笔记

## 事件驱动架构概述

事件驱动架构（Event-Driven Architecture, EDA）是一种软件架构模式，通过事件实现服务间的解耦和异步通信。

## 核心概念

### 事件（Event）

事件是系统中发生的重要业务事实，是不可变的。

### 事件发布者（Publisher）

发布事件的组件，不关心谁订阅了事件。

### 事件订阅者（Subscriber）

订阅事件的组件，对事件做出响应。

### 事件总线（Event Bus）

事件的中介，解耦发布者和订阅者。

## 架构模式

### 1. 发布-订阅模式

```
Publisher → Event Bus → Multiple Subscribers
```

### 2. 事件流模式

```
Event Stream → Multiple Processors
```

## 优势

1. **解耦**：服务间松耦合
2. **可扩展**：易于添加新的事件处理者
3. **异步**：提高系统吞吐量
4. **容错**：故障隔离

## 实现技术

- **消息队列**：Kafka、RabbitMQ、Redis Streams
- **事件存储**：EventStore
- **流处理**：Kafka Streams、Flink

## 最佳实践

1. **事件设计**：事件应该是不可变的、自包含的
2. **幂等性**：确保事件处理是幂等的
3. **版本控制**：支持事件版本演进
4. **监控**：监控事件处理延迟和错误率

## 参考资料

- [事件驱动架构模式](https://microservices.io/patterns/data/event-driven-architecture.html)
- [Martin Fowler - Event-Driven Architecture](https://martinfowler.com/articles/201701-event-driven.html)

