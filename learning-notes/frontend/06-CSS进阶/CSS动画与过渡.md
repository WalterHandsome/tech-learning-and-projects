# CSS 动画与过渡

## 1. transition 过渡

```css
.button {
  background: #3498db;
  transform: translateY(0);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}
.button:hover {
  background: #2980b9;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}
```

## 2. animation 关键帧

```css
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(20px); }
  to   { opacity: 1; transform: translateY(0); }
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

@keyframes pulse {
  0%, 100% { transform: scale(1); }
  50%      { transform: scale(1.05); }
}

.fade-in {
  animation: fadeIn 0.5s ease-out forwards;
}

.spinner {
  animation: spin 1s linear infinite;
}

.pulse {
  animation: pulse 2s ease-in-out infinite;
}
```

## 3. GPU 加速

```css
/* 触发 GPU 加速的属性（合成层） */
.gpu-accelerated {
  transform: translateZ(0);    /* 或 translate3d(0,0,0) */
  will-change: transform;      /* 提前告知浏览器 */
  /* 优先使用 transform 和 opacity 做动画，避免触发重排 */
}

/* 性能好的动画属性：transform, opacity */
/* 性能差的动画属性：width, height, top, left, margin */
```

## 4. FLIP 动画技术

```javascript
// First: 记录初始位置
// Last: 记录最终位置
// Invert: 计算差值，用 transform 反转到初始位置
// Play: 移除 transform，让元素动画到最终位置

function flipAnimate(element) {
  const first = element.getBoundingClientRect();

  // 触发布局变化
  element.classList.toggle('expanded');

  const last = element.getBoundingClientRect();
  const deltaX = first.left - last.left;
  const deltaY = first.top - last.top;

  element.animate([
    { transform: `translate(${deltaX}px, ${deltaY}px)` },
    { transform: 'translate(0, 0)' },
  ], { duration: 300, easing: 'ease-out' });
}
```

## 5. Web Animations API

```javascript
const element = document.querySelector('.box');

const animation = element.animate([
  { transform: 'translateX(0)', opacity: 1 },
  { transform: 'translateX(300px)', opacity: 0.5 },
], {
  duration: 1000,
  easing: 'ease-in-out',
  iterations: Infinity,
  direction: 'alternate',
  fill: 'forwards',
});

animation.pause();
animation.play();
animation.reverse();
animation.cancel();
animation.finished.then(() => console.log('动画完成'));
```
