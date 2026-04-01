# Claude Code 架构深度解析
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang
> 基于 2026-03-31 npm source map 泄露事件的架构分析

## 1. 事件背景

2026 年 3 月 31 日，安全研究员 Chaofan Shou 发现 Claude Code 的 npm 包（`@anthropic-ai/claude-code` v2.1.88）中包含了一个 57MB 的 `.map` 源映射文件，指向 Anthropic R2 存储桶中未混淆的 TypeScript 源码。这次泄露暴露了约 1,900 个文件、512,000+ 行代码，完整揭示了当前最先进的 AI 编码 Agent 的内部架构。

Anthropic 官方确认这是"发布打包流程中的人为错误，不涉及客户数据或凭证泄露"。

**对开发者的价值：** 这是迄今为止对生产级 Agentic 系统最完整的架构参考，揭示了工具系统、权限模型、多 Agent 编排、记忆管理、上下文压缩等核心设计模式。

## 2. 技术栈

| 类别 | 技术 |
|------|------|
| 运行时 | Bun |
| 语言 | TypeScript（strict 模式） |
| 终端 UI | React + Ink |
| CLI 解析 | Commander.js（extra-typings） |
| Schema 验证 | Zod v4 |
| 代码搜索 | ripgrep |
| 协议 | MCP SDK、LSP |
| API | Anthropic SDK |
| 遥测 | OpenTelemetry + gRPC |
| 特性开关 | GrowthBook |
| 认证 | OAuth 2.0、JWT、macOS Keychain |

**关键选型洞察：**
- 选择 Bun 而非 Node.js，利用其原生 TypeScript 支持和更快的启动速度
- 用 React + Ink 构建终端 UI，实现组件化的终端界面（这是非常前沿的做法）
- Zod v4 做运行时 Schema 验证，确保工具输入输出的类型安全

## 3. 整体架构

```
┌─────────────────────────────────────────────────────────────────┐
│                     Claude Code 架构全景                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  入口层    main.tsx（Commander.js CLI + React/Ink 渲染器）        │
│           ─────────────────────────────────────                  │
│  命令层    commands/（50+ 斜杠命令）                              │
│           ─────────────────────────────────────                  │
│  引擎层    QueryEngine.ts（46K行，LLM调用核心）                   │
│           ─────────────────────────────────────                  │
│  工具层    tools/（40+ 工具，每个自包含模块）                      │
│           ─────────────────────────────────────                  │
│  权限层    hooks/toolPermission/（5级权限系统）                    │
│           ─────────────────────────────────────                  │
│  协调层    coordinator/（多Agent编排）                             │
│           ─────────────────────────────────────                  │
│  服务层    services/（API、MCP、OAuth、LSP、分析）                 │
│           ─────────────────────────────────────                  │
│  桥接层    bridge/（IDE双向通信：VS Code、JetBrains）              │
│           ─────────────────────────────────────                  │
│  状态层    state/ + memdir/（持久化记忆目录）                      │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```


## 4. 工具系统（40+ 工具）

每个工具是一个自包含模块，定义输入 Schema、权限模型和执行逻辑。这是 Agent 能力的核心。

### 核心工具清单

