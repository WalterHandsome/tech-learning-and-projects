# CrewAI 多 Agent 协作
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. 概述

CrewAI 是一个角色化多 Agent 协作框架，核心理念是将 AI Agent 组织为一个"团队"（Crew），每个 Agent 扮演特定角色，协作完成复杂任务。GitHub 44K+ Stars，支持 MCP 集成。

## 2. 核心概念

```python
from crewai import Agent, Task, Crew, Process
from crewai.tools import tool

# 1. 定义工具
@tool
def search_web(query: str) -> str:
    """搜索互联网获取最新信息"""
    return search_engine.search(query)

@tool
def write_file(filename: str, content: str) -> str:
    """将内容写入文件"""
    Path(filename).write_text(content)
    return f"已写入 {filename}"

# 2. 定义 Agent（角色）
researcher = Agent(
    role="高级研究员",
    goal="深入研究给定主题，收集全面准确的信息",
    backstory="你是一位经验丰富的研究员，擅长从多个来源收集和分析信息",
    tools=[search_web],
    llm="gpt-4o",
    verbose=True,
)

writer = Agent(
    role="技术作家",
    goal="将研究成果转化为高质量的技术文章",
    backstory="你是一位专业的技术作家，擅长将复杂概念用通俗易懂的方式表达",
    tools=[write_file],
    llm="gpt-4o",
)

reviewer = Agent(
    role="内容审核员",
    goal="审核文章质量，确保准确性和可读性",
    backstory="你是一位严格的编辑，对内容质量有极高的要求",
    llm="gpt-4o",
)

# 3. 定义任务
research_task = Task(
    description="研究 {topic} 的最新发展趋势和关键技术",
    expected_output="一份详细的研究报告，包含关键发现和数据",
    agent=researcher,
)

writing_task = Task(
    description="基于研究报告撰写一篇技术博客文章",
    expected_output="一篇 2000 字左右的技术文章，结构清晰",
    agent=writer,
    context=[research_task],  # 依赖研究任务的输出
)

review_task = Task(
    description="审核文章，提出修改建议",
    expected_output="审核意见和最终版本",
    agent=reviewer,
    context=[writing_task],
)

# 4. 组建团队
crew = Crew(
    agents=[researcher, writer, reviewer],
    tasks=[research_task, writing_task, review_task],
    process=Process.sequential,  # 顺序执行
    verbose=True,
)

# 5. 执行
result = crew.kickoff(inputs={"topic": "AI Agent 协议标准化"})
print(result)
```

## 3. 执行流程

```python
# 顺序执行
process=Process.sequential  # 任务按顺序执行

# 层级执行（Manager Agent 分配任务）
process=Process.hierarchical
manager_llm="gpt-4o"  # Manager 使用的模型
```

## 4. MCP 集成

```python
from crewai import Agent
from crewai.tools import MCPServerAdapter

# 连接 MCP Server
mcp_tools = MCPServerAdapter(
    server_params={
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-github"],
        "env": {"GITHUB_TOKEN": "ghp_xxx"},
    }
)

# Agent 使用 MCP 工具
developer = Agent(
    role="开发者",
    goal="管理 GitHub 仓库",
    tools=mcp_tools.tools,  # 自动发现 MCP Server 提供的工具
)
```

## 5. Memory 系统

```python
crew = Crew(
    agents=[...],
    tasks=[...],
    memory=True,  # 启用记忆
    # 短期记忆：当前执行上下文
    # 长期记忆：跨执行的经验
    # 实体记忆：关键实体信息
)
```

## 6. 框架对比

| 特性 | CrewAI | LangGraph | OpenAI SDK |
|------|--------|-----------|------------|
| 核心理念 | 角色协作 | 图工作流 | 快速原型 |
| 多 Agent | 原生支持 | 需手动编排 | Handoff 模式 |
| 学习曲线 | 低 | 中高 | 低 |
| 模型锁定 | 无 | 无 | OpenAI |
| MCP 支持 | 原生 | 通过工具 | 通过工具 |
| 适用场景 | 团队协作 | 复杂工作流 | GPT 原型 |
