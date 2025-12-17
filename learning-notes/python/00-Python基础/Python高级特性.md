# Python高级特性

## 1. 生成器（Generator）

生成器是一种特殊的迭代器，可以使用函数的方式来创建。生成器使用`yield`关键字返回值，每次调用`next()`时会执行到下一个`yield`语句。

### 1.1 生成器函数

```python
def fibonacci(n):
    """生成斐波那契数列"""
    a, b = 0, 1
    for _ in range(n):
        yield a
        a, b = b, a + b

# 使用生成器
for num in fibonacci(10):
    print(num)
```

### 1.2 生成器表达式

生成器表达式类似于列表推导式，但使用圆括号。

```python
# 列表推导式（立即生成所有元素）
squares_list = [x**2 for x in range(10)]

# 生成器表达式（按需生成元素）
squares_gen = (x**2 for x in range(10))
for square in squares_gen:
    print(square)
```

### 1.3 生成器的优势

1. **内存效率**：生成器按需生成元素，不需要一次性生成所有元素
2. **惰性求值**：只有在需要时才计算下一个值
3. **适合大数据**：处理大量数据时节省内存

## 2. 迭代器（Iterator）

迭代器是实现了迭代器协议的对象，可以使用`iter()`函数和`next()`函数进行操作。

### 2.1 迭代器协议

一个对象要实现迭代器协议，需要实现`__iter__()`和`__next__()`方法。

```python
class CountDown:
    """倒计时迭代器"""
    
    def __init__(self, start):
        self.current = start
    
    def __iter__(self):
        return self
    
    def __next__(self):
        if self.current <= 0:
            raise StopIteration
        self.current -= 1
        return self.current + 1

# 使用迭代器
counter = CountDown(5)
for num in counter:
    print(num)  # 5, 4, 3, 2, 1
```

### 2.2 可迭代对象

实现了`__iter__()`方法的对象是可迭代对象，可以用于`for`循环。

```python
class MyRange:
    """自定义范围类"""
    
    def __init__(self, start, end):
        self.start = start
        self.end = end
    
    def __iter__(self):
        return iter(range(self.start, self.end))

# 使用可迭代对象
for num in MyRange(1, 5):
    print(num)  # 1, 2, 3, 4
```

## 3. 上下文管理器（Context Manager）

上下文管理器是实现了上下文管理器协议的对象，可以使用`with`语句。

### 3.1 __enter__和__exit__方法

```python
class FileManager:
    """文件管理器"""
    
    def __init__(self, filename, mode):
        self.filename = filename
        self.mode = mode
        self.file = None
    
    def __enter__(self):
        self.file = open(self.filename, self.mode)
        return self.file
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.file:
            self.file.close()
        return False  # 不抑制异常

# 使用上下文管理器
with FileManager('test.txt', 'w') as f:
    f.write('Hello, World!')
```

### 3.2 contextlib模块

使用`contextlib.contextmanager`装饰器可以更方便地创建上下文管理器。

```python
from contextlib import contextmanager

@contextmanager
def file_manager(filename, mode):
    """文件管理器（使用contextmanager装饰器）"""
    file = open(filename, mode)
    try:
        yield file
    finally:
        file.close()

# 使用上下文管理器
with file_manager('test.txt', 'w') as f:
    f.write('Hello, World!')
```

## 4. 装饰器进阶

### 4.1 参数化装饰器

装饰器可以接受参数，返回一个装饰器函数。

```python
from functools import wraps
from time import time

def record(output):
    """可以参数化的装饰器"""
    
    def decorate(func):
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            start = time()
            result = func(*args, **kwargs)
            output(func.__name__, time() - start)
            return result
            
        return wrapper
    
    return decorate

# 使用参数化装饰器
def log(name, elapsed):
    print(f'{name}执行了{elapsed:.2f}秒')

@record(log)
def my_function():
    pass
```

### 4.2 类装饰器

可以使用类来实现装饰器。

```python
from functools import wraps
from time import time

class Record:
    """通过定义类的方式定义装饰器"""

    def __init__(self, output):
        self.output = output

    def __call__(self, func):

        @wraps(func)
        def wrapper(*args, **kwargs):
            start = time()
            result = func(*args, **kwargs)
            self.output(func.__name__, time() - start)
            return result

        return wrapper

@Record(log)
def my_function():
    pass
```

### 4.3 装饰器实现单例模式

```python
from functools import wraps

def singleton(cls):
    """装饰类的装饰器"""
    instances = {}

    @wraps(cls)
    def wrapper(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    return wrapper

@singleton
class President:
    """总统(单例类)"""
    pass
```

### 4.4 线程安全的单例装饰器

```python
from functools import wraps
from threading import RLock

def singleton(cls):
    """线程安全的单例装饰器"""
    instances = {}
    locker = RLock()

    @wraps(cls)
    def wrapper(*args, **kwargs):
        if cls not in instances:
            with locker:
                if cls not in instances:
                    instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    return wrapper
```

## 5. 闭包（Closure）

闭包是指在一个函数内部定义的函数，它可以访问外部函数的变量。

### 5.1 闭包示例

```python
def outer_func(x):
    """外部函数"""
    
    def inner_func(y):
        """内部函数（闭包）"""
        return x + y
    
    return inner_func

# 创建闭包
closure = outer_func(10)
print(closure(5))  # 15
```

