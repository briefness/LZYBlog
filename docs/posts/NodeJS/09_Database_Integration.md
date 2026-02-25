# Node.js 深度实战（九）—— 数据库集成：Prisma ORM 实战

type-safe 的数据库操作，从 Schema 到 Query 全程 TypeScript 类型覆盖。

---

## 1. 为什么选 Prisma

2026 年 Node.js 生态主流 ORM 对比：

| ORM | 类型安全 | Schema 优先 | 迁移管理 | 性能 |
|-----|---------|------------|---------|------|
| **Prisma 6** | ✅ 完全类型安全 | ✅ schema.prisma | ✅ 内置 | ⭐⭐⭐ |
| **Drizzle ORM** | ✅ 完全类型安全 | TypeScript 定义 | ✅ | ⭐⭐⭐⭐ |
| **TypeORM** | ⚠️ 部分 | 装饰器或 Entity | ✅ | ⭐⭐⭐ |
| **Sequelize** | ⚠️ 弱 | 模型定义 | ✅ | ⭐⭐ |

**Prisma 的核心优势：** 所有查询结果都有精确的 TypeScript 类型，不需要手写任何类型定义。

### Drizzle ORM 快速对比

Drizzle 在 2026 年凭借极高的性能和 SQL-like 的查询风格成为热门替代方案，**适合对性能敏感或偏好直控 SQL 的项目**：

```typescript
// Drizzle 方式（用 TypeScript 直接定义 Schema，无独立 .prisma 文件）
import { pgTable, serial, text, varchar } from 'drizzle-orm/pg-core';
import { drizzle } from 'drizzle-orm/node-postgres';
import { eq } from 'drizzle-orm';
import pg from 'pg';

// Schema 定义（纯 TypeScript）
export const users = pgTable('users', {
  id: serial('id').primaryKey(),
  name: varchar('name', { length: 100 }).notNull(),
  email: text('email').notNull().unique(),
});

const pool = new pg.Pool({ connectionString: process.env.DATABASE_URL });
const db = drizzle(pool, { schema: { users } });

// 查询（SQL-like 写法，IDE 有完整类型提示）
const result = await db.select().from(users).where(eq(users.id, 1));
// result 类型自动推断为 { id: number; name: string; email: string }[]
```

| 选择 Prisma | 选择 Drizzle |
|------------|-------------|
| 不熟悉 SQL，要声明式 ORM | 熟悉 SQL，要更细粒度的控制 |
| 需要 Prisma Studio 可视化 | 极致性能（Drizzle 无 Runtime 开销）|
| 团队以 Schema.prisma 为契约 | 想在 TypeScript 中直接写 Schema |

