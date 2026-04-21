# Compose 基础与布局
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. @Composable 基础

```kotlin
// 可组合函数
@Composable
fun Greeting(name: String, modifier: Modifier = Modifier) {
    Text(
        text = "Hello, $name!",
        modifier = modifier.padding(16.dp),
        style = MaterialTheme.typography.headlineMedium
    )
}

// 预览
@Preview(showBackground = true)
@Composable
fun GreetingPreview() {
    MyTheme { Greeting("Android") }
}
```

## 2. 基础组件

```kotlin
// Text
Text(
    text = "标题",
    fontSize = 24.sp,
    fontWeight = FontWeight.Bold,
    color = Color.DarkGray,
    maxLines = 2,
    overflow = TextOverflow.Ellipsis
)

// Image
Image(
    painter = painterResource(R.drawable.photo),
    contentDescription = "照片",
    modifier = Modifier.size(120.dp).clip(CircleShape),
    contentScale = ContentScale.Crop
)

// AsyncImage (Coil)
AsyncImage(
    model = "https://example.com/image.jpg",
    contentDescription = null,
    modifier = Modifier.fillMaxWidth(),
    placeholder = painterResource(R.drawable.placeholder)
)

// Button
Button(
    onClick = { /* 点击事件 */ },
    colors = ButtonDefaults.buttonColors(containerColor = Color.Blue)
) {
    Icon(Icons.Default.Add, contentDescription = null)
    Spacer(Modifier.width(8.dp))
    Text("添加")
}
```

## 3. 布局

```kotlin
// Column（垂直排列）
Column(
    modifier = Modifier.fillMaxSize().padding(16.dp),
    verticalArrangement = Arrangement.spacedBy(8.dp),
    horizontalAlignment = Alignment.CenterHorizontally
) {
    Text("第一行")
    Text("第二行")
}

// Row（水平排列）
Row(
    modifier = Modifier.fillMaxWidth(),
    horizontalArrangement = Arrangement.SpaceBetween,
    verticalAlignment = Alignment.CenterVertically
) {
    Text("左侧")
    IconButton(onClick = {}) { Icon(Icons.Default.ArrowForward, null) }
}

// Box（层叠布局）
Box(modifier = Modifier.size(200.dp)) {
    Image(painter, null, Modifier.matchParentSize())
    Text("覆盖文字", Modifier.align(Alignment.BottomCenter))
}
```

## 4. LazyColumn / LazyRow

```kotlin
@Composable
fun UserList(users: List<User>) {
    LazyColumn(
        contentPadding = PaddingValues(16.dp),
        verticalArrangement = Arrangement.spacedBy(8.dp)
    ) {
        items(users, key = { it.id }) { user ->
            UserCard(user)
        }
        item { Spacer(Modifier.height(80.dp)) }
    }
}

// LazyVerticalGrid
LazyVerticalGrid(
    columns = GridCells.Adaptive(minSize = 128.dp),
    contentPadding = PaddingValues(8.dp)
) {
    items(photos) { photo -> PhotoCard(photo) }
}
```

## 5. Modifier

```kotlin
Modifier
    .fillMaxWidth()
    .padding(horizontal = 16.dp, vertical = 8.dp)
    .clip(RoundedCornerShape(12.dp))
    .background(MaterialTheme.colorScheme.surface)
    .border(1.dp, Color.Gray, RoundedCornerShape(12.dp))
    .clickable { onClick() }
    .shadow(4.dp, RoundedCornerShape(12.dp))
```

## 6. Scaffold 与 Material3

```kotlin
@Composable
fun MainScreen(navController: NavController) {
    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("首页") },
                actions = {
                    IconButton(onClick = {}) { Icon(Icons.Default.Search, "搜索") }
                }
            )
        },
        bottomBar = {
            NavigationBar {
                NavigationBarItem(
                    selected = true,
                    onClick = {},
                    icon = { Icon(Icons.Default.Home, null) },
                    label = { Text("首页") }
                )
            }
        },
        floatingActionButton = {
            FloatingActionButton(onClick = {}) { Icon(Icons.Default.Add, "添加") }
        }
    ) { padding ->
        LazyColumn(modifier = Modifier.padding(padding)) {
            items(dataList) { item -> ListItem(item) }
        }
    }
}
```
## 🎬 推荐视频资源

- [Philipp Lackner - Jetpack Compose Full Course](https://www.youtube.com/watch?v=cDabx3SjuOY) — Compose完整课程
- [Android Developers - Compose Tutorial](https://www.youtube.com/watch?v=cDabx3SjuOY) — 官方Compose教程
- [Stevdza-San - Jetpack Compose](https://www.youtube.com/@StevdzaSan) — Compose教程频道
### 📺 B站（Bilibili）
- [Jetpack Compose中文教程](https://www.bilibili.com/video/BV1HV4y1a7n4) — Compose入门到实战

### 🌐 其他平台
- [Android官方Compose教程](https://developer.android.com/courses/android-basics-compose/course) — Google官方Compose课程（免费）
- [Jetpack Compose官方文档](https://developer.android.com/develop/ui/compose/documentation) — 官方文档


## 7. Compose 2026 版本演进

<!-- version-check: Compose BOM 2026.03.00, Compose 1.10.x, checked 2026-04-21 -->

> 🔄 更新于 2026-04-21

### 当前版本

| 组件 | 版本 | 说明 |
|------|------|------|
| Compose BOM | **2026.03.00** | 统一管理所有 Compose 库版本 |
| Compose UI | **1.10.x** | 核心 UI 库 |
| Material3 | **1.4.x** | Material Design 3 组件 |
| Compose Compiler | 与 Kotlin 对齐 | Kotlin 2.0+ 内置，无需单独指定版本 |

### Compose Compiler 变化（Kotlin 2.0+）

```kotlin
// Kotlin 2.0 之前：Compose Compiler 是独立的 Kotlin 编译器插件
// Kotlin 2.0 之后：Compose Compiler 集成到 Kotlin Gradle 插件中

// build.gradle.kts
plugins {
    alias(libs.plugins.kotlin.android)
    alias(libs.plugins.compose.compiler)  // 新增
}

// 不再需要 composeOptions 块
// Compose Compiler 版本自动与 Kotlin 版本对齐
```

### 强类型资源（Compose 1.7+）

```kotlin
// 类型安全的资源访问（替代 R.string / R.drawable）
// 需要在 build.gradle.kts 中启用
android {
    buildFeatures {
        compose = true
    }
}

// 使用
@Composable
fun Greeting() {
    Text(text = stringResource(Res.string.greeting))
    Image(painter = painterResource(Res.drawable.logo), contentDescription = null)
}
```

> 来源：[Compose BOM](https://developer.android.com/develop/ui/compose/bom)、[Compose Releases](https://developer.android.com/jetpack/androidx/releases/compose)
