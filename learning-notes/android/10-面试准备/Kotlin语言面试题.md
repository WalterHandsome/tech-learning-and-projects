# Kotlin 语言面试题

> Author: Walter Wang

## 1. val vs var

```kotlin
// val：只读引用（类似 Java final），引用不可变但对象内容可变
val list = mutableListOf(1, 2, 3)
list.add(4)        // ✅ 对象内容可变
// list = listOf()  // ❌ 引用不可变

// var：可变引用
var name = "张三"
name = "李四"  // ✅

// const val：编译时常量（仅基本类型和 String）
companion object {
    const val MAX_COUNT = 100  // 编译时内联
    val PATTERN = Regex("\\d+")  // 运行时初始化
}
```

## 2. data class

```kotlin
// 自动生成: equals(), hashCode(), toString(), copy(), componentN()
data class User(val name: String, val age: Int)

val u1 = User("张三", 25)
val u2 = u1.copy(age = 26)           // 浅拷贝
val (name, age) = u1                  // 解构
println(u1 == u2)                     // false（结构相等）
println(u1 === u2)                    // false（引用不等）

// 注意：只有主构造函数中的属性参与 equals/hashCode
data class Item(val id: Int, val name: String) {
    var description: String = ""  // 不参与 equals/hashCode
}
```

## 3. sealed class vs enum

```kotlin
// sealed class：限制继承，子类可以有不同属性
sealed class Result<out T> {
    data class Success<T>(val data: T) : Result<T>()
    data class Error(val message: String, val code: Int) : Result<Nothing>()
    data object Loading : Result<Nothing>()
}

// enum：固定实例，所有实例结构相同
enum class Direction { NORTH, SOUTH, EAST, WEST }

// sealed interface（Kotlin 1.5+）
sealed interface UiEvent {
    data class ShowSnackbar(val msg: String) : UiEvent
    data object NavigateBack : UiEvent
}

// when 表达式编译器检查完整性
fun handle(result: Result<String>) = when (result) {
    is Result.Success -> result.data
    is Result.Error -> result.message
    is Result.Loading -> "加载中"
    // 不需要 else，编译器知道所有子类
}
```

## 4. 协程 vs 线程

```kotlin
// 线程：OS 级别，创建开销大（~1MB 栈），数量有限
// 协程：用户级别，轻量（~几KB），可创建数十万个

// 线程切换由 OS 调度，协程切换由程序控制
// 协程可以挂起而不阻塞线程

suspend fun fetchData(): String {
    return withContext(Dispatchers.IO) {
        // 挂起当前协程，释放线程给其他协程使用
        api.getData()
    }
}

// 结构化并发：父协程取消时子协程自动取消
viewModelScope.launch {
    val a = async { fetchA() }
    val b = async { fetchB() }
    // viewModelScope 取消时，a 和 b 自动取消
    process(a.await(), b.await())
}
```

## 5. Flow vs LiveData

```kotlin
// LiveData：
// - 生命周期感知，自动取消订阅
// - 只在主线程观察
// - 无操作符链
// - 适合简单 UI 状态

// Flow：
// - 协程原生，丰富操作符
// - 可在任意线程
// - 冷流（collect 时才执行）
// - 适合复杂数据流

// StateFlow 替代 LiveData
class ViewModel : ViewModel() {
    // LiveData 方式
    private val _data = MutableLiveData<String>()
    val data: LiveData<String> = _data

    // StateFlow 方式（推荐）
    private val _state = MutableStateFlow("")
    val state: StateFlow<String> = _state.asStateFlow()
}

// 收集 Flow 需要生命周期感知
viewLifecycleOwner.lifecycleScope.launch {
    repeatOnLifecycle(Lifecycle.State.STARTED) {
        viewModel.state.collect { updateUI(it) }
    }
}

// Compose 中直接使用
val state by viewModel.state.collectAsStateWithLifecycle()
```

## 6. 扩展函数 vs 继承

```kotlin
// 扩展函数：不修改原类，编译时静态解析
fun String.isValidEmail(): Boolean = Regex("^[\\w.-]+@[\\w.-]+\\.\\w+$").matches(this)
"test@example.com".isValidEmail()  // true

// 注意：扩展函数是静态分发，不支持多态
open class Base
class Derived : Base()

fun Base.greet() = "Base"
fun Derived.greet() = "Derived"

val obj: Base = Derived()
println(obj.greet())  // "Base"（静态类型决定）

// 继承：运行时多态
open class Base { open fun greet() = "Base" }
class Derived : Base() { override fun greet() = "Derived" }
val obj: Base = Derived()
println(obj.greet())  // "Derived"（动态分发）
```

## 7. 内联函数

```kotlin
// inline：函数体在调用处展开，避免 lambda 对象创建
inline fun <T> measureTime(block: () -> T): Pair<T, Long> {
    val start = System.nanoTime()
    val result = block()
    return result to (System.nanoTime() - start)
}

// reified：内联函数中获取泛型类型
inline fun <reified T> Gson.fromJson(json: String): T =
    fromJson(json, T::class.java)

// 使用
val user = gson.fromJson<User>(jsonStr)  // 无需传 Class
```
