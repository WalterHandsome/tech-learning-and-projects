# Instruments 性能分析
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. Time Profiler（CPU 分析）

```swift
// 识别耗时操作：Xcode → Product → Profile → Time Profiler
// 常见问题：主线程执行耗时任务

// ❌ 主线程执行耗时操作
func loadData() {
    let data = try! Data(contentsOf: largeFileURL)  // 阻塞主线程
    processData(data)
}

// ✅ 移到后台线程
func loadData() {
    Task.detached {
        let data = try Data(contentsOf: largeFileURL)
        let result = processData(data)
        await MainActor.run { self.updateUI(result) }
    }
}
```

## 2. Allocations（内存分配）

```swift
// 追踪内存分配：查看对象创建和销毁
// 关注 Persistent（持久）对象数量是否持续增长

// ❌ 频繁创建大对象
func renderCells() {
    for item in items {
        let formatter = DateFormatter()  // 每次循环都创建
        cell.dateLabel.text = formatter.string(from: item.date)
    }
}

// ✅ 复用对象
private let dateFormatter: DateFormatter = {
    let f = DateFormatter()
    f.dateFormat = "yyyy-MM-dd"
    return f
}()

func renderCells() {
    for item in items {
        cell.dateLabel.text = dateFormatter.string(from: item.date)
    }
}
```

## 3. Leaks（内存泄漏）

```swift
// Leaks 工具自动检测循环引用

// ❌ 闭包循环引用
class ViewController: UIViewController {
    var timer: Timer?

    override func viewDidLoad() {
        timer = Timer.scheduledTimer(withTimeInterval: 1, repeats: true) { _ in
            self.updateUI()  // 强引用 self → 泄漏
        }
    }
}

// ✅ 使用 [weak self]
timer = Timer.scheduledTimer(withTimeInterval: 1, repeats: true) { [weak self] _ in
    self?.updateUI()
}

// deinit 验证释放
deinit {
    print("\(Self.self) 已释放")
    timer?.invalidate()
}
```

## 4. Energy Log（能耗分析）

```swift
// 高能耗操作：GPS、网络、CPU 密集计算

// ❌ 持续高精度定位
locationManager.desiredAccuracy = kCLLocationAccuracyBest
locationManager.startUpdatingLocation()

// ✅ 按需定位
locationManager.desiredAccuracy = kCLLocationAccuracyHundredMeters
locationManager.requestLocation()  // 单次定位

// ✅ 批量网络请求
func syncData() async {
    // 合并多个小请求为一个批量请求
    let batchRequest = BatchRequest(items: pendingItems)
    try await apiClient.send(batchRequest)
}
```

## 5. Network（网络分析）

```swift
// 使用 Instruments Network 或 Charles 抓包分析

// 优化策略
let config = URLSessionConfiguration.default
config.urlCache = URLCache(memoryCapacity: 50_000_000, diskCapacity: 100_000_000)
config.requestCachePolicy = .returnCacheDataElseLoad

// 使用 ETag / Last-Modified 条件请求
var request = URLRequest(url: url)
request.setValue(cachedETag, forHTTPHeaderField: "If-None-Match")
```

## 6. os_signpost 自定义埋点

```swift
import os.signpost

let log = OSLog(subsystem: "com.app", category: "Performance")

func loadImages() {
    let signpostID = OSSignpostID(log: log)
    os_signpost(.begin, log: log, name: "ImageLoading", signpostID: signpostID)

    // 执行操作...
    downloadAndDecodeImages()

    os_signpost(.end, log: log, name: "ImageLoading", signpostID: signpostID)
}
```
