# 内存优化与 LeakCanary

## 1. 常见内存泄漏场景

```kotlin
// ❌ 错误：匿名内部类持有 Activity 引用
class LeakyActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        val handler = object : Handler(Looper.getMainLooper()) {
            override fun handleMessage(msg: Message) {
                // 隐式持有 Activity 引用
                updateUI()
            }
        }
        handler.sendEmptyMessageDelayed(0, 60_000)
    }
}

// ✅ 正确：使用弱引用或 lifecycleScope
class SafeActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        lifecycleScope.launch {
            delay(60_000)
            updateUI()  // 自动随生命周期取消
        }
    }
}

// ❌ 错误：Fragment 中持有 Binding
class LeakyFragment : Fragment() {
    private val binding: FragmentBinding = FragmentBinding.inflate(layoutInflater)
    // binding 在 onDestroyView 后仍被持有
}

// ✅ 正确：onDestroyView 中置空
class SafeFragment : Fragment() {
    private var _binding: FragmentBinding? = null
    private val binding get() = _binding!!
    override fun onDestroyView() { super.onDestroyView(); _binding = null }
}

// ❌ 错误：单例持有 Context
object AppManager {
    lateinit var context: Context  // 如果传入 Activity 会泄漏
}

// ✅ 正确：使用 Application Context
object AppManager {
    lateinit var context: Context
    fun init(app: Application) { context = app.applicationContext }
}
```

## 2. LeakCanary

```kotlin
// build.gradle.kts
// debugImplementation("com.squareup.leakcanary:leakcanary-android:2.13")

// 自动检测：Activity/Fragment/ViewModel/View/Service 泄漏
// 无需额外代码，debug 构建自动启用

// 手动监控自定义对象
class MyManager {
    fun destroy() {
        // 清理后告诉 LeakCanary 监控此对象
        AppWatcher.objectWatcher.expectWeaklyReachable(
            this, "MyManager was destroyed"
        )
    }
}
```

## 3. Android Profiler 内存分析

```kotlin
// 触发 GC 后查看内存快照
// Android Studio → Profiler → Memory → Dump Java Heap

// 代码中记录内存信息
fun logMemoryInfo(context: Context) {
    val activityManager = context.getSystemService<ActivityManager>()
    val memInfo = ActivityManager.MemoryInfo()
    activityManager?.getMemoryInfo(memInfo)
    Log.d("Memory", "可用: ${memInfo.availMem / 1024 / 1024}MB")
    Log.d("Memory", "总量: ${memInfo.totalMem / 1024 / 1024}MB")
    Log.d("Memory", "低内存: ${memInfo.lowMemory}")
}
```

## 4. Bitmap 优化

```kotlin
// 按需采样加载大图
fun decodeSampledBitmap(res: Resources, resId: Int, reqWidth: Int, reqHeight: Int): Bitmap {
    val options = BitmapFactory.Options().apply { inJustDecodeBounds = true }
    BitmapFactory.decodeResource(res, resId, options)

    options.inSampleSize = calculateInSampleSize(options, reqWidth, reqHeight)
    options.inJustDecodeBounds = false
    return BitmapFactory.decodeResource(res, resId, options)
}

fun calculateInSampleSize(options: BitmapFactory.Options, reqW: Int, reqH: Int): Int {
    val (height, width) = options.outHeight to options.outWidth
    var inSampleSize = 1
    if (height > reqH || width > reqW) {
        val halfH = height / 2; val halfW = width / 2
        while (halfH / inSampleSize >= reqH && halfW / inSampleSize >= reqW) {
            inSampleSize *= 2
        }
    }
    return inSampleSize
}

// 使用 Coil 自动处理
AsyncImage(
    model = ImageRequest.Builder(context)
        .data(largeImageUrl)
        .size(300, 300)  // 自动缩放
        .build(),
    contentDescription = null
)
```

## 5. 内存优化策略

```kotlin
// 监听内存不足
class MyApp : Application(), ComponentCallbacks2 {
    override fun onTrimMemory(level: Int) {
        when (level) {
            TRIM_MEMORY_UI_HIDDEN -> clearImageCache()
            TRIM_MEMORY_RUNNING_LOW -> reduceMemoryUsage()
            TRIM_MEMORY_COMPLETE -> releaseAllCaches()
        }
    }
}

// 使用 SparseArray 替代 HashMap<Int, Object>
val sparseArray = SparseArray<String>()
sparseArray.put(1, "one")

// 避免自动装箱
val intArray = IntArray(100)  // 而非 Array<Int>
```
