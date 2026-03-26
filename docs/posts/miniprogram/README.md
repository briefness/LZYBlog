# 微信小程序核心原理与实战系列

本系列从零开始，用 17 篇文章 + 4 个 Manim 动画，把你从"小程序是什么"带到"能独立交付三个生产级小程序项目"。以微信原生开发为基础，Manim 动画讲解核心原理，配套 Mermaid 架构图和可运行代码。

> **环境：** 微信开发者工具 latest，小程序基础库 3.x，Manim latest，Python 3.12+

---

## 目录导航

### 准备篇

- **[00. 启程：环境准备与小程序初体验](./00_Preparation.md)**
  - 微信开发者工具安装与项目结构
  - `app.js / app.json / app.wxss` 全局配置
  - rpx 响应式单位速通
  - 开发者工具调试面板使用指南

### 第一阶段：认知与地基

从零建立对小程序的正确心智模型。这个阶段不用任何框架，纯原生代码，理解底层运作。

- **[01. 微信小程序全景：从打开到渲染](./01_Architecture.md)**
  - 小程序 vs H5 vs 原生 App 的本质区别
  - 双线程架构详解：渲染层 WebView + 逻辑层 JS Engine
  - `setData` 的跨线程通信本质
  - App / Page / Component 三套生命周期
  - 🎬 Manim 动画：[01_startup_animation.py](./animations/01_startup_animation.py)

- **[02. WXML 速成：微信的 HTML 长什么样](./02_WXML.md)**
  - 数据绑定 `{{}}` 语法 vs HTML 的差异
  - `wx:if` vs `wx:for` vs `wx:for`
  - `bindtap` vs `catchtap` 事件冒泡机制
  - `import` vs `include` 模板复用
  - 常用内置组件：view / text / image / scroll-view

- **[03. WXSS 速成：微信的 CSS 改造版](./03_WXSS.md)**
  - rpx 响应式单位：设计稿 750px 换算零成本
  - flexbox 布局：常用模式速查
  - 样式隔离：`styleIsolation` 与 `externalClasses`
  - 暗黑模式：`@media preprocessor-theme-dark` + CSS 变量

### 第二阶段：JavaScript 逻辑层

小程序的 JS 环境不是浏览器，理解这个差异才能理解为什么 H5 代码在小程序里跑不了。

- **[04. JavaScript 环境：你不知道的 JavaScript](./04_JS_Environment.md)**
  - 小程序 JS 环境 vs 浏览器环境：`window` / `document` / `fetch` 全都不存在
  - `App()` / `Page()` / `Component()` 三种构造器
  - 模块化：CommonJS vs ES Module 的混用陷阱
  - ES6+ 语法支持情况
  - 作用域与 this：箭头函数的正确使用

- **[05. 异步编程：wx.request 与网络请求封装](./05_Async_Network.md)**
  - `wx.request` 基础与限制（域名白名单、TLS、并发数）
  - Promise 封装 + 请求拦截器
  - 统一 Token 注入 + 错误处理
  - `wx.uploadFile` / `wx.downloadFile` 文件操作
  - `wx.connectSocket` WebSocket 实时通信
  - 🎬 Manim 动画：[05_async_flow_animation.py](./animations/05_async_flow_animation.py)

- **[06. 数据流与状态管理：Page Data 的正确姿势](./06_State_Management.md)**
  - `setData` 深层机制：快照传递 vs 响应式追踪
  - 路径写法 `'key.subKey': value` 性能优化
  - 跨页面通信：URL 参数 / EventChannel / Storage 中转
  - 类 Vuex 的全局 Store 轻量实现
  - 组件间通信：`properties` + `triggerEvent`

### 第三阶段：组件系统

组件化是小程序工程化的核心。掌握组件设计，才能构建可维护的大型应用。

- **[07. 自定义组件：从设计到封装](./07_Custom_Components.md)**
  - `Component()` 构造器 vs `Page()` 的关键差异
  - 组件生命周期：`created / attached / ready / detached`
  - `properties` + `observer` 数据响应
  - 插槽（默认 / 命名 / 多 slot）
  - `externalClasses` 外部样式类
  - `behaviors` 代码复用（类似 Mixin）

