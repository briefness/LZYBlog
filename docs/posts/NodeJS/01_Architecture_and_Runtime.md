# Node.js 深度实战（一）—— 架构与运行时原理

用 Node.js 一年，能说清楚它的架构吗？这篇从 V8、libuv 到内存模型，把 Node.js 的底层搞透。

## 全系列目录

1. **架构与运行时原理**
2. **事件循环深度解析**
3. **模块系统：ESM、CJS 与未来**
4. **Stream 与 Buffer：高性能数据处理**
5. **HTTP/3 与网络编程**
6. **文件系统与操作系统交互**
7. **Worker Threads 与多进程架构**
8. **Fastify + TypeScript 构建现代 REST API**
9. **数据库集成：Prisma ORM 实战**
10. **安全加固指南**
11. **性能优化与可观测性**
12. **测试策略与工程化**
13. **容器化与云原生部署**

---

## 1. Node.js 整体架构

Node.js 不是一个单体程序，而是多个核心组件的精密组合：

```mermaid
graph TD
    A["JavaScript 代码"] --> B["Node.js Core (JavaScript)"]
    B --> C["Node.js Bindings (C++)"]
    C --> D["V8 引擎"]
    C --> E["libuv"]
    C --> F["llhttp / zlib / OpenSSL 等"]
    D --> G["JIT 编译 → 机器码"]
    E --> H["事件循环"]
    E --> I["线程池（4个线程）"]
    I --> J["文件系统 / DNS / CPU密集任务"]
    H --> K["网络 I/O（OS 内核直接处理）"]
```

### 核心组件解析

| 组件 | 语言 | 职责 |
|------|------|------|
| **V8** | C++ | 执行 JavaScript、JIT 编译、垃圾回收 |
| **libuv** | C | 事件循环、线程池、跨平台 I/O 抽象 |
| **llhttp** | C | HTTP 协议解析（前身 http_parser） |
| **OpenSSL** | C | TLS/HTTPS 加密 |
| **Node.js Bindings** | C++ | 连接 JS 世界和 C/C++ 底层 |

## 2. V8 引擎：让 JS 跑得飞快

V8 不是解释器，它是一个 **JIT（Just-In-Time）编译器**。

### 代码执行流程

```mermaid
flowchart LR
    A["源代码\nconst x = 1 + 2"] --> B["Parser\n词法&语法分析"]
    B --> C["AST\n抽象语法树"]
    C --> D["Ignition\n解释器（字节码）"]
    D --> E{热点代码\n检测}
    E --"首次执行"--> F["字节码\n直接执行"]
    E --"多次执行(热点)"--> G["TurboFan\nJIT 编译器"]
    G --> H["机器码\n直接运行"]
    H --"类型假设失败\n去优化"--> D
```

**关键点：** V8 会对频繁执行的函数进行优化编译，转成机器码运行，速度接近 C++。一旦发现类型假设错误（比如传入了不同类型的参数），会回退到字节码解释执行（Deoptimization）。

### 如何写出对 V8 友好的代码

```javascript
// ❌ 不友好：函数参数类型不稳定，导致 V8 无法优化
function add(a, b) {
  return a + b;
}
add(1, 2);       // V8 优化为整数加法
add('a', 'b');   // V8 发现类型错误，去优化！

// ✅ 友好：保持参数类型一致
function addNumbers(a, b) {
  return a + b;
}
function addStrings(a, b) {
  return a + b;
}
```

```javascript
// ❌ 不友好：动态增删对象属性，破坏隐藏类（Hidden Class）
const obj = {};
obj.x = 1;
obj.y = 2;   // 每次添加属性都会创建新的隐藏类

// ✅ 友好：在构造时一次性声明所有属性
const obj = { x: 1, y: 2 };  // V8 创建稳定的隐藏类
```

## 3. libuv：Node.js 的异步引擎

libuv 解决了一个核心问题：**如何用单线程处理大量 I/O 而不阻塞？**

### 操作系统 I/O 的真相

不同操作系统提供不同的异步 I/O 机制：

| 操作系统 | 网络 I/O 机制 | 文件 I/O 机制 |
|---------|-------------|-------------|
| Linux | `epoll` | `io_uring`（新）/ 线程池（旧）|
| macOS | `kqueue` | 线程池 |
| Windows | `IOCP` | `IOCP` |

libuv 把这些差异统一封装，对上层提供一致的 API。

### 被误解的"单线程"

Node.js 主线程是单线程，但 libuv 内部维护了一个**线程池**（默认 4 个线程）。文件系统操作、DNS 解析等任务会被分发到线程池完成，主线程通过回调取回结果。

```mermaid
sequenceDiagram
    participant MT as 主线程（事件循环）
    participant TP as libuv 线程池（4线程）
    participant FS as 文件系统

    MT->>TP: fs.readFile('big.txt', cb)（分发任务）
    Note over MT: 继续处理其他请求
    TP->>FS: 调用系统调用 read()
    FS-->>TP: 返回文件内容
    TP-->>MT: 将回调推入队列
    MT->>MT: 执行回调 cb(null, data)
```

