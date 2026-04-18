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

## 7. Xcode 26 版本演进

> 🔄 更新于 2026-04-18

<!-- version-check: Xcode 26.4, checked 2026-04-18 -->

Xcode 26 于 WWDC 2025 发布，当前稳定版为 Xcode 26.4（2026-03-24）。来源：[Xcode What's New](https://developer.apple.com/xcode/whats-new/)、[Apple Newsroom - Xcode 26.3](https://www.apple.com/gq/newsroom/2026/02/xcode-26-point-3-unlocks-the-power-of-agentic-coding/)

### 版本对比

| 版本 | 发布时间 | Swift | 关键特性 |
|------|---------|-------|---------|
| Xcode 16 | 2024-09 | Swift 6.0 | Swift 6 严格并发、Swift Testing |
| Xcode 26 | 2025-09 | Swift 6.2 | AI 编码助手、Liquid Glass、Approachable Concurrency |
| Xcode 26.3 | 2026-02 | Swift 6.2 | **Agentic Coding**（Claude Agent、Codex 集成） |
| Xcode 26.4 | 2026-03 | Swift 6.2 | 稳定性修复 |
| Xcode 26.5 | Beta | Swift 6.2 | 预览中 |

### AI Coding Intelligence

Xcode 26 内置 AI 编码助手（Coding Intelligence），默认使用 ChatGPT，也支持其他 LLM。

```
// Xcode 26 AI 功能
// - 代码补全和生成
// - 代码重构建议
// - Bug 修复建议
// - 自然语言交互

// Xcode 26.3 Agentic Coding
// - Claude Agent 和 Codex 可以自主分析项目
// - 修改文件、搜索文档、更新项目设置
// - 捕获 Xcode Previews 并迭代修复
```

### 性能改进

```
// Xcode 26 性能数据
// - 下载体积减少 24%
// - 工作区加载速度提升 40%
// - 编译缓存（Compilation Caching）加速增量构建
```

### Build Settings 更新

```
// Xcode 26 推荐配置
SWIFT_VERSION = 6.2
IPHONEOS_DEPLOYMENT_TARGET = 18.0  // 或 26.0（新命名）

// Approachable Concurrency（新项目默认开启）
// Build Settings → Swift Compiler - Upcoming Features
// → Default Actor Isolation = MainActor

// 严格内存安全（可选）
// SWIFT_STRICT_MEMORY_SAFETY = YES
```
