# CI/CD 与自动化部署

## 1. GitHub Actions

```yaml
# .github/workflows/ci.yml
name: CI/CD

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: pnpm/action-setup@v2
        with: { version: 9 }
      - uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: 'pnpm'
      - run: pnpm install --frozen-lockfile
      - run: pnpm lint
      - run: pnpm test -- --run
      - run: pnpm build

  deploy:
    needs: test
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: pnpm/action-setup@v2
        with: { version: 9 }
      - uses: actions/setup-node@v4
        with: { node-version: 20, cache: 'pnpm' }
      - run: pnpm install --frozen-lockfile
      - run: pnpm build
      # 部署到服务器 / CDN / Vercel / Netlify 等
```

## 2. Docker 构建推送

```yaml
  docker:
    needs: test
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: docker/setup-buildx-action@v3
      - uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      - uses: docker/build-push-action@v5
        with:
          push: true
          tags: ghcr.io/${{ github.repository }}:latest
          cache-from: type=gha
          cache-to: type=gha,mode=max
```

## 3. 版本管理（Changesets）

```bash
# 安装
pnpm add -D @changesets/cli
npx changeset init

# 添加变更记录
npx changeset
# 选择包 → 选择版本类型（patch/minor/major）→ 写变更描述

# 发布
npx changeset version  # 更新版本号和 CHANGELOG
npx changeset publish  # 发布到 npm
```

## 4. 部署平台

```
Vercel：
- 零配置部署 Next.js / React / Vue
- 自动 Preview 部署（PR 预览）
- Edge Functions

Netlify：
- 静态站点部署
- Serverless Functions
- 表单处理

自建服务器：
- Docker + Nginx
- PM2 + Node.js
- Kubernetes
```
