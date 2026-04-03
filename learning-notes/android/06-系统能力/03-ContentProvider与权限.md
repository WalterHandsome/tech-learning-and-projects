# ContentProvider 与权限
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. ContentProvider 基础

```kotlin
class NoteProvider : ContentProvider() {
    private lateinit var db: AppDatabase

    companion object {
        const val AUTHORITY = "com.example.app.provider"
        val CONTENT_URI: Uri = Uri.parse("content://$AUTHORITY/notes")
    }

    override fun onCreate(): Boolean {
        db = Room.databaseBuilder(context!!, AppDatabase::class.java, "notes.db").build()
        return true
    }

    override fun query(uri: Uri, projection: Array<String>?, selection: String?,
                       selectionArgs: Array<String>?, sortOrder: String?): Cursor {
        val cursor = db.openHelper.readableDatabase
            .query("SELECT * FROM notes ORDER BY ${sortOrder ?: "id DESC"}")
        cursor.setNotificationUri(context!!.contentResolver, uri)
        return cursor
    }

    override fun insert(uri: Uri, values: ContentValues?): Uri {
        val id = db.openHelper.writableDatabase
            .insert("notes", SQLiteDatabase.CONFLICT_REPLACE, values!!)
        context!!.contentResolver.notifyChange(uri, null)
        return ContentUris.withAppendedId(CONTENT_URI, id)
    }

    override fun update(uri: Uri, values: ContentValues?, sel: String?, args: Array<String>?) = 0
    override fun delete(uri: Uri, sel: String?, args: Array<String>?) = 0
    override fun getType(uri: Uri) = "vnd.android.cursor.dir/vnd.example.notes"
}
```

## 2. 运行时权限

```kotlin
// Compose 方式
@Composable
fun CameraScreen() {
    val cameraPermissionState = rememberPermissionState(Manifest.permission.CAMERA)

    when {
        cameraPermissionState.status.isGranted -> CameraPreview()
        cameraPermissionState.status.shouldShowRationale -> {
            AlertDialog(
                onDismissRequest = {},
                title = { Text("需要相机权限") },
                text = { Text("拍照功能需要相机权限") },
                confirmButton = {
                    Button(onClick = { cameraPermissionState.launchPermissionRequest() }) {
                        Text("授权")
                    }
                }
            )
        }
        else -> {
            Button(onClick = { cameraPermissionState.launchPermissionRequest() }) {
                Text("请求相机权限")
            }
        }
    }
}

// 多权限
@Composable
fun LocationScreen() {
    val permissionState = rememberMultiplePermissionsState(
        listOf(
            Manifest.permission.ACCESS_FINE_LOCATION,
            Manifest.permission.ACCESS_COARSE_LOCATION
        )
    )

    LaunchedEffect(Unit) {
        if (!permissionState.allPermissionsGranted) {
            permissionState.launchMultiplePermissionRequest()
        }
    }
}
```

## 3. Activity Result API 方式

```kotlin
class PhotoActivity : AppCompatActivity() {
    private val requestPermission = registerForActivityResult(
        ActivityResultContracts.RequestMultiplePermissions()
    ) { permissions ->
        val allGranted = permissions.values.all { it }
        if (allGranted) startCamera()
        else handleDenied(permissions)
    }

    private fun checkAndRequestPermissions() {
        val needed = arrayOf(
            Manifest.permission.CAMERA,
            Manifest.permission.WRITE_EXTERNAL_STORAGE
        ).filter {
            ContextCompat.checkSelfPermission(this, it) != PackageManager.PERMISSION_GRANTED
        }
        if (needed.isEmpty()) startCamera()
        else requestPermission.launch(needed.toTypedArray())
    }
}
```

## 4. FileProvider

```kotlin
// AndroidManifest.xml
// <provider
//     android:name="androidx.core.content.FileProvider"
//     android:authorities="${applicationId}.fileprovider"
//     android:exported="false"
//     android:grantUriPermissions="true">
//     <meta-data
//         android:name="android.support.FILE_PROVIDER_PATHS"
//         android:resource="@xml/file_paths" />
// </provider>

// res/xml/file_paths.xml
// <paths>
//     <external-path name="images" path="Pictures/" />
//     <cache-path name="cache" path="/" />
// </paths>

// 使用 FileProvider 分享文件
fun shareImage(context: Context, file: File) {
    val uri = FileProvider.getUriForFile(
        context, "${context.packageName}.fileprovider", file
    )
    val intent = Intent(Intent.ACTION_SEND).apply {
        type = "image/*"
        putExtra(Intent.EXTRA_STREAM, uri)
        addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)
    }
    context.startActivity(Intent.createChooser(intent, "分享图片"))
}
```
