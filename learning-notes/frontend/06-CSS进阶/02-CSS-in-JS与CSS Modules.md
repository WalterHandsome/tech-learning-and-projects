# CSS-in-JS 与 CSS Modules
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. CSS Modules

```css
/* Button.module.css */
.button { padding: 8px 16px; border-radius: 4px; }
.primary { background: #3498db; color: white; }
.large { font-size: 18px; padding: 12px 24px; }
```

```jsx
import styles from './Button.module.css';

function Button({ variant, size, children }) {
  return (
    <button className={`${styles.button} ${styles[variant]} ${styles[size]}`}>
      {children}
    </button>
  );
}
```

## 2. styled-components

```jsx
import styled from 'styled-components';

const Button = styled.button`
  padding: ${props => props.$size === 'lg' ? '12px 24px' : '8px 16px'};
  background: ${props => props.$variant === 'primary' ? '#3498db' : '#eee'};
  color: ${props => props.$variant === 'primary' ? 'white' : '#333'};
  border: none;
  border-radius: 4px;
  cursor: pointer;

  &:hover { opacity: 0.9; }

  @media (max-width: 768px) {
    width: 100%;
  }
`;

// 继承样式
const PrimaryButton = styled(Button)`
  background: #3498db;
  color: white;
`;

// 主题
import { ThemeProvider } from 'styled-components';
const theme = { colors: { primary: '#3498db' }, spacing: { md: '16px' } };
<ThemeProvider theme={theme}><App /></ThemeProvider>
```

## 3. 方案对比

| 方案 | 运行时开销 | 类型安全 | 适用场景 |
|------|-----------|---------|---------|
| CSS Modules | 无 | 一般 | 通用 |
| styled-components | 有 | 好 | React 项目 |
| Tailwind CSS | 无 | 无 | 快速开发 |
| vanilla-extract | 无 | 好 | 零运行时需求 |
