# 从 Claude Code 学构建生产级 AI Agent
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang
> 如果你要从零构建一个 AI Agent 项目，Claude Code 的 512,000 行源码是目前最好的架构参考

## 1. 为什么要学 Claude Code 的架构

Claude Code 泄露的源码揭示了一个关键事实：**模型只占代码量的 1.6%（~8,000 行），98.4% 是工程脚手架**。同一个 Claude 模型在 Web 版和 Claude Code 中表现差异巨大，原因不在模型，而在围绕模型构建的工程系统。

这意味着：如果你想构建一个强大的 AI Agent，重点不是选哪个模型，而是怎么设计围绕模型的系统。

```
你的 Agent 项目应该关注的层次：

┌─────────────────────────────────────────────┐
│  用户体验层（5%）  CLI / Web UI / IDE 插件    │
├─────────────────────────────────────────────┤
│  安全与权限层（15%）  权限模型 / 输入验证      │
├─────────────────────────────────────────────┤
│  工具系统层（25%）  工具定义 / Schema / 执行   │
├─────────────────────────────────────────────┤
│  编排与状态层（25%）  Agent循环 / 多Agent协调  │
├─────────────────────────────────────────────┤
│  上下文与记忆层（20%）  缓存 / 压缩 / 持久化  │
├─────────────────────────────────────────────┤
│  模型调用层（5%）  API调用 / 流式 / 重试      │
├─────────────────────────────────────────────┤
│  可观测层（5%）  日志 / 指标 / 成本追踪       │
└─────────────────────────────────────────────┘
```

## 2. Agent 主循环：最核心的 20 行代码

所有 Agent 的核心都是同一个循环。Claude Code 的实现（简化版）：

```python
"""Agent 主循环 — 所有 Agent 项目的起点"""

async def agent_loop(user_message: str, tools: list, system_prompt: str):
    messages = [{"role": "user", "content": user_message}]
    
    while True:
        # 1. 每轮注入系统提示（CLAUDE.md 每轮加载的原理）
        current_system = load_system_prompt(system_prompt)
        
        # 2. 调用 LLM
        response = await llm.create(
            system=current_system,
            messages=messages,
            tools=tools,
        )
        
        # 3. 如果没有工具调用 → 循环结束，返回结果
        if not response.tool_calls:
            return response.content
        
        # 4. 有工具调用 → 执行工具 → 结果反馈 → 继续循环
        for tool_call in response.tool_calls:
            # 权限检查（Claude Code 的五级权限在这里）
            if not check_permission(tool_call):
                result = "Permission denied"
            else:
                result = await execute_tool(tool_call)
            
            messages.append({"role": "tool", "content": result})
```

**Claude Code 的启示：**
- 循环本身很简单，复杂度在循环的每个环节里
- `load_system_prompt()` 每轮重新加载 → 这就是 CLAUDE.md 每轮注入的原理
- `check_permission()` 在工具执行前 → 安全是前置的，不是事后的
- 没有工具调用时循环才结束 → Agent 会持续工作直到任务完成


## 3. 工具设计：Anthropic 官方原则

Anthropic 在 2025 年发表了《Writing Effective Tools for AI Agents》，结合 Claude Code 源码，总结出以下工具设计原则：

### 原则一：为 Agent 设计，不是为开发者设计

```
❌ 传统 API 思维：
   list_contacts() → 返回所有联系人 → Agent 逐个读取 → 浪费上下文

✅ Agent 友好思维：
   search_contacts(name="Jane") → 只返回相关结果 → 节省上下文
```

Agent 的上下文窗口是有限的，而内存是廉价的。工具应该帮 Agent 跳到相关信息，而不是让它暴力搜索。

### 原则二：合并高频链式操作

```
❌ 碎片化工具：
   list_users() → list_events() → create_event()
   Agent 需要 3 次工具调用

✅ 合并工具：
   schedule_event(attendees=["Jane"], time="next week")
   一次调用完成查找可用时间 + 创建事件
```

### 原则三：返回有意义的上下文，而非原始数据

```python
# ❌ 返回原始 ID
{"user_id": "a1b2c3d4-e5f6-7890", "channel_id": "C0ABCDEF"}

# ✅ 返回可理解的信息
{"user_name": "Jane Smith", "channel_name": "#engineering"}
# 如果下游工具需要 ID，提供 response_format 参数切换详细/简洁模式
```

