# 关键帧动画系统：从插值到矩阵变换

> BaseCut 技术博客第八篇。这篇讲关键帧动画系统的设计与实现——如何让视频动起来。

## 需求分析

关键帧动画和静态属性调整不同：

| 对比项 | 静态属性 | 关键帧动画 |
|--------|---------|-----------|
| 时间依赖 | 否 | 是（随时间变化） |
| 参数变化 | 整个片段固定 | 在时间点之间平滑过渡 |
| 用户操作 | 设置一次 | 在多个时间点设置值 |
| 渲染方式 | 固定变换 | 实时计算插值 |

关键帧动画需要支持：
- 位置、缩放、旋转、透明度动画
- 多种缓动曲线（线性、缓入缓出、弹性等）
- 预览和导出渲染一致性
- 专业级的矩阵变换

---

## 架构设计

### 整体流程

```
用户操作 → AnimationStore → AnimationEngine → WebGLRenderer
     ↓           ↓                ↓                ↓
  设置关键帧   存储动画数据    计算插值/矩阵    应用变换渲染
```

### 核心模块

```typescript
// 1. 类型定义
interface Keyframe {
  id: string
  time: number           // 相对于片段起点的时间（秒）
  value: number          // 属性值
  easing: EasingType     // 缓动类型
}

interface AnimationTrack {
  property: AnimatableProperty  // 'position.x' | 'scale' | 'rotation' | 'opacity'
  keyframes: Keyframe[]
  enabled: boolean
}

// 2. 动画引擎
function getAnimatedTransform(tracks: AnimationTrack[], time: number): AnimatedTransform
function createTransformMatrix(transform: AnimatedTransform, canvasSize): Float32Array

// 3. 状态管理
const animationStore = defineStore('animation', () => {
  const clipAnimations = reactive<Map<string, ClipAnimation>>()
  // CRUD 操作
})
```

---

## 关键帧插值

### 核心算法

```typescript
function interpolateValue(keyframes: Keyframe[], time: number): number {
  // 排序确保时间顺序
  const sorted = [...keyframes].sort((a, b) => a.time - b.time)
  
  // 边界情况：时间在第一个关键帧之前
  if (time <= sorted[0].time) {
    return sorted[0].value
  }
  
  // 边界情况：时间在最后一个关键帧之后
  if (time >= sorted[sorted.length - 1].time) {
    return sorted[sorted.length - 1].value
  }
  
  // 找到当前时间所在的区间
  for (let i = 0; i < sorted.length - 1; i++) {
    const curr = sorted[i]
    const next = sorted[i + 1]
    
    if (time >= curr.time && time <= next.time) {
      // 计算进度 (0~1)
      const progress = (time - curr.time) / (next.time - curr.time)
      
      // 应用缓动函数
      const easedProgress = applyEasing(progress, next.easing)
      
      // 线性插值
      return curr.value + (next.value - curr.value) * easedProgress
    }
  }
  
  return sorted[0].value
}
```

### 行业标准行为

关键帧边界处理遵循 After Effects / 剪映 的标准：

```
时间线：  0s ──── 3s ──── 5s ──── 10s
          │       ◆       ◆       │
          │    X=100   X=0        │
          │       │       │       │
         100     100 ─→ 0        0
         (保持)  (过渡)   (保持)
```

- **第一个关键帧之前** → 保持第一个关键帧的值
- **两个关键帧之间** → 根据缓动曲线插值过渡
- **最后一个关键帧之后** → 保持最后一个关键帧的值

---

## 缓动函数实现

### 基础缓动

```typescript
const easingFunctions = {
  // 线性
  linear: (t: number) => t,
  
  // 二次方
  easeIn: (t: number) => t * t,
  easeOut: (t: number) => t * (2 - t),
  easeInOut: (t: number) => t < 0.5 
    ? 2 * t * t 
    : -1 + (4 - 2 * t) * t,
  
  // 三次方
  easeInCubic: (t: number) => t * t * t,
  easeOutCubic: (t: number) => (--t) * t * t + 1,
  
  // 回弹
  easeInBack: (t: number) => {
    const c = 1.70158
    return t * t * ((c + 1) * t - c)
  },
  easeOutBack: (t: number) => {
    const c = 1.70158
    return 1 + (--t) * t * ((c + 1) * t + c)
  },
  
  // 弹性
  easeOutElastic: (t: number) => {
    if (t === 0 || t === 1) return t
    return Math.pow(2, -10 * t) * Math.sin((t - 0.1) * 5 * Math.PI) + 1
  }
}
```

### 自定义贝塞尔曲线