| 工具 | 功能 | 设计要点 |
|------|------|---------|
| BashTool | Shell 命令执行 | 沙箱隔离，命令白名单/黑名单 |
| FileReadTool | 文件读取（图片/PDF/Notebook） | 支持多格式，自动编码检测 |
| FileWriteTool | 文件创建/覆盖 | 写前权限检查，原子写入 |
| FileEditTool | 部分文件修改（字符串替换） | 精确匹配，避免全文重写 |
| GlobTool | 文件模式匹配搜索 | 快速文件发现 |
| GrepTool | ripgrep 内容搜索 | 比原生 grep 快 10x+ |
| WebFetchTool | URL 内容获取 | 超时控制，内容截断 |
| WebSearchTool | 网络搜索 | 搜索结果结构化 |
| AgentTool | 子 Agent 生成 | 多 Agent 并行的核心 |
| SkillTool | Skill 执行 | 可复用工作流 |
| MCPTool | MCP Server 工具调用 | 动态工具发现 |
| LSPTool | 语言服务器协议集成 | 代码智能（跳转/补全/诊断） |
| NotebookEditTool | Jupyter Notebook 编辑 | Cell 级别操作 |
| TaskCreateTool | 任务创建 | 持久化任务图 |
| SendMessageTool | Agent 间消息传递 | 基于文件的消息队列 |
| TeamCreateTool | 团队 Agent 管理 | 创建/删除团队成员 |
| EnterPlanModeTool | 进入规划模式 | 只规划不执行 |
| EnterWorktreeTool | Git Worktree 隔离 | 每个 Agent 独立工作树 |
| ToolSearchTool | 延迟工具发现 | 按需加载工具定义 |
| CronCreateTool | 定时触发器 | 后台定时任务 |
| SleepTool | 主动模式等待 | Proactive Agent 用 |
| SyntheticOutputTool | 结构化输出生成 | 强制输出格式 |

### 工具设计模式

```typescript
// 每个工具的标准结构（简化示意）
interface Tool {
  name: string;
  description: string;
  inputSchema: ZodSchema;       // Zod v4 输入验证
  permissionModel: PermissionModel; // 权限模型
  execute(input: Input): Promise<Output>;
  
  // 关键：每个工具自声明权限需求
  requiredPermissions: Permission[];
  sideEffects: boolean;         // 是否有副作用
}
```

**核心设计原则：**
1. 自包含 — 每个工具独立定义 Schema、权限、执行逻辑
2. 权限前置 — 执行前必须通过权限检查
3. 副作用声明 — 工具显式声明是否有副作用（读 vs 写）
4. Schema 验证 — Zod v4 确保输入输出类型安全

## 5. 五级权限系统（关键发现）

这是泄露中最有价值的设计之一。Claude Code 不是简单的"允许/拒绝"，而是一个可配置的五级权限系统。

```
┌─────────────────────────────────────────────────────────┐
│                    五级权限模型                            │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  Level 1: Always Allow（始终允许）                        │
│  └─ 配置在 ~/.claude/settings.json 的白名单              │
│  └─ 例：文件读取、grep 搜索                              │
│                                                          │
│  Level 2: Auto-Approve（自动批准）                       │
│  └─ 基于 glob 模式匹配的自动授权                         │
│  └─ 例：*.test.ts 文件的写入自动允许                     │
│                                                          │
│  Level 3: Prompt（交互确认）                             │
│  └─ 需要用户明确确认的操作                               │
│  └─ 例：删除文件、执行未知命令                           │
│                                                          │
│  Level 4: Plan Mode（规划模式）                          │
│  └─ 只生成计划，不执行任何操作                           │
│  └─ 用于审查 Agent 的决策逻辑                            │
│                                                          │
│  Level 5: Never Allow（始终拒绝）                        │
│  └─ 黑名单操作，无论如何不允许                           │
│  └─ 例：rm -rf /、访问 ~/.ssh/                          │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

**配置示例：**

```json
// ~/.claude/settings.json
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

**对我们的启示：** 当你点击"允许"时，说明你的权限配置不够完善。生产环境应该预配置好权限规则，让 Agent 在安全边界内自主运行。

## 6. CLAUDE.md 每轮加载机制（关键发现）

泄露源码揭示了一个被严重低估的特性：**CLAUDE.md 在每一轮对话中都会被重新加载**。

```
用户输入 → 加载 CLAUDE.md → 注入系统提示 → LLM 推理 → 工具调用 → 返回结果
              ↑                                                    │
              └────────────────────────────────────────────────────┘
                              下一轮继续加载
```

**这意味着：**
1. CLAUDE.md 是最高杠杆的配置文件 — 它影响 Agent 的每一次决策
2. 可以动态修改 — 在会话中途修改 CLAUDE.md，下一轮立即生效
3. 层级加载 — 项目根目录 + 子目录的 CLAUDE.md 会合并

