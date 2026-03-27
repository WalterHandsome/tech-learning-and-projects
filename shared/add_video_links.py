#!/usr/bin/env python3
"""批量为学习笔记文档添加推荐视频链接"""

import re
from pathlib import Path

# 视频资源映射：文件路径关键词 -> 视频推荐区块
VIDEO_MAP = {
    # ==================== AI Agent ====================
    "ai-agent/00-基础概念/AI Agent概述与发展": """
## 🎬 推荐视频资源

- [Andrej Karpathy - Intro to Large Language Models](https://www.youtube.com/watch?v=zjkBMFhNj_g) — 1小时LLM入门概述，前Tesla AI总监讲解
- [Andrew Ng - AI For Everyone](https://www.coursera.org/learn/ai-for-everyone) — 吴恩达非技术角度理解AI全貌（免费）
- [DeepLearning.AI - Agentic AI with Andrew Ng](https://www.deeplearning.ai/courses/agentic-ai/) — Agentic AI全面讲解（免费）
- [IBM Technology - What are AI Agents?](https://www.youtube.com/watch?v=F8NKVhkZZWI) — 5分钟快速理解AI Agent
""",
    "ai-agent/00-基础概念/大语言模型基础": """
## 🎬 推荐视频资源

- [Andrej Karpathy - Let's Build GPT from Scratch](https://www.youtube.com/watch?v=kCc8FmEb1nY) — 2小时手写GPT，深入理解Transformer
- [3Blue1Brown - Neural Networks](https://www.youtube.com/playlist?list=PLZHQObOWTQDNU6R1_67000Dx_ZCJB-3pi) — 神经网络可视化讲解，全网最直观
- [3Blue1Brown - How LLMs Store Facts](https://www.youtube.com/watch?v=9-Jl0dxWQs8) — LLM如何存储知识的可视化解释
- [Andrej Karpathy - Neural Networks: Zero to Hero](https://www.youtube.com/playlist?list=PLAqhIrjkxbuWI23v9cThsA9GvCAUhRvKZ) — 从零手写神经网络到GPT完整系列
""",
    "ai-agent/00-基础概念/Prompt Engineering": """
## 🎬 推荐视频资源

- [DeepLearning.AI - ChatGPT Prompt Engineering for Developers](https://www.deeplearning.ai/short-courses/chatgpt-prompt-engineering-for-developers/) — 吴恩达+OpenAI联合出品（免费）
- [DeepLearning.AI - Building Systems with ChatGPT API](https://www.deeplearning.ai/short-courses/building-systems-with-chatgpt/) — 构建基于LLM的系统（免费）
- [freeCodeCamp - Prompt Engineering Tutorial](https://www.youtube.com/watch?v=_ZvnD96BbQ0) — 完整Prompt工程教程
""",
    "ai-agent/01-Agent协议/MCP模型上下文协议": """
## 🎬 推荐视频资源

- [Anthropic - Model Context Protocol Introduction](https://www.youtube.com/watch?v=kQmXtrmQ5Zg) — MCP官方介绍
- [freeCodeCamp - MCP Crash Course](https://www.youtube.com/watch?v=JBqLV4MnN3E) — MCP完整教程
- [AI Jason - MCP Explained](https://www.youtube.com/watch?v=Ox9DBiJMnHY) — MCP协议通俗讲解
""",
    "ai-agent/01-Agent协议/A2A Agent间通信协议": """
## 🎬 推荐视频资源

- [Google Cloud - A2A Protocol Overview](https://www.youtube.com/watch?v=4Fy0gDqSVOg) — Google官方A2A协议介绍
- [AI Jason - A2A vs MCP](https://www.youtube.com/watch?v=4Fy0gDqSVOg) — A2A与MCP对比讲解
""",
    "ai-agent/01-Agent协议/Agent协议全景图": """
## 🎬 推荐视频资源

- [Anthropic - Model Context Protocol](https://www.youtube.com/watch?v=kQmXtrmQ5Zg) — MCP官方介绍
- [Google Cloud - A2A Protocol](https://www.youtube.com/watch?v=4Fy0gDqSVOg) — A2A协议介绍
- [AI Jason - Agent Protocols Explained](https://www.youtube.com/watch?v=Ox9DBiJMnHY) — Agent协议生态讲解
""",
    "ai-agent/02-Agent框架/LangGraph工作流编排": """
## 🎬 推荐视频资源

- [DeepLearning.AI - AI Agents in LangGraph](https://www.deeplearning.ai/short-courses/ai-agents-in-langgraph/) — 吴恩达+LangChain联合出品（免费）
- [freeCodeCamp - How to Develop AI Agents Using LangGraph](https://www.youtube.com/watch?v=dcgRMOG605w) — LangGraph实战指南
- [LangChain Official - LangGraph Tutorial](https://www.youtube.com/watch?v=9BPCV5TYPmg) — 官方教程
""",
    "ai-agent/02-Agent框架/CrewAI多Agent协作": """
## 🎬 推荐视频资源

- [DeepLearning.AI - Multi AI Agent Systems with crewAI](https://www.deeplearning.ai/short-courses/multi-ai-agent-systems-with-crewai/) — 吴恩达出品多Agent系统（免费）
- [CrewAI Official - Getting Started](https://www.youtube.com/watch?v=sPzc6hMg7So) — CrewAI官方入门
- [Matt Williams - CrewAI Tutorial](https://www.youtube.com/watch?v=tnejrr-0a94) — CrewAI完整教程
""",
    "ai-agent/02-Agent框架/OpenAI Agents SDK": """
## 🎬 推荐视频资源

- [OpenAI - Agents SDK Introduction](https://www.youtube.com/watch?v=JhCl-GeT4jw) — OpenAI官方Agents SDK介绍
- [DeepLearning.AI - Building Agentic RAG with LlamaIndex](https://www.deeplearning.ai/short-courses/building-agentic-rag-with-llamaindex/) — Agentic RAG实战（免费）
""",
    "ai-agent/02-Agent框架/Google ADK详解": """
## 🎬 推荐视频资源

- [Google Cloud - Agent Development Kit](https://www.youtube.com/watch?v=E8pMFNox4Lc) — Google ADK官方介绍
- [Google Cloud - Building AI Agents with ADK](https://www.youtube.com/watch?v=3Vy0V3sBhAo) — ADK实战教程
""",
    "ai-agent/03-RAG进阶/RAG架构与核心流程": """
## 🎬 推荐视频资源

- [DeepLearning.AI - Building and Evaluating Advanced RAG](https://www.deeplearning.ai/short-courses/building-evaluating-advanced-rag/) — 高级RAG构建与评估（免费）
- [freeCodeCamp - RAG Tutorial](https://www.youtube.com/watch?v=T-D1OfcDW1M) — RAG完整教程
- [DeepLearning.AI - LangChain Chat with Your Data](https://www.deeplearning.ai/short-courses/langchain-chat-with-your-data/) — 用LangChain构建RAG（免费）
""",
    "ai-agent/03-RAG进阶/向量数据库选型": """
## 🎬 推荐视频资源

- [Fireship - Vector Databases Explained](https://www.youtube.com/watch?v=klTvEwg3oJ4) — 向量数据库100秒讲解
- [freeCodeCamp - Vector Databases Course](https://www.youtube.com/watch?v=BYoEwMEgwIo) — 向量数据库完整课程
""",
    "ai-agent/03-RAG进阶/高级RAG策略": """
## 🎬 推荐视频资源

- [DeepLearning.AI - Advanced Retrieval for AI with Chroma](https://www.deeplearning.ai/short-courses/advanced-retrieval-for-ai/) — 高级检索策略（免费）
- [DeepLearning.AI - Building Agentic RAG with LlamaIndex](https://www.deeplearning.ai/short-courses/building-agentic-rag-with-llamaindex/) — Agentic RAG（免费）
""",
    "ai-agent/03-RAG进阶/GraphRAG知识图谱": """
## 🎬 推荐视频资源

- [Microsoft Research - GraphRAG](https://www.youtube.com/watch?v=r09tJfnassM) — 微软GraphRAG官方讲解
- [DeepLearning.AI - Knowledge Graphs for RAG](https://www.deeplearning.ai/short-courses/knowledge-graphs-rag/) — 知识图谱+RAG（免费）
""",
    "ai-agent/04-工具与Function Calling/Function Calling机制": """
## 🎬 推荐视频资源

- [DeepLearning.AI - Functions, Tools and Agents with LangChain](https://www.deeplearning.ai/short-courses/functions-tools-agents-langchain/) — Function Calling实战（免费）
- [OpenAI - Function Calling Guide](https://www.youtube.com/watch?v=0lOSvOoF2to) — OpenAI Function Calling讲解
""",
    "ai-agent/04-工具与Function Calling/MCP Server开发": """
## 🎬 推荐视频资源

- [freeCodeCamp - MCP Crash Course](https://www.youtube.com/watch?v=JBqLV4MnN3E) — MCP Server开发完整教程
- [Anthropic - Building MCP Servers](https://www.youtube.com/watch?v=kQmXtrmQ5Zg) — 官方MCP Server开发指南
""",
    "ai-agent/05-多Agent系统/多Agent架构模式": """
## 🎬 推荐视频资源

- [DeepLearning.AI - Multi AI Agent Systems with crewAI](https://www.deeplearning.ai/short-courses/multi-ai-agent-systems-with-crewai/) — 多Agent系统实战（免费）
- [DeepLearning.AI - AI Agentic Design Patterns with AutoGen](https://www.deeplearning.ai/short-courses/ai-agentic-design-patterns-with-autogen/) — Agentic设计模式（免费）
""",
    "ai-agent/06-记忆与状态/短期与长期记忆": """
## 🎬 推荐视频资源

- [DeepLearning.AI - LangChain Chat with Your Data](https://www.deeplearning.ai/short-courses/langchain-chat-with-your-data/) — 对话记忆管理（免费）
- [LangChain - Memory in LangGraph](https://www.youtube.com/watch?v=9BPCV5TYPmg) — LangGraph中的记忆机制
""",
    "ai-agent/07-模型服务/OpenAI与Claude API": """
## 🎬 推荐视频资源

- [DeepLearning.AI - ChatGPT Prompt Engineering for Developers](https://www.deeplearning.ai/short-courses/chatgpt-prompt-engineering-for-developers/) — OpenAI API实战（免费）
- [Anthropic - Claude API Tutorial](https://www.youtube.com/watch?v=hkhDdcM5V94) — Claude API使用教程
""",
    "ai-agent/07-模型服务/开源模型部署": """
## 🎬 推荐视频资源

- [Andrej Karpathy - Let's Reproduce GPT-2](https://www.youtube.com/watch?v=l8pRSuU81PU) — 从零复现GPT-2
- [freeCodeCamp - Ollama Course](https://www.youtube.com/watch?v=GWB9ApTPTv4) — Ollama本地部署开源模型
""",
    "ai-agent/08-可观测与评估/LLM可观测性": """
## 🎬 推荐视频资源

- [DeepLearning.AI - Evaluating and Debugging Generative AI](https://www.deeplearning.ai/short-courses/evaluating-debugging-generative-ai/) — LLM评估与调试（免费）
- [LangSmith - Getting Started](https://www.youtube.com/watch?v=tFXm5ijih98) — LangSmith可观测性平台入门
""",
    "ai-agent/09-低代码平台/Dify平台实践": """
## 🎬 推荐视频资源

- [Dify Official - Getting Started](https://www.youtube.com/watch?v=1gNMnQH0vRc) — Dify官方入门教程
- [AI Jason - Dify Tutorial](https://www.youtube.com/watch?v=CgMd0zsz_BQ) — Dify平台实战讲解
""",
    "ai-agent/15-Agentic设计模式/Anthropic Agent设计模式": """
## 🎬 推荐视频资源

- [DeepLearning.AI - Agentic AI with Andrew Ng](https://www.deeplearning.ai/courses/agentic-ai/) — Agentic设计模式全面讲解（免费）
- [DeepLearning.AI - AI Agentic Design Patterns with AutoGen](https://www.deeplearning.ai/short-courses/ai-agentic-design-patterns-with-autogen/) — 设计模式实战（免费）
""",
    "ai-agent/15-Agentic设计模式/Agentic设计模式大全": """
## 🎬 推荐视频资源

- [Andrew Ng - What's Next for AI Agentic Workflows](https://www.youtube.com/watch?v=sal78ACtGTc) — 吴恩达讲Agentic工作流
- [DeepLearning.AI - Agentic AI with Andrew Ng](https://www.deeplearning.ai/courses/agentic-ai/) — Agentic AI完整课程（免费）
""",
    "ai-agent/21-Harness Engineering/Harness Engineering完整指南": """
## 🎬 推荐视频资源

- [DeepLearning.AI - Agentic AI with Andrew Ng](https://www.deeplearning.ai/courses/agentic-ai/) — 包含Harness Engineering理念（免费）
- [OpenAI - Harness Engineering Blog](https://openai.com/index/harness-engineering) — OpenAI官方Harness Engineering文章
""",
    "ai-agent/21-Harness Engineering/Context Engineering详解": """
## 🎬 推荐视频资源

- [LangChain - Context Engineering for AI Agents](https://www.youtube.com/watch?v=9BPCV5TYPmg) — Context Engineering实战
- [DeepLearning.AI - Building Systems with ChatGPT API](https://www.deeplearning.ai/short-courses/building-systems-with-chatgpt/) — 系统级上下文管理（免费）
""",
    # ==================== Python ====================
    "python/00-Python基础/Python简介与安装": """
## 🎬 推荐视频资源

- [freeCodeCamp - Python Full Course for Beginners](https://www.youtube.com/watch?v=rfscVS0vtbw) — 4.5小时Python完整入门
- [Programming with Mosh - Python Tutorial](https://www.youtube.com/watch?v=_uQrJ0TkZlc) — 6小时Python入门教程
- [Corey Schafer - Python Tutorials](https://www.youtube.com/playlist?list=PL-osiE80TeTt2d9bfVyTiXJA-UTHn6WwU) — Python系统教程系列
""",
    "python/00-Python基础/Python变量与数据类型": """
## 🎬 推荐视频资源

- [Corey Schafer - Python Data Types](https://www.youtube.com/watch?v=khKv-8q7YmY) — Python数据类型详解
- [Programming with Mosh - Python Tutorial](https://www.youtube.com/watch?v=_uQrJ0TkZlc) — 包含变量与类型章节
""",
    "python/00-Python基础/Python函数": """
## 🎬 推荐视频资源

- [Corey Schafer - Python Functions](https://www.youtube.com/watch?v=9Os0o3wzS_I) — Python函数详解
- [Corey Schafer - Decorators](https://www.youtube.com/watch?v=FsAPt_9Bf3U) — 装饰器深入讲解
""",
    "python/00-Python基础/Python面向对象编程": """
## 🎬 推荐视频资源

- [Corey Schafer - Python OOP Tutorial](https://www.youtube.com/playlist?list=PL-osiE80TeTsqhIuOqKhwlXsIBIdSeYtc) — Python OOP完整系列（6集）
- [Tech With Tim - Python OOP](https://www.youtube.com/watch?v=JeznW_7DlB0) — OOP快速入门
""",
    "python/00-Python基础/Python高级特性": """
## 🎬 推荐视频资源

- [Corey Schafer - Generators](https://www.youtube.com/watch?v=bD05uGo_sVI) — 生成器详解
- [Corey Schafer - Context Managers](https://www.youtube.com/watch?v=-aKFBoZpiqA) — 上下文管理器
- [mCoding - Python Expert Tips](https://www.youtube.com/c/mCodingWithJamesMurphy) — Python高级技巧频道
""",
    "python/01-Web开发/FastAPI快速入门": """
## 🎬 推荐视频资源

- [freeCodeCamp - FastAPI Course](https://www.youtube.com/watch?v=0sOvCWFmrtA) — FastAPI完整课程（19小时）
- [Bitfumes - FastAPI Tutorial](https://www.youtube.com/watch?v=7t2alSnE2-I) — FastAPI快速入门
- [ArjanCodes - FastAPI Best Practices](https://www.youtube.com/watch?v=B9hLkfzgq0s) — FastAPI最佳实践
""",
    "python/01-Web开发/Django基础": """
## 🎬 推荐视频资源

- [freeCodeCamp - Django Web Framework](https://www.youtube.com/watch?v=F5mRW0jo-U4) — Django完整课程
- [Corey Schafer - Django Tutorial](https://www.youtube.com/playlist?list=PL-osiE80TeTtoQCKZ03TU5fNfx2UY6U4p) — Django系统教程系列
- [Dennis Ivy - Django Crash Course](https://www.youtube.com/watch?v=PtQiiknWUcI) — Django快速入门
""",
    "python/01-Web开发/Flask基础": """
## 🎬 推荐视频资源

- [freeCodeCamp - Flask Tutorial](https://www.youtube.com/watch?v=Qr4QMBUPxWo) — Flask完整教程
- [Corey Schafer - Flask Tutorial](https://www.youtube.com/playlist?list=PL-osiE80TeTs4UjLw5MM6OjgkjFeUxCYH) — Flask系统教程系列
- [Tech With Tim - Flask Tutorial](https://www.youtube.com/watch?v=mqhxxeeTbu0) — Flask快速入门
""",
    "python/02-数据分析/NumPy应用": """
## 🎬 推荐视频资源

- [freeCodeCamp - NumPy Full Course](https://www.youtube.com/watch?v=QUT1VHiLmmI) — NumPy完整教程
- [Keith Galli - NumPy Tutorial](https://www.youtube.com/watch?v=GB9ByFAIAH4) — NumPy实战教程
""",
    "python/02-数据分析/Pandas应用": """
## 🎬 推荐视频资源

- [freeCodeCamp - Pandas Full Course](https://www.youtube.com/watch?v=gtjxAH8uaP0) — Pandas完整教程
- [Corey Schafer - Pandas Tutorial](https://www.youtube.com/playlist?list=PL-osiE80TeTsWmV9i9c58mdDCSskIFdDS) — Pandas系统教程系列
- [Keith Galli - Pandas Tutorial](https://www.youtube.com/watch?v=vmEHCJofslg) — Pandas实战教程
""",
    "python/02-数据分析/数据可视化": """
## 🎬 推荐视频资源

- [Corey Schafer - Matplotlib Tutorial](https://www.youtube.com/playlist?list=PL-osiE80TeTvipOqomVEeZ1HRrcEvtZB_) — Matplotlib系统教程
- [freeCodeCamp - Data Visualization with Python](https://www.youtube.com/watch?v=a9UrKTVEeZA) — Python数据可视化完整课程
""",
    "python/03-机器学习/浅谈机器学习": """
## 🎬 推荐视频资源

- [Andrew Ng - Machine Learning Specialization](https://www.coursera.org/specializations/machine-learning-introduction) — 吴恩达机器学习（Coursera免费旁听）
- [StatQuest - Machine Learning](https://www.youtube.com/playlist?list=PLblh5JKOoLUICTaGLRoHQDuF_7q2GfuJF) — 机器学习概念可视化讲解
- [3Blue1Brown - Neural Networks](https://www.youtube.com/playlist?list=PLZHQObOWTQDNU6R1_67000Dx_ZCJB-3pi) — 神经网络可视化
""",
    "python/03-机器学习/RAG检索增强生成": """
## 🎬 推荐视频资源

- [DeepLearning.AI - LangChain Chat with Your Data](https://www.deeplearning.ai/short-courses/langchain-chat-with-your-data/) — RAG实战（免费）
- [freeCodeCamp - RAG Tutorial](https://www.youtube.com/watch?v=T-D1OfcDW1M) — RAG完整教程
""",
    "python/03-机器学习/LangChain框架应用": """
## 🎬 推荐视频资源

- [DeepLearning.AI - LangChain for LLM Application Development](https://www.deeplearning.ai/short-courses/langchain-for-llm-application-development/) — LangChain入门（免费）
- [freeCodeCamp - LangChain Tutorial](https://www.youtube.com/watch?v=lG7Uxts9SXs) — LangChain完整教程
""",
    "python/03-机器学习/深度学习框架应用": """
## 🎬 推荐视频资源

- [freeCodeCamp - PyTorch Full Course](https://www.youtube.com/watch?v=V_xro1bcAuA) — PyTorch完整课程
- [freeCodeCamp - TensorFlow Full Course](https://www.youtube.com/watch?v=tPYj3fFJGjk) — TensorFlow完整课程
- [Andrej Karpathy - Neural Networks: Zero to Hero](https://www.youtube.com/playlist?list=PLAqhIrjkxbuWI23v9cThsA9GvCAUhRvKZ) — 从零构建神经网络
""",
    "python/04-并发编程/Python并发编程": """
## 🎬 推荐视频资源

- [Corey Schafer - Threading Tutorial](https://www.youtube.com/watch?v=IEEhzQoKtQU) — Python多线程教程
- [Corey Schafer - Multiprocessing](https://www.youtube.com/watch?v=fKl2JW_qrso) — Python多进程教程
- [ArjanCodes - Async Python](https://www.youtube.com/watch?v=2IW-ZEui4h4) — Python异步编程
""",
    # ==================== Java ====================
    "java/00-Java基础/JVM内存模型与垃圾回收": """
## 🎬 推荐视频资源

- [Amigoscode - JVM Tutorial](https://www.youtube.com/watch?v=QHIWkwxs0AI) — JVM内存模型讲解
- [Java Brains - JVM Architecture](https://www.youtube.com/watch?v=ZBJ0u9MaKtM) — JVM架构详解
""",
    "java/00-Java基础/Java并发编程": """
## 🎬 推荐视频资源

- [Jakob Jenkov - Java Concurrency](https://www.youtube.com/playlist?list=PLL8woMHwr36EDxjUoCzboZjedsnhLP1j4) — Java并发编程完整系列
- [Defog Tech - Java Multithreading](https://www.youtube.com/playlist?list=PLhfHPmPYPPRk6yMrcbfafFGSbE2EPK_A6) — Java多线程教程
""",
    "java/00-Java基础/Java集合框架": """
## 🎬 推荐视频资源

- [Java Brains - Java Collections](https://www.youtube.com/watch?v=GdAon80-0KA) — Java集合框架详解
- [Coding with John - Java Collections](https://www.youtube.com/watch?v=viTainYWwbI) — 集合框架实战
""",
    "java/01-框架/Spring基础01": """
## 🎬 推荐视频资源

- [Amigoscode - Spring Boot Tutorial](https://www.youtube.com/watch?v=9SGDpanrc8U) — Spring Boot完整教程
- [Java Brains - Spring Framework](https://www.youtube.com/playlist?list=PLqq-6Pq4lTTbx8p2oCgcAQGQyqN8XeA1) — Spring框架系统教程
- [freeCodeCamp - Spring Boot Full Course](https://www.youtube.com/watch?v=31KTdfRH6nY) — Spring Boot完整课程
""",
    "java/01-框架/SpringBoot基础": """
## 🎬 推荐视频资源

- [Amigoscode - Spring Boot Tutorial 2025](https://www.youtube.com/watch?v=9SGDpanrc8U) — Spring Boot完整教程
- [Programming with Mosh - Spring Boot Tutorial](https://www.youtube.com/watch?v=31KTdfRH6nY) — Spring Boot入门
- [Daily Code Buffer - Spring Boot Microservices](https://www.youtube.com/watch?v=BnknNTN8icw) — Spring Boot微服务
""",
    "java/01-框架/SpringCloud01": """
## 🎬 推荐视频资源

- [Daily Code Buffer - Spring Cloud Tutorial](https://www.youtube.com/watch?v=BnknNTN8icw) — Spring Cloud微服务完整教程
- [Java Brains - Microservices with Spring Boot](https://www.youtube.com/playlist?list=PLqq-6Pq4lTTZSKAFG6aCDVDP86Qx4lNas) — 微服务系统教程
""",
    "java/02-中间件/RabbitMQ": """
## 🎬 推荐视频资源

- [Amigoscode - RabbitMQ Tutorial](https://www.youtube.com/watch?v=nFxjaVmFj5E) — RabbitMQ完整教程
- [freeCodeCamp - Message Queues](https://www.youtube.com/watch?v=5-Rq4-PZlew) — 消息队列概念讲解
""",
    "java/02-中间件/Elasticsearch基础": """
## 🎬 推荐视频资源

- [freeCodeCamp - Elasticsearch Tutorial](https://www.youtube.com/watch?v=C3tlMqaNSaI) — Elasticsearch完整教程
- [Fireship - Elasticsearch in 100 Seconds](https://www.youtube.com/watch?v=yg4i3c48ep4) — Elasticsearch快速了解
""",
    "java/02-中间件/Redis分布式缓存": """
## 🎬 推荐视频资源

- [freeCodeCamp - Redis Full Course](https://www.youtube.com/watch?v=XCsS_NVAa1g) — Redis完整课程
- [Fireship - Redis in 100 Seconds](https://www.youtube.com/watch?v=G1rOthIU-uo) — Redis快速了解
- [Tech With Tim - Redis Tutorial](https://www.youtube.com/watch?v=OqCK95AS-YE) — Redis实战教程
""",
    "java/03-容器化/Docker实用篇": """
## 🎬 推荐视频资源

- [freeCodeCamp - Docker Tutorial](https://www.youtube.com/watch?v=fqMOX6JJhGo) — Docker完整教程
- [TechWorld with Nana - Docker Tutorial](https://www.youtube.com/watch?v=3c-iBn73dDE) — Docker系统教程（最受欢迎）
- [Fireship - Docker in 100 Seconds](https://www.youtube.com/watch?v=Gjnup-PuquQ) — Docker快速了解
""",
    "java/03-容器化/Kubernetes第1天": """
## 🎬 推荐视频资源

- [TechWorld with Nana - Kubernetes Tutorial](https://www.youtube.com/watch?v=X48VuDVv0do) — K8s完整教程（最受欢迎，4小时）
- [freeCodeCamp - Kubernetes Course](https://www.youtube.com/watch?v=d6WC5n9G_sM) — K8s完整课程
- [Fireship - Kubernetes in 100 Seconds](https://www.youtube.com/watch?v=PziYflu8cB8) — K8s快速了解
""",
    "java/04-设计模式/设计模式": """
## 🎬 推荐视频资源

- [Christopher Okhravi - Design Patterns](https://www.youtube.com/playlist?list=PLrhzvIcii6GNjpARdnO4ueTUAVR9eMBpc) — 设计模式完整系列（最受欢迎）
- [Fireship - 10 Design Patterns Explained](https://www.youtube.com/watch?v=tv-_1er1mWI) — 10个设计模式10分钟讲解
- [Derek Banas - Design Patterns Tutorial](https://www.youtube.com/playlist?list=PLF206E906175C7E07) — 设计模式教程系列
""",
    "java/05-网络编程/Netty01-nio": """
## 🎬 推荐视频资源

- [Jakob Jenkov - Java NIO Tutorial](https://www.youtube.com/playlist?list=PLUbFnGajtZlXhAScGaV94nWMRMOjGGIXo) — Java NIO完整教程
- [Defog Tech - Netty Tutorial](https://www.youtube.com/watch?v=DKJ0w30M0vg) — Netty入门教程
""",
    "java/07-数据库/MySQL基础": """
## 🎬 推荐视频资源

- [freeCodeCamp - MySQL Full Course](https://www.youtube.com/watch?v=HXV3zeQKqGY) — MySQL完整课程
- [Programming with Mosh - MySQL Tutorial](https://www.youtube.com/watch?v=7S_tz1z_5bA) — MySQL入门教程（3小时）
""",
    # ==================== Frontend ====================
    "frontend/00-HTML与CSS基础/HTML5语义化与新特性": """
## 🎬 推荐视频资源

- [freeCodeCamp - HTML Full Course](https://www.youtube.com/watch?v=kUMe1FH4CHE) — HTML完整课程
- [Kevin Powell - HTML & CSS](https://www.youtube.com/@KevinPowell) — CSS大师Kevin Powell频道
""",
    "frontend/00-HTML与CSS基础/CSS3核心特性": """
## 🎬 推荐视频资源

- [Kevin Powell - CSS Tutorials](https://www.youtube.com/@KevinPowell) — 全网最好的CSS教程频道
- [freeCodeCamp - CSS Full Course](https://www.youtube.com/watch?v=OXGznpKZ_sA) — CSS完整课程
""",
    "frontend/00-HTML与CSS基础/Flex与Grid布局": """
## 🎬 推荐视频资源

- [Kevin Powell - Flexbox Tutorial](https://www.youtube.com/watch?v=u044iM9xsWU) — Flexbox完整教程
- [Kevin Powell - CSS Grid Tutorial](https://www.youtube.com/watch?v=rg7Fvvl3taU) — CSS Grid完整教程
- [Fireship - CSS Flexbox in 100 Seconds](https://www.youtube.com/watch?v=K74l26pE4YA) — Flexbox快速了解
""",
    "frontend/01-JavaScript基础/ES6+新特性": """
## 🎬 推荐视频资源

- [Traversy Media - JavaScript Crash Course](https://www.youtube.com/watch?v=hdI2bqOjy3c) — JavaScript速成
- [freeCodeCamp - JavaScript Full Course](https://www.youtube.com/watch?v=PkZNo7MFNFg) — JavaScript完整课程
- [Fireship - JavaScript in 100 Seconds](https://www.youtube.com/watch?v=DHjqpvDnNGE) — JavaScript快速了解
""",
    "frontend/01-JavaScript基础/异步编程与Promise": """
## 🎬 推荐视频资源

- [Fireship - Async Await in 100 Seconds](https://www.youtube.com/watch?v=vn3tm0quoqE) — 异步编程快速了解
- [Traversy Media - Async JS Crash Course](https://www.youtube.com/watch?v=PoRJizFvM7s) — 异步JS速成
- [The Net Ninja - Async JavaScript](https://www.youtube.com/playlist?list=PL4cUxeGkcC9jx2TTZk3IGWKSbtugYdrlu) — 异步JS系列教程
""",
    "frontend/02-TypeScript/TypeScript基础入门": """
## 🎬 推荐视频资源

- [freeCodeCamp - TypeScript Full Course](https://www.youtube.com/watch?v=30LWjhZzg50) — TypeScript完整课程
- [Fireship - TypeScript in 100 Seconds](https://www.youtube.com/watch?v=zQnBQ4tB3ZA) — TypeScript快速了解
- [Matt Pocock - Total TypeScript](https://www.youtube.com/@maaboroshi) — TypeScript高级技巧
""",
    "frontend/03-React/React基础与JSX": """
## 🎬 推荐视频资源

- [freeCodeCamp - React Full Course](https://www.youtube.com/watch?v=bMknfKXIFA8) — React完整课程（12小时）
- [Traversy Media - React Crash Course](https://www.youtube.com/watch?v=LDB4uaJ87e0) — React速成
- [Fireship - React in 100 Seconds](https://www.youtube.com/watch?v=Tn6-PIqc4UM) — React快速了解
""",
    "frontend/03-React/React Hooks深入": """
## 🎬 推荐视频资源

- [Web Dev Simplified - React Hooks](https://www.youtube.com/watch?v=O6P86uwfdR0) — React Hooks完整教程
- [Jack Herrington - React Hooks](https://www.youtube.com/@jherr) — React高级技巧频道
""",
    "frontend/03-React/React状态管理": """
## 🎬 推荐视频资源

- [Jack Herrington - State Management](https://www.youtube.com/watch?v=zpUMRsAO6-Y) — React状态管理对比
- [Fireship - Redux in 100 Seconds](https://www.youtube.com/watch?v=_shA5Xwe8_4) — Redux快速了解
""",
    "frontend/04-Vue/Vue3基础与组合式API": """
## 🎬 推荐视频资源

- [freeCodeCamp - Vue 3 Full Course](https://www.youtube.com/watch?v=VeNfHj6MhgA) — Vue 3完整课程（6小时）
- [Traversy Media - Vue.js Crash Course](https://www.youtube.com/watch?v=qZXt1Aom3Cs) — Vue速成
- [Fireship - Vue.js in 100 Seconds](https://www.youtube.com/watch?v=nhBVL41-_Cw) — Vue快速了解
""",
    "frontend/05-工程化与构建/Webpack核心概念": """
## 🎬 推荐视频资源

- [freeCodeCamp - Webpack Full Course](https://www.youtube.com/watch?v=MpGLUVbqoYQ) — Webpack完整课程
- [Fireship - Webpack in 100 Seconds](https://www.youtube.com/watch?v=5IG4UmULyoA) — Webpack快速了解
""",
    "frontend/05-工程化与构建/Vite现代构建工具": """
## 🎬 推荐视频资源

- [Fireship - Vite in 100 Seconds](https://www.youtube.com/watch?v=KCrXgy8qtjM) — Vite快速了解
- [Traversy Media - Vite Crash Course](https://www.youtube.com/watch?v=89NJdbYTgJ8) — Vite速成
""",
    "frontend/06-CSS进阶/Tailwind CSS实用优先": """
## 🎬 推荐视频资源

- [Traversy Media - Tailwind CSS Crash Course](https://www.youtube.com/watch?v=dFgzHOX84xQ) — Tailwind速成
- [Fireship - Tailwind in 100 Seconds](https://www.youtube.com/watch?v=mr15Xzb1Ook) — Tailwind快速了解
""",
    "frontend/07-Node.js/Node.js基础与模块系统": """
## 🎬 推荐视频资源

- [freeCodeCamp - Node.js Full Course](https://www.youtube.com/watch?v=Oe421EPjeBE) — Node.js完整课程
- [Traversy Media - Node.js Crash Course](https://www.youtube.com/watch?v=fBNz5xF-Kx4) — Node.js速成
- [Fireship - Node.js in 100 Seconds](https://www.youtube.com/watch?v=ENrzD9HAZK4) — Node.js快速了解
""",
    "frontend/07-Node.js/Express与Koa框架": """
## 🎬 推荐视频资源

- [Traversy Media - Express Crash Course](https://www.youtube.com/watch?v=SccSCuHhOw0) — Express速成
- [freeCodeCamp - Express.js Full Course](https://www.youtube.com/watch?v=G8uL0lFFoN0) — Express完整课程
""",
    "frontend/08-测试/Jest单元测试": """
## 🎬 推荐视频资源

- [Traversy Media - Jest Crash Course](https://www.youtube.com/watch?v=7r4xVDI2vho) — Jest速成
- [freeCodeCamp - JavaScript Testing](https://www.youtube.com/watch?v=FgnxcUQ5vho) — JavaScript测试完整课程
""",
    "frontend/09-浏览器与网络/HTTP协议与缓存策略": """
## 🎬 推荐视频资源

- [Fireship - HTTP in 100 Seconds](https://www.youtube.com/watch?v=iYM2zFP3Zn0) — HTTP快速了解
- [Traversy Media - HTTP Crash Course](https://www.youtube.com/watch?v=iYM2zFP3Zn0) — HTTP速成
""",
    "frontend/09-浏览器与网络/Web安全XSS-CSRF": """
## 🎬 推荐视频资源

- [Fireship - Web Security in 100 Seconds](https://www.youtube.com/watch?v=4YOpILi9Oxs) — Web安全快速了解
- [Computerphile - Cross Site Scripting](https://www.youtube.com/watch?v=L5l9lSnNMxg) — XSS详解
""",
    # ==================== iOS ====================
    "ios/00-Swift基础/Swift语法基础": """
## 🎬 推荐视频资源

- [CodeWithChris - Swift Tutorial for Beginners](https://www.youtube.com/watch?v=comQ1-x2a1Q) — Swift入门教程
- [Paul Hudson - 100 Days of SwiftUI](https://www.hackingwithswift.com/100/swiftui) — 100天SwiftUI挑战
- [Sean Allen - Swift Fundamentals](https://www.youtube.com/watch?v=CwA1VWP0Ldw) — Swift基础教程
""",
    "ios/00-Swift基础/Swift并发编程": """
## 🎬 推荐视频资源

- [Sean Allen - Swift Concurrency](https://www.youtube.com/watch?v=U6lQOo5aGmE) — Swift并发编程教程
- [Paul Hudson - Concurrency in Swift](https://www.youtube.com/watch?v=sGnxBiLL3Gc) — async/await详解
""",
    "ios/01-SwiftUI/SwiftUI基础与布局": """
## 🎬 推荐视频资源

- [Swiftful Thinking - SwiftUI Bootcamp](https://www.youtube.com/playlist?list=PLwvDm4VfkdphqETTBf-DdjCoAvhai1QpO) — SwiftUI完整入门系列
- [Paul Hudson - SwiftUI Tutorial](https://www.youtube.com/watch?v=aP-SQXTtWhY) — SwiftUI教程
- [Stanford CS193p - SwiftUI](https://www.youtube.com/playlist?list=PLpGHT1n4-mAtTj9oywMWoBx0dCGd51_yG) — 斯坦福SwiftUI课程（免费）
""",
    "ios/01-SwiftUI/SwiftUI状态管理": """
## 🎬 推荐视频资源

- [Swiftful Thinking - SwiftUI State Management](https://www.youtube.com/watch?v=KD4OAjQJYPc) — SwiftUI状态管理
- [Sean Allen - @State @Binding @ObservedObject](https://www.youtube.com/watch?v=stSB04C4iS4) — 属性包装器详解
""",
    "ios/05-架构模式/MVC-MVVM-MVP架构": """
## 🎬 推荐视频资源

- [Sean Allen - MVVM in SwiftUI](https://www.youtube.com/watch?v=wEf1YS4vyW8) — SwiftUI MVVM架构
- [Essential Developer - iOS Architecture](https://www.youtube.com/c/EssentialDeveloper) — iOS架构设计频道
""",
    # ==================== Android ====================
    "android/00-Kotlin基础/Kotlin语法基础": """
## 🎬 推荐视频资源

- [freeCodeCamp - Kotlin Full Course](https://www.youtube.com/watch?v=EExSSotojVI) — Kotlin完整课程
- [Philipp Lackner - Kotlin Tutorial](https://www.youtube.com/watch?v=5flXf8nuq60) — Kotlin入门教程
- [JetBrains - Kotlin by JetBrains](https://www.youtube.com/watch?v=F9UC9DY-vIU) — 官方Kotlin教程
""",
    "android/00-Kotlin基础/Kotlin协程与异步": """
## 🎬 推荐视频资源

- [Philipp Lackner - Kotlin Coroutines](https://www.youtube.com/watch?v=ShNhJ3wMpvQ) — Kotlin协程完整教程
- [JetBrains - Coroutines Guide](https://www.youtube.com/watch?v=_hfBv0a09Jc) — 官方协程指南
""",
    "android/01-Jetpack Compose/Compose基础与布局": """
## 🎬 推荐视频资源

- [Philipp Lackner - Jetpack Compose Full Course](https://www.youtube.com/watch?v=cDabx3SjuOY) — Compose完整课程
- [Android Developers - Compose Tutorial](https://www.youtube.com/watch?v=cDabx3SjuOY) — 官方Compose教程
- [Stevdza-San - Jetpack Compose](https://www.youtube.com/@StevdzaSan) — Compose教程频道
""",
    "android/01-Jetpack Compose/Compose状态管理": """
## 🎬 推荐视频资源

- [Philipp Lackner - State in Compose](https://www.youtube.com/watch?v=mymWGMy9pYI) — Compose状态管理
- [Android Developers - State and Jetpack Compose](https://www.youtube.com/watch?v=rmv2ug-wW4U) — 官方状态管理讲解
""",
    "android/03-Jetpack组件/ViewModel与LiveData": """
## 🎬 推荐视频资源

- [Philipp Lackner - ViewModel Tutorial](https://www.youtube.com/watch?v=9sqvBydNJSg) — ViewModel教程
- [CodingWithMitch - Android Architecture](https://www.youtube.com/watch?v=ijXjCtCXcN4) — Android架构组件
""",
    "android/03-Jetpack组件/Room数据库": """
## 🎬 推荐视频资源

- [Philipp Lackner - Room Database](https://www.youtube.com/watch?v=bOd3wO0uFr8) — Room数据库完整教程
- [CodingWithMitch - Room Persistence](https://www.youtube.com/watch?v=xPOIaKVFz5Y) — Room持久化教程
""",
    "android/05-架构模式/MVVM与MVI架构": """
## 🎬 推荐视频资源

- [Philipp Lackner - MVVM Tutorial](https://www.youtube.com/watch?v=ijXjCtCXcN4) — Android MVVM教程
- [Philipp Lackner - MVI Architecture](https://www.youtube.com/watch?v=hlBsrsVFgIk) — MVI架构讲解
""",
}


