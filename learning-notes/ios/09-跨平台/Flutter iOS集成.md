# Flutter iOS 集成

> Author: Walter Wang

## 1. 创建 Flutter Module

```bash
# 创建 Flutter 模块
flutter create --template module my_flutter_module

# 目录结构
# my_flutter_module/
# ├── .ios/          # iOS 宿主工程（自动生成）
# ├── lib/           # Dart 代码
# └── pubspec.yaml
```

## 2. CocoaPods 集成

```ruby
# iOS 项目的 Podfile
flutter_application_path = '../my_flutter_module'
load File.join(flutter_application_path, '.ios', 'Flutter', 'podhelper.rb')

target 'MyApp' do
  install_all_flutter_pods(flutter_application_path)
end

post_install do |installer|
  flutter_post_install(installer)
end
```

## 3. 打开 Flutter 页面

```swift
import Flutter

class AppDelegate: FlutterAppDelegate {
    lazy var flutterEngine = FlutterEngine(name: "my_engine")

    override func application(_ application: UIApplication,
                              didFinishLaunchingWithOptions launchOptions: [UIApplication.LaunchOptionsKey: Any]?) -> Bool {
        flutterEngine.run()
        return super.application(application, didFinishLaunchingWithOptions: launchOptions)
    }
}

// 跳转到 Flutter 页面
class ViewController: UIViewController {
    @objc func openFlutter() {
        let engine = (UIApplication.shared.delegate as! AppDelegate).flutterEngine
        let flutterVC = FlutterViewController(engine: engine, nibName: nil, bundle: nil)
        present(flutterVC, animated: true)
    }
}
```

## 4. Platform Channel（原生通信）

```swift
// iOS 端：接收 Flutter 调用
let channel = FlutterMethodChannel(name: "com.app/native",
                                    binaryMessenger: flutterVC.binaryMessenger)

channel.setMethodCallHandler { (call, result) in
    switch call.method {
    case "getBatteryLevel":
        let level = UIDevice.current.batteryLevel
        result(Int(level * 100))
    case "showNativeAlert":
        let args = call.arguments as? [String: Any]
        let title = args?["title"] as? String ?? ""
        self.showAlert(title: title)
        result(nil)
    default:
        result(FlutterMethodNotImplemented)
    }
}

// iOS 端：主动调用 Flutter
channel.invokeMethod("updateData", arguments: ["key": "value"]) { result in
    print("Flutter 返回: \(result ?? "nil")")
}
```

```dart
// Flutter 端（Dart）
const channel = MethodChannel('com.app/native');

// 调用原生方法
Future<int> getBatteryLevel() async {
  final level = await channel.invokeMethod<int>('getBatteryLevel');
  return level ?? 0;
}

// 接收原生调用
channel.setMethodCallHandler((call) async {
  if (call.method == 'updateData') {
    final data = call.arguments as Map;
    // 处理数据
    return 'success';
  }
});
```

## 5. EventChannel（事件流）

```swift
// iOS 端：持续发送事件
let eventChannel = FlutterEventChannel(name: "com.app/events",
                                        binaryMessenger: flutterVC.binaryMessenger)

class LocationStreamHandler: NSObject, FlutterStreamHandler {
    var eventSink: FlutterEventSink?

    func onListen(withArguments arguments: Any?, eventSink events: @escaping FlutterEventSink) -> FlutterError? {
        self.eventSink = events
        startLocationUpdates()
        return nil
    }

    func onCancel(withArguments arguments: Any?) -> FlutterError? {
        eventSink = nil
        stopLocationUpdates()
        return nil
    }

    func sendLocation(_ lat: Double, _ lng: Double) {
        eventSink?(["lat": lat, "lng": lng])
    }
}

eventChannel.setStreamHandler(LocationStreamHandler())
```
