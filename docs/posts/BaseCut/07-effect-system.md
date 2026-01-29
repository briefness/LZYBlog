# 视频特效系统：从 Shader 到 Ping-Pong 渲染

> BaseCut 技术博客第七篇。这篇讲特效系统的设计与实现——如何用 WebGL 实现专业级的视频特效。

## 需求分析

视频特效和滤镜不同：

| 对比项 | 滤镜 | 特效 |
|--------|------|------|
| 依赖时间 | 否 | 是（随时间变化） |
| 参数 | 简单（亮度/对比度） | 复杂（频率/方向/强度） |
| 采样方式 | 单点采样 | 多点/偏移采样 |
| 叠加方式 | 通常只应用一个 | 可多个叠加 |

特效需要支持：
- 时间敏感的动画效果
- 多特效链式叠加
- 入场/出场动画
- 实时预览和导出一致性

---

## 架构设计

### 整体流程

```
视频帧 → FBO 预渲染 → 特效链 → 屏幕输出
               ↓
         Ping-Pong 渲染
        ├── Effect 1 → FBO A
        ├── Effect 2 → FBO B  
        ├── Effect 3 → FBO A
        └── 最终输出 → Screen
```

### 核心类

```typescript
// 特效管理器
class EffectManager {
  // 程序缓存（按特效类型）
  private programCache: Map<VideoEffectType, CompiledEffectProgram>
  
  // 帧缓冲（用于特效链式渲染）
  private framebuffers: WebGLFramebuffer[]
  private frameTextures: WebGLTexture[]
  
  // 核心方法
  applyEffects(inputTexture, effects, timeInClip, globalTime): boolean
}
```

---

## 为什么需要 Ping-Pong 渲染？

### 问题：多特效叠加

假设用户给视频加了 3 个特效：闪白 → 故障 → 老电影。

**错误做法：直接叠加**

```javascript
// ❌ 每个特效都读写同一个纹理
applyFlash(texture)   // 读 texture，写 texture
applyGlitch(texture)  // 读 texture，写 texture （读到的是上一步的结果吗？）
applyFilmGrain(texture)
```

WebGL 不允许同时读写同一个纹理（会产生未定义行为）。

**正确做法：Ping-Pong**

```javascript
// ✅ 交替使用两个 FBO
const fboA = createFramebuffer()
const fboB = createFramebuffer()

// 特效 1：读原始纹理 → 写 FBO A
applyFlash(inputTexture, fboA)

// 特效 2：读 FBO A → 写 FBO B
applyGlitch(fboA.texture, fboB)

// 特效 3：读 FBO B → 写屏幕
applyFilmGrain(fboB.texture, screen)
```

每次都从上一步的输出读取，写入下一个缓冲区，像打乒乓球一样来回切换。

---

## 特效着色器实现

### 通用 Uniform

所有特效共享这些参数：

```glsl
uniform sampler2D u_texture;    // 输入纹理
uniform float u_time;           // 全局时间
uniform vec2 u_resolution;      // 画布尺寸
uniform float u_intensity;      // 特效强度 (0~1)
```

### 闪白特效 (Flash)

最简单的特效，用白色和原色混合：

```glsl
void main() {
  vec4 color = texture2D(u_texture, v_texCoord);
  
  // 保留原始 Alpha，仅处理不透明区域
  float alpha = color.a;
  
  // 与白色混合
  color.rgb = mix(color.rgb, u_color, u_intensity);
  color.rgb *= alpha; // 透明区域保持透明
  
  gl_FragColor = color;
}
```

### 故障特效 (Glitch)

这个比较复杂，模拟数字信号干扰：

