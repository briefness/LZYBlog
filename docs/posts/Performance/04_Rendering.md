# 第四部分：渲染性能优化 —— 丝滑般的交互体验

如果 Performance Panel 里的紫色（Rendering）和绿色（Painting）条太长，说明你的 CSS 写法或者 DOM 操作正在“虐待”浏览器内核。

## 4.1 关键渲染路径 (CRP) 的微观世界
浏览器不是一次性画完页面的。
1.  **Parse HTML -> DOM** (字节流 -> 令牌 -> 节点 -> 树)
2.  **Parse CSS -> CSSOM**
3.  **Combine -> Render Tree** (DOM 树中可见的节点 + CSS 样式)
4.  **Layout** (计算盒模型：位置、大小)
5.  **Paint** (填充像素：绘制文字、颜色、阴影)
6.  **Composite** (GPU合成图层)

### 🧐 为什么 `opacity` 比 `visibility` 快？
这需要理解浏览器的 **Layer Model (分层模型)**。
*   现代浏览器（如 Chrome）会将某些特定元素提升为独立的**合成层 (Compositing Layer)**。
*   **GPU 加速**：合成层由 GPU 处理，而不是 CPU。
*   当改变 `opacity` 或 `transform` 时，浏览器不需要重新计算 Layout (回流) 也不需要 Paint (重绘)，只需要 GPU 调整一下纹理的透明度或坐标。这被称为 **Composite-Only Properties**。
*   相比之下，`visibility: hidden` 可能会触发 Paint，甚至在某些复杂布局下触发 Layout。

## 4.2 强制同步布局 (Forced Synchronous Layout) —— 性能杀手

### Case Study: 滚动列表卡顿
*   **代码片段**：
    ```javascript
    // Bad Practice
    function resizeAllParagraphs() {
      const paragraphs = document.querySelectorAll('p');
      for (let i = 0; i < paragraphs.length; i++) {
        // 读取宽度：触发 Layout！
        const width = paragraphs[i].offsetWidth;
        // 写入宽度：标记 Layout 脏（Invalidate Layout）
        paragraphs[i].style.width = width + 'px';
      }
    }
    ```
*   **问题解析**：
    *   正常流水线：JS -> Style -> Layout -> Paint。
    *   上述代码：JS -> **Layout** -> JS -> **Layout** -> JS -> **Layout**...
    *   每次读取 `offsetWidth`，浏览器为了给你返回最新值，被迫立即中断 JS，先执行一次 Layout。如果在循环里这么做，就是**布局抖动 (Layout Thrashing)**。
*   **火焰图特征**：Performance 面板里看到密密麻麻的小紫色长条（Layout），且每个条上方都有红色警告。
*   **Fix**：读写分离。先批量读（Force 一次 Layout），再批量写。

## 4.3 脚本执行：给主线程喘息的机会

### 1. 长任务 (Long Task) 的危害
浏览器主线程是单线程的。如果你写了一个 `while(true)`，UI 就死锁了。
**标准**：任何超过 **50ms** 的任务都被视为长任务。

### 2. Web Workers 与 并行计算
*   **场景**：图片滤镜处理、大文件 MD5 计算。
*   **实战**：把这些 CPU 密集型任务丢给 Worker。主线程只负责 UI 响应。

### 3. requestAnimationFrame vs requestIdleCallback
*   **requestAnimationFrame (rAF)**：
    *   **时机**：每一帧渲染**之前**执行。高优先级。
    *   **用途**：实现流畅动画。务必在 16.6ms 内完成，否则掉帧。
*   **requestIdleCallback**：
    *   **时机**：一帧渲染完，如果还有**剩余时间**，才执行。低优先级。
    *   **用途**：数据上报、预加载资源、非关键 DOM 初始化。

---

**(下一章预告)**：React 和 Vue 帮我们屏蔽了 DOM 操作，但它们也有自己的瓶颈。为什么 React 要搞 Fiber？为什么 Vue 3 要搞 Proxy？下一部分我们深入框架内部。
