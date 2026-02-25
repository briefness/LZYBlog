# Node.js 深度实战（十六）—— 错误处理体系与环境变量管理

一个没有完善错误处理的 Node.js 服务，就像没有安全网的走钢丝。这章把两个被忽视的生产基础设施补齐。

---

## Part 1：错误处理体系

## 1. Node.js 错误类型

```mermaid
graph TD
    A["Node.js 错误"] --> B["操作性错误\nOperational Error\n可预期、可恢复"]
    A --> C["编程错误\nProgrammer Error\n代码 bug，不应捕获"]

    B --> D["网络超时\n文件不存在\n数据库连接失败\n用户输入非法"]
    C --> E["undefined 变量\n类型错误\n断言失败"]

    style B fill:#4ecdc4,color:#fff
    style C fill:#ff6b6b,color:#fff
```

**操作性错误**：应当捕获并优雅处理（返回 4xx/5xx 响应）。

**编程错误**：让进程崩溃，由 PM2/K8s 重启——不要试图恢复，掩盖 bug 只会带来更大问题。

## 2. 自定义错误类：AppError

```typescript
// src/lib/errors.ts

// 错误代码枚举（前后端共享契约）
export enum ErrorCode {
  // 通用
  VALIDATION_ERROR = 'VALIDATION_ERROR',
  NOT_FOUND = 'NOT_FOUND',
  UNAUTHORIZED = 'UNAUTHORIZED',
  FORBIDDEN = 'FORBIDDEN',
  CONFLICT = 'CONFLICT',
  // 业务
  INSUFFICIENT_STOCK = 'INSUFFICIENT_STOCK',
  USER_ALREADY_EXISTS = 'USER_ALREADY_EXISTS',
  INVALID_CREDENTIALS = 'INVALID_CREDENTIALS',
  // 系统
  DATABASE_ERROR = 'DATABASE_ERROR',
  EXTERNAL_SERVICE_ERROR = 'EXTERNAL_SERVICE_ERROR',
}

export class AppError extends Error {
  public readonly code: ErrorCode;
  public readonly statusCode: number;
  public readonly isOperational: boolean;
  public readonly context?: Record<string, unknown>;

  constructor(
    message: string,
    code: ErrorCode,
    statusCode: number = 500,
    context?: Record<string, unknown>,
  ) {
    super(message);
    this.name = 'AppError';
    this.code = code;
    this.statusCode = statusCode;
    this.isOperational = true;  // 标记为可操作错误
    this.context = context;

    // 修复 TypeScript 继承 Error 的 prototype 问题
    Object.setPrototypeOf(this, new.target.prototype);
    Error.captureStackTrace(this, this.constructor);
  }

  // 常用工厂方法
  static notFound(resource: string, id?: string | number) {
    return new AppError(
      `${resource}${id ? ` (id: ${id})` : ''} 不存在`,
      ErrorCode.NOT_FOUND,
      404,
      { resource, id },
    );
  }

  static unauthorized(message = '未认证，请先登录') {
    return new AppError(message, ErrorCode.UNAUTHORIZED, 401);
  }

  static forbidden(message = '无权访问此资源') {
    return new AppError(message, ErrorCode.FORBIDDEN, 403);
  }

  static conflict(message: string, context?: Record<string, unknown>) {
    return new AppError(message, ErrorCode.CONFLICT, 409, context);
  }

  static validation(message: string, context?: Record<string, unknown>) {
    return new AppError(message, ErrorCode.VALIDATION_ERROR, 400, context);
  }
}
```

### 使用示例

```typescript
// 路由中抛出业务错误
app.get('/users/:id', async (request, reply) => {
  const user = await app.db.user.findUnique({
    where: { id: parseInt(request.params.id) },
  });

  if (!user) {
    throw AppError.notFound('User', request.params.id);
    // → 自动返回 404 + { error: 'NOT_FOUND', message: 'User (id: 42) 不存在' }
  }

  if (user.role !== 'ADMIN' && request.user.id !== user.id) {
    throw AppError.forbidden();
  }

  return user;
});
```