### 原则四：控制返回的 Token 量

```python
# Claude Code 默认限制工具响应为 25,000 tokens
MAX_TOOL_RESPONSE_TOKENS = 25_000

# 实现分页、过滤、截断
def search_logs(query: str, limit: int = 50, offset: int = 0) -> str:
    results = db.search(query, limit=limit, offset=offset)
    response = format_results(results)
    
    if len(response) > MAX_TOOL_RESPONSE_TOKENS:
        response = truncate(response)
        response += "\n[结果已截断，请使用更精确的查询或分页获取更多]"
    
    return response
```

### 原则五：错误信息要可操作

```python
# ❌ 无用的错误
raise ToolError("Error 422: Unprocessable Entity")

# ✅ 可操作的错误
raise ToolError(
    "日期格式无效。请使用 YYYY-MM-DD 格式，例如 '2026-04-01'。"
    "你提供的是: '4/1/2026'"
)
```

### 原则六：命名空间隔离

```python
# 当 Agent 有几十上百个工具时，命名空间防止混淆
tools = [
    "slack_search_messages",    # Slack 搜索
    "slack_send_message",       # Slack 发送
    "jira_search_issues",       # Jira 搜索
    "jira_create_issue",        # Jira 创建
    "github_search_code",       # GitHub 搜索
    "github_create_pr",         # GitHub PR
]
# 前缀命名让 Agent 清楚每个工具属于哪个服务
```


## 4. 权限系统：从 Claude Code 的五级模型学安全设计

```python
"""生产级 Agent 权限系统实现"""

from enum import Enum
from pathlib import Path
import fnmatch
import json

class PermissionLevel(Enum):
    ALWAYS_ALLOW = "always_allow"    # 无需确认
    AUTO_APPROVE = "auto_approve"    # 模式匹配自动批准
    PROMPT = "prompt"                # 需要用户确认
    PLAN_ONLY = "plan_only"          # 只规划不执行
    NEVER_ALLOW = "never_allow"      # 始终拒绝

class PermissionManager:
    def __init__(self, config_path: str = "~/.agent/permissions.json"):
        self.config = self._load_config(config_path)
    
    def check(self, tool_name: str, args: dict) -> PermissionLevel:
        # 1. 黑名单优先检查
        for pattern in self.config.get("deny", []):
            if self._matches(tool_name, args, pattern):
                return PermissionLevel.NEVER_ALLOW
        
        # 2. 白名单检查
        for pattern in self.config.get("allow", []):
            if self._matches(tool_name, args, pattern):
                return PermissionLevel.ALWAYS_ALLOW
        
        # 3. 自动批准规则
        for pattern in self.config.get("auto_approve", []):
            if self._matches(tool_name, args, pattern):
                return PermissionLevel.AUTO_APPROVE
        
        # 4. 默认需要确认
        return PermissionLevel.PROMPT
    
    def _matches(self, tool_name: str, args: dict, pattern: str) -> bool:
        # 支持 glob 模式：Read(**), Bash(npm test*), Write(src/**/*.ts)
        tool_pattern, _, arg_pattern = pattern.partition("(")
        arg_pattern = arg_pattern.rstrip(")")
        
        if not fnmatch.fnmatch(tool_name, tool_pattern):
            return False
        if arg_pattern and args:
            return any(fnmatch.fnmatch(str(v), arg_pattern) for v in args.values())
        return True
```

**配置示例：**

```json
{
  "allow": [
    "FileRead(**)",
    "Search(**)",
    "Bash(npm test*)",
    "Bash(git status)",
    "Bash(git diff*)"
  ],
  "auto_approve": [
    "FileWrite(src/**/*.test.*)",
    "Bash(python -m pytest*)"
  ],
  "deny": [
    "Bash(rm -rf *)",
    "FileRead(~/.ssh/**)",
    "FileRead(**/.env*)",
    "Bash(*sudo*)",
    "Bash(*curl*|*wget*)"
  ]
}
```


## 5. 上下文与记忆：长会话不崩溃的秘密

### 5.1 三层记忆架构

