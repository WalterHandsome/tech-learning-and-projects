# Compose 动画与手势
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. animateXxxAsState

```kotlin
// 颜色动画
@Composable
fun AnimatedButton(isSelected: Boolean, onClick: () -> Unit) {
    val backgroundColor by animateColorAsState(
        targetValue = if (isSelected) Color.Blue else Color.Gray,
        animationSpec = tween(durationMillis = 300)
    )
    val size by animateDpAsState(
        targetValue = if (isSelected) 48.dp else 36.dp,
        animationSpec = spring(dampingRatio = Spring.DampingRatioMediumBouncy)
    )

    Box(
        modifier = Modifier
            .size(size)
            .background(backgroundColor, CircleShape)
            .clickable { onClick() }
    )
}

// Float 动画
val alpha by animateFloatAsState(
    targetValue = if (visible) 1f else 0f,
    animationSpec = tween(500)
)
Box(Modifier.graphicsLayer { this.alpha = alpha })
```

## 2. AnimatedVisibility

```kotlin
@Composable
fun ExpandableCard(title: String, content: String) {
    var expanded by remember { mutableStateOf(false) }

    Card(modifier = Modifier.clickable { expanded = !expanded }) {
        Column(Modifier.padding(16.dp)) {
            Text(title, style = MaterialTheme.typography.titleMedium)
            AnimatedVisibility(
                visible = expanded,
                enter = fadeIn() + expandVertically(),
                exit = fadeOut() + shrinkVertically()
            ) {
                Text(content, Modifier.padding(top = 8.dp))
            }
        }
    }
}
```

## 3. AnimatedContent

```kotlin
@Composable
fun CounterDisplay(count: Int) {
    AnimatedContent(
        targetState = count,
        transitionSpec = {
            if (targetState > initialState) {
                slideInVertically { -it } + fadeIn() togetherWith
                    slideOutVertically { it } + fadeOut()
            } else {
                slideInVertically { it } + fadeIn() togetherWith
                    slideOutVertically { -it } + fadeOut()
            }.using(SizeTransform(clip = false))
        }
    ) { target ->
        Text("$target", style = MaterialTheme.typography.displayLarge)
    }
}

// Crossfade（简单切换）
Crossfade(targetState = currentPage) { page ->
    when (page) {
        "home" -> HomeScreen()
        "settings" -> SettingsScreen()
    }
}
```

## 4. updateTransition

```kotlin
enum class BoxState { Collapsed, Expanded }

@Composable
fun TransitionBox() {
    var state by remember { mutableStateOf(BoxState.Collapsed) }
    val transition = updateTransition(targetState = state, label = "box")

    val size by transition.animateDp(label = "size") {
        when (it) { BoxState.Collapsed -> 64.dp; BoxState.Expanded -> 200.dp }
    }
    val color by transition.animateColor(label = "color") {
        when (it) { BoxState.Collapsed -> Color.Blue; BoxState.Expanded -> Color.Red }
    }
    val cornerRadius by transition.animateDp(label = "corner") {
        when (it) { BoxState.Collapsed -> 32.dp; BoxState.Expanded -> 8.dp }
    }

    Box(
        modifier = Modifier
            .size(size)
            .clip(RoundedCornerShape(cornerRadius))
            .background(color)
            .clickable {
                state = if (state == BoxState.Collapsed) BoxState.Expanded else BoxState.Collapsed
            }
    )
}
```

## 5. 无限动画

```kotlin
@Composable
fun PulsingDot() {
    val infiniteTransition = rememberInfiniteTransition()
    val scale by infiniteTransition.animateFloat(
        initialValue = 0.8f,
        targetValue = 1.2f,
        animationSpec = infiniteRepeatable(
            animation = tween(600),
            repeatMode = RepeatMode.Reverse
        )
    )
    Box(
        Modifier.size(20.dp).graphicsLayer { scaleX = scale; scaleY = scale }
            .background(Color.Red, CircleShape)
    )
}
```

## 6. 手势检测

```kotlin
// 点击 / 长按
Modifier.combinedClickable(
    onClick = { /* 单击 */ },
    onLongClick = { /* 长按 */ },
    onDoubleClick = { /* 双击 */ }
)

// 拖拽
@Composable
fun DraggableBox() {
    var offsetX by remember { mutableFloatStateOf(0f) }
    var offsetY by remember { mutableFloatStateOf(0f) }

    Box(
        Modifier
            .offset { IntOffset(offsetX.roundToInt(), offsetY.roundToInt()) }
            .size(80.dp)
            .background(Color.Blue, RoundedCornerShape(8.dp))
            .pointerInput(Unit) {
                detectDragGestures { change, dragAmount ->
                    change.consume()
                    offsetX += dragAmount.x
                    offsetY += dragAmount.y
                }
            }
    )
}

// 滑动删除（SwipeToDismiss）
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun SwipeItem(onDismiss: () -> Unit, content: @Composable () -> Unit) {
    val dismissState = rememberSwipeToDismissBoxState(
        confirmValueChange = { it == SwipeToDismissBoxValue.EndToStart }
    )
    LaunchedEffect(dismissState.currentValue) {
        if (dismissState.currentValue == SwipeToDismissBoxValue.EndToStart) onDismiss()
    }
    SwipeToDismissBox(
        state = dismissState,
        backgroundContent = {
            Box(Modifier.fillMaxSize().background(Color.Red).padding(16.dp)) {
                Icon(Icons.Default.Delete, null, Modifier.align(Alignment.CenterEnd))
            }
        }
    ) { content() }
}
```
