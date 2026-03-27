# ES6+ 新特性
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. 解构赋值

```javascript
// 数组解构
const [a, b, ...rest] = [1, 2, 3, 4, 5];
const [x = 0, y = 0] = [1]; // 默认值

// 对象解构
const { name, age, city = '北京' } = user;
const { name: userName } = user; // 重命名

// 嵌套解构
const { address: { street } } = user;

// 函数参数解构
function greet({ name, age = 18 }) {
  return `${name}, ${age}岁`;
}
```

## 2. 模板字符串

```javascript
const name = '张三';
const greeting = `Hello, ${name}`;

// 多行字符串
const html = `
  <div class="card">
    <h2>${title}</h2>
    <p>${content}</p>
  </div>
`;

// 标签模板
function highlight(strings, ...values) {
  return strings.reduce((result, str, i) => {
    return result + str + (values[i] ? `<mark>${values[i]}</mark>` : '');
  }, '');
}
const msg = highlight`Hello ${name}, you are ${age} years old`;
```

## 3. 展开运算符与剩余参数

```javascript
// 展开运算符
const arr = [...arr1, ...arr2];
const obj = { ...obj1, ...obj2, extra: true };

// 剩余参数
function sum(...nums) {
  return nums.reduce((a, b) => a + b, 0);
}
```

## 4. Map / Set / WeakMap / WeakSet

```javascript
// Map（键值对，键可以是任意类型）
const map = new Map();
map.set('key', 'value');
map.set(obj, 'object value');
map.get('key');    // 'value'
map.has('key');    // true
map.delete('key');
map.size;          // 1
for (const [key, value] of map) { /* ... */ }

// Set（唯一值集合）
const set = new Set([1, 2, 3, 2, 1]);
set.add(4);
set.has(3);    // true
set.delete(1);
set.size;      // 3
const unique = [...new Set(array)]; // 数组去重

// WeakMap（键必须是对象，弱引用，不阻止垃圾回收）
const wm = new WeakMap();
wm.set(obj, 'metadata');

// WeakSet（值必须是对象，弱引用）
const ws = new WeakSet();
ws.add(obj);
```

## 5. Proxy / Reflect

```javascript
const handler = {
  get(target, prop, receiver) {
    console.log(`读取 ${prop}`);
    return Reflect.get(target, prop, receiver);
  },
  set(target, prop, value, receiver) {
    console.log(`设置 ${prop} = ${value}`);
    return Reflect.set(target, prop, value, receiver);
  },
  deleteProperty(target, prop) {
    console.log(`删除 ${prop}`);
    return Reflect.deleteProperty(target, prop);
  }
};

const proxy = new Proxy({ name: '张三' }, handler);
proxy.name;        // 读取 name → '张三'
proxy.age = 25;    // 设置 age = 25

// 实际应用：响应式数据（Vue3 原理）
function reactive(obj) {
  return new Proxy(obj, {
    get(target, key, receiver) {
      track(target, key); // 收集依赖
      return Reflect.get(target, key, receiver);
    },
    set(target, key, value, receiver) {
      const result = Reflect.set(target, key, value, receiver);
      trigger(target, key); // 触发更新
      return result;
    }
  });
}
```

## 6. Symbol

```javascript
const s1 = Symbol('description');
const s2 = Symbol('description');
s1 === s2; // false（每个 Symbol 都是唯一的）

// 作为对象属性键（避免命名冲突）
const ID = Symbol('id');
const user = { [ID]: 1, name: '张三' };

// 内置 Symbol
Symbol.iterator   // 定义迭代器
Symbol.toPrimitive // 类型转换
Symbol.hasInstance // instanceof 行为
```

## 7. Iterator 与 for...of

```javascript
// 可迭代协议：实现 [Symbol.iterator] 方法
class Range {
  constructor(start, end) {
    this.start = start;
    this.end = end;
  }
  [Symbol.iterator]() {
    let current = this.start;
    const end = this.end;
    return {
      next() {
        return current <= end
          ? { value: current++, done: false }
          : { done: true };
      }
    };
  }
}

for (const num of new Range(1, 5)) {
  console.log(num); // 1, 2, 3, 4, 5
}
```

## 8. 可选链与空值合并

```javascript
// 可选链 ?.
const street = user?.address?.street;
const first = arr?.[0];
const result = obj?.method?.();

// 空值合并 ??（仅 null/undefined 时取默认值）
const name = user.name ?? '匿名';
const count = data.count ?? 0;

// 对比 ||（所有假值都会取默认值）
0 || 10;    // 10
0 ?? 10;    // 0
'' || '默认'; // '默认'
'' ?? '默认'; // ''
```

## 9. 模块化

```javascript
// 命名导出
export const PI = 3.14;
export function add(a, b) { return a + b; }
export class Calculator { /* ... */ }

// 默认导出
export default function main() { /* ... */ }

// 命名导入
import { PI, add } from './math.js';
import { add as sum } from './math.js'; // 重命名

// 默认导入
import main from './main.js';

// 全部导入
import * as math from './math.js';

// 动态导入（代码分割）
const module = await import('./heavy-module.js');
```
## 🎬 推荐视频资源

- [Traversy Media - JavaScript Crash Course](https://www.youtube.com/watch?v=hdI2bqOjy3c) — JavaScript速成
- [freeCodeCamp - JavaScript Full Course](https://www.youtube.com/watch?v=PkZNo7MFNFg) — JavaScript完整课程
- [Fireship - JavaScript in 100 Seconds](https://www.youtube.com/watch?v=DHjqpvDnNGE) — JavaScript快速了解