## 3. Fastify 全局错误处理器

```typescript
// src/plugins/error-handler.ts
import fp from 'fastify-plugin';
import { AppError, ErrorCode } from '../lib/errors.js';
import { Prisma } from '@prisma/client';
import { ZodError } from 'zod';

export default fp(async (app) => {
  app.setErrorHandler((error, request, reply) => {
    // 1. AppError（已知业务错误）
    if (error instanceof AppError) {
      return reply.code(error.statusCode).send({
        error: error.code,
        message: error.message,
        ...(process.env.NODE_ENV !== 'production' && { context: error.context }),
      });
    }

    // 2. Prisma 唯一约束冲突（如邮箱重复）
    if (error instanceof Prisma.PrismaClientKnownRequestError) {
      if (error.code === 'P2002') {
        const fields = (error.meta?.target as string[])?.join(', ');
        return reply.code(409).send({
          error: ErrorCode.CONFLICT,
          message: `${fields} 已存在，请换一个`,
        });
      }
      if (error.code === 'P2025') {
        return reply.code(404).send({
          error: ErrorCode.NOT_FOUND,
          message: '记录不存在',
        });
      }
    }

    // 3. Fastify Schema 验证错误
    if (error.validation) {
      return reply.code(400).send({
        error: ErrorCode.VALIDATION_ERROR,
        message: '请求参数不合法',
        details: error.validation,
      });
    }

    // 4. Zod 验证错误
    if (error instanceof ZodError) {
      return reply.code(400).send({
        error: ErrorCode.VALIDATION_ERROR,
        message: '数据验证失败',
        details: error.flatten(),
      });
    }

    // 5. 未知错误（编程错误）
    request.log.error({ err: error, reqId: request.id }, '未处理的服务器错误');

    return reply.code(500).send({
      error: 'INTERNAL_SERVER_ERROR',
      message: '服务器内部错误，请稍后重试',
      requestId: request.id,  // 让用户可以反馈给开发者查日志
    });
  });
});
```

## 4. 全局未处理错误捕获

```typescript
// src/index.ts（服务启动入口）

// 捕获未被 try/catch 处理的 Promise 拒绝
process.on('unhandledRejection', (reason, promise) => {
  console.error('未处理的 Promise 拒绝：', reason);
  // 记录后退出，让 PM2/K8s 重启
  // 注意：不要继续运行，状态已经不可信
  process.exit(1);
});

// 捕获同步代码中的未处理异常
process.on('uncaughtException', (error) => {
  console.error('未捕获的异常：', error);
  // 这是编程错误，必须退出
  process.exit(1);
});

// 优雅关闭（接收到 SIGTERM 信号时，如 K8s 滚动更新）
const gracefulShutdown = async (signal: string) => {
  console.log(`接收到 ${signal}，开始优雅关闭...`);
  try {
    await app.close();           // 停止接受新请求，等待现有请求完成
    await prisma.$disconnect();  // 关闭数据库连接
    console.log('服务已优雅关闭');
    process.exit(0);
  } catch (err) {
    console.error('关闭失败：', err);
    process.exit(1);
  }
};

process.on('SIGTERM', () => gracefulShutdown('SIGTERM'));
process.on('SIGINT', () => gracefulShutdown('SIGINT'));   // Ctrl+C
```

---

## Part 2：环境变量管理

## 5. 为什么要验证环境变量

启动时就检查所有必需的环境变量，而不是等到运行时才发现缺少某个 KEY——否则可能在凌晨 3 点，客户投诉时才发现部署时忘了配置 `JWT_SECRET`。

## 6. Zod 验证环境变量

```bash
npm install zod dotenv
```

