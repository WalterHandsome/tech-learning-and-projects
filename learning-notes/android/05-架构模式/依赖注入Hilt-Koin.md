# 依赖注入 Hilt / Koin

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
