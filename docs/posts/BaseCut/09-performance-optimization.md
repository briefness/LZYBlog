# 纯前端视频编辑器的性能优化实战

> 这是 BaseCut 技术博客系列的第九篇。聊聊在做前端视频编辑器时，我们怎么把"慢到无法使用"优化成"丝滑如原生"。

## 性能是生死线

视频编辑器对性能要求极高。用户拖动时间轴、调整滤镜、预览转场——任何卡顿都会让人抓狂。

一个残酷的事实：

```
1080p 视频 @ 30fps = 每帧 6200 万像素操作
每秒 = 18.6 亿次像素计算
```

如果性能不行，用户拖个进度条就像在玩 PPT。所以性能优化不是"锦上添花"，而是"生死线"。

这篇文章会汇总项目里**实际落地**的优化手段，包括我们最新实施的一系列算法和内存优化。

---

## 一、GPU 加速：WebGL 渲染

### 问题：CPU 扛不住像素级计算

视频滤镜（亮度、对比度、色相）需要对每个像素做数学运算。用 Canvas 2D 的 `getImageData` + 循环，实测：

| 分辨率 | Canvas 2D 帧率 | 体验 |
|--------|--------------|------|
| 480p | 25 fps | 勉强能用 |
| 720p | 12 fps | 明显卡顿 |
| 1080p | 5 fps | 幻灯片 |

### 解决方案：WebGL 着色器 + 静态缓冲区复用

把计算扔给 GPU。GPU 有几千个并行核心，天生适合"对每个像素做同样计算"的场景。

```glsl
// 片段着色器 - 在 GPU 上并行执行
void main() {
  vec4 color = texture2D(u_texture, v_texCoord);
  vec3 rgb = color.rgb;
  
  // 亮度调整
  rgb += u_brightness;
  
  // 对比度调整
  rgb = (rgb - 0.5) * u_contrast + 0.5;
  
  // 色相偏移
  vec3 hsl = rgb2hsl(rgb);
  hsl.x = mod(hsl.x + u_hue, 1.0);
  hsl.y *= u_saturation;
  rgb = hsl2rgb(hsl);
  
  gl_FragColor = vec4(clamp(rgb, 0.0, 1.0), color.a);
}
```

**内存优化：预分配静态缓冲区**

每帧渲染都创建 `Float32Array` 会产生大量垃圾回收压力。我们预分配静态数组，运行时只更新值：

```typescript
class WebGLRenderer {
  // 预分配静态缓冲区，避免每帧 GC
  private readonly staticPositions = new Float32Array(12)
  private readonly staticTexCoords = new Float32Array(12)
  private readonly fullscreenQuad = new Float32Array([
    -1, -1, 1, -1, -1, 1, -1, 1, 1, -1, 1, 1
  ])
  
  renderFrame(source, cropMode) {
    // 直接修改预分配数组的值，不创建新对象
    this.staticPositions[0] = -scaleX
    this.staticPositions[1] = -scaleY
    // ...
    
    gl.bufferData(gl.ARRAY_BUFFER, this.staticPositions, gl.DYNAMIC_DRAW)
  }
}
```

**优化效果：**

| 优化项 | 效果 |
|--------|------|
| WebGL 渲染 | 帧率提升 10-20 倍 |
| 静态缓冲区 | 减少 GC，帧率再提 5-10% |

---

## 二、视频预加载池：O(1) LRU 淘汰

### 问题：频繁创建 Video 元素很慢

用户在时间轴切换片段时，如果每次都 `new Video()` + 加载 + 等待 `canplay`，会有明显延迟。

### 解决方案：Video 元素对象池 + 双向链表 LRU

传统 LRU 实现在淘汰时需要遍历所有元素找最久未使用的（O(n)）。我们使用 **Map + 双向链表** 实现真正的 O(1) 淘汰：

```typescript
interface LRUNode {
  key: string
  video: PooledVideo
  prev: LRUNode | null
  next: LRUNode | null
}

class VideoPool {
  private pool: Map<string, LRUNode> = new Map()  // O(1) 查找
  private head: LRUNode  // 最近使用（头部）
  private tail: LRUNode  // 最久未使用（尾部）
  
  // O(1) 移动到头部
  private moveToHead(node: LRUNode): void {
    this.removeNode(node)
    this.addToHead(node)
  }
  
  // O(1) 淘汰尾部
  private evictLRU(): void {
    const node = this.tail.prev  // 直接取尾部，不用遍历
    this.removeNode(node)
    this.pool.delete(node.key)
  }
  
  async preload(materialId: string, url: string) {
    const node = this.pool.get(materialId)
    if (node) {
      this.moveToHead(node)  // 访问后移到头部
      return node.video.element
    }
    
    if (this.pool.size >= this.maxSize) {
      this.evictLRU()  // O(1) 淘汰
    }
    
    return this.loadVideo(materialId, url)
  }
}
```

