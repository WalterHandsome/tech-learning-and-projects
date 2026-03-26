# HTTP 协议与缓存策略

## 1. HTTP 版本对比

| 特性 | HTTP/1.1 | HTTP/2 | HTTP/3 |
|------|---------|--------|--------|
| 传输层 | TCP | TCP | QUIC (UDP) |
| 多路复用 | 否（队头阻塞） | 是 | 是 |
| 头部压缩 | 否 | HPACK | QPACK |
| 服务器推送 | 否 | 是 | 否 |
| 连接建立 | TCP + TLS | TCP + TLS | 0-RTT / 1-RTT |

## 2. HTTPS / TLS

```
客户端                    服务器
  │── ClientHello ──────────>│  （支持的加密套件）
  │<── ServerHello ──────────│  （选择的加密套件 + 证书）
  │── 验证证书 + 密钥交换 ──>│
  │<── 完成握手 ─────────────│
  │<══ 加密通信 ════════════>│
```

## 3. 缓存策略

### 3.1 强缓存（不发请求）

```
Cache-Control: max-age=31536000    # 缓存1年
Cache-Control: no-cache            # 每次都协商
Cache-Control: no-store            # 不缓存
Cache-Control: private             # 仅浏览器缓存
Cache-Control: public              # 允许CDN缓存

Expires: Thu, 01 Jan 2026 00:00:00 GMT  # 过期时间（优先级低于 Cache-Control）
```

### 3.2 协商缓存（发请求验证）

```
# 基于修改时间
Last-Modified: Wed, 01 Jan 2025 00:00:00 GMT  # 响应头
If-Modified-Since: Wed, 01 Jan 2025 00:00:00 GMT  # 请求头
# 返回 304 Not Modified 或 200 + 新内容

# 基于内容哈希（更精确）
ETag: "abc123"                    # 响应头
If-None-Match: "abc123"           # 请求头
```

### 3.3 缓存策略实践

```
# 静态资源（带哈希的文件名）
Cache-Control: max-age=31536000, immutable
# 例：app.a1b2c3.js, style.d4e5f6.css

# HTML 文件
Cache-Control: no-cache
# 每次协商，确保获取最新版本

# API 响应
Cache-Control: no-store
# 或 Cache-Control: max-age=60（短时间缓存）
```

## 4. Service Worker 缓存

```javascript
// sw.js
const CACHE_NAME = 'v1';
const ASSETS = ['/', '/index.html', '/style.css', '/app.js'];

// 安装：预缓存资源
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache => cache.addAll(ASSETS))
  );
});

// 请求拦截：缓存优先策略
self.addEventListener('fetch', (event) => {
  event.respondWith(
    caches.match(event.request).then(cached => {
      return cached || fetch(event.request).then(response => {
        const clone = response.clone();
        caches.open(CACHE_NAME).then(cache => cache.put(event.request, clone));
        return response;
      });
    })
  );
});
```

## 5. 常见状态码

```
200 OK                    # 成功
201 Created               # 创建成功
204 No Content            # 成功但无内容
301 Moved Permanently     # 永久重定向
302 Found                 # 临时重定向
304 Not Modified          # 协商缓存命中
400 Bad Request           # 请求参数错误
401 Unauthorized          # 未认证
403 Forbidden             # 无权限
404 Not Found             # 资源不存在
429 Too Many Requests     # 限流
500 Internal Server Error # 服务器错误
502 Bad Gateway           # 网关错误
503 Service Unavailable   # 服务不可用
```
