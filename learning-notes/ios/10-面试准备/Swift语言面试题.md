# Swift 语言面试题

> Author: Walter Wang

## 1. 值类型 vs 引用类型

```swift
// 值类型：struct, enum, tuple（复制语义）
struct Point {
    var x: Int
    var y: Int
}
var a = Point(x: 1, y: 2)
var b = a       // 复制
b.x = 10
print(a.x)     // 1（不受影响）

// 引用类型：class（共享语义）
class Person {
    var name: String
    init(name: String) { self.name = name }
}
let p1 = Person(name: "张三")
let p2 = p1     // 共享同一实例
p2.name = "李四"
print(p1.name)  // "李四"（被修改）

// 选择原则：
// - 优先使用 struct（线程安全、性能好）
// - 需要继承、共享状态、deinit 时用 class
// - Swift 标准库大量使用 struct：String, Array, Dictionary
```

## 2. Optional 原理

```swift
// Optional 本质是枚举
enum Optional<Wrapped> {
    case none
    case some(Wrapped)
}

// 解包方式对比
var name: String? = "Swift"

// 1. if let（安全）
if let name = name { print(name) }

// 2. guard let（提前退出）
guard let name = name else { return }

// 3. ?? 空合运算符
let display = name ?? "默认值"

// 4. 可选链
let count = name?.count  // Int?

// 5. 强制解包（危险）
let forced = name!  // nil 时崩溃

// 6. Swift 5.7 简写
if let name { print(name) }  // 等同于 if let name = name
```

## 3. 闭包与捕获

```swift
// 闭包捕获值（引用捕获）
func makeCounter() -> () -> Int {
    var count = 0
    return {
        count += 1  // 捕获 count 的引用
        return count
    }
}
let counter = makeCounter()
counter()  // 1
counter()  // 2

// 捕获列表（值捕获）
var value = 10
let closure = { [value] in print(value) }
value = 20
closure()  // 10（捕获时的值）

// 逃逸闭包 vs 非逃逸闭包
func doWork(completion: @escaping () -> Void) {
    DispatchQueue.global().async { completion() }  // 逃逸：闭包在函数返回后执行
}
func doSync(action: () -> Void) {
    action()  // 非逃逸：闭包在函数返回前执行（默认）
}
```

## 4. ARC 与内存管理

```swift
// strong（默认）：增加引用计数
// weak：不增加引用计数，对象释放后自动置 nil（必须是 Optional）
// unowned：不增加引用计数，对象释放后不置 nil（访问会崩溃）

class Owner {
    var pet: Pet?
    deinit { print("Owner 释放") }
}
class Pet {
    weak var owner: Owner?  // weak 打破循环引用
    deinit { print("Pet 释放") }
}

// 闭包中的循环引用
class ViewModel {
    var name = "test"
    var onUpdate: (() -> Void)?

    func setup() {
        // ❌ 循环引用：self → onUpdate → self
        onUpdate = { print(self.name) }

        // ✅ weak self
        onUpdate = { [weak self] in print(self?.name ?? "") }

        // ✅ unowned self（确定 self 不会先释放时）
        onUpdate = { [unowned self] in print(self.name) }
    }
}
```

## 5. async/await 与 Actor

```swift
// async/await
func fetchUser() async throws -> User {
    let (data, _) = try await URLSession.shared.data(from: url)
    return try JSONDecoder().decode(User.self, from: data)
}

// 并发执行
async let users = fetchUsers()
async let posts = fetchPosts()
let (u, p) = try await (users, posts)  // 并行请求

// TaskGroup
let results = try await withThrowingTaskGroup(of: User.self) { group in
    for id in ids {
        group.addTask { try await fetchUser(id: id) }
    }
    var users: [User] = []
    for try await user in group { users.append(user) }
    return users
}

// Actor（线程安全）
actor BankAccount {
    private var balance: Double = 0

    func deposit(_ amount: Double) { balance += amount }
    func getBalance() -> Double { balance }
}

let account = BankAccount()
await account.deposit(100)  // 必须 await
```

## 6. 协议与泛型

```swift
// 协议关联类型
protocol Repository {
    associatedtype Item
    func getAll() async throws -> [Item]
    func save(_ item: Item) async throws
}

// 泛型约束
func findFirst<T: Collection>(in collection: T, where predicate: (T.Element) -> Bool) -> T.Element? {
    collection.first(where: predicate)
}

// some vs any
func makeView() -> some View { Text("Hello") }  // 不透明类型（编译时确定）
func getRepository() -> any Repository { RemoteRepo() }  // 存在类型（运行时多态）
```
