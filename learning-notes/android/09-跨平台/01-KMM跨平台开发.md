# KMM 跨平台开发
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. Kotlin Multiplatform 项目结构

```
shared/
├── src/
│   ├── commonMain/kotlin/    # 共享代码
│   ├── androidMain/kotlin/   # Android 特定实现
│   └── iosMain/kotlin/       # iOS 特定实现
├── build.gradle.kts
androidApp/                    # Android 应用
iosApp/                        # iOS 应用
```

```kotlin
// shared/build.gradle.kts
plugins {
    kotlin("multiplatform")
    id("com.android.library")
    kotlin("plugin.serialization")
}

kotlin {
    androidTarget()
    iosX64()
    iosArm64()
    iosSimulatorArm64()

    sourceSets {
        commonMain.dependencies {
            implementation("io.ktor:ktor-client-core:2.3.7")
            implementation("io.ktor:ktor-client-content-negotiation:2.3.7")
            implementation("org.jetbrains.kotlinx:kotlinx-serialization-json:1.6.2")
            implementation("org.jetbrains.kotlinx:kotlinx-coroutines-core:1.7.3")
        }
        androidMain.dependencies {
            implementation("io.ktor:ktor-client-okhttp:2.3.7")
        }
        iosMain.dependencies {
            implementation("io.ktor:ktor-client-darwin:2.3.7")
        }
    }
}
```

## 2. expect / actual

```kotlin
// commonMain：声明期望
expect class PlatformInfo() {
    val name: String
    val version: String
}

expect fun createUUID(): String

// androidMain：Android 实现
actual class PlatformInfo actual constructor() {
    actual val name: String = "Android"
    actual val version: String = "${Build.VERSION.SDK_INT}"
}

actual fun createUUID(): String = java.util.UUID.randomUUID().toString()

// iosMain：iOS 实现
actual class PlatformInfo actual constructor() {
    actual val name: String = "iOS"
    actual val version: String = UIDevice.currentDevice.systemVersion
}

actual fun createUUID(): String = NSUUID().UUIDString()
```

## 3. Ktor 网络请求

```kotlin
// commonMain
class ApiClient {
    private val client = HttpClient {
        install(ContentNegotiation) { json(Json { ignoreUnknownKeys = true }) }
        install(Logging) { level = LogLevel.BODY }
        defaultRequest { url("https://api.example.com/v1/") }
    }

    suspend fun getUsers(): List<User> = client.get("users").body()

    suspend fun createUser(user: CreateUserRequest): User =
        client.post("users") {
            contentType(ContentType.Application.Json)
            setBody(user)
        }.body()
}

@Serializable
data class User(val id: String, val name: String, val email: String)
```

## 4. SQLDelight 数据库

```sql
-- shared/src/commonMain/sqldelight/com/example/db/User.sq
CREATE TABLE UserEntity (
    id TEXT NOT NULL PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT NOT NULL
);

selectAll:
SELECT * FROM UserEntity ORDER BY name;

insertUser:
INSERT OR REPLACE INTO UserEntity(id, name, email) VALUES (?, ?, ?);

deleteUser:
DELETE FROM UserEntity WHERE id = ?;
```

```kotlin
// commonMain
class UserLocalDataSource(private val database: AppDatabase) {
    fun getAllUsers(): Flow<List<UserEntity>> =
        database.userQueries.selectAll().asFlow().mapToList(Dispatchers.Default)

    suspend fun insertUser(user: User) {
        database.userQueries.insertUser(user.id, user.name, user.email)
    }
}

// androidMain
actual fun createDatabase(context: Any): AppDatabase {
    val driver = AndroidSqliteDriver(AppDatabase.Schema, context as Context, "app.db")
    return AppDatabase(driver)
}
```

## 5. 共享 ViewModel 逻辑

```kotlin
// commonMain
class UserViewModel(private val repository: UserRepository) {
    private val _state = MutableStateFlow(UserState())
    val state: StateFlow<UserState> = _state.asStateFlow()

    fun loadUsers() {
        _state.update { it.copy(isLoading = true) }
        CoroutineScope(Dispatchers.Default).launch {
            try {
                val users = repository.getUsers()
                _state.update { it.copy(users = users, isLoading = false) }
            } catch (e: Exception) {
                _state.update { it.copy(error = e.message, isLoading = false) }
            }
        }
    }
}

data class UserState(
    val users: List<User> = emptyList(),
    val isLoading: Boolean = false,
    val error: String? = null
)
```

