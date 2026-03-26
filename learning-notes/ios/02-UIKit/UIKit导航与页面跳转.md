# UIKit 导航与页面跳转

## 1. UINavigationController

```swift
// AppDelegate / SceneDelegate 中设置
let rootVC = HomeViewController()
let nav = UINavigationController(rootViewController: rootVC)
window?.rootViewController = nav

// Push / Pop
navigationController?.pushViewController(detailVC, animated: true)
navigationController?.popViewController(animated: true)
navigationController?.popToRootViewController(animated: true)

// 自定义导航栏
navigationItem.title = "首页"
navigationItem.rightBarButtonItem = UIBarButtonItem(
    image: UIImage(systemName: "plus"),
    style: .plain,
    target: self,
    action: #selector(addTapped)
)

// 大标题
navigationController?.navigationBar.prefersLargeTitles = true
navigationItem.largeTitleDisplayMode = .always
```

## 2. UITabBarController

```swift
class MainTabBarController: UITabBarController {
    override func viewDidLoad() {
        super.viewDidLoad()

        let homeNav = UINavigationController(rootViewController: HomeVC())
        homeNav.tabBarItem = UITabBarItem(title: "首页", image: UIImage(systemName: "house"), tag: 0)

        let profileNav = UINavigationController(rootViewController: ProfileVC())
        profileNav.tabBarItem = UITabBarItem(title: "我的", image: UIImage(systemName: "person"), tag: 1)

        viewControllers = [homeNav, profileNav]
        tabBar.tintColor = .systemBlue
    }
}
```

## 3. Present / Dismiss

```swift
// 模态弹出
let settingsVC = SettingsViewController()
settingsVC.modalPresentationStyle = .pageSheet  // .fullScreen, .formSheet
settingsVC.modalTransitionStyle = .coverVertical
present(settingsVC, animated: true)

// 关闭
dismiss(animated: true)

// Sheet 半屏（iOS 15+）
if let sheet = settingsVC.sheetPresentationController {
    sheet.detents = [.medium(), .large()]
    sheet.prefersGrabberVisible = true
}
present(settingsVC, animated: true)
```

## 4. 页面传值

```swift
// 正向传值：属性赋值
let detailVC = DetailViewController()
detailVC.userId = selectedUser.id
navigationController?.pushViewController(detailVC, animated: true)

// 反向传值：Delegate
protocol DetailDelegate: AnyObject {
    func detailDidUpdate(_ data: String)
}

class DetailViewController: UIViewController {
    weak var delegate: DetailDelegate?

    func save() {
        delegate?.detailDidUpdate("新数据")
        navigationController?.popViewController(animated: true)
    }
}

// 反向传值：闭包
class DetailViewController: UIViewController {
    var onComplete: ((String) -> Void)?

    func save() {
        onComplete?("新数据")
        dismiss(animated: true)
    }
}
```

## 5. Coordinator 模式

```swift
protocol Coordinator: AnyObject {
    var childCoordinators: [Coordinator] { get set }
    var navigationController: UINavigationController { get set }
    func start()
}

class AppCoordinator: Coordinator {
    var childCoordinators: [Coordinator] = []
    var navigationController: UINavigationController

    init(navigationController: UINavigationController) {
        self.navigationController = navigationController
    }

    func start() {
        let homeVC = HomeViewController()
        homeVC.coordinator = self
        navigationController.pushViewController(homeVC, animated: false)
    }

    func showDetail(for user: User) {
        let detailVC = DetailViewController()
        detailVC.user = user
        navigationController.pushViewController(detailVC, animated: true)
    }

    func showLogin() {
        let loginCoordinator = LoginCoordinator(navigationController: navigationController)
        childCoordinators.append(loginCoordinator)
        loginCoordinator.start()
    }
}
```
