# DOM 与 BOM 操作

## 1. DOM 查询

```javascript
// 推荐
document.getElementById('id');
document.querySelector('.class');       // 返回第一个匹配
document.querySelectorAll('.class');    // 返回 NodeList

// 其他
document.getElementsByClassName('class'); // HTMLCollection（实时）
document.getElementsByTagName('div');
element.closest('.parent');              // 向上查找最近匹配的祖先
element.matches('.selector');            // 是否匹配选择器
```

## 2. DOM 操作

```javascript
// 创建
const div = document.createElement('div');
const text = document.createTextNode('hello');
const fragment = document.createDocumentFragment(); // 文档片段（批量操作）

// 插入
parent.appendChild(child);
parent.insertBefore(newNode, referenceNode);
parent.append(node1, node2, 'text');     // 可插入多个
parent.prepend(node);                     // 插入到开头
element.before(node);                     // 插入到元素前
element.after(node);                      // 插入到元素后

// 替换与删除
parent.replaceChild(newChild, oldChild);
element.replaceWith(newElement);
parent.removeChild(child);
element.remove();

// 克隆
const clone = element.cloneNode(true); // true = 深克隆

// 属性操作
element.setAttribute('data-id', '123');
element.getAttribute('data-id');
element.removeAttribute('data-id');
element.dataset.id;                    // data-* 属性
element.classList.add('active');
element.classList.remove('active');
element.classList.toggle('active');
element.classList.contains('active');

// 样式操作
element.style.color = 'red';
element.style.cssText = 'color: red; font-size: 16px;';
getComputedStyle(element).color;       // 获取计算后的样式

// 内容操作
element.innerHTML = '<p>HTML内容</p>';
element.textContent = '纯文本内容';
element.innerText = '可见文本';        // 受CSS影响
```

## 3. 事件模型

```javascript
// 事件流：捕获阶段 → 目标阶段 → 冒泡阶段

// 添加事件监听
element.addEventListener('click', handler, {
  capture: false,  // 是否在捕获阶段触发
  once: true,      // 只触发一次
  passive: true,   // 不会调用 preventDefault（提升滚动性能）
});

// 移除事件监听
element.removeEventListener('click', handler);

// 事件对象
element.addEventListener('click', (e) => {
  e.target;           // 触发事件的元素
  e.currentTarget;    // 绑定事件的元素
  e.preventDefault();  // 阻止默认行为
  e.stopPropagation(); // 阻止冒泡
  e.type;             // 事件类型
});

// 事件委托（利用冒泡，减少事件绑定）
document.getElementById('list').addEventListener('click', (e) => {
  if (e.target.matches('li')) {
    console.log('点击了:', e.target.textContent);
  }
});
```

## 4. Observer API

```javascript
// IntersectionObserver（元素可见性，懒加载/无限滚动）
const observer = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      entry.target.src = entry.target.dataset.src; // 懒加载
      observer.unobserve(entry.target);
    }
  });
}, { threshold: 0.1 });
document.querySelectorAll('img[data-src]').forEach(img => observer.observe(img));

// MutationObserver（DOM变化监听）
const mutationObserver = new MutationObserver((mutations) => {
  mutations.forEach(m => console.log('DOM变化:', m.type));
});
mutationObserver.observe(element, { childList: true, subtree: true, attributes: true });

// ResizeObserver（元素尺寸变化）
const resizeObserver = new ResizeObserver((entries) => {
  entries.forEach(entry => {
    console.log('新尺寸:', entry.contentRect.width, entry.contentRect.height);
  });
});
resizeObserver.observe(element);
```

## 5. BOM 对象

```javascript
// window
window.innerWidth;   // 视口宽度
window.innerHeight;  // 视口高度
window.scrollTo({ top: 0, behavior: 'smooth' });
window.open(url);

// location
location.href;       // 完整URL
location.pathname;   // 路径
location.search;     // 查询参数
location.hash;       // 哈希值
location.reload();   // 刷新

// history
history.pushState(state, '', '/new-url');
history.replaceState(state, '', '/new-url');
history.back();
history.forward();
window.addEventListener('popstate', (e) => { /* 路由变化 */ });

// navigator
navigator.userAgent;
navigator.language;
navigator.clipboard.writeText('复制内容');
```
