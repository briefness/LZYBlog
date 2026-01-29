# LeaferJS 贴纸系统的实现

> BaseCut 技术博客第六篇，也是最后一篇。这篇讲贴纸系统——怎么实现可拖拽、可缩放、可旋转的图片叠加。

---

## 需求分析

用户想在视频上叠加各种元素：

```
贴纸类型：
├── 表情包、GIF
├── 图片水印
├── 品牌 Logo
└── 静态/动态贴图

交互需求：
├── 选中高亮
├── 拖拽移动
├── 八向缩放
├── 旋转
└── 控制出现/消失时间
```

这些需求听起来简单，但自己实现会非常复杂：
- 鼠标点击在哪个元素上？（命中检测）
- 怎么画选中框和控制手柄？
- 怎么响应拖拽、缩放、旋转？

所以需要找一个 Canvas 2D 渲染库。

---

## 技术选型：为什么选 LeaferJS

### 备选方案对比

| 库 | 优点 | 缺点 |
|---|------|------|
| **原生 Canvas** | 轻量 | 要自己实现所有交互逻辑 |
| **Fabric.js** | 生态成熟，功能全 | 包体 200KB+，代码老旧 |
| **Konva.js** | 性能还行 | API 设计一般 |
| **LeaferJS** | 极致性能、TS 原生、编辑器功能开箱即用 | 社区相对小 |

### LeaferJS 简介

