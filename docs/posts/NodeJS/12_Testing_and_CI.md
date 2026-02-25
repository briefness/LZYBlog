# Node.js 深度实战（十二）—— 测试策略与工程化

没有测试的代码就是负债。Vitest + Supertest 构建让团队有底气迭代的测试体系。

---

## 1. 测试金字塔

```mermaid
graph TD
    A["端到端测试 E2E\nPlaywright\n少量，慢，贵\n关键业务流程"]
    B["集成测试 Integration\nSupertest\n中等数量\nAPI 接口、数据库交互"]
    C["单元测试 Unit\nVitest\n大量，快，廉价\n纯函数、工具类、业务逻辑"]

    C --> B --> A
    style C fill:#4ecdc4,color:#fff
    style B fill:#f7dc6f,color:#333
    style A fill:#ff6b6b,color:#fff
```

## 2. Vitest：现代 Node.js 单元测试

Vitest 与 Jest API 兼容，但基于 Vite，速度更快，原生支持 ESM 和 TypeScript。

```bash
npm install -D vitest @vitest/coverage-v8
```

```json
{
  "scripts": {
    "test": "vitest run",
    "test:watch": "vitest",
    "test:coverage": "vitest run --coverage"
  }
}
```

### 基础单元测试

```typescript
// src/utils/price.test.ts
import { describe, it, expect } from 'vitest';
import { calculateDiscount, formatPrice } from './price.js';

describe('price 工具函数', () => {
  describe('calculateDiscount', () => {
    it('普通用户享受 0 折扣', () => {
      expect(calculateDiscount(100, 'user')).toBe(100);
    });

    it('VIP 用户享受 9 折优惠', () => {
      expect(calculateDiscount(100, 'vip')).toBe(90);
    });

    it('价格为 0 时不抛出错误', () => {
      expect(() => calculateDiscount(0, 'vip')).not.toThrow();
    });

    it('负数价格应该抛出错误', () => {
      expect(() => calculateDiscount(-10, 'user')).toThrow('价格不能为负数');
    });
  });

  describe('formatPrice', () => {
    it('正确格式化人民币', () => {
      expect(formatPrice(1234.5)).toBe('¥1,234.50');
    });
  });
});
```

### Mock 和 Stub

```typescript
// src/services/email.test.ts
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { sendWelcomeEmail } from './email.js';
import * as nodemailer from 'nodemailer';

// Mock 整个模块
vi.mock('nodemailer');

describe('sendWelcomeEmail', () => {
  const mockSendMail = vi.fn().mockResolvedValue({ messageId: 'test-id' });

  beforeEach(() => {
    vi.mocked(nodemailer.createTransport).mockReturnValue({
      sendMail: mockSendMail,
    } as any);
  });

  afterEach(() => {
    vi.clearAllMocks();
  });

  it('发送包含正确内容的欢迎邮件', async () => {
    await sendWelcomeEmail({ email: 'test@example.com', name: '张三' });

    expect(mockSendMail).toHaveBeenCalledOnce();
    expect(mockSendMail).toHaveBeenCalledWith(
      expect.objectContaining({
        to: 'test@example.com',
        subject: expect.stringContaining('欢迎'),
      })
    );
  });
});
```

## 3. Supertest：API 集成测试

```bash
npm install -D supertest @types/supertest
```

