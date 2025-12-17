# Python算法与数据结构

## 1. 算法与数据结构概述

算法和数据结构是编程的基础，Python提供了丰富的数据结构，同时也可以实现各种经典算法。

## 2. 数据结构

### 2.1 数组和列表

```python
# 列表操作
arr = [1, 2, 3, 4, 5]

# 访问：O(1)
value = arr[0]

# 插入：O(n)
arr.insert(0, 0)

# 删除：O(n)
arr.remove(3)

# 查找：O(n)
index = arr.index(4)
```

### 2.2 栈（Stack）

```python
class Stack:
    def __init__(self):
        self.items = []
    
    def push(self, item):
        self.items.append(item)
    
    def pop(self):
        if self.is_empty():
            raise IndexError("Stack is empty")
        return self.items.pop()
    
    def peek(self):
        return self.items[-1]
    
    def is_empty(self):
        return len(self.items) == 0
    
    def size(self):
        return len(self.items)

# 使用
stack = Stack()
stack.push(1)
stack.push(2)
print(stack.pop())  # 2
```

### 2.3 队列（Queue）

```python
from collections import deque

class Queue:
    def __init__(self):
        self.items = deque()
    
    def enqueue(self, item):
        self.items.append(item)
    
    def dequeue(self):
        if self.is_empty():
            raise IndexError("Queue is empty")
        return self.items.popleft()
    
    def is_empty(self):
        return len(self.items) == 0
    
    def size(self):
        return len(self.items)

# 使用
queue = Queue()
queue.enqueue(1)
queue.enqueue(2)
print(queue.dequeue())  # 1
```

### 2.4 优先队列

```python
import heapq

# 最小堆
heap = []
heapq.heappush(heap, 3)
heapq.heappush(heap, 1)
heapq.heappush(heap, 2)
print(heapq.heappop(heap))  # 1

# 最大堆（使用负数）
heap = []
heapq.heappush(heap, -3)
heapq.heappush(heap, -1)
heapq.heappush(heap, -2)
print(-heapq.heappop(heap))  # 3
```

### 2.5 链表

```python
class Node:
    def __init__(self, data):
        self.data = data
        self.next = None

class LinkedList:
    def __init__(self):
        self.head = None
    
    def append(self, data):
        new_node = Node(data)
        if not self.head:
            self.head = new_node
            return
        current = self.head
        while current.next:
            current = current.next
        current.next = new_node
    
    def prepend(self, data):
        new_node = Node(data)
        new_node.next = self.head
        self.head = new_node
    
    def delete(self, data):
        if not self.head:
            return
        if self.head.data == data:
            self.head = self.head.next
            return
        current = self.head
        while current.next:
            if current.next.data == data:
                current.next = current.next.next
                return
            current = current.next
```

### 2.6 二叉树

```python
class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

class BinaryTree:
    def __init__(self):
        self.root = None
    
    def insert(self, val):
        if not self.root:
            self.root = TreeNode(val)
        else:
            self._insert(self.root, val)
    
    def _insert(self, node, val):
        if val < node.val:
            if node.left:
                self._insert(node.left, val)
            else:
                node.left = TreeNode(val)
        else:
            if node.right:
                self._insert(node.right, val)
            else:
                node.right = TreeNode(val)
    
    def inorder(self, node):
        if node:
            self.inorder(node.left)
            print(node.val)
            self.inorder(node.right)
```

### 2.7 哈希表

```python
# Python字典就是哈希表
hash_table = {}

# 插入：O(1)
hash_table['key'] = 'value'

# 查找：O(1)
value = hash_table.get('key')

# 删除：O(1)
del hash_table['key']
```

### 2.8 图

```python
from collections import defaultdict

class Graph:
    def __init__(self):
        self.graph = defaultdict(list)
    
    def add_edge(self, u, v):
        self.graph[u].append(v)
    
    def dfs(self, start, visited=None):
        if visited is None:
            visited = set()
        visited.add(start)
        print(start)
        for neighbor in self.graph[start]:
            if neighbor not in visited:
                self.dfs(neighbor, visited)
    
    def bfs(self, start):
        visited = set()
        queue = [start]
        visited.add(start)
        while queue:
            node = queue.pop(0)
            print(node)
            for neighbor in self.graph[node]:
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(neighbor)
```

