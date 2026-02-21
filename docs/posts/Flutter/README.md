# Flutter 核心原理深度解析系列

本系列文章旨在辅助开发者从底层视角理解 Flutter 的运行机制，从而写出更高效、更优雅的代码。

内容涵盖了从架构设计、渲染管线、布局原理到状态管理、异步并发等核心主题，坚持“深入浅出、拒绝说教”的写作原则。

## 目录

### [Start] 00. [启程：环境准备与 Dart 速成](./00_Preparation.md)
   - FVM 环境搭建最佳实践
   - Dart 语言极速作弊表 (Cheatsheet)
   - Hello World 结构深度解析

### 1. [拨开云雾：Flutter 架构与渲染三棵树](./01_Architecture.md)

   - Flutter vs Native/Web 的架构区别
   - Widget, Element, RenderObject 三棵树的关系与职责

### 2. [驯服布局：约束与尺寸的博弈](./02_Layout.md)
   - 布局口诀：Constraints go down, Sizes go up
   - Tight vs Loose 约束解析
   - 常见布局问题排查

### 3. [像素的旅程：渲染管线与帧生成](./03_Rendering.md)
   - V-Sync 信号与掉帧
   - Animation -> Build -> Layout -> Paint -> Composite 流水线
   - Raster/GPU 线程的工作

### 4. [数据的流动：状态管理本质](./04_State.md)
   - 声明式 UI (UI = f(State))
   - Ephemeral vs App State
   - InheritedWidget 的 O(1) 查找机制

### 5. [驯服单线程：异步机制与事件循环](./05_Async.md)
   - Dart 单线程模型真相
   - Event Loop: Microtask vs Event Queue
   - Isolate 并发机制

### 6. [迈向专业：工程化与最佳实践入门](./06_Practice.md)
   - Clean Architecture 分层架构
   - const 的性能玄学
   - 错误处理与日志规范

---

### 7. [滑动的艺术：Slivers 与 Viewport](./07_Slivers.md)
   - RenderBox vs RenderSliver 协议区别
   - CustomScrollView 与 Viewport 懒加载机制

### 8. [手势竞技场：Gesture Arena](./08_Gestures.md)
   - HitTest 命中测试流程
   - 竞技场胜利规则与手势冲突解决

### 9. [打破次元壁：Native Interop 与 FFI](./09_Native.md)
   - Platform Channels 通信架构及代价
   - Dart FFI 直接调用 C/C++ 内存

### 10. [守护质量：测试金字塔与 CI/CD](./10_Testing.md)
   - Unit / Widget / Integration 三层测试
   - Golden Test 像素级验证

---

### 11. [智能应用：Flutter x AI (Gemini)](./11_AI.md)
   - Gemini API 接入与多模态输入
   - Streaming UI 流式响应设计

### 12. [游戏开发：Flame 与 Casual Toolkit](./12_Games.md)
   - Flame 引擎 Game Loop 机制
   - 休闲游戏 Casual Toolkit 实践

### 13. [变现与集成：Ads, IAP & Ecosystem](./13_Ecosystem.md)
   - AdMob 广告与应用内支付 (IAP) 流程
   - Firebase 全栈集成

---

### 14. [极致打磨：走向生产级应用](./14_Quality.md)
   - Accessibility (无障碍): Semantics Widget
   - Internationalization (国际化): ARB 与 intl
   - DevTools: 内存泄漏检测与网络抓包
   - Deployment: 代码混淆 (Obfuscation) 与包体积分析

---

### [Bonus] 15. [灵动交互：动画与转场](./15_Animation.md)
   - Implicit Animations (隐式动画)
   - Explicit Animations (显式动画)
   - Hero 过渡与 Lottie 集成




