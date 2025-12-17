# FastAPI 快速入门

> 从 private-notes 提取的技术学习笔记

## FastAPI 简介

FastAPI 是一个现代、快速的 Web 框架，用于构建 API，基于 Python 3.6+ 的类型提示。

## 核心特性

- **高性能**：与 NodeJS 和 Go 相当
- **快速开发**：开发速度提升约 200% 到 300%
- **类型提示**：基于 Python 类型提示
- **自动文档**：自动生成 OpenAPI 和 Swagger 文档
- **异步支持**：原生支持 async/await

## 快速开始

### 安装

```bash
pip install fastapi uvicorn
```

### 基本示例

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/items/{item_id}")
async def read_item(item_id: int):
    return {"item_id": item_id}
```

### 运行

```bash
uvicorn main:app --reload
```

## 核心功能

### 1. 路径参数

```python
@app.get("/items/{item_id}")
async def read_item(item_id: int):
    return {"item_id": item_id}
```

### 2. 查询参数

```python
@app.get("/items/")
async def read_items(skip: int = 0, limit: int = 10):
    return {"skip": skip, "limit": limit}
```

### 3. 请求体

```python
from pydantic import BaseModel

class Item(BaseModel):
    name: str
    price: float

@app.post("/items/")
async def create_item(item: Item):
    return item
```

### 4. WebSocket

```python
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        await websocket.send_text(f"Message: {data}")
```

## 最佳实践

1. **使用类型提示**：提高代码可读性和 IDE 支持
2. **依赖注入**：使用 Depends 管理依赖
3. **异常处理**：统一异常处理
4. **中间件**：CORS、日志等
5. **测试**：使用 TestClient 进行测试

## 参考资料

- [FastAPI 官方文档](https://fastapi.tiangolo.com/)
- [FastAPI 中文文档](https://fastapi.tiangolo.com/zh/)

