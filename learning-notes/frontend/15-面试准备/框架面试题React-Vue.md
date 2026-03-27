# 框架面试题 React / Vue
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. React 面试题

### 虚拟 DOM 与 Diff 算法

```
虚拟 DOM：用 JS 对象描述 DOM 结构，减少直接操作真实 DOM

Diff 策略（O(n)）：
1. 同层比较，不跨层级
2. 不同类型的元素 → 销毁重建
3. 通过 key 标识同一元素（列表优化）

React Fiber：
- 将渲染工作拆分为多个小任务
- 可中断、可恢复、可设优先级
- 实现时间切片（Time Slicing）
- 支持并发模式（Concurrent Mode）
```

### Hooks 原理

```
- Hooks 依赖调用顺序（链表结构）
- 不能在条件语句中使用 Hook（破坏顺序）
- useState 通过闭包保存状态
- useEffect 在 commit 阶段异步执行
- useLayoutEffect 在 DOM 更新后同步执行
```

### 常见问题

```
Q: React 中 key 的作用？
A: 帮助 Diff 算法识别列表中哪些元素变化了，避免不必要的销毁重建。
   不要用 index 作为 key（列表顺序变化时会出问题）。

Q: setState 是同步还是异步？
A: React 18 中，所有 setState 都是批量异步更新（自动批处理）。
   如果需要同步获取更新后的值，使用 flushSync。

Q: useEffect 和 useLayoutEffect 的区别？
A: useEffect 异步执行，不阻塞渲染；
   useLayoutEffect 同步执行，在 DOM 更新后、浏览器绘制前执行。
   需要读取 DOM 布局信息时用 useLayoutEffect。

Q: React.memo、useMemo、useCallback 的区别？
A: React.memo — 组件级别，浅比较 props
   useMemo — 缓存计算结果
   useCallback — 缓存函数引用
```

## 2. Vue 面试题

### 响应式原理

```
Vue 2：Object.defineProperty
  - 劫持对象属性的 getter/setter
  - 缺点：无法检测属性新增/删除、数组索引变化

Vue 3：Proxy
  - 代理整个对象
  - 支持属性新增/删除、数组操作
  - 惰性响应式（访问时才递归代理）

依赖收集：
  - 读取数据时（getter）→ track 收集依赖
  - 修改数据时（setter）→ trigger 触发更新
```

### Diff 算法

```
Vue 3 Diff（双端 + 最长递增子序列）：
1. 从头部开始比较相同节点
2. 从尾部开始比较相同节点
3. 处理新增节点
4. 处理删除节点
5. 处理乱序节点（最长递增子序列优化移动次数）
```

### 常见问题

```
Q: computed 和 watch 的区别？
A: computed — 有缓存，依赖不变不重新计算，适合派生数据
   watch — 无缓存，适合执行副作用（API 调用、DOM 操作）

Q: v-if 和 v-show 的区别？
A: v-if — 条件渲染，切换时销毁/重建 DOM
   v-show — display 切换，DOM 始终存在
   频繁切换用 v-show，条件很少变化用 v-if

Q: nextTick 的原理？
A: Vue 异步更新 DOM，nextTick 在 DOM 更新后执行回调。
   内部使用 Promise.then（微任务）实现。

Q: Composition API vs Options API？
A: Composition API 更好的逻辑复用（composables）、更好的 TypeScript 支持、
   更灵活的代码组织。Options API 更直观，适合简单组件。
```

## 3. 通用框架问题

```
Q: 虚拟 DOM 一定比直接操作 DOM 快吗？
A: 不一定。虚拟 DOM 的优势是：
   1. 批量更新，减少 DOM 操作次数
   2. 跨平台（SSR、Native）
   3. 声明式编程，开发体验好
   对于简单的单次 DOM 操作，直接操作更快。

Q: SSR 的优缺点？
A: 优点：首屏快、SEO 好
   缺点：服务器压力大、开发复杂度高、部分浏览器 API 不可用

Q: 如何选择 React 还是 Vue？
A: React — 大型项目、灵活度高、生态丰富、函数式编程
   Vue — 上手快、模板语法直观、官方工具链完善、渐进式
```
