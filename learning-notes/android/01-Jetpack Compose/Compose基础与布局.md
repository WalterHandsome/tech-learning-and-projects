# Compose 基础与布局

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
