# CSS3 核心特性
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. 选择器

### 1.1 属性选择器

```css
/* 存在属性 */
[title] { color: red; }

/* 属性值等于 */
[type="text"] { border: 1px solid #ccc; }

/* 属性值以...开头 */
[href^="https"] { color: green; }

/* 属性值以...结尾 */
[href$=".pdf"] { color: red; }

/* 属性值包含... */
[class*="btn"] { cursor: pointer; }
```

### 1.2 伪类选择器

```css
/* 结构伪类 */
:first-child      /* 第一个子元素 */
:last-child       /* 最后一个子元素 */
:nth-child(n)     /* 第n个子元素 */
:nth-child(2n)    /* 偶数子元素 */
:nth-child(2n+1)  /* 奇数子元素 */
:nth-of-type(n)   /* 同类型第n个 */
:not(selector)    /* 排除选择器 */
:empty            /* 空元素 */

/* 状态伪类 */
:hover    /* 鼠标悬停 */
:focus    /* 获得焦点 */
:active   /* 激活状态 */
:checked  /* 选中状态 */
:disabled /* 禁用状态 */
:valid    /* 验证通过 */
:invalid  /* 验证失败 */

/* 链接伪类 */
:link     /* 未访问 */
:visited  /* 已访问 */
```

### 1.3 伪元素

```css
::before    /* 元素前插入内容 */
::after     /* 元素后插入内容 */
::first-line   /* 第一行 */
::first-letter /* 首字母 */
::selection    /* 选中文本 */
::placeholder  /* 占位符文本 */

/* 示例：清除浮动 */
.clearfix::after {
  content: '';
  display: block;
  clear: both;
}

/* 示例：装饰性元素 */
.title::before {
  content: '📌';
  margin-right: 8px;
}
```

## 2. 盒模型

### 2.1 标准盒模型 vs IE 盒模型

```css
/* 标准盒模型：width = 内容宽度 */
.standard {
  box-sizing: content-box; /* 默认 */
  width: 200px;
  padding: 20px;
  border: 1px solid #ccc;
  /* 实际宽度 = 200 + 20*2 + 1*2 = 242px */
}

/* IE 盒模型：width = 内容 + padding + border */
.border-box {
  box-sizing: border-box; /* 推荐 */
  width: 200px;
  padding: 20px;
  border: 1px solid #ccc;
  /* 实际宽度 = 200px */
}

/* 全局设置（推荐） */
*, *::before, *::after {
  box-sizing: border-box;
}
```

### 2.2 margin 合并与塌陷

```css
/* 相邻兄弟元素 margin 合并：取较大值 */
.box1 { margin-bottom: 20px; }
.box2 { margin-top: 30px; }
/* 实际间距 = 30px（不是50px） */

/* 父子元素 margin 塌陷解决方案 */
.parent {
  /* 方案1：overflow */
  overflow: hidden;

  /* 方案2：border */
  border-top: 1px solid transparent;

  /* 方案3：padding 代替子元素 margin */
  padding-top: 20px;
}
```

## 3. BFC（块级格式化上下文）

### 3.1 触发 BFC 的条件

```css
/* 以下属性会创建 BFC */
overflow: hidden | auto | scroll;
display: flow-root;  /* 最佳方案 */
display: flex | inline-flex;
display: grid | inline-grid;
float: left | right;
position: absolute | fixed;
```

### 3.2 BFC 的作用

```css
/* 1. 解决 margin 塌陷 */
.parent {
  display: flow-root;
}

/* 2. 清除浮动 */
.container {
  display: flow-root; /* 包含浮动子元素 */
}

/* 3. 阻止元素被浮动元素覆盖 */
.sidebar { float: left; width: 200px; }
.content { display: flow-root; } /* 不会环绕 sidebar */
```

## 4. 层叠上下文与 z-index

```css
/* 层叠顺序（从低到高）：
   1. 背景和边框
   2. 负 z-index
   3. 块级元素
   4. 浮动元素
   5. 行内元素
   6. z-index: 0 / auto
   7. 正 z-index
*/

/* 创建层叠上下文的条件 */
.stacking-context {
  position: relative; /* + z-index 非 auto */
  z-index: 1;

  /* 或者以下属性也会创建 */
  opacity: 0.99;          /* opacity < 1 */
  transform: translateZ(0); /* transform 非 none */
  filter: blur(0);         /* filter 非 none */
  isolation: isolate;
}
```