### 5.2 闭包的应用

```python
def make_multiplier(n):
    """创建一个乘法函数"""
    def multiplier(x):
        return x * n
    return multiplier

# 创建不同的乘法函数
double = make_multiplier(2)
triple = make_multiplier(3)

print(double(5))  # 10
print(triple(5))  # 15
```

## 6. 作用域和命名空间

### 6.1 LEGB规则

Python 搜索变量的顺序：
- **L**ocal（局部作用域）
- **E**nclosed（嵌套作用域）
- **G**lobal（全局作用域）
- **B**uilt-in（内置作用域）

### 6.2 global和nonlocal关键字

```python
x = 100  # 全局变量

def outer():
    y = 200  # 嵌套作用域变量
    
    def inner():
        global x
        nonlocal y
        x = 300  # 修改全局变量
        y = 400  # 修改嵌套作用域变量
    
    inner()
    print(y)  # 400

outer()
print(x)  # 300
```

## 7. 元类（Metaclass）

元类是创建类的类，Python 中一切都是对象，类也是对象。

### 7.1 使用type创建类

```python
# 使用type动态创建类
MyClass = type('MyClass', (object,), {'x': 100})

obj = MyClass()
print(obj.x)  # 100
```

### 7.2 自定义元类

```python
class MyMeta(type):
    """自定义元类"""
    
    def __new__(mcs, name, bases, namespace):
        namespace['created_by'] = 'MyMeta'
        return super().__new__(mcs, name, bases, namespace)

class MyClass(metaclass=MyMeta):
    pass

print(MyClass.created_by)  # MyMeta
```

## 8. 抽象基类（ABC）

抽象基类用于定义接口，不能直接实例化。

### 8.1 使用ABC定义抽象类

```python
from abc import ABCMeta, abstractmethod

class Employee(metaclass=ABCMeta):
    """员工(抽象类)"""

    def __init__(self, name):
        self.name = name

    @abstractmethod
    def get_salary(self):
        """结算月薪(抽象方法)"""
        pass

class Manager(Employee):
    """部门经理"""

    def get_salary(self):
        return 15000.0

# employee = Employee('张三')  # TypeError: Can't instantiate abstract class
manager = Manager('李四')
print(manager.get_salary())  # 15000.0
```

## 9. 描述符（Descriptor）

描述符是一个实现了`__get__`、`__set__`或`__delete__`方法的类。

### 9.1 属性描述符

```python
class Descriptor:
    """属性描述符"""
    
    def __init__(self, name):
        self.name = name
    
    def __get__(self, instance, owner):
        print(f'Getting {self.name}')
        return instance.__dict__[self.name]
    
    def __set__(self, instance, value):
        print(f'Setting {self.name} to {value}')
        instance.__dict__[self.name] = value

class MyClass:
    x = Descriptor('x')
    y = Descriptor('y')

obj = MyClass()
obj.x = 100  # Setting x to 100
print(obj.x)  # Getting x, 100
```

## 10. 协程（Coroutine）

协程是一种轻量级的线程，可以在函数执行过程中暂停和恢复。

### 10.1 使用yield实现协程

```python
def coroutine():
    """简单的协程示例"""
    while True:
        value = yield
        print(f'Received: {value}')

# 创建协程
co = coroutine()
next(co)  # 启动协程
co.send('Hello')  # Received: Hello
co.send('World')  # Received: World
```

### 10.2 async/await（Python 3.5+）

```python
import asyncio

async def async_function():
    """异步函数"""
    print('开始执行')
    await asyncio.sleep(1)
    print('执行完成')

# 运行异步函数
asyncio.run(async_function())
```

## 11. 数据类（Dataclass，Python 3.7+）

数据类是一个装饰器，可以自动生成`__init__`、`__repr__`等方法。

```python
from dataclasses import dataclass

@dataclass
class Point:
    x: float
    y: float
    
    def distance_to_origin(self):
        return (self.x**2 + self.y**2)**0.5

p = Point(3.0, 4.0)
print(p)  # Point(x=3.0, y=4.0)
print(p.distance_to_origin())  # 5.0
```

## 12. 类型提示（Type Hints）

Python 3.5+ 支持类型提示，提高代码可读性和IDE支持。

```python
from typing import List, Dict, Optional

def greet(name: str) -> str:
    """类型提示示例"""
    return f'Hello, {name}!'

def process_items(items: List[int]) -> Dict[str, int]:
    """处理列表并返回字典"""
    return {'count': len(items), 'sum': sum(items)}

def find_user(user_id: int) -> Optional[str]:
    """可能返回None的函数"""
    if user_id > 0:
        return f'User_{user_id}'
    return None
```

## 13. 枚举（Enum）

枚举用于定义常量集合。

```python
from enum import Enum

class Color(Enum):
    RED = 1
    GREEN = 2
    BLUE = 3

print(Color.RED)      # Color.RED
print(Color.RED.name) # RED
print(Color.RED.value) # 1
```

## 14. 总结

Python 提供了许多高级特性，包括生成器、迭代器、上下文管理器、装饰器、闭包、元类等。这些特性让 Python 代码更加优雅、高效和灵活。掌握这些高级特性可以帮助你写出更专业的 Python 代码。

