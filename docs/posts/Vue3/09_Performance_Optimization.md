# Vue 3 深度精通 (九) —— 极致性能优化终极指南

性能优化涵盖从网络加载到运行时渲染的全过程。本章深入每一个细节，力求最大化利用浏览器性能。

## 网络层优化：不仅仅是 Code Splitting

除路由懒加载外，还可进行以下优化：

### Bundle Analysis

明确打包内容至关重要。使用 `rollup-plugin-visualizer` 分析打包结果。

```bash
npm install --save-dev rollup-plugin-visualizer
```

找出那些巨大的依赖（如 lodash, moment），替换为轻量级替代品（lodash-es, dayjs）。

### 预加载机制 (Prefetch/Preload)

对于首屏关键资源，使用 `<link rel="preload">`。对于可能访问的路由（如下一步跳转），使用 `<link rel="prefetch">`。

Vite 插件 `vite-plugin-pwa` 或手写 script 可以动态注入 link 标签。

## 运行时优化：在主线程上跳舞

### 调度器 (Scheduler) 与 `nextTick`

Vue 的更新是异步的。多次修改状态只会触发一次更新。

如果真的有繁重的计算任务，可以使用 `requestIdleCallback` 或 `scheduler.postTask`（实验性）切分任务，避免阻塞 UI 渲染。

```javascript
// 长任务切片
async function heavyTask() {
  const steps = 10000
  for (let i = 0; i < steps; i++) {
    process(i)
    if (i % 100 === 0) {
      // 让出主线程
      await new Promise(resolve => requestIdleCallback(resolve))
    }
  }
}
```

### Web Workers

对于纯计算逻辑（如复杂的 Excel 处理、图像压缩），不要让它占用主线程。使用 Web Worker。

推荐库：`comlink` 或 `worker-loader`（Vite 已内置支持 worker import）。

```javascript
/* worker.js */
self.onmessage = (e) => {
  const result = heavyCompute(e.data)
  self.postMessage(result)
}
```

### 虚拟列表 (Virtual List)

当列表项超过 1000 个时，渲染所有 DOM 必然卡顿。虚拟列表的核心思想是：**只渲染可视区域及其缓冲区**。

虽然 VueUse 提供了 `useVirtualList`，但理解其原理至关重要：
1.  计算总高度（itemHeight * total）。
2.  监听滚动事件 `scroll`。
3.  根据 `scrollTop` 计算 `startIndex` 和 `endIndex`。
4.  只截取 `list.slice(start, end)` 进行渲染。
5.  使用 padding-top 把可视区域顶到正确的位置。

```mermaid
graph TD
    Container[滚动容器]
    Phantom[幽灵占位 (总高度)]
    
    subgraph 可视区域
        padding[padding-top: startIndex * itemHeight]
        Item1[列表项 N]
        Item2[列表项 N+1]
        Item3[列表项 N+2]
    end
    
    Container --> Phantom
    Phantom --> 可视区域
    
    style 可视区域 fill:#b2dfdb,stroke:#00897b
```

## 服务端渲染 (SSR) / 静态站点生成 (SSG)

若首屏性能是瓶颈（SEO, FCP），SSR 是有效解决方案。

*   **SSR**: Nuxt 3。服务器直接返回渲染好的 HTML。
*   **SSG**: Vite SSG。构建时生成静态 HTML。适用于博客、文档。

## 结语

性能优化无止境。熟悉工具（Devtools, Lighthouse）、浏览器原理（重排重绘）及框架机制（Diff算法），方能在实战中游刃有余。下一篇将深入 Vue 3 的**内核源码**，揭开响应式与编译器的底层机制。
