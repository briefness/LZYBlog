# 纯前端导出视频，我用的是 WebCodecs

> BaseCut 技术博客第五篇。这篇是干货最多的一篇——怎么把编辑好的内容导出成 MP4 文件。

## 整体流程

先把导出流程画出来：

![导出流程图](./images/05-export-flow.png)

逐帧渲染 → 创建 VideoFrame → 编码 → 封装成 MP4 → 下载。这个流程跑一遍，就能把时间轴上的内容变成一个可分享的视频文件。

---

## 视频编码基础知识

在讲 WebCodecs 之前，先补一些视频编码的背景知识。

### 为什么视频需要压缩

一帧 1080p 画面有多大？

```
1920 × 1080 × 3 bytes (RGB) = 6.2 MB

一秒 30 帧：6.2 × 30 = 186 MB/s

一分钟视频：186 × 60 = 11.2 GB
```

没有压缩的话，一分钟视频就要 10GB，根本没法传播。

### 压缩的核心思路

视频压缩利用两种冗余：

**1. 空间冗余（Spatial Redundancy）**

一帧画面里，相邻像素往往颜色相近。比如蓝天部分，几千个像素都是差不多的蓝色。

不需要存每个像素的颜色，可以存"这一块区域都是这个颜色"。

**2. 时间冗余（Temporal Redundancy）**

相邻帧之间差异很小。比如一个人讲话，背景完全没动。

不需要存完整的每一帧，可以存"相对于上一帧，哪里变了"。

### I/P/B 帧

视频编码把帧分成三类：

| 类型 | 全称 | 作用 |
|------|------|------|
| I 帧 | Intra-coded | 完整画面，不依赖其他帧 |
| P 帧 | Predictive | 存储与前一帧的差异 |
| B 帧 | Bidirectional | 存储与前后两帧的差异 |

```
典型的帧序列：

I  P  B  B  P  B  B  P  B  B  I  P  B  B ...
│                            │
└──────── GOP ───────────────┘
    (一组画面)
```

I 帧最大，但可以独立解码（用于快进拖拽）。
B 帧最小，但解码时需要前后帧。

###H.264/AVC

H.264 是目前最通用的视频编码标准，几乎所有设备都支持。

它的压缩率非常高：原本 10GB 的视频可以压到几百 MB，肉眼几乎看不出画质损失。

---

## 技术选型：WebCodecs vs FFmpeg.wasm

### FFmpeg.wasm

FFmpeg 是视频处理领域的"神器"，FFmpeg.wasm 是它的 WebAssembly 移植版。

**优点：**
- 功能极其丰富，几乎支持所有格式
- 社区活跃，文档多
- 可以做复杂的滤镜、混流

**缺点：**
- 核心文件 **30MB+**，首次加载很慢
- WebAssembly 是软件模拟，**没有硬件加速**
- 需要在 WASM 内存中操作，容易内存不足
- 实测编码速度约 **10 fps**

### WebCodecs

WebCodecs 是 W3C 标准，Chrome 2020 年开始支持。

**优点：**
- 浏览器内置，**零加载成本**
- 可以调用系统的硬件编码器（**GPU 加速**）
- 直接操作 VideoFrame，内存效率高
- 实测编码速度 **100+ fps**

**缺点：**
- Safari **不支持**（截至 2024 年底）
- 只负责编码，不负责封装（需要额外的 muxer）
- API 相对底层，需要更多代码

### 我的选择

```
编码速度对比：

FFmpeg.wasm: 10 fps → 导出 1 分钟视频需要 3 分钟
WebCodecs:   100 fps → 导出 1 分钟视频需要 18 秒
```

性能差 10 倍。用户等不起 3 分钟，所以我选了 WebCodecs。

Safari 用户暂时无法导出，但考虑到主流用户在 Chrome 上，可以接受。

---

## WebCodecs 核心 API

### VideoFrame

`VideoFrame` 代表一帧原始画面。

```typescript
// 从 Canvas 创建 VideoFrame
const frame = new VideoFrame(canvas, {
  timestamp: time * 1_000_000  // 微秒
})

// 属性
frame.timestamp    // 时间戳
frame.codedWidth   // 宽度
frame.codedHeight  // 高度
frame.duration     // 持续时间

// 用完必须关闭！
frame.close()
```

### VideoEncoder

`VideoEncoder` 负责把 VideoFrame 压缩成 H.264 数据。

```typescript
const encoder = new VideoEncoder({
  output: (chunk, metadata) => {
    // chunk 是压缩后的数据
    // metadata 包含 decoderConfig 等信息
  },
  error: (e) => {
    console.error('Encode error:', e)
  }
})

// 配置编码参数
encoder.configure({
  codec: 'avc1.42001f',  // H.264 Baseline Profile
  width: 1920,
  height: 1080,
  bitrate: 8_000_000,    // 8 Mbps
  framerate: 30
})

// 编码一帧
encoder.encode(frame, { keyFrame: true })

// 等待所有帧编码完成
await encoder.flush()
```

