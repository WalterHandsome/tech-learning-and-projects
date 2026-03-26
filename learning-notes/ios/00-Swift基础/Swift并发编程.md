# Swift 并发编程

## 1. async/await

```swift
// 异步函数
func fetchUser(id: Int) async throws -> User {
    let url = URL(string: "https://api.example.com/users/\(id)")!
    let (data, response) = try await URLSession.shared.data(from: url)
    guard let httpResponse = response as? HTTPURLResponse,
          httpResponse.statusCode == 200 else {
        throw NetworkError.serverError
    }
    return try JSONDecoder().decode(User.self, from: data)
}

// 调用异步函数
let user = try await fetchUser(id: 1)

// 并发执行
async let user = fetchUser(id: 1)
async let posts = fetchPosts(userId: 1)
let (userData, postsData) = try await (user, posts)
```

## 2. Task 与 TaskGroup

```swift
// Task（创建异步任务）
Task {
    let user = try await fetchUser(id: 1)
    await MainActor.run {
        self.user = user  // 回到主线程更新 UI
    }
}

// Task.detached（不继承上下文）
Task.detached(priority: .background) {
    await processLargeData()
}

// TaskGroup（并发执行多个任务）
let users = try await withThrowingTaskGroup(of: User.self) { group in
    for id in userIds {
        group.addTask { try await fetchUser(id: id) }
    }
    var results: [User] = []
    for try await user in group {
        results.append(user)
    }
    return results
}
```

## 3. Actor

```swift
// Actor（线程安全的引用类型）
actor UserCache {
    private var cache: [Int: User] = [:]

    func getUser(id: Int) -> User? {
        return cache[id]
    }

    func setUser(_ user: User) {
        cache[user.id] = user
    }
}

let cache = UserCache()
await cache.setUser(user)
let cached = await cache.getUser(id: 1)

// @MainActor（主线程执行）
@MainActor
class ViewModel: ObservableObject {
    @Published var users: [User] = []

    func loadUsers() async {
        let users = try? await fetchUsers()
        self.users = users ?? []  // 自动在主线程
    }
}
```

## 4. AsyncSequence

```swift
// 异步序列
for try await line in url.lines {
    print(line)
}

// AsyncStream
let stream = AsyncStream<Int> { continuation in
    for i in 0..<10 {
        continuation.yield(i)
        try? await Task.sleep(nanoseconds: 1_000_000_000)
    }
    continuation.finish()
}

for await value in stream {
    print(value)
}
```

## 5. GCD（Grand Central Dispatch）

```swift
// 主队列
DispatchQueue.main.async {
    // UI 更新
}

// 全局队列
DispatchQueue.global(qos: .userInitiated).async {
    // 后台任务
    DispatchQueue.main.async {
        // 回到主线程
    }
}

// 自定义队列
let queue = DispatchQueue(label: "com.app.processing", qos: .utility)

// DispatchGroup
let group = DispatchGroup()
group.enter()
fetchData { group.leave() }
group.enter()
fetchMore { group.leave() }
group.notify(queue: .main) {
    print("全部完成")
}
```