**最佳实践：**

```markdown
# CLAUDE.md — 高杠杆配置示例

## 项目上下文
- 这是一个 Python 3.12 + FastAPI 项目
- 数据库：PostgreSQL + SQLAlchemy
- 测试：pytest，覆盖率要求 > 80%

## 编码规范（每轮都会执行）
- 所有函数必须有类型注解
- 使用 ruff format 格式化
- 错误处理使用自定义异常类（见 src/exceptions.py）
- API 响应统一使用 ResponseModel

## 禁止操作
- 不要修改 alembic/versions/ 中的已有迁移
- 不要直接操作数据库，必须通过 ORM
- 不要在代码中硬编码密钥

## 测试要求
- 每个新功能必须有对应测试
- 修改代码后运行 pytest -xvs 验证
```

## 7. 上下文压缩策略（5 种）

长会话是 LLM Agent 的核心挑战。Claude Code 实现了 5 种压缩策略：

| 策略 | 触发条件 | 机制 | 保留内容 |
|------|---------|------|---------|
| Microcompact | 基于时间 | 清除旧的工具调用结果 | 保留决策，丢弃细节 |
| Context Collapse | 上下文过长 | 摘要压缩对话片段 | 关键决策和结论 |
| Session Memory | 主动触发 | 提取关键上下文到文件 | 持久化到 memdir/ |
| Full Compact | /compact 命令 | 摘要整个对话历史 | 全局摘要 |
| PTL Truncation | 最后手段 | 丢弃最早的消息组 | 保留最近上下文 |

```
上下文窗口使用率
100% ┤                          ╭─── PTL Truncation（最后手段）
 90% ┤                     ╭────╯
 80% ┤                ╭────╯ ← Full Compact 触发线
 70% ┤           ╭────╯
 60% ┤      ╭────╯ ← Context Collapse 触发线
 50% ┤ ╭────╯
 40% ┤─╯ ← Microcompact 持续运行
     └──────────────────────────────────────→ 对话轮次
```

**对我们的启示：** 不要等到 Agent 开始"忘事"才压缩。主动使用 `/compact` 命令，或在 CLAUDE.md 中设置关键上下文，确保每轮都能读到。

## 8. 多 Agent 编排（Swarm 模式）

泄露揭示了 Claude Code 的多 Agent 系统是基于**文件系统的消息传递**，而非数据库或消息队列。

```
┌─────────────────────────────────────────────────┐
│              Lead Agent（主 Agent）               │
│  ├─ 任务分解                                     │
│  ├─ 子 Agent 生成（AgentTool）                   │
│  ├─ 结果聚合                                     │
│  └─ 冲突解决                                     │
├─────────────────────────────────────────────────┤
│                                                  │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐      │
│  │ Agent A  │  │ Agent B  │  │ Agent C  │      │
│  │ 前端重构  │  │ API修改   │  │ 测试编写  │      │
│  │ Worktree │  │ Worktree │  │ Worktree │      │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘      │
│       │              │              │            │
│       └──────────────┴──────────────┘            │
│              共享 Prompt Cache                    │
│              文件系统消息传递                      │
│              JSON 任务图                          │
└─────────────────────────────────────────────────┘
```

**关键设计决策：**

1. **Prompt Cache 共享** — 子 Agent fork 时创建父上下文的字节级副本，共享 Prompt Cache。这意味着并行 Agent 几乎不增加额外成本（这是最"mind-blowing"的发现）
2. **Git Worktree 隔离** — 每个子 Agent 在独立的 Git Worktree 中工作，避免文件冲突
3. **文件系统通信** — Agent 间通过写入对方的 inbox 文件通信，任务是磁盘上的 JSON 文件
4. **无数据库/无消息队列** — 整个多 Agent 系统基于文件系统，极简但有效

**为什么选择文件系统而非数据库？**
- 零依赖：不需要安装 Redis/PostgreSQL
- 可调试：直接 `cat` 查看 Agent 状态
- 可恢复：任务图持久化在磁盘，会话重启后可恢复
- 简单：JSON 文件比 IPC/RPC 简单得多

