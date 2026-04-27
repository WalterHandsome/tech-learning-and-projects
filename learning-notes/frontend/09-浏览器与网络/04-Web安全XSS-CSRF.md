# Web 安全 XSS / CSRF
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. XSS（跨站脚本攻击）

### 1.1 类型

```
存储型 XSS：恶意脚本存储在服务器（数据库），其他用户访问时执行
反射型 XSS：恶意脚本在 URL 参数中，服务器返回时执行
DOM 型 XSS：恶意脚本通过 DOM 操作注入，不经过服务器
```

### 1.2 防御

```javascript
// 1. 输出编码（最基本的防御）
function escapeHtml(str) {
  const map = { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#x27;' };
  return str.replace(/[&<>"']/g, (c) => map[c]);
}

// 2. React/Vue 默认转义（安全）
<div>{userInput}</div>  // React 自动转义
<div>{{ userInput }}</div>  // Vue 自动转义

// ⚠️ 危险操作（避免使用）
<div dangerouslySetInnerHTML={{ __html: userInput }} />  // React
<div v-html="userInput"></div>  // Vue

// 3. CSP（Content Security Policy）
// HTTP 响应头
Content-Security-Policy: default-src 'self'; script-src 'self' 'nonce-abc123'; style-src 'self' 'unsafe-inline'

// 4. HttpOnly Cookie（防止 JS 读取）
Set-Cookie: token=abc; HttpOnly; Secure; SameSite=Strict
```

## 2. CSRF（跨站请求伪造）

### 2.1 原理

```
1. 用户登录 A 网站，浏览器保存 Cookie
2. 用户访问恶意网站 B
3. B 网站向 A 发起请求，浏览器自动携带 A 的 Cookie
4. A 网站无法区分是用户还是恶意请求
```

### 2.2 防御

```javascript
// 1. CSRF Token
// 服务端生成 Token，嵌入表单或请求头
<input type="hidden" name="_csrf" value="token123">

// 2. SameSite Cookie
Set-Cookie: token=abc; SameSite=Strict  // 完全禁止跨站携带
Set-Cookie: token=abc; SameSite=Lax     // 允许导航跳转携带（默认）

// 3. 验证 Origin / Referer 头
if (req.headers.origin !== 'https://mysite.com') {
  return res.status(403).json({ error: 'Forbidden' });
}

// 4. 双重 Cookie 验证
// Cookie 中设置 csrf_token，请求头中也携带，服务端比对
```

## 3. 其他安全措施

```javascript
// CORS 跨域配置
app.use(cors({
  origin: ['https://mysite.com'],
  credentials: true,
  methods: ['GET', 'POST', 'PUT', 'DELETE'],
}));

// 点击劫持防御
X-Frame-Options: DENY
Content-Security-Policy: frame-ancestors 'none'

// 子资源完整性（SRI）
<script src="https://cdn.example.com/lib.js"
  integrity="sha384-oqVuAfXRKap7fdgcCY5uykM6+R9GqQ8K/uxy9rx7HNQlGYl1kPzQho1wx4JwY8w"
  crossorigin="anonymous">
</script>

// 安全响应头
Strict-Transport-Security: max-age=31536000; includeSubDomains  // HSTS
X-Content-Type-Options: nosniff
X-XSS-Protection: 0  // 现代浏览器建议关闭，使用 CSP 替代
Referrer-Policy: strict-origin-when-cross-origin
```

<!-- version-check: Trusted Types Baseline 2026-02, CSP Level 3, checked 2026-04-27 -->

> 🔄 更新于 2026-04-27

## 4. Trusted Types API（2026 年全浏览器支持）

Trusted Types 自 2026 年 2 月起成为 **Baseline Newly Available**，所有主流浏览器均已支持。它从根本上防止 DOM XSS：不再依赖开发者"记得转义"，而是让浏览器强制要求只有经过策略处理的类型化值才能传入危险 DOM API。

来源：[MDN Trusted Types API](https://developer.mozilla.org/docs/Web/API/Trusted_Types_API)

```javascript
// 1. 启用 Trusted Types（CSP 头）
// Content-Security-Policy: trusted-types myPolicy; require-trusted-types-for 'script'

// 2. 定义策略
const policy = trustedTypes.createPolicy('myPolicy', {
  createHTML: (input) => {
    // 在这里做安全处理（转义、白名单过滤等）
    return DOMPurify.sanitize(input);
  },
  createScriptURL: (input) => {
    // 只允许可信域名的脚本
    const url = new URL(input);
    if (url.origin === 'https://cdn.mysite.com') return input;
    throw new TypeError('不允许的脚本来源');
  }
});

// 3. 使用策略创建可信值
element.innerHTML = policy.createHTML(userInput);  // ✅ 通过策略
element.innerHTML = userInput;                      // ❌ 浏览器拒绝

// Trusted Types 类型：
// TrustedHTML    → innerHTML, outerHTML, insertAdjacentHTML
// TrustedScript  → eval(), setTimeout(string)
// TrustedScriptURL → script.src, Worker()
```

来源：[Stop Sanitizing HTML: Use Trusted Types](https://loke.dev/blog/stop-sanitizing-html-use-trusted-types)

### CSP Level 3 更新

W3C CSP Level 3 规范在 2026 年持续更新，关键变化：

```
# 2026 年推荐的安全响应头组合
Content-Security-Policy: default-src 'self'; script-src 'self' 'nonce-{random}'; style-src 'self' 'unsafe-inline'; trusted-types myPolicy; require-trusted-types-for 'script'
Strict-Transport-Security: max-age=63072000; includeSubDomains; preload
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
Referrer-Policy: strict-origin-when-cross-origin
Permissions-Policy: camera=(), microphone=(), geolocation=()
```

来源：[W3C CSP Level 3](https://www.w3.org/TR/CSP/)
## 🎬 推荐视频资源

- [Fireship - Web Security in 100 Seconds](https://www.youtube.com/watch?v=4YOpILi9Oxs) — Web安全快速了解
- [Computerphile - Cross Site Scripting](https://www.youtube.com/watch?v=L5l9lSnNMxg) — XSS详解
