# UIKit 核心组件

## 1. UIView 基础

```swift
// 创建视图
let view = UIView(frame: CGRect(x: 0, y: 0, width: 200, height: 100))
view.backgroundColor = .systemBlue
view.layer.cornerRadius = 12
view.layer.shadowColor = UIColor.black.cgColor
view.layer.shadowOpacity = 0.2
view.layer.shadowOffset = CGSize(width: 0, height: 2)
view.layer.shadowRadius = 4

// 添加子视图
parentView.addSubview(view)
parentView.insertSubview(view, at: 0)
parentView.bringSubviewToFront(view)
view.removeFromSuperview()
```

## 2. UILabel

```swift
let label = UILabel()
label.text = "Hello UIKit"
label.font = .systemFont(ofSize: 16, weight: .bold)
label.textColor = .label
label.textAlignment = .center
label.numberOfLines = 0  // 多行显示
label.lineBreakMode = .byWordWrapping

// 富文本
let attributed = NSMutableAttributedString(string: "加粗和颜色")
attributed.addAttribute(.font, value: UIFont.boldSystemFont(ofSize: 18), range: NSRange(location: 0, length: 2))
attributed.addAttribute(.foregroundColor, value: UIColor.red, range: NSRange(location: 3, length: 2))
label.attributedText = attributed
```

## 3. UIButton

```swift
let button = UIButton(type: .system)
button.setTitle("点击", for: .normal)
button.setTitleColor(.white, for: .normal)
button.backgroundColor = .systemBlue
button.layer.cornerRadius = 8
button.addTarget(self, action: #selector(buttonTapped), for: .touchUpInside)

// iOS 15+ UIButton.Configuration
var config = UIButton.Configuration.filled()
config.title = "确认"
config.image = UIImage(systemName: "checkmark")
config.imagePadding = 8
config.cornerStyle = .medium
let modernButton = UIButton(configuration: config)
```

## 4. UIImageView

```swift
let imageView = UIImageView()
imageView.image = UIImage(named: "photo")
imageView.contentMode = .scaleAspectFill
imageView.clipsToBounds = true
imageView.layer.cornerRadius = 40  // 圆形头像

// SF Symbols
imageView.image = UIImage(systemName: "heart.fill")
imageView.tintColor = .systemRed
```

## 5. UITextField

```swift
let textField = UITextField()
textField.placeholder = "请输入用户名"
textField.borderStyle = .roundedRect
textField.clearButtonMode = .whileEditing
textField.returnKeyType = .done
textField.delegate = self

// UITextFieldDelegate
extension ViewController: UITextFieldDelegate {
    func textFieldShouldReturn(_ textField: UITextField) -> Bool {
        textField.resignFirstResponder()
        return true
    }
    func textField(_ textField: UITextField, shouldChangeCharactersIn range: NSRange,
                   replacementString string: String) -> Bool {
        let maxLength = 20
        let currentText = textField.text ?? ""
        let newLength = currentText.count + string.count - range.length
        return newLength <= maxLength
    }
}
```

## 6. UIScrollView

```swift
let scrollView = UIScrollView()
scrollView.contentSize = CGSize(width: view.bounds.width, height: 2000)
scrollView.showsVerticalScrollIndicator = true
scrollView.isPagingEnabled = false
scrollView.delegate = self

// 分页滚动
scrollView.isPagingEnabled = true
scrollView.contentSize = CGSize(width: view.bounds.width * 3, height: view.bounds.height)

extension ViewController: UIScrollViewDelegate {
    func scrollViewDidScroll(_ scrollView: UIScrollView) {
        let offsetY = scrollView.contentOffset.y
        print("滚动偏移: \(offsetY)")
    }
}
```

## 7. UIStackView

```swift
let stackView = UIStackView(arrangedSubviews: [label, button, imageView])
stackView.axis = .vertical
stackView.spacing = 12
stackView.alignment = .fill
stackView.distribution = .fillEqually

// 动态添加/移除
stackView.addArrangedSubview(newView)
stackView.removeArrangedSubview(oldView)
oldView.removeFromSuperview()

// 嵌套 StackView 构建复杂布局
let row = UIStackView(arrangedSubviews: [icon, titleLabel, Spacer()])
row.axis = .horizontal
row.spacing = 8
```