## 3. 排序算法

### 3.1 冒泡排序

```python
def bubble_sort(arr):
    n = len(arr)
    for i in range(n):
        for j in range(0, n - i - 1):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
    return arr

# 时间复杂度：O(n²)
# 空间复杂度：O(1)
```

### 3.2 选择排序

```python
def selection_sort(arr):
    n = len(arr)
    for i in range(n):
        min_idx = i
        for j in range(i + 1, n):
            if arr[j] < arr[min_idx]:
                min_idx = j
        arr[i], arr[min_idx] = arr[min_idx], arr[i]
    return arr

# 时间复杂度：O(n²)
# 空间复杂度：O(1)
```

### 3.3 插入排序

```python
def insertion_sort(arr):
    for i in range(1, len(arr)):
        key = arr[i]
        j = i - 1
        while j >= 0 and arr[j] > key:
            arr[j + 1] = arr[j]
            j -= 1
        arr[j + 1] = key
    return arr

# 时间复杂度：O(n²)
# 空间复杂度：O(1)
```

### 3.4 快速排序

```python
def quick_sort(arr):
    if len(arr) <= 1:
        return arr
    pivot = arr[len(arr) // 2]
    left = [x for x in arr if x < pivot]
    middle = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]
    return quick_sort(left) + middle + quick_sort(right)

# 时间复杂度：平均O(n log n)，最坏O(n²)
# 空间复杂度：O(log n)
```

### 3.5 归并排序

```python
def merge_sort(arr):
    if len(arr) <= 1:
        return arr
    mid = len(arr) // 2
    left = merge_sort(arr[:mid])
    right = merge_sort(arr[mid:])
    return merge(left, right)

def merge(left, right):
    result = []
    i = j = 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1
    result.extend(left[i:])
    result.extend(right[j:])
    return result

# 时间复杂度：O(n log n)
# 空间复杂度：O(n)
```

### 3.6 堆排序

```python
import heapq

def heap_sort(arr):
    heap = []
    for item in arr:
        heapq.heappush(heap, item)
    return [heapq.heappop(heap) for _ in range(len(heap))]

# 时间复杂度：O(n log n)
# 空间复杂度：O(n)
```

## 4. 搜索算法

### 4.1 线性搜索

```python
def linear_search(arr, target):
    for i, item in enumerate(arr):
        if item == target:
            return i
    return -1

# 时间复杂度：O(n)
```

### 4.2 二分搜索

```python
def binary_search(arr, target):
    left, right = 0, len(arr) - 1
    while left <= right:
        mid = (left + right) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    return -1

# 时间复杂度：O(log n)
# 要求：数组必须有序
```

## 5. 动态规划

### 5.1 斐波那契数列

```python
def fibonacci(n, memo={}):
    if n in memo:
        return memo[n]
    if n <= 2:
        return 1
    memo[n] = fibonacci(n - 1, memo) + fibonacci(n - 2, memo)
    return memo[n]

# 时间复杂度：O(n)
# 空间复杂度：O(n)
```

### 5.2 最长公共子序列

```python
def lcs(s1, s2):
    m, n = len(s1), len(s2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if s1[i - 1] == s2[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1
            else:
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])
    
    return dp[m][n]
```

### 5.3 背包问题

```python
def knapsack(weights, values, capacity):
    n = len(weights)
    dp = [[0] * (capacity + 1) for _ in range(n + 1)]
    
    for i in range(1, n + 1):
        for w in range(1, capacity + 1):
            if weights[i - 1] <= w:
                dp[i][w] = max(
                    dp[i - 1][w],
                    dp[i - 1][w - weights[i - 1]] + values[i - 1]
                )
            else:
                dp[i][w] = dp[i - 1][w]
    
    return dp[n][capacity]
```

## 6. 贪心算法

### 6.1 活动选择问题

```python
def activity_selection(activities):
    # 按结束时间排序
    activities.sort(key=lambda x: x[1])
    selected = [activities[0]]
    
    for activity in activities[1:]:
        if activity[0] >= selected[-1][1]:
            selected.append(activity)
    
    return selected
```

