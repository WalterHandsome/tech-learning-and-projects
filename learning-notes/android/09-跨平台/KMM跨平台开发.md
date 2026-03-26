# KMM 跨平台开发

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
