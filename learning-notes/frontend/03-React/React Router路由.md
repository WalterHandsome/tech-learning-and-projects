# React Router 路由

> Author: Walter Wang

## 1. 基本配置（v6）

```jsx
import { BrowserRouter, Routes, Route, Link, NavLink, Outlet } from 'react-router-dom';

function App() {
  return (
    <BrowserRouter>
      <nav>
        <Link to="/">首页</Link>
        <NavLink to="/about" className={({ isActive }) => isActive ? 'active' : ''}>
          关于
        </NavLink>
      </nav>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Home />} />
          <Route path="about" element={<About />} />
          <Route path="users" element={<Users />}>
            <Route path=":userId" element={<UserDetail />} />
          </Route>
          <Route path="*" element={<NotFound />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

function Layout() {
  return (
    <div>
      <header>Header</header>
      <main><Outlet /></main> {/* 子路由渲染位置 */}
      <footer>Footer</footer>
    </div>
  );
}
```

## 2. 路由 Hooks

```jsx
import { useParams, useSearchParams, useNavigate, useLocation } from 'react-router-dom';

function UserDetail() {
  const { userId } = useParams();           // 路径参数
  const [searchParams, setSearchParams] = useSearchParams(); // 查询参数
  const navigate = useNavigate();            // 编程式导航
  const location = useLocation();            // 当前位置信息

  const tab = searchParams.get('tab') || 'profile';

  return (
    <div>
      <h1>用户 {userId}</h1>
      <button onClick={() => navigate(-1)}>返回</button>
      <button onClick={() => navigate('/users', { replace: true })}>
        回到列表
      </button>
    </div>
  );
}
```

## 3. 路由守卫

```jsx
function ProtectedRoute({ children }) {
  const { user } = useAuth();
  const location = useLocation();

  if (!user) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }
  return children;
}

// 使用
<Route path="/dashboard" element={
  <ProtectedRoute>
    <Dashboard />
  </ProtectedRoute>
} />
```

## 4. 路由懒加载

```jsx
import { lazy, Suspense } from 'react';

const Dashboard = lazy(() => import('./pages/Dashboard'));
const Settings = lazy(() => import('./pages/Settings'));

function App() {
  return (
    <Suspense fallback={<div>加载中...</div>}>
      <Routes>
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/settings" element={<Settings />} />
      </Routes>
    </Suspense>
  );
}
```

## 5. 数据加载（loader）

```jsx
import { createBrowserRouter, RouterProvider, useLoaderData } from 'react-router-dom';

const router = createBrowserRouter([
  {
    path: '/users/:id',
    element: <UserDetail />,
    loader: async ({ params }) => {
      const res = await fetch(`/api/users/${params.id}`);
      if (!res.ok) throw new Response('Not Found', { status: 404 });
      return res.json();
    },
    errorElement: <ErrorPage />,
  },
]);

function UserDetail() {
  const user = useLoaderData();
  return <h1>{user.name}</h1>;
}

function App() {
  return <RouterProvider router={router} />;
}
```
