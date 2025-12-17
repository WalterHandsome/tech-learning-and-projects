# Python并发编程

## 1. 并发编程概述

并发编程是指在同一时间段内执行多个任务，Python提供了多种并发编程的方式：
- **多线程（threading）**：适合I/O密集型任务
- **多进程（multiprocessing）**：适合CPU密集型任务
- **异步编程（asyncio）**：适合高并发I/O操作

## 2. 多线程编程

### 2.1 线程基础

```python
import threading
import time

def worker(name):
    print(f'线程 {name} 开始执行')
    time.sleep(2)
    print(f'线程 {name} 执行完成')

# 创建线程
t1 = threading.Thread(target=worker, args=('A',))
t2 = threading.Thread(target=worker, args=('B',))

# 启动线程
t1.start()
t2.start()

# 等待线程完成
t1.join()
t2.join()
```

### 2.2 线程类

```python
class MyThread(threading.Thread):
    def __init__(self, name):
        super().__init__()
        self.name = name
    
    def run(self):
        print(f'线程 {self.name} 开始执行')
        time.sleep(2)
        print(f'线程 {self.name} 执行完成')

# 使用
t = MyThread('Worker')
t.start()
t.join()
```

### 2.3 线程同步

#### 锁（Lock）

```python
import threading

counter = 0
lock = threading.Lock()

def increment():
    global counter
    for _ in range(100000):
        lock.acquire()
        counter += 1
        lock.release()

# 使用with语句
def increment_safe():
    global counter
    for _ in range(100000):
        with lock:
            counter += 1

t1 = threading.Thread(target=increment_safe)
t2 = threading.Thread(target=increment_safe)
t1.start()
t2.start()
t1.join()
t2.join()
print(f'Counter: {counter}')
```

#### 可重入锁（RLock）

```python
rlock = threading.RLock()

def recursive_function(count):
    with rlock:
        if count > 0:
            print(f'Count: {count}')
            recursive_function(count - 1)
```

#### 信号量（Semaphore）

```python
semaphore = threading.Semaphore(3)  # 最多3个线程同时执行

def worker():
    with semaphore:
        print(f'{threading.current_thread().name} 开始工作')
        time.sleep(2)
        print(f'{threading.current_thread().name} 完成工作')

for i in range(10):
    t = threading.Thread(target=worker)
    t.start()
```

#### 事件（Event）

```python
event = threading.Event()

def waiter():
    print('等待事件...')
    event.wait()
    print('事件已触发')

def setter():
    time.sleep(3)
    print('设置事件')
    event.set()

t1 = threading.Thread(target=waiter)
t2 = threading.Thread(target=setter)
t1.start()
t2.start()
```

#### 条件变量（Condition）

```python
condition = threading.Condition()
items = []

def consumer():
    with condition:
        while len(items) == 0:
            condition.wait()
        item = items.pop(0)
        print(f'消费: {item}')

def producer():
    with condition:
        items.append('item')
        condition.notify()

t1 = threading.Thread(target=consumer)
t2 = threading.Thread(target=producer)
t1.start()
t2.start()
```

### 2.4 线程池

```python
from concurrent.futures import ThreadPoolExecutor
import time

def task(n):
    print(f'任务 {n} 开始')
    time.sleep(1)
    return n * 2

# 使用线程池
with ThreadPoolExecutor(max_workers=3) as executor:
    futures = [executor.submit(task, i) for i in range(5)]
    results = [f.result() for f in futures]
    print(results)
```

### 2.5 线程本地存储

```python
thread_local = threading.local()

def worker():
    thread_local.value = threading.current_thread().name
    print(f'线程本地值: {thread_local.value}')

t1 = threading.Thread(target=worker)
t2 = threading.Thread(target=worker)
t1.start()
t2.start()
```

## 3. 多进程编程

### 3.1 进程基础

```python
import multiprocessing
import time

def worker(name):
    print(f'进程 {name} 开始执行')
    time.sleep(2)
    print(f'进程 {name} 执行完成')

if __name__ == '__main__':
    p1 = multiprocessing.Process(target=worker, args=('A',))
    p2 = multiprocessing.Process(target=worker, args=('B',))
    
    p1.start()
    p2.start()
    
    p1.join()
    p2.join()
```

### 3.2 进程间通信

#### 队列（Queue）

```python
from multiprocessing import Process, Queue

def producer(q):
    for i in range(5):
        q.put(i)
        print(f'生产: {i}')

def consumer(q):
    while True:
        item = q.get()
        if item is None:
            break
        print(f'消费: {item}')

if __name__ == '__main__':
    q = Queue()
    p1 = Process(target=producer, args=(q,))
    p2 = Process(target=consumer, args=(q,))
    
    p1.start()
    p2.start()
    
    p1.join()
    q.put(None)  # 结束信号
    p2.join()
```

#### 管道（Pipe）

```python
from multiprocessing import Process, Pipe

def sender(conn):
    conn.send('Hello')
    conn.close()

def receiver(conn):
    msg = conn.recv()
    print(f'收到: {msg}')
    conn.close()

if __name__ == '__main__':
    parent_conn, child_conn = Pipe()
    p1 = Process(target=sender, args=(child_conn,))
    p2 = Process(target=receiver, args=(parent_conn,))
    
    p1.start()
    p2.start()
    p1.join()
    p2.join()
```

#### 共享内存