```
┌─────────────────────────────────────────────┐
│  第一层：工作记忆（对话上下文）                 │
│  ├─ 当前会话的消息历史                        │
│  ├─ 工具调用结果                              │
│  └─ 受上下文窗口限制（需要压缩策略）           │
├─────────────────────────────────────────────┤
│  第二层：项目记忆（CLAUDE.md / 配置文件）       │
│  ├─ 每轮重新加载（最高杠杆）                   │
│  ├─ 项目规范、编码风格、常用命令               │
│  └─ 不受上下文窗口限制（文件系统持久化）        │
├─────────────────────────────────────────────┤
│  第三层：长期记忆（memdir / 记忆蒸馏）          │
│  ├─ 跨会话持久化                              │
│  ├─ 自动提取关键知识                          │
│  └─ KAIROS autoDream 定期整理                 │
└─────────────────────────────────────────────┘
```

### 5.2 上下文压缩实现

```python
"""从 Claude Code 学到的上下文压缩策略"""

class ContextManager:
    MAX_CONTEXT_TOKENS = 128_000
    COMPACT_THRESHOLD = 0.8  # 80% 时开始压缩
    MAX_COMPACT_FAILURES = 3  # Claude Code 的教训：连续失败 3 次就停止
    
    def __init__(self, llm):
        self.llm = llm
        self.messages = []
        self.compact_failures = 0
    
    async def add_message(self, message: dict):
        self.messages.append(message)
        
        usage = self.estimate_tokens() / self.MAX_CONTEXT_TOKENS
        
        if usage > 0.95:
            # 策略5：PTL截断 — 最后手段，丢弃最早消息
            self._truncate_oldest()
        elif usage > self.COMPACT_THRESHOLD:
            # 策略4：Full Compact — 摘要整个历史
            await self._full_compact()
        
        # 策略1：Microcompact — 持续运行，清除旧工具结果
        self._microcompact()
    
    def _microcompact(self):
        """清除超过 10 轮的工具调用详细结果，只保留摘要"""
        for i, msg in enumerate(self.messages[:-10]):
            if msg.get("role") == "tool" and len(str(msg["content"])) > 500:
                msg["content"] = f"[工具结果已压缩: {msg['content'][:100]}...]"
    
    async def _full_compact(self):
        """用 LLM 摘要整个对话历史"""
        if self.compact_failures >= self.MAX_COMPACT_FAILURES:
            return  # Claude Code 的教训：避免无限重试
        
        try:
            summary = await self.llm.create(
                messages=[{
                    "role": "user",
                    "content": f"请摘要以下对话的关键决策和结论：\n{self._format_history()}"
                }]
            )
            # 用摘要替换历史消息
            self.messages = [
                {"role": "system", "content": f"[会话摘要]\n{summary}"},
                *self.messages[-5:]  # 保留最近 5 条
            ]
            self.compact_failures = 0
        except Exception:
            self.compact_failures += 1
    
    def _truncate_oldest(self):
        """丢弃最早的消息组"""
        # 保留系统消息和最近 10 条
        self.messages = [self.messages[0]] + self.messages[-10:]
```

### 5.3 cache_edits：标记删除而非真删除

```python
"""Claude Code 长会话不变慢的核心机制"""

class CacheAwareMessageStore:
    """标记删除旧消息，保持缓存连续性"""
    
    def __init__(self):
        self.messages = []
        self.skip_indices = set()  # 标记为跳过的消息索引
    
    def mark_skip(self, index: int):
        """标记消息为跳过（而非删除）"""
        self.skip_indices.add(index)
    
    def get_visible_messages(self) -> list:
        """返回模型可见的消息（跳过被标记的）"""
        return [
            msg for i, msg in enumerate(self.messages)
            if i not in self.skip_indices
        ]
    
    def get_cache_key(self) -> str:
        """缓存键基于完整消息列表（包括被跳过的）"""
        # 关键：缓存连续性不受 skip 影响
        return hash(tuple(str(m) for m in self.messages))
```


## 6. 多 Agent 编排：从单 Agent 到 Swarm

### 6.1 何时需要多 Agent

