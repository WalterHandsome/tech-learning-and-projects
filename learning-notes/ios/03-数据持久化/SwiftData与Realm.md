# SwiftData 与 Realm
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. SwiftData 数据模型（iOS 17+）

```swift
import SwiftData

@Model
class Task {
    var id: UUID
    var title: String
    var isCompleted: Bool
    var createdAt: Date
    @Relationship(deleteRule: .cascade) var subtasks: [Subtask]

    init(title: String) {
        self.id = UUID()
        self.title = title
        self.isCompleted = false
        self.createdAt = Date()
        self.subtasks = []
    }
}

@Model
class Subtask {
    var title: String
    var isDone: Bool
    var task: Task?

    init(title: String) {
        self.title = title
        self.isDone = false
    }
}
```

## 2. SwiftData 容器配置

```swift
import SwiftUI

@main
struct MyApp: App {
    var body: some Scene {
        WindowGroup {
            ContentView()
        }
        .modelContainer(for: [Task.self, Subtask.self])
    }
}
```

## 3. SwiftData CRUD（SwiftUI）

```swift
struct TaskListView: View {
    @Environment(\.modelContext) private var context
    @Query(sort: \Task.createdAt, order: .reverse) var tasks: [Task]

    var body: some View {
        List {
            ForEach(tasks) { task in
                HStack {
                    Image(systemName: task.isCompleted ? "checkmark.circle.fill" : "circle")
                    Text(task.title)
                }
                .onTapGesture { task.isCompleted.toggle() }
            }
            .onDelete(perform: deleteTasks)
        }
    }

    func addTask(title: String) {
        let task = Task(title: title)
        context.insert(task)
    }

    func deleteTasks(at offsets: IndexSet) {
        for index in offsets {
            context.delete(tasks[index])
        }
    }
}
```

## 4. @Query 过滤与排序

```swift
// 过滤未完成任务
@Query(filter: #Predicate<Task> { !$0.isCompleted },
       sort: \Task.createdAt)
var pendingTasks: [Task]

// 动态过滤
struct FilteredView: View {
    @Query var tasks: [Task]

    init(showCompleted: Bool) {
        let predicate = #Predicate<Task> { task in
            showCompleted || !task.isCompleted
        }
        _tasks = Query(filter: predicate, sort: \Task.createdAt)
    }

    var body: some View {
        List(tasks) { task in Text(task.title) }
    }
}
```

## 5. Realm 数据模型

```swift
import RealmSwift

class Dog: Object {
    @Persisted(primaryKey: true) var id: ObjectId
    @Persisted var name: String
    @Persisted var age: Int
    @Persisted var owner: Person?
}

class Person: Object {
    @Persisted(primaryKey: true) var id: ObjectId
    @Persisted var name: String
    @Persisted var dogs: List<Dog>
}
```

## 6. Realm CRUD

```swift
let realm = try! Realm()

// 创建
try! realm.write {
    let dog = Dog()
    dog.name = "旺财"
    dog.age = 3
    realm.add(dog)
}

// 查询
let puppies = realm.objects(Dog.self).where { $0.age < 2 }
let sorted = realm.objects(Dog.self).sorted(byKeyPath: "name")

// 更新
try! realm.write {
    dog.age += 1
}

// 删除
try! realm.write {
    realm.delete(dog)
}
```
