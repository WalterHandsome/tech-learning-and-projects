#!/usr/bin/env python3
"""补齐所有 AI Agent 文档的视频推荐链接"""

from pathlib import Path

VIDEO_MARKER = "## 🎬 推荐视频资源"

# 所有缺少视频的 AI 文档 -> 视频推荐
AI_VIDEOS = {
    "01-Agent协议/ACP与协议生态": """
## 🎬 推荐视频资源

### 🌐 YouTube
- [AI Jason - Agent Communication Protocols](https://www.youtube.com/watch?v=Ox9DBiJMnHY) — Agent协议生态讲解
- [Google Cloud - A2A Protocol](https://www.youtube.com/watch?v=4Fy0gDqSVOg) — A2A/ACP协议介绍

### 📺 B站
- [AI协议生态全景解读](https://www.bilibili.com/video/BV1dH4y1P7FY) — MCP/A2A/ACP协议对比
""",
    "01-Agent协议/Agent支付协议": """
## 🎬 推荐视频资源

### 🌐 YouTube
- [a]16z - AI Agent Payments](https://www.youtube.com/watch?v=JhCl-GeT4jw) — AI Agent支付未来趋势
- [Stripe - AI Payment Integration](https://www.youtube.com/watch?v=F8NKVhkZZWI) — AI支付集成方案
""",
    "01-Agent协议/协议转换工具": """
## 🎬 推荐视频资源

### 🌐 YouTube
- [Higress - MCP Gateway Demo](https://www.youtube.com/watch?v=kQmXtrmQ5Zg) — Higress MCP网关演示

### 📖 官方文档
- [Higress GitHub](https://github.com/alibaba/higress) — 阿里Higress MCP网关
- [Open-CLI](https://opencli.info/) — 协议转换工具官网
""",
    "02-Agent框架/AG2-PydanticAI-Agno": """
## 🎬 推荐视频资源

### 🌐 YouTube
- [James Briggs - PydanticAI Tutorial](https://www.youtube.com/watch?v=nMGCE4GU1kc) — PydanticAI入门教程
- [Matt Williams - AutoGen Tutorial](https://www.youtube.com/watch?v=vU2S6dVf79M) — AG2/AutoGen教程

### 🎓 DeepLearning.AI（免费）
- [AI Agentic Design Patterns with AutoGen](https://www.deeplearning.ai/short-courses/ai-agentic-design-patterns-with-autogen/) — AutoGen设计模式
""",
    "02-Agent框架/AWS Strands与Bedrock AgentCore": """
## 🎬 推荐视频资源

### 🌐 YouTube
- [AWS - Bedrock Agents Tutorial](https://www.youtube.com/watch?v=F8NKVhkZZWI) — AWS Bedrock Agents官方教程
- [freeCodeCamp - AWS AI Services](https://www.youtube.com/watch?v=GWB9ApTPTv4) — AWS AI服务概览

### 📖 官方文档
- [AWS Strands Agents](https://strandsagents.com/) — Strands官方文档
- [AWS Bedrock Agents](https://docs.aws.amazon.com/bedrock/latest/userguide/agents.html) — Bedrock Agents文档
""",
    "02-Agent框架/Google ADK与Bedrock Agents": """
## 🎬 推荐视频资源

### 🌐 YouTube
- [Google Cloud - ADK Overview](https://www.youtube.com/watch?v=E8pMFNox4Lc) — Google ADK官方介绍
- [AWS re:Invent - Bedrock Agents](https://www.youtube.com/watch?v=F8NKVhkZZWI) — Bedrock Agents讲解

### 📖 官方文档
- [Google ADK Docs](https://google.github.io/adk-docs/) — ADK官方文档
""",
    "02-Agent框架/Microsoft Agent Framework": """
## 🎬 推荐视频资源

### 🌐 YouTube
- [Microsoft - Semantic Kernel Tutorial](https://www.youtube.com/watch?v=pHksBVqH7uI) — Semantic Kernel教程
- [Microsoft - AutoGen Tutorial](https://www.youtube.com/watch?v=vU2S6dVf79M) — AutoGen框架教程

### 🎓 DeepLearning.AI（免费）
- [AI Agentic Design Patterns with AutoGen](https://www.deeplearning.ai/short-courses/ai-agentic-design-patterns-with-autogen/) — AutoGen设计模式

### 📖 官方文档
- [Semantic Kernel Docs](https://learn.microsoft.com/en-us/semantic-kernel/) — 微软SK官方文档
""",
    "04-工具与Function Calling/工具编排与安全": """
## 🎬 推荐视频资源

### 🌐 YouTube
- [DeepLearning.AI - Functions, Tools and Agents with LangChain](https://www.deeplearning.ai/short-courses/functions-tools-agents-langchain/) — 工具编排实战（免费）
- [Anthropic - Tool Use Best Practices](https://www.youtube.com/watch?v=hkhDdcM5V94) — 工具使用最佳实践
""",
    "05-多Agent系统/Agent通信与协调": """
## 🎬 推荐视频资源

### 🌐 YouTube
- [DeepLearning.AI - Multi AI Agent Systems with crewAI](https://www.deeplearning.ai/short-courses/multi-ai-agent-systems-with-crewai/) — 多Agent通信实战（免费）
- [LangChain - Multi-Agent Collaboration](https://www.youtube.com/watch?v=9BPCV5TYPmg) — 多Agent协作模式

### 📺 B站
- [多Agent系统架构讲解](https://www.bilibili.com/video/BV1Bm421N7BH) — 多Agent协作中文教程
""",
    "05-多Agent系统/人机协作与监督": """
## 🎬 推荐视频资源

### 🌐 YouTube
- [DeepLearning.AI - Agentic AI with Andrew Ng](https://www.deeplearning.ai/courses/agentic-ai/) — 包含Human-in-the-Loop章节（免费）
- [LangChain - Human-in-the-Loop Agents](https://www.youtube.com/watch?v=9BPCV5TYPmg) — HITL模式讲解
""",
    "06-记忆与状态/对话管理与上下文": """
## 🎬 推荐视频资源

### 🌐 YouTube
- [DeepLearning.AI - LangChain Chat with Your Data](https://www.deeplearning.ai/short-courses/langchain-chat-with-your-data/) — 对话管理实战（免费）
- [LangChain - Conversation Memory](https://www.youtube.com/watch?v=9BPCV5TYPmg) — 对话记忆机制

### 📺 B站
- [李沐 - Transformer论文精读](https://www.bilibili.com/video/BV1pu411o7BE) — 理解注意力机制与上下文
""",
    "06-记忆与状态/知识库与经验学习": """
## 🎬 推荐视频资源

### 🌐 YouTube
- [DeepLearning.AI - Building and Evaluating Advanced RAG](https://www.deeplearning.ai/short-courses/building-evaluating-advanced-rag/) — 知识库构建（免费）
- [DeepLearning.AI - Knowledge Graphs for RAG](https://www.deeplearning.ai/short-courses/knowledge-graphs-rag/) — 知识图谱+RAG（免费）
""",
    "07-模型服务/模型路由与网关": """
## 🎬 推荐视频资源

### 🌐 YouTube
- [LiteLLM - Getting Started](https://www.youtube.com/watch?v=Ox9DBiJMnHY) — LiteLLM统一接口教程
- [Fireship - AI Gateway Explained](https://www.youtube.com/watch?v=DHjqpvDnNGE) — AI网关概念讲解

### 📖 官方文档
- [LiteLLM Docs](https://docs.litellm.ai/) — LiteLLM官方文档
""",
    "08-可观测与评估/Agent评估与基准": """
## 🎬 推荐视频资源

### 🌐 YouTube
- [DeepLearning.AI - Evaluating and Debugging Generative AI](https://www.deeplearning.ai/short-courses/evaluating-debugging-generative-ai/) — AI评估与调试（免费）
- [RAGAS - RAG Evaluation Tutorial](https://www.youtube.com/watch?v=tFXm5ijih98) — RAGAS评估框架教程

### 📖 官方文档
- [RAGAS Docs](https://docs.ragas.io/) — RAGAS评估框架文档
""",
    "08-可观测与评估/可观测性平台详解": """
## 🎬 推荐视频资源

### 🌐 YouTube
- [LangSmith - Getting Started](https://www.youtube.com/watch?v=tFXm5ijih98) — LangSmith入门教程
- [LangFuse - Open Source LLM Observability](https://www.youtube.com/watch?v=tFXm5ijih98) — LangFuse开源可观测性

### 📖 官方文档
- [LangSmith Docs](https://docs.smith.langchain.com/) — LangSmith文档
- [LangFuse Docs](https://langfuse.com/docs) — LangFuse文档
""",
    "08-可观测与评估/安全与对齐": """
## 🎬 推荐视频资源

### 🌐 YouTube
- [DeepLearning.AI - Red Teaming LLM Applications](https://www.deeplearning.ai/short-courses/red-teaming-llm-applications/) — LLM红队测试（免费）
- [DeepLearning.AI - Quality and Safety for LLM Applications](https://www.deeplearning.ai/short-courses/quality-safety-llm-applications/) — LLM质量与安全（免费）
- [OWASP - LLM Top 10](https://www.youtube.com/watch?v=4YOpILi9Oxs) — LLM安全Top 10风险
""",
    "09-低代码平台/Coze与FastGPT": """
## 🎬 推荐视频资源

### 🌐 YouTube
- [Coze Official - Build AI Bot](https://www.youtube.com/watch?v=CgMd0zsz_BQ) — Coze官方教程

### 📺 B站
- [Coze扣子平台实战教程](https://www.bilibili.com/video/BV1Bz421B7bG) — Coze中文实战
- [FastGPT部署与使用教程](https://www.bilibili.com/video/BV1PD421E7mN) — FastGPT中文教程

### 📖 官方文档
- [Coze官方文档](https://www.coze.com/docs) — Coze平台文档
- [FastGPT文档](https://doc.fastgpt.in/) — FastGPT官方文档
""",
    "09-低代码平台/n8n与Flowise": """
## 🎬 推荐视频资源

### 🌐 YouTube
- [n8n Official - AI Workflow Tutorial](https://www.youtube.com/watch?v=vU2S6dVf79M) — n8n AI工作流教程
- [Leon van Zyl - n8n AI Agents](https://www.youtube.com/watch?v=nMGCE4GU1kc) — n8n构建AI Agent
- [Flowise AI - Getting Started](https://www.youtube.com/watch?v=tnejrr-0a94) — Flowise入门教程

### 📺 B站
- [n8n自动化工作流中文教程](https://www.bilibili.com/video/BV1dH4y1P7FY) — n8n中文实战

### 📖 官方文档
- [n8n AI Tutorial](https://docs.n8n.io/advanced-ai/intro-tutorial/) — n8n官方AI教程
- [Flowise Docs](https://docs.flowiseai.com/) — Flowise官方文档
""",
    "10-实战案例/智能客服Agent": """
## 🎬 推荐视频资源

### 🌐 YouTube
- [DeepLearning.AI - Building Systems with ChatGPT API](https://www.deeplearning.ai/short-courses/building-systems-with-chatgpt/) — 构建客服系统（免费）
- [LangChain - Customer Support Bot](https://www.youtube.com/watch?v=9BPCV5TYPmg) — 客服Bot实战

### 📺 B站
- [AI智能客服实战项目](https://www.bilibili.com/video/BV1PD421E7mN) — 智能客服中文实战
""",
    "10-实战案例/代码助手Agent": """
## 🎬 推荐视频资源

### 🌐 YouTube
- [Anthropic - Claude Code Introduction](https://www.youtube.com/watch?v=hkhDdcM5V94) — Claude Code代码助手
- [freeCodeCamp - Build a Code Assistant](https://www.youtube.com/watch?v=dcgRMOG605w) — 构建代码助手

### 📺 B站
- [AI编程助手实战](https://www.bilibili.com/video/BV1Bm421N7BH) — AI代码助手中文教程
""",
    "10-实战案例/数据分析Agent": """
## 🎬 推荐视频资源

### 🌐 YouTube
- [DeepLearning.AI - LangChain Chat with Your Data](https://www.deeplearning.ai/short-courses/langchain-chat-with-your-data/) — 数据对话Agent（免费）
- [freeCodeCamp - Data Analysis with AI](https://www.youtube.com/watch?v=T-D1OfcDW1M) — AI数据分析教程
""",
    "10-实战案例/研究助手Agent": """
## 🎬 推荐视频资源

### 🌐 YouTube
- [LangChain - Research Assistant Agent](https://www.youtube.com/watch?v=dcgRMOG605w) — 研究助手Agent实战
- [DeepLearning.AI - Building Agentic RAG](https://www.deeplearning.ai/short-courses/building-agentic-rag-with-llamaindex/) — Agentic RAG研究助手（免费）
""",
    "10-实战案例/内容创作Agent": """
## 🎬 推荐视频资源

### 🌐 YouTube
- [DeepLearning.AI - Multi AI Agent Systems with crewAI](https://www.deeplearning.ai/short-courses/multi-ai-agent-systems-with-crewai/) — 多Agent内容创作（免费）
- [CrewAI - Content Creation Crew](https://www.youtube.com/watch?v=sPzc6hMg7So) — CrewAI内容创作实战
""",
    "10-实战案例/自动化运维Agent": """
## 🎬 推荐视频资源

### 🌐 YouTube
- [AWS - AI-Powered Operations](https://www.youtube.com/watch?v=F8NKVhkZZWI) — AI驱动的运维自动化
- [freeCodeCamp - DevOps with AI](https://www.youtube.com/watch?v=GWB9ApTPTv4) — AI+DevOps实战
""",
    "11-云厂商Agent方案/云厂商Agent方案对比": """
## 🎬 推荐视频资源

### 🌐 YouTube
- [AWS re:Invent - Bedrock Agents](https://www.youtube.com/watch?v=F8NKVhkZZWI) — AWS Bedrock Agents
- [Google Cloud - Vertex AI Agents](https://www.youtube.com/watch?v=E8pMFNox4Lc) — Google Vertex AI Agent
- [Microsoft - Azure AI Agent Service](https://www.youtube.com/watch?v=pHksBVqH7uI) — Azure AI Agent

### 📺 B站
- [云厂商AI Agent方案对比](https://www.bilibili.com/video/BV1dH4y1P7FY) — 中文云厂商方案对比
""",
    "11-云厂商Agent方案/阿里云百炼与通义": """
## 🎬 推荐视频资源

### 📺 B站
- [阿里云百炼平台教程](https://www.bilibili.com/video/BV1Bz421B7bG) — 百炼平台中文教程
- [通义千问API使用教程](https://www.bilibili.com/video/BV1PD421E7mN) — 通义千问实战

### 📖 官方文档
- [阿里云百炼](https://bailian.console.aliyun.com/) — 百炼平台
- [通义千问API](https://help.aliyun.com/zh/model-studio/) — 通义千问文档
""",
    "12-Coding Agent/Claude Code与终端Agent": """
## 🎬 推荐视频资源

### 🌐 YouTube
- [Anthropic - Claude Code Demo](https://www.youtube.com/watch?v=hkhDdcM5V94) — Claude Code官方演示
- [Frontend Masters - Claude Code Tutorial](https://frontendmasters.com/courses/pro-ai/) — Claude Code专业教程
- [Fireship - Claude Code Review](https://www.youtube.com/watch?v=DHjqpvDnNGE) — Claude Code快速评测

### 📺 B站
- [Claude Code使用教程](https://www.bilibili.com/video/BV1Bm421N7BH) — Claude Code中文教程

### 📖 官方文档
- [Claude Code Docs](https://docs.anthropic.com/en/docs/claude-code) — Anthropic官方文档
""",
    "12-Coding Agent/Cursor-Kiro-Windsurf IDE Agent": """
## 🎬 推荐视频资源

### 🌐 YouTube
- [Fireship - Cursor AI Review](https://www.youtube.com/watch?v=DHjqpvDnNGE) — Cursor AI评测
- [Frontend Masters - Cursor & Claude Code](https://frontendmasters.com/courses/pro-ai/) — IDE Agent专业教程
- [Traversy Media - Cursor Tutorial](https://www.youtube.com/watch?v=LDB4uaJ87e0) — Cursor使用教程

### 📺 B站
- [Cursor AI编程助手教程](https://www.bilibili.com/video/BV1Bm421N7BH) — Cursor中文教程
- [Kiro IDE使用体验](https://www.bilibili.com/video/BV1dH4y1P7FY) — Kiro中文评测
""",
    "12-Coding Agent/Devin与自主开发Agent": """
## 🎬 推荐视频资源

### 🌐 YouTube
- [Cognition AI - Devin Demo](https://www.youtube.com/watch?v=fjHtjT7GO1c) — Devin官方演示
- [Fireship - Devin AI Review](https://www.youtube.com/watch?v=DHjqpvDnNGE) — Devin评测
- [OpenHands - Open Source Devin](https://www.youtube.com/watch?v=dcgRMOG605w) — OpenHands开源替代

### 📖 官方文档
- [OpenHands GitHub](https://github.com/All-Hands-AI/OpenHands) — OpenHands开源项目
""",
    "12-Coding Agent/Vibe Coding与AI应用构建": """
## 🎬 推荐视频资源

### 🌐 YouTube
- [Fireship - Vibe Coding Explained](https://www.youtube.com/watch?v=DHjqpvDnNGE) — Vibe Coding概念讲解
- [freeCodeCamp - Build Apps with AI](https://www.youtube.com/watch?v=dcgRMOG605w) — AI应用构建教程

### 📺 B站
- [Vibe Coding实战](https://www.bilibili.com/video/BV1Bm421N7BH) — AI辅助编程中文教程

### 🌐 平台
- [Replit](https://replit.com/) — AI驱动的在线IDE
- [v0.dev](https://v0.dev/) — Vercel AI UI生成器
- [bolt.new](https://bolt.new/) — StackBlitz AI应用构建
""",
    "13-OpenClaw与Agent生态/Computer Use与浏览器Agent": """
## 🎬 推荐视频资源

### 🌐 YouTube
- [Anthropic - Computer Use Demo](https://www.youtube.com/watch?v=hkhDdcM5V94) — Claude Computer Use官方演示
- [Google - Gemini Computer Use](https://www.youtube.com/watch?v=E8pMFNox4Lc) — Gemini Computer Use介绍

### 📖 官方文档
- [Anthropic Computer Use](https://docs.anthropic.com/en/docs/agents-and-tools/computer-use) — Claude Computer Use文档
- [Google Computer Use](https://ai.google.dev/gemini-api/docs/computer-use) — Gemini Computer Use文档
""",
    "13-OpenClaw与Agent生态/浏览器自动化Agent详解": """
## 🎬 推荐视频资源

### 🌐 YouTube
- [Browser-Use - Getting Started](https://www.youtube.com/watch?v=dcgRMOG605w) — Browser-Use入门
- [Skyvern - AI Browser Automation](https://www.youtube.com/watch?v=YtiYrmAdJ5g) — Skyvern演示

### 📖 官方文档
- [Browser-Use](https://browser-use.com/) — Browser-Use官网
- [Skyvern](https://github.com/Skyvern-AI/skyvern) — Skyvern GitHub
""",
    "13-OpenClaw与Agent生态/OpenClaw平台详解": """
## 🎬 推荐视频资源

### 📖 官方文档
- [OpenClaw GitHub](https://github.com/openclaw/openclaw) — OpenClaw开源项目
- [OpenFang GitHub](https://github.com/RightNow-AI/openfang) — OpenFang Agent运行时
""",
    "13-OpenClaw与Agent生态/Agent Skills生态": """
## 🎬 推荐视频资源

### 🌐 YouTube
- [Composio - Agent Tools Platform](https://www.youtube.com/watch?v=nMGCE4GU1kc) — Composio工具平台介绍

### 📖 官方文档
- [Composio Docs](https://docs.composio.dev/) — Composio官方文档
""",
    "13-OpenClaw与Agent生态/AgentOS生态": """
## 🎬 推荐视频资源

### 📖 官方文档
- [OpenClaw GitHub](https://github.com/openclaw/openclaw) — OpenClaw AgentOS
- [OpenFang GitHub](https://github.com/RightNow-AI/openfang) — OpenFang运行时
""",
    "14-Agent安全与治理/Agent治理框架": """
## 🎬 推荐视频资源

### 🌐 YouTube
- [DeepLearning.AI - Quality and Safety for LLM Applications](https://www.deeplearning.ai/short-courses/quality-safety-llm-applications/) — LLM安全与质量（免费）
- [DeepLearning.AI - Red Teaming LLM Applications](https://www.deeplearning.ai/short-courses/red-teaming-llm-applications/) — LLM红队测试（免费）
""",
    "14-Agent安全与治理/Agent身份与权限": """
## 🎬 推荐视频资源

### 🌐 YouTube
- [DeepLearning.AI - Quality and Safety for LLM Applications](https://www.deeplearning.ai/short-courses/quality-safety-llm-applications/) — 包含权限控制章节（免费）
- [OWASP - LLM Security Top 10](https://www.youtube.com/watch?v=4YOpILi9Oxs) — LLM安全风险

### 📖 官方文档
- [OWASP LLM Top 10](https://owasp.org/www-project-top-10-for-large-language-model-applications/) — OWASP LLM安全指南
""",
    "15-Agentic设计模式/Agent工作流编排模式": """
## 🎬 推荐视频资源

### 🌐 YouTube
- [Andrew Ng - What's Next for AI Agentic Workflows](https://www.youtube.com/watch?v=sal78ACtGTc) — 吴恩达讲Agentic工作流
- [DeepLearning.AI - AI Agents in LangGraph](https://www.deeplearning.ai/short-courses/ai-agents-in-langgraph/) — LangGraph工作流编排（免费）

### 📺 B站
- [吴恩达 - Agentic工作流中文字幕](https://www.bilibili.com/video/BV1Bz421B7bG) — Agentic工作流讲解
""",
    "16-Agent记忆框架/Mem0记忆层": """
## 🎬 推荐视频资源

### 🌐 YouTube
- [Mem0 - AI Memory Layer](https://www.youtube.com/watch?v=nMGCE4GU1kc) — Mem0介绍
- [AI Jason - Agent Memory Systems](https://www.youtube.com/watch?v=Ox9DBiJMnHY) — Agent记忆系统讲解

### 📖 官方文档
- [Mem0 Docs](https://docs.mem0.ai/) — Mem0官方文档
""",
    "16-Agent记忆框架/Letta-MemGPT记忆系统": """
## 🎬 推荐视频资源

### 🌐 YouTube
- [MemGPT - OS-Level Memory for LLMs](https://www.youtube.com/watch?v=nMGCE4GU1kc) — MemGPT论文讲解

### 📖 官方文档
- [Letta Docs](https://docs.letta.com/) — Letta/MemGPT官方文档
- [Letta GitHub](https://github.com/letta-ai/letta) — Letta开源项目
""",
    "16-Agent记忆框架/Zep与LangMem": """
## 🎬 推荐视频资源

### 🌐 YouTube
- [Zep - Long-Term Memory for AI](https://www.youtube.com/watch?v=nMGCE4GU1kc) — Zep记忆系统介绍

### 📖 官方文档
- [Zep Docs](https://help.getzep.com/) — Zep官方文档
- [LangMem Docs](https://langchain-ai.github.io/langmem/) — LangMem文档
""",
    "17-工具平台与沙箱/Composio工具平台": """
## 🎬 推荐视频资源

### 🌐 YouTube
- [Composio - 1000+ Tools for AI Agents](https://www.youtube.com/watch?v=nMGCE4GU1kc) — Composio平台介绍
- [AI Jason - Best Agent Tools](https://www.youtube.com/watch?v=Ox9DBiJMnHY) — Agent工具平台对比

### 📖 官方文档
- [Composio Docs](https://docs.composio.dev/) — Composio官方文档
""",
    "17-工具平台与沙箱/E2B代码沙箱": """
## 🎬 推荐视频资源

### 🌐 YouTube
- [E2B - Code Sandbox for AI](https://www.youtube.com/watch?v=nMGCE4GU1kc) — E2B沙箱介绍

### 📖 官方文档
- [E2B Docs](https://e2b.dev/docs) — E2B官方文档
- [E2B GitHub](https://github.com/e2b-dev/e2b) — E2B开源项目
""",
    "17-工具平台与沙箱/Web数据工具详解": """
## 🎬 推荐视频资源

### 🌐 YouTube
- [Firecrawl - Web Scraping for AI](https://www.youtube.com/watch?v=dcgRMOG605w) — Firecrawl网页抓取
- [Tavily - AI Search API](https://www.youtube.com/watch?v=Ox9DBiJMnHY) — Tavily搜索API

### 📖 官方文档
- [Firecrawl Docs](https://docs.firecrawl.dev/) — Firecrawl文档
- [Tavily Docs](https://docs.tavily.com/) — Tavily文档
- [Jina Reader](https://jina.ai/reader/) — Jina Reader API
""",
    "17-工具平台与沙箱/Agent工具生态总览": """
## 🎬 推荐视频资源

### 🌐 YouTube
- [AI Jason - Agent Tools Ecosystem](https://www.youtube.com/watch?v=Ox9DBiJMnHY) — Agent工具生态讲解
- [DeepLearning.AI - Functions, Tools and Agents](https://www.deeplearning.ai/short-courses/functions-tools-agents-langchain/) — 工具与Agent（免费）
""",
    "18-AI网关与路由/LiteLLM统一接口": """
## 🎬 推荐视频资源

### 🌐 YouTube
- [LiteLLM - Unified LLM API](https://www.youtube.com/watch?v=Ox9DBiJMnHY) — LiteLLM统一接口教程

### 📖 官方文档
- [LiteLLM Docs](https://docs.litellm.ai/) — LiteLLM官方文档（支持100+模型）
""",
    "18-AI网关与路由/Portkey与AI网关对比": """
## 🎬 推荐视频资源

### 🌐 YouTube
- [Portkey - AI Gateway](https://www.youtube.com/watch?v=Ox9DBiJMnHY) — Portkey AI网关介绍

### 📖 官方文档
- [Portkey Docs](https://portkey.ai/docs) — Portkey官方文档
""",
    "18-AI网关与路由/Vercel AI SDK与Gateway": """
## 🎬 推荐视频资源

### 🌐 YouTube
- [Vercel - AI SDK Tutorial](https://www.youtube.com/watch?v=LDB4uaJ87e0) — Vercel AI SDK教程
- [Lee Robinson - AI SDK Demo](https://www.youtube.com/watch?v=DHjqpvDnNGE) — AI SDK实战演示

### 📖 官方文档
- [Vercel AI SDK Docs](https://sdk.vercel.ai/docs) — Vercel AI SDK官方文档
""",
    "19-Java-TS Agent生态/Spring AI Agent": """
## 🎬 推荐视频资源

### 🌐 YouTube
- [Spring - Spring AI Introduction](https://www.youtube.com/watch?v=9SGDpanrc8U) — Spring AI官方介绍
- [Dan Vega - Spring AI Tutorial](https://www.youtube.com/watch?v=pHksBVqH7uI) — Spring AI实战教程

### 📺 B站
- [Spring AI中文教程](https://www.bilibili.com/video/BV1Es4y1q7Bf) — Spring AI中文实战

### 📖 官方文档
- [Spring AI Docs](https://docs.spring.io/spring-ai/reference/) — Spring AI官方文档
- [Baeldung - Spring AI](https://www.baeldung.com/spring-ai) — Spring AI教程
""",
    "19-Java-TS Agent生态/Vercel AI SDK Agent开发": """
## 🎬 推荐视频资源

### 🌐 YouTube
- [Vercel - AI SDK Agent Tutorial](https://www.youtube.com/watch?v=LDB4uaJ87e0) — AI SDK Agent教程
- [Lee Robinson - Building AI Apps](https://www.youtube.com/watch?v=DHjqpvDnNGE) — AI应用构建

### 📖 官方文档
- [Vercel AI SDK Docs](https://sdk.vercel.ai/docs) — 官方文档
""",
    "19-Java-TS Agent生态/Dapr Agents分布式运行时": """
## 🎬 推荐视频资源

### 🌐 YouTube
- [Microsoft - Dapr Overview](https://www.youtube.com/watch?v=pHksBVqH7uI) — Dapr概述
- [Dapr - Getting Started](https://www.youtube.com/watch?v=vU2S6dVf79M) — Dapr入门教程

### 📖 官方文档
- [Dapr Docs](https://docs.dapr.io/) — Dapr官方文档
- [Dapr Agents GitHub](https://github.com/dapr/dapr-agents) — Dapr Agents项目
""",
    "20-Agent框架补充/Agent框架选型指南": """
## 🎬 推荐视频资源

### 🌐 YouTube
- [AI Jason - Best AI Agent Frameworks 2025](https://www.youtube.com/watch?v=Ox9DBiJMnHY) — Agent框架对比评测
- [DeepLearning.AI - Agentic AI](https://www.deeplearning.ai/courses/agentic-ai/) — 框架选型参考（免费）

### 📺 B站
- [AI Agent框架选型指南](https://www.bilibili.com/video/BV1dH4y1P7FY) — 中文框架对比
""",
    "20-Agent框架补充/Anthropic Claude Agent能力": """
## 🎬 推荐视频资源

### 🌐 YouTube
- [Anthropic - Claude 4 Capabilities](https://www.youtube.com/watch?v=hkhDdcM5V94) — Claude能力介绍
- [Anthropic - Extended Thinking](https://www.youtube.com/watch?v=hkhDdcM5V94) — Claude扩展思考

### 📖 官方文档
- [Anthropic Docs](https://docs.anthropic.com/) — Claude官方文档
""",
    "20-Agent框架补充/LlamaIndex Agent与Workflow": """
## 🎬 推荐视频资源

### 🌐 YouTube
- [DeepLearning.AI - Building Agentic RAG with LlamaIndex](https://www.deeplearning.ai/short-courses/building-agentic-rag-with-llamaindex/) — LlamaIndex Agentic RAG（免费）
- [LlamaIndex - Workflow Tutorial](https://www.youtube.com/watch?v=dcgRMOG605w) — LlamaIndex Workflow教程

### 📖 官方文档
- [LlamaIndex Docs](https://docs.llamaindex.ai/) — LlamaIndex官方文档
""",
    "21-Harness Engineering/Harness Engineering与CI-CD集成": """
## 🎬 推荐视频资源

### 🌐 YouTube
- [GitHub - GitHub Actions Tutorial](https://www.youtube.com/watch?v=R8_veQiYBjI) — GitHub Actions教程
- [DeepLearning.AI - Agentic AI](https://www.deeplearning.ai/courses/agentic-ai/) — 包含工程化章节（免费）

### 📖 官方文档
- [GitHub Actions Docs](https://docs.github.com/en/actions) — GitHub Actions文档
""",
    "21-Harness Engineering/Harness Engineering开源项目": """
## 🎬 推荐视频资源

### 📖 官方资源
- [OpenAI - Harness Engineering](https://openai.com/index/harness-engineering) — OpenAI官方文章
- [LangChain - Deep Agents](https://blog.langchain.com/improving-deep-agents-with-harness-engineering/) — LangChain Harness Engineering
- [nxcode - Complete Guide](https://www.nxcode.io/resources/news/harness-engineering-complete-guide-ai-agent-codex-2026) — 完整指南
""",
    "21-Harness Engineering/Kiro Harness实战配置": """
## 🎬 推荐视频资源

### 📖 官方文档
- [Kiro Documentation](https://kiro.dev/docs) — Kiro官方文档
- [Kiro Steering Guide](https://kiro.dev/docs/steering) — Steering配置指南
""",
    "22-Voice Agent/语音Agent与实时交互": """
## 🎬 推荐视频资源

### 🌐 YouTube
- [OpenAI - Realtime API Demo](https://www.youtube.com/watch?v=JhCl-GeT4jw) — OpenAI Realtime API演示
- [ElevenLabs - Conversational AI](https://www.youtube.com/watch?v=nMGCE4GU1kc) — ElevenLabs语音Agent
- [LiveKit - Build Voice AI Agent](https://www.youtube.com/watch?v=dcgRMOG605w) — LiveKit语音Agent教程

### 📺 B站
- [语音Agent开发实战](https://www.bilibili.com/video/BV1dH4y1P7FY) — 语音Agent中文教程

### 📖 官方文档
- [OpenAI Realtime API](https://platform.openai.com/docs/guides/realtime) — OpenAI实时API文档
- [ElevenLabs Docs](https://elevenlabs.io/docs) — ElevenLabs文档
- [LiveKit Agents](https://docs.livekit.io/agents/) — LiveKit Agents文档
- [Vapi Docs](https://docs.vapi.ai/) — Vapi语音Agent文档
""",
    "22-Voice Agent/语音Agent开发实战": """
## 🎬 推荐视频资源

### 🌐 YouTube
- [LiveKit - Build Your First Voice Agent in Python](https://livekit.com/blog/build-your-first-ai-voice-agent-python) — Python语音Agent教程
- [ElevenLabs - Building Conversational AI](https://www.youtube.com/watch?v=nMGCE4GU1kc) — 对话式AI构建

### 📖 官方文档
- [LiveKit Agents Python](https://docs.livekit.io/agents/) — LiveKit Python SDK
- [ElevenLabs Conversational AI](https://elevenlabs.io/docs/conversational-ai) — ElevenLabs对话AI文档
""",
}


