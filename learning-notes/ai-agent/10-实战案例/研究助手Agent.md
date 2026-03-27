# 研究助手 Agent
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. 系统架构

```
┌─────────────────────────────────────────────────────┐
│                 研究助手 Agent                        │
├──────────┬──────────┬──────────┬───────────────────┤
│ 文献搜索  │ 论文分析  │ 知识整合  │ 报告生成          │
├──────────┼──────────┼──────────┼───────────────────┤
│ Arxiv    │ PDF 解析  │ 交叉引用  │ Markdown 输出     │
│ Scholar  │ 摘要提取  │ 主题聚类  │ 结构化报告        │
│ Web 搜索 │ 方法分析  │ 趋势分析  │ 参考文献          │
└──────────┴──────────┴──────────┴───────────────────┘
         ↕ 记忆层（研究上下文持久化）↕
```

## 2. 工具定义

```python
from langchain_core.tools import tool
import arxiv
import requests

@tool
def search_arxiv(query: str, max_results: int = 5) -> str:
    """搜索 Arxiv 论文"""
    client = arxiv.Client()
    search = arxiv.Search(query=query, max_results=max_results, sort_by=arxiv.SortCriterion.Relevance)
    results = []
    for paper in client.results(search):
        results.append({
            "title": paper.title,
            "authors": [a.name for a in paper.authors[:3]],
            "summary": paper.summary[:300],
            "url": paper.entry_id,
            "published": paper.published.strftime("%Y-%m-%d"),
        })
    import json
    return json.dumps(results, ensure_ascii=False, indent=2)

@tool
def search_web(query: str) -> str:
    """使用 Tavily 搜索互联网"""
    from tavily import TavilyClient
    client = TavilyClient()
    result = client.search(query, search_depth="advanced", max_results=5)
    return "\n".join(f"- {r['title']}: {r['content'][:200]}" for r in result["results"])

@tool
def read_webpage(url: str) -> str:
    """读取网页内容"""
    response = requests.get(f"https://r.jina.ai/{url}")
    return response.text[:5000]

@tool
def analyze_pdf(pdf_url: str) -> str:
    """下载并分析 PDF 论文"""
    response = requests.get(pdf_url)
    from io import BytesIO
    from pypdf import PdfReader
    reader = PdfReader(BytesIO(response.content))
    text = "\n".join(page.extract_text() for page in reader.pages[:10])
    return text[:8000]
```

## 3. LangGraph 研究工作流

```python
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI
from typing import TypedDict, Annotated
from operator import add

class ResearchState(TypedDict):
    topic: str
    messages: Annotated[list, add]
    papers: list[dict]
    web_findings: list[str]
    analysis: str
    report: str

llm = ChatOpenAI(model="gpt-4o")

# 节点1：文献搜索
async def search_literature(state: ResearchState) -> dict:
    agent = create_react_agent(llm, tools=[search_arxiv, search_web])
    result = await agent.ainvoke({
        "messages": [("user", f"搜索关于 '{state['topic']}' 的最新论文和资料，至少找5篇")]
    })
    last_msg = result["messages"][-1].content
    return {"messages": [("assistant", f"文献搜索完成：{last_msg}")]}

# 节点2：深度分析
async def deep_analysis(state: ResearchState) -> dict:
    agent = create_react_agent(llm, tools=[analyze_pdf, read_webpage])
    result = await agent.ainvoke({
        "messages": [("user", f"深入分析以下研究材料，提取关键方法和发现：\n{state['messages'][-1]}")]
    })
    return {"analysis": result["messages"][-1].content}

# 节点3：报告生成
async def generate_report(state: ResearchState) -> dict:
    prompt = f"""基于以下研究分析，生成结构化研究报告：

主题：{state['topic']}
分析：{state['analysis']}

报告格式：
# 研究报告：{{主题}}
## 1. 研究背景
## 2. 关键发现
## 3. 方法对比
## 4. 趋势分析
## 5. 结论与建议
## 参考文献
"""
    response = await llm.ainvoke(prompt)
    return {"report": response.content}

# 节点4：质量检查
async def quality_check(state: ResearchState) -> str:
    response = await llm.ainvoke(
        f"评估研究报告质量(1-10)，只输出分数：\n{state['report'][:2000]}"
    )
    score = int(response.content.strip().split()[0])
    return "output" if score >= 7 else "deep_analysis"

# 构建图
graph = StateGraph(ResearchState)
graph.add_node("search", search_literature)
graph.add_node("deep_analysis", deep_analysis)
graph.add_node("generate_report", generate_report)
graph.add_node("output", lambda s: s)

graph.add_edge(START, "search")
graph.add_edge("search", "deep_analysis")
graph.add_edge("deep_analysis", "generate_report")
graph.add_conditional_edges("generate_report", quality_check)
graph.add_edge("output", END)

research_agent = graph.compile()
```

## 4. 运行研究助手

```python
import asyncio

async def run_research(topic: str) -> str:
    result = await research_agent.ainvoke({
        "topic": topic,
        "messages": [],
        "papers": [],
        "web_findings": [],
        "analysis": "",
        "report": "",
    })
    return result["report"]

report = asyncio.run(run_research("2025年大语言模型Agent的最新进展"))
print(report)
```

## 5. 研究记忆管理

```python
from mem0 import Memory

memory = Memory()

class ResearchMemory:
    """研究上下文记忆"""

    def __init__(self, project_id: str):
        self.project_id = project_id
        self.memory = Memory()

    def save_finding(self, finding: str):
        self.memory.add(finding, user_id=self.project_id, metadata={"type": "finding"})

    def save_paper(self, title: str, summary: str):
        self.memory.add(
            f"论文：{title}\n摘要：{summary}",
            user_id=self.project_id,
            metadata={"type": "paper"},
        )

    def get_context(self, query: str) -> str:
        results = self.memory.search(query, user_id=self.project_id)
        return "\n".join(f"- {r['memory']}" for r in results)

# 跨会话保持研究上下文
rm = ResearchMemory("ai-agent-research-2025")
rm.save_paper("ReAct: Synergizing Reasoning and Acting", "结合推理和行动的Agent框架...")
context = rm.get_context("Agent 推理方法")
```

## 6. 输出示例

```markdown
# 研究报告：2025年大语言模型Agent的最新进展

## 1. 研究背景
LLM Agent 在 2025 年进入生产化阶段，主要框架趋于成熟...

## 2. 关键发现
- **多Agent协作**成为主流架构模式
- **MCP协议**统一了工具集成标准
- **记忆系统**从简单缓存演进为分层架构
- **可观测性**成为生产部署的必备能力

## 3. 方法对比
| 方法 | 优势 | 局限 | 代表工作 |
|------|------|------|---------|
| ReAct | 通用性强 | 推理链长 | Yao et al. |
| Plan-Execute | 结构化 | 计划僵化 | Wang et al. |
| Reflection | 自我改进 | 成本高 | Shinn et al. |

## 4. 趋势分析
...

## 参考文献
1. [论文标题](URL) - 作者, 2025
2. ...
```
## 🎬 推荐视频资源

### 🌐 YouTube
- [LangChain - Research Assistant Agent](https://www.youtube.com/watch?v=dcgRMOG605w) — 研究助手Agent实战
- [DeepLearning.AI - Building Agentic RAG](https://www.deeplearning.ai/short-courses/building-agentic-rag-with-llamaindex/) — Agentic RAG研究助手（免费）
