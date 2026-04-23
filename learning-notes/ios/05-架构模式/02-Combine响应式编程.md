# Combine 响应式编程
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. Publisher 与 Subscriber

```swift
import Combine

// 基础发布者
let publisher = [1, 2, 3, 4, 5].publisher
publisher.sink { completion in
    print("完成: \(completion)")
} receiveValue: { value in
    print("收到: \(value)")
}

// Just: 发送单个值
let just = Just("Hello Combine")
just.sink { print($0) }

// Future: 异步单次结果
let future = Future<String, Error> { promise in
    DispatchQueue.global().asyncAfter(deadline: .now() + 1) {
        promise(.success("异步结果"))
    }
}
```

## 2. 常用操作符

```swift
var cancellables = Set<AnyCancellable>()

// map / filter / compactMap
[1, 2, 3, 4, 5].publisher
    .filter { $0 % 2 == 0 }
    .map { "数字: \($0)" }
    .sink { print($0) }
    .store(in: &cancellables)

// flatMap: 将值转换为新的 Publisher
func fetchUser(id: Int) -> AnyPublisher<User, Error> { /* ... */ }

[1, 2, 3].publisher
    .flatMap { id in fetchUser(id: id) }
    .sink(receiveCompletion: { _ in }, receiveValue: { print($0) })
    .store(in: &cancellables)

// combineLatest: 合并多个流
let name = CurrentValueSubject<String, Never>("张三")
let age = CurrentValueSubject<Int, Never>(25)

name.combineLatest(age)
    .map { "\($0) - \($1)岁" }
    .sink { print($0) }
    .store(in: &cancellables)

// debounce: 防抖（搜索场景）
searchTextField.textPublisher
    .debounce(for: .milliseconds(300), scheduler: RunLoop.main)
    .removeDuplicates()
    .sink { query in search(query) }
    .store(in: &cancellables)
```

## 3. Subject

```swift
// PassthroughSubject: 无初始值
let eventBus = PassthroughSubject<String, Never>()
eventBus.sink { print("事件: \($0)") }.store(in: &cancellables)
eventBus.send("用户登录")
eventBus.send("数据刷新")

// CurrentValueSubject: 有初始值
let counter = CurrentValueSubject<Int, Never>(0)
counter.sink { print("计数: \($0)") }.store(in: &cancellables)
counter.value += 1  // 直接修改
counter.send(10)    // 发送新值
print(counter.value) // 读取当前值
```

## 4. @Published 属性包装器

```swift
class LoginViewModel: ObservableObject {
    @Published var username = ""
    @Published var password = ""
    @Published var isLoginEnabled = false
    @Published var errorMessage: String?

    private var cancellables = Set<AnyCancellable>()

    init() {
        // 组合多个 @Published 属性
        $username.combineLatest($password)
            .map { !$0.isEmpty && $1.count >= 6 }
            .assign(to: &$isLoginEnabled)
    }

    func login() {
        $username
            .combineLatest($password)
            .first()
            .flatMap { [weak self] username, password in
                self?.authService.login(username: username, password: password)
                    ?? Fail(error: AuthError.unknown).eraseToAnyPublisher()
            }
            .sink(
                receiveCompletion: { [weak self] completion in
                    if case .failure(let error) = completion {
                        self?.errorMessage = error.localizedDescription
                    }
                },
                receiveValue: { token in print("登录成功: \(token)") }
            )
            .store(in: &cancellables)
    }
}
```

## 5. Cancellable 生命周期管理

```swift
class MyViewController: UIViewController {
    private var cancellables = Set<AnyCancellable>()

    override func viewDidLoad() {
        super.viewDidLoad()

        // 订阅会在 cancellables 被释放时自动取消
        NotificationCenter.default.publisher(for: UIApplication.didBecomeActiveNotification)
            .sink { _ in print("App 激活") }
            .store(in: &cancellables)
    }

    // 手动取消
    private var singleCancellable: AnyCancellable?

    func startListening() {
        singleCancellable = timer.sink { print($0) }
    }

    func stopListening() {
        singleCancellable?.cancel()
        singleCancellable = nil
    }
}
```

## 6. 错误处理

```swift
URLSession.shared.dataTaskPublisher(for: url)
    .map(\.data)
    .decode(type: [User].self, decoder: JSONDecoder())
    .retry(2)                          // 失败重试2次
    .catch { _ in Just([]) }           // 错误时返回空数组
    .receive(on: DispatchQueue.main)
    .assign(to: &$users)
```

## 7. Combine 在 2026 年的定位

<!-- version-check: Combine framework, Swift 6.2, iOS 26, checked 2026-04-23 -->

> 🔄 更新于 2026-04-23

### Combine vs async/await：何时用哪个

Apple 自 Swift 5.5 引入 async/await 后，Combine 的定位逐渐收窄。2026 年的共识是：

| 场景 | 推荐方案 | 原因 |
|------|---------|------|
| 网络请求 | async/await | 更简洁，错误处理更直观 |
| 单次异步操作 | async/await | Future 过于冗长 |
| 多值流（实时数据） | AsyncSequence 或 Combine | 两者都可，AsyncSequence 更轻量 |
| 搜索防抖 | Combine | `debounce` + `removeDuplicates` 仍是最优雅的方案 |
| UIKit 数据绑定 | Combine | `@Published` + `sink` 是 UIKit 响应式绑定的标准方式 |
| SwiftUI 状态管理 | @Observable | 不再需要 Combine 做 SwiftUI 绑定 |
| 多流合并/转换 | Combine | `combineLatest`、`merge`、`zip` 等操作符仍然强大 |

### 从 Combine 迁移到 async/await

```swift
// 旧方式：Combine 网络请求
func fetchUsersCombine() -> AnyPublisher<[User], Error> {
    URLSession.shared.dataTaskPublisher(for: url)
        .map(\.data)
        .decode(type: [User].self, decoder: JSONDecoder())
        .eraseToAnyPublisher()
}

// 新方式：async/await（推荐）
func fetchUsers() async throws -> [User] {
    let (data, _) = try await URLSession.shared.data(from: url)
    return try JSONDecoder().decode([User].self, from: data)
}

// 旧方式：Combine 搜索防抖
$searchText
    .debounce(for: .milliseconds(300), scheduler: RunLoop.main)
    .removeDuplicates()
    .sink { query in self.search(query) }
    .store(in: &cancellables)

// 新方式：AsyncSequence 搜索防抖（iOS 17+）
// 注意：AsyncSequence 目前没有内置 debounce，
// 搜索防抖场景 Combine 仍然更优雅
```

### 2026 年建议

- **新 SwiftUI 项目**：优先 async/await + @Observable，Combine 仅用于复杂流操作
- **UIKit 项目**：Combine 仍是数据绑定的最佳选择
- **混合项目**：网络层用 async/await，UI 绑定层按框架选择
- Combine 不会被废弃，但 Apple 已停止为其添加新功能

来源：[Swift Forums - Move from Combine to Swift concurrency?](https://forums.swift.org/t/move-from-combine-to-swift-concurrency) | [Swift 6 Concurrency Patterns](https://ignit.group/blog/swift-6-concurrency-advanced-patterns-2-3)
