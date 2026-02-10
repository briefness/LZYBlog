# BaseCut - 纯前端在线视频剪辑器技术专栏

**BaseCut** 是一个完全基于 Web 技术的在线视频剪辑工具。本专栏包含 **10 篇文章**，深入剖析其背后的技术架构与核心实现。

利用现代浏览器的能力（**WebGL**、**WebCodecs**、**FileSystem API**），打破“Web 端无法处理高性能音视频”的刻板印象，实现功能对标桌面端的轻量级剪辑器。

> **项目仓库**：[https://github.com/briefness/BaseCut](https://github.com/briefness/BaseCut)

## 目录索引

### 🔹 核心架构与基础
- **[01 架构设计：Web 视频剪辑器开发实战](./01-architecture.md)**
  <br>纯前端方案的选择逻辑解析，以及 Vue 3 + TypeScript + Pinia 的架构设计与技术选型详解。

- **[02 时间轴状态管理：数据模型设计](./02-timeline-state.md)**
  <br>剪辑器的核心组件。解析 Track（轨道）、Clip（片段）的数据结构设计，以及基于 Pinia 的状态流转机制。

### 🔹 渲染与特效引擎
- **[03 WebGL 渲染：GPU 加速与滤镜实现](./03-webgl-rendering.md)**
  <br>剖析滤镜背后的数学原理。对比 Canvas 2D 与 WebGL 的性能差异，以及着色器（Shader）的实战应用。

- **[04 转场效果实现](./04-transitions.md)**
  <br>深入解析 Lerp 插值算法、缓动函数（Easing），以及基于 WebGL 实现淡入淡出、滑动、擦除等转场特效的方法。

- **[07 效果系统详解](./07-effect-system.md)**
  <br>构建可扩展的效果插件系统，支持滤镜、特效的动态加载与参数调节。

### 🔹 交互与功能模块
- **[06 LeaferJS 贴纸系统](./06-leaferjs-sticker.md)**
  <br>利用国产高性能 Canvas 引擎 LeaferJS，实现贴纸的拖拽、缩放、旋转与层级管理。

- **[08 关键帧动画](./08-keyframe-animation.md)**
  <br>超越简单的位移效果，设计并实现一套专业的关键帧动画系统，支持属性随时间线性或曲线变化。

- **[10 撤销重做（Undo/Redo）设计](./10-undo-redo.md)**
  <br>基于 Command 模式的历史记录管理，实现全状态回滚与重做功能。

### 🔹 性能与工程化
- **[05 WebCodecs 导出：极速视频生成](./05-webcodecs-export.md)**
  <br>替代传统的 FFmpeg.wasm 方案，使用浏览器原生 WebCodecs API 进行硬件加速编码，提升导出速度 10 倍以上。

- **[09 性能优化实战](./09-performance-optimization.md)**
  <br>复杂剪辑界面在 1080p 预览下的 60FPS 优化策略。涵盖渲染循环、内存管理到 Web Worker 的全方位优化。

---

*随着浏览器的进化，许多传统原生应用的功能已能在 Web 端实现。本系列旨在分享相关技术与实现经验。*
