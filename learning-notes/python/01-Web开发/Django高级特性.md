# Django 高级特性

> Django 框架的高级功能和最佳实践

## 1. Django 中间件

### 1.1 自定义中间件

```python
# middleware.py
class CustomMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # 请求处理前
        print(f"请求路径: {request.path}")
        
        response = self.get_response(request)
        
        # 响应处理后
        response['X-Custom-Header'] = 'Custom Value'
        return response
```

### 1.2 中间件注册

```python
# settings.py
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'myapp.middleware.CustomMiddleware',
    # ...
]
```

## 2. Django 信号

### 2.1 内置信号

```python
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver

@receiver(pre_save, sender=User)
def user_pre_save(sender, instance, **kwargs):
    print(f"保存前: {instance.username}")

@receiver(post_save, sender=User)
def user_post_save(sender, instance, created, **kwargs):
    if created:
        print(f"新用户创建: {instance.username}")
    else:
        print(f"用户更新: {instance.username}")
```

### 2.2 自定义信号

```python
from django.dispatch import Signal

order_created = Signal(providing_args=["order", "user"])

# 发送信号
order_created.send(sender=self.__class__, order=order, user=user)

# 接收信号
@receiver(order_created)
def handle_order_created(sender, order, user, **kwargs):
    print(f"订单创建: {order.id} by {user.username}")
```

## 3. Django 缓存

### 3.1 缓存配置

```python
# settings.py
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
    }
}
```

### 3.2 缓存使用

```python
from django.core.cache import cache

# 设置缓存
cache.set('key', 'value', timeout=300)

# 获取缓存
value = cache.get('key')

# 删除缓存
cache.delete('key')

# 装饰器缓存
from django.views.decorators.cache import cache_page

@cache_page(60 * 15)  # 缓存15分钟
def my_view(request):
    return HttpResponse("Hello")
```

## 4. Django REST Framework

### 4.1 序列化器

```python
from rest_framework import serializers

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']
        read_only_fields = ['id']
    
    def validate_email(self, value):
        if not value.endswith('@example.com'):
            raise serializers.ValidationError("邮箱格式不正确")
        return value
```

### 4.2 视图集

```python
from rest_framework import viewsets
from rest_framework.decorators import action

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    
    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        user = self.get_object()
        user.is_active = True
        user.save()
        return Response({'status': 'activated'})
```

## 5. Django 管理后台

### 5.1 自定义Admin

```python
from django.contrib import admin

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['username', 'email', 'is_active', 'date_joined']
    list_filter = ['is_active', 'date_joined']
    search_fields = ['username', 'email']
    readonly_fields = ['date_joined']
    
    fieldsets = (
        ('基本信息', {
            'fields': ('username', 'email')
        }),
        ('权限', {
            'fields': ('is_active', 'is_staff')
        }),
    )
```

## 6. Django 任务队列

### 6.1 Celery 集成

```python
# tasks.py
from celery import shared_task

@shared_task
def send_email_task(user_id, message):
    user = User.objects.get(id=user_id)
    send_mail(
        '通知',
        message,
        'from@example.com',
        [user.email],
    )
```

## 7. 总结

Django高级特性要点：
- **中间件**：请求/响应处理、自定义中间件
- **信号**：模型信号、自定义信号
- **缓存**：Redis缓存、视图缓存、装饰器缓存
- **DRF**：序列化器、视图集、权限控制
- **管理后台**：自定义Admin、列表显示、过滤器
- **任务队列**：Celery异步任务

这些特性提高Django应用的性能和可维护性。

