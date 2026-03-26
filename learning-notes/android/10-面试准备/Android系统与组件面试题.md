# Android 系统与组件面试题

## 1. Activity 启动模式

```kotlin
// standard：默认，每次创建新实例
// singleTop：栈顶复用，触发 onNewIntent
// singleTask：栈内复用，清除其上所有 Activity
// singleInstance：独占任务栈

// AndroidManifest.xml
// <activity android:launchMode="singleTask" />

// Intent Flag
intent.flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TOP

// 场景：
// standard → 普通页面
// singleTop → 通知点击打开的页面（避免重复创建）
// singleTask → 首页（返回时清除栈）
// singleInstance → 来电界面（独立任务栈）

// taskAffinity 控制任务栈归属
// <activity android:taskAffinity="com.example.task2" />
```

## 2. Handler 机制

```kotlin
// 核心组件: Looper, MessageQueue, Handler, Message

// 主线程 Looper 在 ActivityThread.main() 中创建
// Looper.prepareMainLooper() → Looper.loop()

// 工作原理:
// 1. Handler.sendMessage() → MessageQueue.enqueueMessage()
// 2. Looper.loop() 不断从 MessageQueue 取消息
// 3. msg.target.dispatchMessage(msg) → Handler.handleMessage()

// 子线程使用 Handler
class WorkerThread : Thread() {
    lateinit var handler: Handler

    override fun run() {
        Looper.prepare()
        handler = Handler(Looper.myLooper()!!) { msg ->
            // 在子线程处理消息
            true
        }
        Looper.loop()
    }
}

// 现代替代方案
// 协程: viewModelScope.launch { }
// Flow: flow { }.flowOn(Dispatchers.IO)

// IdleHandler: 主线程空闲时执行
Looper.myQueue().addIdleHandler {
    doIdleWork()
    false  // false = 执行一次
}
```

## 3. Binder IPC

```kotlin
// Binder 是 Android 跨进程通信的核心机制
// Client → Proxy → Binder Driver(内核) → Stub → Server

// AIDL 定义接口
// IUserService.aidl
// interface IUserService {
//     User getUser(int id);
//     void saveUser(in User user);
// }

// 服务端
class UserService : Service() {
    private val binder = object : IUserService.Stub() {
        override fun getUser(id: Int): User = database.getUser(id)
        override fun saveUser(user: User) { database.save(user) }
    }
    override fun onBind(intent: Intent): IBinder = binder
}

// 客户端
val connection = object : ServiceConnection {
    override fun onServiceConnected(name: ComponentName, service: IBinder) {
        val userService = IUserService.Stub.asInterface(service)
        val user = userService.getUser(1)
    }
    override fun onServiceDisconnected(name: ComponentName) {}
}
bindService(intent, connection, BIND_AUTO_CREATE)
```

## 4. View 绘制流程

```kotlin
// ViewRootImpl.performTraversals() 触发三大流程

// 1. Measure（测量）
// MeasureSpec = Mode + Size
// EXACTLY: match_parent / 固定值
// AT_MOST: wrap_content
// UNSPECIFIED: 不限制

// 2. Layout（布局）
// 确定 View 在父容器中的位置 (left, top, right, bottom)

// 3. Draw（绘制）
// drawBackground → onDraw → dispatchDraw(子View) → onDrawForeground

// requestLayout(): 重新 measure + layout
// invalidate(): 重新 draw（主线程）
// postInvalidate(): 重新 draw（子线程）

// View.post() 为什么能获取宽高？
// 因为 post 的 Runnable 在 performTraversals 之后执行
view.post {
    val width = view.width   // 此时已完成测量
    val height = view.height
}
```

## 5. 事件分发机制

```kotlin
// 分发顺序: Activity → Window → DecorView → ViewGroup → View

// ViewGroup 三个关键方法:
// dispatchTouchEvent(): 分发事件
// onInterceptTouchEvent(): 是否拦截（ViewGroup 独有）
// onTouchEvent(): 处理事件

// 伪代码
fun dispatchTouchEvent(ev: MotionEvent): Boolean {
    var consumed = false
    if (onInterceptTouchEvent(ev)) {
        consumed = onTouchEvent(ev)      // 自己处理
    } else {
        consumed = child.dispatchTouchEvent(ev)  // 传给子 View
    }
    return consumed
}

// 滑动冲突解决
// 外部拦截法（父 View 决定）
override fun onInterceptTouchEvent(ev: MotionEvent): Boolean {
    return when (ev.action) {
        MotionEvent.ACTION_DOWN -> false
        MotionEvent.ACTION_MOVE -> needIntercept(ev)  // 根据条件拦截
        else -> false
    }
}

// 内部拦截法（子 View 决定）
// 子 View: parent.requestDisallowInterceptTouchEvent(true)
```

## 6. Context 类型

```kotlin
// Application Context: 全局单例，生命周期 = 应用
// Activity Context: 随 Activity 销毁
// Service Context: 随 Service 销毁

// 使用原则:
// 启动 Activity → Activity Context
// 弹 Dialog → Activity Context
// 启动 Service → 任意 Context
// 发送广播 → 任意 Context
// 加载资源 → 任意 Context
// 单例中 → Application Context（避免泄漏）
```
