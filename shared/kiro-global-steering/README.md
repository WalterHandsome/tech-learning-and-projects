---
inclusion: manual
---

# Kiro 全局 Steering 配置

> 本目录通过软链接挂载到 `~/.kiro/steering/`，实现全局 steering 的 git 版本管理。

## 工作原理

```
~/.kiro/steering/ → 软链接 → 本目录 (shared/kiro-global-steering/)
```

修改本目录中的文件 = 修改全局 steering，同时变更会被 git 追踪。

## 文件说明

| 文件 | 用途 |
|------|------|
| `language-chinese.md` | 强制 Kiro 使用中文交流 |
| `work-methodology.md` | 通用编码行为准则（先想再写、最小必要、精准改动、目标驱动、先读再写） |

## 新电脑 / 重新设置

如果在新电脑上克隆了本仓库，需要重新建立软链接：

```bash
# 删除默认的 steering 目录（如果有）
rm -rf ~/.kiro/steering

# 创建软链接（替换为你的实际仓库路径）
ln -s /path/to/tech-learning-and-projects/shared/kiro-global-steering ~/.kiro/steering
```