- **[08. 内置组件进阶：复杂 UI 的构建块](./08_Built_in_Components.md)**
  - `scroll-view` 虚拟列表：解决长列表性能问题
  - Canvas 2D：离屏渲染 + 绘制实战
  - video 弹幕实现与坑点
  - map 组件：markers / polyline / circles
  - swiper 轮播图 + 自定义指示点
  - 原生 vs uni-app vs Taro 组件系统对比

### 第四阶段：API 与实战工具

小程序最大的差异化能力，来自微信生态。

- **[09. 微信开放能力：登录、支付、订阅](./09_Wechat_APIs.md)**
  - 微信登录全链路：`wx.login()` → code → 后端换 openid → 返回 token
  - 微信支付：`统一下单` → 前端调起支付 → 后端回调验证
  - 订阅消息 vs 模板消息（2024 最新）
  - 分享能力：`onShareAppMessage` + `button open-type="share"`
  - 地理位置：`wx.getLocation` + GCJ02 坐标

- **[10. 本地存储、云函数与 CDN](./10_Storage_CDN.md)**
  - `wx.getStorageSync` vs `wx.getStorage`：同步阻塞 vs 异步非阻塞
  - Storage 安全边界：明文存储 + 加密方案
  - 带过期时间的 Storage 封装
  - 云开发：云函数 + 云数据库 + 云存储快速入门
  - CDN + URL 参数裁剪 + WebP 格式：图片三重优化

### 第五阶段：三大实战项目

前四个阶段的所有知识在这里汇聚。三个项目难度递进，每个都是生产级别的完整实现。

- **[11. 实战（一）：TodoList 任务管理](./11_Project_Todo.md)**
  - Store 单例 + 订阅模式实现全局状态管理
  - Storage 封装：软删除 + 5 秒撤销机制
  - 自定义组件 `todo-item`：左滑删除（touch 事件）
  - CSS 变量 + 系统暗黑模式适配
  - `wx.vibrateShort` 触觉反馈

- **[12. 实战（二）：新闻阅读器](./12_Project_News.md)**
  - `IntersectionObserver` 实现图片懒加载
  - 骨架屏组件：消除白屏焦虑
  - 新闻列表：分页加载 + 上拉触底
  - 详情页：模板复用 + 分享能力
  - 收藏功能：Storage 持久化 + 跨页面状态同步

- **[13. 实战（三）：电商购物车](./13_Project_Ecommerce.md)**
  - CartStore：集中管理购物车全局状态
  - SKU 弹窗：规格互斥 + 库存匹配 + 价格联动
  - 价格计算：全程以"分"为单位，精确到分的浮点运算陷阱
  - 微信支付：`统一下单` → `wx.requestPayment()` → 轮询回调
  - 🎬 Manim 动画：[13_ecommerce_flow_animation.py](./animations/13_ecommerce_flow_animation.py)

### 第六阶段：生产化与架构

从"能跑"到"能上线"的最后一公里。

- **[14. 性能优化与调试：从小程序到精品](./14_Performance.md)**
  - 首屏优化：分包加载 + 骨架屏
  - `setData` 艺术：只传必要数据、路径写法、避免 scroll 中更新
  - 图片懒加载：`IntersectionObserver` + CDN + WebP
  - 包体积控制：tree-shaking + iconfont + CDN
  - 微信 Trace 工具 + Performance API 性能监控
  - 🎬 Manim 动画：[14_perf_optimization_animation.py](./animations/14_perf_optimization_animation.py)

- **[15. 工程化与发布：CI/CD + 灰度发布](./15_DevOps.md)**
  - 多环境配置：`process.env` + `project.config.json`
  - GitHub Actions CI/CD 完整配置（lint / test / build / upload）
  - 微信开发者工具 CLI 自动化上传
  - 灰度发布：白名单灰度方案 + 版本管理
  - 审核避坑：诱导分享 / 虚拟支付 / 授权说明三大高频被拒原因

### 补充篇：跨平台扩展

- **[16. 扩展一：uni-app 跨平台实战](./16_Uniapp.md)**
  - uni-app vs 原生小程序：选型决策树
  - Vue 3 语法速通：`setup` / `ref` / `computed` / `v-for`
  - 条件编译：`#ifdef` / `#ifndef` 处理平台差异
  - 统一 API：`uni.xxx` 自动适配各平台
  - 性能对比：编译产物 + 包体积分析

