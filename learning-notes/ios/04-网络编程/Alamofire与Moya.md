# Alamofire 与 Moya

> Author: Walter Wang

## 1. Alamofire 基础请求

```swift
import Alamofire

// GET 请求
AF.request("https://api.example.com/users")
    .validate()
    .responseDecodable(of: [User].self) { response in
        switch response.result {
        case .success(let users):
            print("获取到 \(users.count) 个用户")
        case .failure(let error):
            print("请求失败: \(error)")
        }
    }

// POST 请求
let params: [String: Any] = ["name": "张三", "email": "zhang@example.com"]
AF.request("https://api.example.com/users",
           method: .post,
           parameters: params,
           encoding: JSONEncoding.default,
           headers: ["Authorization": "Bearer \(token)"])
    .validate()
    .responseDecodable(of: User.self) { response in
        // 处理响应
    }
```

## 2. Alamofire async/await

```swift
func fetchUsers() async throws -> [User] {
    let response = await AF.request("https://api.example.com/users")
        .validate()
        .serializingDecodable([User].self)
        .response
    switch response.result {
    case .success(let users): return users
    case .failure(let error): throw error
    }
}
```

## 3. 请求拦截器

```swift
class AuthInterceptor: RequestInterceptor {
    func adapt(_ urlRequest: URLRequest, for session: Session,
               completion: @escaping (Result<URLRequest, Error>) -> Void) {
        var request = urlRequest
        request.setValue("Bearer \(TokenManager.shared.accessToken)", forHTTPHeaderField: "Authorization")
        completion(.success(request))
    }

    func retry(_ request: Request, for session: Session, dueTo error: Error,
               completion: @escaping (RetryResult) -> Void) {
        guard let statusCode = request.response?.statusCode, statusCode == 401 else {
            completion(.doNotRetry)
            return
        }
        // Token 过期，刷新后重试
        TokenManager.shared.refreshToken { success in
            completion(success ? .retry : .doNotRetry)
        }
    }
}

// 使用拦截器
let session = Session(interceptor: AuthInterceptor())
session.request("https://api.example.com/profile")
    .responseDecodable(of: Profile.self) { response in }
```

## 4. Moya TargetType

```swift
import Moya

enum UserAPI {
    case getUsers
    case getUser(id: Int)
    case createUser(name: String, email: String)
    case deleteUser(id: Int)
}

extension UserAPI: TargetType {
    var baseURL: URL { URL(string: "https://api.example.com")! }

    var path: String {
        switch self {
        case .getUsers: return "/users"
        case .getUser(let id): return "/users/\(id)"
        case .createUser: return "/users"
        case .deleteUser(let id): return "/users/\(id)"
        }
    }

    var method: Moya.Method {
        switch self {
        case .getUsers, .getUser: return .get
        case .createUser: return .post
        case .deleteUser: return .delete
        }
    }

    var task: Moya.Task {
        switch self {
        case .createUser(let name, let email):
            return .requestParameters(
                parameters: ["name": name, "email": email],
                encoding: JSONEncoding.default
            )
        default:
            return .requestPlain
        }
    }

    var headers: [String: String]? {
        ["Content-Type": "application/json"]
    }
}
```

## 5. Moya Provider 使用

```swift
let provider = MoyaProvider<UserAPI>()

// 基础调用
provider.request(.getUsers) { result in
    switch result {
    case .success(let response):
        let users = try? JSONDecoder().decode([User].self, from: response.data)
    case .failure(let error):
        print("错误: \(error)")
    }
}

// async/await
func fetchUser(id: Int) async throws -> User {
    return try await withCheckedThrowingContinuation { continuation in
        provider.request(.getUser(id: id)) { result in
            switch result {
            case .success(let response):
                do {
                    let user = try JSONDecoder().decode(User.self, from: response.data)
                    continuation.resume(returning: user)
                } catch { continuation.resume(throwing: error) }
            case .failure(let error):
                continuation.resume(throwing: error)
            }
        }
    }
}
```
