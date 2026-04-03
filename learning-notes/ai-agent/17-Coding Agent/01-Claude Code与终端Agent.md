# Claude Code 与终端 Agent
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. Claude Code 概述

Claude Code 是 Anthropic 推出的终端原生 Agentic 编码工具。直接在终端中运行，能理解整个代码库、编辑文件、执行命令、操作 Git，无需离开命令行。

```
┌──────────────── Claude Code ────────────────┐
│                                              │
│  终端界面                                     │
│  ├─ 自然语言交互                              │
│  ├─ 代码库全局理解                            │
│  └─ 多文件编辑                                │
│                                              │
│  核心能力                                     │
│  ├─ 读取/搜索代码    ├─ 执行 Shell 命令       │
│  ├─ 编辑/创建文件    ├─ Git 工作流            │
│  ├─ MCP 工具扩展     └─ 多 Agent 并行         │
│                                              │
└──────────────────────────────────────────────┘
```

## 2. 基本使用

```bash
# 安装
npm install -g @anthropic-ai/claude-code

# 在项目目录启动
cd my-project
claude

# 直接传入任务（非交互模式）
claude "解释这个项目的架构"
claude "修复 src/auth.ts 中的登录 bug"
claude "为 UserService 类添加单元测试"

# 管道模式（用于 CI/CD）
echo "检查代码中的安全漏洞" | claude --pipe
```

## 3. 常用命令与模式

```bash
# 交互模式中的命令
> /help              # 查看帮助
> /compact            # 压缩上下文
> /clear              # 清除对话历史
> /model              # 切换模型
> /mcp                # 管理 MCP 工具
> /cost               # 查看 Token 用量

# 常见使用模式
> 阅读 src/ 目录，解释项目架构
> 找到所有使用 deprecated API 的地方并更新
> 创建一个 PR，修复 issue #42
> 运行测试，修复失败的用例
> 重构 database 模块，使用连接池
```

## 4. CLAUDE.md 项目配置

```markdown
# CLAUDE.md（放在项目根目录）

## 项目概述
这是一个 Python FastAPI 后端服务，使用 PostgreSQL 数据库。

## 技术栈
- Python 3.12 + FastAPI
- SQLAlchemy ORM
- Alembic 数据库迁移
- pytest 测试框架

## 代码规范
- 使用 ruff 格式化代码
- 类型注解必须完整
- 每个公共函数需要 docstring
- 测试文件放在 tests/ 对应目录

## 常用命令
- 运行测试: pytest -xvs
- 格式化: ruff format .
- 类型检查: mypy src/
- 数据库迁移: alembic upgrade head

## 注意事项
- 不要修改 alembic/versions/ 中的已有迁移文件
- API 路由定义在 src/routes/ 目录
- 环境变量通过 .env 文件管理
```

## 5. MCP 工具扩展

```json
// ~/.claude/mcp.json
{
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": { "GITHUB_TOKEN": "ghp_xxx" }
    },
    "postgres": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-postgres"],
      "env": { "DATABASE_URL": "postgresql://..." }
    },
    "jira": {
      "command": "npx",
      "args": ["-y", "mcp-server-jira"],
      "env": { "JIRA_URL": "https://xxx.atlassian.net" }
    }
  }
}
```

## 6. 多 Agent 并行（Claude Code 5）

```bash
# Claude Code 支持并行 Agent 执行
# 主 Agent 可以 spawn 子 Agent 并行处理不同文件/任务

> 重构整个项目的错误处理：
>   1. 统一异常类定义
>   2. 更新所有路由的错误处理
>   3. 添加全局异常处理中间件
>   4. 更新对应的测试

# Claude Code 会自动并行处理多个文件的修改
# 子 Agent 各自负责不同模块，最后合并结果
```

## 7. Git 工作流集成

