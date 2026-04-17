# Kafka 事件驱动架构
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

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

## Kafka 版本演进

> 🔄 更新于 2026-04-18

<!-- version-check: Kafka 4.2.0, checked 2026-04-18 -->

### Kafka 4.x 重大变化

Apache Kafka 4.0（2025 年底）是一次里程碑式的架构升级：

| 变化 | 说明 |
|------|------|
| **ZooKeeper 完全移除** | KRaft 成为唯一的集群管理方式，不再依赖 ZooKeeper |
| **KRaft 模式** | 基于 Raft 共识协议的原生元数据管理，简化部署和运维 |
| **Queues for Kafka（KIP-932）** | Share Groups 支持队列语义，多消费者可并发消费同一分区 |
| **Kafka 4.2.0**（2026-02） | 当前最新稳定版，Share Groups 生产就绪 |

**KRaft 模式启动（无需 ZooKeeper）：**

```bash
# 生成集群 ID
KAFKA_CLUSTER_ID="$(bin/kafka-storage.sh random-uuid)"

# 格式化存储
bin/kafka-storage.sh format -t $KAFKA_CLUSTER_ID -c config/kraft/server.properties

# 启动 Kafka（KRaft 模式）
bin/kafka-server-start.sh config/kraft/server.properties
```

**Share Groups（队列语义）：**

```java
// Kafka 4.x：Share Groups 消费者
// 多个消费者可以并发消费同一分区的不同消息
Properties props = new Properties();
props.put("bootstrap.servers", "localhost:9092");
props.put("group.id", "my-share-group");
props.put("group.type", "share"); // 新增：指定为 Share Group

KafkaShareConsumer<String, String> consumer = new KafkaShareConsumer<>(props);
consumer.subscribe(List.of("my-topic"));
```

> 来源：[Apache Kafka 4.2.0 Release](https://kafka.apache.org/blog/2026/02/17/apache-kafka-4.2.0-release-announcement/)

## 参考资料

- [Kafka 官方文档](https://kafka.apache.org/documentation/)
- [事件驱动架构模式](https://microservices.io/patterns/data/event-driven-architecture.html)
- [KRaft 模式指南](https://developer.confluent.io/learn/kraft/)

