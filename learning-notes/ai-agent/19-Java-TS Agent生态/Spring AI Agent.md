# Spring AI Agent

> Author: Walter Wang

## 1. 概述

Spring AI 是 Spring 生态的 AI 框架，为 Java/Kotlin 开发者提供统一的 AI 模型接口、工具调用、RAG、MCP 客户端等能力。

```
┌─────────────────────────────────────────────┐
│            Spring Boot 应用                   │
├─────────────────────────────────────────────┤
│              Spring AI                       │
│  ┌──────────┐ ┌──────────┐ ┌────────────┐  │
│  │ChatClient│ │Tool Call │ │RAG         │  │
│  │统一对话   │ │工具调用   │ │检索增强     │  │
│  └──────────┘ └──────────┘ └────────────┘  │
│  ┌──────────┐ ┌──────────┐ ┌────────────┐  │
│  │Advisor   │ │MCP Client│ │VectorStore │  │
│  │中间件     │ │MCP 客户端│ │向量存储     │  │
│  └──────────┘ └──────────┘ └────────────┘  │
├──────┬──────┬──────┬──────┬────────────────┤
│OpenAI│Claude│Gemini│Ollama│ Bedrock 等     │
└──────┴──────┴──────┴──────┴────────────────┘
```

## 2. 快速开始

```xml
<!-- pom.xml -->
<dependency>
    <groupId>org.springframework.ai</groupId>
    <artifactId>spring-ai-openai-spring-boot-starter</artifactId>
</dependency>
```

```yaml
# application.yml
spring:
  ai:
    openai:
      api-key: ${OPENAI_API_KEY}
      chat:
        options:
          model: gpt-4o
          temperature: 0.7
```

```java
@RestController
public class ChatController {

    private final ChatClient chatClient;

    public ChatController(ChatClient.Builder builder) {
        this.chatClient = builder
            .defaultSystem("你是一个友好的 AI 助手")
            .build();
    }

    @GetMapping("/chat")
    public String chat(@RequestParam String message) {
        return chatClient.prompt()
            .user(message)
            .call()
            .content();
    }

    // 流式响应
    @GetMapping(value = "/stream", produces = MediaType.TEXT_EVENT_STREAM_VALUE)
    public Flux<String> stream(@RequestParam String message) {
        return chatClient.prompt()
            .user(message)
            .stream()
            .content();
    }
}
```

## 3. 工具调用（Function Calling）

```java
// 定义工具
@Component
public class WeatherTools {

    @Tool(description = "获取指定城市的天气信息")
    public WeatherInfo getWeather(@ToolParam(description = "城市名称") String city) {
        // 调用天气 API
        return new WeatherInfo(city, 28, "晴");
    }

    @Tool(description = "获取城市的空气质量指数")
    public AqiInfo getAqi(@ToolParam(description = "城市名称") String city) {
        return new AqiInfo(city, 45, "优");
    }

    record WeatherInfo(String city, int temperature, String condition) {}
    record AqiInfo(String city, int aqi, String level) {}
}

// 在 ChatClient 中使用工具
@RestController
public class AgentController {

    private final ChatClient chatClient;

    public AgentController(ChatClient.Builder builder, WeatherTools weatherTools) {
        this.chatClient = builder
            .defaultSystem("你是天气助手，使用工具查询天气信息")
            .defaultTools(weatherTools)  // 注册工具
            .build();
    }

    @GetMapping("/agent")
    public String agent(@RequestParam String query) {
        return chatClient.prompt()
            .user(query)
            .call()
            .content();
        // 模型自动决定是否调用工具
    }
}
```

## 4. Advisor 模式（中间件）

```java
// Advisor = AI 调用的中间件，类似 Spring MVC 的 Interceptor
@Component
public class LoggingAdvisor implements CallAroundAdvisor {

    @Override
    public AdvisedResponse aroundCall(AdvisedRequest request, CallAroundAdvisorChain chain) {
        // 请求前
        long start = System.currentTimeMillis();
        log.info("AI 请求: {}", request.userText());

        // 执行调用
        AdvisedResponse response = chain.nextAroundCall(request);

        // 请求后
        long duration = System.currentTimeMillis() - start;
        log.info("AI 响应: {} ({}ms)", response.response().getResult().getOutput().getText(), duration);

        return response;
    }

    @Override
    public int getOrder() { return 0; }
}

// 使用 Advisor
ChatClient chatClient = builder
    .defaultAdvisors(
        new LoggingAdvisor(),
        new MessageChatMemoryAdvisor(chatMemory),  // 内置记忆 Advisor
        new SafeGuardAdvisor("不要讨论政治话题")     // 护栏 Advisor
    )
    .build();
```