## 5. 定位方案

```css
/* 静态定位（默认） */
.static { position: static; }

/* 相对定位（相对自身原位置偏移，不脱离文档流） */
.relative {
  position: relative;
  top: 10px;
  left: 20px;
}

/* 绝对定位（相对最近的定位祖先，脱离文档流） */
.absolute {
  position: absolute;
  top: 0;
  right: 0;
}

/* 固定定位（相对视口，脱离文档流） */
.fixed {
  position: fixed;
  bottom: 20px;
  right: 20px;
}

/* 粘性定位（滚动到阈值时固定） */
.sticky {
  position: sticky;
  top: 0; /* 滚动到顶部时固定 */
}
```

## 6. CSS3 新特性

### 6.1 圆角与阴影

```css
.card {
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  /* box-shadow: x偏移 y偏移 模糊半径 扩展半径 颜色 */
}

.text {
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
}
```

### 6.2 渐变

```css
/* 线性渐变 */
.linear {
  background: linear-gradient(to right, #3498db, #2ecc71);
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

/* 径向渐变 */
.radial {
  background: radial-gradient(circle, #3498db, #2c3e50);
}

/* 锥形渐变 */
.conic {
  background: conic-gradient(red, yellow, green, blue, red);
}
```

### 6.3 变换 transform

```css
.transform {
  transform: translate(50px, 100px);  /* 平移 */
  transform: rotate(45deg);           /* 旋转 */
  transform: scale(1.5);              /* 缩放 */
  transform: skew(10deg, 20deg);      /* 倾斜 */

  /* 组合变换 */
  transform: translate(-50%, -50%) rotate(45deg) scale(1.2);

  /* 3D 变换 */
  transform: perspective(500px) rotateY(30deg);
  transform-origin: center center;    /* 变换原点 */
}
```

### 6.4 过渡 transition

```css
.button {
  background: #3498db;
  transition: all 0.3s ease;
  /* transition: 属性 时长 缓动函数 延迟 */
  /* 缓动函数：ease | linear | ease-in | ease-out | ease-in-out | cubic-bezier() */
}

.button:hover {
  background: #2980b9;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}
```

### 6.5 CSS 变量（自定义属性）

```css
:root {
  --primary-color: #3498db;
  --secondary-color: #2ecc71;
  --font-size-base: 16px;
  --spacing-unit: 8px;
  --border-radius: 4px;
}

.button {
  background: var(--primary-color);
  font-size: var(--font-size-base);
  padding: calc(var(--spacing-unit) * 2) calc(var(--spacing-unit) * 3);
  border-radius: var(--border-radius);
}

/* 暗色主题 */
[data-theme="dark"] {
  --primary-color: #2980b9;
  --bg-color: #1a1a2e;
  --text-color: #eee;
}
```

## 7. CSS 函数

```css
.element {
  /* calc() 计算 */
  width: calc(100% - 200px);
  height: calc(100vh - 60px);

  /* min() / max() / clamp() */
  width: min(90%, 1200px);
  font-size: clamp(14px, 2vw, 18px); /* 最小值, 首选值, 最大值 */

  /* 颜色函数 */
  color: rgb(52, 152, 219);
  color: rgba(52, 152, 219, 0.8);
  color: hsl(204, 70%, 53%);
  color: hsla(204, 70%, 53%, 0.8);
}
```

## 8. 居中方案总结

```css
/* 1. Flex 居中（推荐） */
.flex-center {
  display: flex;
  justify-content: center;
  align-items: center;
}

/* 2. Grid 居中 */
.grid-center {
  display: grid;
  place-items: center;
}

/* 3. 绝对定位 + transform */
.abs-center {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
}

/* 4. 绝对定位 + margin auto */
.abs-margin {
  position: absolute;
  top: 0; right: 0; bottom: 0; left: 0;
  margin: auto;
  width: 200px;
  height: 200px;
}

/* 5. 行内元素水平居中 */
.text-center {
  text-align: center;
  line-height: 100px; /* 单行垂直居中 */
}
```
