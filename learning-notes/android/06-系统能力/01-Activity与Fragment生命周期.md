# Activity 与 Fragment 生命周期
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. Activity 生命周期

```kotlin
class MainActivity : AppCompatActivity() {
    // 完整生命周期: onCreate → onStart → onResume → onPause → onStop → onDestroy
    // 可见: onStart ~ onStop
    // 前台: onResume ~ onPause

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)
        // 初始化 UI、恢复状态
        savedInstanceState?.let {
            val query = it.getString("search_query", "")
        }
    }

    override fun onSaveInstanceState(outState: Bundle) {
        super.onSaveInstanceState(outState)
        outState.putString("search_query", currentQuery)
    }

    override fun onStart() { super.onStart(); /* 注册监听 */ }
    override fun onResume() { super.onResume(); /* 恢复动画/传感器 */ }
    override fun onPause() { super.onPause(); /* 暂停动画 */ }
    override fun onStop() { super.onStop(); /* 释放资源 */ }
    override fun onDestroy() { super.onDestroy(); /* 最终清理 */ }
}
```

## 2. Fragment 生命周期

```kotlin
class UserFragment : Fragment(R.layout.fragment_user) {
    // onAttach → onCreate → onCreateView → onViewCreated → onStart → onResume
    // → onPause → onStop → onDestroyView → onDestroy → onDetach

    private var _binding: FragmentUserBinding? = null
    private val binding get() = _binding!!

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        _binding = FragmentUserBinding.bind(view)
        setupUI()
        observeData()
    }

    private fun observeData() {
        viewLifecycleOwner.lifecycleScope.launch {
            repeatOnLifecycle(Lifecycle.State.STARTED) {
                viewModel.uiState.collect { updateUI(it) }
            }
        }
    }

    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null  // 防止内存泄漏
    }
}
```

## 3. 配置变更处理

```kotlin
// 方式一：ViewModel 保存数据（推荐）
class SearchViewModel : ViewModel() {
    var searchQuery = ""  // 配置变更后自动保留
}

// 方式二：声明处理特定配置变更
// AndroidManifest.xml:
// android:configChanges="orientation|screenSize|keyboardHidden"
override fun onConfigurationChanged(newConfig: Configuration) {
    super.onConfigurationChanged(newConfig)
    if (newConfig.orientation == Configuration.ORIENTATION_LANDSCAPE) {
        // 横屏处理
    }
}

// 方式三：rememberSaveable（Compose）
var text by rememberSaveable { mutableStateOf("") }
```

## 4. Activity Result API

```kotlin
class PhotoFragment : Fragment() {
    // 替代 startActivityForResult
    private val pickImage = registerForActivityResult(
        ActivityResultContracts.GetContent()
    ) { uri: Uri? ->
        uri?.let { loadImage(it) }
    }

    private val requestPermission = registerForActivityResult(
        ActivityResultContracts.RequestPermission()
    ) { granted ->
        if (granted) openCamera() else showPermissionDenied()
    }

    private val takePicture = registerForActivityResult(
        ActivityResultContracts.TakePicturePreview()
    ) { bitmap ->
        bitmap?.let { showPreview(it) }
    }

    fun onPickImageClick() { pickImage.launch("image/*") }
    fun onCameraClick() { requestPermission.launch(Manifest.permission.CAMERA) }
}
```

## 5. Fragment 通信

```kotlin
// 方式一：共享 ViewModel
class SharedViewModel : ViewModel() {
    val selectedItem = MutableStateFlow<Item?>(null)
}

class ListFragment : Fragment() {
    private val sharedVm: SharedViewModel by activityViewModels()
    fun onItemClick(item: Item) { sharedVm.selectedItem.value = item }
}

class DetailFragment : Fragment() {
    private val sharedVm: SharedViewModel by activityViewModels()
}

// 方式二：Fragment Result API
// 发送
parentFragmentManager.setFragmentResult("requestKey", bundleOf("data" to "value"))

// 接收
parentFragmentManager.setFragmentResultListener("requestKey", viewLifecycleOwner) { _, bundle ->
    val result = bundle.getString("data")
}
```

> 🔄 更新于 2026-04-23

## 6. Android 16 (API 36) 行为变化

<!-- version-check: Android 16 API 36, Activity behavior changes, checked 2026-04-23 -->

Android 16 对 Activity 和窗口行为引入了多项强制性变化，面向 targetSdk 36 的应用必须适配。来源：[Android 16 Behavior Changes](https://developer.android.com/about/versions/16/behavior-changes-16)

### 6.1 Edge-to-Edge 强制启用

```kotlin
// Android 15 中可以通过以下方式 opt-out：
// R.attr.windowOptOutEdgeToEdgeEnforcement = true
// ⚠️ Android 16 中此属性已废弃且无效！

// 正确做法：适配 edge-to-edge
class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        // enableEdgeToEdge() 在 API 36 中已默认启用
        enableEdgeToEdge()

        setContent {
            // 使用 WindowInsets 处理系统栏
            Scaffold(
                modifier = Modifier.fillMaxSize(),
                contentWindowInsets = WindowInsets(0) // 自行处理 insets
            ) { innerPadding ->
                Content(modifier = Modifier.padding(innerPadding))
            }
        }
    }
}
```

### 6.2 Predictive Back 默认启用

```kotlin
// Android 16 中 predictive back 系统动画默认启用：
// - back-to-home 动画
// - cross-task 动画
// - cross-activity 动画

// 如果使用自定义返回逻辑，必须迁移到 OnBackPressedCallback
class MyFragment : Fragment() {
    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        // ✅ 正确：使用 OnBackPressedCallback
        requireActivity().onBackPressedDispatcher.addCallback(
            viewLifecycleOwner
        ) {
            // 自定义返回逻辑
            if (hasUnsavedChanges) {
                showSaveDialog()
            } else {
                isEnabled = false
                requireActivity().onBackPressedDispatcher.onBackPressed()
            }
        }
    }
}
```

### 6.3 大屏幕适配

```
Android 16 大屏幕变化：
├─ 限制屏幕方向和可调整大小的能力被逐步移除
├─ 应用必须支持任意窗口大小和宽高比
├─ 多窗口模式成为标准行为
└─ 建议使用 WindowSizeClass 适配不同屏幕
```