```python
from multiprocessing import Process, Value, Array

def increment(n, arr):
    n.value += 1
    for i in range(len(arr)):
        arr[i] += 1

if __name__ == '__main__':
    num = Value('i', 0)
    arr = Array('i', [1, 2, 3])
    
    p1 = Process(target=increment, args=(num, arr))
    p2 = Process(target=increment, args=(num, arr))
    
    p1.start()
    p2.start()
    p1.join()
    p2.join()
    
    print(f'Num: {num.value}')
    print(f'Arr: {list(arr)}')
```

### 3.3 进程池

```python
from multiprocessing import Pool
import time

def task(n):
    print(f'任务 {n} 开始')
    time.sleep(1)
    return n * 2

if __name__ == '__main__':
    with Pool(processes=3) as pool:
        results = pool.map(task, range(5))
        print(results)
```

### 3.4 进程锁

```python
from multiprocessing import Process, Lock

def worker(lock, counter):
    for _ in range(100000):
        with lock:
            counter.value += 1

if __name__ == '__main__':
    lock = Lock()
    counter = multiprocessing.Value('i', 0)
    
    p1 = Process(target=worker, args=(lock, counter))
    p2 = Process(target=worker, args=(lock, counter))
    
    p1.start()
    p2.start()
    p1.join()
    p2.join()
    
    print(f'Counter: {counter.value}')
```

## 4. 异步编程（asyncio）

### 4.1 协程基础

```python
import asyncio

async def hello():
    print('Hello')
    await asyncio.sleep(1)
    print('World')

# 运行协程
asyncio.run(hello())
```

### 4.2 并发执行

```python
import asyncio

async def task(name, delay):
    print(f'任务 {name} 开始')
    await asyncio.sleep(delay)
    print(f'任务 {name} 完成')
    return f'任务 {name} 结果'

async def main():
    # 并发执行多个任务
    results = await asyncio.gather(
        task('A', 2),
        task('B', 1),
        task('C', 3)
    )
    print(results)

asyncio.run(main())
```

### 4.3 任务管理

```python
import asyncio

async def long_task():
    await asyncio.sleep(5)
    return '完成'

async def main():
    # 创建任务
    task1 = asyncio.create_task(long_task())
    task2 = asyncio.create_task(long_task())
    
    # 等待任务完成
    results = await asyncio.gather(task1, task2)
    print(results)

asyncio.run(main())
```

### 4.4 异步锁

```python
import asyncio

async def worker(lock, name):
    async with lock:
        print(f'{name} 开始工作')
        await asyncio.sleep(1)
        print(f'{name} 完成工作')

async def main():
    lock = asyncio.Lock()
    await asyncio.gather(
        worker(lock, 'A'),
        worker(lock, 'B'),
        worker(lock, 'C')
    )

asyncio.run(main())
```

### 4.5 异步队列

```python
import asyncio

async def producer(queue):
    for i in range(5):
        await queue.put(i)
        print(f'生产: {i}')
        await asyncio.sleep(0.5)

async def consumer(queue):
    while True:
        item = await queue.get()
        if item is None:
            break
        print(f'消费: {item}')
        queue.task_done()

async def main():
    queue = asyncio.Queue()
    
    # 创建生产者和消费者
    prod = asyncio.create_task(producer(queue))
    cons = asyncio.create_task(consumer(queue))
    
    await prod
    await queue.put(None)  # 结束信号
    await cons

asyncio.run(main())
```

### 4.6 异步HTTP请求

```python
import asyncio
import aiohttp

async def fetch(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.text()

async def main():
    urls = [
        'https://www.example.com',
        'https://www.python.org',
        'https://www.github.com'
    ]
    
    tasks = [fetch(url) for url in urls]
    results = await asyncio.gather(*tasks)
    print(results)

asyncio.run(main())
```

## 5. 选择合适的方式

### 5.1 I/O密集型任务

适合使用**多线程**或**异步编程**：

```python
# 多线程方式
import threading
import requests

def fetch_url(url):
    response = requests.get(url)
    return response.status_code

threads = []
for url in urls:
    t = threading.Thread(target=fetch_url, args=(url,))
    t.start()
    threads.append(t)

for t in threads:
    t.join()

# 异步方式（更高效）
import asyncio
import aiohttp

async def fetch_url(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return response.status

async def main():
    tasks = [fetch_url(url) for url in urls]
    results = await asyncio.gather(*tasks)
    return results
```

### 5.2 CPU密集型任务

适合使用**多进程**：

```python
from multiprocessing import Pool

def cpu_intensive_task(n):
    result = 0
    for i in range(n):
        result += i ** 2
    return result

if __name__ == '__main__':
    with Pool() as pool:
        results = pool.map(cpu_intensive_task, [1000000] * 4)
```

## 6. 最佳实践

1. **避免全局解释器锁（GIL）的影响**：对于CPU密集型任务，使用多进程
2. **合理使用线程池和进程池**：避免创建过多线程/进程
3. **注意线程安全**：使用锁保护共享资源
4. **异步编程的优势**：对于高并发I/O操作，异步编程性能更好
5. **避免死锁**：注意锁的获取顺序

## 7. 总结

Python提供了多种并发编程方式：
- **多线程**：适合I/O密集型任务，但受GIL限制
- **多进程**：适合CPU密集型任务，可以充分利用多核CPU
- **异步编程**：适合高并发I/O操作，性能优异

选择合适的并发方式可以显著提高程序性能。

