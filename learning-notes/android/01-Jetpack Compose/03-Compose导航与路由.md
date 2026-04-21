# Compose 导航与路由
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. Navigation Compose 基础

```kotlin
// 依赖: androidx.navigation:navigation-compose:2.9+

// 定义路由
object Routes {
    const val HOME = "home"
    const val DETAIL = "detail/{itemId}"
    const val PROFILE = "profile?name={name}"

    fun detail(itemId: String) = "detail/$itemId"
    fun profile(name: String) = "profile?name=$name"
}

// NavHost 设置
@Composable
fun AppNavigation() {
    val navController = rememberNavController()

    NavHost(navController = navController, startDestination = Routes.HOME) {
        composable(Routes.HOME) {
            HomeScreen(
                onItemClick = { id -> navController.navigate(Routes.detail(id)) }
            )
        }
        composable(
            route = Routes.DETAIL,
            arguments = listOf(navArgument("itemId") { type = NavType.StringType })
        ) { backStackEntry ->
            val itemId = backStackEntry.arguments?.getString("itemId") ?: ""
            DetailScreen(itemId = itemId, onBack = { navController.popBackStack() })
        }
    }
}
```

## 2. 参数传递

```kotlin
// 必选参数
composable(
    route = "user/{userId}",
    arguments = listOf(navArgument("userId") { type = NavType.IntType })
) { entry ->
    val userId = entry.arguments?.getInt("userId") ?: 0
    UserScreen(userId)
}

// 可选参数（Query 参数）
composable(
    route = "search?query={query}&sort={sort}",
    arguments = listOf(
        navArgument("query") { defaultValue = "" },
        navArgument("sort") { defaultValue = "date" }
    )
) { entry ->
    val query = entry.arguments?.getString("query") ?: ""
    SearchScreen(query)
}

// 导航时传参
navController.navigate("user/123")
navController.navigate("search?query=kotlin&sort=name")
```

## 3. Deep Links

```kotlin
composable(
    route = "detail/{id}",
    deepLinks = listOf(
        navDeepLink { uriPattern = "https://myapp.com/detail/{id}" },
        navDeepLink { action = "com.example.DETAIL_ACTION" }
    )
) { entry ->
    DetailScreen(entry.arguments?.getString("id") ?: "")
}

// AndroidManifest.xml 中配置
// <intent-filter>
//     <action android:name="android.intent.action.VIEW" />
//     <category android:name="android.intent.category.DEFAULT" />
//     <category android:name="android.intent.category.BROWSABLE" />
//     <data android:scheme="https" android:host="myapp.com" />
// </intent-filter>
```

## 4. 导航选项

```kotlin
// 避免重复入栈
navController.navigate(Routes.HOME) {
    popUpTo(Routes.HOME) { inclusive = true }
    launchSingleTop = true
}

// 返回到指定页面
navController.navigate("result") {
    popUpTo("home") { inclusive = false }
}

// 返回并传递结果
navController.previousBackStackEntry
    ?.savedStateHandle?.set("result_key", "选中的数据")
navController.popBackStack()

// 接收结果
val result = navController.currentBackStackEntry
    ?.savedStateHandle?.get<String>("result_key")
```

## 5. Bottom Navigation

```kotlin
data class BottomNavItem(val route: String, val icon: ImageVector, val label: String)

val bottomNavItems = listOf(
    BottomNavItem("home", Icons.Default.Home, "首页"),
    BottomNavItem("search", Icons.Default.Search, "搜索"),
    BottomNavItem("profile", Icons.Default.Person, "我的")
)

@Composable
fun MainScreen() {
    val navController = rememberNavController()
    val currentRoute = navController.currentBackStackEntryAsState().value?.destination?.route

    Scaffold(
        bottomBar = {
            NavigationBar {
                bottomNavItems.forEach { item ->
                    NavigationBarItem(
                        selected = currentRoute == item.route,
                        onClick = {
                            navController.navigate(item.route) {
                                popUpTo(navController.graph.startDestinationId) { saveState = true }
                                launchSingleTop = true
                                restoreState = true
                            }
                        },
                        icon = { Icon(item.icon, item.label) },
                        label = { Text(item.label) }
                    )
                }
            }
        }
    ) { padding ->
        NavHost(navController, "home", Modifier.padding(padding)) {
            composable("home") { HomeScreen() }
            composable("search") { SearchScreen() }
            composable("profile") { ProfileScreen() }
        }
    }
}
```


## 6. Navigation 2026 更新与 Navigation 3

<!-- version-check: Navigation Compose 2.9.7, Navigation 3 alpha, checked 2026-04-21 -->

> 🔄 更新于 2026-04-21

### Navigation Compose 2.8+ 类型安全路由

```kotlin
// Navigation 2.8+ 引入类型安全路由（替代字符串路由）
// 使用 @Serializable 数据类定义路由
@Serializable
data object Home

@Serializable
data class Detail(val itemId: String)

@Serializable
data class Profile(val name: String = "")

// NavHost 使用类型安全路由
@Composable
fun AppNavigation() {
    val navController = rememberNavController()

    NavHost(navController = navController, startDestination = Home) {
        composable<Home> {
            HomeScreen(
                onItemClick = { id -> navController.navigate(Detail(id)) }
            )
        }
        composable<Detail> { backStackEntry ->
            val detail: Detail = backStackEntry.toRoute()
            DetailScreen(itemId = detail.itemId)
        }
    }
}
```

### Navigation 3（预览版）

Navigation 3 是全新的 Compose-first 导航库，提供完全的 back stack 控制：

```kotlin
// Navigation 3 核心概念：开发者拥有 back stack
// 依赖: androidx.navigation3:navigation3-compose (alpha)
val backStack = rememberMutableStateListOf<Any>(Home)

NavDisplay(
    backStack = backStack,
    onBack = { backStack.removeLastOrNull() },
    entryProvider = entryProvider {
        entry<Home> { HomeScreen(onNavigate = { backStack.add(it) }) }
        entry<Detail> { detail -> DetailScreen(detail.itemId) }
    }
)
```

> 来源：[Navigation Compose](https://developer.android.com/jetpack/androidx/releases/navigation)、[Navigation 3](https://developer.android.com/jetpack/androidx/releases/navigation3)
