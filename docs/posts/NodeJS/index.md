# Node.js 深度实战系列

Node.js 深度实战系列是一套从零开始、循序渐进的系统性学习指南，覆盖从运行时原理到生产部署的完整知识体系。

基于 Node.js 24 LTS（2026 年最新长期支持版）编写，融合 2026 年前沿工程实践，适合零基础入门和有经验开发者查漏补缺。

## 📚 目录导航

### 第零阶段：极速入门
- **[00. 极速入门（零基础篇）](./00_Quick_Start.md)** 🆕
  - 10 分钟搭建第一个 Node.js 项目
  - 理解 require vs import、同步 vs 异步
  - 用 Fastify 写首个 REST API

### 第一阶段：运行时原理

- **[01. 架构与运行时原理](./01_Architecture_and_Runtime.md)**
  - V8 引擎与 libuv：Node.js 的灵魂
  - 内存模型：堆、栈与垃圾回收机制
  - Node.js 24 新特性一览

- **[02. 事件循环深度解析](./02_Event_Loop_Deep_Dive.md)** 🔥
  - 六个阶段的完整流程图解
  - `process.nextTick` vs `queueMicrotask` vs `setImmediate`
  - 异步编程进化史：回调 → Promise → async/await

- **[03. 模块系统：ESM、CJS 与未来](./03_Module_System.md)**
  - CommonJS 原理剖析（`module.exports` 的本质）
  - ES Modules 在 Node.js 中的完整实现
  - 双模块包的正确编写姿势

### 第二阶段：核心能力

- **[04. Stream 与 Buffer：高性能数据处理](./04_Streams_and_Buffer.md)** 💧
  - Buffer 内存模型与零拷贝原理
  - 四种 Stream 类型与背压（Backpressure）机制
  - `pipeline` 与异步迭代器的实战应用

- **[05. HTTP/3 与网络编程](./05_HTTP_and_Network.md)**
  - 从 TCP 到 HTTP/3（QUIC）的演进
  - Node.js 内置 HTTP/3 支持实战
  - WebSocket 与 Server-Sent Events

- **[06. 文件系统与操作系统交互](./06_File_System_and_OS.md)**
  - `fs` 模块最佳实践（同步 vs 异步 vs 流）
  - 文件监听（`FSWatcher`）和 `chokidar`
  - 子进程与 Shell 脚本编排

### 第三阶段：高并发与多核

- **[07. Worker Threads 与多进程架构](./07_Worker_Threads_and_Clustering.md)** ⚡
  - 单线程的瓶颈：CPU 密集型任务
  - Worker Threads 原理与 `SharedArrayBuffer`
  - Cluster 模块：充分利用多核 CPU

### 第四阶段：生产级框架实战

- **[08. Fastify + TypeScript 构建现代 REST API](./08_Fastify_Modern_API.md)** 🚀
  - 为什么 Fastify 比 Express 快 3 倍
  - 插件体系与 Schema 驱动开发
  - JWT 认证、速率限制与错误处理

- **[09. 数据库集成：Prisma ORM 实战](./09_Database_Integration.md)**
  - Prisma Schema、迁移与类型安全
  - 关联查询、事务与 N+1 问题
  - Redis 缓存集成

- **[10. 安全加固指南](./10_Security_and_Auth.md)** 🔒
  - OWASP Top 10 在 Node.js 中的防御
  - JWT、OAuth2 与 Passkey 实现
  - 依赖安全审计（`npm audit`）

### 第五阶段：性能、测试与部署

- **[11. 性能优化与可观测性](./11_Performance_and_Monitoring.md)** 📊
  - 火焰图分析与内存泄漏排查
  - OpenTelemetry 链路追踪
  - Node.js 内置性能钩子

- **[12. 测试策略与工程化](./12_Testing_and_CI.md)**
  - Vitest：单元测试与集成测试
  - Supertest API 测试
  - GitHub Actions CI/CD 流水线

- **[13. 容器化与云原生部署](./13_Deployment_and_Cloud.md)** ☁️
  - Docker 多阶段构建优化
  - Kubernetes 健康检查与滚动更新
  - Serverless：AWS Lambda vs Cloudflare Workers

### 第六阶段：工程化进阶

- **[14. 现代包管理：pnpm、Corepack 与 Monorepo](./14_Package_Management.md)** 📦
  - pnpm 全局内容寻址存储原理（为什么比 npm 快 2-3 倍）
  - Corepack：团队包管理器版本锁定
  - pnpm Workspace + Turborepo：Monorepo 构建加速

- **[15. Node.js 原生 TypeScript 支持](./15_TypeScript_Native.md)** 🆕
  - `--experimental-strip-types` vs `--transform-types` 适用边界
  - tsx / ts-node / tsc 完整对比
  - 2026 年推荐的 TypeScript 项目配置最佳实践

### 第七阶段：生产基础设施

- **[16. 错误处理体系与环境变量管理](./16_Error_Handling_and_Env.md)** 🛡️
  - `AppError` 自定义错误类 + Fastify 全局错误处理器
  - `unhandledRejection` + `uncaughtException` + 优雅关闭
  - Zod 验证环境变量，启动时即发现配置错误

- **[17. 结构化日志与调试技巧](./17_Logging_and_Debug.md)** 🔍
  - Pino 请求 ID 追踪、子 Logger、敏感字段脱敏
  - `--inspect` + Chrome DevTools 断点调试、内存快照、CPU Profile
  - VS Code `launch.json` 配置 TypeScript 服务调试

- **[18. 消息队列：BullMQ 任务调度](./18_BullMQ.md)** 📨
  - Queue / Worker / Job 核心概念与异步化模式
  - 延迟任务、Cron 定时任务、任务优先级
  - Bull Board 可视化监控 + Worker 独立进程部署

## 🌟 系列特色

- **深度**：不只讲 API 用法，深入 libuv、V8 和操作系统原理
- **图解**：大量 Mermaid 流程图，可视化事件循环、Stream 管道等复杂逻辑
- **前沿**：基于 Node.js 24 LTS，涵盖原生 HTTP/3、ESM 完整支持、SEA 单文件程序、原生 TypeScript 等 2026 年最新特性
- **实战**：每章均有可运行的完整代码案例
- **共 19 篇**：从零基础到消息队列的完整知识体系

---

> 系列持续更新，欢迎 Star 和提交 Issue。
