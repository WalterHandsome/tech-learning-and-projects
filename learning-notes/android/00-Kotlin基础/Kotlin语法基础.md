# Kotlin 语法基础

> Author: Walter Wang

## 1. 变量与类型

```kotlin
val constant = 10       // 不可变（推荐）
var variable = 20       // 可变

// 类型声明
val name: String = "张三"
val age: Int = 25
val height: Double = 1.75
val isActive: Boolean = true

// 类型推断
val message = "Hello"   // 自动推断为 String
val count = 42          // 自动推断为 Int

// 字符串模板
val greeting = "Hello, $name"
val info = "Name: ${user.name}, Age: ${user.age}"

// 多行字符串
val json = """
    {
        "name": "$name",
        "age": $age
    }
""".trimIndent()
```

## 2. 空安全

```kotlin
var nickname: String? = null  // 可空类型

// 安全调用
val length = nickname?.length  // Int?

// Elvis 运算符
val displayName = nickname ?: "匿名"

// 安全调用链
val city = user?.address?.city ?: "未知"

// let 作用域函数
nickname?.let { name ->
    println("昵称: $name")
}

// 非空断言（谨慎使用）
val forcedName = nickname!!  // 如果为 null 抛出 NPE

// 安全类型转换
val str = value as? String  // 失败返回 null
```

## 3. 集合

```kotlin
// 不可变集合
val fruits = listOf("苹果", "香蕉", "橙子")
val scores = mapOf("张三" to 90, "李四" to 85)
val tags = setOf("Kotlin", "Android")

// 可变集合
val mutableFruits = mutableListOf("苹果", "香蕉")
mutableFruits.add("橙子")
mutableFruits.removeAt(0)

val mutableScores = mutableMapOf("张三" to 90)
mutableScores["李四"] = 85

// 集合操作
val numbers = listOf(1, 2, 3, 4, 5)
val doubled = numbers.map { it * 2 }              // [2, 4, 6, 8, 10]
val evens = numbers.filter { it % 2 == 0 }        // [2, 4]
val sum = numbers.reduce { acc, n -> acc + n }     // 15
val total = numbers.fold(0) { acc, n -> acc + n }  // 15
val names = users.mapNotNull { it.name }           // 过滤 null
val allTags = users.flatMap { it.tags }            // 展平
val grouped = users.groupBy { it.department }      // 分组
val first = numbers.firstOrNull { it > 3 }        // 4
val any = numbers.any { it > 4 }                   // true
val all = numbers.all { it > 0 }                   // true
```

## 4. 控制流

```kotlin
// if 表达式（有返回值）
val max = if (a > b) a else b

// when 表达式（替代 switch）
val result = when (score) {
    in 90..100 -> "优秀"
    in 60..89 -> "及格"
    else -> "不及格"
}

// when 无参数
when {
    user.isAdmin -> handleAdmin()
    user.isActive -> handleActive()
    else -> handleDefault()
}

// for 循环
for (i in 0 until 5) { }          // 0,1,2,3,4
for (i in 5 downTo 1) { }         // 5,4,3,2,1
for (i in 0..10 step 2) { }       // 0,2,4,6,8,10
for ((index, value) in list.withIndex()) { }
for ((key, value) in map) { }

// 区间
val range = 1..10          // 闭区间
val until = 1 until 10     // 半开区间
```

## 5. 函数

```kotlin
// 基本函数
fun greet(name: String, greeting: String = "Hello"): String {
    return "$greeting, $name"
}

// 单表达式函数
fun add(a: Int, b: Int) = a + b

// 命名参数
greet(name = "张三", greeting = "Hi")

// 可变参数
fun sum(vararg numbers: Int): Int = numbers.sum()

// 扩展函数
fun String.isEmail(): Boolean = contains("@") && contains(".")
"test@example.com".isEmail()  // true

// 中缀函数
infix fun Int.times(str: String) = str.repeat(this)
val result = 3 times "abc"  // "abcabcabc"

// 高阶函数
fun <T> List<T>.customFilter(predicate: (T) -> Boolean): List<T> {
    val result = mutableListOf<T>()
    for (item in this) {
        if (predicate(item)) result.add(item)
    }
    return result
}
```

## 6. 数据类与密封类

```kotlin
// 数据类（自动生成 equals/hashCode/toString/copy/componentN）
data class User(
    val id: Int,
    val name: String,
    val email: String,
)

val user = User(1, "张三", "test@example.com")
val copy = user.copy(name = "李四")
val (id, name, email) = user  // 解构

// 密封类（限制继承）
sealed class Result<out T> {
    data class Success<T>(val data: T) : Result<T>()
    data class Error(val message: String, val cause: Throwable? = null) : Result<Nothing>()
    data object Loading : Result<Nothing>()
}

// 配合 when 使用（编译器检查完整性）
fun handleResult(result: Result<User>) = when (result) {
    is Result.Success -> showUser(result.data)
    is Result.Error -> showError(result.message)
    is Result.Loading -> showLoading()
}

// 枚举类
enum class Status(val code: Int) {
    ACTIVE(1), INACTIVE(0), DELETED(-1);
}
```

## 7. 作用域函数

```kotlin
// let：非空执行，转换
val length = name?.let { it.length } ?: 0

// run：对象配置 + 计算结果
val result = user.run {
    "$name ($email)"
}

// with：对同一对象多次操作
with(user) {
    println(name)
    println(email)
}

// apply：对象配置（返回对象本身）
val user = User().apply {
    name = "张三"
    email = "test@example.com"
}

// also：附加操作（返回对象本身）
val user = createUser().also {
    logger.info("Created user: ${it.name}")
}
```