## 9. Hook 系统（25+ 生命周期事件）

泄露揭示了一个强大的 Hook 系统，这是 Claude Code 真正的扩展 API。

```
Agent 生命周期
│
├─ SessionStart          ← 会话开始
├─ UserPromptSubmit      ← 用户提交提示
│   ├─ PreToolUse        ← 工具调用前（可拦截）
│   ├─ ToolExecution     ← 工具执行中
│   ├─ PostToolUse       ← 工具调用后
│   └─ ... (循环)
├─ AgentResponse         ← Agent 响应
├─ SessionEnd            ← 会话结束
│
Hook 可触发的动作：
├─ 运行 Shell 命令
├─ 注入 LLM 上下文
├─ 运行完整 Agent 验证循环
├─ 调用 Webhook
└─ 运行 JavaScript 函数
```

**生产级 Hook 示例：**

```json
// .claude/hooks/pre-write-lint.json
{
  "name": "Pre-Write Lint",
  "version": "1.0.0",
  "when": {
    "type": "preToolUse",
    "toolTypes": ["write"]
  },
  "then": {
    "type": "runCommand",
    "command": "npx eslint --fix ${file}"
  }
}

// .claude/hooks/post-edit-test.json
{
  "name": "Post-Edit Test",
  "version": "1.0.0",
  "when": {
    "type": "postToolUse",
    "toolTypes": ["write"]
  },
  "then": {
    "type": "runCommand",
    "command": "npm test -- --related ${file}"
  }
}
```

## 10. 特性开关系统（44 个 Flag）

泄露揭示了 44 个特性开关，指向多个未发布功能：

| Flag | 推测功能 |
|------|---------|
| PROACTIVE | 主动模式 — Agent 在用户不操作时主动执行任务 |
| KAIROS | 自主 Agent 系统 — 根据用户注意力动态调整主动性 |
| BRIDGE_MODE | IDE 桥接模式 |
| DAEMON | 后台守护进程模式 |
| VOICE_MODE | 语音输入模式 |
| AGENT_TRIGGERS | Agent 触发器（定时/事件驱动） |
| MONITOR_TOOL | 监控工具 |
| BUDDY | 虚拟宠物系统（含多物种、稀有度、配饰） |

**实现方式（Bun 编译时消除）：**

```typescript
import { feature } from 'bun:bundle'

// 未启用的代码在构建时完全移除（Dead Code Elimination）
const voiceCommand = feature('VOICE_MODE')
  ? require('./commands/voice/index.js').default
  : null
```

**对我们的启示：** 特性开关是管理 Agent 功能演进的最佳实践。通过编译时消除，未启用的功能不会增加包体积。

## 11. 启动优化（并行预取）

Claude Code 的启动速度优化是一个值得学习的工程实践：

```typescript
// main.tsx — 在其他 import 之前作为副作用触发
startMdmRawRead()        // 预读 MDM 设置
startKeychainPrefetch()  // 预取密钥链
// API 预连接也在此并行启动

// 重模块延迟加载
// OpenTelemetry、gRPC、分析等模块通过 dynamic import() 按需加载
```

**优化策略：**
1. 并行预取 — MDM 设置、密钥链读取、API 预连接同时进行
2. 延迟加载 — 重模块（遥测、gRPC、分析）按需 `import()`
3. 特性开关 — 未启用功能在编译时完全移除

## 12. 服务层架构

| 服务 | 职责 |
|------|------|
| api/ | Anthropic API 客户端、文件 API、引导程序 |
| mcp/ | MCP Server 连接和管理 |
| oauth/ | OAuth 2.0 认证流程 |
| lsp/ | 语言服务器协议管理器 |
| analytics/ | GrowthBook 特性开关和分析 |
| plugins/ | 插件加载器 |
| compact/ | 对话上下文压缩 |
| policyLimits/ | 组织策略限制 |
| extractMemories/ | 自动记忆提取 |
| tokenEstimation.ts | Token 计数估算 |
| teamMemorySync/ | 团队记忆同步 |

