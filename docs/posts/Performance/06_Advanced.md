# 第六部分：前沿技术与未来趋势

当常规手段（压缩、缓存、代码分割）已经做到极致，LCP 依然卡在 1.5s 无法突破时，说明你需要**架构级**的升级。

## 6.1 渲染架构的变革：CSR -> SSR -> ISR

### 1. 客户端渲染 (CSR) 的阿喀琉斯之踵
*   **瀑布流**：下载 HTML (空) -> 下载 JS -> 执行 JS -> 请求 API -> 渲染 DOM。
*   用户要把这个链条全跑完才能看到东西。

### 2. 服务端渲染 (SSR) 的回潮
*   **原理**：Node.js 服务器直接执行 React/Vue 代码，生成充满数据的 HTML 字符串。
*   **优势**：FCP (First Contentful Paint) 极快。因为 HTML 一下载完就有内容。
*   **代价**：
    *   **TTFB 变长**：服务器需要时间去请求数据库和拼装 HTML。
    *   **Hydration (水合)**：HTML 虽然画出来了，但不可交互（按钮点不动）。必须等 JS 下载并执行完 `hydrate()`，绑定事件监听器后，页面才“活”过来。
    *   *优化 Metric*：关注 **Tti (Time to Interactive)**。

### 3. ISR (Incremental Static Regeneration) - 动静结合
Next.js 提出的 ISR 完美平衡了静态生成的“快”和动态渲染的“准”。
*   **流程**：
    1.  用户 A 访问 `/product/123`，CDN 立即返回昨天生成的 HTML（瞬开，但价格可能是旧的）。
    2.  Next.js 后台触发 Regeneration，重新拉新价格生成新 HTML。
    3.  用户 B 访问 `/product/123`，看到了新 HTML。
*   **核心参数**：`revalidate: 60` (秒)。

## 6.2 WebAssembly (Wasm)：突破 JS 算力天花板

JavaScript 是单线程且动态类型的，天生不适合密集计算。

### Case Study: Figma 的 Web 版
*   **挑战**：在浏览器里做矢量图形编辑，涉及大量矩阵运算和几何渲染。用 JS 跑太慢，且 GC (垃圾回收) 会造成卡顿。
*   **解法**：核心引擎用 C++ 编写，编译成 Wasm。
*   **收益**：
    *   性能接近原生应用（Native）。
    *   无 GC 暂停（C++ 手动管理内存）。
*   **平民级应用**：
    *   **FFmpeg.wasm**：浏览器前端直接转码视频，无需上传后台。
    *   **Canvas 滤镜**：图像处理速度比 JS 快 10-20 倍。

## 6.3 浏览器的新“黑魔法”

### 1. `fetchpriority`
资源加载也有 VIP 通道。
*   `high`: LCP 图片。
*   `low`: 屏幕下方的图片、统计脚本。
```html
<img src="hero-banner.jpg" fetchpriority="high" alt="Hero">
```
*   **效果**：LCP 资源会插队到 CSS 之前下载（在部分浏览器支持下），直接提升 LCP。

### 2. Speculative Rules API (Prerender)
这是 Chrome 团队目前力推的“作弊级”优化。
*   **原理**：你预测用户**很可能**下一步会点“详情页”，于是告诉浏览器：“趁现在没事干，悄悄在后台把详情页渲染好”。
*   **体验**：当用户真的点击链接时，耗时为 **0ms**。页面是瞬间替换的。
```html
<script type="speculationrules">
{
  "prerender": [
    {
      "source": "list",
      "urls": ["/page/2", "/page/3"]
    }
  ]
}
</script>
```

---

**(下一章预告)**：技术再牛，如果没人守门，代码库一个月就会腐烂。我们需要把性能优化写进制度，写进 DevOps 流水线。