### 6.2 找零问题

```python
def make_change(amount, coins):
    coins.sort(reverse=True)
    change = []
    
    for coin in coins:
        while amount >= coin:
            change.append(coin)
            amount -= coin
    
    return change if amount == 0 else None
```

## 7. 回溯算法

### 7.1 N皇后问题

```python
def solve_n_queens(n):
    def is_safe(board, row, col):
        for i in range(row):
            if board[i] == col or \
               board[i] - i == col - row or \
               board[i] + i == col + row:
                return False
        return True
    
    def backtrack(board, row):
        if row == n:
            solutions.append(board[:])
            return
        for col in range(n):
            if is_safe(board, row, col):
                board[row] = col
                backtrack(board, row + 1)
                board[row] = -1
    
    solutions = []
    board = [-1] * n
    backtrack(board, 0)
    return solutions
```

### 7.2 全排列

```python
def permutations(nums):
    def backtrack(path, used):
        if len(path) == len(nums):
            result.append(path[:])
            return
        for i in range(len(nums)):
            if not used[i]:
                used[i] = True
                path.append(nums[i])
                backtrack(path, used)
                path.pop()
                used[i] = False
    
    result = []
    backtrack([], [False] * len(nums))
    return result
```

## 8. 图算法

### 8.1 最短路径（Dijkstra）

```python
import heapq

def dijkstra(graph, start):
    distances = {node: float('inf') for node in graph}
    distances[start] = 0
    pq = [(0, start)]
    
    while pq:
        current_dist, current = heapq.heappop(pq)
        if current_dist > distances[current]:
            continue
        for neighbor, weight in graph[current].items():
            distance = current_dist + weight
            if distance < distances[neighbor]:
                distances[neighbor] = distance
                heapq.heappush(pq, (distance, neighbor))
    
    return distances
```

### 8.2 最小生成树（Kruskal）

```python
class UnionFind:
    def __init__(self, n):
        self.parent = list(range(n))
    
    def find(self, x):
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])
        return self.parent[x]
    
    def union(self, x, y):
        self.parent[self.find(x)] = self.find(y)

def kruskal(edges, n):
    edges.sort(key=lambda x: x[2])
    uf = UnionFind(n)
    mst = []
    
    for u, v, weight in edges:
        if uf.find(u) != uf.find(v):
            uf.union(u, v)
            mst.append((u, v, weight))
    
    return mst
```

## 9. 字符串算法

### 9.1 KMP算法

```python
def kmp_search(text, pattern):
    def build_lps(pattern):
        lps = [0] * len(pattern)
        length = 0
        i = 1
        while i < len(pattern):
            if pattern[i] == pattern[length]:
                length += 1
                lps[i] = length
                i += 1
            else:
                if length != 0:
                    length = lps[length - 1]
                else:
                    lps[i] = 0
                    i += 1
        return lps
    
    lps = build_lps(pattern)
    i = j = 0
    while i < len(text):
        if text[i] == pattern[j]:
            i += 1
            j += 1
        if j == len(pattern):
            return i - j
        elif i < len(text) and text[i] != pattern[j]:
            if j != 0:
                j = lps[j - 1]
            else:
                i += 1
    return -1
```

## 10. 复杂度分析

### 10.1 时间复杂度

- **O(1)**：常数时间
- **O(log n)**：对数时间
- **O(n)**：线性时间
- **O(n log n)**：线性对数时间
- **O(n²)**：平方时间
- **O(2ⁿ)**：指数时间

### 10.2 空间复杂度

- **O(1)**：常数空间
- **O(n)**：线性空间
- **O(n²)**：平方空间

## 11. 总结

Python算法与数据结构：
- **数据结构**：列表、栈、队列、树、图等
- **排序算法**：冒泡、快速、归并等
- **搜索算法**：线性、二分搜索
- **动态规划**：解决最优化问题
- **贪心算法**：局部最优解
- **回溯算法**：解决组合问题

掌握这些算法和数据结构可以提高编程能力和问题解决能力。

