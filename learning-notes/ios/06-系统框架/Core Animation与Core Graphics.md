# Core Animation 与 Core Graphics

## 1. CALayer 基础

```swift
let layer = CALayer()
layer.frame = CGRect(x: 50, y: 50, width: 200, height: 200)
layer.backgroundColor = UIColor.systemBlue.cgColor
layer.cornerRadius = 20
layer.borderWidth = 2
layer.borderColor = UIColor.white.cgColor
layer.shadowColor = UIColor.black.cgColor
layer.shadowOpacity = 0.3
layer.shadowOffset = CGSize(width: 0, height: 4)
layer.shadowRadius = 8
view.layer.addSublayer(layer)

// 渐变层
let gradientLayer = CAGradientLayer()
gradientLayer.frame = view.bounds
gradientLayer.colors = [UIColor.systemBlue.cgColor, UIColor.systemPurple.cgColor]
gradientLayer.startPoint = CGPoint(x: 0, y: 0)
gradientLayer.endPoint = CGPoint(x: 1, y: 1)
view.layer.insertSublayer(gradientLayer, at: 0)

// 形状层
let shapeLayer = CAShapeLayer()
shapeLayer.path = UIBezierPath(ovalIn: CGRect(x: 0, y: 0, width: 100, height: 100)).cgPath
shapeLayer.fillColor = UIColor.systemRed.cgColor
shapeLayer.strokeColor = UIColor.white.cgColor
shapeLayer.lineWidth = 3
```

## 2. CABasicAnimation

```swift
// 位移动画
let moveAnimation = CABasicAnimation(keyPath: "position.x")
moveAnimation.fromValue = 50
moveAnimation.toValue = 300
moveAnimation.duration = 1.0
moveAnimation.timingFunction = CAMediaTimingFunction(name: .easeInEaseOut)
layer.add(moveAnimation, forKey: "move")

// 缩放动画
let scaleAnimation = CABasicAnimation(keyPath: "transform.scale")
scaleAnimation.fromValue = 1.0
scaleAnimation.toValue = 1.5
scaleAnimation.duration = 0.5
scaleAnimation.autoreverses = true
layer.add(scaleAnimation, forKey: "scale")

// 旋转动画
let rotateAnimation = CABasicAnimation(keyPath: "transform.rotation.z")
rotateAnimation.fromValue = 0
rotateAnimation.toValue = CGFloat.pi * 2
rotateAnimation.duration = 2.0
rotateAnimation.repeatCount = .infinity
layer.add(rotateAnimation, forKey: "rotate")
```

## 3. CAKeyframeAnimation

```swift
// 关键帧路径动画
let pathAnimation = CAKeyframeAnimation(keyPath: "position")
let path = UIBezierPath()
path.move(to: CGPoint(x: 50, y: 300))
path.addCurve(to: CGPoint(x: 300, y: 300),
              controlPoint1: CGPoint(x: 100, y: 100),
              controlPoint2: CGPoint(x: 250, y: 500))
pathAnimation.path = path.cgPath
pathAnimation.duration = 2.0
pathAnimation.timingFunction = CAMediaTimingFunction(name: .easeInEaseOut)
layer.add(pathAnimation, forKey: "pathMove")

// 颜色关键帧
let colorAnimation = CAKeyframeAnimation(keyPath: "backgroundColor")
colorAnimation.values = [UIColor.red.cgColor, UIColor.green.cgColor, UIColor.blue.cgColor]
colorAnimation.keyTimes = [0, 0.5, 1.0]
colorAnimation.duration = 3.0
layer.add(colorAnimation, forKey: "colorChange")
```

## 4. CAAnimationGroup

```swift
let group = CAAnimationGroup()
group.animations = [moveAnimation, scaleAnimation, rotateAnimation]
group.duration = 2.0
group.fillMode = .forwards
group.isRemovedOnCompletion = false
layer.add(group, forKey: "group")
```

## 5. Core Graphics 绘制

```swift
class CustomDrawView: UIView {
    override func draw(_ rect: CGRect) {
        guard let context = UIGraphicsGetCurrentContext() else { return }

        // 矩形
        context.setFillColor(UIColor.systemBlue.cgColor)
        context.fill(CGRect(x: 20, y: 20, width: 100, height: 60))

        // 圆形
        context.setFillColor(UIColor.systemRed.cgColor)
        context.fillEllipse(in: CGRect(x: 150, y: 20, width: 80, height: 80))

        // 线条
        context.setStrokeColor(UIColor.systemGreen.cgColor)
        context.setLineWidth(3)
        context.move(to: CGPoint(x: 20, y: 150))
        context.addLine(to: CGPoint(x: 300, y: 150))
        context.strokePath()
    }
}
```

## 6. UIBezierPath 贝塞尔曲线

```swift
class HeartView: UIView {
    override func draw(_ rect: CGRect) {
        let path = UIBezierPath()
        let center = CGPoint(x: rect.midX, y: rect.midY)

        path.move(to: CGPoint(x: center.x, y: center.y + 30))
        path.addCurve(to: CGPoint(x: center.x, y: center.y - 30),
                      controlPoint1: CGPoint(x: center.x - 60, y: center.y),
                      controlPoint2: CGPoint(x: center.x - 30, y: center.y - 50))
        path.addCurve(to: CGPoint(x: center.x, y: center.y + 30),
                      controlPoint1: CGPoint(x: center.x + 30, y: center.y - 50),
                      controlPoint2: CGPoint(x: center.x + 60, y: center.y))

        UIColor.systemRed.setFill()
        path.fill()
    }
}

// 圆形进度条
class CircularProgressView: UIView {
    var progress: CGFloat = 0.7 {
        didSet { progressLayer.strokeEnd = progress }
    }

    private let progressLayer = CAShapeLayer()

    override func layoutSubviews() {
        super.layoutSubviews()
        let path = UIBezierPath(arcCenter: CGPoint(x: bounds.midX, y: bounds.midY),
                                radius: bounds.width / 2 - 10,
                                startAngle: -.pi / 2,
                                endAngle: .pi * 1.5,
                                clockwise: true)
        progressLayer.path = path.cgPath
        progressLayer.strokeColor = UIColor.systemBlue.cgColor
        progressLayer.fillColor = UIColor.clear.cgColor
        progressLayer.lineWidth = 8
        progressLayer.lineCap = .round
        progressLayer.strokeEnd = progress
        layer.addSublayer(progressLayer)
    }
}
```
