# Service 与广播接收器

> Author: Walter Wang

## 1. Started Service

```kotlin
class DownloadService : Service() {
    private val scope = CoroutineScope(Dispatchers.IO + SupervisorJob())

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        val url = intent?.getStringExtra("url") ?: return START_NOT_STICKY
        scope.launch {
            downloadFile(url)
            stopSelf(startId)
        }
        return START_REDELIVER_INTENT  // 被杀后重新传递 Intent
    }

    override fun onBind(intent: Intent?): IBinder? = null

    override fun onDestroy() {
        scope.cancel()
        super.onDestroy()
    }
}

// 启动
context.startService(Intent(context, DownloadService::class.java).apply {
    putExtra("url", "https://example.com/file.zip")
})
```

## 2. Bound Service

```kotlin
class MusicService : Service() {
    private val binder = MusicBinder()
    private var mediaPlayer: MediaPlayer? = null

    inner class MusicBinder : Binder() {
        fun getService(): MusicService = this@MusicService
    }

    override fun onBind(intent: Intent): IBinder = binder

    fun play(uri: Uri) {
        mediaPlayer = MediaPlayer.create(this, uri).apply { start() }
    }

    fun pause() { mediaPlayer?.pause() }
    fun stop() { mediaPlayer?.stop(); mediaPlayer?.release() }
}

// 绑定
class MusicActivity : AppCompatActivity() {
    private var musicService: MusicService? = null
    private val connection = object : ServiceConnection {
        override fun onServiceConnected(name: ComponentName, service: IBinder) {
            musicService = (service as MusicService.MusicBinder).getService()
        }
        override fun onServiceDisconnected(name: ComponentName) { musicService = null }
    }

    override fun onStart() {
        super.onStart()
        bindService(Intent(this, MusicService::class.java), connection, BIND_AUTO_CREATE)
    }

    override fun onStop() {
        unbindService(connection)
        super.onStop()
    }
}
```

## 3. 前台 Service

```kotlin
class LocationService : Service() {
    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        val notification = NotificationCompat.Builder(this, "location_channel")
            .setContentTitle("位置追踪中")
            .setSmallIcon(R.drawable.ic_location)
            .setOngoing(true)
            .build()

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
            startForeground(1, notification, ServiceInfo.FOREGROUND_SERVICE_TYPE_LOCATION)
        } else {
            startForeground(1, notification)
        }
        startLocationUpdates()
        return START_STICKY
    }

    override fun onBind(intent: Intent?): IBinder? = null
}

// AndroidManifest.xml
// <service android:name=".LocationService"
//     android:foregroundServiceType="location"
//     android:exported="false" />
```

## 4. BroadcastReceiver

```kotlin
// 静态注册（AndroidManifest.xml）
class BootReceiver : BroadcastReceiver() {
    override fun onReceive(context: Context, intent: Intent) {
        if (intent.action == Intent.ACTION_BOOT_COMPLETED) {
            // 开机启动任务
            WorkManager.getInstance(context).enqueue(syncWorkRequest)
        }
    }
}

// 动态注册
class NetworkFragment : Fragment() {
    private val networkReceiver = object : BroadcastReceiver() {
        override fun onReceive(context: Context, intent: Intent) {
            val isConnected = isNetworkAvailable(context)
            updateUI(isConnected)
        }
    }

    override fun onStart() {
        super.onStart()
        val filter = IntentFilter(ConnectivityManager.CONNECTIVITY_ACTION)
        requireContext().registerReceiver(networkReceiver, filter)
    }

    override fun onStop() {
        requireContext().unregisterReceiver(networkReceiver)
        super.onStop()
    }
}

// 发送本地广播
LocalBroadcastManager.getInstance(context)
    .sendBroadcast(Intent("com.example.DATA_UPDATED"))
```
