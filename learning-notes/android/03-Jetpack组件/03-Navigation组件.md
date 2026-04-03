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
