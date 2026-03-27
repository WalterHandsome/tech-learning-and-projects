# CocoaPods / SPM / Carthage
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. CocoaPods

```ruby
# Podfile
platform :ios, '16.0'
use_frameworks!

target 'MyApp' do
  pod 'Alamofire', '~> 5.8'
  pod 'SnapKit', '~> 5.6'
  pod 'Kingfisher', '~> 7.0'
  pod 'SwiftLint'

  target 'MyAppTests' do
    inherit! :search_paths
    pod 'Quick'
    pod 'Nimble'
  end
end

post_install do |installer|
  installer.pods_project.targets.each do |target|
    target.build_configurations.each do |config|
      config.build_settings['IPHONEOS_DEPLOYMENT_TARGET'] = '16.0'
    end
  end
end
```

```bash
# 常用命令
pod init              # 创建 Podfile
pod install           # 安装依赖
pod update            # 更新依赖
pod update Alamofire  # 更新指定库
pod outdated          # 查看可更新的库
pod deintegrate       # 移除 CocoaPods
```

## 2. Swift Package Manager (SPM)

```swift
// Package.swift（本地包）
// swift-tools-version: 5.9
import PackageDescription

let package = Package(
    name: "MyLibrary",
    platforms: [.iOS(.v16)],
    products: [
        .library(name: "MyLibrary", targets: ["MyLibrary"]),
    ],
    dependencies: [
        .package(url: "https://github.com/Alamofire/Alamofire.git", from: "5.8.0"),
        .package(url: "https://github.com/SnapKit/SnapKit.git", from: "5.6.0"),
    ],
    targets: [
        .target(
            name: "MyLibrary",
            dependencies: ["Alamofire", "SnapKit"]
        ),
        .testTarget(
            name: "MyLibraryTests",
            dependencies: ["MyLibrary"]
        ),
    ]
)
```

```swift
// Xcode 中添加 SPM 依赖：
// File → Add Package Dependencies → 输入 GitHub URL
// 选择版本规则：Up to Next Major / Exact Version / Branch

// 代码中使用
import Alamofire
import SnapKit
```

## 3. Carthage

```
# Cartfile
github "Alamofire/Alamofire" ~> 5.8
github "SnapKit/SnapKit" ~> 5.6
github "onevcat/Kingfisher" ~> 7.0
```

```bash
# 构建
carthage update --platform iOS --use-xcframeworks

# 生成的 .xcframework 在 Carthage/Build/ 目录
# 手动拖入 Xcode → Target → Frameworks, Libraries
```

## 4. 三者对比

```
特性            CocoaPods       SPM             Carthage
─────────────────────────────────────────────────────────
集成方式        修改项目结构     Xcode 原生       手动链接
配置文件        Podfile         Package.swift    Cartfile
中心化          是（Specs仓库） 去中心化          去中心化
编译方式        源码/预编译      源码编译          预编译 framework
二进制缓存      支持            Xcode 15+        天然支持
学习成本        低              低               中
推荐场景        老项目兼容       新项目首选        需要预编译
```

## 5. SPM 本地包开发

```swift
// 项目中创建本地包用于模块化
// File → New → Package

// 主项目引用本地包
// 将包文件夹拖入 Xcode 项目
// Target → General → Frameworks → 添加本地包

// 本地包之间的依赖
.target(
    name: "Feature",
    dependencies: [
        .product(name: "Core", package: "CoreModule"),
    ]
)
```
