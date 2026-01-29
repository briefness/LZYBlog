# 转场效果是怎么实现的

> BaseCut 技术博客第四篇。这篇聊转场——两个画面之间的淡入淡出、滑动、擦除是怎么做的。

---

## 什么是转场

最简单的解释：**让画面 A 逐渐变成画面 B**。

没有转场的话，两个片段之间是硬切：

```
时间轴：

片段 A    |    片段 B
oooooooooo|oooooooooo
          ↑
      瞬间切换
```

有转场的话：

```
片段 A      转场区间      片段 B
ooooooooo[A+B 混合区]ooooooooo
         ↑───────────↑
       起点         终点
```

---

## 转场的历史：电影中的视觉语言

转场不是瞎搞，它是电影百年历史沉淀下来的**视觉语言**。

### 硬切（Hard Cut）

镜头直接切换，没有任何过渡。

用途：
- 同一场景的不同角度
- 紧张、快节奏的剪辑

### 淡入淡出（Fade In/Out）

画面逐渐变亮或变暗，通常是黑场。

用途：
- 场景开始/结束
- 表示时间流逝

### 叠化（Dissolve）

两个画面叠加在一起，A 逐渐消失，B 逐渐出现。

用途：
- 平行时空
- 回忆、梦境
- 时间流逝

### 擦除（Wipe）

一条线从一侧推到另一侧，后面露出新画面。

用途：
- 《星球大战》经典转场
- 复古风格

---

## 转场的数学本质

### 核心公式：线性插值

不管多复杂的转场，核心都是一个公式：

```
output = A × (1 - progress) + B × progress
```

其中 `progress` 从 0 变到 1：

```
progress = 0.0  →  100% A，0% B
progress = 0.5  →  50% A，50% B
progress = 1.0  →  0% A，100% B
```

这个公式叫 **Linear Interpolation**，简称 **Lerp**，是图形学最常用的公式之一。

### 不同转场类型

虽然公式一样，但 A 和 B 的"混合方式"可以有很多变化：

| 类型 | 混合方式 |
|------|----------|
| 淡入淡出 | 整个画面透明度渐变 |
| 滑动 | B 从画面外推入，A 被推走 |
| 擦除 | 一条线逐渐划过，后面露出 B |
| 缩放 | A 缩小消失，B 放大出现 |

---

## 缓动函数（Easing）

如果 progress 匀速从 0 增长到 1，动画会很"机械"，像机器人一样。

真实世界的物体都有惯性：
- 汽车启动：先慢后快（Ease-In）
- 门关闭：先快后慢（Ease-Out）
- 弹簧：快-慢-回弹

### 常用缓动函数

**线性（Linear）**

```javascript
function linear(t) {
  return t
}
```

没有加速度，匀速变化。

**缓入（Ease-In）**

```javascript
function easeIn(t) {
  return t * t
}
```

开始慢，结束快。

**缓出（Ease-Out）**

```javascript
function easeOut(t) {
  return 1 - (1 - t) * (1 - t)
}
```

开始快，结束慢。

**缓入缓出（Ease-In-Out）**

```javascript
function easeInOut(t) {
  return t < 0.5
    ? 2 * t * t
    : 1 - Math.pow(-2 * t + 2, 2) / 2
}
```

两头慢，中间快。最常用。

### 对比效果

```
时间：  0    0.25   0.5   0.75   1
线性：  0    0.25   0.5   0.75   1.0
缓动：  0    0.12   0.5   0.88   1.0
```

缓动让动画有"弹性"，更自然。

---

## WebGL 实现

### 双纹理绑定

转场需要同时访问两帧画面，所以要绑定两个纹理：

```javascript
// 绑定 A 帧到纹理槽位 0
gl.activeTexture(gl.TEXTURE0)
gl.bindTexture(gl.TEXTURE_2D, textureA)
gl.uniform1i(uTexALocation, 0)

// 绑定 B 帧到纹理槽位 1
gl.activeTexture(gl.TEXTURE1)
gl.bindTexture(gl.TEXTURE_2D, textureB)
gl.uniform1i(uTexBLocation, 1)

// 传入进度
gl.uniform1f(uProgressLocation, progress)

// 渲染
gl.drawArrays(gl.TRIANGLE_STRIP, 0, 4)
```

### 淡入淡出着色器

```glsl
uniform sampler2D u_texA;
uniform sampler2D u_texB;
uniform float u_progress;

void main() {
  vec4 colorA = texture2D(u_texA, v_texCoord);
  vec4 colorB = texture2D(u_texB, v_texCoord);
  
  // GLSL 内置的 mix 函数就是 Lerp
  gl_FragColor = mix(colorA, colorB, u_progress);
}
```

### 滑动着色器

```glsl
void main() {
  // A 向左移动
  vec2 uvA = v_texCoord + vec2(u_progress, 0.0);
  // B 从右边进来
  vec2 uvB = v_texCoord - vec2(1.0 - u_progress, 0.0);
  
  vec4 colorA = texture2D(u_texA, uvA);
  vec4 colorB = texture2D(u_texB, uvB);
  
  // 根据 UV 坐标判断显示哪个
  if (v_texCoord.x > 1.0 - u_progress) {
    gl_FragColor = colorB;
  } else {
    gl_FragColor = colorA;
  }
}
```

### 擦除着色器

```glsl
void main() {
  vec4 colorA = texture2D(u_texA, v_texCoord);
  vec4 colorB = texture2D(u_texB, v_texCoord);
  
  // 一条竖线从左向右扫过
  if (v_texCoord.x < u_progress) {
    gl_FragColor = colorB;
  } else {
    gl_FragColor = colorA;
  }
}
```

---

## 转场时机判断

播放器在渲染每一帧时，需要判断当前是否处于转场区间：

```typescript
function render(currentTime: number) {
  // 查找当前时间是否有转场
  const transition = findActiveTransition(currentTime)
  
  if (transition) {
    // 计算进度 (0-1)
    const rawProgress = (currentTime - transition.startTime) / transition.duration
    
    // 应用缓动函数
    const progress = easeInOut(rawProgress)
    
    // 获取两帧画面
    const frameA = getFrame(transition.clipA, currentTime)
    const frameB = getFrame(transition.clipB, currentTime)
    
    // 渲染转场
    webgl.renderTransition(frameA, frameB, progress, transition.type)
  } else {
    // 正常渲染单帧
    const frame = getCurrentFrame(currentTime)
    webgl.renderFrame(frame)
  }
}
```

---

## 下一篇

讲视频导出——怎么把编辑好的内容变成 MP4 文件，以及 WebCodecs 的原理。

---

**系列目录**

1. [x] 技术选型与项目结构
2. [x] 时间轴数据模型
3. [x] WebGL 渲染与滤镜
4. [x] 转场动画实现（本文）
5. [ ] WebCodecs 视频导出
6. [ ] LeaferJS 贴纸系统
