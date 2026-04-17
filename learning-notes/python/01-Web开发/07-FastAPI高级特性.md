# FastAPI 高级特性
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

> FastAPI 的高级功能和最佳实践

## 1. 依赖注入系统

### 1.1 基础依赖注入

```python
from fastapi import Depends, FastAPI

app = FastAPI()

def get_db():
    db = "database_connection"
    try:
        yield db
    finally:
        # 清理资源
        print("关闭数据库连接")

@app.get("/items/")
async def read_items(db = Depends(get_db)):
    return {"db": db}
```

### 1.2 类依赖

```python
class Database:
    def __init__(self):
        self.connection = "connected"
    
    def query(self, sql: str):
        return f"执行: {sql}"

def get_database():
    return Database()

@app.get("/query/")
async def query_data(db: Database = Depends(get_database)):
    return db.query("SELECT * FROM users")
```

### 1.3 嵌套依赖

```python
def get_query_params(q: str = None, skip: int = 0, limit: int = 10):
    return {"q": q, "skip": skip, "limit": limit}

def get_db():
    return "db_connection"

@app.get("/items/")
async def read_items(
    params: dict = Depends(get_query_params),
    db: str = Depends(get_db)
):
    return {"params": params, "db": db}
```

### 1.4 依赖覆盖

```python
from fastapi.testclient import TestClient

def override_get_db():
    return "test_db"

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)
```

## 2. 中间件

### 2.1 自定义中间件

```python
import time
from fastapi import Request

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response
```

### 2.2 CORS 中间件

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

### 2.3 认证中间件

```python
from fastapi import HTTPException, status

async def verify_token(request: Request):
    token = request.headers.get("Authorization")
    if not token or not token.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证令牌"
        )
    return token.replace("Bearer ", "")

@app.middleware("http")
async def auth_middleware(request: Request, call_next):
    if request.url.path.startswith("/api/"):
        await verify_token(request)
    response = await call_next(request)
    return response
```

## 3. 路由和APIRouter

### 3.1 APIRouter 使用

```python
from fastapi import APIRouter

router = APIRouter(prefix="/api/v1", tags=["users"])

@router.get("/users/")
async def get_users():
    return [{"id": 1, "name": "Alice"}]

@router.post("/users/")
async def create_user(user: dict):
    return {"id": 2, **user}

app.include_router(router)
```

### 3.2 路由前缀和标签

```python
api_router = APIRouter(prefix="/api", tags=["API"])
v1_router = APIRouter(prefix="/v1", tags=["v1"])

@v1_router.get("/items/")
async def get_items():
    return []

api_router.include_router(v1_router)
app.include_router(api_router)
```

## 4. 请求验证和序列化

### 4.1 Pydantic 模型

```python
from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime

class User(BaseModel):
    id: int
    name: str = Field(..., min_length=1, max_length=50)
    email: str = Field(..., regex=r'^[\w\.-]+@[\w\.-]+\.\w+$')
    age: Optional[int] = Field(None, ge=0, le=120)
    tags: List[str] = []
    created_at: datetime = Field(default_factory=datetime.now)
    
    @validator('name')
    def name_must_not_be_empty(cls, v):
        if not v.strip():
            raise ValueError('名称不能为空')
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "id": 1,
                "name": "Alice",
                "email": "alice@example.com",
                "age": 25
            }
        }
```

### 4.2 响应模型

```python
class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    
    class Config:
        orm_mode = True

@app.get("/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: int):
    # 返回完整User对象，但只序列化UserResponse字段
    return User(id=user_id, name="Alice", email="alice@example.com", age=25)
```

## 5. 异常处理

### 5.1 自定义异常

```python
from fastapi import HTTPException, status

class UserNotFoundError(HTTPException):
    def __init__(self, user_id: int):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"用户 {user_id} 不存在"
        )

@app.get("/users/{user_id}")
async def get_user(user_id: int):
    if user_id > 100:
        raise UserNotFoundError(user_id)
    return {"id": user_id, "name": "Alice"}
```

### 5.2 全局异常处理

```python
from fastapi import Request
from fastapi.responses import JSONResponse

@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    return JSONResponse(
        status_code=400,
        content={"message": str(exc)}
    )

@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    return JSONResponse(
        status_code=404,
        content={"message": "资源不存在"}
    )
```

## 6. 后台任务

### 6.1 BackgroundTasks

