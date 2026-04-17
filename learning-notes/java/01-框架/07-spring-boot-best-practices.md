# Spring Boot 最佳实践
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

> 本文档总结了 Spring Boot 开发中的最佳实践和常见模式

## 1. 项目结构

### 推荐的项目结构
```
project/
├── common-lib/          # 公共库
├── user-service/        # 业务服务
├── order-service/
└── api-gateway/
```

### 包结构
```
com.example.service/
├── controller/         # 控制器层
├── service/           # 业务逻辑层
├── repository/        # 数据访问层
├── entity/            # 实体类
└── dto/               # 数据传输对象
```

## 2. 统一异常处理

使用 `@RestControllerAdvice` 统一处理异常：

```java
@RestControllerAdvice
public class GlobalExceptionHandler {
    @ExceptionHandler(BusinessException.class)
    public ResponseEntity<ErrorResponse> handleBusinessException(BusinessException e) {
        // 统一异常响应格式
    }
}
```

## 3. 统一响应格式

定义标准的 API 响应格式：

```java
@Data
@Builder
public class ApiResponse<T> {
    private Integer code;
    private String message;
    private T data;
    private LocalDateTime timestamp;
}
```

## 4. 全链路追踪

使用 TraceId 实现全链路追踪：

```java
@Component
public class TraceIdFilter extends OncePerRequestFilter {
    @Override
    protected void doFilterInternal(...) {
        String traceId = UUID.randomUUID().toString();
        MDC.put("traceId", traceId);
        // ...
    }
}
```

## 5. 配置管理

### 使用环境变量
```yaml
spring:
  datasource:
    url: ${DATASOURCE_URL:jdbc:postgresql://localhost:5432/db}
    username: ${DATASOURCE_USERNAME:postgres}
    password: ${DATASOURCE_PASSWORD:postgres}
```

### 配置文件分离
- `application.yml` - 基础配置
- `application-local.yml` - 本地开发（不提交）
- `application-prod.yml` - 生产环境（不提交）

## 6. 测试

### 单元测试
```java
@ExtendWith(MockitoExtension.class)
class UserServiceTest {
    @Mock
    private UserRepository userRepository;
    
    @Test
    void testCreateUser() {
        // 测试逻辑
    }
}
```

### 集成测试
```java
@SpringBootTest
@AutoConfigureMockMvc
class UserControllerTest {
    @Autowired
    private MockMvc mockMvc;
    
    @Test
    void testCreateUser() throws Exception {
        // 测试逻辑
    }
}
```

## 7. 日志规范

### 日志级别
- ERROR: 系统错误，需要立即处理
- WARN: 警告信息，可能的问题
- INFO: 重要业务流程
- DEBUG: 调试信息（开发环境）

### 日志格式
```yaml
logging:
  pattern:
    console: "%d{yyyy-MM-dd HH:mm:ss} [%thread] %-5level [%X{traceId}] %logger{36} - %msg%n"
```

## 8. 事件驱动架构

使用 Kafka 实现事件驱动：

```java
@Service
public class UserService {
    private final KafkaTemplate<String, Object> kafkaTemplate;
    
    public void createUser(User user) {
        // 创建用户
        userRepository.save(user);
        // 发送事件
        kafkaTemplate.send("user-created", user.getId().toString(), user);
    }
}
```

## 9. 监控和健康检查

### Actuator 配置
```yaml
management:
  endpoints:
    web:
      exposure:
        include: health,info,prometheus
```

### 自定义健康检查
```java
@Component
public class CustomHealthIndicator implements HealthIndicator {
    @Override
    public Health health() {
        // 检查逻辑
        return Health.up().build();
    }
}
```

## 10. 容器化部署

### Dockerfile
```dockerfile
FROM maven:3.9-eclipse-temurin-17 AS build
WORKDIR /app
COPY . .
RUN mvn clean package -DskipTests

FROM eclipse-temurin:17-jre-alpine
COPY --from=build /app/target/*.jar app.jar
ENTRYPOINT ["java", "-jar", "app.jar"]
```

## 11. Spring Boot 版本演进

> 🔄 更新于 2026-04-18

<!-- version-check: Spring Boot 4.0.0, checked 2026-04-18 -->

### Spring Boot 3.x 重大变化（2022-11 至 2025-05）

Spring Boot 3.0 是自 2.x 以来最大的版本升级：

| 变化 | 说明 |
|------|------|
| **Java 17 基线** | 最低要求 Java 17，推荐 Java 21 |
| **Jakarta EE 10** | `javax.*` → `jakarta.*` 命名空间迁移 |
| **GraalVM 原生镜像** | 一等公民支持，启动时间 < 100ms |
| **可观测性** | Micrometer Observation API + OpenTelemetry 集成 |
| **Virtual Threads** | 3.2+ 支持 `spring.threads.virtual.enabled=true` |
| **HTTP Interface Client** | 声明式 HTTP 客户端（类似 Feign） |
| **RestClient** | 3.2+ 新增，替代 RestTemplate 的现代 API |