```glsl
void main() {
  vec2 uv = v_texCoord;
  float alpha = texture2D(u_texture, uv).a;
  
  // 1. 水平抖动
  float noise = fract(sin(dot(uv.y * 100.0, u_time * 10.0)) * 43758.5453);
  float shake = (noise - 0.5) * u_intensity * 0.02;
  uv.x += shake;
  
  // 2. RGB 分离（色差）
  float rgbSplit = u_rgbSplit * u_intensity * 0.01;
  float r = texture2D(u_texture, uv + vec2(rgbSplit, 0.0)).r;
  float g = texture2D(u_texture, uv).g;
  float b = texture2D(u_texture, uv - vec2(rgbSplit, 0.0)).b;
  
  // 3. 扫描线
  float scanline = sin(uv.y * u_resolution.y * 2.0) * 0.5 + 0.5;
  scanline = 1.0 - u_scanlineIntensity * (1.0 - scanline) * u_intensity;
  
  vec3 color = vec3(r, g, b) * scanline;
  
  // 关键：透明区域强制为黑色
  color *= alpha;
  
  gl_FragColor = vec4(color, alpha);
}
```

### 老电影特效 (Film Grain)

模拟老胶片的颗粒感：

```glsl
// 噪声函数
float noise(vec2 p) {
  return fract(sin(dot(p, vec2(12.9898, 78.233))) * 43758.5453);
}

void main() {
  vec4 color = texture2D(u_texture, v_texCoord);
  float alpha = color.a;
  
  // 1. 颗粒噪声
  float grain = noise(v_texCoord * u_resolution + u_time * 1000.0);
  grain = (grain - 0.5) * u_grainIntensity * u_intensity;
  
  // 2. 垂直划痕
  float scratchX = floor(v_texCoord.x * 100.0) / 100.0;
  float scratch = noise(vec2(scratchX, u_time * 10.0));
  scratch = scratch > 0.97 ? u_scratchIntensity : 0.0;
  
  // 3. 亮度闪烁
  float flicker = 1.0 - u_flickerIntensity * (noise(vec2(u_time * 8.0, 0.0)) - 0.5);
  
  // 4. 复古色调（棕褐色）
  float gray = dot(color.rgb, vec3(0.299, 0.587, 0.114));
  vec3 sepia = vec3(gray) * vec3(1.2, 1.0, 0.8);
  color.rgb = mix(color.rgb, sepia, u_sepiaAmount * u_intensity);
  
  // 合成
  color.rgb = (color.rgb + grain + scratch) * flicker;
  color.rgb *= alpha;
  
  gl_FragColor = vec4(color.rgb, alpha);
}
```

---

## 入场/出场动画

特效不应该突然出现或消失，需要渐入渐出：

```typescript
function getEffectIntensity(effect: VideoEffect, timeInClip: number): number {
  const { startTime, duration, fadeIn = 0, fadeOut = 0 } = effect
  const endTime = startTime + duration
  
  // 计算在特效内的相对时间
  const relativeTime = timeInClip - startTime
  
  // 入场动画
  if (relativeTime < fadeIn) {
    return relativeTime / fadeIn
  }
  
  // 出场动画
  if (relativeTime > duration - fadeOut) {
    return (duration - relativeTime) / fadeOut
  }
  
  // 正常强度
  return 1.0
}
```

这个强度值会乘以 `u_intensity`，实现平滑过渡。

---

## 关键修复：透明区域处理

### 问题

竖屏视频在横屏画布上会有黑边：

```
┌─────────────────────────┐
│  黑边  │  视频  │  黑边  │
│        │        │        │
│        │        │        │
└─────────────────────────┘
```

如果特效不处理透明区域，就会出现"特效溢出"——黑边也被特效污染了。

### 原因

故障特效使用偏移采样：

```glsl
float r = texture2D(u_texture, uv + vec2(rgbSplit, 0.0)).r;
```

当采样点在透明区域（黑边）时，可能采样到视频边缘的像素。

### 解决方案

**硬性 Alpha 遮罩**：

```glsl
// 在着色器最后
color *= alpha;  // RGB 乘以 Alpha

gl_FragColor = vec4(color, alpha);
```

