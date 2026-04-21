# 依赖注入 Hilt / Koin
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. Hilt 基础

```kotlin
// Application
@HiltAndroidApp
class MyApp : Application()

// Activity
@AndroidEntryPoint
class MainActivity : ComponentActivity()

// ViewModel 注入
@HiltViewModel
class UserViewModel @Inject constructor(
    private val repository: UserRepository,
    private val savedStateHandle: SavedStateHandle
) : ViewModel()
```

## 2. Hilt Module

```kotlin
// 接口绑定
@Module
@InstallIn(SingletonComponent::class)
abstract class RepositoryModule {
    @Binds
    @Singleton
    abstract fun bindUserRepository(impl: UserRepositoryImpl): UserRepository
}

// 实例提供
@Module
@InstallIn(SingletonComponent::class)
object NetworkModule {
    @Provides
    @Singleton
    fun provideOkHttpClient(): OkHttpClient = OkHttpClient.Builder()
        .addInterceptor(HttpLoggingInterceptor())
        .build()

    @Provides
    @Singleton
    fun provideRetrofit(client: OkHttpClient): Retrofit = Retrofit.Builder()
        .baseUrl("https://api.example.com/")
        .client(client)
        .addConverterFactory(Json.asConverterFactory("application/json".toMediaType()))
        .build()

    @Provides
    @Singleton
    fun provideApiService(retrofit: Retrofit): ApiService =
        retrofit.create(ApiService::class.java)
}
```

## 3. Hilt Scope

```kotlin
// SingletonComponent  → Application 生命周期
// ActivityComponent   → Activity 生命周期
// ViewModelComponent  → ViewModel 生命周期
// FragmentComponent   → Fragment 生命周期

// Qualifier（区分同类型）
@Qualifier
@Retention(AnnotationRetention.BINARY)
annotation class IoDispatcher

@Module
@InstallIn(SingletonComponent::class)
object DispatcherModule {
    @Provides
    @IoDispatcher
    fun provideIoDispatcher(): CoroutineDispatcher = Dispatchers.IO
}

class UserRepository @Inject constructor(
    private val api: ApiService,
    @IoDispatcher private val dispatcher: CoroutineDispatcher
)
```

## 4. Koin 基础

```kotlin
// Application
class MyApp : Application() {
    override fun onCreate() {
        super.onCreate()
        startKoin {
            androidContext(this@MyApp)
            modules(appModule, networkModule, viewModelModule)
        }
    }
}

// Module 定义
val appModule = module {
    single<UserRepository> { UserRepositoryImpl(get(), get()) }
    factory { GetUsersUseCase(get()) }
}

val networkModule = module {
    single {
        OkHttpClient.Builder()
            .addInterceptor(HttpLoggingInterceptor())
            .build()
    }
    single {
        Retrofit.Builder()
            .baseUrl("https://api.example.com/")
            .client(get())
            .addConverterFactory(Json.asConverterFactory("application/json".toMediaType()))
            .build()
    }
    single { get<Retrofit>().create(ApiService::class.java) }
}

val viewModelModule = module {
    viewModel { UserViewModel(get()) }
    viewModel { (userId: String) -> DetailViewModel(userId, get()) }
}
```

## 5. Koin 使用

```kotlin
// Activity 中注入
class MainActivity : AppCompatActivity() {
    private val viewModel: UserViewModel by viewModel()
}

// Compose 中注入
@Composable
fun UserScreen(viewModel: UserViewModel = koinViewModel()) {
    val state by viewModel.uiState.collectAsStateWithLifecycle()
}

// 带参数
val detailVm: DetailViewModel by viewModel { parametersOf("user_123") }

// Scope
val sessionModule = module {
    scope<UserSession> {
        scoped { AuthRepository(get()) }
    }
}
```

## 6. Hilt vs Koin 对比

```kotlin
// Hilt：编译时检查，Google 官方，注解驱动，学习曲线较高
// Koin：运行时解析，DSL 简洁，轻量，适合中小项目
// 推荐：大型项目用 Hilt，快速原型用 Koin
```

## 7. 2026 版本演进

> 🔄 更新于 2026-04-21

<!-- version-check: Hilt/Dagger 2.57.1, Koin 4.1, checked 2026-04-21 -->

### Hilt/Dagger 2.57.1（当前稳定版）

- 新增 `jakarta.inject.Provider` 注入支持（与 `javax.inject.Provider` 同等使用）
- 要求 Kotlin 2.0+（与 Kotlin 1.9 不兼容，需注意升级）
- Android 官方文档已更新为 2.57.1 作为推荐版本
- 来源：[Dagger Releases](https://github.com/google/dagger/releases)

```kotlin
// Hilt 2.57.1 版本配置
// build.gradle.kts (Project)
plugins {
    id("com.google.dagger.hilt.android") version "2.57.1" apply false
}

// build.gradle.kts (App)
plugins {
    id("com.google.dagger.hilt.android")
    id("com.google.devtools.ksp") // KSP 替代 kapt
}

dependencies {
    implementation("com.google.dagger:hilt-android:2.57.1")
    ksp("com.google.dagger:hilt-android-compiler:2.57.1")
    // jakarta.inject.Provider 现在可以直接使用
    // 无需额外依赖
}
```

### Koin 4.1（2025-06 发布）

Koin 4.1 是一个重要版本，引入了 Kotlin Compiler Plugin 和大量 KMP 改进：

- **Kotlin Compiler Plugin**：原生编译时安全 + 自动装配，推荐所有 Kotlin 2.x 新项目使用
- **模块化解析引擎**：可复用配置块、运行时特性标志
- **Archetype-based Scopes**：包括 ViewModel 构造函数注入的人体工学改进
- **Compose 1.8/MPP 支持**：自动上下文处理、更快注入、预览支持
- **Ktor 3.2 集成**：内联模块、请求作用域、多平台 artifact
- **WASM-safe UUID**：支持 Kotlin/WASM 目标
- 来源：[Koin 4.1 Blog](https://blog.kotzilla.io/koin-4.1-is-here)

```kotlin
// Koin 4.1 + Kotlin Compiler Plugin 配置
// build.gradle.kts
plugins {
    id("io.insert-koin.koin") version "4.1.0" // Koin Compiler Plugin
}

dependencies {
    implementation("io.insert-koin:koin-android:4.1.0")
    implementation("io.insert-koin:koin-androidx-compose:4.1.0")
}

// 使用 Compiler Plugin 的自动装配（无需手动 get()）
@Single
class UserRepository(
    private val api: ApiService,  // 自动装配
    private val dao: UserDao      // 自动装配
)

@Factory
class GetUsersUseCase(
    private val repository: UserRepository  // 编译时检查
)
```

### 更新后的 Hilt vs Koin 对比

| 维度 | Hilt 2.57.1 | Koin 4.1 |
|------|-------------|----------|
| 检查时机 | 编译时 | 编译时（Compiler Plugin）或运行时 |
| 官方支持 | Google 官方 | 社区驱动 |
| KMP 支持 | ❌ 仅 Android | ✅ 全平台（iOS/JS/WASM） |
| Compose 集成 | `hiltViewModel()` | `koinViewModel()`，自动上下文 |
| 注解/DSL | 注解驱动 | DSL + 注解（可选） |
| Jakarta 支持 | ✅ 2.57+ | N/A |
| 学习曲线 | 较高 | 较低 |
| 推荐场景 | 大型 Android 项目 | KMP 项目、中小项目 |
