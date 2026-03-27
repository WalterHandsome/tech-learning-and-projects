# JavaScript 高频面试题
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. 数据类型

```javascript
// typeof null === 'object' 的原因？
// 历史遗留 bug，JS 最初用 32 位表示值，低 3 位表示类型，000 表示对象，null 全为 0

// [] == false 为什么是 true？
// [] → '' → 0, false → 0, 0 == 0 → true

// 0.1 + 0.2 !== 0.3 的原因？
// IEEE 754 浮点数精度问题
// 解决：Math.abs(0.1 + 0.2 - 0.3) < Number.EPSILON
```

## 2. 手写题

```javascript
// 防抖
function debounce(fn, delay) {
  let timer;
  return function(...args) {
    clearTimeout(timer);
    timer = setTimeout(() => fn.apply(this, args), delay);
  };
}

// 节流
function throttle(fn, interval) {
  let lastTime = 0;
  return function(...args) {
    const now = Date.now();
    if (now - lastTime >= interval) {
      lastTime = now;
      fn.apply(this, args);
    }
  };
}

// 深拷贝
function deepClone(obj, map = new WeakMap()) {
  if (obj === null || typeof obj !== 'object') return obj;
  if (obj instanceof Date) return new Date(obj);
  if (obj instanceof RegExp) return new RegExp(obj);
  if (map.has(obj)) return map.get(obj);
  const clone = Array.isArray(obj) ? [] : {};
  map.set(obj, clone);
  for (const key of Object.keys(obj)) {
    clone[key] = deepClone(obj[key], map);
  }
  return clone;
}

// Promise.all
function promiseAll(promises) {
  return new Promise((resolve, reject) => {
    const results = [];
    let count = 0;
    promises.forEach((p, i) => {
      Promise.resolve(p).then(
        (value) => {
          results[i] = value;
          if (++count === promises.length) resolve(results);
        },
        reject
      );
    });
  });
}

// 柯里化
function curry(fn) {
  return function curried(...args) {
    if (args.length >= fn.length) return fn.apply(this, args);
    return (...moreArgs) => curried(...args, ...moreArgs);
  };
}

// 发布订阅
class EventEmitter {
  constructor() { this.events = {}; }
  on(event, fn) {
    (this.events[event] ||= []).push(fn);
    return this;
  }
  off(event, fn) {
    this.events[event] = this.events[event]?.filter(f => f !== fn);
    return this;
  }
  emit(event, ...args) {
    this.events[event]?.forEach(fn => fn(...args));
    return this;
  }
  once(event, fn) {
    const wrapper = (...args) => { fn(...args); this.off(event, wrapper); };
    return this.on(event, wrapper);
  }
}

// new 操作符
function myNew(Constructor, ...args) {
  const obj = Object.create(Constructor.prototype);
  const result = Constructor.apply(obj, args);
  return result instanceof Object ? result : obj;
}

// instanceof
function myInstanceof(obj, Constructor) {
  let proto = Object.getPrototypeOf(obj);
  while (proto) {
    if (proto === Constructor.prototype) return true;
    proto = Object.getPrototypeOf(proto);
  }
  return false;
}

// 数组扁平化
function flatten(arr, depth = Infinity) {
  return depth > 0
    ? arr.reduce((acc, val) =>
        acc.concat(Array.isArray(val) ? flatten(val, depth - 1) : val), [])
    : arr.slice();
}
// 或 arr.flat(Infinity)

// 数组去重
const unique = (arr) => [...new Set(arr)];
```

## 3. 闭包与作用域

```javascript
// 经典题
for (var i = 0; i < 5; i++) {
  setTimeout(() => console.log(i), 0);
}
// 输出：5 5 5 5 5
// 解决：let / IIFE / setTimeout 第三个参数

// 事件循环
console.log('1');
setTimeout(() => console.log('2'), 0);
Promise.resolve().then(() => console.log('3'));
Promise.resolve().then(() => {
  console.log('4');
  setTimeout(() => console.log('5'), 0);
});
console.log('6');
// 输出：1 6 3 4 2 5
```
