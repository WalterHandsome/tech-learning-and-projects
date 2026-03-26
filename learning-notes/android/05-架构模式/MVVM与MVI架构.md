# MVVM 与 MVI 架构

## 1. MVVM（ViewModel + StateFlow + Repository）

```kotlin
// --- UiState ---
data class UserListUiState(
    val users: List<User> = emptyList(),
    val isLoading: Boolean = false,
    val error: String? = null
)

// --- ViewModel ---
@HiltViewModel
class UserListViewModel @Inject constructor(
    private val repository: UserRepository
) : ViewModel() {

    private val _uiState = MutableStateFlow(UserListUiState())
    val uiState: StateFlow<UserListUiState> = _uiState.asStateFlow()

    init { loadUsers() }

    fun loadUsers() {
        viewModelScope.launch {
            _uiState.update { it.copy(isLoading = true, error = null) }
            try {
                val users = repository.getUsers()
                _uiState.update { it.copy(users = users, isLoading = false) }
            } catch (e: Exception) {
                _uiState.update { it.copy(error = e.message, isLoading = false) }
            }
        }
    }

    fun deleteUser(userId: String) {
        viewModelScope.launch {
            repository.deleteUser(userId)
            loadUsers()
        }
    }
}

// --- Repository ---
class UserRepository @Inject constructor(
    private val api: ApiService,
    private val dao: UserDao
) {
    suspend fun getUsers(): List<User> {
        val remote = api.getUsers()
        dao.insertAll(remote.map { it.toEntity() })
        return remote
    }
}

// --- UI (Compose) ---
@Composable
fun UserListScreen(viewModel: UserListViewModel = hiltViewModel()) {
    val uiState by viewModel.uiState.collectAsStateWithLifecycle()

    when {
        uiState.isLoading -> CircularProgressIndicator()
        uiState.error != null -> ErrorView(uiState.error!!) { viewModel.loadUsers() }
        else -> UserList(uiState.users, onDelete = viewModel::deleteUser)
    }
}
```

## 2. MVI（单向数据流）

```kotlin
// --- Intent（用户意图）---
sealed class UserIntent {
    data object LoadUsers : UserIntent()
    data class DeleteUser(val id: String) : UserIntent()
    data class SearchUsers(val query: String) : UserIntent()
}

// --- State ---
data class UserState(
    val users: List<User> = emptyList(),
    val isLoading: Boolean = false,
    val error: String? = null,
    val query: String = ""
)

// --- Side Effect（一次性事件）---
sealed class UserEffect {
    data class ShowToast(val message: String) : UserEffect()
    data object NavigateBack : UserEffect()
}

// --- ViewModel ---
@HiltViewModel
class UserMviViewModel @Inject constructor(
    private val repository: UserRepository
) : ViewModel() {

    private val _state = MutableStateFlow(UserState())
    val state: StateFlow<UserState> = _state.asStateFlow()

    private val _effect = MutableSharedFlow<UserEffect>()
    val effect: SharedFlow<UserEffect> = _effect.asSharedFlow()

    fun onIntent(intent: UserIntent) {
        when (intent) {
            is UserIntent.LoadUsers -> loadUsers()
            is UserIntent.DeleteUser -> deleteUser(intent.id)
            is UserIntent.SearchUsers -> search(intent.query)
        }
    }

    private fun loadUsers() {
        viewModelScope.launch {
            _state.update { it.copy(isLoading = true) }
            try {
                val users = repository.getUsers()
                _state.update { it.copy(users = users, isLoading = false) }
            } catch (e: Exception) {
                _state.update { it.copy(error = e.message, isLoading = false) }
                _effect.emit(UserEffect.ShowToast("加载失败"))
            }
        }
    }

    private fun deleteUser(id: String) {
        viewModelScope.launch {
            repository.deleteUser(id)
            _effect.emit(UserEffect.ShowToast("已删除"))
            loadUsers()
        }
    }

    private fun search(query: String) {
        _state.update { it.copy(query = query) }
    }
}

// --- UI ---
@Composable
fun UserMviScreen(viewModel: UserMviViewModel = hiltViewModel()) {
    val state by viewModel.state.collectAsStateWithLifecycle()

    LaunchedEffect(Unit) {
        viewModel.effect.collect { effect ->
            when (effect) {
                is UserEffect.ShowToast -> { /* show snackbar */ }
                is UserEffect.NavigateBack -> { /* navigate */ }
            }
        }
    }

    LaunchedEffect(Unit) { viewModel.onIntent(UserIntent.LoadUsers) }

    Column {
        SearchBar(state.query) { viewModel.onIntent(UserIntent.SearchUsers(it)) }
        UserList(state.users) { viewModel.onIntent(UserIntent.DeleteUser(it)) }
    }
}
```
