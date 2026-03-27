# SwiftUI 与 UIKit 混合开发
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. UIHostingController（SwiftUI → UIKit）

```swift
import SwiftUI

// 在 UIKit 中使用 SwiftUI 视图
class ViewController: UIViewController {
    override func viewDidLoad() {
        super.viewDidLoad()

        let swiftUIView = ProfileView(user: currentUser)
        let hostingController = UIHostingController(rootView: swiftUIView)

        addChild(hostingController)
        view.addSubview(hostingController.view)
        hostingController.view.translatesAutoresizingMaskIntoConstraints = false
        NSLayoutConstraint.activate([
            hostingController.view.topAnchor.constraint(equalTo: view.topAnchor),
            hostingController.view.bottomAnchor.constraint(equalTo: view.bottomAnchor),
            hostingController.view.leadingAnchor.constraint(equalTo: view.leadingAnchor),
            hostingController.view.trailingAnchor.constraint(equalTo: view.trailingAnchor)
        ])
        hostingController.didMove(toParent: self)
    }
}

// Push SwiftUI 页面
func showSwiftUIDetail() {
    let detailView = DetailView(itemId: selectedId)
    let hostingVC = UIHostingController(rootView: detailView)
    navigationController?.pushViewController(hostingVC, animated: true)
}
```


## 2. UIViewRepresentable（UIKit → SwiftUI）

```swift
// 将 UIKit 视图包装为 SwiftUI 视图
struct MapViewWrapper: UIViewRepresentable {
    @Binding var region: MKCoordinateRegion

    func makeUIView(context: Context) -> MKMapView {
        let mapView = MKMapView()
        mapView.delegate = context.coordinator
        return mapView
    }

    func updateUIView(_ mapView: MKMapView, context: Context) {
        mapView.setRegion(region, animated: true)
    }

    func makeCoordinator() -> Coordinator {
        Coordinator(self)
    }

    class Coordinator: NSObject, MKMapViewDelegate {
        var parent: MapViewWrapper
        init(_ parent: MapViewWrapper) { self.parent = parent }

        func mapView(_ mapView: MKMapView, regionDidChangeAnimated animated: Bool) {
            parent.region = mapView.region
        }
    }
}

// 在 SwiftUI 中使用
struct ContentView: View {
    @State private var region = MKCoordinateRegion(
        center: CLLocationCoordinate2D(latitude: 39.9, longitude: 116.4),
        span: MKCoordinateSpan(latitudeDelta: 0.05, longitudeDelta: 0.05)
    )
    var body: some View {
        MapViewWrapper(region: $region)
            .frame(height: 300)
    }
}
```

## 3. UIViewControllerRepresentable

```swift
struct ImagePickerView: UIViewControllerRepresentable {
    @Binding var selectedImage: UIImage?
    @Environment(\.dismiss) var dismiss

    func makeUIViewController(context: Context) -> UIImagePickerController {
        let picker = UIImagePickerController()
        picker.delegate = context.coordinator
        picker.sourceType = .photoLibrary
        return picker
    }

    func updateUIViewController(_ uiViewController: UIImagePickerController, context: Context) {}

    func makeCoordinator() -> Coordinator { Coordinator(self) }

    class Coordinator: NSObject, UIImagePickerControllerDelegate, UINavigationControllerDelegate {
        let parent: ImagePickerView
        init(_ parent: ImagePickerView) { self.parent = parent }

        func imagePickerController(_ picker: UIImagePickerController,
                                   didFinishPickingMediaWithInfo info: [UIImagePickerController.InfoKey: Any]) {
            parent.selectedImage = info[.originalImage] as? UIImage
            parent.dismiss()
        }
    }
}
```

## 4. 数据共享（ObservableObject）

```swift
// 共享数据模型
class SharedViewModel: ObservableObject {
    @Published var count = 0
}

// UIKit 中使用
class CounterVC: UIViewController {
    let viewModel = SharedViewModel()
    private var cancellables = Set<AnyCancellable>()

    func setupBinding() {
        viewModel.$count
            .sink { [weak self] value in self?.label.text = "\(value)" }
            .store(in: &cancellables)
    }

    func showSwiftUIView() {
        let swiftUIView = CounterView(viewModel: viewModel)
        let hostingVC = UIHostingController(rootView: swiftUIView)
        present(hostingVC, animated: true)
    }
}

// SwiftUI 中使用同一个 ViewModel
struct CounterView: View {
    @ObservedObject var viewModel: SharedViewModel
    var body: some View {
        Button("计数: \(viewModel.count)") { viewModel.count += 1 }
    }
}
```