## 5. RAG 实现

```java
@Configuration
public class RagConfig {

    @Bean
    public VectorStore vectorStore(EmbeddingModel embeddingModel) {
        return new PgVectorStore(jdbcTemplate, embeddingModel);
    }
}

@Service
public class RagService {

    private final ChatClient chatClient;
    private final VectorStore vectorStore;

    public RagService(ChatClient.Builder builder, VectorStore vectorStore) {
        this.vectorStore = vectorStore;
        this.chatClient = builder
            .defaultAdvisors(
                new QuestionAnswerAdvisor(vectorStore, SearchRequest.builder()
                    .similarityThreshold(0.7)
                    .topK(5)
                    .build())
            )
            .build();
    }

    // 文档导入
    public void ingestDocuments(List<Document> documents) {
        vectorStore.add(documents);
    }

    // RAG 查询
    public String query(String question) {
        return chatClient.prompt()
            .user(question)
            .call()
            .content();
    }
}
```

## 6. MCP 客户端

```yaml
# application.yml
spring:
  ai:
    mcp:
      client:
        stdio:
          servers:
            filesystem:
              command: npx
              args: ["-y", "@modelcontextprotocol/server-filesystem", "/workspace"]
            github:
              command: npx
              args: ["-y", "@modelcontextprotocol/server-github"]
              env:
                GITHUB_TOKEN: ${GITHUB_TOKEN}
```

```java
@RestController
public class McpAgentController {

    private final ChatClient chatClient;

    public McpAgentController(ChatClient.Builder builder, ToolCallbackProvider mcpTools) {
        this.chatClient = builder
            .defaultSystem("你是开发助手，可以操作文件系统和 GitHub")
            .defaultTools(mcpTools)  // MCP 工具自动注册
            .build();
    }

    @GetMapping("/mcp-agent")
    public String mcpAgent(@RequestParam String task) {
        return chatClient.prompt()
            .user(task)
            .call()
            .content();
    }
}
```

## 7. 结构化输出

```java
// 定义输出结构
record CodeReview(
    int score,
    List<Issue> issues,
    String summary
) {
    record Issue(String severity, int line, String description) {}
}

@GetMapping("/review")
public CodeReview reviewCode(@RequestParam String code) {
    return chatClient.prompt()
        .user("审查以下代码：\n" + code)
        .call()
        .entity(CodeReview.class);  // 自动解析为 Java 对象
}
```

## 8. 实现 Anthropic Agent 模式

```java
// Evaluator-Optimizer 模式
@Service
public class EvalOptimizeAgent {

    private final ChatClient chatClient;

    public String generate(String task, int maxIterations) {
        String output = chatClient.prompt()
            .user("完成任务：" + task)
            .call().content();

        for (int i = 0; i < maxIterations; i++) {
            // 评估
            EvalResult eval = chatClient.prompt()
                .user("评估输出质量(1-10)并给建议：\n" + output)
                .call()
                .entity(EvalResult.class);

            if (eval.score() >= 8) break;

            // 优化
            output = chatClient.prompt()
                .user("改进输出：\n原文：" + output + "\n建议：" + eval.feedback())
                .call().content();
        }
        return output;
    }

    record EvalResult(int score, String feedback) {}
}
```

## 9. 多模型切换

```yaml
# application.yml — 配置多个模型
spring:
  ai:
    openai:
      api-key: ${OPENAI_API_KEY}
    anthropic:
      api-key: ${ANTHROPIC_API_KEY}
    ollama:
      base-url: http://localhost:11434
```

```java
@Service
public class MultiModelService {

    @Qualifier("openAiChatModel")
    private final ChatModel openai;

    @Qualifier("anthropicChatModel")
    private final ChatModel claude;

    public String routeByComplexity(String query, String complexity) {
        ChatModel model = switch (complexity) {
            case "high" -> openai;    // 复杂任务用 GPT-4o
            case "low" -> claude;     // 简单任务用 Claude Haiku
            default -> openai;
        };

        return ChatClient.create(model).prompt()
            .user(query)
            .call()
            .content();
    }
}
```
