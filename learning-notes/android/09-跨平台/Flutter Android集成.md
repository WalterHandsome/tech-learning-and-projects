# Flutter Android 集成

> Author: Walter Wang

## 1. Flutter Module 集成

```kotlin
// settings.gradle.kts
// 将 Flutter Module 作为子项目
setBinding(Binding(gradle))
evaluate(File(settingsDir, "../flutter_module/.android/include_flutter.groovy"))

// app/build.gradle.kts
dependencies {
    implementation(project(":flutter"))
}
```

## 2. 启动 Flutter 页面

```kotlin
// 方式一：FlutterActivity
class MainActivity : AppCompatActivity() {
    fun openFlutterPage() {
        startActivity(
            FlutterActivity
                .withNewEngine()
                .initialRoute("/home")
                .build(this)
        )
    }

    // 缓存引擎（加速启动）
    fun openWithCachedEngine() {
        startActivity(
            FlutterActivity
                .withCachedEngine("my_engine")
                .build(this)
        )
    }
}

// Application 中预热引擎
class MyApp : Application() {
    override fun onCreate() {
        super.onCreate()
        val flutterEngine = FlutterEngine(this).apply {
            dartExecutor.executeDartEntrypoint(DartExecutor.DartEntrypoint.createDefault())
        }
        FlutterEngineCache.getInstance().put("my_engine", flutterEngine)
    }
}
```

## 3. FlutterFragment

```kotlin
class HostActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_host)

        val flutterFragment = FlutterFragment
            .withCachedEngine("my_engine")
            .build<FlutterFragment>()

        supportFragmentManager.beginTransaction()
            .replace(R.id.flutter_container, flutterFragment)
            .commit()
    }
}
```

## 4. MethodChannel（方法调用）

```kotlin
// Android 端
class MainActivity : FlutterActivity() {
    override fun configureFlutterEngine(flutterEngine: FlutterEngine) {
        super.configureFlutterEngine(flutterEngine)

        MethodChannel(flutterEngine.dartExecutor.binaryMessenger, "com.example/native")
            .setMethodCallHandler { call, result ->
                when (call.method) {
                    "getBatteryLevel" -> {
                        val level = getBatteryLevel()
                        if (level != -1) result.success(level)
                        else result.error("UNAVAILABLE", "电量信息不可用", null)
                    }
                    "getUserInfo" -> {
                        val name = call.argument<String>("name")
                        result.success(mapOf("name" to name, "platform" to "Android"))
                    }
                    else -> result.notImplemented()
                }
            }
    }

    private fun getBatteryLevel(): Int {
        val manager = getSystemService(BATTERY_SERVICE) as BatteryManager
        return manager.getIntProperty(BatteryManager.BATTERY_PROPERTY_CAPACITY)
    }
}
```

```dart
// Flutter 端
class NativeBridge {
  static const _channel = MethodChannel('com.example/native');

  static Future<int> getBatteryLevel() async {
    return await _channel.invokeMethod('getBatteryLevel');
  }

  static Future<Map> getUserInfo(String name) async {
    return await _channel.invokeMethod('getUserInfo', {'name': name});
  }
}
```

## 5. EventChannel（事件流）

```kotlin
// Android 端：持续发送事件
EventChannel(flutterEngine.dartExecutor.binaryMessenger, "com.example/events")
    .setStreamHandler(object : EventChannel.StreamHandler {
        private var eventSink: EventChannel.EventSink? = null

        override fun onListen(arguments: Any?, events: EventChannel.EventSink) {
            eventSink = events
            // 发送位置更新
            locationManager.requestLocationUpdates(provider, 1000, 10f) { location ->
                eventSink?.success(mapOf("lat" to location.latitude, "lng" to location.longitude))
            }
        }

        override fun onCancel(arguments: Any?) {
            eventSink = null
            locationManager.removeUpdates(listener)
        }
    })
```

```dart
// Flutter 端：监听事件
final _eventChannel = EventChannel('com.example/events');
_eventChannel.receiveBroadcastStream().listen((event) {
  print('Location: ${event['lat']}, ${event['lng']}');
});
```