## 6. 2026 版本演进

> 🔄 更新于 2026-04-21

<!-- version-check: Kotlin 2.3.20, Compose Multiplatform 1.10.2, checked 2026-04-21 -->

### Compose Multiplatform 1.10.x

JetBrains 于 2026-01 发布 Compose Multiplatform 1.10.0，当前稳定版为 1.10.2。三大核心更新：

**1. 统一 @Preview 注解**：
- 三个平台各自的 `@Preview` 注解统一为一个
- 在 `commonMain` 中使用 `androidx.compose.ui.tooling.preview.Preview`
- IDE 提供快速修复建议，自动迁移旧注解

```kotlin
// commonMain — 统一的 @Preview 注解
import androidx.compose.ui.tooling.preview.Preview

@Preview
@Composable
fun GreetingPreview() {
    Text("Hello, Compose Multiplatform!")
}
```

**2. Navigation 3 跨平台支持**：
- 全新导航库，直接操作导航栈
- 添加/移除目的地更直观
- 非 Android 平台也可使用
- PredictiveBackHandler 已废弃，改用 Navigation Event 库

**3. Compose Hot Reload 1.0 稳定版**：
- 实时查看 UI 代码变更，无需重启应用
- 内置于 Compose Multiplatform Gradle 插件，默认启用，零配置
- 支持添加/删除函数、类、参数等几乎任意代码变更
- 通过 `./gradlew :myApp:hotRunJvm` 或 IDE 按钮启动

### Compose Multiplatform for iOS 已稳定

自 Compose Multiplatform 1.8.0（2025-05）起，iOS 平台已达到 Stable 状态，可用于生产环境。

### 依赖版本更新

```kotlin
// shared/build.gradle.kts — 2026 推荐版本
plugins {
    kotlin("multiplatform") version "2.3.20"
    id("com.android.library")
    kotlin("plugin.serialization") version "2.3.20"
    id("org.jetbrains.compose") version "1.10.2"
}

kotlin {
    androidTarget()
    iosX64()
    iosArm64()
    iosSimulatorArm64()
    // 新增：Web 和 Desktop 目标
    jvm("desktop")
    // wasmJs()  // Compose for Web (Beta)

    sourceSets {
        commonMain.dependencies {
            implementation(compose.runtime)
            implementation(compose.foundation)
            implementation(compose.material3)
            implementation(compose.ui)
            // Ktor 3.x（KMP 原生支持）
            implementation("io.ktor:ktor-client-core:3.1.3")
            implementation("io.ktor:ktor-client-content-negotiation:3.1.3")
            implementation("org.jetbrains.kotlinx:kotlinx-serialization-json:1.8.1")
            implementation("org.jetbrains.kotlinx:kotlinx-coroutines-core:1.10.2")
        }
        androidMain.dependencies {
            implementation("io.ktor:ktor-client-okhttp:3.1.3")
        }
        iosMain.dependencies {
            implementation("io.ktor:ktor-client-darwin:3.1.3")
        }
    }
}
```

### KMP 生态成熟度（2026）

| 能力 | 状态 | 说明 |
|------|------|------|
| 共享业务逻辑 | ✅ Stable | Kotlin 2.3.20 + K2 编译器 |
| Compose UI 共享（Android） | ✅ Stable | Compose 1.10.x |
| Compose UI 共享（iOS） | ✅ Stable | 自 CMP 1.8.0 起 |
| Compose UI 共享（Desktop） | ✅ Stable | JVM 目标 |
| Compose UI 共享（Web） | 🔶 Beta | Wasm 目标 |
| Navigation 3 | ✅ 跨平台 | CMP 1.10.0 引入 |
| Hot Reload | ✅ Stable 1.0 | 零配置，默认启用 |
| Room 数据库 | ✅ KMP 支持 | Room 2.8.4+ / Room 3.0 alpha |
| Ktor 网络 | ✅ Stable | Ktor 3.x |

> 来源：[Compose Multiplatform 1.10.0 Blog](https://blog.jetbrains.com/kotlin/2026/01/compose-multiplatform-1-10-0/)、[Compose Hot Reload 1.0.0](https://blog.jetbrains.com/kotlin/2026/01/the-journey-to-compose-hot-reload-1-0-0/)、[KMP Compatibility Guide](https://www.jetbrains.com/help/kotlin-multiplatform-dev/multiplatform-compatibility-guide.html)
