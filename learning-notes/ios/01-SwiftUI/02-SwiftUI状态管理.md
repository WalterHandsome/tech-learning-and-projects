# SwiftUI 状态管理
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. @State

```swift
// 视图内部的简单状态
struct CounterView: View {
    @State private var count = 0

    var body: some View {
        VStack {
            Text("Count: \(count)")
            Button("+1") { count += 1 }
        }
    }
}
```

## 2. @Binding

```swift
// 父子组件共享状态
struct ParentView: View {
    @State private var isOn = false

    var body: some View {
        ToggleView(isOn: $isOn)  // 传递 Binding
    }
}

struct ToggleView: View {
    @Binding var isOn: Bool

    var body: some View {
        Toggle("开关", isOn: $isOn)
    }
}
```

## 3. @StateObject / @ObservedObject

```swift
// ObservableObject（iOS 13+）
class UserViewModel: ObservableObject {
    @Published var users: [User] = []
    @Published var isLoading = false
    @Published var errorMessage: String?

    func loadUsers() async {
        isLoading = true
        defer { isLoading = false }
        do {
            users = try await UserService.fetchUsers()
        } catch {
            errorMessage = error.localizedDescription
        }
    }
}

// @StateObject（创建并持有，视图重建不会重新创建）
struct UserListView: View {
    @StateObject private var viewModel = UserViewModel()

    var body: some View {
        List(viewModel.users) { user in
            Text(user.name)
        }
        .task { await viewModel.loadUsers() }
    }
}

// @ObservedObject（外部传入，不持有）
struct UserDetailView: View {
    @ObservedObject var viewModel: UserViewModel
    // ...
}
```

## 4. @EnvironmentObject

```swift
// 跨层级共享状态
class AppState: ObservableObject {
    @Published var isLoggedIn = false
    @Published var currentUser: User?
    @Published var theme: Theme = .light
}

// 注入
@main
struct MyApp: App {
    @StateObject private var appState = AppState()

    var body: some Scene {
        WindowGroup {
            ContentView()
                .environmentObject(appState)
        }
    }
}

// 任意子视图中使用
struct ProfileView: View {
    @EnvironmentObject var appState: AppState

    var body: some View {
        if let user = appState.currentUser {
            Text("Hello, \(user.name)")
        }
    }
}
```

## 5. @Observable（iOS 17+）

```swift
import Observation

// 更简洁的状态管理
@Observable
class UserViewModel {
    var users: [User] = []
    var isLoading = false
    var errorMessage: String?

    func loadUsers() async {
        isLoading = true
        defer { isLoading = false }
        do {
            users = try await UserService.fetchUsers()
        } catch {
            errorMessage = error.localizedDescription
        }
    }
}

// 使用（不需要 @StateObject/@ObservedObject）
struct UserListView: View {
    @State private var viewModel = UserViewModel()

    var body: some View {
        List(viewModel.users) { user in
            Text(user.name)
        }
        .task { await viewModel.loadUsers() }
    }
}
```
## 🎬 推荐视频资源

- [Swiftful Thinking - SwiftUI State Management](https://www.youtube.com/watch?v=KD4OAjQJYPc) — SwiftUI状态管理
- [Sean Allen - @State @Binding @ObservedObject](https://www.youtube.com/watch?v=stSB04C4iS4) — 属性包装器详解
