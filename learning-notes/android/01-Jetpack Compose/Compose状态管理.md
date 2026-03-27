# Compose 状态管理
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. remember 与 mutableStateOf

```kotlin
@Composable
fun Counter() {
    // 重组时保留状态
    var count by remember { mutableStateOf(0) }

    Button(onClick = { count++ }) {
        Text("点击次数: $count")
    }
}

// remember 缓存计算结果
@Composable
fun FilteredList(items: List<String>, query: String) {
    val filtered = remember(items, query) {
        items.filter { it.contains(query, ignoreCase = true) }
    }
    LazyColumn {
        items(filtered) { Text(it) }
    }
}
```

## 2. rememberSaveable

```kotlin
// 配置变更（旋转屏幕）后保留状态
@Composable
fun InputForm() {
    var text by rememberSaveable { mutableStateOf("") }

    OutlinedTextField(
        value = text,
        onValueChange = { text = it },
        label = { Text("用户名") }
    )
}

// 自定义 Saver
data class City(val name: String, val country: String)

val CitySaver = run {
    val nameKey = "name"
    val countryKey = "country"
    mapSaver(
        save = { mapOf(nameKey to it.name, countryKey to it.country) },
        restore = { City(it[nameKey] as String, it[countryKey] as String) }
    )
}

@Composable
fun CityScreen() {
    var city by rememberSaveable(stateSaver = CitySaver) {
        mutableStateOf(City("北京", "中国"))
    }
}
```

## 3. State Hoisting（状态提升）

```kotlin
// 无状态组件
@Composable
fun SearchBar(
    query: String,
    onQueryChange: (String) -> Unit,
    modifier: Modifier = Modifier
) {
    OutlinedTextField(
        value = query,
        onValueChange = onQueryChange,
        modifier = modifier.fillMaxWidth(),
        placeholder = { Text("搜索...") },
        leadingIcon = { Icon(Icons.Default.Search, null) }
    )
}

// 有状态的父组件
@Composable
fun SearchScreen(viewModel: SearchViewModel = hiltViewModel()) {
    val uiState by viewModel.uiState.collectAsStateWithLifecycle()

    Column {
        SearchBar(
            query = uiState.query,
            onQueryChange = viewModel::onQueryChange
        )
        SearchResults(results = uiState.results)
    }
}
```

## 4. derivedStateOf

```kotlin
@Composable
fun TodoList(todos: List<Todo>) {
    // 仅在计算结果变化时触发重组
    val completedCount by remember(todos) {
        derivedStateOf { todos.count { it.isCompleted } }
    }

    val listState = rememberLazyListState()
    val showButton by remember {
        derivedStateOf { listState.firstVisibleItemIndex > 0 }
    }

    Scaffold(
        floatingActionButton = {
            if (showButton) {
                FloatingActionButton(onClick = { /* 回到顶部 */ }) {
                    Icon(Icons.Default.KeyboardArrowUp, null)
                }
            }
        }
    ) { padding ->
        Column(Modifier.padding(padding)) {
            Text("已完成: $completedCount / ${todos.size}")
            LazyColumn(state = listState) {
                items(todos) { TodoItem(it) }
            }
        }
    }
}
```

## 5. Side Effects

```kotlin
// LaunchedEffect：在组合中启动协程
@Composable
fun UserProfile(userId: String, viewModel: UserViewModel = hiltViewModel()) {
    LaunchedEffect(userId) {
        viewModel.loadUser(userId)  // userId 变化时重新加载
    }
}

// DisposableEffect：需要清理的副作用
@Composable
fun LocationTracker(onLocationUpdate: (Location) -> Unit) {
    val context = LocalContext.current
    DisposableEffect(Unit) {
        val locationManager = context.getSystemService<LocationManager>()
        val listener = LocationListener { onLocationUpdate(it) }
        locationManager?.requestLocationUpdates(GPS_PROVIDER, 1000, 10f, listener)
        onDispose {
            locationManager?.removeUpdates(listener)
        }
    }
}

// SideEffect：每次重组后执行
@Composable
fun AnalyticsScreen(screenName: String) {
    val analytics = LocalAnalytics.current
    SideEffect {
        analytics.logScreenView(screenName)
    }
}

// snapshotFlow：将 Compose State 转为 Flow
@Composable
fun ScrollTracker(listState: LazyListState) {
    LaunchedEffect(listState) {
        snapshotFlow { listState.firstVisibleItemIndex }
            .distinctUntilChanged()
            .collect { index -> analytics.logScroll(index) }
    }
}
```
## 🎬 推荐视频资源

- [Philipp Lackner - State in Compose](https://www.youtube.com/watch?v=mymWGMy9pYI) — Compose状态管理
- [Android Developers - State and Jetpack Compose](https://www.youtube.com/watch?v=rmv2ug-wW4U) — 官方状态管理讲解
