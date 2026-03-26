# AI Agent 技术学习笔记

> 本目录包含 AI Agent 与大模型应用开发的学习笔记，按类别组织

## 📁 目录结构

```
ai-agent/
├── 00-基础概念/                  # AI Agent 核心概念
│   ├── AI Agent概述与发展.md
│   ├── 大语言模型基础.md
│   └── Prompt Engineering.md
│
├── 01-Agent协议/                 # Agent 通信协议
│   ├── MCP模型上下文协议.md
│   ├── A2A Agent间通信协议.md
│   └── ACP与协议生态.md
│
├── 02-Agent框架/                 # 主流开发框架
│   ├── LangGraph工作流编排.md
│   ├── CrewAI多Agent协作.md
│   ├── OpenAI Agents SDK.md
│   ├── Google ADK与Bedrock Agents.md
│   └── AG2-PydanticAI-Agno.md
│
├── 03-RAG进阶/                   # 检索增强生成
│   ├── RAG架构与核心流程.md
│   ├── 向量数据库选型.md
│   ├── 高级RAG策略.md
│   └── GraphRAG知识图谱.md
│
├── 04-工具与Function Calling/     # 工具调用
│   ├── Function Calling机制.md
│   ├── MCP Server开发.md
│   └── 工具编排与安全.md
│
├── 05-多Agent系统/                # 多Agent协作
│   ├── 多Agent架构模式.md
│   ├── Agent通信与协调.md
│   └── 人机协作与监督.md
│
├── 06-记忆与状态/                 # Agent记忆系统
│   ├── 短期与长期记忆.md
│   ├── 对话管理与上下文.md
│   └── 知识库与经验学习.md
│
├── 07-模型服务/                   # LLM 接入与部署
│   ├── OpenAI与Claude API.md
│   ├── 开源模型部署.md
│   └── 模型路由与网关.md
│
├── 08-可观测与评估/               # 监控与评估
│   ├── LLM可观测性.md
│   ├── Agent评估与基准.md
│   └── 安全与对齐.md
│
├── 09-低代码平台/                 # 可视化构建
│   ├── Dify平台实践.md
│   ├── Coze与FastGPT.md
│   └── n8n与Flowise.md
│
├── 10-实战案例/                   # 项目实践
│   ├── 智能客服Agent.md
│   ├── 代码助手Agent.md
│   └── 数据分析Agent.md
│
└── README.md                     # 本文件
```

## 📚 内容说明

### 基础概念

- **AI Agent概述与发展**：Agent定义与分类、从Chatbot到Agentic AI的演进、ReAct/Plan-and-Execute/Tool Use范式、2025-2026行业趋势
- **大语言模型基础**：Transformer架构、GPT/Claude/Gemini/Llama模型对比、Token与上下文窗口、Temperature/Top-P采样、多模态能力
- **Prompt Engineering**：系统提示词设计、Few-shot/Chain-of-Thought/Tree-of-Thought、结构化输出、提示词注入防御

### Agent 协议

- **MCP模型上下文协议**：MCP架构（Host/Client/Server）、工具发现与调用、资源与提示模板、传输层（stdio/SSE/Streamable HTTP）、安全模型、MCP Server开发实践
- **A2A Agent间通信协议**：Google A2A协议、Agent Card发现机制、任务生命周期管理、流式通信、企业级认证授权、与MCP的互补关系
- **ACP与协议生态**：IBM ACP轻量消息协议、ANP Agent网络协议、协议选型指南（MCP vs A2A vs ACP）

### Agent 框架

- **LangGraph工作流编排**：图结构（StateGraph/Node/Edge）、条件路由、检查点与状态持久化、人机交互节点、子图、LangGraph Cloud部署
- **CrewAI多Agent协作**：Agent/Task/Crew/Tool核心概念、角色定义与任务分配、顺序/层级/共识流程、MCP集成、Memory系统、企业级部署
- **OpenAI Agents SDK**：Agent/Handoff/Guardrail核心概念、工具定义、Agent间交接、输入输出护栏、Tracing追踪、快速原型开发
- **Google ADK与Bedrock Agents**：Google Agent Development Kit、Amazon Bedrock Agents、云厂商Agent方案对比
- **AG2-PydanticAI-Agno**：AG2（原AutoGen）多Agent对话、PydanticAI类型安全Agent、Agno高性能运行时、smolagents轻量方案

### RAG 进阶

