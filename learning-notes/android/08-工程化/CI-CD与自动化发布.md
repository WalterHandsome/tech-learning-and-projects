# CI/CD 与自动化发布

> Author: Walter Wang

## 1. GitHub Actions

```yaml
# .github/workflows/android.yml
name: Android CI

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-java@v4
        with:
          distribution: 'temurin'
          java-version: '17'
      - uses: gradle/actions/setup-gradle@v3

      - name: Run unit tests
        run: ./gradlew testDebugUnitTest

      - name: Run lint
        run: ./gradlew lintDebug

      - name: Upload test results
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: test-results
          path: app/build/reports/tests/

  build:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-java@v4
        with:
          distribution: 'temurin'
          java-version: '17'

      - name: Build Release APK
        run: ./gradlew assembleRelease
        env:
          KEYSTORE_PASSWORD: ${{ secrets.KEYSTORE_PASSWORD }}
          KEY_ALIAS: ${{ secrets.KEY_ALIAS }}
          KEY_PASSWORD: ${{ secrets.KEY_PASSWORD }}

      - name: Upload APK
        uses: actions/upload-artifact@v4
        with:
          name: release-apk
          path: app/build/outputs/apk/release/*.apk
```

## 2. 签名配置（CI 环境）

```kotlin
// app/build.gradle.kts
android {
    signingConfigs {
        create("release") {
            val keystoreFile = file("keystore/release.jks")
            if (keystoreFile.exists()) {
                storeFile = keystoreFile
                storePassword = System.getenv("KEYSTORE_PASSWORD")
                keyAlias = System.getenv("KEY_ALIAS")
                keyPassword = System.getenv("KEY_PASSWORD")
            }
        }
    }
}
```

```yaml
# GitHub Actions 中解码 keystore
- name: Decode Keystore
  run: echo "${{ secrets.KEYSTORE_BASE64 }}" | base64 -d > app/keystore/release.jks
```

## 3. Fastlane

```ruby
# fastlane/Fastfile
default_platform(:android)

platform :android do
  desc "Run tests"
  lane :test do
    gradle(task: "testDebugUnitTest")
  end

  desc "Build and deploy to Firebase"
  lane :beta do
    gradle(task: "assembleRelease")
    firebase_app_distribution(
      app: "1:123456:android:abcdef",
      groups: "internal-testers",
      release_notes: changelog_from_git_commits
    )
  end

  desc "Deploy to Google Play"
  lane :deploy do
    gradle(task: "bundleRelease")
    upload_to_play_store(
      track: "internal",
      aab: "app/build/outputs/bundle/release/app-release.aab",
      skip_upload_metadata: true,
      skip_upload_images: true
    )
  end
end
```

## 4. Firebase App Distribution

```yaml
# GitHub Actions 集成
- name: Upload to Firebase
  uses: wzieba/Firebase-Distribution-Github-Action@v1
  with:
    appId: ${{ secrets.FIREBASE_APP_ID }}
    serviceCredentialsFileContent: ${{ secrets.FIREBASE_CREDENTIALS }}
    groups: internal-testers
    file: app/build/outputs/apk/release/app-release.apk
    releaseNotes: |
      ${{ github.event.head_commit.message }}
```

## 5. 版本自动化

```kotlin
// 语义化版本 + Git Tag
// tag: v1.2.3 → versionName = "1.2.3", versionCode = 10203

// GitHub Actions Release 触发
// on:
//   push:
//     tags: ['v*']

// Gradle 读取 Git Tag
fun getVersionFromTag(): String {
    val process = Runtime.getRuntime().exec("git describe --tags --abbrev=0")
    val tag = process.inputStream.bufferedReader().readText().trim()
    return tag.removePrefix("v").ifEmpty { "0.0.1" }
}
```
