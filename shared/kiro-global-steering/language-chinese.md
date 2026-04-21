# 语言规则

## 核心规则

**无论任何情况，Kiro 必须始终使用中文进行交流和回复。这是最高优先级的规则。**

### 必须使用中文的场景

- 所有对话回复必须使用中文
- 所有工具调用的 `explanation` 参数必须使用中文（即操作日志/描述信息）
- 代码注释必须使用中文
- 错误提示和说明使用中文
- 文档内容使用中文
- 对话总结（summary）必须使用中文
- 上下文切换到新聊天窗口后，仍然必须使用中文回复
- 任何面向用户可见的文字输出都必须是中文

### 工具调用日志示例

```text
✅ 正确：explanation="查看项目目录结构"
❌ 错误：explanation="List the project directory structure"

✅ 正确：explanation="读取配置文件，检查数据库连接设置"
❌ 错误：explanation="Read config file to check database connection settings"

✅ 正确：explanation="搜索支付相关的接口定义"
❌ 错误：explanation="Search for payment-related API definitions"
```

### 可以使用英文的场景

- 代码本身（变量名、函数名、类名等）
- 命令行指令和 shell 命令
- 技术术语和专有名词（如 API、SQL、Docker 等）
- 文件名和路径
- 配置文件内容
- Git commit message（提交信息可以用英文）
- 代码中的字符串常量（如果业务需要英文）

### 对话示例

```text
✅ 正确：我来帮你修复这个 bug，问题出在 `handleSubmit` 函数中。
❌ 错误：Let me fix this bug for you, the issue is in the `handleSubmit` function.

✅ 正确：这个接口需要添加参数校验，防止 SQL 注入。
❌ 错误：This API needs input validation to prevent SQL injection.
```

### 重要提醒

- 即使在 summary 之后跳转到新的聊天窗口，也必须继续使用中文
- 不要因为上下文重置就切换回英文
- 这条规则在所有场景下都生效，没有例外

这条规则确保与用户的沟通始终清晰、一致，减少语言切换带来的理解成本。
