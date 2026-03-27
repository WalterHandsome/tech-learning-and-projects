# DataStore 数据存储
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. Preferences DataStore

```kotlin
// 创建 DataStore
val Context.dataStore by preferencesDataStore(name = "settings")

// 定义 Key
object PrefsKeys {
    val DARK_MODE = booleanPreferencesKey("dark_mode")
    val FONT_SIZE = intPreferencesKey("font_size")
    val USERNAME = stringPreferencesKey("username")
    val LANGUAGE = stringPreferencesKey("language")
}

// 读取数据（Flow）
class SettingsRepository(private val dataStore: DataStore<Preferences>) {

    val darkMode: Flow<Boolean> = dataStore.data
        .catch { if (it is IOException) emit(emptyPreferences()) else throw it }
        .map { it[PrefsKeys.DARK_MODE] ?: false }

    val fontSize: Flow<Int> = dataStore.data
        .map { it[PrefsKeys.FONT_SIZE] ?: 14 }

    // 写入数据
    suspend fun setDarkMode(enabled: Boolean) {
        dataStore.edit { it[PrefsKeys.DARK_MODE] = enabled }
    }

    suspend fun setFontSize(size: Int) {
        dataStore.edit { it[PrefsKeys.FONT_SIZE] = size }
    }

    // 清除所有
    suspend fun clearAll() {
        dataStore.edit { it.clear() }
    }
}
```

## 2. 在 ViewModel 中使用

```kotlin
class SettingsViewModel(private val repository: SettingsRepository) : ViewModel() {

    val uiState: StateFlow<SettingsUiState> = combine(
        repository.darkMode,
        repository.fontSize
    ) { darkMode, fontSize ->
        SettingsUiState(darkMode = darkMode, fontSize = fontSize)
    }.stateIn(viewModelScope, SharingStarted.WhileSubscribed(5000), SettingsUiState())

    fun toggleDarkMode() {
        viewModelScope.launch {
            repository.setDarkMode(!uiState.value.darkMode)
        }
    }
}

data class SettingsUiState(
    val darkMode: Boolean = false,
    val fontSize: Int = 14
)
```

## 3. Proto DataStore

```protobuf
// app/src/main/proto/user_prefs.proto
syntax = "proto3";
option java_package = "com.example.app";
message UserPrefs {
    string theme = 1;
    int32 font_size = 2;
    bool notifications_enabled = 3;
}
```

```kotlin
// Serializer
object UserPrefsSerializer : Serializer<UserPrefs> {
    override val defaultValue: UserPrefs = UserPrefs.getDefaultInstance()

    override suspend fun readFrom(input: InputStream): UserPrefs =
        try { UserPrefs.parseFrom(input) }
        catch (e: InvalidProtocolBufferException) { throw CorruptionException("Cannot read proto", e) }

    override suspend fun writeTo(t: UserPrefs, output: OutputStream) = t.writeTo(output)
}

// 创建 Proto DataStore
val Context.userPrefsStore by dataStore(
    fileName = "user_prefs.pb",
    serializer = UserPrefsSerializer
)

// 读写
class UserPrefsRepository(private val dataStore: DataStore<UserPrefs>) {
    val prefs: Flow<UserPrefs> = dataStore.data

    suspend fun updateTheme(theme: String) {
        dataStore.updateData { it.toBuilder().setTheme(theme).build() }
    }
}
```

## 4. 从 SharedPreferences 迁移

```kotlin
val Context.dataStore by preferencesDataStore(
    name = "settings",
    produceMigrations = { context ->
        listOf(SharedPreferencesMigration(context, "old_shared_prefs"))
    }
)

// 迁移完成后旧 SharedPreferences 文件自动删除
```