```typescript
function cubicBezier(
  t: number,
  p1x: number, p1y: number,
  p2x: number, p2y: number
): number {
  // 牛顿迭代法求解
  let x = t
  for (let i = 0; i < 8; i++) {
    const currentX = bezierX(x, p1x, p2x) - t
    if (Math.abs(currentX) < 0.001) break
    const derivativeX = bezierDerivativeX(x, p1x, p2x)
    x -= currentX / derivativeX
  }
  return bezierY(x, p1y, p2y)
}
```

---

## 矩阵变换

### 为什么需要矩阵？

多个变换需要**按顺序组合**：

```
错误：先移动再缩放 ≠ 先缩放再移动

正确：使用变换矩阵，统一处理
```

### 4x4 变换矩阵

```typescript
function createTransformMatrix(
  transform: AnimatedTransform,
  canvasWidth: number,
  canvasHeight: number
): Float32Array {
  const matrix = new Float32Array(16)
  
  // 1. 单位矩阵
  mat4.identity(matrix)
  
  // 2. 平移（转换为 NDC 坐标）
  const tx = transform.position.x / canvasWidth * 2
  const ty = -transform.position.y / canvasHeight * 2
  mat4.translate(matrix, matrix, [tx, ty, 0])
  
  // 3. 旋转（弧度）
  const radians = transform.rotation * Math.PI / 180
  mat4.rotateZ(matrix, matrix, radians)
  
  // 4. 缩放
  mat4.scale(matrix, matrix, [transform.scale.x, transform.scale.y, 1])
  
  return matrix
}
```

### 锚点处理

变换需要围绕锚点进行：

```typescript
// 完整的变换顺序
// 1. 移动到锚点
mat4.translate(matrix, matrix, [-anchorX, -anchorY, 0])
// 2. 缩放
mat4.scale(matrix, matrix, [scaleX, scaleY, 1])
// 3. 旋转
mat4.rotateZ(matrix, matrix, rotation)
// 4. 移回原位
mat4.translate(matrix, matrix, [anchorX, anchorY, 0])
// 5. 最终位移
mat4.translate(matrix, matrix, [posX, posY, 0])
```

---

## WebGL 动画着色器

### 顶点着色器

```glsl
attribute vec2 a_position;
attribute vec2 a_texCoord;

uniform mat4 u_matrix;      // 变换矩阵
uniform mat4 u_projection;  // 投影矩阵

varying vec2 v_texCoord;

void main() {
  // 应用变换矩阵
  gl_Position = u_projection * u_matrix * vec4(a_position, 0.0, 1.0);
  v_texCoord = a_texCoord;
}
```

### 片段着色器

```glsl
precision mediump float;

uniform sampler2D u_texture;
uniform float u_opacity;  // 透明度动画

varying vec2 v_texCoord;

void main() {
  vec4 color = texture2D(u_texture, v_texCoord);
  
  // 应用透明度
  color.a *= u_opacity;
  
  // 预乘 Alpha
  color.rgb *= color.a;
  
  gl_FragColor = color;
}
```

---

## 渲染集成

### 预览播放

```typescript
// Player.vue - renderCurrentFrame
async function renderCurrentFrame() {
  const animation = animationStore.getClipAnimation(videoClip.id)
  
  // 计算片段内时间
  const timeInClip = currentTime - clip.startTime
  
  if (animation && hasActiveKeyframes(animation)) {
    // 计算动画变换
    const animTransform = getAnimatedTransform(animation.tracks, timeInClip)
    const matrix = createTransformMatrix(animTransform, canvasWidth, canvasHeight)
    
    // 使用动画渲染器
    renderer.renderFrameWithAnimation(videoElement, matrix, animTransform.opacity)
  } else {
    // 普通渲染
    renderer.renderFrame(videoElement)
  }
}
```

### 视频导出

```typescript
// WebCodecsExporter.ts
async function exportClip(clip: WebCodecsExportClip) {
  if (clip.animation && hasActiveKeyframes(clip.animation)) {
    const animTransform = getAnimatedTransform(
      clip.animation.tracks,
      timeInClip
    )
    const matrix = createTransformMatrix(animTransform, width, height)
    
    renderer.renderFrameWithAnimation(frame, matrix, animTransform.opacity)
  }
}
```

---

## 状态管理

### Pinia Store 设计