- **RAG架构与核心流程**：Naive RAG → Advanced RAG → Modular RAG演进、文档加载与分块策略、Embedding模型选型、检索与重排序、生成与引用
- **向量数据库选型**：Pinecone、Weaviate、Qdrant、Milvus、Chroma、pgvector对比、混合搜索（向量+关键词+语义）
- **高级RAG策略**：查询改写与扩展、HyDE假设文档嵌入、Self-RAG自反思检索、Contextual Retrieval、Reranking重排序、Agentic RAG
- **GraphRAG知识图谱**：知识图谱构建、实体关系抽取、图检索策略、Microsoft GraphRAG、Neo4j集成、图+向量混合检索

### 工具与 Function Calling

- **Function Calling机制**：OpenAI/Claude/Gemini Function Calling对比、工具定义Schema、并行工具调用、流式工具调用
- **MCP Server开发**：Python/TypeScript SDK、工具/资源/提示注册、传输层实现、认证与授权、测试与调试
- **工具编排与安全**：工具链编排、权限控制、输入验证、速率限制、审计日志、沙箱执行

### 多 Agent 系统

- **多Agent架构模式**：Supervisor监督者模式、Hierarchical层级模式、Swarm群体模式、Network网络模式、选型指南
- **Agent通信与协调**：消息传递、共享状态、任务委派与交接（Handoff）、冲突解决、A2A协议实践
- **人机协作与监督**：Human-in-the-Loop、审批工作流、中断与恢复、信任层级、渐进式自主

### 记忆与状态

- **短期与长期记忆**：对话缓冲记忆、摘要记忆、向量记忆、实体记忆、记忆检索策略
- **对话管理与上下文**：多轮对话管理、上下文窗口优化、对话历史压缩、会话隔离
- **知识库与经验学习**：知识库构建与更新、经验回放、反思机制、自我改进

### 模型服务

- **OpenAI与Claude API**：Chat Completions API、Anthropic Messages API、流式响应、多模态输入、Batch API、成本优化
- **开源模型部署**：vLLM/Ollama/llama.cpp推理引擎、Llama/Qwen/DeepSeek模型、量化部署（GGUF/AWQ/GPTQ）、GPU资源规划
- **模型路由与网关**：LiteLLM统一接口、模型负载均衡、Fallback策略、Token用量追踪、API Key管理

### 可观测与评估

- **LLM可观测性**：LangSmith/LangFuse/Phoenix追踪平台、Trace/Span/Run链路追踪、Token用量监控、延迟分析、成本追踪
- **Agent评估与基准**：任务完成率、工具调用准确率、RAGAS评估框架、人工评估、A/B测试、回归测试
- **安全与对齐**：提示词注入防御、输出过滤、PII检测、内容安全策略、Red Teaming、Guardrails护栏

### 低代码平台

- **Dify平台实践**：工作流编排、知识库管理、Agent模式、API发布、私有化部署
- **Coze与FastGPT**：Coze Bot构建、插件市场、FastGPT知识库问答、工作流编排
- **n8n与Flowise**：n8n AI Agent节点、Flowise可视化LangChain、自动化工作流集成

### 实战案例

- **智能客服Agent**：多轮对话、知识库检索、工单创建、人工转接、满意度评估
- **代码助手Agent**：代码生成与审查、仓库理解、Bug修复、测试生成、MCP工具集成
- **数据分析Agent**：自然语言转SQL、数据可视化、报表生成、异常检测、多数据源接入

## 🎯 学习路径建议

### 入门阶段
1. **基础概念**：AI Agent概述 → 大语言模型基础 → Prompt Engineering
2. **快速体验**：低代码平台（Dify/Coze）→ 感受Agent能力

### 开发阶段
3. **协议理解**：MCP协议 → A2A协议 → 协议生态
4. **框架学习**：LangGraph → CrewAI → OpenAI Agents SDK（选一深入）
5. **RAG实践**：RAG核心流程 → 向量数据库 → 高级RAG策略
6. **工具开发**：Function Calling → MCP Server开发

### 进阶阶段
7. **多Agent系统**：架构模式 → 通信协调 → 人机协作
8. **记忆系统**：短期/长期记忆 → 对话管理 → 知识库
9. **模型服务**：API接入 → 开源模型部署 → 模型路由
10. **可观测性**：链路追踪 → 评估基准 → 安全对齐

### 实战阶段
11. **项目实践**：智能客服 → 代码助手 → 数据分析Agent

## 📖 使用说明

- 所有笔记从个人学习过程中整理，已移除敏感信息
- 包含代码示例和最佳实践
- 技术发展迅速，内容持续更新

## 🔗 相关资源

- [LangGraph 文档](https://langchain-ai.github.io/langgraph/)
- [CrewAI 文档](https://docs.crewai.com/)
- [OpenAI Agents SDK](https://openai.github.io/openai-agents-python/)
- [MCP 规范](https://modelcontextprotocol.io/)
- [A2A 协议](https://google.github.io/A2A/)
- [Dify 文档](https://docs.dify.ai/)
