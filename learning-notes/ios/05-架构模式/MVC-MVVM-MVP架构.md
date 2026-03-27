# MVC / MVVM / MVP 架构

> Author: Walter Wang

## 1. MVC（Apple 默认）

```swift
// Controller 承担过多职责（Massive View Controller 问题）
class UserListViewController: UIViewController {
    private let tableView = UITableView()
    private var users: [User] = []

    override func viewDidLoad() {
        super.viewDidLoad()
        // 网络请求、数据解析、UI 配置、事件处理全在 Controller
        fetchUsers()
    }

    func fetchUsers() {
        URLSession.shared.dataTask(with: url) { data, _, _ in
            self.users = try! JSONDecoder().decode([User].self, from: data!)
            DispatchQueue.main.async { self.tableView.reloadData() }
        }.resume()
    }
}
```

## 2. MVVM 架构

```swift
// Model
struct User: Codable, Identifiable {
    let id: Int
    let name: String
    let email: String
}

// ViewModel
class UserListViewModel: ObservableObject {
    @Published var users: [User] = []
    @Published var isLoading = false
    @Published var errorMessage: String?

    private let repository: UserRepository

    init(repository: UserRepository = UserRepository()) {
        self.repository = repository
    }

    @MainActor
    func fetchUsers() async {
        isLoading = true
        defer { isLoading = false }
        do {
            users = try await repository.getUsers()
        } catch {
            errorMessage = error.localizedDescription
        }
    }
}

// View (SwiftUI)
struct UserListView: View {
    @StateObject private var viewModel = UserListViewModel()

    var body: some View {
        List(viewModel.users) { user in
            Text(user.name)
        }
        .overlay { if viewModel.isLoading { ProgressView() } }
        .task { await viewModel.fetchUsers() }
    }
}
```

## 3. MVVM + UIKit（Combine 绑定）

```swift
class UserListViewController: UIViewController {
    private let viewModel = UserListViewModel()
    private var cancellables = Set<AnyCancellable>()

    override func viewDidLoad() {
        super.viewDidLoad()
        bindViewModel()
        Task { await viewModel.fetchUsers() }
    }

    private func bindViewModel() {
        viewModel.$users
            .receive(on: DispatchQueue.main)
            .sink { [weak self] _ in self?.tableView.reloadData() }
            .store(in: &cancellables)

        viewModel.$isLoading
            .receive(on: DispatchQueue.main)
            .sink { [weak self] loading in
                loading ? self?.spinner.startAnimating() : self?.spinner.stopAnimating()
            }
            .store(in: &cancellables)
    }
}
```

## 4. MVP 架构

```swift
// Presenter 协议
protocol UserListPresenter {
    func viewDidLoad()
    func didSelectUser(at index: Int)
}

// View 协议
protocol UserListViewProtocol: AnyObject {
    func showUsers(_ users: [User])
    func showLoading()
    func hideLoading()
    func showError(_ message: String)
}

// Presenter 实现
class UserListPresenterImpl: UserListPresenter {
    weak var view: UserListViewProtocol?
    private let repository: UserRepository

    init(view: UserListViewProtocol, repository: UserRepository) {
        self.view = view
        self.repository = repository
    }

    func viewDidLoad() {
        view?.showLoading()
        Task {
            do {
                let users = try await repository.getUsers()
                await MainActor.run {
                    view?.hideLoading()
                    view?.showUsers(users)
                }
            } catch {
                await MainActor.run { view?.showError(error.localizedDescription) }
            }
        }
    }

    func didSelectUser(at index: Int) { /* 导航逻辑 */ }
}
```

## 5. VIPER 概览

```swift
// VIPER 五层：View - Interactor - Presenter - Entity - Router
// View: 显示 UI
// Interactor: 业务逻辑
// Presenter: 连接 View 和 Interactor
// Entity: 数据模型
// Router: 页面跳转

protocol UserRouterProtocol {
    func navigateToDetail(user: User)
}

protocol UserInteractorProtocol {
    func fetchUsers() async throws -> [User]
}
```