```bash
# Claude Code 原生支持 Git 操作
> 创建一个新分支 feature/user-auth，实现用户认证模块
> 查看最近的 commit，解释每个变更的目的
> 帮我写一个好的 commit message 并提交
> 创建 PR，标题和描述要清晰

# 代码审查
> 审查 PR #15 的代码变更，给出改进建议
```

## 8. 终端 Agent 对比

| 特性 | Claude Code | Aider | Codex CLI | Gemini CLI |
|------|------------|-------|-----------|------------|
| 开发商 | Anthropic | 开源 | OpenAI | Google |
| 模型 | Claude 4/Sonnet | 多模型 | GPT-4o/o3 | Gemini 2.5 |
| 代码库理解 | 全局索引 | Git 感知 | 全局索引 | 全局索引 |
| 多文件编辑 | ✅ | ✅ | ✅ | ✅ |
| 命令执行 | ✅ | 有限 | ✅ 沙箱 | ✅ |
| MCP 支持 | ✅ | ❌ | ❌ | ✅ |
| 多 Agent | ✅ 并行 | ❌ | ❌ | ❌ |
| Git 集成 | ✅ 原生 | ✅ 原生 | ✅ | ✅ |
| 价格 | Claude API 计费 | 免费+API费 | OpenAI 计费 | Gemini 计费 |

## 9. 权限配置（五级权限系统）

Claude Code 内部实现了五级权限模型，点击"允许"说明配置不够完善：

```json
// ~/.claude/settings.json — 预配置权限规则
{
  "permissions": {
    "allow": [
      "Read(**)",
      "Glob(**)",
      "Grep(**)",
      "Bash(npm test*)",
      "Bash(git *)",
      "Write(src/**/*.test.ts)"
    ],
    "deny": [
      "Bash(rm -rf *)",
      "Read(~/.ssh/**)",
      "Write(.env*)"
    ]
  }
}
```

## 10. 上下文管理（5 种压缩策略）

Claude Code 内部有 5 种上下文压缩策略，从轻到重：
1. Microcompact — 基于时间清除旧工具结果
2. Context Collapse — 摘要压缩对话片段
3. Session Memory — 提取关键上下文到文件
4. Full Compact — `/compact` 命令，摘要整个历史
5. PTL Truncation — 最后手段，丢弃最早消息

**关键：** CLAUDE.md 在每一轮对话中都会重新加载，所以把最重要的上下文放在 CLAUDE.md 中，而不是依赖对话历史。

## 11. 最佳实践

```
1. CLAUDE.md 是最高杠杆 — 每轮都会加载，放入项目规范和关键上下文
2. 预配置权限 — 用 settings.json 配置 allow/deny，减少交互确认
3. 主动压缩 — 长会话用 /compact，不要等 Agent 开始"忘事"
4. 任务粒度 — 一次一个明确任务，避免模糊指令
5. 验证习惯 — 让 Claude Code 运行测试验证修改
6. Git Worktree — 多 Agent 并行时利用 Worktree 隔离
7. Hook 扩展 — 用 Hook 系统自动化 lint/test/通知
8. MCP 扩展 — 为常用服务配置 MCP Server
```

> 📖 深度架构分析见 → `Claude Code架构深度解析.md`（本目录）
## 🎬 推荐视频资源

### 🌐 YouTube
- [Anthropic - Claude Code Demo](https://www.youtube.com/watch?v=hkhDdcM5V94) — Claude Code官方演示
- [Frontend Masters - Claude Code Tutorial](https://frontendmasters.com/courses/pro-ai/) — Claude Code专业教程
- [Fireship - Claude Code Review](https://www.youtube.com/watch?v=DHjqpvDnNGE) — Claude Code快速评测

### 📺 B站
- [Claude Code使用教程](https://www.bilibili.com/video/BV1Bm421N7BH) — Claude Code中文教程

### 📖 官方文档
- [Claude Code Docs](https://docs.anthropic.com/en/docs/claude-code) — Anthropic官方文档