```
单 Agent 够用的场景：
├─ 单文件修改
├─ 简单问答
├─ 线性工作流（A → B → C）
└─ 上下文窗口内能完成的任务

需要多 Agent 的场景：
├─ 跨多个文件/模块的重构
├─ 需要不同专业知识的任务（前端 + 后端 + 测试）
├─ 任务可并行化（互不依赖的子任务）
└─ 单个上下文窗口装不下的大型任务
```

### 6.2 Claude Code 的 Swarm 模式实现

```python
"""从 Claude Code 学到的多 Agent 编排模式"""

import json
import asyncio
from pathlib import Path
from dataclasses import dataclass, field

@dataclass
class AgentTask:
    id: str
    description: str
    status: str = "pending"  # pending → running → completed → failed
    result: str = ""
    assigned_to: str = ""

@dataclass  
class AgentTeam:
    lead: str
    members: list[str] = field(default_factory=list)
    tasks: list[AgentTask] = field(default_factory=list)
    
    # Claude Code 的关键设计：文件系统通信
    workspace: Path = Path(".agent/team")
    
    def save_state(self):
        """持久化团队状态到磁盘（可恢复）"""
        self.workspace.mkdir(parents=True, exist_ok=True)
        state = {
            "lead": self.lead,
            "members": self.members,
            "tasks": [vars(t) for t in self.tasks],
        }
        (self.workspace / "team.json").write_text(json.dumps(state, indent=2))
    
    def send_message(self, from_agent: str, to_agent: str, content: str):
        """Agent 间通信：写入对方的 inbox 文件"""
        inbox = self.workspace / to_agent / "inbox.jsonl"
        inbox.parent.mkdir(parents=True, exist_ok=True)
        msg = json.dumps({"from": from_agent, "content": content})
        with open(inbox, "a") as f:
            f.write(msg + "\n")


async def run_swarm(task_description: str, llm):
    """Lead Agent 分解任务 → 分配给 Worker → 聚合结果"""
    
    # 1. Lead Agent 分解任务
    plan = await llm.create(messages=[{
        "role": "user",
        "content": f"将以下任务分解为可并行执行的子任务：\n{task_description}"
    }])
    
    subtasks = parse_subtasks(plan)
    team = AgentTeam(lead="lead", members=[f"worker_{i}" for i in range(len(subtasks))])
    
    # 2. 并行执行子任务（共享 Prompt Cache）
    async def run_worker(worker_id: str, task: AgentTask):
        # 关键：子 Agent 继承父上下文的缓存
        result = await llm.create(
            messages=[{"role": "user", "content": task.description}],
            # cache_control: 复用父上下文的缓存前缀
        )
        task.status = "completed"
        task.result = result
        team.save_state()  # 持久化到磁盘
    
    await asyncio.gather(*[
        run_worker(f"worker_{i}", task) 
        for i, task in enumerate(subtasks)
    ])
    
    # 3. Lead Agent 聚合结果
    results = "\n".join(f"子任务 {t.id}: {t.result}" for t in subtasks)
    final = await llm.create(messages=[{
        "role": "user",
        "content": f"以下是各子任务的结果，请合并为最终输出：\n{results}"
    }])
    
    return final
```

### 6.3 编排提示词而非代码

Claude Code 的一个关键发现：**多 Agent 编排算法是提示词，不是代码**。

```python
COORDINATOR_PROMPT = """
你是团队的 Lead Agent，负责协调多个 Worker Agent。

规则：
1. 不要橡皮图章式地批准低质量工作 — 如果 Worker 的输出不够好，要求重做
2. 你必须理解每个发现后才能指导后续工作 — 不要把理解工作转交给另一个 Worker
3. 分配任务时要明确：输入是什么、期望输出是什么、完成标准是什么
4. 当多个 Worker 的结果有冲突时，你负责裁决
5. 如果一个子任务失败了，评估是否影响其他子任务，必要时重新规划
"""
```


## 7. 成本工程：每个 Token 都是钱

### 7.1 缓存经济学

```
Claude Opus 4.6 定价：
├─ 标准输入：$5 / 百万 Token
├─ 缓存命中：$0.5 / 百万 Token（90% 折扣）
└─ 缓存未命中 = 成本 10x

→ 架构设计必须以缓存为中心
```

### 7.2 成本优化策略

