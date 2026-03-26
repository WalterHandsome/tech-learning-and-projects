# WorkManager 后台任务

## 1. 基本 Worker

```kotlin
class UploadWorker(
    context: Context,
    params: WorkerParameters
) : CoroutineWorker(context, params) {

    override suspend fun doWork(): Result {
        val imageUri = inputData.getString("image_uri") ?: return Result.failure()

        return try {
            val url = uploadImage(imageUri)
            val output = workDataOf("uploaded_url" to url)
            Result.success(output)
        } catch (e: Exception) {
            if (runAttemptCount < 3) Result.retry() else Result.failure()
        }
    }
}
```

## 2. OneTimeWorkRequest

```kotlin
val uploadWork = OneTimeWorkRequestBuilder<UploadWorker>()
    .setInputData(workDataOf("image_uri" to uri.toString()))
    .setConstraints(
        Constraints.Builder()
            .setRequiredNetworkType(NetworkType.CONNECTED)
            .setRequiresBatteryNotLow(true)
            .build()
    )
    .setBackoffCriteria(BackoffPolicy.EXPONENTIAL, 30, TimeUnit.SECONDS)
    .addTag("upload")
    .build()

WorkManager.getInstance(context).enqueue(uploadWork)
```

## 3. PeriodicWorkRequest

```kotlin
val syncWork = PeriodicWorkRequestBuilder<SyncWorker>(
    repeatInterval = 1, repeatIntervalTimeUnit = TimeUnit.HOURS,
    flexTimeInterval = 15, flexTimeIntervalUnit = TimeUnit.MINUTES
)
    .setConstraints(
        Constraints.Builder().setRequiredNetworkType(NetworkType.CONNECTED).build()
    )
    .build()

// 唯一任务（避免重复）
WorkManager.getInstance(context).enqueueUniquePeriodicWork(
    "sync_data",
    ExistingPeriodicWorkPolicy.KEEP,
    syncWork
)
```

## 4. 任务链

```kotlin
WorkManager.getInstance(context)
    .beginWith(listOf(downloadWork1, downloadWork2))  // 并行
    .then(processWork)                                  // 串行
    .then(uploadWork)                                   // 串行
    .enqueue()

// 唯一任务链
WorkManager.getInstance(context)
    .beginUniqueWork("import_flow", ExistingWorkPolicy.REPLACE, downloadWork)
    .then(parseWork)
    .then(saveWork)
    .enqueue()
```

## 5. 观察任务状态

```kotlin
// ViewModel 中观察
class UploadViewModel(application: Application) : AndroidViewModel(application) {
    private val workManager = WorkManager.getInstance(application)

    fun startUpload(uri: String) {
        val request = OneTimeWorkRequestBuilder<UploadWorker>()
            .setInputData(workDataOf("image_uri" to uri))
            .build()
        workManager.enqueue(request)
    }

    // 通过 ID 观察
    fun getWorkInfo(id: UUID): LiveData<WorkInfo> =
        workManager.getWorkInfoByIdLiveData(id)

    // 通过 Tag 观察
    val uploadProgress: LiveData<List<WorkInfo>> =
        workManager.getWorkInfosByTagLiveData("upload")
}

// Compose 中观察
@Composable
fun UploadStatus(workId: UUID) {
    val workInfo = WorkManager.getInstance(LocalContext.current)
        .getWorkInfoByIdLiveData(workId)
        .observeAsState()

    when (workInfo.value?.state) {
        WorkInfo.State.RUNNING -> CircularProgressIndicator()
        WorkInfo.State.SUCCEEDED -> {
            val url = workInfo.value?.outputData?.getString("uploaded_url")
            Text("上传成功: $url")
        }
        WorkInfo.State.FAILED -> Text("上传失败")
        else -> {}
    }
}
```

## 6. 前台 Worker（长时间任务）

```kotlin
class LongUploadWorker(context: Context, params: WorkerParameters)
    : CoroutineWorker(context, params) {

    override suspend fun getForegroundInfo(): ForegroundInfo {
        val notification = NotificationCompat.Builder(applicationContext, "upload_channel")
            .setContentTitle("正在上传")
            .setSmallIcon(R.drawable.ic_upload)
            .setProgress(100, 0, true)
            .build()
        return ForegroundInfo(NOTIFICATION_ID, notification)
    }

    override suspend fun doWork(): Result {
        setForeground(getForegroundInfo())
        // 执行长时间任务...
        return Result.success()
    }
}
```
