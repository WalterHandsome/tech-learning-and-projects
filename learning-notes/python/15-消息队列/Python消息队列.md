# Python消息队列

## 1. 消息队列概述

消息队列是一种异步通信机制，用于解耦生产者和消费者。Python常用的消息队列：
- **RabbitMQ**：功能强大的消息代理
- **Kafka**：高吞吐量的分布式流平台
- **Redis**：轻量级消息队列
- **Celery**：分布式任务队列

## 2. RabbitMQ

### 2.1 安装

```bash
pip install pika
```

### 2.2 基本使用

#### 生产者

```python
import pika

# 连接RabbitMQ
connection = pika.BlockingConnection(
    pika.ConnectionParameters('localhost')
)
channel = connection.channel()

# 声明队列
channel.queue_declare(queue='hello')

# 发送消息
channel.basic_publish(
    exchange='',
    routing_key='hello',
    body='Hello, RabbitMQ!'
)

print("消息已发送")
connection.close()
```

#### 消费者

```python
import pika

def callback(ch, method, properties, body):
    print(f"收到消息: {body.decode()}")

# 连接
connection = pika.BlockingConnection(
    pika.ConnectionParameters('localhost')
)
channel = connection.channel()

# 声明队列
channel.queue_declare(queue='hello')

# 消费消息
channel.basic_consume(
    queue='hello',
    on_message_callback=callback,
    auto_ack=True
)

print('等待消息...')
channel.start_consuming()
```

### 2.3 工作队列

#### 生产者

```python
import pika
import sys

connection = pika.BlockingConnection(
    pika.ConnectionParameters('localhost')
)
channel = connection.channel()

channel.queue_declare(queue='task_queue', durable=True)

message = ' '.join(sys.argv[1:]) or "Hello World!"
channel.basic_publish(
    exchange='',
    routing_key='task_queue',
    body=message,
    properties=pika.BasicProperties(
        delivery_mode=2,  # 消息持久化
    )
)

connection.close()
```

#### 消费者

```python
import pika
import time

def callback(ch, method, properties, body):
    print(f"收到: {body.decode()}")
    time.sleep(body.count(b'.'))
    print("完成")
    ch.basic_ack(delivery_tag=method.delivery_tag)

connection = pika.BlockingConnection(
    pika.ConnectionParameters('localhost')
)
channel = connection.channel()

channel.queue_declare(queue='task_queue', durable=True)
channel.basic_qos(prefetch_count=1)  # 公平分发

channel.basic_consume(
    queue='task_queue',
    on_message_callback=callback
)

channel.start_consuming()
```

### 2.4 发布/订阅

#### 发布者

```python
import pika

connection = pika.BlockingConnection(
    pika.ConnectionParameters('localhost')
)
channel = connection.channel()

# 声明交换机
channel.exchange_declare(exchange='logs', exchange_type='fanout')

message = "日志消息"
channel.basic_publish(
    exchange='logs',
    routing_key='',
    body=message
)

connection.close()
```

#### 订阅者

```python
import pika

connection = pika.BlockingConnection(
    pika.ConnectionParameters('localhost')
)
channel = connection.channel()

# 声明交换机
channel.exchange_declare(exchange='logs', exchange_type='fanout')

# 声明临时队列
result = channel.queue_declare(queue='', exclusive=True)
queue_name = result.method.queue

# 绑定队列
channel.queue_bind(exchange='logs', queue=queue_name)

def callback(ch, method, properties, body):
    print(f"收到: {body.decode()}")

channel.basic_consume(
    queue=queue_name,
    on_message_callback=callback,
    auto_ack=True
)

channel.start_consuming()
```

### 2.5 路由

```python
# 发布者
channel.exchange_declare(exchange='direct_logs', exchange_type='direct')

severity = 'error'
message = '错误消息'
channel.basic_publish(
    exchange='direct_logs',
    routing_key=severity,
    body=message
)

# 消费者
channel.exchange_declare(exchange='direct_logs', exchange_type='direct')
result = channel.queue_declare(queue='', exclusive=True)
queue_name = result.method.queue

# 绑定多个路由键
for severity in ['error', 'warning', 'info']:
    channel.queue_bind(
        exchange='direct_logs',
        queue=queue_name,
        routing_key=severity
    )
```

## 3. Kafka

### 3.1 安装

```bash
pip install kafka-python
```

### 3.2 生产者

```python
from kafka import KafkaProducer
import json

# 创建生产者
producer = KafkaProducer(
    bootstrap_servers=['localhost:9092'],
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

# 发送消息
producer.send('my_topic', {'key': 'value'})

# 确保消息发送
producer.flush()
producer.close()
```

