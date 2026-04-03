# Vue3 高级特性
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. Teleport

```vue
<!-- 将内容渲染到 DOM 的其他位置（如 body） -->
<template>
  <button @click="showModal = true">打开弹窗</button>
  <Teleport to="body">
    <div v-if="showModal" class="modal-overlay">
      <div class="modal">
        <h2>弹窗标题</h2>
        <button @click="showModal = false">关闭</button>
      </div>
    </div>
  </Teleport>
</template>
```

## 2. Suspense

```vue
<!-- 异步组件加载状态 -->
<template>
  <Suspense>
    <template #default>
      <AsyncComponent />
    </template>
    <template #fallback>
      <div>加载中...</div>
    </template>
  </Suspense>
</template>

<!-- AsyncComponent.vue（setup 中使用 await） -->
<script setup>
const data = await fetch('/api/data').then(r => r.json());
</script>
```

## 3. 自定义指令

```javascript
// 全局注册
app.directive('focus', {
  mounted(el) { el.focus(); },
});

// 局部注册（setup 中以 v 开头命名）
const vClickOutside = {
  mounted(el, binding) {
    el._clickOutside = (e) => {
      if (!el.contains(e.target)) binding.value(e);
    };
    document.addEventListener('click', el._clickOutside);
  },
  unmounted(el) {
    document.removeEventListener('click', el._clickOutside);
  },
};

// 使用
<input v-focus />
<div v-click-outside="closeMenu">菜单内容</div>
```

## 4. Transition 动画

```vue
<template>
  <button @click="show = !show">切换</button>
  <Transition name="fade" mode="out-in">
    <div v-if="show" key="content">内容</div>
  </Transition>

  <!-- 列表过渡 -->
  <TransitionGroup name="list" tag="ul">
    <li v-for="item in items" :key="item.id">{{ item.name }}</li>
  </TransitionGroup>
</template>

<style>
.fade-enter-active, .fade-leave-active { transition: opacity 0.3s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }

.list-enter-active, .list-leave-active { transition: all 0.5s ease; }
.list-enter-from, .list-leave-to { opacity: 0; transform: translateX(30px); }
.list-move { transition: transform 0.5s ease; }
</style>
```

## 5. KeepAlive

```vue
<!-- 缓存组件状态，避免重复渲染 -->
<template>
  <KeepAlive :include="['Home', 'About']" :max="10">
    <component :is="currentComponent" />
  </KeepAlive>
</template>

<script setup>
import { onActivated, onDeactivated } from 'vue';

// KeepAlive 专属生命周期
onActivated(() => { console.log('组件被激活'); });
onDeactivated(() => { console.log('组件被缓存'); });
</script>
```

## 6. 异步组件

```javascript
import { defineAsyncComponent } from 'vue';

const AsyncComp = defineAsyncComponent({
  loader: () => import('./HeavyComponent.vue'),
  loadingComponent: LoadingSpinner,
  errorComponent: ErrorDisplay,
  delay: 200,      // 延迟显示 loading（ms）
  timeout: 10000,  // 超时时间（ms）
});
```

## 7. 插件开发

```javascript
// plugins/toast.js
export const toastPlugin = {
  install(app, options = {}) {
    const toast = reactive({ message: '', visible: false });

    app.config.globalProperties.$toast = (msg) => {
      toast.message = msg;
      toast.visible = true;
      setTimeout(() => { toast.visible = false; }, options.duration || 3000);
    };

    app.provide('toast', toast);
  },
};

// main.js
app.use(toastPlugin, { duration: 5000 });
```
