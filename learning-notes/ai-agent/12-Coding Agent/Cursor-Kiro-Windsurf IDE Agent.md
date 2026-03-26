# Cursor / Kiro / Windsurf IDE Agent

## 1. IDE 集成 Coding Agent 概述

IDE Agent 将 AI 能力直接嵌入开发环境，提供代码补全、多文件编辑、对话式编程等能力。相比终端 Agent，IDE Agent 拥有更丰富的上下文（语法树、诊断信息、UI 交互）。

```
┌─────────────── IDE Agent 架构 ───────────────┐
│                                               │
│  ┌─────────┐  ┌──────────┐  ┌─────────────┐ │
│  │代码补全  │  │ 对话/Chat │  │ 多文件编辑   │ │
│  │Tab 补全  │  │ 上下文问答 │  │ Composer    │ │
│  └─────────┘  └──────────┘  └─────────────┘ │
│       ↕             ↕              ↕          │
│  ┌───────────────────────────────────────┐   │
│  │  代码索引 / 语法树 / 诊断 / Git 状态   │   │
│  └───────────────────────────────────────┘   │
│       ↕             ↕              ↕          │
│  ┌───────────────────────────────────────┐   │
│  │     LLM (Claude/GPT/Gemini/自选)      │   │
│  └───────────────────────────────────────┘   │
└──────────────────────────────────────────────┘
```

## 2. Cursor

AI-first 代码编辑器（基于 VS Code fork），以 Composer 多文件编辑和智能补全著称。

```
核心功能：
├─ Tab 补全：上下文感知的代码补全
├─ Chat：对话式编程，引用文件/符号
├─ Composer：多文件编辑，Agent 模式
├─ Cmd+K：内联代码生成/编辑
└─ @引用：@file @folder @web @docs @codebase
```

### .cursorrules 配置

```markdown
# .cursorrules（项目根目录）

You are an expert TypeScript developer.

## Code Style
- Use functional components with hooks
- Prefer named exports over default exports
- Use Zod for runtime validation
- Error handling: use Result pattern, avoid try-catch

## Project Structure
- src/routes/ - API route handlers
- src/services/ - Business logic
- src/models/ - Data models with Zod schemas
- src/utils/ - Shared utilities

## Testing
- Use Vitest for unit tests
- Test files: *.test.ts next to source files
- Mock external services, don't mock internal modules
```

## 3. Kiro

AWS 推出的 AI IDE，核心特色是 Specs 驱动开发和 Hooks 自动化。

```
核心功能：
├─ Specs：需求 → 设计 → 任务的结构化开发流程
├─ Hooks：文件变更/事件触发的自动化动作
├─ Steering：项目级 AI 行为配置
├─ MCP 集成：扩展工具能力
└─ Agent 模式：自主完成复杂任务
```

### Steering 文件

```markdown
# .kiro/steering/project.md
# inclusion: auto

## 项目概述
这是一个 Node.js 后端服务。

## 代码规范
- 使用 TypeScript strict 模式
- 所有函数必须有 JSDoc 注释
- 使用 ESM 模块系统

## 测试要求
- 每个 service 文件必须有对应测试
- 使用 Vitest 测试框架
```

### Hooks 自动化

```
Hooks 示例：
├─ 文件保存时自动运行 lint
├─ 创建新文件时自动生成测试模板
├─ 提交前自动检查类型错误
└─ Agent 完成任务后自动运行测试
```

## 4. Windsurf

Codeium 推出的 AI IDE，以 Cascade 流式编辑和深度上下文理解为特色。

```
核心功能：
├─ Cascade：多步骤 Agent 流，自动执行编辑链
├─ Flows：上下文感知的代码操作流
├─ Supercomplete：超级补全（预测下一步操作）
├─ 命令执行：内置终端命令执行
└─ 多模型：支持 GPT/Claude/Gemini
```

## 5. GitHub Copilot

GitHub 原生 AI 编程助手，集成于 VS Code / JetBrains / Neovim。

```
核心功能：
├─ 代码补全：行级/块级智能补全
├─ Copilot Chat：对话式编程
├─ Workspace Agent：@workspace 全项目理解
├─ Copilot Edits：多文件编辑模式
└─ CLI：终端命令建议
```

## 6. 综合对比

| 特性 | Cursor | Kiro | Windsurf | GitHub Copilot |
|------|--------|------|----------|----------------|
| 基础 | VS Code fork | VS Code fork | VS Code fork | VS Code 插件 |
| 核心模式 | Composer Agent | Specs 驱动 | Cascade 流 | Copilot Edits |
| 多文件编辑 | ✅ 强 | ✅ | ✅ | ✅ |
| 项目配置 | .cursorrules | Steering/Hooks | Cascade Rules | .github/copilot |
| 模型支持 | Claude/GPT/自选 | Claude/多模型 | GPT/Claude/Gemini | GPT/Claude |
| MCP 支持 | ✅ | ✅ 原生 | ✅ | ✅ |
| 结构化开发 | ❌ | ✅ Specs | ❌ | ❌ |
| 自动化 | 有限 | ✅ Hooks | 有限 | 有限 |
| 免费版 | 有限额度 | 免费 | 有限额度 | 免费额度 |
| Pro 价格 | $20/月 | 免费(Preview) | $15/月 | $10/月 |
| 特色优势 | 补全体验最佳 | 规范化开发流程 | 流式编辑体验 | 生态集成最广 |

## 7. IDE Agent vs 终端 Agent

```
IDE Agent 优势：
  ✅ 可视化 diff，直观审查变更
  ✅ 语法高亮、诊断信息、自动补全
  ✅ 文件树、符号导航等 IDE 能力
  ✅ 适合日常开发、代码审查

终端 Agent 优势：
  ✅ 无 GUI 依赖，可在服务器/CI 中运行
  ✅ 管道组合，与 Shell 工具链集成
  ✅ 适合批量操作、自动化脚本
  ✅ SSH 远程开发友好

推荐：日常开发用 IDE Agent，自动化/CI 用终端 Agent
```

## 8. 选型建议

```
追求补全体验和灵活性     → Cursor
需要规范化开发流程       → Kiro
喜欢流式编辑体验        → Windsurf
已有 GitHub 生态        → GitHub Copilot
团队统一工具            → GitHub Copilot（覆盖面最广）
```
