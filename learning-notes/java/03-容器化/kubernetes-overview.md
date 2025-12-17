# Kubernetes 概述

> 从 private-notes 提取的技术学习笔记

## Kubernetes 简介

Kubernetes（K8s）是一个开源的容器编排平台，用于自动化部署、扩展和管理容器化应用程序。

## 应用部署方式演变

1. **传统部署**：直接部署在物理机
2. **虚拟化部署**：虚拟机环境
3. **容器化部署**：Docker 容器

## Kubernetes 核心功能

- **自我修复**：容器崩溃时自动重启
- **弹性伸缩**：根据负载自动调整容器数量
- **服务发现**：自动发现依赖服务
- **负载均衡**：自动实现请求负载均衡
- **版本回退**：支持版本回滚
- **存储编排**：自动创建存储卷

## 核心组件

### Master 节点

- **ApiServer**：资源操作的唯一入口
- **Scheduler**：负责集群资源调度
- **ControllerManager**：维护集群状态
- **Etcd**：存储集群资源对象信息

### Node 节点

- **Kubelet**：维护容器的生命周期
- **KubeProxy**：服务发现和负载均衡
- **Docker**：容器运行时

## 核心概念

- **Pod**：最小的部署单元
- **Service**：服务发现和负载均衡
- **Deployment**：管理 Pod 的副本
- **Namespace**：资源隔离
- **ConfigMap**：配置管理
- **Secret**：敏感信息管理

## 常用命令

```bash
# 查看资源
kubectl get pods
kubectl get services
kubectl get deployments

# 创建资源
kubectl apply -f <yaml-file>

# 删除资源
kubectl delete -f <yaml-file>

# 查看日志
kubectl logs <pod-name>

# 进入容器
kubectl exec -it <pod-name> -- /bin/bash
```

## 参考资料

- [Kubernetes 官方文档](https://kubernetes.io/docs/)
- [Kubernetes 中文文档](https://kubernetes.io/zh-cn/docs/)