> 本章以 Prisma 为主要示例，Drizzle 的 API 风格参考 [官方文档](https://orm.drizzle.team)。


## 2. 项目初始化

```bash
npm install prisma @prisma/client
npx prisma init --datasource-provider postgresql
```

## 3. Schema 设计

```prisma
// prisma/schema.prisma
generator client {
  provider = "prisma-client-js"
  // Prisma 6 新特性：使用 Rust 原生驱动，性能提升 50%
  previewFeatures = ["tracing"]
}

datasource db {
  provider = "postgresql"
  url      = env("DATABASE_URL")
}

model User {
  id        Int      @id @default(autoincrement())
  email     String   @unique
  name      String
  role      Role     @default(USER)
  posts     Post[]
  profile   Profile?
  createdAt DateTime @default(now())
  updatedAt DateTime @updatedAt

  @@index([email])
}

model Post {
  id        Int      @id @default(autoincrement())
  title     String
  content   String?
  published Boolean  @default(false)
  author    User     @relation(fields: [authorId], references: [id])
  authorId  Int
  tags      Tag[]    @relation("PostTags")  // 多对多
  createdAt DateTime @default(now())

  @@index([authorId])
}

model Tag {
  id    Int    @id @default(autoincrement())
  name  String @unique
  posts Post[] @relation("PostTags")
}

model Profile {
  id     Int    @id @default(autoincrement())
  bio    String?
  avatar String?
  user   User   @relation(fields: [userId], references: [id])
  userId Int    @unique
}

enum Role {
  USER
  ADMIN
}
```

### 运行迁移

```bash
# 开发环境：创建迁移文件并应用
npx prisma migrate dev --name "init"

# 生产环境：只应用已有迁移
npx prisma migrate deploy

# 生成 Prisma Client（Schema 变更后必须重新生成）
npx prisma generate

# 可视化数据库（开发利器）
npx prisma studio
```

## 4. 基础 CRUD 操作

```typescript
import { PrismaClient } from '@prisma/client';

const prisma = new PrismaClient({
  log: ['query', 'info', 'warn', 'error'],  // 开发环境打印所有 SQL
});

// ✅ 创建
const user = await prisma.user.create({
  data: {
    email: 'test@example.com',
    name: '张三',
    profile: {
      create: { bio: 'Node.js 开发者' }  // 同时创建关联数据
    }
  },
  include: { profile: true }  // 返回时包含关联数据
});
// user 的类型是 (User & { profile: Profile | null })，完全推断！

// ✅ 查询（带条件）
const users = await prisma.user.findMany({
  where: {
    role: 'ADMIN',
    createdAt: { gte: new Date('2026-01-01') },
  },
  select: {
    id: true,
    name: true,
    email: true,
    // password: false  // 不返回敏感字段
  },
  orderBy: { createdAt: 'desc' },
  skip: 0,
  take: 20,
});

// ✅ 更新
const updated = await prisma.user.update({
  where: { id: 1 },
  data: { name: '李四', updatedAt: new Date() },
});

// ✅ 删除（软删除用 update，物理删除用 delete）
await prisma.user.delete({ where: { id: 1 } });

// ✅ 批量操作
const result = await prisma.user.updateMany({
  where: { role: 'USER', createdAt: { lt: new Date('2025-01-01') } },
  data: { role: 'ADMIN' },
});
console.log(`更新了 ${result.count} 条记录`);
```

## 5. 关联查询与 N+1 问题

```typescript
// ❌ N+1 问题：先查 users，再为每个 user 查 posts（N+1 次查询）
const users = await prisma.user.findMany();
for (const user of users) {
  const posts = await prisma.post.findMany({ where: { authorId: user.id } });
  // 100 个用户 = 101 次数据库查询！
}

// ✅ include：一次查询获取所有数据（JOIN）
const usersWithPosts = await prisma.user.findMany({
  include: {
    posts: {
      where: { published: true },  // 可以对关联数据加条件
      select: { id: true, title: true, createdAt: true },
      orderBy: { createdAt: 'desc' },
      take: 5,  // 每个用户最多 5 篇文章
    },
    profile: true,
    _count: { select: { posts: true } },  // 文章数量
  }
});

// usersWithPosts 的完整类型被自动推断，无需手写！
```

## 6. 事务

```typescript
// 方式一：interactive transaction（推荐，可处理复杂逻辑）
const result = await prisma.$transaction(async (tx) => {
  // tx 就是 prisma，但在同一事务中
  const order = await tx.order.create({
    data: { userId: 1, total: 100 }
  });

  // 扣减库存
  const product = await tx.product.update({
    where: { id: 5 },
    data: { stock: { decrement: 1 } }
  });

  if (product.stock < 0) {
    throw new Error('库存不足');  // 抛出错误，事务自动回滚
  }

  return order;
});

// 方式二：批量事务（顺序执行，更高效）
const [newUser, newProfile] = await prisma.$transaction([
  prisma.user.create({ data: { email: 'x@x.com', name: 'X' } }),
  prisma.profile.create({ data: { userId: 1, bio: 'test' } }),
]);
```

## 7. 集成到 Fastify 插件

### PrismaClient 单例（重要！）

```typescript
// src/lib/prisma.ts —— 单例，全局只创建一次
import { PrismaClient } from '@prisma/client';

// ❌ 错误：每次调用都 new PrismaClient()
// → 每个实例都有独立连接池，耗尽数据库连接！
// const prisma = new PrismaClient();

// ✅ 正确：单例模式（开发环境热重载防重复创建）
const globalForPrisma = globalThis as unknown as { prisma: PrismaClient };

export const prisma =
  globalForPrisma.prisma ??
  new PrismaClient({
    log: process.env.NODE_ENV === 'development'
      ? ['query', 'warn', 'error']
      : ['warn', 'error'],
    // 连接池配置
    datasources: {
      db: {
        url: process.env.DATABASE_URL,
      },
    },
  });

if (process.env.NODE_ENV !== 'production') {
  globalForPrisma.prisma = prisma;  // 开发时 HMR 不会重复创建
}
```

```typescript
// src/plugins/database.ts
import fp from 'fastify-plugin';
import { prisma } from '../lib/prisma.js';
import type { PrismaClient } from '@prisma/client';

declare module 'fastify' {
  interface FastifyInstance {
    db: PrismaClient;
  }
}

export default fp(async (app) => {
  app.decorate('db', prisma);

  app.addHook('onClose', async () => {
    await prisma.$disconnect();
  });
});
```

## 8. Redis 缓存集成

```bash
npm install ioredis
```

```typescript
// 缓存层封装
import Redis from 'ioredis';

const redis = new Redis(process.env.REDIS_URL);

async function getUserWithCache(userId: number) {
  const cacheKey = `user:${userId}`;

  // 先查缓存
  const cached = await redis.get(cacheKey);
  if (cached) {
    return JSON.parse(cached) as User;
  }

  // 缓存未命中，查数据库
  const user = await prisma.user.findUnique({ where: { id: userId } });

  if (user) {
    // 写入缓存，TTL 5 分钟
    await redis.setex(cacheKey, 300, JSON.stringify(user));
  }

  return user;
}

// 缓存失效（更新用户后调用）
async function invalidateUserCache(userId: number) {
  await redis.del(`user:${userId}`);
}
```

## 总结

- Prisma Schema 是单一事实来源：从 Schema 生成 Client 和迁移文件
- `include` 解决 N+1 问题；`select` 只返回需要的字段（减少网络传输）
- 事务使用 `$transaction` 中的 `tx` 参数，而非全局 `prisma`
- Redis 缓存热点数据，但要记得在数据变更时主动失效缓存

---

下一章探讨 **安全加固指南**，涵盖 OWASP Top 10 的 Node.js 防御实现。
