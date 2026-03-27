# CI/CD 与自动化发布

> Author: Walter Wang

## 1. Fastlane 基础配置

```ruby
# Fastfile
default_platform(:ios)

platform :ios do
  desc "运行测试"
  lane :test do
    run_tests(
      scheme: "MyApp",
      devices: ["iPhone 15"],
      code_coverage: true
    )
  end

  desc "发布到 TestFlight"
  lane :beta do
    increment_build_number
    build_app(
      scheme: "MyApp",
      export_method: "app-store",
      output_directory: "./build"
    )
    upload_to_testflight(
      skip_waiting_for_build_processing: true
    )
    slack(message: "新版本已上传 TestFlight")
  end

  desc "发布到 App Store"
  lane :release do
    build_app(scheme: "MyApp", export_method: "app-store")
    upload_to_app_store(
      force: true,
      submit_for_review: true,
      automatic_release: true
    )
  end
end
```

## 2. Fastlane Match（证书管理）

```ruby
# Matchfile
git_url("https://github.com/company/certificates.git")
storage_mode("git")
type("appstore")
app_identifier("com.company.app")

# 使用
lane :sync_certs do
  match(type: "development")
  match(type: "appstore")
end
```

## 3. GitHub Actions

```yaml
# .github/workflows/ios.yml
name: iOS CI

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  build-and-test:
    runs-on: macos-14
    steps:
      - uses: actions/checkout@v4

      - name: Select Xcode
        run: sudo xcode-select -s /Applications/Xcode_15.2.app

      - name: Install dependencies
        run: |
          brew install swiftlint
          swift package resolve

      - name: SwiftLint
        run: swiftlint --strict

      - name: Build
        run: |
          xcodebuild build \
            -scheme MyApp \
            -destination 'platform=iOS Simulator,name=iPhone 15' \
            -configuration Debug

      - name: Test
        run: |
          xcodebuild test \
            -scheme MyApp \
            -destination 'platform=iOS Simulator,name=iPhone 15' \
            -resultBundlePath TestResults

      - name: Upload test results
        uses: actions/upload-artifact@v4
        if: always()
        with:
          name: test-results
          path: TestResults
```

## 4. GitHub Actions + Fastlane 发布

```yaml
  deploy-testflight:
    needs: build-and-test
    runs-on: macos-14
    if: github.ref == 'refs/heads/main'
    steps:
      - uses: actions/checkout@v4

      - name: Install Fastlane
        run: gem install fastlane

      - name: Deploy to TestFlight
        env:
          APP_STORE_CONNECT_API_KEY_ID: ${{ secrets.API_KEY_ID }}
          APP_STORE_CONNECT_ISSUER_ID: ${{ secrets.ISSUER_ID }}
          APP_STORE_CONNECT_API_KEY: ${{ secrets.API_KEY }}
          MATCH_PASSWORD: ${{ secrets.MATCH_PASSWORD }}
        run: fastlane beta
```

## 5. Xcode Cloud

```swift
// Xcode → Product → Xcode Cloud → Create Workflow
// 配置项：
// - Start Conditions: Branch changes, PR, Tag
// - Environment: Xcode version, macOS version
// - Build Actions: Build, Test, Analyze, Archive
// - Post Actions: TestFlight, Notify

// ci_scripts/ci_post_clone.sh（自定义脚本）
#!/bin/sh
brew install swiftlint
swift package resolve
```

## 6. TestFlight 分发

```swift
// Fastlane 自动上传
lane :beta do
  build_app(scheme: "MyApp")
  upload_to_testflight(
    changelog: "修复已知问题，优化性能",
    groups: ["内部测试组"],
    distribute_external: true,
    notify_external_testers: true
  )
end

// App Store Connect API Key 认证（无需密码）
app_store_connect_api_key(
  key_id: "XXXXXXXXXX",
  issuer_id: "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
  key_filepath: "./AuthKey.p8"
)
```
