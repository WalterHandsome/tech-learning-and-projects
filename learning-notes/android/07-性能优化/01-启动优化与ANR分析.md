# 启动优化与 ANR 分析
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. 启动类型

```kotlin
// 冷启动：进程不存在 → 创建进程 → Application → Activity
// 温启动：进程存在，Activity 被回收 → 重建 Activity
// 热启动：进程和 Activity 都在 → onRestart → onStart

// 测量启动时间
// adb shell am start-activity -W com.example.app/.MainActivity
// TotalTime: 冷启动总时间
```

## 2. App Startup 库

```kotlin
// 依赖: androidx.startup:startup-runtime

// 定义 Initializer
class TimberInitializer : Initializer<Unit> {
    override fun create(context: Context) {
        Timber.plant(Timber.DebugTree())
    }
    override fun dependencies(): List<Class<out Initializer<*>>> = emptyList()
}

class CoilInitializer : Initializer<ImageLoader> {
    override fun create(context: Context): ImageLoader {
        return ImageLoader.Builder(context)
            .memoryCache { MemoryCache.Builder(context).maxSizePercent(0.25).build() }
            .build()
    }
    override fun dependencies() = listOf(TimberInitializer::class.java)
}

// AndroidManifest.xml
// <provider android:name="androidx.startup.InitializationProvider"
//     android:authorities="${applicationId}.androidx-startup">
//     <meta-data android:name="com.example.CoilInitializer"
//         android:value="androidx.startup" />
// </provider>

// 延迟初始化
AppInitializer.getInstance(context).initializeComponent(CoilInitializer::class.java)
```

## 3. 启动优化策略

```kotlin
class MyApp : Application() {
    override fun onCreate() {
        super.onCreate()
        // 1. 必要初始化（主线程）
        initCrashReporter()

        // 2. 异步初始化
        CoroutineScope(Dispatchers.Default).launch {
            initAnalytics()
            initPush()
        }

        // 3. 延迟初始化（首屏显示后）
        // 在 Activity.onResume 后执行
    }
}

// IdleHandler：空闲时执行
class MainActivity : AppCompatActivity() {
    override fun onResume() {
        super.onResume()
        Looper.myQueue().addIdleHandler {
            initNonCriticalSDKs()
            false  // 返回 false 表示只执行一次
        }
    }
}
```

## 4. Baseline Profiles

```kotlin
// 依赖: androidx.benchmark:benchmark-macro-junit4

@RunWith(AndroidJUnit4::class)
class BaselineProfileGenerator {
    @get:Rule
    val rule = BaselineProfileRule()

    @Test
    fun generateBaselineProfile() {
        rule.collect(packageName = "com.example.app") {
            // 冷启动
            pressHome()
            startActivityAndWait()

            // 关键用户路径
            device.findObject(By.text("搜索")).click()
            device.waitForIdle()
            device.findObject(By.res("search_input")).text = "kotlin"
        }
    }
}

// build.gradle.kts
// baselineProfile { automaticGenerationDuringBuild = true }
```

## 5. ANR 分析

```kotlin
// ANR 触发条件：
// - 主线程 5 秒内未响应输入事件
// - BroadcastReceiver 10 秒内未完成
// - Service 20 秒内未完成

// ❌ 错误：主线程执行耗时操作
class BadActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        val data = database.queryAll()  // 主线程 IO → ANR
    }
}

// ✅ 正确：异步执行
class GoodActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        lifecycleScope.launch {
            val data = withContext(Dispatchers.IO) { database.queryAll() }
            updateUI(data)
        }
    }
}

// StrictMode 检测
if (BuildConfig.DEBUG) {
    StrictMode.setThreadPolicy(
        StrictMode.ThreadPolicy.Builder()
            .detectDiskReads()
            .detectDiskWrites()
            .detectNetwork()
            .penaltyLog()
            .build()
    )
}

// ANR 日志位置: /data/anr/traces.txt
// adb pull /data/anr/traces.txt
```
