# HTTP服务器开发
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

> 使用 Python 构建高性能 HTTP 服务器

## 1. 使用 http.server（基础）

### 1.1 简单HTTP服务器

```python
from http.server import HTTPServer, BaseHTTPRequestHandler

class MyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(b'<h1>Hello, World!</h1>')
    
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(b'{"status": "ok"}')

server = HTTPServer(('localhost', 8000), MyHandler)
server.serve_forever()
```

## 2. 使用 Flask 构建 RESTful API

### 2.1 基础API

```python
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/api/users', methods=['GET'])
def get_users():
    users = [{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}]
    return jsonify(users)

@app.route('/api/users', methods=['POST'])
def create_user():
    data = request.json
    # 创建用户逻辑
    return jsonify({"id": 3, **data}), 201

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
```

### 2.2 蓝图和模块化

```python
from flask import Blueprint

api = Blueprint('api', __name__, url_prefix='/api')

@api.route('/users')
def get_users():
    return jsonify({"users": []})

app.register_blueprint(api)
```

## 3. 使用 FastAPI 构建现代API

### 3.1 基础API

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

class User(BaseModel):
    name: str
    email: str

@app.get("/api/users")
async def get_users():
    return [{"id": 1, "name": "Alice"}]

@app.post("/api/users")
async def create_user(user: User):
    return {"id": 2, **user.dict()}
```

### 3.2 依赖注入

```python
from fastapi import Depends

def get_db():
    # 数据库连接
    db = "connection"
    yield db
    # 清理

@app.get("/api/users")
async def get_users(db = Depends(get_db)):
    return {"users": []}
```

## 4. 使用 aiohttp 构建异步服务器

### 4.1 异步HTTP服务器

```python
from aiohttp import web
import aiohttp

async def handle(request):
    return web.json_response({"message": "Hello"})

async def handle_post(request):
    data = await request.json()
    return web.json_response({"received": data})

app = web.Application()
app.router.add_get('/', handle)
app.router.add_post('/api/data', handle_post)

web.run_app(app, host='0.0.0.0', port=8080)
```

### 4.2 中间件

```python
@web.middleware
async def auth_middleware(request, handler):
    token = request.headers.get('Authorization')
    if not token:
        return web.json_response({"error": "Unauthorized"}, status=401)
    return await handler(request)

app.middlewares.append(auth_middleware)
```

## 5. 使用 Tornado 构建高性能服务器

### 5.1 Tornado 服务器

```python
import tornado.ioloop
import tornado.web

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write({"message": "Hello"})
    
    def post(self):
        data = tornado.escape.json_decode(self.request.body)
        self.write({"received": data})

def make_app():
    return tornado.web.Application([
        (r"/", MainHandler),
    ])

if __name__ == "__main__":
    app = make_app()
    app.listen(8888)
    tornado.ioloop.IOLoop.current().start()
```

## 6. WebSocket 服务器

### 6.1 FastAPI WebSocket

```python
from fastapi import WebSocket

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        await websocket.send_text(f"Echo: {data}")
```

### 6.2 aiohttp WebSocket

```python
async def websocket_handler(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)
    
    async for msg in ws:
        if msg.type == aiohttp.WSMsgType.TEXT:
            await ws.send_str(f"Echo: {msg.data}")
        elif msg.type == aiohttp.WSMsgType.ERROR:
            break
    
    return ws

app.router.add_get('/ws', websocket_handler)
```

## 7. 性能优化

### 7.1 连接池

```python
import aiohttp

async def fetch_with_pool():
    connector = aiohttp.TCPConnector(limit=100)
    async with aiohttp.ClientSession(connector=connector) as session:
        async with session.get('https://example.com') as response:
            return await response.text()
```

### 7.2 异步处理

```python
from concurrent.futures import ThreadPoolExecutor

executor = ThreadPoolExecutor(max_workers=10)

@app.post("/api/process")
async def process_data(data: dict):
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(
        executor,
        cpu_intensive_task,
        data
    )
    return {"result": result}
```

## 8. 安全实践

### 8.1 CORS 配置

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://example.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 8.2 限流

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.get("/api/data")
@limiter.limit("10/minute")
async def get_data(request: Request):
    return {"data": "..."}
```

## 9. 总结

HTTP服务器开发要点：
- **框架选择**：Flask（简单）、FastAPI（现代）、aiohttp（异步）
- **异步处理**：提高并发性能
- **中间件**：统一处理逻辑
- **WebSocket**：实时通信
- **性能优化**：连接池、异步处理
- **安全实践**：CORS、限流、认证

