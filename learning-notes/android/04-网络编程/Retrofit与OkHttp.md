# Retrofit 与 OkHttp

## 1. Retrofit 接口定义

```kotlin
interface ApiService {
    @GET("users")
    suspend fun getUsers(@Query("page") page: Int): Response<List<User>>

    @GET("users/{id}")
    suspend fun getUser(@Path("id") userId: String): User

    @POST("users")
    suspend fun createUser(@Body user: CreateUserRequest): User

    @PUT("users/{id}")
    suspend fun updateUser(@Path("id") id: String, @Body user: User): User

    @DELETE("users/{id}")
    suspend fun deleteUser(@Path("id") id: String): Response<Unit>

    @Multipart
    @POST("upload")
    suspend fun uploadFile(
        @Part file: MultipartBody.Part,
        @Part("description") desc: RequestBody
    ): UploadResponse

    @Headers("Cache-Control: max-age=600")
    @GET("config")
    suspend fun getConfig(): AppConfig
}
```

## 2. Retrofit 配置

```kotlin
@Module
@InstallIn(SingletonComponent::class)
object NetworkModule {

    @Provides
    @Singleton
    fun provideOkHttpClient(): OkHttpClient = OkHttpClient.Builder()
        .connectTimeout(15, TimeUnit.SECONDS)
        .readTimeout(15, TimeUnit.SECONDS)
        .addInterceptor(AuthInterceptor())
        .addInterceptor(HttpLoggingInterceptor().apply {
            level = HttpLoggingInterceptor.Level.BODY
        })
        .build()

    @Provides
    @Singleton
    fun provideRetrofit(client: OkHttpClient): Retrofit = Retrofit.Builder()
        .baseUrl("https://api.example.com/v1/")
        .client(client)
        .addConverterFactory(Json.asConverterFactory("application/json".toMediaType()))
        .build()

    @Provides
    @Singleton
    fun provideApiService(retrofit: Retrofit): ApiService =
        retrofit.create(ApiService::class.java)
}
```

## 3. OkHttp 拦截器

```kotlin
// 认证拦截器
class AuthInterceptor @Inject constructor(
    private val tokenManager: TokenManager
) : Interceptor {
    override fun intercept(chain: Interceptor.Chain): Response {
        val request = chain.request().newBuilder()
            .addHeader("Authorization", "Bearer ${tokenManager.getToken()}")
            .addHeader("Accept", "application/json")
            .build()
        return chain.proceed(request)
    }
}

// Token 刷新拦截器
class TokenRefreshInterceptor(
    private val tokenManager: TokenManager
) : Authenticator {
    override fun authenticate(route: Route?, response: Response): Request? {
        if (response.code == 401) {
            val newToken = runBlocking { tokenManager.refreshToken() } ?: return null
            return response.request.newBuilder()
                .header("Authorization", "Bearer $newToken")
                .build()
        }
        return null
    }
}
```

## 4. 统一错误处理

```kotlin
sealed class ApiResult<out T> {
    data class Success<T>(val data: T) : ApiResult<T>()
    data class Error(val code: Int, val message: String) : ApiResult<Nothing>()
    data class Exception(val e: Throwable) : ApiResult<Nothing>()
}

suspend fun <T> safeApiCall(call: suspend () -> Response<T>): ApiResult<T> {
    return try {
        val response = call()
        if (response.isSuccessful) {
            ApiResult.Success(response.body()!!)
        } else {
            ApiResult.Error(response.code(), response.message())
        }
    } catch (e: IOException) {
        ApiResult.Exception(e)
    }
}

// 使用
class UserRepository @Inject constructor(private val api: ApiService) {
    suspend fun getUsers(page: Int): ApiResult<List<User>> =
        safeApiCall { api.getUsers(page) }
}
```

## 5. 连接池与性能

```kotlin
val client = OkHttpClient.Builder()
    .connectionPool(ConnectionPool(5, 5, TimeUnit.MINUTES))
    .protocols(listOf(Protocol.HTTP_2, Protocol.HTTP_1_1))
    .dns(object : Dns {
        override fun lookup(hostname: String): List<InetAddress> {
            // 自定义 DNS 解析
            return Dns.SYSTEM.lookup(hostname)
        }
    })
    .build()
```
