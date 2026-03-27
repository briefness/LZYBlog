# 微信小程序核心原理与实战系列

本系列从零开始，用 17 篇文章，把你从"小程序是什么"带到"能独立交付三个生产级小程序项目"。以微信原生开发为基础，配合 Mermaid 架构图、CSS 动画组件和可运行代码讲解核心原理。

> **环境：** 微信开发者工具 latest，小程序基础库 3.x

## 目录

### 准备篇

- **[00. 启程：环境准备与小程序初体验](./00_Preparation.md)**
  - 微信开发者工具安装与项目结构、`app.js / app.json / app.wxss` 全局配置、rpx 响应式单位速通

### 第一阶段：认知与地基

从零建立对小程序的正确心智模型。纯原生代码，理解底层运作。

- **[01. 微信小程序全景：从打开到渲染](./01_Architecture.md)**
  - 双线程架构、WebView + JS Engine、`setData` 跨线程通信、三套生命周期
  - 🎨 可视化演示：启动流程动态演示

- **[02. WXML 速成：微信的 HTML 长什么样](./02_WXML.md)**
  - 数据绑定 `{{}}`、条件/列表渲染、`bindtap` vs `catchtap`、`import` vs `include`

- **[03. WXSS 速成：微信的 CSS 改造版](./03_WXSS.md)**
  - rpx 换算流程图、flexbox 布局、样式隔离层级图、暗黑模式适配

### 第二阶段：JavaScript 逻辑层

小程序的 JS 环境不是浏览器，理解这个差异才能理解为什么 H5 代码在小程序里跑不了。

- **[04. JavaScript 环境：你不知道的 JavaScript](./04_JS_Environment.md)**
  - JS 环境 vs 浏览器、`App()` / `Page()` / `Component()` 构造器、CommonJS vs ES Module
  - 小程序 JS vs 浏览器 JS 能力对比图
  - **TypeScript 全面支持**：Page/Component 泛型、工具函数泛型

- **[05. 异步编程：wx.request 与网络请求封装](./05_Async_Network.md)**
  - Promise 封装、请求/响应拦截器、Token 注入、`wx.connectSocket` WebSocket
  - 🎨 可视化演示：异步网络请求完整时序

- **[06. 数据流与状态管理：Page Data 的正确姿势](./06_State_Management.md)**
  - `setData` 深层机制、路径写法、跨页面通信、类 Vuex 全局 Store

### 第三阶段：组件系统

- **[07. 自定义组件：从设计到封装](./07_Custom_Components.md)**
  - `Component()` vs `Page()`、生命周期、`properties` + `observer`、插槽、`behaviors`

- **[08. 内置组件进阶：复杂 UI 的构建块](./08_Built_in_Components.md)**
  - `scroll-view` 虚拟列表、Canvas 2D离屏渲染、video/map/swiper
  - **组件选择决策树**：列表 → 轮播 → 地图 → 视频 → Canvas 按场景选型

### 第四阶段：API 与实战工具

- **[09. 微信开放能力：登录、支付、订阅](./09_Wechat_APIs.md)**
  - 登录全链路、支付前后端完整流程（Node.js Mock）、订阅消息、分享能力

- **[10. 本地存储、云函数与 CDN](./10_Storage_CDN.md)**
  - Storage sync vs async、Storage 安全边界、云开发快速入门
  - **数据流全景图**：Storage vs 云数据库 vs CDN 三层架构选型

### 第五阶段：三大实战项目

- **[11. 实战（一）：TodoList 任务管理](./11_Project_Todo.md)**
  - Store 单例 + 订阅模式、Storage 软删除 + 5 秒撤销、左滑删除、暗黑模式

- **[12. 实战（二）：新闻阅读器](./12_Project_News.md)**
  - `IntersectionObserver` 图片懒加载、骨架屏、分页加载、收藏功能

- **[13. 实战（三）：电商购物车](./13_Project_Ecommerce.md)**
  - CartStore + SKU 弹窗 + 价格精确计算（分单位）
  - **微信支付完整后端链路**：Node.js 统一下单 + 签名 + 回调验证 Mock
  - 🎨 可视化演示：电商购物流程状态机

### 第六阶段：生产化与架构

- **[14. 性能优化与调试：从小程序到精品](./14_Performance.md)**
  - 分包加载、骨架屏、`setData` 艺术、IntersectionObserver 懒加载、CDN + WebP
  - 🎨 可视化演示：渲染链路优化对比

- **[15. 工程化与发布：CI/CD + 灰度发布](./15_DevOps.md)**
  - 多环境配置、GitHub Actions CI/CD、微信 CLI、灰度发布白名单方案、审核避坑

### 补充篇：跨平台扩展

- **[16. 扩展一：uni-app 跨平台实战](./16_Uniapp.md)**
  - Vue 3 语法速通、条件编译 `#ifdef`、uni-app 编译流程图、迷你实战案例

- **[17. 扩展二：Taro 3.x React 化改造](./17_Taro.md)**
  - React Hooks、Zustand 状态管理、Taro 3.x 运行时架构图、迷你实战 + TS 示例

---

## 系列特色

- **渐进式学习路径**：先理解原生原理，再掌握工程化，最后三个项目练手
- **双线程架构为核心**：所有 API 和组件的选择，都从双线程的性能模型出发理解
- **Mermaid 图解 + CSS 动画组件**：启动流程、异步时序、购物流程、优化对比全部可视化
- **三大实战项目递进**：TodoList（状态管理）→ 新闻阅读器（列表优化）→ 电商购物车（复杂状态 + 支付）
- **TypeScript 全面支持**：04 篇专讲 TS 类型定义，三大实战项目代码均有 TS 版本示例
- **微信支付完整后端链路**：Node.js Mock 覆盖统一下单、签名、回调验证三个核心环节
- **生产导向**：每篇文章都包含 Trade-offs 讨论和常见坑点

---

## 推荐阅读路径

| 背景 | 推荐路径 |
|------|---------|
| 零基础小白 | 00 → 01 → 02 → 03 → 04 → 05 → 06 → 07 → 08 → 09 → 10 → 11 → 12 → 13 → 14 → 15 |
| 有 Vue 经验 | 01 → 04 对比 Vue → 06 对比 Vuex → 07 对比 Vue 组件 → 16 uni-app |
| 有 React 经验 | 01 → 04 对比 React → 06 对比 Redux → 07 对比 React 组件 → 17 Taro |
| 想快速做项目 | 00 → 07 组件 → 11/12/13 三大项目 → 14 性能优化 → 15 发布上线 |

> 系列共 17 篇，已全部完成。
