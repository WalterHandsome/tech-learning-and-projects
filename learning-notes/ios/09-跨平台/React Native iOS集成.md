# React Native iOS 集成

> Author: Walter Wang

## 1. 集成到现有 iOS 项目

```ruby
# Podfile
require_relative '../node_modules/react-native/scripts/react_native_pods'

platform :ios, '16.0'

target 'MyApp' do
  config = use_native_modules!
  use_react_native!(path: '../node_modules/react-native')
end
```

```bash
# 安装依赖
cd ios && pod install
```

## 2. 加载 RN 页面

```swift
import React

class RNViewController: UIViewController {
    override func viewDidLoad() {
        super.viewDidLoad()

        let jsCodeLocation = URL(string: "http://localhost:8081/index.bundle?platform=ios")!

        let rootView = RCTRootView(
            bundleURL: jsCodeLocation,
            moduleName: "MyRNModule",
            initialProperties: ["userId": "123"],
            launchOptions: nil
        )
        view = rootView
    }
}

// 跳转到 RN 页面
func openRNPage() {
    let rnVC = RNViewController()
    navigationController?.pushViewController(rnVC, animated: true)
}
```

## 3. Native Module（原生模块）

```swift
import React

@objc(DeviceInfoModule)
class DeviceInfoModule: NSObject {

    @objc static func requiresMainQueueSetup() -> Bool { return false }

    @objc func getDeviceInfo(_ resolve: @escaping RCTPromiseResolveBlock,
                              rejecter reject: @escaping RCTPromiseRejectBlock) {
        let info: [String: Any] = [
            "model": UIDevice.current.model,
            "systemVersion": UIDevice.current.systemVersion,
            "name": UIDevice.current.name
        ]
        resolve(info)
    }

    @objc func showNativeAlert(_ title: String, message: String) {
        DispatchQueue.main.async {
            let alert = UIAlertController(title: title, message: message, preferredStyle: .alert)
            alert.addAction(UIAlertAction(title: "OK", style: .default))
            UIApplication.shared.keyWindow?.rootViewController?.present(alert, animated: true)
        }
    }
}
```

```objc
// DeviceInfoModule.m（桥接文件）
#import <React/RCTBridgeModule.h>

@interface RCT_EXTERN_MODULE(DeviceInfoModule, NSObject)
RCT_EXTERN_METHOD(getDeviceInfo:(RCTPromiseResolveBlock)resolve
                  rejecter:(RCTPromiseRejectBlock)reject)
RCT_EXTERN_METHOD(showNativeAlert:(NSString *)title message:(NSString *)message)
@end
```

```javascript
// JavaScript 端调用
import { NativeModules } from 'react-native';
const { DeviceInfoModule } = NativeModules;

const info = await DeviceInfoModule.getDeviceInfo();
console.log(info.model);

DeviceInfoModule.showNativeAlert('提示', '来自 RN 的消息');
```

## 4. Native 事件发送

```swift
@objc(EventEmitterModule)
class EventEmitterModule: RCTEventEmitter {
    override func supportedEvents() -> [String]! {
        return ["onLocationUpdate", "onNetworkChange"]
    }

    override static func requiresMainQueueSetup() -> Bool { return true }

    func sendLocationUpdate(lat: Double, lng: Double) {
        sendEvent(withName: "onLocationUpdate", body: ["lat": lat, "lng": lng])
    }
}
```

```javascript
// JavaScript 端监听
import { NativeEventEmitter, NativeModules } from 'react-native';

const emitter = new NativeEventEmitter(NativeModules.EventEmitterModule);
const subscription = emitter.addListener('onLocationUpdate', (event) => {
  console.log(`位置: ${event.lat}, ${event.lng}`);
});

// 清理
subscription.remove();
```

## 5. Turbo Module（新架构）

```swift
// 新架构使用 Turbo Module 替代 Bridge Module
// 优势：JSI 直接调用，无需序列化，性能更好

@objc(NativeDeviceInfo)
class NativeDeviceInfo: NSObject {
    @objc func getModel() -> String {
        return UIDevice.current.model
    }

    @objc func getSystemVersion() -> String {
        return UIDevice.current.systemVersion
    }
}
```
