# Kafka 事件驱动架构

> 从 private-notes 提取的技术学习笔记

## 概述

事件驱动架构（Event-Driven Architecture）是一种软件架构模式，通过事件实现服务间的解耦和异步通信。

## 核心概念

### 同步 vs 异步通信

**同步通信**：
- 实时响应
- 耦合度高
- 性能和吞吐能力下降
- 有级联失败问题

**异步通信**：
- 吞吐量提升
- 故障隔离
- 耦合度极低
- 流量削峰

### 事件驱动架构

```
发布者 (Publisher) → 事件总线 (Broker) → 订阅者 (Subscriber)
```

**优势**：
- 服务解耦
- 异步处理
- 可扩展性强
- 容错性好

## Kafka 实现

### 基本概念

- **Topic**：消息主题
- **Partition**：分区，提高并发
- **Producer**：生产者
- **Consumer**：消费者
- **Consumer Group**：消费者组

### 使用示例

```java
// 生产者
@Service
public class EventPublisher {
    @Autowired
    private KafkaTemplate<String, Object> kafkaTemplate;
    
    public void publishEvent(String topic, Object event) {
        kafkaTemplate.send(topic, event);
    }
}

// 消费者
@Component
public class EventConsumer {
    @KafkaListener(topics = "user-created", groupId = "order-service")
    public void handleUserCreated(UserCreatedEvent event) {
        // 处理事件
    }
}
```

## 最佳实践

1. **事件设计**：事件应该是不可变的、自包含的
2. **幂等性**：确保事件处理是幂等的
3. **错误处理**：实现重试和死信队列
4. **监控**：监控事件处理延迟和错误率

## 参考资料

- [Kafka 官方文档](https://kafka.apache.org/documentation/)
- [事件驱动架构模式](https://microservices.io/patterns/data/event-driven-architecture.html)

