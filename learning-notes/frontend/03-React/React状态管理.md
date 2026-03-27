# React 状态管理
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. Context API

```jsx
// 适合低频更新的全局状态（主题、语言、用户信息）
const AuthContext = createContext(null);

function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const login = async (credentials) => { /* ... */ };
  const logout = () => setUser(null);
  return (
    <AuthContext.Provider value={{ user, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

const useAuth = () => useContext(AuthContext);
```

## 2. Redux Toolkit

```javascript
// store.js
import { configureStore } from '@reduxjs/toolkit';
import counterReducer from './counterSlice';

export const store = configureStore({
  reducer: { counter: counterReducer },
});

// counterSlice.js
import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';

export const fetchCount = createAsyncThunk('counter/fetch', async (amount) => {
  const res = await fetch(`/api/count?amount=${amount}`);
  return res.json();
});

const counterSlice = createSlice({
  name: 'counter',
  initialState: { value: 0, status: 'idle' },
  reducers: {
    increment: (state) => { state.value += 1; }, // Immer 允许直接修改
    decrement: (state) => { state.value -= 1; },
    incrementByAmount: (state, action) => { state.value += action.payload; },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchCount.pending, (state) => { state.status = 'loading'; })
      .addCase(fetchCount.fulfilled, (state, action) => {
        state.status = 'idle';
        state.value = action.payload;
      });
  },
});

export const { increment, decrement } = counterSlice.actions;
export default counterSlice.reducer;

// 组件中使用
import { useSelector, useDispatch } from 'react-redux';
function Counter() {
  const count = useSelector(state => state.counter.value);
  const dispatch = useDispatch();
  return <button onClick={() => dispatch(increment())}>{count}</button>;
}
```

## 3. Zustand（轻量推荐）

```javascript
import { create } from 'zustand';
import { devtools, persist } from 'zustand/middleware';

const useStore = create(
  devtools(
    persist(
      (set, get) => ({
        count: 0,
        increment: () => set(state => ({ count: state.count + 1 })),
        decrement: () => set(state => ({ count: state.count - 1 })),
        reset: () => set({ count: 0 }),
        // 异步操作
        fetchCount: async () => {
          const res = await fetch('/api/count');
          const data = await res.json();
          set({ count: data.count });
        },
      }),
      { name: 'counter-storage' } // localStorage 持久化
    )
  )
);

// 组件中使用（自动订阅，精确更新）
function Counter() {
  const count = useStore(state => state.count);
  const increment = useStore(state => state.increment);
  return <button onClick={increment}>{count}</button>;
}
```

## 4. TanStack Query（服务端状态）

```jsx
import { useQuery, useMutation, useQueryClient, QueryClient, QueryClientProvider } from '@tanstack/react-query';

const queryClient = new QueryClient();

// 查询
function UserList() {
  const { data, isLoading, error } = useQuery({
    queryKey: ['users'],
    queryFn: () => fetch('/api/users').then(r => r.json()),
    staleTime: 5 * 60 * 1000,  // 5分钟内不重新请求
    gcTime: 10 * 60 * 1000,    // 缓存保留10分钟
  });

  if (isLoading) return <div>加载中...</div>;
  if (error) return <div>错误: {error.message}</div>;
  return <ul>{data.map(u => <li key={u.id}>{u.name}</li>)}</ul>;
}

// 变更
function CreateUser() {
  const queryClient = useQueryClient();
  const mutation = useMutation({
    mutationFn: (newUser) => fetch('/api/users', {
      method: 'POST',
      body: JSON.stringify(newUser),
    }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['users'] }); // 刷新列表
    },
  });

  return <button onClick={() => mutation.mutate({ name: '新用户' })}>创建</button>;
}
```

## 5. 状态管理选型

| 方案 | 适用场景 | 复杂度 |
|------|---------|--------|
| useState | 组件内部状态 | 低 |
| Context | 低频全局状态（主题、认证） | 低 |
| Zustand | 中小型应用全局状态 | 低 |
| Redux Toolkit | 大型应用、复杂状态逻辑 | 中 |
| TanStack Query | 服务端状态（API数据缓存） | 中 |
| Jotai | 原子化状态管理 | 低 |
