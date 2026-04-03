# SwiftUI 基础与布局
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. 基础组件

```swift
import SwiftUI

struct ContentView: View {
    var body: some View {
        VStack(spacing: 16) {
            // 文本
            Text("Hello, SwiftUI")
                .font(.title)
                .fontWeight(.bold)
                .foregroundColor(.primary)

            // 图片
            Image(systemName: "star.fill")
                .resizable()
                .frame(width: 50, height: 50)
                .foregroundColor(.yellow)

            // 按钮
            Button("点击我") {
                print("按钮被点击")
            }
            .buttonStyle(.borderedProminent)

            // 输入框
            TextField("请输入", text: $inputText)
                .textFieldStyle(.roundedBorder)
                .padding(.horizontal)

            // 开关
            Toggle("启用通知", isOn: $isEnabled)
                .padding(.horizontal)
        }
        .padding()
    }
}
```

## 2. 布局

```swift
// HStack（水平排列）
HStack(alignment: .center, spacing: 12) {
    Image(systemName: "person.circle")
    VStack(alignment: .leading) {
        Text("张三").font(.headline)
        Text("iOS Developer").font(.subheadline).foregroundColor(.gray)
    }
    Spacer()
    Text("在线").foregroundColor(.green)
}

// VStack（垂直排列）
VStack(alignment: .leading, spacing: 8) {
    Text("标题").font(.title)
    Text("描述内容").font(.body)
}

// ZStack（层叠）
ZStack {
    Color.blue.ignoresSafeArea()
    VStack {
        Text("覆盖在蓝色背景上").foregroundColor(.white)
    }
}

// LazyVGrid / LazyHGrid
let columns = [GridItem(.adaptive(minimum: 150))]
LazyVGrid(columns: columns, spacing: 16) {
    ForEach(items) { item in
        CardView(item: item)
    }
}
```

## 3. 列表

```swift
// List
List {
    Section("水果") {
        ForEach(fruits, id: \.self) { fruit in
            Text(fruit)
        }
        .onDelete { indexSet in
            fruits.remove(atOffsets: indexSet)
        }
    }
}
.listStyle(.insetGrouped)

// LazyVStack（自定义列表，性能好）
ScrollView {
    LazyVStack(spacing: 12) {
        ForEach(items) { item in
            ItemRow(item: item)
        }
    }
    .padding()
}
```

## 4. 修饰符

```swift
Text("Hello")
    .font(.title)
    .foregroundColor(.blue)
    .padding()
    .background(Color.yellow)
    .cornerRadius(8)
    .shadow(radius: 4)
    .frame(maxWidth: .infinity, alignment: .leading)

// 自定义修饰符
struct CardModifier: ViewModifier {
    func body(content: Content) -> some View {
        content
            .padding()
            .background(Color.white)
            .cornerRadius(12)
            .shadow(color: .gray.opacity(0.2), radius: 8, x: 0, y: 2)
    }
}

extension View {
    func cardStyle() -> some View {
        modifier(CardModifier())
    }
}

// 使用
Text("卡片内容").cardStyle()
```

## 5. GeometryReader

```swift
GeometryReader { geometry in
    HStack(spacing: 0) {
        Color.red
            .frame(width: geometry.size.width * 0.3)
        Color.blue
            .frame(width: geometry.size.width * 0.7)
    }
}
```
## 🎬 推荐视频资源

- [Swiftful Thinking - SwiftUI Bootcamp](https://www.youtube.com/playlist?list=PLwvDm4VfkdphqETTBf-DdjCoAvhai1QpO) — SwiftUI完整入门系列
- [Paul Hudson - SwiftUI Tutorial](https://www.youtube.com/watch?v=aP-SQXTtWhY) — SwiftUI教程
- [Stanford CS193p - SwiftUI](https://www.youtube.com/playlist?list=PLpGHT1n4-mAtTj9oywMWoBx0dCGd51_yG) — 斯坦福SwiftUI课程（免费）
### 📺 B站（Bilibili）
- [SwiftUI中文教程](https://www.bilibili.com/video/BV1s3411g7ab) — SwiftUI入门到实战

### 🎓 斯坦福公开课
- [Stanford CS193p - SwiftUI](https://cs193p.sites.stanford.edu/) — 斯坦福iOS开发课程（免费，B站有中文字幕版）

### 🌐 其他平台
- [Hacking with Swift - 100 Days of SwiftUI](https://www.hackingwithswift.com/100/swiftui) — 最受欢迎的SwiftUI学习路径