这确保透明区域的 RGB 始终为 0（黑色），即使采样到了其他内容。

---

## 导出一致性

### 问题

预览正常，但导出黑屏。

### 根因分析

特效有独立的时间范围。一个视频片段可能：
- 0-2 秒：无特效
- 2-4 秒：有特效
- 4-6 秒：无特效

代码流程：

```typescript
// 检测到片段有特效附加
if (effects.length > 0) {
  // 渲染到 FBO
  renderFrame(source, fbo)
  
  // 应用特效
  const applied = applyEffects(fboTexture, effects, timeInClip)
  
  // BUG：如果当前帧没有激活的特效，applyEffects 返回 false
  // FBO 内容没有被复制到屏幕！
  if (!applied) {
    // 这里需要手动将 FBO 内容渲染到屏幕
    renderTextureToScreen(fboTexture)  // ← 关键修复
  }
}
```

### 解决方案

检查 `applyEffects` 返回值，如果返回 `false`（无激活特效），手动将 FBO 纹理渲染到屏幕。

---

## 状态沙箱

WebGL 是状态机，特效切换时必须正确管理状态：

```typescript
// 特效渲染完成后，恢复干净状态
gl.bindFramebuffer(gl.FRAMEBUFFER, null)
gl.activeTexture(gl.TEXTURE0)
gl.bindTexture(gl.TEXTURE_2D, null)
gl.disable(gl.BLEND)
gl.useProgram(null)
```

否则上一个特效的状态会污染下一帧的渲染。

---

## 性能优化

### 1. 程序缓存

着色器编译很慢（可能需要几十毫秒），所以按类型缓存：

```typescript
private programCache: Map<VideoEffectType, CompiledEffectProgram> = new Map()

getOrCreateProgram(type: VideoEffectType): CompiledEffectProgram {
  if (this.programCache.has(type)) {
    return this.programCache.get(type)!
  }
  
  // 只在首次使用时编译
  const program = this.compileProgram(type)
  this.programCache.set(type, program)
  return program
}
```

### 2. 静态几何缓冲

特效使用的全屏 Quad 是固定的，所以用静态缓冲：

```typescript
private initBuffers(): void {
  // 顶点位置（永远是全屏）
  const positions = new Float32Array([
    -1, -1, 1, -1, -1, 1, -1, 1, 1, -1, 1, 1
  ])
  
  gl.bindBuffer(gl.ARRAY_BUFFER, this.geometryBuffer)
  gl.bufferData(gl.ARRAY_BUFFER, positions, gl.STATIC_DRAW)  // STATIC_DRAW
}
```

### 3. 懒初始化

只有在真正需要特效时才初始化 FBO：

```typescript
getFramebuffer(index: number): WebGLFramebuffer | null {
  if (this.framebuffers.length === 0) {
    this.initFramebuffers()  // 懒初始化
  }
  return this.framebuffers[index] || null
}
```

---

## 支持的特效列表

| 特效 | 类型 | 主要参数 |
|------|------|----------|
| Flash | 闪白 | 颜色、强度 |
| Shake | 抖动 | 频率、方向 |
| Glitch | 故障 | RGB分离、扫描线、块状干扰 |
| Radial Blur | 径向模糊 | 中心点、采样数 |
| Chromatic | 色差 | 角度 |
| Pixelate | 像素化 | 像素大小 |
| Invert | 反色 | - |
| Film Grain | 老电影 | 颗粒、划痕、闪烁、复古色调 |
| Vignette | 暗角 | 半径、柔和度 |
| Split Screen | 分屏 | 分屏数、方向、间隔 |

---

## 下一篇

本系列已完结。完整目录：

1. [x] 技术选型与项目结构
2. [x] 时间轴数据模型
3. [x] WebGL 渲染与滤镜
4. [x] 转场动画实现
5. [x] WebCodecs 视频导出
6. [x] LeaferJS 贴纸系统
7. [x] 视频特效系统（本文）
