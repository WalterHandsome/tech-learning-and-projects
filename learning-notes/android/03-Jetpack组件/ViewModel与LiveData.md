# ViewModel 与 LiveData
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. ViewModel 生命周期

```kotlin
// ViewModel 在配置变更（旋转屏幕）时存活
class UserViewModel(
    private val repository: UserRepository,
    private val savedStateHandle: SavedStateHandle
) : ViewModel() {

    private val _uiState = MutableStateFlow(UserUiState())
    val uiState: StateFlow<UserUiState> = _uiState.asStateFlow()

    init { loadUsers() }

    private fun loadUsers() {
        viewModelScope.launch {
            _uiState.update { it.copy(isLoading = true) }
            try {
                val users = repository.getUsers()
                _uiState.update { it.copy(users = users, isLoading = false) }
            } catch (e: Exception) {
                _uiState.update { it.copy(error = e.message, isLoading = false) }
            }
        }
    }

    override fun onCleared() {
        super.onCleared()
        // 清理资源
    }
}

data class UserUiState(
    val users: List<User> = emptyList(),
    val isLoading: Boolean = false,
    val error: String? = null
)
```

## 2. SavedStateHandle

```kotlin
class SearchViewModel(private val savedStateHandle: SavedStateHandle) : ViewModel() {
    // 进程被杀后恢复
    var query: String
        get() = savedStateHandle["query"] ?: ""
        set(value) { savedStateHandle["query"] = value }

    val queryFlow: StateFlow<String> = savedStateHandle.getStateFlow("query", "")

    // 配合 Navigation 获取参数
    private val userId: String = savedStateHandle["userId"] ?: ""
}
```

## 3. LiveData

```kotlin
class PostViewModel : ViewModel() {
    private val _posts = MutableLiveData<List<Post>>()
    val posts: LiveData<List<Post>> = _posts

    fun loadPosts() {
        viewModelScope.launch {
            _posts.value = repository.getPosts()  // 主线程
            _posts.postValue(data)                 // 任意线程
        }
    }
}

// 观察 LiveData
class PostFragment : Fragment() {
    private val viewModel: PostViewModel by viewModels()

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        viewModel.posts.observe(viewLifecycleOwner) { posts ->
            adapter.submitList(posts)
        }
    }
}
```

## 4. Transformations

```kotlin
class UserViewModel : ViewModel() {
    private val _userId = MutableLiveData<String>()

    // map：同步转换
    val userName: LiveData<String> = _userId.map { id ->
        "User: $id"
    }

    // switchMap：异步转换（返回新 LiveData）
    val userDetail: LiveData<User> = _userId.switchMap { id ->
        repository.getUserLiveData(id)
    }

    // MediatorLiveData：合并多个源
    val combined = MediatorLiveData<Pair<User?, List<Post>?>>().apply {
        addSource(userLiveData) { user -> value = Pair(user, postsLiveData.value) }
        addSource(postsLiveData) { posts -> value = Pair(userLiveData.value, posts) }
    }
}
```

## 5. StateFlow 替代 LiveData（推荐）

```kotlin
class ModernViewModel(private val repository: UserRepository) : ViewModel() {
    private val _uiState = MutableStateFlow(UiState())
    val uiState: StateFlow<UiState> = _uiState.asStateFlow()

    // 事件用 SharedFlow（一次性事件）
    private val _events = MutableSharedFlow<UiEvent>()
    val events: SharedFlow<UiEvent> = _events.asSharedFlow()

    fun onAction(action: UserAction) {
        when (action) {
            is UserAction.Delete -> deleteUser(action.userId)
            is UserAction.Refresh -> refresh()
        }
    }

    private fun deleteUser(id: String) {
        viewModelScope.launch {
            repository.deleteUser(id)
            _events.emit(UiEvent.ShowSnackbar("已删除"))
        }
    }
}

// Compose 中收集
@Composable
fun UserScreen(viewModel: ModernViewModel = hiltViewModel()) {
    val uiState by viewModel.uiState.collectAsStateWithLifecycle()

    LaunchedEffect(Unit) {
        viewModel.events.collect { event ->
            when (event) {
                is UiEvent.ShowSnackbar -> snackbarHostState.showSnackbar(event.message)
            }
        }
    }
}
```
