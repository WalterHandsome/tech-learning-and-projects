# Docker 基础与实践

> 从 private-notes 提取的技术学习笔记

## Docker 简介

Docker 是一个开源的应用容器引擎，让开发者可以打包他们的应用以及依赖包到一个可移植的镜像中。

## 核心概念

### 1. 镜像（Image）

镜像是一个只读的模板，用于创建容器。

### 2. 容器（Container）

容器是镜像的运行实例，可以被创建、启动、停止、删除。

### 3. 仓库（Repository）

仓库是集中存放镜像的地方。

## Docker 解决的问题

### 依赖兼容问题

- 将应用的 Libs、Deps、配置与应用一起打包
- 将每个应用放到一个隔离容器去运行

### 操作系统环境差异

- 共享操作系统内核
- 每个容器拥有自己的文件系统、CPU、内存、进程空间

## 常用命令

```bash
# 镜像操作
docker images              # 查看镜像
docker pull <image>        # 拉取镜像
docker build -t <name> .  # 构建镜像
docker rmi <image>         # 删除镜像

# 容器操作
docker ps                  # 查看运行中的容器
docker ps -a               # 查看所有容器
docker run <image>         # 运行容器
docker stop <container>    # 停止容器
docker rm <container>      # 删除容器

# Docker Compose
docker-compose up          # 启动服务
docker-compose down        # 停止服务
docker-compose ps          # 查看服务状态
```

## Dockerfile 示例

```dockerfile
FROM openjdk:17-jre-slim
WORKDIR /app
COPY target/*.jar app.jar
EXPOSE 8080
ENTRYPOINT ["java", "-jar", "app.jar"]
```

## 最佳实践

1. **多阶段构建**：减小镜像大小
2. **使用 .dockerignore**：排除不需要的文件
3. **非 root 用户运行**：提高安全性
4. **健康检查**：添加 HEALTHCHECK
5. **合理使用缓存**：优化构建速度

## 参考资料

- [Docker 官方文档](https://docs.docker.com/)
- [Docker 最佳实践](https://docs.docker.com/develop/dev-best-practices/)