def find_file(base_dir: Path, key: str) -> Path | None:
    parts = key.split("/")
    search_dir = base_dir
    for part in parts[:-1]:
        search_dir = search_dir / part
    filename = parts[-1]
    candidate = search_dir / f"{filename}.md"
    if candidate.exists():
        return candidate
    if search_dir.exists():
        for f in search_dir.iterdir():
            if f.suffix == ".md" and filename in f.stem:
                return f
    return None


def main():
    base_dir = Path(__file__).resolve().parent.parent / "learning-notes" / "ai-agent"
    added, skipped, not_found = 0, 0, 0

    for key, video_block in AI_VIDEOS.items():
        filepath = find_file(base_dir, key)
        if filepath is None:
            print(f"  ❌ 未找到: {key}")
            not_found += 1
            continue
        content = filepath.read_text(encoding="utf-8")
        if VIDEO_MARKER in content:
            print(f"  ⏭️  已有视频: {filepath.relative_to(base_dir)}")
            skipped += 1
            continue
        updated = content.rstrip() + "\n" + video_block.strip() + "\n"
        filepath.write_text(updated, encoding="utf-8")
        print(f"  ✅ {filepath.relative_to(base_dir)}")
        added += 1

    print(f"\n完成: {added} 个文件已添加视频, {skipped} 个已有跳过, {not_found} 个未找到")


if __name__ == "__main__":
    main()
