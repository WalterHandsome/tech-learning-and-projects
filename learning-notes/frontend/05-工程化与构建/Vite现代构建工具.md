# Vite 现代构建工具

## 1. 核心原理

- 开发环境：基于浏览器原生 ESM，按需编译，启动极快
- 生产环境：使用 Rollup 打包，支持 Tree Shaking、代码分割
- 依赖预构建：使用 esbuild 将 CommonJS/UMD 转为 ESM，合并小模块

## 2. 基本配置

```javascript
// vite.config.ts
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
// import vue from '@vitejs/plugin-vue';

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: { '@': '/src' },
  },
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:8080',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ''),
      },
    },
  },
  build: {
    outDir: 'dist',
    sourcemap: true,
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['react', 'react-dom'],
          utils: ['lodash-es', 'dayjs'],
        },
      },
    },
  },
  css: {
    modules: { localsConvention: 'camelCase' },
    preprocessorOptions: {
      scss: { additionalData: `@use "@/styles/variables" as *;` },
    },
  },
});
```

## 3. 环境变量

```bash
# .env.development
VITE_API_URL=http://localhost:8080
VITE_APP_TITLE=My App (Dev)

# .env.production
VITE_API_URL=https://api.example.com
VITE_APP_TITLE=My App
```

```javascript
// 使用（必须以 VITE_ 开头）
const apiUrl = import.meta.env.VITE_API_URL;
const isDev = import.meta.env.DEV;
const isProd = import.meta.env.PROD;
const mode = import.meta.env.MODE;
```

## 4. 插件系统

```javascript
// 自定义插件
function myPlugin() {
  return {
    name: 'my-plugin',
    configResolved(config) { /* 配置解析完成 */ },
    transformIndexHtml(html) {
      return html.replace('__TITLE__', 'My App');
    },
    transform(code, id) {
      if (id.endsWith('.md')) {
        return `export default ${JSON.stringify(marked(code))}`;
      }
    },
  };
}

// 常用插件
// @vitejs/plugin-react     — React 支持
// @vitejs/plugin-vue       — Vue 支持
// vite-plugin-compression  — Gzip/Brotli 压缩
// vite-plugin-svg-icons    — SVG 图标
// unplugin-auto-import     — 自动导入
```

## 5. SSR 支持

```javascript
// server.js
import express from 'express';
import { createServer as createViteServer } from 'vite';

const app = express();
const vite = await createViteServer({ server: { middlewareMode: true } });
app.use(vite.middlewares);

app.use('*', async (req, res) => {
  const template = await vite.transformIndexHtml(req.originalUrl, fs.readFileSync('index.html', 'utf-8'));
  const { render } = await vite.ssrLoadModule('/src/entry-server.js');
  const appHtml = await render(req.originalUrl);
  const html = template.replace('<!--ssr-outlet-->', appHtml);
  res.status(200).set({ 'Content-Type': 'text/html' }).end(html);
});
```