```typescript
// tests/users.test.ts
import { describe, it, expect, beforeAll, afterAll } from 'vitest';
import supertest from 'supertest';
import { buildApp } from '../src/index.js';
import type { FastifyInstance } from 'fastify';

describe('Users API', () => {
  let app: FastifyInstance;
  let authToken: string;

  beforeAll(async () => {
    app = await buildApp();
    await app.ready();

    // 准备测试数据：创建一个测试用户并登录获取 token
    const loginRes = await supertest(app.server)
      .post('/api/v1/auth/login')
      .send({ email: 'admin@test.com', password: 'test123' });

    authToken = loginRes.body.token;
  });

  afterAll(async () => {
    await app.close();
  });

  it('GET /api/v1/users — 未认证时返回 401', async () => {
    const res = await supertest(app.server)
      .get('/api/v1/users')
      .expect(401);

    expect(res.body.error).toBe('Unauthorized');
  });

  it('GET /api/v1/users — 认证后返回用户列表', async () => {
    const res = await supertest(app.server)
      .get('/api/v1/users')
      .set('Authorization', `Bearer ${authToken}`)
      .expect(200);

    expect(res.body.data).toBeInstanceOf(Array);
    expect(res.body.total).toBeTypeOf('number');
  });

  it('POST /api/v1/users — 创建用户（Schema 验证）', async () => {
    // 测试无效参数
    await supertest(app.server)
      .post('/api/v1/users')
      .set('Authorization', `Bearer ${authToken}`)
      .send({ email: 'not-an-email', name: '' })
      .expect(400);

    // 测试有效参数
    const res = await supertest(app.server)
      .post('/api/v1/users')
      .set('Authorization', `Bearer ${authToken}`)
      .send({ email: `test-${Date.now()}@example.com`, name: '测试用户' })
      .expect(201);

    expect(res.body.id).toBeTypeOf('number');
    expect(res.body.email).toContain('@');
  });
});
```

## 4. 测试数据库隔离

```typescript
// tests/setup.ts
import { PrismaClient } from '@prisma/client';
import { beforeAll, afterAll, beforeEach } from 'vitest';

// 使用独立的测试数据库
const prisma = new PrismaClient({
  datasources: { db: { url: process.env.TEST_DATABASE_URL } },
});

beforeAll(async () => {
  // 清空测试数据库并运行迁移
  await prisma.$executeRaw`TRUNCATE TABLE "User", "Post" CASCADE`;
  // 插入种子数据
  await seedTestData(prisma);
});

afterAll(async () => {
  await prisma.$disconnect();
});

// vitest.config.ts 中配置
import { defineConfig } from 'vitest/config';

export default defineConfig({
  test: {
    globalSetup: ['./tests/setup.ts'],
    coverage: {
      provider: 'v8',
      reporter: ['text', 'html', 'lcov'],
      thresholds: {
        lines: 80,    // 行覆盖率低于 80% 则 CI 失败
        functions: 75,
        branches: 70,
      },
    },
  },
});
```

## 5. GitHub Actions CI/CD

```yaml
# .github/workflows/ci.yml
name: CI/CD Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:16
        env:
          POSTGRES_DB: test_db
          POSTGRES_PASSWORD: test123
        ports: ['5432:5432']
        options: >-
          --health-cmd pg_isready
          --health-interval 10s

    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-node@v4
        with:
          node-version: '24'
          cache: 'npm'

      - run: npm ci

      - name: 运行数据库迁移
        run: npx prisma migrate deploy
        env:
          TEST_DATABASE_URL: postgresql://postgres:test123@localhost:5432/test_db

      - name: 安全审计
        run: npm audit --audit-level=high

      - name: 运行测试（含覆盖率）
        run: npm run test:coverage
        env:
          TEST_DATABASE_URL: postgresql://postgres:test123@localhost:5432/test_db

      - name: 上传覆盖率报告
        uses: codecov/codecov-action@v4
        with:
          file: ./coverage/lcov.info

  deploy:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
      - uses: actions/checkout@v4
      - name: 构建 Docker 镜像
        run: docker build -t myapp:${{ github.sha }} .
      - name: 推送镜像
        run: |
          echo ${{ secrets.DOCKER_TOKEN }} | docker login -u ${{ secrets.DOCKER_USER }} --password-stdin
          docker push myapp:${{ github.sha }}
```

## 总结

- 单元测试覆盖纯函数和核心业务逻辑；API 集成测试用 Supertest 验证接口行为
- 在 CI 中设置覆盖率阈值（80% 行覆盖），低于阈值则构建失败
- 测试数据库独立于开发/生产，使用 `TRUNCATE + 种子数据` 保证每次测试幂等
- GitHub Actions 自动化：提交后自动测试，测试通过才能部署

---

下一章探讨 **容器化与云原生部署**，打造最小化 Docker 镜像和零停机部署方案。