```typescript
// src/lib/env.ts
import { z } from 'zod';
import { config } from 'dotenv';

// 开发/测试环境从 .env 文件读取
config({ path: process.env.NODE_ENV === 'test' ? '.env.test' : '.env' });

const envSchema = z.object({
  // 服务配置
  NODE_ENV: z.enum(['development', 'test', 'production']).default('development'),
  PORT: z.coerce.number().int().min(1).max(65535).default(3000),
  HOST: z.string().default('0.0.0.0'),

  // 数据库
  DATABASE_URL: z.string().url('DATABASE_URL 必须是有效的数据库连接字符串'),

  // JWT
  JWT_SECRET: z.string().min(32, 'JWT_SECRET 长度至少 32 个字符'),
  JWT_EXPIRES_IN: z.string().default('15m'),

  // Redis（可选）
  REDIS_URL: z.string().url().optional(),

  // 邮件（可选）  
  SMTP_HOST: z.string().optional(),
  SMTP_PORT: z.coerce.number().optional(),
  SMTP_USER: z.string().optional(),
  SMTP_PASS: z.string().optional(),
});

// 启动时立即验证（失败则进程退出，不会带着错误配置启动）
const parsed = envSchema.safeParse(process.env);

if (!parsed.success) {
  console.error('❌ 环境变量配置错误：');
  const errors = parsed.error.flatten().fieldErrors;
  for (const [key, messages] of Object.entries(errors)) {
    console.error(`  ${key}: ${messages?.join(', ')}`);
  }
  process.exit(1);
}

export const env = parsed.data;
// env 的类型由 Zod Schema 完全推断，完全类型安全！
```

### .env 文件结构

```bash
# .env（开发环境，提交 .env.example 而不是 .env！）
NODE_ENV=development
PORT=3000

# 数据库
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/myapp

# 安全
JWT_SECRET=your-super-secret-jwt-key-at-least-32-chars-long
JWT_EXPIRES_IN=15m

# 可选
REDIS_URL=redis://localhost:6379
```

```bash
# .env.example（提交到 Git，供团队参考配置结构）
NODE_ENV=development
PORT=3000
DATABASE_URL=postgresql://user:password@localhost:5432/myapp
JWT_SECRET=  # 至少32位随机字符串
JWT_EXPIRES_IN=15m
REDIS_URL=   # 可选
```

```bash
# .gitignore 中必须包含：
.env
.env.local
.env.*.local
# 不要忽略 .env.example！
```

### 在代码中使用

```typescript
// 任何地方直接 import，完全类型安全
import { env } from './lib/env.js';

await app.listen({ port: env.PORT, host: env.HOST });
// env.PORT 是 number 类型，不是 string
// env.REDIS_URL 是 string | undefined，会提示你处理 undefined 情况
```

## 7. 错误处理完整流程图

```mermaid
flowchart TD
    A["HTTP 请求"] --> B["路由处理函数"]
    B --> C{抛出错误？}

    C --"AppError\n业务错误"--> D["全局 setErrorHandler\n返回对应 4xx"]
    C --"Prisma 约束错误"--> E["转换为 409 Conflict"]
    C --"未知错误"--> F["记录日志\n返回 500"]
    C --"无错误"--> G["正常响应"]

    H["unhandledRejection\nuncaughtException"] --> I["记录错误\nprocess.exit(1)"]
    I --> J["PM2 / K8s 自动重启"]

    style D fill:#4ecdc4,color:#fff
    style F fill:#ff6b6b,color:#fff
    style J fill:#f7dc6f,color:#333
```

## 总结

- 错误分两类：**操作性错误**（可恢复，返回 4xx）和**编程错误**（让进程崩溃，由 PM2 重启）
- `AppError` 统一错误结构，工厂方法简化常见错误创建
- `unhandledRejection` 和 `uncaughtException` 必须监听，记录日志后退出
- 优雅关闭（SIGTERM）让 K8s 滚动更新时不丢失进行中的请求
- 用 **Zod 验证环境变量**，启动时即发现配置错误，杜绝带错误配置运行

---

下一章探讨 **结构化日志与调试技巧**，用 Pino 打造生产级日志体系。
