# Express 与 Koa 框架
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. Express

```javascript
import express from 'express';
import cors from 'cors';

const app = express();

// 中间件
app.use(cors());
app.use(express.json());
app.use(express.urlencoded({ extended: true }));
app.use(express.static('public'));

// 路由
app.get('/api/users', async (req, res) => {
  const { page = 1, limit = 10 } = req.query;
  const users = await User.find().skip((page - 1) * limit).limit(limit);
  res.json({ code: 0, data: users });
});

app.get('/api/users/:id', async (req, res) => {
  const user = await User.findById(req.params.id);
  if (!user) return res.status(404).json({ code: 404, message: 'Not found' });
  res.json({ code: 0, data: user });
});

app.post('/api/users', async (req, res) => {
  const user = await User.create(req.body);
  res.status(201).json({ code: 0, data: user });
});

// 路由模块化
import { Router } from 'express';
const router = Router();
router.get('/', getUsers);
router.post('/', createUser);
app.use('/api/users', router);

// 错误处理中间件（4个参数）
app.use((err, req, res, next) => {
  console.error(err.stack);
  res.status(err.status || 500).json({
    code: err.status || 500,
    message: err.message || 'Internal Server Error',
  });
});

app.listen(3000, () => console.log('Server running on port 3000'));
```

## 2. Koa

```javascript
import Koa from 'koa';
import Router from '@koa/router';
import bodyParser from 'koa-bodyparser';

const app = new Koa();
const router = new Router();

// 洋葱模型中间件
app.use(async (ctx, next) => {
  const start = Date.now();
  await next();
  const ms = Date.now() - start;
  ctx.set('X-Response-Time', `${ms}ms`);
});

app.use(bodyParser());

// 路由
router.get('/api/users', async (ctx) => {
  ctx.body = { code: 0, data: await User.find() };
});

router.post('/api/users', async (ctx) => {
  const user = await User.create(ctx.request.body);
  ctx.status = 201;
  ctx.body = { code: 0, data: user };
});

app.use(router.routes());
app.use(router.allowedMethods());

// 错误处理
app.on('error', (err, ctx) => {
  console.error('Server error:', err);
});

app.listen(3000);
```

## 3. NestJS（简介）

```typescript
// NestJS：基于装饰器的 Node.js 框架，类似 Spring Boot
@Controller('users')
export class UsersController {
  constructor(private readonly usersService: UsersService) {}

  @Get()
  findAll(): Promise<User[]> {
    return this.usersService.findAll();
  }

  @Post()
  create(@Body() createUserDto: CreateUserDto): Promise<User> {
    return this.usersService.create(createUserDto);
  }
}

@Injectable()
export class UsersService {
  constructor(@InjectRepository(User) private repo: Repository<User>) {}
  findAll() { return this.repo.find(); }
  create(dto: CreateUserDto) { return this.repo.save(dto); }
}
```