## 13. 对 Agent 开发者的核心启示

### 可直接借鉴的设计模式

```
1. 工具自包含模式
   每个工具独立定义 Schema + 权限 + 执行逻辑
   → 适用于任何 Agent 框架的工具设计

2. 五级权限模型
   Always Allow → Auto-Approve → Prompt → Plan → Never Allow
   → 比简单的 allow/deny 更适合生产环境

3. CLAUDE.md 每轮注入
   项目配置在每轮对话中重新加载
   → 最高杠杆的 Agent 行为控制手段

4. Prompt Cache 共享
   子 Agent 共享父上下文的缓存
   → 多 Agent 并行的成本优化关键

5. 文件系统通信
   Agent 间通过 JSON 文件通信
   → 零依赖、可调试、可恢复

6. 五种上下文压缩
   从微压缩到全量截断的渐进策略
   → 长会话 Agent 的必备能力

7. Hook 生命周期
   25+ 事件点，5 种动作类型
   → Agent 可扩展性的核心

8. 特性开关 + 编译时消除
   未启用功能零成本
   → Agent 功能演进的最佳实践
```

### 安全教训

```
1. Source Map 泄露
   → 生产构建必须排除 .map 文件
   → npm publish 前检查包内容（npm pack --dry-run）

2. 供应链安全
   → CI/CD 中加入包内容审计步骤
   → 使用 .npmignore 或 package.json files 字段精确控制发布内容

3. 凭证管理
   → Claude Code 使用 OS 原生密钥链（macOS Keychain）
   → 不在文件系统中明文存储 Token
```

## 14. 与其他 Coding Agent 的架构对比

| 维度 | Claude Code | Cursor | Devin | Aider |
|------|------------|--------|-------|-------|
| 运行环境 | 终端（Bun） | IDE（Electron） | 云端沙箱 | 终端（Python） |
| UI 框架 | React + Ink | React | Web UI | 纯文本 |
| 工具数量 | 40+ | ~20 | ~30 | ~10 |
| 权限模型 | 5级可配置 | 基础确认 | 沙箱隔离 | 基础确认 |
| 多 Agent | Swarm（文件通信） | 后台 Agent | 单 Agent | 无 |
| 上下文压缩 | 5种策略 | 基础截断 | 未知 | 基础截断 |
| MCP 支持 | 原生 | 原生 | 无 | 无 |
| 开源 | ❌（已泄露） | ❌ | ❌ | ✅ |

## 🎬 推荐视频资源

### 🌐 YouTube
- [Matthew Berman - Claude Code Leak Analysis](https://www.youtube.com/watch?v=hkhDdcM5V94) — Claude Code 泄露深度分析
- [Anthropic - How We Built Multi-Agent Research](https://www.anthropic.com/engineering/multi-agent-research-system) — Anthropic 官方多 Agent 架构文章
- [PromptLayer - Claude Code Agent Loop](https://blog.promptlayer.com/claude-code-behind-the-scenes-of-the-master-agent-loop/) — Agent 主循环深度解析

### 📺 B站
- [Claude Code 源码泄露分析](https://www.bilibili.com/video/BV1Bm421N7BH) — 中文架构分析

### 📖 参考资料
- [Claude Code Leak: What Developers Can Learn](https://www.startuphub.ai/ai-news/artificial-intelligence/2026/claude-code-leak-what-developers-can-learn) — 开发者视角分析
- [Ars Technica - Claude Code Source Leak](https://arstechnica.com/ai/2026/03/entire-claude-code-cli-source-code-leaks-thanks-to-exposed-map-file/) — 事件报道
- [Claude Code Camp - Agent Teams Under the Hood](https://www.claudecodecamp.com/p/claude-code-agent-teams-how-they-work-under-the-hood) — 多 Agent 系统内部机制
- [GitHub Archive](https://github.com/WalterHandsome/claude-code) — 源码存档（教育研究用途）