### 3.3 消费者

```python
from kafka import KafkaConsumer
import json

# 创建消费者
consumer = KafkaConsumer(
    'my_topic',
    bootstrap_servers=['localhost:9092'],
    value_deserializer=lambda m: json.loads(m.decode('utf-8')),
    auto_offset_reset='earliest',
    enable_auto_commit=True,
    group_id='my-group'
)

# 消费消息
for message in consumer:
    print(f"收到: {message.value}")
```

### 3.4 批量消费

```python
from kafka import KafkaConsumer

consumer = KafkaConsumer(
    'my_topic',
    bootstrap_servers=['localhost:9092'],
    max_poll_records=100
)

while True:
    msg_pack = consumer.poll(timeout_ms=1000)
    for topic_partition, messages in msg_pack.items():
        for message in messages:
            print(message.value)
```

## 4. Redis消息队列

### 4.1 简单队列

```python
import redis
import json

r = redis.Redis(host='localhost', port=6379, db=0)

# 生产者
def produce(queue_name, message):
    r.lpush(queue_name, json.dumps(message))

# 消费者
def consume(queue_name, timeout=0):
    result = r.brpop(queue_name, timeout=timeout)
    if result:
        return json.loads(result[1])
    return None

# 使用
produce('my_queue', {'data': 'value'})
message = consume('my_queue', timeout=1)
```

### 4.2 发布/订阅

```python
import redis
import json

r = redis.Redis(host='localhost', port=6379, db=0)

# 发布者
def publish(channel, message):
    r.publish(channel, json.dumps(message))

# 订阅者
class Subscriber:
    def __init__(self):
        self.pubsub = r.pubsub()
    
    def subscribe(self, channel):
        self.pubsub.subscribe(channel)
    
    def listen(self):
        for message in self.pubsub.listen():
            if message['type'] == 'message':
                data = json.loads(message['data'])
                print(f"收到: {data}")

# 使用
subscriber = Subscriber()
subscriber.subscribe('my_channel')
subscriber.listen()
```

## 5. Celery

### 5.1 安装

```bash
pip install celery redis
```

### 5.2 配置

```python
# celery_app.py
from celery import Celery

app = Celery(
    'tasks',
    broker='redis://localhost:6379/0',
    backend='redis://localhost:6379/0'
)

app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
)
```

### 5.3 定义任务

```python
from celery_app import app

@app.task
def add(x, y):
    return x + y

@app.task
def send_email(to, subject, body):
    # 发送邮件逻辑
    return f"邮件已发送到 {to}"
```

### 5.4 调用任务

```python
from tasks import add, send_email

# 异步调用
result = add.delay(4, 4)
print(result.get())  # 获取结果

# 定时任务
from datetime import datetime, timedelta
eta = datetime.now() + timedelta(seconds=10)
add.apply_async((4, 4), eta=eta)

# 定期任务
from celery.schedules import crontab

app.conf.beat_schedule = {
    'send-email-every-minute': {
        'task': 'tasks.send_email',
        'schedule': crontab(minute='*/1'),
        'args': ('user@example.com', 'Subject', 'Body')
    },
}
```

### 5.5 启动Worker

```bash
# 启动worker
celery -A tasks worker --loglevel=info

# 启动beat（定时任务）
celery -A tasks beat --loglevel=info
```

## 6. 消息队列选择

### 6.1 RabbitMQ

**适用场景**：
- 需要复杂的路由规则
- 需要消息确认和持久化
- 中小型应用

**优点**：
- 功能丰富
- 可靠性高
- 易于使用

### 6.2 Kafka

**适用场景**：
- 高吞吐量需求
- 流式数据处理
- 大数据场景

**优点**：
- 高吞吐量
- 可扩展性强
- 支持流处理

### 6.3 Redis

**适用场景**：
- 简单队列需求
- 已有Redis基础设施
- 轻量级应用

**优点**：
- 简单易用
- 性能好
- 无需额外组件

### 6.4 Celery

**适用场景**：
- 异步任务处理
- 定时任务
- 分布式任务

**优点**：
- 功能强大
- 支持多种后端
- 易于集成

## 7. 最佳实践

1. **消息持久化**：重要消息需要持久化
2. **消息确认**：确保消息被正确处理
3. **错误处理**：处理消息处理失败的情况
4. **监控**：监控队列长度和处理速度
5. **限流**：防止消息积压

## 8. 总结

Python消息队列工具：
- **RabbitMQ**：功能丰富的消息代理
- **Kafka**：高吞吐量的流平台
- **Redis**：轻量级消息队列
- **Celery**：分布式任务队列

选择合适的消息队列可以提高系统的可扩展性和可靠性。

