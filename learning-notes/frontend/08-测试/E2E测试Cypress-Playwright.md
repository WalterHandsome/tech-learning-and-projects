# E2E 测试 Cypress / Playwright

## 1. Playwright（推荐）

```javascript
// playwright.config.ts
import { defineConfig } from '@playwright/test';

export default defineConfig({
  testDir: './e2e',
  use: {
    baseURL: 'http://localhost:3000',
    screenshot: 'only-on-failure',
    trace: 'on-first-retry',
  },
  projects: [
    { name: 'chromium', use: { browserName: 'chromium' } },
    { name: 'firefox', use: { browserName: 'firefox' } },
    { name: 'webkit', use: { browserName: 'webkit' } },
  ],
  webServer: {
    command: 'npm run dev',
    port: 3000,
    reuseExistingServer: !process.env.CI,
  },
});
```

```javascript
// e2e/login.spec.ts
import { test, expect } from '@playwright/test';

test.describe('Login', () => {
  test('should login successfully', async ({ page }) => {
    await page.goto('/login');
    await page.getByLabel('用户名').fill('admin');
    await page.getByLabel('密码').fill('123456');
    await page.getByRole('button', { name: '登录' }).click();

    await expect(page).toHaveURL('/dashboard');
    await expect(page.getByText('欢迎回来')).toBeVisible();
  });

  test('should show error for invalid credentials', async ({ page }) => {
    await page.goto('/login');
    await page.getByLabel('用户名').fill('wrong');
    await page.getByLabel('密码').fill('wrong');
    await page.getByRole('button', { name: '登录' }).click();

    await expect(page.getByText('用户名或密码错误')).toBeVisible();
  });
});

// API 拦截
test('mock API response', async ({ page }) => {
  await page.route('/api/users', (route) => {
    route.fulfill({
      status: 200,
      body: JSON.stringify([{ id: 1, name: '张三' }]),
    });
  });
  await page.goto('/users');
  await expect(page.getByText('张三')).toBeVisible();
});
```

## 2. Cypress

```javascript
// cypress/e2e/login.cy.js
describe('Login', () => {
  beforeEach(() => { cy.visit('/login'); });

  it('should login successfully', () => {
    cy.get('[data-testid="username"]').type('admin');
    cy.get('[data-testid="password"]').type('123456');
    cy.get('button[type="submit"]').click();
    cy.url().should('include', '/dashboard');
    cy.contains('欢迎回来').should('be.visible');
  });

  // 网络拦截
  it('should handle API error', () => {
    cy.intercept('POST', '/api/login', { statusCode: 401, body: { message: '认证失败' } });
    cy.get('[data-testid="username"]').type('wrong');
    cy.get('[data-testid="password"]').type('wrong');
    cy.get('button[type="submit"]').click();
    cy.contains('认证失败').should('be.visible');
  });
});
```

## 3. 对比

| 特性 | Playwright | Cypress |
|------|-----------|---------|
| 多浏览器 | Chromium/Firefox/WebKit | Chromium/Firefox/WebKit |
| 多标签页 | 支持 | 不支持 |
| 自动等待 | 内置 | 内置 |
| 并行执行 | 原生支持 | 需要付费 |
| API 测试 | 支持 | 支持 |
| 语言 | JS/TS/Python/Java/C# | JS/TS |