```typescript
export const useAnimationStore = defineStore('animation', () => {
  // 响应式存储
  const clipAnimations = reactive<Map<string, ClipAnimation>>(new Map())
  
  // 添加关键帧
  function addKeyframe(
    clipId: string,
    property: AnimatableProperty,
    data: Partial<Keyframe>
  ): Keyframe {
    ensureTrackExists(clipId, property)
    
    const keyframe: Keyframe = {
      id: crypto.randomUUID(),
      time: data.time ?? 0,
      value: data.value ?? getDefaultValue(property),
      easing: data.easing ?? 'easeInOut'
    }
    
    const track = getTrack(clipId, property)!
    track.keyframes.push(keyframe)
    
    // 保持排序
    track.keyframes.sort((a, b) => a.time - b.time)
    
    return keyframe
  }
  
  // 更新关键帧
  function updateKeyframe(
    clipId: string,
    property: AnimatableProperty,
    keyframeId: string,
    updates: Partial<Keyframe>
  ) {
    const track = getTrack(clipId, property)
    if (!track) return
    
    const keyframe = track.keyframes.find(kf => kf.id === keyframeId)
    if (keyframe) {
      Object.assign(keyframe, updates)
      
      // 时间变化需要重新排序
      if (updates.time !== undefined) {
        track.keyframes.sort((a, b) => a.time - b.time)
      }
    }
  }
  
  return { clipAnimations, addKeyframe, updateKeyframe, ... }
})
```

---

## UI 设计

### 属性面板结构

```
┌─────────────────────────────────────┐
│ 🎬 关键帧动画           ⏱️ 00:02.89 │
├─────────────────────────────────────┤
│ ▼ 📍 位置                           │
│   ◆ X  [  100.00  ] px  ◀ ▶        │
│   ◇ Y  [    0.00  ] px  ◀ ▶        │
├─────────────────────────────────────┤
│ ▶ 🔍 缩放                           │
│ ▶ 🔄 旋转                           │
│ ▶ 💧 透明度                         │
└─────────────────────────────────────┘

◆ = 当前时间有关键帧（黄色）
◇ = 当前时间无关键帧（灰色）
◀ ▶ = 跳转到上/下一个关键帧
```

### 输入确认逻辑

为了更好的用户体验，输入值只在**失去焦点**或**按 Enter** 时才提交：

```typescript
const localInputValue = ref(displayValue.value)
const isEditing = ref(false)

function onInputFocus() {
  isEditing.value = true
}

function commitValue() {
  isEditing.value = false
  
  const actualValue = parseFloat(localInputValue.value)
  if (isNaN(actualValue)) {
    localInputValue.value = displayValue.value
    return
  }
  
  // 有关键帧则更新，无则创建
  if (hasKeyframeAtCurrentTime) {
    updateKeyframe(clipId, property, currentKeyframe.id, { value: actualValue })
  } else {
    addKeyframe(clipId, property, { time: currentTime, value: actualValue })
  }
}
```

---

## 支持的属性

| 属性 | 类型 | 范围 | 默认值 |
|------|------|------|--------|
| position.x | 位置 X | -10000 ~ 10000 px | 0 |
| position.y | 位置 Y | -10000 ~ 10000 px | 0 |
| scale.x | 缩放 X | 0 ~ 10 | 1 |
| scale.y | 缩放 Y | 0 ~ 10 | 1 |
| scale | 统一缩放 | 0 ~ 10 | 1 |
| rotation | 旋转 | -360° ~ 360° | 0 |
| opacity | 透明度 | 0 ~ 1 | 1 |
| anchor.x | 锚点 X | 0 ~ 1 | 0.5 |
| anchor.y | 锚点 Y | 0 ~ 1 | 0.5 |

---

## 性能优化

### 1. 惰性计算

只有动画片段才计算变换：

```typescript
if (animation && animation.tracks.some(t => t.enabled && t.keyframes.length > 0)) {
  // 有动画，计算变换
} else {
  // 无动画，直接渲染
}
```

### 2. 矩阵缓存

同一帧内多次渲染可复用矩阵：

```typescript
const matrixCache = new Map<string, Float32Array>()

function getCachedMatrix(clipId: string, time: number): Float32Array {
  const key = `${clipId}-${time.toFixed(3)}`
  if (matrixCache.has(key)) {
    return matrixCache.get(key)!
  }
  // 计算并缓存
}
```

### 3. 关键帧预排序

添加关键帧时立即排序，而不是每次插值时排序：

```typescript
function addKeyframe(keyframe: Keyframe) {
  track.keyframes.push(keyframe)
  track.keyframes.sort((a, b) => a.time - b.time)  // 一次排序
}
```

---

## 下一篇

本系列已完结。完整目录：

1. [x] 技术选型与项目结构
2. [x] 时间轴数据模型
3. [x] WebGL 渲染与滤镜
4. [x] 转场动画实现
5. [x] WebCodecs 视频导出
6. [x] LeaferJS 贴纸系统
7. [x] 视频特效系统
8. [x] 关键帧动画系统（本文）