```python
"""从 Claude Code 学到的成本优化"""

class CostOptimizer:
    # 策略1：模型路由 — 用最便宜的够用模型
    MODEL_TIERS = {
        "simple": "claude-haiku",      # 简单任务（格式化、分类）
        "standard": "claude-sonnet",   # 标准任务（代码编写、分析）
        "complex": "claude-opus",      # 复杂任务（架构设计、多步推理）
    }
    
    # 策略2：缓存友好的消息结构
    @staticmethod
    def build_messages(system: str, history: list, user_msg: str):
        return [
            # 静态内容放前面 → 缓存命中率高
            {"role": "system", "content": system, "cache_control": {"type": "ephemeral"}},
            # 历史消息 → 增量追加，不重排序
            *history,
            # 动态内容放最后 → 只有这部分是新的
            {"role": "user", "content": user_msg},
        ]
    
    # 策略3：工具响应 Token 限制
    MAX_TOOL_RESPONSE = 25_000  # Claude Code 的默认值
    
    # 策略4：子 Agent 复用父缓存
    # fork 子 Agent 时，创建父上下文的字节级副本
    # 共享 Prompt Cache → 并行 Agent 几乎不增加额外成本
```

### 7.3 成本监控

```python
"""Token 成本追踪器"""

class CostTracker:
    PRICING = {
        "claude-opus": {"input": 15.0, "output": 75.0, "cache_read": 1.5},
        "claude-sonnet": {"input": 3.0, "output": 15.0, "cache_read": 0.3},
        "claude-haiku": {"input": 0.25, "output": 1.25, "cache_read": 0.025},
    }
    
    def __init__(self):
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.total_cache_hits = 0
        self.total_cost_usd = 0.0
    
    def track(self, model: str, usage: dict):
        pricing = self.PRICING[model]
        input_cost = usage["input_tokens"] * pricing["input"] / 1_000_000
        output_cost = usage["output_tokens"] * pricing["output"] / 1_000_000
        cache_savings = usage.get("cache_read_tokens", 0) * (
            pricing["input"] - pricing["cache_read"]
        ) / 1_000_000
        
        self.total_cost_usd += input_cost + output_cost
        print(f"本次: ${input_cost + output_cost:.4f} | 缓存节省: ${cache_savings:.4f}")
```

## 8. 安全加固：23 项检查的启示

### 8.1 输入验证清单

```python
"""从 Claude Code 的 bashSecurity.ts 学到的安全检查"""

DANGEROUS_PATTERNS = [
    # 1. 危险命令
    r"rm\s+-rf\s+/",
    r"mkfs\.",
    r"dd\s+if=",
    r":(){ :|:& };:",  # Fork bomb
    
    # 2. 权限提升
    r"\bsudo\b",
    r"\bsu\s+-",
    r"chmod\s+777",
    
    # 3. 网络外传
    r"\bcurl\b.*\|\s*bash",
    r"\bwget\b.*\|\s*sh",
    
    # 4. 环境变量注入
    r"export\s+.*=.*\$\(",
    r"\beval\b",
    
    # 5. Zsh 特有攻击（Claude Code 的发现）
    r"=curl",           # Zsh 等号扩展绕过
    r"\x00",            # IFS null-byte 注入
    r"[\u200b-\u200f]", # Unicode 零宽字符注入
]

def validate_command(command: str) -> tuple[bool, str]:
    """验证命令安全性，返回 (是否安全, 原因)"""
    import re
    for pattern in DANGEROUS_PATTERNS:
        if re.search(pattern, command):
            return False, f"命令匹配危险模式: {pattern}"
    return True, "OK"
```

### 8.2 工具安全标记

```python
"""每个工具必须声明安全属性"""

@dataclass
class ToolSafety:
    has_side_effects: bool    # 是否有副作用（写入/删除/发送）
    requires_read_first: bool # 是否需要先读取再修改（Claude Code 的 FileEdit 要求）
    network_access: bool      # 是否需要网络访问
    max_execution_time: int   # 最大执行时间（秒）
    
# Claude Code 的做法：工具默认标记为 "unsafe, writable"
# 除非开发者显式声明为安全
```

## 9. 可扩展性：Hook 系统设计

