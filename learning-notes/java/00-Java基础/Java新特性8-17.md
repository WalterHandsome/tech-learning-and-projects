# Java新特性8-17

## Java 8 新特性

### 1. Lambda表达式

Lambda表达式是Java 8最重要的特性之一，它允许我们将函数作为方法的参数，或者将代码本身当作数据处理。

**语法格式：**
```java
(parameters) -> expression
或
(parameters) -> { statements; }
```

**示例：**
```java
// 旧写法
Collections.sort(list, new Comparator<String>() {
    @Override
    public int compare(String s1, String s2) {
        return s1.compareTo(s2);
    }
});

// Lambda表达式写法
Collections.sort(list, (s1, s2) -> s1.compareTo(s2));
```

### 2. 函数式接口

函数式接口是只包含一个抽象方法的接口。Java 8提供了`@FunctionalInterface`注解来标识函数式接口。

**常用的函数式接口：**
- `Function<T, R>`: 接受一个参数，返回一个结果
- `Consumer<T>`: 接受一个参数，无返回值
- `Supplier<T>`: 无参数，返回一个结果
- `Predicate<T>`: 接受一个参数，返回boolean值

**示例：**
```java
@FunctionalInterface
public interface MyFunction {
    int apply(int x, int y);
}

MyFunction add = (x, y) -> x + y;
MyFunction multiply = (x, y) -> x * y;
```

### 3. Stream API

Stream API是Java 8中处理集合的关键抽象概念，它可以让你以一种声明的方式处理数据集合。

**Stream的特点：**
- 不是数据结构，不会存储数据
- 不会改变源数据，会返回一个新的Stream
- 延迟执行，只有在终端操作时才会执行
- 可以并行处理

**常用操作：**
```java
List<String> list = Arrays.asList("a", "b", "c", "d");

// 过滤
list.stream().filter(s -> s.startsWith("a")).forEach(System.out::println);

// 映射
list.stream().map(String::toUpperCase).forEach(System.out::println);

// 排序
list.stream().sorted().forEach(System.out::println);

// 收集
List<String> result = list.stream()
    .filter(s -> s.length() > 1)
    .collect(Collectors.toList());
```

### 4. 接口默认方法和静态方法

Java 8允许在接口中定义默认方法和静态方法。

**默认方法：**
```java
public interface MyInterface {
    default void defaultMethod() {
        System.out.println("Default method");
    }
}
```

**静态方法：**
```java
public interface MyInterface {
    static void staticMethod() {
        System.out.println("Static method");
    }
}
```

### 5. 新的日期和时间API

Java 8引入了新的日期和时间API（java.time包），解决了旧API的线程安全问题。

**主要类：**
- `LocalDate`: 日期（年月日）
- `LocalTime`: 时间（时分秒）
- `LocalDateTime`: 日期时间
- `ZonedDateTime`: 带时区的日期时间
- `Duration`: 时间间隔
- `Period`: 日期间隔

**示例：**
```java
// 获取当前日期
LocalDate today = LocalDate.now();

// 创建指定日期
LocalDate date = LocalDate.of(2024, 1, 1);

// 日期格式化
DateTimeFormatter formatter = DateTimeFormatter.ofPattern("yyyy-MM-dd");
String formatted = date.format(formatter);

// 日期解析
LocalDate parsed = LocalDate.parse("2024-01-01", formatter);
```

### 6. Optional类

Optional类是一个容器类，可以保存类型T的值，或者仅仅保存null。Optional提供很多有用的方法，这样我们就不用显式进行空值检测。

**示例：**
```java
Optional<String> optional = Optional.of("value");
optional.ifPresent(System.out::println);
String value = optional.orElse("default");
```

### 7. 方法引用

方法引用是Lambda表达式的简化写法。

**四种方法引用类型：**
1. 静态方法引用：`ClassName::staticMethod`
2. 实例方法引用：`instance::instanceMethod`
3. 类的实例方法引用：`ClassName::instanceMethod`
4. 构造器引用：`ClassName::new`

**示例：**
```java
List<String> list = Arrays.asList("a", "b", "c");
list.forEach(System.out::println); // 方法引用
list.forEach(s -> System.out.println(s)); // Lambda表达式
```

