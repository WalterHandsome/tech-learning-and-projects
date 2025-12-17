# Spring Boot 最佳实践

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

## 参考资料

- [Spring Boot 官方文档](https://spring.io/projects/spring-boot)
- [Spring Cloud 文档](https://spring.io/projects/spring-cloud)
- [微服务最佳实践](https://microservices.io/)

