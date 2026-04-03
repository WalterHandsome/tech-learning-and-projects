# Flutter 与 Dart 基础
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. Dart 语法

```dart
// 变量
var name = '张三';           // 类型推断
String city = '北京';        // 显式类型
final age = 25;              // 运行时常量
const pi = 3.14;             // 编译时常量
int? nullable;               // 可空类型

// 函数
String greet(String name, {int age = 18}) => 'Hello $name, $age';

// 类
class User {
  final String name;
  final int age;
  User({required this.name, required this.age});
}

// 异步
Future<String> fetchData() async {
  final response = await http.get(Uri.parse('https://api.example.com'));
  return response.body;
}
```

## 2. Widget 体系

```dart
// StatelessWidget（无状态）
class Greeting extends StatelessWidget {
  final String name;
  const Greeting({super.key, required this.name});

  @override
  Widget build(BuildContext context) {
    return Text('Hello, $name', style: const TextStyle(fontSize: 24));
  }
}

// StatefulWidget（有状态）
class Counter extends StatefulWidget {
  const Counter({super.key});
  @override
  State<Counter> createState() => _CounterState();
}

class _CounterState extends State<Counter> {
  int _count = 0;

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        Text('Count: $_count'),
        ElevatedButton(
          onPressed: () => setState(() => _count++),
          child: const Text('+1'),
        ),
      ],
    );
  }
}
```

## 3. 布局

```dart
// Row / Column（类似 Flex）
Row(
  mainAxisAlignment: MainAxisAlignment.spaceBetween,
  children: [Text('左'), Text('右')],
)

// Container（类似 div）
Container(
  padding: const EdgeInsets.all(16),
  margin: const EdgeInsets.symmetric(horizontal: 8),
  decoration: BoxDecoration(
    color: Colors.white,
    borderRadius: BorderRadius.circular(8),
    boxShadow: [BoxShadow(color: Colors.grey.shade200, blurRadius: 8)],
  ),
  child: const Text('卡片内容'),
)

// ListView（列表）
ListView.builder(
  itemCount: items.length,
  itemBuilder: (context, index) => ListTile(title: Text(items[index].name)),
)
```

## 4. 状态管理

```dart
// Provider（官方推荐）
class CounterProvider extends ChangeNotifier {
  int _count = 0;
  int get count => _count;
  void increment() { _count++; notifyListeners(); }
}

// 使用
ChangeNotifierProvider(
  create: (_) => CounterProvider(),
  child: Consumer<CounterProvider>(
    builder: (context, counter, child) => Text('${counter.count}'),
  ),
)

// Riverpod（更现代的方案）
final counterProvider = StateNotifierProvider<CounterNotifier, int>((ref) => CounterNotifier());
```
