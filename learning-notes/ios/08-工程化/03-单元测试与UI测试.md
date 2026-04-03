# 单元测试与 UI 测试
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. XCTest 基础

```swift
import XCTest
@testable import MyApp

class UserServiceTests: XCTestCase {

    var sut: UserService!  // System Under Test

    override func setUp() {
        super.setUp()
        sut = UserService(repository: MockUserRepository())
    }

    override func tearDown() {
        sut = nil
        super.tearDown()
    }

    func testFetchUsersReturnsNonEmpty() async throws {
        let users = try await sut.fetchUsers()
        XCTAssertFalse(users.isEmpty)
        XCTAssertEqual(users.count, 3)
    }

    func testFetchUserByIdReturnsCorrectUser() async throws {
        let user = try await sut.fetchUser(id: 1)
        XCTAssertEqual(user.name, "张三")
        XCTAssertEqual(user.email, "zhang@example.com")
    }

    func testFetchUserWithInvalidIdThrows() async {
        do {
            _ = try await sut.fetchUser(id: -1)
            XCTFail("应该抛出错误")
        } catch {
            XCTAssertTrue(error is UserError)
        }
    }
}
```

## 2. Mock 对象

```swift
protocol UserRepository {
    func getUsers() async throws -> [User]
    func getUser(id: Int) async throws -> User
}

class MockUserRepository: UserRepository {
    var mockUsers: [User] = [
        User(id: 1, name: "张三", email: "zhang@example.com"),
        User(id: 2, name: "李四", email: "li@example.com"),
        User(id: 3, name: "王五", email: "wang@example.com"),
    ]
    var shouldThrowError = false
    var fetchUsersCallCount = 0

    func getUsers() async throws -> [User] {
        fetchUsersCallCount += 1
        if shouldThrowError { throw UserError.networkError }
        return mockUsers
    }

    func getUser(id: Int) async throws -> User {
        guard let user = mockUsers.first(where: { $0.id == id }) else {
            throw UserError.notFound
        }
        return user
    }
}
```

## 3. ViewModel 测试

```swift
class UserListViewModelTests: XCTestCase {
    var viewModel: UserListViewModel!
    var mockRepo: MockUserRepository!

    override func setUp() {
        mockRepo = MockUserRepository()
        viewModel = UserListViewModel(repository: mockRepo)
    }

    func testLoadUsersSuccess() async {
        await viewModel.loadUsers()
        XCTAssertEqual(viewModel.users.count, 3)
        XCTAssertFalse(viewModel.isLoading)
        XCTAssertNil(viewModel.errorMessage)
    }

    func testLoadUsersFailure() async {
        mockRepo.shouldThrowError = true
        await viewModel.loadUsers()
        XCTAssertTrue(viewModel.users.isEmpty)
        XCTAssertNotNil(viewModel.errorMessage)
    }

    func testLoadUsersCallsRepository() async {
        await viewModel.loadUsers()
        XCTAssertEqual(mockRepo.fetchUsersCallCount, 1)
    }
}
```

## 4. 异步测试

```swift
func testAsyncOperation() async throws {
    let result = try await sut.performAsyncTask()
    XCTAssertEqual(result, expectedValue)
}

// Expectation（回调风格）
func testCallbackOperation() {
    let expectation = expectation(description: "数据加载完成")

    sut.fetchData { result in
        XCTAssertNotNil(result)
        expectation.fulfill()
    }

    waitForExpectations(timeout: 5)
}
```

## 5. XCUITest UI 测试

```swift
class LoginUITests: XCTestCase {
    let app = XCUIApplication()

    override func setUp() {
        continueAfterFailure = false
        app.launchArguments = ["--uitesting"]
        app.launch()
    }

    func testLoginFlow() {
        let emailField = app.textFields["emailTextField"]
        emailField.tap()
        emailField.typeText("test@example.com")

        let passwordField = app.secureTextFields["passwordTextField"]
        passwordField.tap()
        passwordField.typeText("password123")

        app.buttons["loginButton"].tap()

        // 等待首页出现
        let homeTitle = app.staticTexts["首页"]
        XCTAssertTrue(homeTitle.waitForExistence(timeout: 5))
    }

    func testEmptyFieldShowsError() {
        app.buttons["loginButton"].tap()
        let errorLabel = app.staticTexts["请输入邮箱"]
        XCTAssertTrue(errorLabel.exists)
    }
}
```

## 6. 测试覆盖率

```swift
// Xcode → Product → Scheme → Edit Scheme → Test → Code Coverage ✓
// 运行测试后：Xcode → Report Navigator → 查看覆盖率

// 设置覆盖率目标
// 核心业务逻辑 > 80%
// ViewModel > 90%
// 工具类 > 95%
```
