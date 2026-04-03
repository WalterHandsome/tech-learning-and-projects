# Jest 单元测试
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. 基础语法

```javascript
// sum.test.js
import { sum, multiply } from './math';

describe('Math utils', () => {
  // 基本测试
  it('should add two numbers', () => {
    expect(sum(1, 2)).toBe(3);
  });

  // 常用匹配器
  it('matchers', () => {
    expect(2 + 2).toBe(4);                    // 严格相等
    expect({ name: '张三' }).toEqual({ name: '张三' }); // 深度相等
    expect(null).toBeNull();
    expect(undefined).toBeUndefined();
    expect(1).toBeTruthy();
    expect(0).toBeFalsy();
    expect(10).toBeGreaterThan(5);
    expect('hello').toContain('ell');
    expect([1, 2, 3]).toContain(2);
    expect(() => { throw new Error('fail'); }).toThrow('fail');
  });
});
```

## 2. Mock 函数

```javascript
// Mock 函数
const mockFn = jest.fn();
mockFn.mockReturnValue(42);
mockFn.mockResolvedValue({ data: 'ok' });
mockFn.mockImplementation((x) => x * 2);

expect(mockFn).toHaveBeenCalled();
expect(mockFn).toHaveBeenCalledWith('arg');
expect(mockFn).toHaveBeenCalledTimes(1);

// Mock 模块
jest.mock('./api', () => ({
  fetchUser: jest.fn().mockResolvedValue({ id: 1, name: '张三' }),
}));

// Spy
const spy = jest.spyOn(console, 'log');
doSomething();
expect(spy).toHaveBeenCalledWith('expected message');
spy.mockRestore();
```

## 3. 异步测试

```javascript
// async/await
it('fetches user data', async () => {
  const user = await fetchUser(1);
  expect(user.name).toBe('张三');
});

// resolves/rejects
it('resolves with data', () => {
  return expect(fetchUser(1)).resolves.toEqual({ id: 1, name: '张三' });
});

it('rejects with error', () => {
  return expect(fetchUser(-1)).rejects.toThrow('Not found');
});
```

## 4. 生命周期

```javascript
describe('Database tests', () => {
  beforeAll(async () => { await db.connect(); });
  afterAll(async () => { await db.disconnect(); });
  beforeEach(async () => { await db.clear(); });
  afterEach(() => { jest.restoreAllMocks(); });

  it('should create user', async () => { /* ... */ });
});
```

## 5. Vitest（Vite 项目推荐）

```javascript
// vitest 与 jest API 基本兼容
import { describe, it, expect, vi } from 'vitest';

const mockFn = vi.fn();
vi.mock('./api');
vi.spyOn(console, 'log');

// 优势：
// - 与 Vite 共享配置，开箱即用
// - 原生 ESM 支持
// - 更快的执行速度
// - 兼容 Jest API
```
## 🎬 推荐视频资源

- [Traversy Media - Jest Crash Course](https://www.youtube.com/watch?v=7r4xVDI2vho) — Jest速成
- [freeCodeCamp - JavaScript Testing](https://www.youtube.com/watch?v=FgnxcUQ5vho) — JavaScript测试完整课程
