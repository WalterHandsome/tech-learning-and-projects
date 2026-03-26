# Kotlin 序列化与 JSON

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
