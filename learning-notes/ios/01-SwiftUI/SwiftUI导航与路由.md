# SwiftUI 导航与路由

> Author: Walter Wang

## 1. NavigationStack（iOS 16+）

```swift
struct ContentView: View {
    @State private var path = NavigationPath()

    var body: some View {
        NavigationStack(path: $path) {
            List(users) { user in
                NavigationLink(value: user) {
                    Text(user.name)
                }
            }
            .navigationTitle("用户列表")
            .navigationDestination(for: User.self) { user in
                UserDetailView(user: user)
            }
        }
    }

    // 编程式导航
    func navigateToUser(_ user: User) {
        path.append(user)
    }

    func popToRoot() {
        path = NavigationPath()
    }
}
```

## 2. Sheet / FullScreenCover

```swift
struct ContentView: View {
    @State private var showSheet = false
    @State private var showFullScreen = false

    var body: some View {
        VStack {
            Button("打开 Sheet") { showSheet = true }
            Button("全屏弹窗") { showFullScreen = true }
        }
        .sheet(isPresented: $showSheet) {
            SettingsView()
                .presentationDetents([.medium, .large])  // 半屏
        }
        .fullScreenCover(isPresented: $showFullScreen) {
            LoginView()
        }
    }
}
```

## 3. TabView

```swift
struct MainTabView: View {
    @State private var selectedTab = 0

    var body: some View {
        TabView(selection: $selectedTab) {
            HomeView()
                .tabItem { Label("首页", systemImage: "house") }
                .tag(0)
            SearchView()
                .tabItem { Label("搜索", systemImage: "magnifyingglass") }
                .tag(1)
            ProfileView()
                .tabItem { Label("我的", systemImage: "person") }
                .tag(2)
        }
    }
}
```

## 4. 路由管理

```swift
// 集中式路由管理
enum Route: Hashable {
    case userDetail(User)
    case settings
    case editProfile
}

class Router: ObservableObject {
    @Published var path = NavigationPath()

    func navigate(to route: Route) { path.append(route) }
    func pop() { path.removeLast() }
    func popToRoot() { path = NavigationPath() }
}
```
