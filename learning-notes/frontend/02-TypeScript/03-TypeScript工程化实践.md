# TypeScript 工程化实践
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. tsconfig.json 配置

<!-- version-check: TypeScript 5.9, checked 2026-04-18 -->

> 🔄 更新于 2026-04-18：TypeScript 5.9（2025-07 发布）是当前稳定版，新增 `--strictInference` 标志（在 `--strict` 下默认启用）、重新设计的 `tsc --init` 生成精简 tsconfig、`import defer` 支持。TypeScript 7.0 正在开发中，使用 Go 重写编译器，构建速度预计提升 10x。

来源：[TypeScript 5.9 文档](https://www.typescriptlang.org/docs/handbook/release-notes/typescript-5-9.html)

```jsonc
{
  "compilerOptions": {
    // 目标与模块
    "target": "ES2020",
    "module": "ESNext",
    "moduleResolution": "bundler",
    "lib": ["ES2020", "DOM", "DOM.Iterable"],

    // 严格模式（推荐全部开启）
    "strict": true,
    "noImplicitAny": true,
    "strictNullChecks": true,
    "strictFunctionTypes": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true,

    // 路径与输出
    "baseUrl": ".",
    "paths": {
      "@/*": ["src/*"],
      "@components/*": ["src/components/*"]
    },
    "outDir": "dist",
    "rootDir": "src",

    // JSX（React项目）
    "jsx": "react-jsx",

    // 互操作
    "esModuleInterop": true,
    "allowSyntheticDefaultImports": true,
    "resolveJsonModule": true,
    "isolatedModules": true,

    // 声明文件
    "declaration": true,
    "declarationMap": true,
    "sourceMap": true,

    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true
  },
  "include": ["src/**/*"],
  "exclude": ["node_modules", "dist"]
}
```

## 2. 声明文件

```typescript
// types/global.d.ts — 全局类型声明
declare global {
  interface Window {
    __APP_CONFIG__: {
      apiUrl: string;
      env: 'development' | 'production';
    };
  }
}

// 模块声明（为无类型的库添加类型）
declare module '*.css' {
  const classes: { [key: string]: string };
  export default classes;
}

declare module '*.svg' {
  const content: string;
  export default content;
}

declare module 'some-untyped-lib' {
  export function doSomething(input: string): number;
}
```

## 3. 与 React 集成

```typescript
// 组件 Props 类型
interface ButtonProps {
  variant?: 'primary' | 'secondary' | 'danger';
  size?: 'sm' | 'md' | 'lg';
  disabled?: boolean;
  onClick?: (e: React.MouseEvent<HTMLButtonElement>) => void;
  children: React.ReactNode;
}

const Button: React.FC<ButtonProps> = ({ variant = 'primary', children, ...props }) => {
  return <button className={variant} {...props}>{children}</button>;
};

// 事件类型
const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {};
const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {};

// Ref 类型
const inputRef = useRef<HTMLInputElement>(null);

// 泛型组件
interface ListProps<T> {
  items: T[];
  renderItem: (item: T) => React.ReactNode;
}

function List<T>({ items, renderItem }: ListProps<T>) {
  return <ul>{items.map(renderItem)}</ul>;
}
```

## 4. 与 Vue 集成

```typescript
// defineComponent + TypeScript
<script setup lang="ts">
import { ref, computed } from 'vue';

interface User {
  id: number;
  name: string;
}

const props = defineProps<{
  title: string;
  users: User[];
  count?: number;
}>();

const emit = defineEmits<{
  (e: 'update', id: number): void;
  (e: 'delete', id: number): void;
}>();

const search = ref<string>('');
const filteredUsers = computed<User[]>(() =>
  props.users.filter(u => u.name.includes(search.value))
);
</script>
```
