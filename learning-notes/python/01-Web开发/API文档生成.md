# API 文档生成

> Python Web API 文档自动生成工具和最佳实践

## 1. FastAPI 自动文档

### 1.1 Swagger UI

```python
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="My API", version="1.0.0")

class User(BaseModel):
    id: int
    username: str
    email: str

@app.get("/users/{user_id}", response_model=User)
async def get_user(user_id: int):
    """获取用户信息"""
    return User(id=user_id, username="test", email="test@example.com")

# 自动生成文档
# 访问 http://localhost:8000/docs 查看 Swagger UI
# 访问 http://localhost:8000/redoc 查看 ReDoc
```

### 1.2 文档增强

```python
from fastapi import FastAPI, Query, Path
from typing import Optional

@app.get(
    "/users/{user_id}",
    summary="获取用户",
    description="根据用户ID获取用户详细信息",
    response_description="用户对象",
    tags=["用户管理"]
)
async def get_user(
    user_id: int = Path(..., description="用户ID", gt=0),
    include_email: bool = Query(False, description="是否包含邮箱")
):
    """获取用户信息"""
    pass
```

## 2. Django REST Framework 文档

### 2.1 CoreAPI 文档

```python
# settings.py
INSTALLED_APPS = [
    'rest_framework',
    'rest_framework.documentation',
]

# urls.py
from rest_framework.documentation import include_docs_urls

urlpatterns = [
    path('docs/', include_docs_urls(title='API Documentation')),
]
```

### 2.2 Schema 定义

```python
from rest_framework import serializers, viewsets
from rest_framework.schemas import AutoSchema

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    
    def get_schema_fields(self, view):
        return [
            coreapi.Field(
                name='username',
                required=True,
                location='form',
                description='用户名'
            )
        ]
```

## 3. Flask API 文档

### 3.1 Flask-RESTX

```python
from flask import Flask
from flask_restx import Api, Resource, fields

app = Flask(__name__)
api = Api(app, doc='/docs/')

user_model = api.model('User', {
    'id': fields.Integer(required=True, description='用户ID'),
    'username': fields.String(required=True, description='用户名'),
    'email': fields.String(required=True, description='邮箱')
})

@api.route('/users/<int:user_id>')
@api.doc(params={'user_id': '用户ID'})
class User(Resource):
    @api.doc('get_user')
    @api.marshal_with(user_model)
    def get(self, user_id):
        """获取用户信息"""
        return {'id': user_id, 'username': 'test'}
```

### 3.2 Flask-APIDoc

```python
from flask_apidoc import ApiDoc

app = Flask(__name__)
ApiDoc(app)

@app.route('/users/<int:user_id>')
def get_user(user_id):
    """
    获取用户信息
    
    Args:
        user_id: 用户ID
    
    Returns:
        dict: 用户信息
    """
    return {'id': user_id}
```

## 4. OpenAPI/Swagger 规范

### 4.1 手动编写 OpenAPI

```python
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

app = FastAPI()

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Custom API",
        version="1.0.0",
        description="自定义API文档",
        routes=app.routes,
    )
    # 自定义修改
    openapi_schema["info"]["x-logo"] = {
        "url": "https://fastapi.tiangolo.com/img/logo-margin/logo-teal.png"
    }
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi
```

## 5. Sphinx API 文档

### 5.1 配置 Sphinx

```python
# conf.py
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.viewcode',
]

# 生成文档
# sphinx-apidoc -o docs/ src/
# sphinx-build -b html docs/ docs/_build/
```

## 6. 文档最佳实践

### 6.1 文档规范

```python
from fastapi import FastAPI, Query
from typing import Optional

@app.get("/search")
async def search(
    q: str = Query(..., description="搜索关键词", min_length=1),
    limit: int = Query(10, ge=1, le=100, description="返回结果数量"),
    offset: int = Query(0, ge=0, description="偏移量")
):
    """
    搜索接口
    
    - **q**: 搜索关键词
    - **limit**: 返回结果数量（1-100）
    - **offset**: 偏移量
    
    返回搜索结果列表
    """
    pass
```

## 7. 总结

API文档生成要点：
- **FastAPI自动文档**：Swagger UI、ReDoc、文档增强
- **Django DRF文档**：CoreAPI、Schema定义
- **Flask文档**：Flask-RESTX、Flask-APIDoc
- **OpenAPI规范**：手动编写、自定义Schema
- **Sphinx文档**：自动生成、代码文档
- **文档最佳实践**：规范编写、参数说明

良好的API文档提高开发效率。