- **[17. 扩展二：Taro 3.x React 化改造](./17_Taro.md)**
  - Taro 3.x 架构：运行时适配层 vs 纯编译时
  - React Hooks：`useState` / `useEffect` / `useCallback`
  - 自定义 Hooks：Storage / 请求 / 状态管理的 Hook 封装
  - Zustand 状态管理：比 Redux 更轻量的方案
  - Taro vs 原生：JSX vs WXML、Hooks vs setData

---

## 技术栈版本锁定（2026 年 3 月）

| 工具 / 框架 | 版本 | 用途 |
|------------|------|------|
| 微信开发者工具 | latest | 开发与调试 |
| 小程序基础库 | 3.x | 运行时 |
| Manim | latest | 动画生成 |
| Python | 3.12+ | Manim 运行环境 |
| Node.js | 20+ | CLI / 构建工具 |
| ESLint | 9.x | 代码检查 |
| Prettier | 3.x | 代码格式化 |

---

## 系列特色

- **渐进式学习路径**：先理解原生原理，再掌握工程化，最后三个项目练手
- **双线程架构为核心**：所有 API 和组件的选择，都从双线程的性能模型出发理解
- **Manim 动画 + Mermaid 图解**：启动流程、异步时序、购物流程、优化对比全部可视化
- **三大实战项目递进**：TodoList（状态管理）→ 新闻阅读器（列表优化）→ 电商购物车（复杂状态 + 支付）
- **生产导向**：每篇文章都包含 Trade-offs 讨论和常见坑点，不只教怎么做，也教怎么避坑
- **TypeScript 全面支持**：04 篇专讲 TS 类型定义（Page/Component 泛型、工具函数泛型），三大实战项目代码均有 TS 版本示例
- **跨平台扩展**：uni-app（Vue）和 Taro（React）作为选读补充，扩展技术视野

---

## 配套动画运行方式

```bash
# 安装 Manim
pip install manim

# 进入动画目录
cd animations

# 运行启动流程动画（01）
manim -pql 01_startup_animation.py StartupFlow

# 运行异步网络动画（05）
manim -pql 05_async_flow_animation.py AsyncFlow

# 运行电商流程动画（13）
manim -pql 13_ecommerce_flow_animation.py EcommerceFlow

# 运行性能优化动画（14）
manim -pql 14_perf_optimization_animation.py PerfOptimization
```

---

## 文件结构

```
miniprogram/
├── README.md                          # 系列总导航
├── 00_Preparation.md                 # 环境准备
├── 01_Architecture.md               # 架构全景
├── 02_WXML.md                       # WXML 速成
├── 03_WXSS.md                       # WXSS 速成
├── 04_JS_Environment.md             # JS 环境
├── 05_Async_Network.md              # 异步网络
├── 06_State_Management.md             # 状态管理
├── 07_Custom_Components.md            # 自定义组件
├── 08_Built_in_Components.md         # 内置组件
├── 09_Wechat_APIs.md                 # 微信 API
├── 10_Storage_CDN.md               # 存储与 CDN
├── 11_Project_Todo.md               # 实战一
├── 12_Project_News.md                # 实战二
├── 13_Project_Ecommerce.md          # 实战三
├── 14_Performance.md                # 性能优化
├── 15_DevOps.md                    # 工程化发布
├── 16_Uniapp.md                    # uni-app 扩展
├── 17_Taro.md                      # Taro 扩展
└── animations/
    ├── 01_startup_animation.py
    ├── 05_async_flow_animation.py
    ├── 13_ecommerce_flow_animation.py
    └── 14_perf_optimization_animation.py
```

---

## 推荐阅读路径

| 背景 | 推荐路径 |
|------|---------|
| 零基础小白 | 00 → 01 → 02 → 03 → 04 → 05 → 06 → 07 → 08 → 09 → 10 → 11 → 12 → 13 → 14 → 15 |
| 有 Vue 经验 | 01 → 04 对比 Vue → 06 对比 Vuex → 07 对比 Vue 组件 → 16 uni-app |
| 有 React 经验 | 01 → 04 对比 React → 06 对比 Redux → 07 对比 React 组件 → 17 Taro |
| 想快速做项目 | 00 → 07 组件 → 11/12/13 三大项目 → 14 性能优化 → 15 发布上线 |

---

> 系列共 17 篇，已全部完成。