```yaml
# Spring Boot 3.2+ 启用虚拟线程
spring:
  threads:
    virtual:
      enabled: true
```

```java
// RestClient（Spring Boot 3.2+，替代 RestTemplate）
@Configuration
public class RestClientConfig {
    @Bean
    RestClient restClient(RestClient.Builder builder) {
        return builder
            .baseUrl("https://api.example.com")
            .defaultHeader("Accept", "application/json")
            .build();
    }
}

// 使用 RestClient
@Service
public class UserService {
    private final RestClient restClient;

    public User getUser(Long id) {
        return restClient.get()
            .uri("/users/{id}", id)
            .retrieve()
            .body(User.class);
    }
}
```

### Spring Boot 4.0（2025-11-20）

> Spring Boot 4.0 基于 Spring Framework 7，是继 3.0 之后的又一次重大升级。
> 来源：[Spring Boot 4.0 Release Notes](https://github.com/spring-projects/spring-boot/wiki/Spring-Boot-4.0-Release-Notes)

**核心变化：**

| 变化 | 说明 |
|------|------|
| **Spring Framework 7** | 底层框架大版本升级 |
| **Jakarta EE 11** | 从 Jakarta EE 10 升级 |
| **Jackson 3** | 默认序列化库升级到 Jackson 3 |
| **JSpecify Null-Safety** | 全面采用 JSpecify 空安全注解 |
| **原生 API 版本控制** | 内置 `spring.mvc.apiversion.*` 配置 |
| **HTTP Service Clients** | 自动配置声明式 HTTP 客户端 |
| **OpenTelemetry Starter** | 新增 `spring-boot-starter-opentelemetry` |
| **Gradle 9 支持** | 支持 Gradle 9，保留 Gradle 8.14+ 兼容 |

```java
// Spring Boot 4.0：HTTP Service Client（自动配置）
@HttpExchange(url = "https://api.example.com")
public interface UserService {

    @GetExchange("/users/{id}")
    User getUser(@PathVariable Long id);

    @PostExchange("/users")
    User createUser(@RequestBody User user);
}

// 直接注入使用，无需手动配置
@RestController
public class UserController {
    private final UserService userService;

    @GetMapping("/users/{id}")
    public User getUser(@PathVariable Long id) {
        return userService.getUser(id);
    }
}
```

```java
// Spring Boot 4.0：API 版本控制（原生支持）
@RestController
@RequestMapping("/api/users")
public class UserController {

    @GetMapping(produces = "application/vnd.api.v1+json")
    public List<UserV1> getUsersV1() { /* ... */ }

    @GetMapping(produces = "application/vnd.api.v2+json")
    public List<UserV2> getUsersV2() { /* ... */ }
}
```

### 版本选择建议

```
┌─────────────────────────────────────────────────────┐
│            Spring Boot 版本选择指南                   │
├─────────────────────────────────────────────────────┤
│                                                     │
│  新项目（2026 年）                                   │
│  ├── 保守选择 → Spring Boot 3.5.x + Java 21        │
│  └── 前沿选择 → Spring Boot 4.0.x + Java 21        │
│                                                     │
│  现有项目迁移路径                                    │
│  ├── 2.x → 先升级到 3.5.x → 再升级到 4.0           │
│  └── 3.x → 升级到 3.5.x → 再升级到 4.0             │
│                                                     │
│  ⚠️ Spring Boot 3.5 是 3.x 最后一个 minor 版本     │
│                                                     │
└─────────────────────────────────────────────────────┘
```

### Dockerfile 更新

```dockerfile
# Spring Boot 4.0 推荐 Dockerfile（Java 21）
FROM maven:3.9-eclipse-temurin-21 AS build
WORKDIR /app
COPY pom.xml .
RUN mvn dependency:go-offline
COPY src ./src
RUN mvn clean package -DskipTests

FROM eclipse-temurin:21-jre-alpine
COPY --from=build /app/target/*.jar app.jar
# 启用虚拟线程和 ZGC
ENTRYPOINT ["java", "-XX:+UseZGC", "-jar", "app.jar"]
```

## 参考资料

- [Spring Boot 官方文档](https://spring.io/projects/spring-boot)
- [Spring Boot 4.0 Release Notes](https://github.com/spring-projects/spring-boot/wiki/Spring-Boot-4.0-Release-Notes)
- [Spring Boot 3.5 Release Notes](https://github.com/spring-projects/spring-boot/wiki/Spring-Boot-3.5-Release-Notes)
- [Spring Cloud 文档](https://spring.io/projects/spring-cloud)
- [微服务最佳实践](https://microservices.io/)

