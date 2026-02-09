# Vue 3 深度精通 (十) —— 源码级解析与核心原理

我们终于来到了终章。这一章不仅是"面试宝典"，更是为了让你在复杂问题面前能像编译器一样思考。

## 响应式系统 (Reactivity)：Effect Scope 与 Clean Up

我们已经知道 `Proxy` 拦截了副作用。但当 `watch` 或 `computed` 被卸载时，Vue 是怎么知道不要继续监听的？

### Effect Scope

Vue 3 引入了 `effectScope()`，这是一个高级 API，用于批量收集副作用。

```javascript
/* 内部实现概览 */
class EffectScope {
  run(fn) {
    this.active = true
    return fn()
  }
  stop() {
    this.effects.forEach(e => e.stop()) // 停止所有子 effect
  }
}
```

当组件卸载 (`onUnmounted`) 时，其实是停止了该组件作用域内的所有 `effect`。这就是为什么在 `script setup` 中我们不需要手动销毁 watcher。

## 调度器 (Scheduler) 与 `flushJobs`

Vue 的响应式是**去抖动**的。

假设你改了 10 次 `state.count`，Vue 并不是 patch 10 次 DOM，而是放入一个 `queue` 中，然后在下一个微任务（Promise.resolve().then）中一次性 `flushJobs`。

这也解释了为什么需要 `nextTick`。

```javascript
import { nextTick } from 'vue'

state.count = 1
console.log(dom.innerHTML) // 还是旧的 0
await nextTick()
console.log(dom.innerHTML) // 变成了 1
```

`nextTick` 本质上就是把自己推入了那个微任务队列的最后。

## 渲染器 (Renderer)：Diff 算法的秘密

### 最长递增子序列 (LIS)

Vue 3 的 Diff 算法被称为 `Fast Diff`。在处理有 Key 的列表更新时，如果只是顺序变了（比如 `[1, 2, 3]` 变成 `[1, 3, 2]`），它可以计算出最小移动路径。

利用 LIS 算法，Vue 可以在 O(N log N) 的时间内找出不需要移动的元素序列，只移动其他的。

对比 React 的 O(N) 启发式算法，Vue 在处理大量节点乱序时通常表现更优。

## 编译器 (Compiler)：动静分离的极致

### Hoist Static与 Patch Flags

再回顾一下我们在第一章提到的静态提升 (Static Hoisting)。编译器还会做什么？

*   **Cache Handlers**: 事件处理函数可能会在重新渲染时生成新的 inline function，导致 props change 触发子组件更新。Vue 3 会自动缓存它们。
    ```javascript
    // 编译前
    <div @click="e => v = e.target.value" />
    
    // 编译后 (大概)
    _cache[0] || (_cache[0] = e => v = e.target.value)
    ```

*   **Block Tree**: 编译器会将模板分块。只有包含动态内容的节点才会被追踪。这使得 Diff 的复杂度与动态节点数量成正比，而不是模板总大小。

## 结语：通往大师之路

至此，我们的 Vue 3 深度精通系列完结。从应用架构到源码细节，我们几乎涵盖了 Vue 3 的方方面面。

但这只是开始。Vue 生态还在快速演进（如 Vapor Mode）。保持好奇心，不断探索，你终将成为真正的大师。
