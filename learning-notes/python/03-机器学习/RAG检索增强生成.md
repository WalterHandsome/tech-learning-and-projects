# RAG 检索增强生成实现指南

> 从 private-notes 提取的技术学习笔记

## RAG 概述

RAG（Retrieval-Augmented Generation）是一种结合检索和生成的 AI 技术，通过检索相关文档来增强 LLM 的生成能力。

## 核心流程

### 1. 文档预处理

- 文档分块（Chunking）
- 文本清洗
- 元数据提取

### 2. 向量化

- 使用 Embedding 模型将文本转换为向量
- 常用模型：text-embedding-ada-002

### 3. 向量存储

- 使用向量数据库存储
- 常用方案：PostgreSQL + pgvector、Pinecone、Weaviate

### 4. 检索

- 查询向量化
- 相似度搜索（Top-K）
- 相关性排序

### 5. 生成

- 将检索结果作为上下文
- 调用 LLM 生成回答

## 实现示例

```python
from llama_index import VectorStoreIndex, SimpleDirectoryReader
from llama_index.embeddings import OpenAIEmbedding

# 1. 加载文档
documents = SimpleDirectoryReader("data").load_data()

# 2. 创建索引
index = VectorStoreIndex.from_documents(documents)

# 3. 查询
query_engine = index.as_query_engine()
response = query_engine.query("你的问题")
```

## 优化策略

1. **分块策略**：选择合适的 chunk size
2. **检索策略**：Top-K、重排序
3. **提示工程**：优化 prompt 设计
4. **混合检索**：结合关键词和语义检索

## 参考资料

- [LlamaIndex 文档](https://docs.llamaindex.ai/)
- [RAG 论文](https://arxiv.org/abs/2005.11401)