### 8. 并发增强

Java 8在并发方面做了很多改进：
- `CompletableFuture`: 异步编程
- `StampedLock`: 新的锁机制
- `LongAdder`: 高并发计数器

## Java 9 新特性

### 1. 模块系统（Project Jigsaw）

Java 9引入了模块系统，允许开发者将代码组织成模块。

**module-info.java示例：**
```java
module com.example {
    requires java.base;
    exports com.example.api;
}
```

### 2. 接口私有方法

Java 9允许在接口中定义私有方法。

```java
public interface MyInterface {
    default void method1() {
        privateMethod();
    }
    
    private void privateMethod() {
        System.out.println("Private method");
    }
}
```

### 3. 改进的Stream API

新增了`takeWhile`、`dropWhile`等方法。

```java
List<Integer> list = Arrays.asList(1, 2, 3, 4, 5);
list.stream()
    .takeWhile(n -> n < 4)
    .forEach(System.out::println); // 输出: 1, 2, 3
```

### 4. 集合工厂方法

新增了`List.of()`、`Set.of()`、`Map.of()`等工厂方法。

```java
List<String> list = List.of("a", "b", "c");
Set<String> set = Set.of("a", "b", "c");
Map<String, Integer> map = Map.of("a", 1, "b", 2);
```

## Java 10 新特性

### 1. 局部变量类型推断

使用`var`关键字进行局部变量类型推断。

```java
var list = new ArrayList<String>();
var map = new HashMap<String, Integer>();
```

## Java 11 新特性

### 1. HTTP Client API

Java 11引入了新的HTTP Client API，支持HTTP/2和WebSocket。

```java
HttpClient client = HttpClient.newHttpClient();
HttpRequest request = HttpRequest.newBuilder()
    .uri(URI.create("https://example.com"))
    .build();
HttpResponse<String> response = client.send(request, 
    HttpResponse.BodyHandlers.ofString());
```

### 2. String新增方法

- `isBlank()`: 判断字符串是否为空白
- `strip()`: 去除首尾空白字符
- `repeat(int)`: 重复字符串

```java
String str = "  ";
System.out.println(str.isBlank()); // true
System.out.println("  hello  ".strip()); // "hello"
System.out.println("a".repeat(3)); // "aaa"
```

## Java 12-17 新特性

### Java 12

- Switch表达式（预览）
- 文本块（预览）

### Java 13

- 文本块（第二次预览）
- Switch表达式（第二次预览）

### Java 14

- Switch表达式（正式）
- 文本块（第三次预览）
- 记录类（Record，预览）
- Pattern Matching for instanceof（预览）

### Java 15

- 文本块（正式）
- 密封类（Sealed Classes，预览）
- Pattern Matching for instanceof（第二次预览）

### Java 16

- 记录类（Record，正式）
- Pattern Matching for instanceof（正式）
- 密封类（Sealed Classes，第二次预览）

### Java 17

- 密封类（Sealed Classes，正式）
- Pattern Matching for switch（预览）

**记录类（Record）示例：**
```java
public record Person(String name, int age) {
    // 自动生成构造函数、getter、equals、hashCode、toString
}

Person person = new Person("John", 30);
System.out.println(person.name()); // "John"
```

**密封类（Sealed Classes）示例：**
```java
public sealed class Shape permits Circle, Rectangle {
    // ...
}

public final class Circle extends Shape {
    // ...
}
```

**Pattern Matching示例：**
```java
// instanceof模式匹配
if (obj instanceof String s) {
    System.out.println(s.length());
}

// switch表达式
String result = switch (day) {
    case MONDAY, FRIDAY, SUNDAY -> "Weekend";
    case TUESDAY -> "Weekday";
    default -> throw new IllegalArgumentException();
};
```

## 总结

Java 8-17的演进主要围绕以下几个方面：
1. **函数式编程**：Lambda表达式、Stream API、函数式接口
2. **类型推断**：var关键字、模式匹配
3. **模块化**：模块系统
4. **语法简化**：记录类、文本块、switch表达式
5. **性能优化**：新的并发API、GC改进
6. **API增强**：新的日期时间API、HTTP Client等

这些新特性让Java语言更加现代化，提高了开发效率和代码可读性。