**调整线程池大小：**

```bash
# 文件系统密集型应用可适当增大
UV_THREADPOOL_SIZE=16 node app.js
```

## 4. Node.js 内存模型

### V8 堆内存结构

```mermaid
graph TD
    A["V8 堆内存 (Heap)"] --> B["新生代 (New Space)\n~2MB 小对象，生命周期短"]
    A --> C["老生代 (Old Space)\n大对象/长期存活对象"]
    A --> D["代码空间 (Code Space)\nJIT 编译后的机器码"]
    A --> E["大对象空间 (Large Object)\n单个 > 1MB"]

    B --> F["From 区"]
    B --> G["To 区"]
    F --> H["Scavenge GC（超快，微秒级）"]
```

### 垃圾回收机制

V8 使用**分代垃圾回收**：

- **新生代（Scavenge）**：大部分短期变量在这里出生和死去。采用 Cheney 算法，将活对象复制到 To 区，然后清空 From 区，速度极快（仅微秒级）。
- **老生代（Mark-Sweep / Mark-Compact）**：长期存活的对象晋升到老生代。采用标记-清除或标记-整理，耗时更长，但频率更低。

```javascript
// 模拟内存泄漏（常见错误）
const leaked = [];

setInterval(() => {
  leaked.push(new Array(1000).fill('leak'));  // 每秒泄漏约 8KB
  console.log('内存使用：', process.memoryUsage().heapUsed / 1024 / 1024, 'MB');
}, 1000);
```

### 查看内存使用

```javascript
const mem = process.memoryUsage();
console.log({
  rss: `${(mem.rss / 1024 / 1024).toFixed(2)} MB`,        // 进程总内存
  heapTotal: `${(mem.heapTotal / 1024 / 1024).toFixed(2)} MB`,  // 分配的堆大小
  heapUsed: `${(mem.heapUsed / 1024 / 1024).toFixed(2)} MB`,    // 实际使用的堆
  external: `${(mem.external / 1024 / 1024).toFixed(2)} MB`,    // C++ 对象占用（如 Buffer）
});
```

## 5. Node.js 24 LTS 新特性（2026年）

### 原生支持 `require(esm)`

过去 CommonJS 无法直接 `require` ES Module，Node.js 22 解除了这个限制，Node.js 24 正式稳定：

```javascript
// legacy.cjs（CommonJS 文件）
const { helper } = require('./utils.mjs');  // ✅ Node.js 22+ 直接支持！
```

### 原生 `--watch` 模式稳定化

无需 nodemon，Node.js 22 的内置文件监听正式稳定：

```bash
node --watch app.js
```

### `WebSocket` 客户端内置

无需安装 `ws` 包，Node.js 22 内置 WebSocket 客户端（WHATWG 标准规范）：

```javascript
const ws = new WebSocket('wss://echo.websocket.org');
ws.onopen = () => ws.send('Hello!');
ws.onmessage = (e) => console.log(e.data);
```

### `--strip-types`：TypeScript 原生支持（节点 24 正式稳定）

Node.js 22.6 引入实验性，Node.js 24 正式稳定，直接运行 TypeScript 文件无需编译：

```bash
# Node.js 24 中已无 experimental 前缀
node --strip-types app.ts
```

### `AbortSignal.timeout()` 内置支持稳定

```javascript
// 5秒超时自动取消请求
const response = await fetch('https://api.example.com/data', {
  signal: AbortSignal.timeout(5000)
});
```

## 6. 完整架构图

```mermaid
graph TB
    subgraph "用户代码层"
        A["app.js / TypeScript"]
    end

    subgraph "Node.js 运行时（JavaScript）"
        B["http / fs / net / stream / ...内置模块"]
        C["npm 包（Fastify、Prisma、...）"]
    end

    subgraph "Node.js Bindings（C++）"
        D["node_http_parser / node_fs / node_net ..."]
    end

    subgraph "底层库（C/C++）"
        E["V8\nJS引擎"]
        F["libuv\n事件循环+线程池"]
        G["OpenSSL\nTLS"]
        H["llhttp\nHTTP解析"]
        I["zlib\n压缩"]
    end

    subgraph "操作系统"
        J["epoll / kqueue / IOCP\n网络I/O"]
        K["文件系统\n系统调用"]
    end

    A --> B & C
    B --> D
    C --> D
    D --> E & F & G & H & I
    F --> J & K
```

## 总结

- Node.js = V8（JS 执行） + libuv（异步 I/O） + 大量 C++ 绑定
- V8 的 JIT 编译让 JS 接近 C++ 速度，但需要保持类型一致性
- libuv 线程池处理文件/DNS，网络 I/O 直接走 OS 内核
- Node.js 24 LTS（24 是 2025~2028年的 Active LTS）带来了原生 TypeScript 类型剥离（`--strip-types`）、`require(esm)` 互通等重大改进

---

下一章将深入 **事件循环**，彻底搞清楚 `nextTick`、`Promise` 和 `setTimeout` 的执行顺序。
