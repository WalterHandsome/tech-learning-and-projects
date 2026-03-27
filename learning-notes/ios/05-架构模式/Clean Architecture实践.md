# Clean Architecture 实践
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. 分层架构概览

```
┌─────────────────────────────┐
│   Presentation Layer        │  ← ViewModel, View, Coordinator
├─────────────────────────────┤
│   Domain Layer              │  ← UseCase, Entity, Repository Protocol
├─────────────────────────────┤
│   Data Layer                │  ← Repository Impl, API, Database
└─────────────────────────────┘
依赖方向：外层 → 内层（Domain 不依赖任何外层）
```

## 2. Domain Layer（核心业务）

```swift
// Entity
struct User {
    let id: Int
    let name: String
    let email: String
}

// Repository 协议（定义在 Domain 层）
protocol UserRepository {
    func getUsers() async throws -> [User]
    func getUser(id: Int) async throws -> User
    func saveUser(_ user: User) async throws
}

// Use Case
class FetchUsersUseCase {
    private let repository: UserRepository

    init(repository: UserRepository) {
        self.repository = repository
    }

    func execute() async throws -> [User] {
        try await repository.getUsers()
    }
}

class GetUserDetailUseCase {
    private let repository: UserRepository

    init(repository: UserRepository) {
        self.repository = repository
    }

    func execute(id: Int) async throws -> User {
        try await repository.getUser(id: id)
    }
}
```

## 3. Data Layer（数据实现）

```swift
// DTO（Data Transfer Object）
struct UserDTO: Codable {
    let id: Int
    let name: String
    let email: String

    func toDomain() -> User {
        User(id: id, name: name, email: email)
    }
}

// Repository 实现
class UserRepositoryImpl: UserRepository {
    private let remoteDataSource: UserRemoteDataSource
    private let localDataSource: UserLocalDataSource

    init(remote: UserRemoteDataSource, local: UserLocalDataSource) {
        self.remoteDataSource = remote
        self.localDataSource = local
    }

    func getUsers() async throws -> [User] {
        do {
            let dtos = try await remoteDataSource.fetchUsers()
            let users = dtos.map { $0.toDomain() }
            try await localDataSource.cacheUsers(dtos)  // 缓存
            return users
        } catch {
            // 网络失败时读取缓存
            let cached = try await localDataSource.getCachedUsers()
            return cached.map { $0.toDomain() }
        }
    }

    func getUser(id: Int) async throws -> User {
        let dto = try await remoteDataSource.fetchUser(id: id)
        return dto.toDomain()
    }

    func saveUser(_ user: User) async throws {
        try await remoteDataSource.createUser(user)
    }
}

// Remote Data Source
class UserRemoteDataSource {
    private let apiClient: APIClient

    init(apiClient: APIClient) { self.apiClient = apiClient }

    func fetchUsers() async throws -> [UserDTO] {
        try await apiClient.request("/users")
    }

    func fetchUser(id: Int) async throws -> UserDTO {
        try await apiClient.request("/users/\(id)")
    }
}
```

## 4. Presentation Layer

```swift
class UserListViewModel: ObservableObject {
    @Published var users: [UserViewData] = []
    @Published var isLoading = false

    private let fetchUsersUseCase: FetchUsersUseCase

    init(fetchUsersUseCase: FetchUsersUseCase) {
        self.fetchUsersUseCase = fetchUsersUseCase
    }

    @MainActor
    func loadUsers() async {
        isLoading = true
        defer { isLoading = false }
        do {
            let domainUsers = try await fetchUsersUseCase.execute()
            users = domainUsers.map { UserViewData(name: $0.name, email: $0.email) }
        } catch {
            // 处理错误
        }
    }
}

// View Data（展示模型）
struct UserViewData: Identifiable {
    let id = UUID()
    let name: String
    let email: String
}
```

## 5. 组装依赖

```swift
class AppDIContainer {
    // Data Layer
    lazy var apiClient = APIClient.shared
    lazy var remoteDataSource = UserRemoteDataSource(apiClient: apiClient)
    lazy var localDataSource = UserLocalDataSource()
    lazy var userRepository: UserRepository = UserRepositoryImpl(
        remote: remoteDataSource, local: localDataSource
    )

    // Domain Layer
    func makeFetchUsersUseCase() -> FetchUsersUseCase {
        FetchUsersUseCase(repository: userRepository)
    }

    // Presentation Layer
    func makeUserListViewModel() -> UserListViewModel {
        UserListViewModel(fetchUsersUseCase: makeFetchUsersUseCase())
    }
}
```
