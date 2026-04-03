# Xcode 项目配置与构建
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. Build Settings 关键配置

```
// 常用 Build Settings
PRODUCT_BUNDLE_IDENTIFIER = com.company.app
SWIFT_VERSION = 5.9
IPHONEOS_DEPLOYMENT_TARGET = 16.0
TARGETED_DEVICE_FAMILY = 1,2  // 1=iPhone, 2=iPad

// 优化级别
// Debug:   SWIFT_OPTIMIZATION_LEVEL = -Onone（无优化，方便调试）
// Release: SWIFT_OPTIMIZATION_LEVEL = -O（速度优先）
//          或 -Osize（体积优先）

// 代码签名
CODE_SIGN_STYLE = Automatic
DEVELOPMENT_TEAM = XXXXXXXXXX
```

## 2. xcconfig 配置文件

```
// Base.xcconfig
PRODUCT_NAME = MyApp
SWIFT_VERSION = 5.9
IPHONEOS_DEPLOYMENT_TARGET = 16.0

// Debug.xcconfig
#include "Base.xcconfig"
API_BASE_URL = https:\/\/dev-api.example.com
SWIFT_ACTIVE_COMPILATION_CONDITIONS = DEBUG
GCC_OPTIMIZATION_LEVEL = 0

// Release.xcconfig
#include "Base.xcconfig"
API_BASE_URL = https:\/\/api.example.com
SWIFT_ACTIVE_COMPILATION_CONDITIONS = RELEASE
ENABLE_TESTABILITY = NO
```

## 3. 多环境配置

```swift
// Info.plist 中引用 xcconfig 变量
// API_BASE_URL = $(API_BASE_URL)

// 代码中读取
enum Environment {
    static var apiBaseURL: String {
        Bundle.main.infoDictionary?["API_BASE_URL"] as? String ?? ""
    }

    static var isDebug: Bool {
        #if DEBUG
        return true
        #else
        return false
        #endif
    }
}

// 编译条件
#if DEBUG
let logger = DebugLogger()
#elseif STAGING
let logger = StagingLogger()
#else
let logger = ProductionLogger()
#endif
```

## 4. Scheme 配置

```swift
// Xcode → Product → Scheme → Edit Scheme
// - Build: 选择编译的 Target
// - Run: 选择 Debug/Release Configuration
// - Test: 配置测试 Target
// - Archive: 发布配置

// 创建多个 Scheme：MyApp-Dev, MyApp-Staging, MyApp-Prod
// 每个 Scheme 关联不同的 xcconfig
```

## 5. Build Phase 脚本

```bash
# SwiftLint 检查（Build Phases → New Run Script Phase）
if which swiftlint > /dev/null; then
    swiftlint
else
    echo "warning: SwiftLint not installed"
fi

# 自动递增 Build Number
buildNumber=$(/usr/libexec/PlistBuddy -c "Print CFBundleVersion" "${PROJECT_DIR}/${INFOPLIST_FILE}")
buildNumber=$(($buildNumber + 1))
/usr/libexec/PlistBuddy -c "Set :CFBundleVersion $buildNumber" "${PROJECT_DIR}/${INFOPLIST_FILE}"
```

## 6. 编译速度优化

```swift
// 1. 查看编译耗时
// Build Settings → Other Swift Flags → -Xfrontend -warn-long-function-bodies=100

// 2. 减少类型推断复杂度
// ❌ 编译器推断耗时
let result = items.map { $0.value }.filter { $0 > 0 }.reduce(0, +)

// ✅ 显式标注类型
let values: [Int] = items.map { $0.value }
let filtered: [Int] = values.filter { $0 > 0 }
let result: Int = filtered.reduce(0, +)

// 3. 模块化编译（SPM 分模块，只重编修改的模块）
// 4. 开启 Eager Linking: Build Settings → EAGER_LINKING = YES
```
