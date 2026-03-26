# Gradle 构建系统

## 1. build.gradle.kts 基础

```kotlin
// app/build.gradle.kts
plugins {
    alias(libs.plugins.android.application)
    alias(libs.plugins.kotlin.android)
    alias(libs.plugins.hilt)
    alias(libs.plugins.ksp)
}

android {
    namespace = "com.example.app"
    compileSdk = 34

    defaultConfig {
        applicationId = "com.example.app"
        minSdk = 26
        targetSdk = 34
        versionCode = 1
        versionName = "1.0.0"
        testInstrumentationRunner = "androidx.test.runner.AndroidJUnitRunner"
    }

    buildFeatures {
        compose = true
        buildConfig = true
    }

    composeOptions {
        kotlinCompilerExtensionVersion = libs.versions.composeCompiler.get()
    }

    kotlin { jvmToolchain(17) }
}
```

## 2. Version Catalog

```toml
# gradle/libs.versions.toml
[versions]
agp = "8.2.2"
kotlin = "1.9.22"
compose-bom = "2024.02.00"
hilt = "2.50"
room = "2.6.1"
ktor = "2.3.7"

[libraries]
# Compose
compose-bom = { group = "androidx.compose", name = "compose-bom", version.ref = "compose-bom" }
compose-ui = { group = "androidx.compose.ui", name = "ui" }
compose-material3 = { group = "androidx.compose.material3", name = "material3" }
compose-navigation = { group = "androidx.navigation", name = "navigation-compose", version = "2.7.6" }

# Hilt
hilt-android = { group = "com.google.dagger", name = "hilt-android", version.ref = "hilt" }
hilt-compiler = { group = "com.google.dagger", name = "hilt-compiler", version.ref = "hilt" }

# Room
room-runtime = { group = "androidx.room", name = "room-runtime", version.ref = "room" }
room-compiler = { group = "androidx.room", name = "room-compiler", version.ref = "room" }
room-ktx = { group = "androidx.room", name = "room-ktx", version.ref = "room" }

[bundles]
compose = ["compose-ui", "compose-material3", "compose-navigation"]
room = ["room-runtime", "room-ktx"]

[plugins]
android-application = { id = "com.android.application", version.ref = "agp" }
kotlin-android = { id = "org.jetbrains.kotlin.android", version.ref = "kotlin" }
hilt = { id = "com.google.dagger.hilt.android", version.ref = "hilt" }
ksp = { id = "com.google.devtools.ksp", version = "1.9.22-1.0.17" }
```

## 3. Build Variants

```kotlin
android {
    buildTypes {
        debug {
            isDebuggable = true
            applicationIdSuffix = ".debug"
            versionNameSuffix = "-debug"
            buildConfigField("String", "API_URL", "\"https://dev-api.example.com\"")
        }
        release {
            isMinifyEnabled = true
            isShrinkResources = true
            buildConfigField("String", "API_URL", "\"https://api.example.com\"")
            proguardFiles(getDefaultProguardFile("proguard-android-optimize.txt"), "proguard-rules.pro")
        }
    }

    flavorDimensions += "environment"
    productFlavors {
        create("staging") {
            dimension = "environment"
            applicationIdSuffix = ".staging"
            buildConfigField("String", "ENV", "\"staging\"")
        }
        create("production") {
            dimension = "environment"
            buildConfigField("String", "ENV", "\"production\"")
        }
    }
}
```

## 4. 自定义 Gradle Task

```kotlin
// 打印 APK 大小
tasks.register("printApkSize") {
    doLast {
        val apkDir = layout.buildDirectory.dir("outputs/apk/release").get().asFile
        apkDir.listFiles()?.filter { it.extension == "apk" }?.forEach {
            println("${it.name}: ${it.length() / 1024 / 1024}MB")
        }
    }
}

// 复制 APK 到指定目录
tasks.register<Copy>("copyRelease") {
    from(layout.buildDirectory.dir("outputs/apk/release"))
    into("${rootProject.projectDir}/release")
    include("*.apk")
    rename { "app-v${android.defaultConfig.versionName}.apk" }
}
```

## 5. 构建加速

```properties
# gradle.properties
org.gradle.jvmargs=-Xmx4g -XX:+UseParallelGC
org.gradle.parallel=true
org.gradle.caching=true
org.gradle.configuration-cache=true
kotlin.incremental=true
```