```python
"""从 Claude Code 学到的 Hook 系统"""

from enum import Enum
from typing import Callable, Any

class HookEvent(Enum):
    SESSION_START = "session_start"
    USER_PROMPT = "user_prompt"
    PRE_TOOL_USE = "pre_tool_use"
    POST_TOOL_USE = "post_tool_use"
    PRE_COMPACT = "pre_compact"
    AGENT_RESPONSE = "agent_response"
    SESSION_END = "session_end"

class HookManager:
    def __init__(self):
        self._hooks: dict[HookEvent, list[Callable]] = {e: [] for e in HookEvent}
    
    def register(self, event: HookEvent, handler: Callable):
        self._hooks[event].append(handler)
    
    async def trigger(self, event: HookEvent, context: dict) -> dict:
        for handler in self._hooks[event]:
            result = await handler(context)
            if result and result.get("abort"):
                return result  # Hook 可以中止操作
        return {"continue": True}

# 使用示例
hooks = HookManager()

# 写文件前自动 lint
async def auto_lint(ctx):
    if ctx["tool"] == "FileWrite" and ctx["file"].endswith((".ts", ".js")):
        os.system(f"npx eslint --fix {ctx['file']}")

# 每次工具调用后运行相关测试
async def auto_test(ctx):
    if ctx["tool"] in ("FileWrite", "FileEdit"):
        os.system(f"npm test -- --related {ctx['file']}")

hooks.register(HookEvent.PRE_TOOL_USE, auto_lint)
hooks.register(HookEvent.POST_TOOL_USE, auto_test)
```


## 10. 项目配置系统：最高杠杆的控制手段

```python
"""项目配置加载器 — 模仿 CLAUDE.md 每轮加载机制"""

from pathlib import Path

class ProjectConfig:
    """
    层级配置加载：
    1. 全局配置 ~/.agent/config.md
    2. 项目根目录 ./AGENT.md
    3. 子目录 ./src/AGENT.md（覆盖上层）
    """
    
    def load(self, working_dir: Path) -> str:
        configs = []
        
        # 全局配置
        global_config = Path.home() / ".agent" / "config.md"
        if global_config.exists():
            configs.append(global_config.read_text())
        
        # 从项目根到当前目录，逐层加载
        for parent in reversed(list(working_dir.parents)):
            config_file = parent / "AGENT.md"
            if config_file.exists():
                configs.append(config_file.read_text())
        
        # 当前目录
        local_config = working_dir / "AGENT.md"
        if local_config.exists():
            configs.append(local_config.read_text())
        
        return "\n---\n".join(configs)
    
    def inject_to_system_prompt(self, base_prompt: str, working_dir: Path) -> str:
        """每轮调用时注入项目配置"""
        project_context = self.load(working_dir)
        if project_context:
            return f"{base_prompt}\n\n## 项目配置\n{project_context}"
        return base_prompt
```

## 11. 评估驱动开发：用 Eval 优化工具

Anthropic 官方推荐的工具优化流程：

```
1. 构建原型工具
   ↓
2. 生成评估任务（基于真实场景，不是玩具示例）
   ↓
3. 运行评估（Agent 循环 + 工具调用 + 结果验证）
   ↓
4. 分析结果（Agent 在哪里卡住？哪些工具调用失败？）
   ↓
5. 让 Agent 自己优化工具（把评估日志喂给 Claude Code）
   ↓
6. 重复 3-5 直到性能达标
   ↓
7. 用留出测试集验证（防止过拟合）
```

**关键洞察：** Anthropic 发现让 Claude Code 分析评估日志并自动优化工具描述，效果甚至超过人类专家手写的工具定义。Claude Sonnet 3.5 在 SWE-bench 上的 SOTA 成绩，就是通过精确优化工具描述实现的。

## 12. 完整项目脚手架