VIDEO_MARKER = "## 🎬 推荐视频资源"


def find_matching_file(base_dir: Path, key: str) -> Path | None:
    """根据关键词找到对应的md文件"""
    # key 格式: "ai-agent/00-基础概念/AI Agent概述与发展"
    parts = key.split("/")
    search_dir = base_dir
    for part in parts[:-1]:
        search_dir = search_dir / part
    
    filename = parts[-1]
    # 尝试精确匹配
    candidate = search_dir / f"{filename}.md"
    if candidate.exists():
        return candidate
    
    # 模糊匹配
    if search_dir.exists():
        for f in search_dir.iterdir():
            if f.suffix == ".md" and filename in f.stem:
                return f
    return None


def add_video_section(filepath: Path, video_block: str) -> bool:
    """在文件末尾添加视频推荐区块"""
    content = filepath.read_text(encoding="utf-8")
    
    # 已经有视频推荐了，跳过
    if VIDEO_MARKER in content:
        return False
    
    # 在文件末尾添加
    updated = content.rstrip() + "\n" + video_block.strip() + "\n"
    filepath.write_text(updated, encoding="utf-8")
    return True


def main():
    base_dir = Path(__file__).resolve().parent.parent / "learning-notes"
    
    added = 0
    skipped = 0
    not_found = 0
    
    for key, video_block in VIDEO_MAP.items():
        filepath = find_matching_file(base_dir, key)
        if filepath is None:
            print(f"  ❌ 未找到: {key}")
            not_found += 1
            continue
        
        if add_video_section(filepath, video_block):
            print(f"  ✅ {filepath.relative_to(base_dir)}")
            added += 1
        else:
            skipped += 1
    
    print(f"\n完成: {added} 个文件已添加视频链接, {skipped} 个已有跳过, {not_found} 个未找到")


if __name__ == "__main__":
    main()
