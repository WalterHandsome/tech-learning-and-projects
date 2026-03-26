# Activity 与 Fragment 生命周期

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
