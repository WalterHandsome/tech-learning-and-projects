# Navigation 组件
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. NavGraph（XML 方式）

```xml
<!-- res/navigation/nav_graph.xml -->
<navigation xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:app="http://schemas.android.com/apk/res-auto"
    app:startDestination="@id/homeFragment">

    <fragment
        android:id="@+id/homeFragment"
        android:name="com.example.HomeFragment"
        android:label="首页">
        <action
            android:id="@+id/action_home_to_detail"
            app:destination="@id/detailFragment"
            app:enterAnim="@anim/slide_in_right"
            app:exitAnim="@anim/slide_out_left" />
    </fragment>

    <fragment
        android:id="@+id/detailFragment"
        android:name="com.example.DetailFragment"
        android:label="详情">
        <argument
            android:name="itemId"
            app:argType="string" />
    </fragment>
</navigation>
```

## 2. Safe Args

```kotlin
// build.gradle.kts: id("androidx.navigation.safeargs.kotlin")

// 发送参数
class HomeFragment : Fragment() {
    private val navController by lazy { findNavController() }

    fun navigateToDetail(itemId: String) {
        val action = HomeFragmentDirections.actionHomeToDetail(itemId = itemId)
        navController.navigate(action)
    }
}

// 接收参数
class DetailFragment : Fragment() {
    private val args: DetailFragmentArgs by navArgs()

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        val itemId = args.itemId
        viewModel.loadItem(itemId)
    }
}
```

## 3. Deep Link

```xml
<!-- nav_graph.xml -->
<fragment android:id="@+id/detailFragment">
    <deepLink
        app:uri="https://example.com/detail/{itemId}"
        app:action="android.intent.action.VIEW" />
</fragment>

<!-- AndroidManifest.xml -->
<activity android:name=".MainActivity">
    <nav-graph android:value="@navigation/nav_graph" />
</activity>
```

```kotlin
// 代码创建 Deep Link
val pendingIntent = NavDeepLinkBuilder(context)
    .setGraph(R.navigation.nav_graph)
    .setDestination(R.id.detailFragment)
    .setArguments(bundleOf("itemId" to "123"))
    .createPendingIntent()
```

## 4. NavigationUI

```kotlin
class MainActivity : AppCompatActivity() {
    private lateinit var navController: NavController

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        val binding = ActivityMainBinding.inflate(layoutInflater)
        setContentView(binding.root)

        val navHostFragment = supportFragmentManager
            .findFragmentById(R.id.nav_host) as NavHostFragment
        navController = navHostFragment.navController

        // Toolbar 联动
        val appBarConfig = AppBarConfiguration(
            topLevelDestinationIds = setOf(R.id.homeFragment, R.id.searchFragment, R.id.profileFragment),
            drawerLayout = binding.drawerLayout
        )
        setupActionBarWithNavController(navController, appBarConfig)

        // BottomNavigationView 联动
        binding.bottomNav.setupWithNavController(navController)
    }

    override fun onSupportNavigateUp(): Boolean =
        navController.navigateUp() || super.onSupportNavigateUp()
}
```

## 5. 嵌套导航图

```xml
<navigation app:startDestination="@id/homeFragment">
    <fragment android:id="@+id/homeFragment" ... />

    <!-- 嵌套图：登录流程 -->
    <navigation
        android:id="@+id/login_graph"
        app:startDestination="@id/loginFragment">
        <fragment android:id="@+id/loginFragment" ... />
        <fragment android:id="@+id/registerFragment" ... />
    </navigation>
</navigation>
```

```kotlin
// 导航到嵌套图
navController.navigate(R.id.login_graph)

// Fragment 间共享 ViewModel（通过 NavGraph scope）
class LoginFragment : Fragment() {
    private val sharedViewModel: AuthViewModel by navGraphViewModels(R.id.login_graph)
}
```

## 6. Navigation Compose 类型安全路由（2.8+）

> 🔄 更新于 2026-05-01

Navigation Compose 2.8+ 引入了基于 `@Serializable` 数据类的类型安全路由，替代字符串路由。Navigation 2.9.7 是当前稳定版。来源：[Android Developers - Navigation Compose](https://developer.android.com/guide/navigation/design/type-safety)

<!-- version-check: Navigation Compose 2.9.7, Navigation 3 alpha, checked 2026-05-01 -->

```kotlin
// 定义路由（使用 @Serializable 数据类）
@Serializable
object Home  // 无参数路由

@Serializable
data class Detail(val itemId: String)  // 带参数路由

@Serializable
data class Search(val query: String = "")  // 带默认值

// NavHost 使用类型安全路由
@Composable
fun AppNavigation() {
    val navController = rememberNavController()

    NavHost(navController = navController, startDestination = Home) {
        composable<Home> {
            HomeScreen(
                onItemClick = { id -> navController.navigate(Detail(itemId = id)) }
            )
        }
        composable<Detail> { backStackEntry ->
            // 自动解析参数，编译时类型检查
            val detail: Detail = backStackEntry.toRoute()
            DetailScreen(itemId = detail.itemId)
        }
        composable<Search> { backStackEntry ->
            val search: Search = backStackEntry.toRoute()
            SearchScreen(initialQuery = search.query)
        }
    }
}
```

### Navigation 3 预览版

Navigation 3 是全新的 Compose-first 导航库，开发者完全控制 back stack。目前处于 alpha 阶段，API 可能变化。

```kotlin
// Navigation 3 核心概念：开发者管理 back stack
// 依赖：androidx.navigation3:navigation3-compose:0.1.0-alpha04
@Composable
fun Nav3Example() {
    // 开发者自己持有 back stack
    val backStack = rememberMutableStateListOf<Any>(Home)

    NavDisplay(
        backStack = backStack,
        onBack = { backStack.removeLastOrNull() }
    ) { destination ->
        when (destination) {
            is Home -> HomeScreen(
                onNavigate = { backStack.add(Detail(it)) }
            )
            is Detail -> DetailScreen(itemId = destination.itemId)
        }
    }
}
```

### Navigation 版本选择

```
你的项目情况？
├─ Fragment + XML → Navigation 2.9.7（Safe Args）
├─ Compose 项目 → Navigation Compose 2.9.7（类型安全路由）
├─ 新项目想尝鲜 → Navigation 3 alpha（API 不稳定）
└─ KMP 项目 → Navigation Compose 2.9.7（支持 KMP）
```
