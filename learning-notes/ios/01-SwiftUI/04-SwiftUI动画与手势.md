# SwiftUI 动画与手势
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. 基础动画

```swift
struct AnimationDemo: View {
    @State private var isExpanded = false

    var body: some View {
        VStack {
            RoundedRectangle(cornerRadius: 12)
                .fill(.blue)
                .frame(width: isExpanded ? 300 : 100, height: isExpanded ? 300 : 100)
                .animation(.spring(response: 0.5, dampingFraction: 0.6), value: isExpanded)

            Button("切换") {
                isExpanded.toggle()
            }

            // 显式动画
            Button("显式动画") {
                withAnimation(.easeInOut(duration: 0.5)) {
                    isExpanded.toggle()
                }
            }
        }
    }
}
```

## 2. 过渡动画

```swift
struct TransitionDemo: View {
    @State private var showDetail = false

    var body: some View {
        VStack {
            if showDetail {
                DetailView()
                    .transition(.asymmetric(
                        insertion: .slide.combined(with: .opacity),
                        removal: .scale.combined(with: .opacity)
                    ))
            }
            Button("切换") {
                withAnimation { showDetail.toggle() }
            }
        }
    }
}
```

## 3. 手势

```swift
struct GestureDemo: View {
    @State private var offset = CGSize.zero
    @State private var scale: CGFloat = 1.0
    @GestureState private var dragOffset = CGSize.zero

    var body: some View {
        Image("photo")
            .resizable()
            .scaledToFit()
            .scaleEffect(scale)
            .offset(x: offset.width + dragOffset.width,
                    y: offset.height + dragOffset.height)
            // 拖拽手势
            .gesture(
                DragGesture()
                    .updating($dragOffset) { value, state, _ in
                        state = value.translation
                    }
                    .onEnded { value in
                        offset.width += value.translation.width
                        offset.height += value.translation.height
                    }
            )
            // 缩放手势
            .gesture(
                MagnificationGesture()
                    .onChanged { value in scale = value }
            )
            // 双击重置
            .onTapGesture(count: 2) {
                withAnimation {
                    scale = 1.0
                    offset = .zero
                }
            }
    }
}
```

## 4. matchedGeometryEffect

```swift
struct HeroAnimation: View {
    @Namespace private var animation
    @State private var isExpanded = false

    var body: some View {
        if isExpanded {
            DetailCard(namespace: animation)
                .onTapGesture { withAnimation(.spring()) { isExpanded = false } }
        } else {
            ThumbnailCard(namespace: animation)
                .onTapGesture { withAnimation(.spring()) { isExpanded = true } }
        }
    }
}
```