[LeaferJS](https://leaferjs.com) 是一个国产开源的 Canvas 2D 渲染引擎，有几个特点非常吸引我：

**1. 性能炸裂**

官方 benchmark 数据：

| 场景 | LeaferJS | Fabric.js |
|------|----------|-----------|
| 创建 1 万个矩形 | 15ms | 800ms |
| 创建 100 万个矩形 | 1.5s | 崩溃 |
| 内存占用（100万矩形）| 350MB | - |

性能差距是 **50-100 倍**。

**2. 包体积极小**

```
LeaferJS (gzip): 42KB
Fabric.js (gzip): 200KB+
```

只有 Fabric.js 的 1/5。

**3. TypeScript 原生**

整个库用 TypeScript 编写，API 类型定义完善，开发体验很好。

**4. 编辑器功能开箱即用**

`@leafer-in/editor` 插件提供了：
- 选中框
- 八向缩放手柄
- 旋转手柄
- 多选
- 对齐吸附

不用自己实现，直接用。

---

## LeaferJS 基础使用

### 安装

```bash
npm install leafer-ui @leafer-in/editor
```

### 创建画布

```typescript
import { App, Rect, Image } from 'leafer-ui'
import '@leafer-in/editor'  // 引入编辑器插件

// 创建应用
const app = new App({
  view: 'canvas-container',  // 容器 ID
  type: 'design',            // 设计模式，支持编辑
  editor: {}                 // 启用编辑器
})

// 添加一个矩形
const rect = new Rect({
  x: 100,
  y: 100,
  width: 200,
  height: 150,
  fill: '#32cd79',
  editable: true  // 可编辑
})

app.tree.add(rect)
```

加上 `editable: true`，矩形就可以拖拽、缩放、旋转了。

### 添加图片

```typescript
const sticker = new Image({
  url: '/stickers/emoji.png',
  x: 200,
  y: 200,
  width: 100,
  height: 100,
  editable: true
})

app.tree.add(sticker)
```

### 监听事件

```typescript
// 拖拽结束
sticker.on('drag.end', (e) => {
  console.log('新位置:', e.target.x, e.target.y)
})

// 缩放/旋转结束
sticker.on('transform.end', (e) => {
  const { x, y, scaleX, scaleY, rotation } = e.target
  console.log('变换:', { x, y, scaleX, scaleY, rotation })
})
```

---

## 贴纸数据模型

### 类型定义

```typescript
interface StickerClip {
  id: string
  trackId: string
  resourceId: string  // 图片资源 ID
  
  // 时间范围
  startTime: number
  duration: number
  
  // 变换参数（百分比，0-1）
  transform: {
    x: number        // 0.5 表示居中
    y: number
    scaleX: number   // 1 表示原始大小
    scaleY: number
    rotation: number // 角度，0-360
    opacity: number  // 透明度，0-1
  }
}
```

**为什么用百分比存位置？**

预览窗口和导出分辨率可能不一样。用百分比可以自动适配：

```typescript
// 百分比 → 像素
function toPixel(percent: number, canvasSize: number) {
  return percent * canvasSize
}

// 像素 → 百分比
function toPercent(pixel: number, canvasSize: number) {
  return pixel / canvasSize
}
```

---

## 核心问题：双向数据同步

### 问题描述

系统里有两份"数据"：

```
1. Pinia Store 里的贴纸数据 → 真正的数据源
2. LeaferJS 画布上的图形对象 → 可视化表现
```

它们必须保持同步，但有两个方向：

**Store → LeaferJS**（正常渲染）

```
当前时间变化时：
1. 查询 Store 里有哪些贴纸应该显示
2. 在 LeaferJS 画布上创建/更新对应图形
```

**LeaferJS → Store**（用户交互）

```
用户拖拽贴纸时：
1. LeaferJS 更新图形位置
2. 把新位置写回 Store
```

### 踩的坑：交互时的冲突

一开始我没注意这个问题，结果出现了"贴纸跳来跳去"的 bug：

```
用户正在拖拽贴纸（x: 100 → 101 → 102 → 103...）
    ↓
播放器在渲染每一帧
    ↓
渲染时从 Store 读取 x = 100（还没更新）
    ↓
LeaferJS 图形被强制重置回 100
    ↓
用户感觉贴纸"跳"了一下
```

### 解决方案：交互锁

```typescript
let isInteracting = false

// 开始拖拽时上锁
function onDragStart() {
  isInteracting = true
}

// 结束拖拽时解锁，并同步到 Store
function onDragEnd(e) {
  isInteracting = false
  
  const { x, y, scaleX, scaleY, rotation } = e.target
  store.updateClip(clipId, {
    transform: {
      x: toPercent(x, canvasWidth),
      y: toPercent(y, canvasHeight),
      scaleX,
      scaleY,
      rotation
    }
  })
}

// 渲染时检查锁状态
function syncFromStore() {
  if (isInteracting) return  // 有锁，跳过同步
  
  // 正常同步...
}
```

---

## 时间轴联动

贴纸有出场和退场时间，需要和时间轴联动。

```typescript
function onTimeUpdate(currentTime: number) {
  // 1. 获取当前时间应该显示的贴纸
  const activeClips = store.getActiveStickers(currentTime)
  
  // 2. 遍历所有贴纸
  for (const clip of activeClips) {
    let leaferObj = leaferMap.get(clip.id)
    
    // 如果不存在，创建
    if (!leaferObj) {
      leaferObj = createLeaferImage(clip)
      app.tree.add(leaferObj)
      leaferMap.set(clip.id, leaferObj)
    }
    
    // 如果没在交互，从 Store 同步位置
    if (!isInteracting) {
      leaferObj.x = toPixel(clip.transform.x, canvasWidth)
      leaferObj.y = toPixel(clip.transform.y, canvasHeight)
      leaferObj.scaleX = clip.transform.scaleX
      leaferObj.scaleY = clip.transform.scaleY
      leaferObj.rotation = clip.transform.rotation
    }
  }
  
  // 3. 移除不该显示的贴纸
  for (const [id, obj] of leaferMap) {
    if (!activeClips.find(c => c.id === id)) {
      obj.remove()
      leaferMap.delete(id)
    }
  }
}
```

---

## 导出时的贴纸渲染

预览时用 LeaferJS 渲染贴纸（支持交互），导出时用 WebGL 渲染贴纸（性能更好）。

### 为什么导出时换 WebGL？

```
LeaferJS（Canvas 2D）：
├── 优点：交互方便
├── 缺点：每帧都要 drawImage，叠加多个贴纸时性能下降

WebGL：
├── 优点：GPU 加速，性能稳定
├── 缺点：不支持交互（但导出时不需要交互）
```

### 导出渲染逻辑

```typescript
function renderFrame(time: number) {
  // 1. 渲染视频底图
  webgl.drawVideo(videoFrame)
  
  // 2. 获取当前时间的贴纸
  const stickers = store.getActiveStickers(time)
  
  // 3. 按层级顺序渲染
  for (const sticker of stickers) {
    // 把贴纸图片作为纹理
    const texture = getTexture(sticker.resourceId)
    
    // 应用变换矩阵
    webgl.drawTexture(texture, {
      x: sticker.transform.x * canvasWidth,
      y: sticker.transform.y * canvasHeight,
      scaleX: sticker.transform.scaleX,
      scaleY: sticker.transform.scaleY,
      rotation: sticker.transform.rotation,
      opacity: sticker.transform.opacity
    })
  }
}
```

---

## 系列总结

六篇写完了！回顾一下整个项目用到的核心技术：

| 模块 | 技术 | 为什么选它 |
|------|------|------------|
| 前端框架 | Vue 3 | 响应式系统适合复杂状态联动 |
| 类型系统 | TypeScript | 3 万行代码必须有类型约束 |
| 状态管理 | Pinia | 简洁，比 Vuex 好用 |
| 视频渲染 | WebGL | 60fps 必须 GPU 加速 |
| 视频编码 | WebCodecs | 硬件加速，比 FFmpeg.wasm 快 10 倍 |
| MP4 封装 | mp4-muxer | 轻量，专注做一件事 |
| 贴纸渲染 | LeaferJS | 性能炸裂，编辑器开箱即用 |

### 这套方案的局限

- Safari 不支持 WebCodecs，暂时无法导出
- 4K 导出比较慢（WebGL 渲染是瓶颈）
- 音频处理还比较简陋（只支持简单混音）

但作为一个 MVP，已经能满足基本需求了。

如果你也想做类似的项目，希望这个系列能帮到你。

---

**系列目录**

1. [x] 技术选型与项目结构
2. [x] 时间轴数据模型
3. [x] WebGL 渲染与滤镜
4. [x] 转场动画实现
5. [x] WebCodecs 视频导出
6. [x] LeaferJS 贴纸系统（本文）
