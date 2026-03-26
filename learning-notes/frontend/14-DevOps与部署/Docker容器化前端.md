# Docker 容器化前端

## 1. 多阶段构建

```dockerfile
# 阶段1：构建
FROM node:20-alpine AS builder
WORKDIR /app
COPY package.json pnpm-lock.yaml ./
RUN corepack enable && pnpm install --frozen-lockfile
COPY . .
RUN pnpm build

# 阶段2：运行
FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

## 2. nginx.conf

```nginx
server {
    listen 80;
    root /usr/share/nginx/html;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location ~* \.(js|css|png|jpg|svg|woff2)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    gzip on;
    gzip_types text/plain text/css application/json application/javascript image/svg+xml;
}
```

## 3. Docker Compose

```yaml
# docker-compose.yml
version: '3.8'
services:
  web:
    build: .
    ports:
      - "80:80"
    environment:
      - VITE_API_URL=http://api:8080
    depends_on:
      - api
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost"]
      interval: 30s
      timeout: 10s
      retries: 3

  api:
    image: my-api:latest
    ports:
      - "8080:8080"
    environment:
      - DATABASE_URL=postgresql://db:5432/mydb
```

## 4. 环境变量注入

```bash
# 构建时注入
docker build --build-arg VITE_API_URL=https://api.example.com -t my-app .

# 运行时注入（需要特殊处理，因为前端是静态文件）
# 方案：使用 entrypoint 脚本替换占位符
```

```bash
#!/bin/sh
# entrypoint.sh
# 将环境变量注入到 JS 文件中
envsubst < /usr/share/nginx/html/env-config.template.js > /usr/share/nginx/html/env-config.js
nginx -g "daemon off;"
```

## 5. 镜像优化

```
优化策略：
1. 使用 alpine 基础镜像（更小）
2. 多阶段构建（只保留产物）
3. .dockerignore 排除不需要的文件
4. 合理利用构建缓存（先 COPY package.json）
```

```
# .dockerignore
node_modules
dist
.git
*.md
.env*
```
