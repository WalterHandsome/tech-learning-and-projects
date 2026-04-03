# Electron 桌面应用
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. 架构

```
Electron 应用
├── 主进程（Main Process）    — Node.js 环境，管理窗口和系统交互
├── 渲染进程（Renderer）      — Chromium，运行 Web 页面
└── 预加载脚本（Preload）     — 桥接主进程和渲染进程
```

## 2. 基本结构

```javascript
// main.js（主进程）
import { app, BrowserWindow, ipcMain } from 'electron';
import path from 'path';

function createWindow() {
  const win = new BrowserWindow({
    width: 1200,
    height: 800,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true,  // 安全：隔离上下文
      nodeIntegration: false,  // 安全：禁用 Node
    },
  });
  win.loadFile('index.html');
  // 或 win.loadURL('http://localhost:3000'); // 开发模式
}

app.whenReady().then(createWindow);
app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') app.quit();
});
```

## 3. IPC 通信

```javascript
// preload.js（预加载脚本）
import { contextBridge, ipcRenderer } from 'electron';

contextBridge.exposeInMainWorld('electronAPI', {
  readFile: (path) => ipcRenderer.invoke('read-file', path),
  onUpdate: (callback) => ipcRenderer.on('update', (_, data) => callback(data)),
});

// main.js（主进程处理）
ipcMain.handle('read-file', async (event, filePath) => {
  return fs.readFileSync(filePath, 'utf-8');
});

// renderer.js（渲染进程调用）
const content = await window.electronAPI.readFile('/path/to/file');
```

## 4. 打包发布

```javascript
// electron-builder 配置
// package.json
{
  "build": {
    "appId": "com.example.myapp",
    "mac": { "target": "dmg" },
    "win": { "target": "nsis" },
    "linux": { "target": "AppImage" }
  }
}
```

```bash
npx electron-builder --mac --win --linux
```
