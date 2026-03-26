# Node.js 数据库操作

## 1. Prisma ORM（推荐）

```prisma
// prisma/schema.prisma
generator client {
  provider = "prisma-client-js"
}

datasource db {
  provider = "postgresql"
  url      = env("DATABASE_URL")
}

model User {
  id        Int      @id @default(autoincrement())
  email     String   @unique
  name      String?
  posts     Post[]
  createdAt DateTime @default(now())
}

model Post {
  id       Int    @id @default(autoincrement())
  title    String
  content  String?
  author   User   @relation(fields: [authorId], references: [id])
  authorId Int
}
```

```javascript
import { PrismaClient } from '@prisma/client';
const prisma = new PrismaClient();

// CRUD
const user = await prisma.user.create({
  data: { email: 'test@example.com', name: '张三' },
});

const users = await prisma.user.findMany({
  where: { name: { contains: '张' } },
  include: { posts: true },
  orderBy: { createdAt: 'desc' },
  skip: 0,
  take: 10,
});

await prisma.user.update({
  where: { id: 1 },
  data: { name: '李四' },
});

await prisma.user.delete({ where: { id: 1 } });

// 事务
await prisma.$transaction([
  prisma.user.create({ data: { email: 'a@b.com' } }),
  prisma.post.create({ data: { title: 'Hello', authorId: 1 } }),
]);
```

## 2. MongoDB（Mongoose）

```javascript
import mongoose from 'mongoose';

await mongoose.connect(process.env.MONGODB_URI);

const userSchema = new mongoose.Schema({
  name: { type: String, required: true },
  email: { type: String, unique: true },
  age: { type: Number, min: 0 },
  createdAt: { type: Date, default: Date.now },
});

const User = mongoose.model('User', userSchema);

// CRUD
const user = await User.create({ name: '张三', email: 'test@example.com' });
const users = await User.find({ age: { $gte: 18 } }).sort({ createdAt: -1 }).limit(10);
await User.findByIdAndUpdate(id, { name: '李四' });
await User.findByIdAndDelete(id);
```

## 3. Redis（ioredis）

```javascript
import Redis from 'ioredis';
const redis = new Redis(process.env.REDIS_URL);

// 基本操作
await redis.set('key', 'value', 'EX', 3600); // 1小时过期
const value = await redis.get('key');

// Hash
await redis.hset('user:1', { name: '张三', age: '25' });
const user = await redis.hgetall('user:1');

// 缓存模式
async function getCachedUser(id) {
  const cached = await redis.get(`user:${id}`);
  if (cached) return JSON.parse(cached);

  const user = await prisma.user.findUnique({ where: { id } });
  await redis.set(`user:${id}`, JSON.stringify(user), 'EX', 300);
  return user;
}
```