```
my-agent/
├── agent.md                    # 项目配置（每轮加载）
├── src/
│   ├── main.py                 # 入口 + Agent 主循环
│   ├── tools/                  # 工具系统
│   │   ├── __init__.py         # 工具注册表
│   │   ├── base.py             # 工具基类（Schema + 权限 + 执行）
│   │   ├── file_tools.py       # 文件操作工具
│   │   ├── shell_tools.py      # Shell 命令工具
│   │   ├── search_tools.py     # 搜索工具
│   │   └── mcp_tools.py        # MCP 工具桥接
│   ├── permissions/            # 权限系统
│   │   ├── manager.py          # 五级权限管理器
│   │   └── security.py         # 输入验证 + 安全检查
│   ├── context/                # 上下文管理
│   │   ├── manager.py          # 上下文压缩（5种策略）
│   │   ├── memory.py           # 持久化记忆
│   │   └── cache.py            # Prompt Cache 优化
│   ├── coordinator/            # 多 Agent 编排
│   │   ├── swarm.py            # Swarm 模式
│   │   └── tasks.py            # 任务图管理
│   ├── hooks/                  # Hook 系统
│   │   ├── manager.py          # Hook 管理器
│   │   └── builtin.py          # 内置 Hook（lint/test/notify）
│   └── cost/                   # 成本追踪
│       └── tracker.py          # Token 成本监控
├── config/
│   ├── permissions.json        # 权限配置
│   ├── hooks.json              # Hook 配置
│   └── mcp.json                # MCP Server 配置
├── evals/                      # 评估系统
│   ├── tasks/                  # 评估任务
│   ├── run_eval.py             # 评估运行器
│   └── analyze.py              # 结果分析
└── tests/
    ├── test_tools.py
    ├── test_permissions.py
    └── test_context.py
```

## 13. 从原型到生产的检查清单

```
□ Phase 1: 原型（1-2 天）
  □ Agent 主循环能跑通
  □ 3-5 个核心工具可用
  □ 基础权限检查（allow/deny）
  □ 简单的对话历史管理

□ Phase 2: 可用（1 周）
  □ 工具 Schema 验证（Pydantic/Zod）
  □ 五级权限系统
  □ 上下文压缩（至少 Microcompact + Full Compact）
  □ 错误处理与重试
  □ 成本追踪
  □ 基础评估任务

□ Phase 3: 生产级（2-4 周）
  □ Hook 系统（PreToolUse/PostToolUse）
  □ 多 Agent 编排（如果需要）
  □ Prompt Cache 优化
  □ 输入安全验证（参考 23 项检查）
  □ 持久化记忆（跨会话）
  □ 可观测性（日志/指标/追踪）
  □ 完整评估套件 + 留出测试集
  □ CI/CD 集成评估

□ Phase 4: 规模化
  □ 模型路由（按任务复杂度选模型）
  □ 缓存经济学优化（cache_edits）
  □ 团队记忆同步
  □ 组织策略限制
  □ 安全审计
```

## 🎬 推荐视频资源

### 🌐 YouTube
- [Anthropic - Writing Effective Tools for AI Agents](https://www.anthropic.com/engineering/writing-tools-for-agents) — Anthropic 官方工具设计指南（必读）
- [Anthropic - How We Built Multi-Agent Research](https://www.anthropic.com/engineering/multi-agent-research-system) — 多 Agent 系统构建
- [DeepLearning.AI - Agentic AI with Andrew Ng](https://www.deeplearning.ai/courses/agentic-ai/) — Agentic AI 完整课程（免费）
- [PromptLayer - Claude Code Agent Loop](https://blog.promptlayer.com/claude-code-behind-the-scenes-of-the-master-agent-loop/) — Agent 主循环解析

### 📺 B站
- [李沐 - 动手学深度学习](https://www.bilibili.com/video/BV1if4y147hS) — AI 工程基础
- [AI Agent 开发实战](https://www.bilibili.com/video/BV1Bm421N7BH) — Agent 开发中文教程

### 📖 参考资料
- [Anthropic - Writing Tools for Agents](https://www.anthropic.com/engineering/writing-tools-for-agents) — 工具设计原则（本文主要参考）
- [Building Production-Grade AI Agents](https://pub.towardsai.net/building-production-grade-ai-agents-in-2025-the-complete-technical-guide-9f02eff84ea2) — 生产级 Agent 技术指南
- [Claude Code 架构深度解析](./Claude%20Code架构深度解析.md) — 本目录，源码泄露分析
- [15 Hard-Earned Lessons to Ship AI Agents](https://medium.com/data-science-collective/beyond-the-prototype-15-hard-earned-lessons-to-ship-production-ready-ai-agents-e58139d80299) — 15 条实战教训
- [Portkey - Scaling Claude Code Agents](https://portkey.ai/blog/claude-code-agents/) — 团队级 Agent 扩展
