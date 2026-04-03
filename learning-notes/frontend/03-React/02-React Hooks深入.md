# React Hooks 深入
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. useState

```jsx
// 基本用法
const [count, setCount] = useState(0);

// 函数式更新（基于前一个状态）
setCount(prev => prev + 1);

// 惰性初始化（复杂计算只在首次渲染执行）
const [state, setState] = useState(() => {
  return expensiveComputation();
});

// 对象状态（需要展开合并）
const [form, setForm] = useState({ name: '', email: '' });
setForm(prev => ({ ...prev, name: '张三' }));
```

## 2. useEffect

```jsx
// 每次渲染后执行
useEffect(() => { console.log('rendered'); });

// 仅挂载时执行
useEffect(() => { fetchData(); }, []);

// 依赖变化时执行
useEffect(() => {
  const results = search(query);
  setResults(results);
}, [query]);

// 清理副作用
useEffect(() => {
  const timer = setInterval(() => tick(), 1000);
  return () => clearInterval(timer); // 清理
}, []);

// 请求数据模式
useEffect(() => {
  let cancelled = false;
  async function fetchData() {
    const res = await fetch(`/api/users/${id}`);
    const data = await res.json();
    if (!cancelled) setUser(data);
  }
  fetchData();
  return () => { cancelled = true; }; // 防止竞态
}, [id]);
```

## 3. useContext

```jsx
const ThemeContext = createContext({ theme: 'light', toggle: () => {} });

function ThemeProvider({ children }) {
  const [theme, setTheme] = useState('light');
  const toggle = () => setTheme(t => t === 'light' ? 'dark' : 'light');
  return (
    <ThemeContext.Provider value={{ theme, toggle }}>
      {children}
    </ThemeContext.Provider>
  );
}

// 自定义 Hook 封装
function useTheme() {
  const context = useContext(ThemeContext);
  if (!context) throw new Error('useTheme must be used within ThemeProvider');
  return context;
}
```

## 4. useReducer

```jsx
const initialState = { count: 0, step: 1 };

function reducer(state, action) {
  switch (action.type) {
    case 'increment': return { ...state, count: state.count + state.step };
    case 'decrement': return { ...state, count: state.count - state.step };
    case 'setStep':   return { ...state, step: action.payload };
    case 'reset':     return initialState;
    default: throw new Error(`Unknown action: ${action.type}`);
  }
}

function Counter() {
  const [state, dispatch] = useReducer(reducer, initialState);
  return (
    <div>
      <p>Count: {state.count}</p>
      <button onClick={() => dispatch({ type: 'increment' })}>+</button>
      <button onClick={() => dispatch({ type: 'decrement' })}>-</button>
      <button onClick={() => dispatch({ type: 'reset' })}>重置</button>
    </div>
  );
}
```

## 5. useMemo / useCallback

```jsx
// useMemo：缓存计算结果
const expensiveResult = useMemo(() => {
  return items.filter(item => item.active).sort((a, b) => a.name.localeCompare(b.name));
}, [items]);

// useCallback：缓存函数引用（配合 React.memo 使用）
const handleClick = useCallback((id) => {
  setSelectedId(id);
}, []);

// React.memo：浅比较 props，避免不必要的重渲染
const MemoChild = React.memo(function Child({ onClick, data }) {
  return <div onClick={onClick}>{data.name}</div>;
});
```

## 6. useRef

```jsx
// DOM 引用
const inputRef = useRef(null);
const focusInput = () => inputRef.current?.focus();
<input ref={inputRef} />

// 保存可变值（不触发重渲染）
const timerRef = useRef(null);
useEffect(() => {
  timerRef.current = setInterval(() => tick(), 1000);
  return () => clearInterval(timerRef.current);
}, []);

// 保存前一个值
function usePrevious(value) {
  const ref = useRef();
  useEffect(() => { ref.current = value; });
  return ref.current;
}
```

## 7. 自定义 Hook

```jsx
// useLocalStorage
function useLocalStorage(key, initialValue) {
  const [value, setValue] = useState(() => {
    try {
      const item = localStorage.getItem(key);
      return item ? JSON.parse(item) : initialValue;
    } catch { return initialValue; }
  });

  useEffect(() => {
    localStorage.setItem(key, JSON.stringify(value));
  }, [key, value]);

  return [value, setValue];
}

// useDebounce
function useDebounce(value, delay = 300) {
  const [debouncedValue, setDebouncedValue] = useState(value);
  useEffect(() => {
    const timer = setTimeout(() => setDebouncedValue(value), delay);
    return () => clearTimeout(timer);
  }, [value, delay]);
  return debouncedValue;
}

// useFetch
function useFetch(url) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    fetch(url)
      .then(res => res.json())
      .then(data => { if (!cancelled) setData(data); })
      .catch(err => { if (!cancelled) setError(err); })
      .finally(() => { if (!cancelled) setLoading(false); });
    return () => { cancelled = true; };
  }, [url]);

  return { data, loading, error };
}
```
## 🎬 推荐视频资源

- [Web Dev Simplified - React Hooks](https://www.youtube.com/watch?v=O6P86uwfdR0) — React Hooks完整教程
- [Jack Herrington - React Hooks](https://www.youtube.com/@jherr) — React高级技巧频道