```python
from fastapi import BackgroundTasks

def send_email(email: str, message: str):
    print(f"发送邮件到 {email}: {message}")

@app.post("/send-notification/")
async def send_notification(
    email: str,
    message: str,
    background_tasks: BackgroundTasks
):
    background_tasks.add_task(send_email, email, message)
    return {"message": "通知已加入队列"}
```

### 6.2 使用 Celery

```python
from celery import Celery

celery_app = Celery('tasks', broker='redis://localhost:6379')

@celery_app.task
def process_data(data: dict):
    # 处理数据
    return {"processed": True}

@app.post("/process/")
async def process(data: dict):
    task = process_data.delay(data)
    return {"task_id": task.id}
```

## 7. WebSocket 高级用法

### 7.1 WebSocket 连接管理

```python
from fastapi import WebSocket, WebSocketDisconnect
from typing import List

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
    
    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
    
    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)
    
    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: int):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.send_personal_message(f"Echo: {data}", websocket)
            await manager.broadcast(f"Client {client_id}: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
```

## 8. 文件上传和下载

### 8.1 文件上传

```python
from fastapi import UploadFile, File
import shutil

@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    with open(f"uploads/{file.filename}", "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return {"filename": file.filename, "size": file.size}
```

### 8.2 多文件上传

```python
@app.post("/upload-multiple/")
async def upload_files(files: List[UploadFile] = File(...)):
    filenames = []
    for file in files:
        with open(f"uploads/{file.filename}", "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        filenames.append(file.filename)
    return {"uploaded": filenames}
```

### 8.3 文件下载

```python
from fastapi.responses import FileResponse

@app.get("/download/{filename}")
async def download_file(filename: str):
    return FileResponse(
        f"uploads/{filename}",
        media_type="application/octet-stream",
        filename=filename
    )
```

## 9. 数据库集成

### 9.1 SQLAlchemy 集成

```python
from sqlalchemy.orm import Session
from database import SessionLocal

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/users/")
async def get_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    return users
```

### 9.2 数据库迁移

```python
# 使用 Alembic
# alembic init alembic
# alembic revision --autogenerate -m "create users table"
# alembic upgrade head
```

## 10. 缓存

### 10.1 Redis 缓存

```python
import redis
from functools import wraps

redis_client = redis.Redis(host='localhost', port=6379, db=0)

def cache_result(expiration: int = 300):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            cache_key = f"{func.__name__}:{args}:{kwargs}"
            cached = redis_client.get(cache_key)
            if cached:
                return json.loads(cached)
            result = await func(*args, **kwargs)
            redis_client.setex(cache_key, expiration, json.dumps(result))
            return result
        return wrapper
    return decorator

@app.get("/expensive-operation/")
@cache_result(expiration=600)
async def expensive_operation():
    # 耗时操作
    await asyncio.sleep(2)
    return {"result": "data"}
```

## 11. 限流

### 11.1 使用 slowapi

```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.get("/api/data/")
@limiter.limit("10/minute")
async def get_data(request: Request):
    return {"data": "..."}
```

## 12. 测试

### 12.1 使用 TestClient

```python
from fastapi.testclient import TestClient

client = TestClient(app)

def test_read_users():
    response = client.get("/users/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_create_user():
    response = client.post(
        "/users/",
        json={"name": "Bob", "email": "bob@example.com"}
    )
    assert response.status_code == 201
    assert response.json()["name"] == "Bob"
```

## 13. 最佳实践

### 13.1 项目结构

```
project/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes.py
│   ├── core/
│   │   ├── config.py
│   │   └── security.py
│   ├── models/
│   │   └── user.py
│   └── schemas/
│       └── user.py
├── tests/
└── requirements.txt
```

### 13.2 配置管理

> 🔄 更新于 2026-04-18：Pydantic v2 使用 `model_config` 替代 `class Config`，`BaseSettings` 移至 `pydantic-settings` 包

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "My API"
    database_url: str
    secret_key: str
    
    model_config = {"env_file": ".env"}

settings = Settings()
```

## 14. 总结

FastAPI 高级特性包括：
- **依赖注入**：灵活的资源管理
- **中间件**：请求/响应处理
- **路由组织**：APIRouter 模块化
- **数据验证**：Pydantic 模型
- **异常处理**：统一错误处理
- **后台任务**：异步任务处理
- **WebSocket**：实时通信
- **文件处理**：上传下载
- **数据库集成**：ORM 支持
- **缓存和限流**：性能优化
- **测试**：TestClient 测试

通过这些高级特性，可以构建生产级的 FastAPI 应用。

