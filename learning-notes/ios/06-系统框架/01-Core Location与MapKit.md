# Core Location 与 MapKit
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. 请求定位权限

```swift
import CoreLocation

class LocationManager: NSObject, CLLocationManagerDelegate {
    private let manager = CLLocationManager()

    override init() {
        super.init()
        manager.delegate = self
        manager.desiredAccuracy = kCLLocationAccuracyBest
    }

    func requestPermission() {
        manager.requestWhenInUseAuthorization()  // 使用时定位
        // manager.requestAlwaysAuthorization()  // 始终定位
    }

    func startUpdating() {
        manager.startUpdatingLocation()
    }

    // 权限变化回调
    func locationManagerDidChangeAuthorization(_ manager: CLLocationManager) {
        switch manager.authorizationStatus {
        case .authorizedWhenInUse, .authorizedAlways:
            manager.startUpdatingLocation()
        case .denied, .restricted:
            print("定位权限被拒绝")
        case .notDetermined:
            requestPermission()
        @unknown default: break
        }
    }

    // 位置更新
    func locationManager(_ manager: CLLocationManager, didUpdateLocations locations: [CLLocation]) {
        guard let location = locations.last else { return }
        print("纬度: \(location.coordinate.latitude), 经度: \(location.coordinate.longitude)")
    }
}
```

## 2. 地理编码与反地理编码

```swift
let geocoder = CLGeocoder()

// 地址 → 坐标
func geocode(address: String) async throws -> CLLocationCoordinate2D? {
    let placemarks = try await geocoder.geocodeAddressString(address)
    return placemarks.first?.location?.coordinate
}

// 坐标 → 地址
func reverseGeocode(location: CLLocation) async throws -> String? {
    let placemarks = try await geocoder.reverseGeocodeLocation(location)
    guard let placemark = placemarks.first else { return nil }
    return [placemark.locality, placemark.subLocality, placemark.thoroughfare]
        .compactMap { $0 }
        .joined(separator: " ")
}
```

## 3. MKMapView 基础

```swift
import MapKit

class MapViewController: UIViewController {
    private let mapView = MKMapView()

    override func viewDidLoad() {
        super.viewDidLoad()
        view.addSubview(mapView)
        mapView.frame = view.bounds
        mapView.delegate = self

        // 设置区域
        let center = CLLocationCoordinate2D(latitude: 39.9042, longitude: 116.4074)
        let region = MKCoordinateRegion(center: center,
                                         latitudinalMeters: 5000,
                                         longitudinalMeters: 5000)
        mapView.setRegion(region, animated: true)
        mapView.showsUserLocation = true
    }
}
```

## 4. 地图标注

```swift
// 添加标注
let annotation = MKPointAnnotation()
annotation.coordinate = CLLocationCoordinate2D(latitude: 39.9042, longitude: 116.4074)
annotation.title = "天安门"
annotation.subtitle = "北京市中心"
mapView.addAnnotation(annotation)

// 自定义标注视图
extension MapViewController: MKMapViewDelegate {
    func mapView(_ mapView: MKMapView, viewFor annotation: MKAnnotation) -> MKAnnotationView? {
        guard !(annotation is MKUserLocation) else { return nil }
        let identifier = "CustomPin"
        var view = mapView.dequeueReusableAnnotationView(withIdentifier: identifier) as? MKMarkerAnnotationView
        if view == nil {
            view = MKMarkerAnnotationView(annotation: annotation, reuseIdentifier: identifier)
            view?.canShowCallout = true
            view?.markerTintColor = .systemRed
            view?.rightCalloutAccessoryView = UIButton(type: .detailDisclosure)
        }
        view?.annotation = annotation
        return view
    }
}
```

## 5. SwiftUI Map（iOS 17+）

```swift
import SwiftUI
import MapKit

struct MapContentView: View {
    @State private var position: MapCameraPosition = .region(
        MKCoordinateRegion(
            center: CLLocationCoordinate2D(latitude: 39.9042, longitude: 116.4074),
            span: MKCoordinateSpan(latitudeDelta: 0.05, longitudeDelta: 0.05)
        )
    )

    var body: some View {
        Map(position: $position) {
            Marker("天安门", coordinate: CLLocationCoordinate2D(latitude: 39.9042, longitude: 116.4074))
            UserAnnotation()
        }
        .mapControls {
            MapUserLocationButton()
            MapCompass()
            MapScaleView()
        }
    }
}
```
