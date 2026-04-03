# Node.js 性能优化
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. 内存泄漏排查

```javascript
// 使用 --inspect 启动
// node --inspect server.js
// Chrome DevTools → Memory → Heap Snapshot

// 常见内存泄漏原因
// 1. 全局变量累积
// 2. 闭包引用未释放
// 3. 事件监听器未移除
// 4. 定时器未清理
// 5. 大数组/对象缓存无上限

// 使用 LRU 缓存限制大小
import { LRUCache } from 'lru-cache';
const cache = new LRUCache({ max: 500, ttl: 1000 * 60 * 5 });
```

## 2. Worker Threads

```javascript
// CPU 密集型任务使用 Worker Threads
import { Worker } from 'node:worker_threads';

function runWorker(data) {
  return new Promise((resolve, reject) => {
    const worker = new Worker('./heavy-task.js', { workerData: data });
    worker.on('message', resolve);
    worker.on('error', reject);
  });
}

// 使用 worker pool（piscina）
import Piscina from 'piscina';
const pool = new Piscina({ filename: './worker.js', maxThreads: 4 });
const result = await pool.run({ data: 'input' });
```

## 3. Stream 流式处理

```javascript
// 避免一次性加载大文件到内存
import { createReadStream } from 'node:fs';
import { pipeline } from 'node:stream/promises';

// 流式响应
app.get('/api/export', async (req, res) => {
  res.setHeader('Content-Type', 'text/csv');
  const cursor = db.collection('users').find().stream();
  cursor.pipe(new CSVTransform()).pipe(res);
});
```

## 4. PM2 进程管理

```javascript
// ecosystem.config.js
module.exports = {
  apps: [{
    name: 'api',
    script: 'dist/server.js',
    instances: 'max',     // 使用所有 CPU 核心
    exec_mode: 'cluster',
    max_memory_restart: '1G',
    env_production: {
      NODE_ENV: 'production',
      PORT: 3000,
    },
  }],
};
```

```bash
pm2 start ecosystem.config.js --env production
pm2 monit     # 监控
pm2 logs      # 查看日志
pm2 reload all # 零停机重启
```
