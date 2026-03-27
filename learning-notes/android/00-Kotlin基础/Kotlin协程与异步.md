# Kotlin 协程与异步
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. 协程基础

```kotlin
import kotlinx.coroutines.*

// launch（不返回结果）
fun main() = runBlocking {
    launch {
        delay(1000)
        println("World")
    }
    println("Hello")
}

// async（返回结果）
suspend fun fetchUserAndPosts(): Pair<User, List<Post>> = coroutineScope {
    val user = async { fetchUser() }
    val posts = async { fetchPosts() }
    Pair(user.await(), posts.await())  // 并发执行
}

// coroutineScope（结构化并发）
suspend fun loadData() = coroutineScope {
    val users = async { api.getUsers() }
    val posts = async { api.getPosts() }
    ProcessedData(users.await(), posts.await())
}
```

## 2. CoroutineScope 与 Dispatcher

```kotlin
// Dispatchers
Dispatchers.Main       // 主线程（UI 更新）
Dispatchers.IO         // IO 操作（网络、磁盘）
Dispatchers.Default    // CPU 密集型计算

// 切换线程
suspend fun fetchUser(): User = withContext(Dispatchers.IO) {
    api.getUser()  // 在 IO 线程执行
}

// ViewModel 中的协程
class UserViewModel : ViewModel() {
    fun loadUsers() {
        viewModelScope.launch {
            try {
                val users = withContext(Dispatchers.IO) { repository.getUsers() }
                _uiState.value = UiState.Success(users)
            } catch (e: Exception) {
                _uiState.value = UiState.Error(e.message)
            }
        }
    }
}

// 生命周期感知的协程
class MyFragment : Fragment() {
    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        viewLifecycleOwner.lifecycleScope.launch {
            repeatOnLifecycle(Lifecycle.State.STARTED) {
                viewModel.uiState.collect { state -> updateUI(state) }
            }
        }
    }
}
```

## 3. Flow

```kotlin
// 冷流（每次 collect 都重新执行）
fun getUsers(): Flow<List<User>> = flow {
    val users = api.getUsers()
    emit(users)
}

// 操作符
repository.getUsers()
    .map { users -> users.filter { it.isActive } }
    .catch { e -> emit(emptyList()) }
    .onStart { showLoading() }
    .onCompletion { hideLoading() }
    .flowOn(Dispatchers.IO)
    .collect { users -> updateUI(users) }

// StateFlow（热流，有初始值，类似 LiveData）
class UserViewModel : ViewModel() {
    private val _uiState = MutableStateFlow<UiState>(UiState.Loading)
    val uiState: StateFlow<UiState> = _uiState.asStateFlow()

    fun loadUsers() {
        viewModelScope.launch {
            _uiState.value = UiState.Loading
            try {
                val users = repository.getUsers()
                _uiState.value = UiState.Success(users)
            } catch (e: Exception) {
                _uiState.value = UiState.Error(e.message ?: "Unknown error")
            }
        }
    }
}

// SharedFlow（热流，无初始值，事件广播）
class EventBus {
    private val _events = MutableSharedFlow<Event>()
    val events: SharedFlow<Event> = _events.asSharedFlow()

    suspend fun emit(event: Event) { _events.emit(event) }
}

// stateIn / shareIn（Flow → StateFlow/SharedFlow）
val users: StateFlow<List<User>> = repository.getUsers()
    .stateIn(viewModelScope, SharingStarted.WhileSubscribed(5000), emptyList())
```

## 4. 异常处理

```kotlin
// try-catch
viewModelScope.launch {
    try {
        val data = fetchData()
    } catch (e: CancellationException) {
        throw e  // 不要捕获取消异常
    } catch (e: Exception) {
        handleError(e)
    }
}

// CoroutineExceptionHandler
val handler = CoroutineExceptionHandler { _, exception ->
    Log.e("Coroutine", "Error: ${exception.message}")
}
viewModelScope.launch(handler) {
    fetchData()
}

// supervisorScope（子协程失败不影响其他）
supervisorScope {
    val job1 = launch { task1() }
    val job2 = launch { task2() }  // task1 失败不影响 task2
}
```
