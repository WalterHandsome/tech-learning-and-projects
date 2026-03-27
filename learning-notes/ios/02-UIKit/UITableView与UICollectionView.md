# UITableView 与 UICollectionView

> Author: Walter Wang

## 1. UITableView 基础

```swift
class UserListVC: UIViewController, UITableViewDataSource, UITableViewDelegate {
    private let tableView = UITableView(frame: .zero, style: .insetGrouped)
    private var users: [User] = []

    override func viewDidLoad() {
        super.viewDidLoad()
        tableView.dataSource = self
        tableView.delegate = self
        tableView.register(UserCell.self, forCellReuseIdentifier: "UserCell")
        view.addSubview(tableView)
    }

    func tableView(_ tableView: UITableView, numberOfRowsInSection section: Int) -> Int {
        users.count
    }

    func tableView(_ tableView: UITableView, cellForRowAt indexPath: IndexPath) -> UITableViewCell {
        let cell = tableView.dequeueReusableCell(withIdentifier: "UserCell", for: indexPath) as! UserCell
        cell.configure(with: users[indexPath.row])
        return cell
    }

    func tableView(_ tableView: UITableView, didSelectRowAt indexPath: IndexPath) {
        tableView.deselectRow(at: indexPath, animated: true)
        let detail = UserDetailVC(user: users[indexPath.row])
        navigationController?.pushViewController(detail, animated: true)
    }
}
```

## 2. 自定义 Cell

```swift
class UserCell: UITableViewCell {
    private let avatarView = UIImageView()
    private let nameLabel = UILabel()

    override init(style: UITableViewCell.CellStyle, reuseIdentifier: String?) {
        super.init(style: style, reuseIdentifier: reuseIdentifier)
        setupUI()
    }
    required init?(coder: NSCoder) { fatalError() }

    private func setupUI() {
        [avatarView, nameLabel].forEach {
            $0.translatesAutoresizingMaskIntoConstraints = false
            contentView.addSubview($0)
        }
        NSLayoutConstraint.activate([
            avatarView.leadingAnchor.constraint(equalTo: contentView.leadingAnchor, constant: 16),
            avatarView.centerYAnchor.constraint(equalTo: contentView.centerYAnchor),
            avatarView.widthAnchor.constraint(equalToConstant: 44),
            avatarView.heightAnchor.constraint(equalToConstant: 44),
            nameLabel.leadingAnchor.constraint(equalTo: avatarView.trailingAnchor, constant: 12),
            nameLabel.centerYAnchor.constraint(equalTo: contentView.centerYAnchor)
        ])
    }

    func configure(with user: User) {
        nameLabel.text = user.name
        avatarView.image = UIImage(named: user.avatar)
    }
}
```

## 3. DiffableDataSource（iOS 13+）

```swift
enum Section { case main }

class DiffableVC: UIViewController {
    var dataSource: UITableViewDiffableDataSource<Section, User>!

    func configureDataSource() {
        dataSource = UITableViewDiffableDataSource(tableView: tableView) { tableView, indexPath, user in
            let cell = tableView.dequeueReusableCell(withIdentifier: "UserCell", for: indexPath)
            cell.textLabel?.text = user.name
            return cell
        }
    }

    func updateList(with users: [User], animated: Bool = true) {
        var snapshot = NSDiffableDataSourceSnapshot<Section, User>()
        snapshot.appendSections([.main])
        snapshot.appendItems(users)
        dataSource.apply(snapshot, animatingDifferences: animated)
    }
}
```

## 4. UICollectionView FlowLayout

```swift
let layout = UICollectionViewFlowLayout()
layout.itemSize = CGSize(width: 170, height: 200)
layout.minimumInteritemSpacing = 12
layout.minimumLineSpacing = 12
layout.sectionInset = UIEdgeInsets(top: 16, left: 16, bottom: 16, right: 16)

let collectionView = UICollectionView(frame: .zero, collectionViewLayout: layout)
collectionView.register(PhotoCell.self, forCellWithReuseIdentifier: "PhotoCell")
```

## 5. Compositional Layout（iOS 13+）

```swift
func createLayout() -> UICollectionViewCompositionalLayout {
    // Item
    let itemSize = NSCollectionLayoutSize(widthDimension: .fractionalWidth(0.5),
                                          heightDimension: .fractionalHeight(1.0))
    let item = NSCollectionLayoutItem(layoutSize: itemSize)
    item.contentInsets = NSDirectionalEdgeInsets(top: 4, leading: 4, bottom: 4, trailing: 4)

    // Group
    let groupSize = NSCollectionLayoutSize(widthDimension: .fractionalWidth(1.0),
                                           heightDimension: .absolute(200))
    let group = NSCollectionLayoutGroup.horizontal(layoutSize: groupSize, subitems: [item])

    // Section
    let section = NSCollectionLayoutSection(group: group)
    section.orthogonalScrollingBehavior = .continuous  // 横向滚动

    return UICollectionViewCompositionalLayout(section: section)
}
```