**时间复杂度对比：**

| 操作 | 传统 Map 实现 | 双向链表实现 |
|------|-------------|-------------|
| 查找 | O(1) | O(1) |
| 更新使用时间 | O(1) | O(1) |
| 淘汰最久未使用 | **O(n)** | **O(1)** |

---

## 三、关键帧动画：二分搜索优化

### 问题：关键帧线性查找太慢

动画插值需要找到当前时间所在的关键帧区间。原来用线性遍历，大量关键帧时性能堪忧。

### 解决方案：二分搜索 O(log n)

```typescript
// 二分搜索找到最后一个 time <= 目标时间的关键帧
function binarySearchKeyframe(keyframes: Keyframe[], time: number): number {
  let lo = 0, hi = keyframes.length - 1
  
  if (keyframes[lo].time > time) return -1
  
  while (lo < hi) {
    const mid = (lo + hi + 1) >> 1  // 位运算避免浮点误差
    if (keyframes[mid].time <= time) {
      lo = mid
    } else {
      hi = mid - 1
    }
  }
  
  return lo
}

export function interpolate(keyframes: Keyframe[], time: number): number {
  // 边界处理...
  
  // 使用二分搜索找到区间
  const prevIndex = binarySearchKeyframe(keyframes, time)
  const prevKey = keyframes[prevIndex]
  const nextKey = keyframes[prevIndex + 1]
  
  // 插值计算...
  return prevKey.value + (nextKey.value - prevKey.value) * easedProgress
}
```

**性能对比：**

| 关键帧数量 | 线性搜索 | 二分搜索 |
|-----------|---------|---------|
| 10 个 | 0.01ms | 0.01ms |
| 100 个 | 0.1ms | 0.01ms |
| 1000 个 | 1ms | **0.01ms** |

---

## 四、波形提取：TypedArray 向量化

### 问题：音频峰值提取 CPU 密集

波形提取需要遍历几百万个音频采样点，找每个区间的峰值。

### 解决方案：预分配 Float32Array + 避免函数调用

```typescript
private async doExtractWaveform(audioUrl, materialId, samplesPerSecond, channel) {
  const channelData = audioBuffer.getChannelData(channel)
  const totalSamples = Math.ceil(duration * samplesPerSecond)
  
  // 性能优化：预分配 Float32Array
  const peaks = new Float32Array(totalSamples)
  const dataLength = channelData.length
  
  for (let i = 0; i < totalSamples; i++) {
    const start = i * samplesPerPeak
    const end = start + samplesPerPeak < dataLength 
      ? start + samplesPerPeak 
      : dataLength
    
    let maxPeak = 0
    for (let j = start; j < end; j++) {
      const v = channelData[j]
      // 避免 Math.abs 函数调用开销
      const abs = v < 0 ? -v : v
      if (abs > maxPeak) maxPeak = abs
    }
    peaks[i] = maxPeak
  }
  
  return Array.from(peaks)
}
```

**优化点：**

1. **预分配 Float32Array**：避免动态 `push` 的内存重分配
2. **手动绝对值**：`v < 0 ? -v : v` 比 `Math.abs(v)` 快
3. **预计算边界**：避免循环内 `Math.min` 调用

---

## 五、帧提取：动态并发控制

### 问题：固定并发数无法利用多核

帧提取是 CPU 密集操作，固定并发数 2 在多核设备上浪费资源。

### 解决方案：根据硬件动态调整

```typescript
async extractFrames(video, materialId, inPoint, outPoint, count) {
  const times = // 计算时间点...
  
  // 根据 CPU 核心数动态调整并发
  const concurrency = Math.max(2, Math.min(4, navigator.hardwareConcurrency || 2))
  
  const results: string[] = []
  for (let i = 0; i < times.length; i += concurrency) {
    const batch = times.slice(i, i + concurrency)
    const batchResults = await Promise.all(
      batch.map(time => this.extractFrame(video, materialId, time))
    )
    results.push(...batchResults)
  }
  
  return results
}
```

