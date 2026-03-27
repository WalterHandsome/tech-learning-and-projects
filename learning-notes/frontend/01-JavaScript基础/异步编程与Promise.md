# 异步编程与 Promise

> Author: Walter Wang

## 1. 事件循环（Event Loop）

```
┌───────────────────────┐
│      调用栈 (Call Stack)  │
└───────────┬───────────┘
            │
            ▼
┌───────────────────────┐
│    微任务队列 (Microtask)  │  ← Promise.then, queueMicrotask, MutationObserver
└───────────┬───────────┘
            │
            ▼
┌───────────────────────┐
│    宏任务队列 (Macrotask)  │  ← setTimeout, setInterval, I/O, UI渲染
└───────────────────────┘

执行顺序：同步代码 → 微任务 → 宏任务（循环）
```

```javascript
console.log('1');                    // 同步
setTimeout(() => console.log('2'), 0); // 宏任务
Promise.resolve().then(() => console.log('3')); // 微任务
console.log('4');                    // 同步
// 输出：1, 4, 3, 2
```

## 2. Promise

### 2.1 基本用法

```javascript
const promise = new Promise((resolve, reject) => {
  // 异步操作
  setTimeout(() => {
    const success = true;
    if (success) {
      resolve('成功数据');
    } else {
      reject(new Error('失败原因'));
    }
  }, 1000);
});

promise
  .then(data => console.log(data))
  .catch(err => console.error(err))
  .finally(() => console.log('完成'));
```

### 2.2 链式调用

```javascript
fetch('/api/user')
  .then(res => res.json())
  .then(user => fetch(`/api/posts?userId=${user.id}`))
  .then(res => res.json())
  .then(posts => console.log(posts))
  .catch(err => console.error(err));
```

### 2.3 静态方法

```javascript
// Promise.all：全部成功才成功，一个失败就失败
const results = await Promise.all([
  fetch('/api/users'),
  fetch('/api/posts'),
  fetch('/api/comments'),
]);

// Promise.allSettled：等待全部完成，不管成功失败
const results = await Promise.allSettled([p1, p2, p3]);
// [{ status: 'fulfilled', value: ... }, { status: 'rejected', reason: ... }]

// Promise.race：返回最先完成的（成功或失败）
const result = await Promise.race([fetchData(), timeout(5000)]);

// Promise.any：返回最先成功的，全部失败才失败
const result = await Promise.any([source1(), source2(), source3()]);
```

## 3. async / await

```javascript
// async 函数返回 Promise
async function fetchUser(id) {
  try {
    const res = await fetch(`/api/users/${id}`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const user = await res.json();
    return user;
  } catch (err) {
    console.error('获取用户失败:', err);
    throw err;
  }
}

// 并发请求
async function fetchAll() {
  const [users, posts] = await Promise.all([
    fetch('/api/users').then(r => r.json()),
    fetch('/api/posts').then(r => r.json()),
  ]);
  return { users, posts };
}

// 顺序执行
async function sequential(urls) {
  const results = [];
  for (const url of urls) {
    const res = await fetch(url);
    results.push(await res.json());
  }
  return results;
}

// 控制并发数
async function concurrentLimit(tasks, limit) {
  const results = [];
  const executing = new Set();

  for (const task of tasks) {
    const p = task().then(result => {
      executing.delete(p);
      return result;
    });
    executing.add(p);
    results.push(p);

    if (executing.size >= limit) {
      await Promise.race(executing);
    }
  }
  return Promise.all(results);
}
```

## 4. 手写 Promise（简化版）

```javascript
class MyPromise {
  constructor(executor) {
    this.state = 'pending';
    this.value = undefined;
    this.callbacks = [];

    const resolve = (value) => {
      if (this.state !== 'pending') return;
      this.state = 'fulfilled';
      this.value = value;
      this.callbacks.forEach(cb => cb.onFulfilled(value));
    };

    const reject = (reason) => {
      if (this.state !== 'pending') return;
      this.state = 'rejected';
      this.value = reason;
      this.callbacks.forEach(cb => cb.onRejected(reason));
    };

    try { executor(resolve, reject); }
    catch (err) { reject(err); }
  }

  then(onFulfilled, onRejected) {
    return new MyPromise((resolve, reject) => {
      const handle = (callback, fallback) => {
        try {
          const fn = typeof callback === 'function' ? callback : fallback;
          resolve(fn(this.value));
        } catch (err) { reject(err); }
      };

      if (this.state === 'fulfilled') {
        queueMicrotask(() => handle(onFulfilled, v => v));
      } else if (this.state === 'rejected') {
        queueMicrotask(() => handle(onRejected, e => { throw e; }));
      } else {
        this.callbacks.push({
          onFulfilled: () => handle(onFulfilled, v => v),
          onRejected: () => handle(onRejected, e => { throw e; }),
        });
      }
    });
  }

  catch(onRejected) { return this.then(null, onRejected); }
}
```