### EncodedVideoChunk

`EncodedVideoChunk` 是编码器输出的压缩数据。

```typescript
interface EncodedVideoChunk {
  type: 'key' | 'delta'  // I 帧还是 P/B 帧
  timestamp: number       // 时间戳（微秒）
  duration: number        // 持续时间
  data: ArrayBuffer       // 压缩后的 H.264 数据
}
```

---

## 完整导出流程

### 核心代码

```typescript
async function exportVideo() {
  const chunks: EncodedVideoChunk[] = []
  
  // 1. 创建编码器
  const encoder = new VideoEncoder({
    output: (chunk) => {
      chunks.push(chunk)
    },
    error: (e) => console.error(e)
  })
  
  // 2. 配置编码参数
  encoder.configure({
    codec: 'avc1.42001f',
    width: 1920,
    height: 1080,
    bitrate: 8_000_000,
    framerate: 30
  })
  
  // 3. 逐帧循环
  const totalFrames = Math.ceil(duration * 30)
  
  for (let i = 0; i < totalFrames; i++) {
    const time = i / 30
    
    // a. 用 WebGL 渲染这一帧
    await webglRenderer.render(time)
    
    // b. 从 Canvas 创建 VideoFrame
    const frame = new VideoFrame(canvas, {
      timestamp: time * 1_000_000  // 微秒
    })
    
    // c. 编码（每 30 帧一个关键帧）
    encoder.encode(frame, { keyFrame: i % 30 === 0 })
    
    // d. 立即释放内存！！！
    frame.close()
    
    // e. 控制编码队列，防止内存爆炸
    if (encoder.encodeQueueSize > 5) {
      await new Promise(r => setTimeout(r, 1))
    }
    
    // f. 更新进度
    onProgress(i / totalFrames)
  }
  
  // 4. 等待编码完成
  await encoder.flush()
  
  // 5. 封装成 MP4
  const mp4Blob = await muxToMp4(chunks)
  
  // 6. 触发下载
  downloadBlob(mp4Blob, 'output.mp4')
}
```

### MP4 封装

WebCodecs 只管编码，输出的是裸的 H.264 数据。需要封装成 MP4 容器才能被播放器识别。

我用的是 `mp4-muxer` 这个库：

```typescript
import { Muxer, ArrayBufferTarget } from 'mp4-muxer'

async function muxToMp4(chunks: EncodedVideoChunk[]): Promise<Blob> {
  const muxer = new Muxer({
    target: new ArrayBufferTarget(),
    video: {
      codec: 'avc',
      width: 1920,
      height: 1080
    },
    fastStart: 'in-memory'  // 把 moov 放在文件开头，支持边下边播
  })
  
  for (const chunk of chunks) {
    muxer.addVideoChunk(chunk)
  }
  
  muxer.finalize()
  
  return new Blob([muxer.target.buffer], { type: 'video/mp4' })
}
```

---

## 内存管理：最重要的事

### 为什么 frame.close() 这么重要

VideoFrame 占用的内存很大：

```
1080p 一帧 = 1920 × 1080 × 4 bytes (RGBA) ≈ 8 MB

如果不及时 close()：
100 帧 = 800 MB
1000 帧 = 8 GB

浏览器崩溃
```

### 正确写法

```javascript
// 用完立即关闭
const frame = new VideoFrame(canvas, { timestamp })
encoder.encode(frame)
frame.close()  // ← 必须的！
```

### 错误写法

```javascript
// 忘了 close()，内存泄漏
const frame = new VideoFrame(canvas, { timestamp })
encoder.encode(frame)
// 缺少 frame.close()
```

---

## 性能优化

### 编码队列控制

编码器内部有一个队列。如果渲染太快，队列会积压，内存暴涨。

```typescript
// 等待队列消化
if (encoder.encodeQueueSize > 5) {
  await new Promise(r => setTimeout(r, 1))
}
```

### 渲染和编码并行

更高级的优化是用 OffscreenCanvas 在 Worker 里渲染，主线程只管编码。

这个项目没做这个优化，留给以后。

---

## 实测性能

在 M1 MacBook Pro 上：

| 时长 | 导出耗时 | 速度 |
|------|----------|------|
| 30s | ~5s | 6x 实时 |
| 1min | ~10s | 6x 实时 |
| 5min | ~50s | 6x 实时 |

基本是实时速度的 6 倍，还算可接受。

---

## 下一篇

讲 LeaferJS 贴纸系统——怎么实现可拖拽、可缩放的图片叠加。

---

**系列目录**

1. [x] 技术选型与项目结构
2. [x] 时间轴数据模型
3. [x] WebGL 渲染与滤镜
4. [x] 转场动画实现
5. [x] WebCodecs 视频导出（本文）
6. [ ] LeaferJS 贴纸系统