| 设备 | CPU 核心 | 并发数 |
|------|---------|-------|
| 低端设备 | 2 | 2 |
| 普通笔记本 | 4-8 | 4 |
| 高端设备 | 8+ | 4（上限保护） |

---

## 六、状态管理：片段索引缓存

### 问题：频繁查找片段 O(n*m)

`getClipById` 需要遍历所有轨道的所有片段，时间复杂度 O(n*m)。

### 解决方案：计算属性缓存索引

```typescript
export const useTimelineStore = defineStore('timeline', () => {
  const tracks = ref<Track[]>([])
  
  // 性能优化：片段 ID 索引缓存
  // 使用计算属性自动缓存，仅在 tracks 变化时重建
  const clipIdMap = computed(() => {
    const map = new Map<string, Clip>()
    for (const track of tracks.value) {
      for (const clip of track.clips) {
        map.set(clip.id, clip)
      }
    }
    return map
  })
  
  // O(1) 查找
  function getClipById(clipId: string): Clip | null {
    return clipIdMap.value.get(clipId) ?? null
  }
  
  // selectedClip 也使用索引
  const selectedClip = computed(() => 
    clipIdMap.value.get(selectedClipId.value) ?? null
  )
})
```

---

## 七、Canvas 绘制：Path2D 批量渲染

### 问题：波形条形多次绘制调用

波形图需要绘制几百个条形，每个都单独 `beginPath() + fill()` 效率低。

### 解决方案：Path2D 批量构建一次填充

```typescript
function drawWaveform() {
  const ctx = canvas.getContext('2d')
  ctx.fillStyle = 'rgba(255, 255, 255, 0.65)'
  
  // 使用 Path2D 批量构建所有路径
  const path = new Path2D()
  
  for (let i = 0; i < numBars; i++) {
    const barHeight = calculateBarHeight(i)
    const x = i * barSpacing
    const y = height - barHeight
    
    // 添加到路径，不立即绘制
    path.roundRect(x, y, barWidth, barHeight, 1)
  }
  
  // 一次性填充所有条形
  ctx.fill(path)
}
```

**对比：**

| 方式 | 绘制调用次数 |
|------|-------------|
| 循环内 fill() | n 次 |
| Path2D 批量 | **1 次** |

---

## 八、其他优化

### Ping-Pong 帧缓冲

多特效叠加时，使用两个 FBO 交替读写，避免中间结果复制：

```
特效1: 读 A → 写 B
特效2: 读 B → 写 A
特效3: 读 A → 写 屏幕
```

### 着色器懒编译

按需编译特效着色器，首次使用时编译，后续复用缓存。

### Worker 线程池

重计算任务（帧批量提取、音频解码）放到 Worker，根据 `hardwareConcurrency` 动态创建 Worker 数量。

### 懒加载

使用 `IntersectionObserver` 延迟加载可视区域外的波形和缩略图。

---

## 小结

| 优化手段 | 解决的问题 | 核心技术 |
|---------|-----------|---------|
| WebGL 渲染 | 滤镜计算慢 | GPU 并行着色器 |
| 静态缓冲区 | 每帧 GC 压力 | 预分配 Float32Array |
| O(1) LRU 池 | 视频加载延迟 | Map + 双向链表 |
| 二分搜索 | 关键帧查找慢 | O(log n) 算法 |
| TypedArray | 波形提取 CPU 密集 | 向量化 + 避免函数调用 |
| 动态并发 | 多核利用不足 | hardwareConcurrency |
| 索引缓存 | 片段查找 O(n²) | 计算属性 Map |
| Path2D 批量 | Canvas 绘制调用多 | 路径合并一次填充 |

性能优化没有银弹，关键是**找到瓶颈**，**选对数据结构和算法**。

---

**系列目录**

1. [x] [技术选型与项目结构](./01-architecture.md)
2. [x] [时间轴数据模型](./02-timeline-state.md)
3. [x] [WebGL 渲染与滤镜](./03-webgl-rendering.md)
4. [x] [转场动画实现](./04-transitions.md)
5. [x] [WebCodecs 视频导出](./05-webcodecs-export.md)
6. [x] [LeaferJS 贴纸系统](./06-leaferjs-sticker.md)
7. [x] [特效系统](./07-effect-system.md)
8. [x] [关键帧动画](./08-keyframe-animation.md)
9. [x] 性能优化实战（本文）
