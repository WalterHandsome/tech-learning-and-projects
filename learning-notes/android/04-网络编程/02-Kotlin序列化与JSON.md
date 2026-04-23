# Kotlin 序列化与 JSON
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. kotlinx.serialization

```kotlin
// build.gradle.kts: id("org.jetbrains.kotlin.plugin.serialization")
// 依赖: org.jetbrains.kotlinx:kotlinx-serialization-json

@Serializable
data class User(
    val id: Int,
    val name: String,
    @SerialName("email_address") val email: String,
    val avatar: String? = null,           // 可选字段
    @Transient val localCache: String = "" // 不参与序列化
)

// 序列化 / 反序列化
val json = Json {
    ignoreUnknownKeys = true
    prettyPrint = true
    encodeDefaults = false
    coerceInputValues = true  // null → 默认值
}

val user = User(1, "张三", "test@example.com")
val jsonStr = json.encodeToString(user)
val parsed: User = json.decodeFromString(jsonStr)

// 列表
val users: List<User> = json.decodeFromString(jsonArrayStr)
```

## 2. 多态序列化

```kotlin
@Serializable
sealed class ApiResponse<out T> {
    @Serializable
    @SerialName("success")
    data class Success<T>(val data: T, val code: Int = 200) : ApiResponse<T>()

    @Serializable
    @SerialName("error")
    data class Error(val message: String, val code: Int) : ApiResponse<Nothing>()
}

// 配合 Retrofit
val retrofit = Retrofit.Builder()
    .baseUrl(BASE_URL)
    .addConverterFactory(json.asConverterFactory("application/json".toMediaType()))
    .build()
```

## 3. Gson

```kotlin
// 依赖: com.google.code.gson:gson

data class Post(
    val id: Int,
    val title: String,
    @SerializedName("created_at") val createdAt: String,
    @Expose(serialize = false) val internalId: String? = null
)

val gson = GsonBuilder()
    .setDateFormat("yyyy-MM-dd'T'HH:mm:ss")
    .serializeNulls()
    .excludeFieldsWithoutExposeAnnotation()
    .registerTypeAdapter(Date::class.java, DateDeserializer())
    .create()

val post: Post = gson.fromJson(jsonStr, Post::class.java)
val jsonStr = gson.toJson(post)

// 泛型反序列化
val type = object : TypeToken<List<Post>>() {}.type
val posts: List<Post> = gson.fromJson(jsonStr, type)

// 自定义 TypeAdapter
class DateDeserializer : JsonDeserializer<Date> {
    override fun deserialize(json: JsonElement, type: Type, ctx: JsonDeserializationContext): Date {
        return SimpleDateFormat("yyyy-MM-dd", Locale.getDefault()).parse(json.asString)!!
    }
}
```

## 4. Moshi

```kotlin
// 依赖: com.squareup.moshi:moshi-kotlin

@JsonClass(generateAdapter = true)
data class Article(
    val id: Long,
    val title: String,
    @Json(name = "author_name") val author: String,
    val tags: List<String> = emptyList()
)

val moshi = Moshi.Builder()
    .addLast(KotlinJsonAdapterFactory())
    .build()

val adapter = moshi.adapter<Article>()
val article = adapter.fromJson(jsonStr)
val json = adapter.toJson(article)

// 列表
val listAdapter = moshi.adapter<List<Article>>()
val articles = listAdapter.fromJson(jsonArrayStr)

// 配合 Retrofit
Retrofit.Builder()
    .addConverterFactory(MoshiConverterFactory.create(moshi))
    .build()
```

## 5. 对比选择

```kotlin
// kotlinx.serialization：Kotlin 原生，编译时生成，KMM 支持
// Gson：Java 生态广泛，运行时反射，配置灵活
// Moshi：Square 出品，Kotlin 友好，代码生成 + 反射两种模式

// 推荐：新项目用 kotlinx.serialization，已有项目按现有选择
```

## 6. 2026 版本演进与 Ktor 集成

<!-- version-check: kotlinx-serialization 1.8.x (Kotlin 2.3.20), Ktor 3.4.0, checked 2026-04-22 -->

> 🔄 更新于 2026-04-22

kotlinx.serialization 随 Kotlin 2.3.20 持续更新，Ktor 3.4.0 带来了 OpenAPI 生成和 Zstd 支持。来源：[Ktor 3.4.0](https://blog.jetbrains.com/kotlin/2026/01/ktor-3-4-0-is-now-available/)

### 6.1 kotlinx.serialization 最新实践

```kotlin
// build.gradle.kts（Kotlin 2.3.20 + kotlinx-serialization）
plugins {
    id("org.jetbrains.kotlin.plugin.serialization") version "2.3.20"
}

dependencies {
    implementation("org.jetbrains.kotlinx:kotlinx-serialization-json:1.8.1")
}

// 2026 推荐 Json 配置
val json = Json {
    ignoreUnknownKeys = true       // 忽略未知字段
    encodeDefaults = false          // 不序列化默认值
    coerceInputValues = true        // null → 默认值
    explicitNulls = false           // 不输出 null 字段
    isLenient = true                // 宽松解析
    prettyPrint = false             // 生产环境关闭美化
}
```

### 6.2 Ktor 3.4.0 网络客户端

```kotlin
// Ktor 3.4.0 作为 OkHttp 的 Kotlin 原生替代
// build.gradle.kts
dependencies {
    implementation("io.ktor:ktor-client-core:3.4.0")
    implementation("io.ktor:ktor-client-okhttp:3.4.0")  // 或 CIO 引擎
    implementation("io.ktor:ktor-client-content-negotiation:3.4.0")
    implementation("io.ktor:ktor-serialization-kotlinx-json:3.4.0")
}

// 配置 Ktor 客户端
val client = HttpClient(OkHttp) {
    install(ContentNegotiation) {
        json(Json {
            ignoreUnknownKeys = true
            encodeDefaults = false
        })
    }
    install(HttpTimeout) {
        requestTimeoutMillis = 15_000
        connectTimeoutMillis = 10_000
    }
}

// 使用
suspend fun getUsers(): List<User> {
    return client.get("https://api.example.com/users").body()
}
```

### 6.3 序列化方案选型（2026）

```
方案                    推荐场景                    KMP 支持
──────────────────────────────────────────────────────────
kotlinx.serialization   新项目、KMP 项目             ✅ 全平台
Moshi                   已有 Square 技术栈           ❌ JVM only
Gson                    已有 Java 项目               ❌ JVM only
Ktor serialization      Ktor 客户端/服务端           ✅ 全平台
```

> **2026 推荐**：新项目统一使用 `kotlinx.serialization`，配合 Ktor 3.4.0 或 Retrofit 3.0 使用。KMP 项目必须使用 `kotlinx.serialization`。
