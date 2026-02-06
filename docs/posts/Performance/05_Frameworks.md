# 第五部分：框架特有优化 —— 以主流框架为例

框架帮我们做了很多事，也“隐藏”了很多开销。你需要理解框架的调度机制，才能与它共舞。

## 5.1 React：对抗不必要的渲染

React 的核心心智模型是：`UI = f(state)`。当 State 变化，默认行为是**全量递归渲染子树**。

### 1. Visualizing Re-renders (可视化重渲染)
建议在开发环境安装 **React DevTools**，开启 "Highlight updates when components render"。
*   **现象**：你在输入框打一个字，结果整个页面的 Header、Sidebar、Footer 全部闪了一下绿色框。
*   **后果**：虽然 Virtual DOM 会通过 Diff 避免真实 DOM 操作，但生成 Virtual DOM 树本身（JS执行）就是纯纯的 CPU 浪费。

### 2. Context 的性能陷阱
*   **场景**：Context Provider 放在了 App 根部，value 是一个大对象 `{ user, theme, settings, ... }`。
*   **问题**：任何一个小属性（如 theme）改变，**所有**消费了该 Context 的组件都会强制重渲染，即使它只用了 `user` 字段。
*   **优化**：
    *   **拆分 Context**：`UserContext`, `ThemeContext`。
    *   **Context Selector** (或者使用 Zustand/Jotai 等原子化状态库)。

### 3. Concurrent Mode (并发模式) 的降维打击
React 18 的 `useTransition` 解决了“响应度”问题。
*   **Case Study: 搜索联想卡顿**
    *   **代码**：
        ```javascript
        const [query, setQuery] = useState('');
        // 这是一个极其耗时的过滤操作
        const list = useMemo(() => heavyFilter(items, query), [query]);
        ```
    *   **Bug**：用户快速打字时，因为 `heavyFilter` 稍微有点慢（比如 100ms），导致输入框卡顿，字符上屏不跟手 (INP 变差)。
    *   **即使加了防抖 (Debounce) 也没用**：防抖只能减少请求次数，不能解决“一旦开始渲染就卡死主线程”的问题。
    *   **Fix with `useDeferredValue`**：
        ```javascript
        const deferredQuery = useDeferredValue(query);
        // 列表渲染使用的是“延迟版”query，输入框使用的是“实时版”query
        const list = useMemo(() => heavyFilter(items, deferredQuery), [deferredQuery]);
        ```
    *   **效果**：输入框始终流畅（高优先级），列表更新可以稍后一点点（低优先级，可被中断）。

## 5.2 Vue：精细的响应式系统

Vue 的依赖收集机制让它天生比 React 更少发生“无脑重渲染”，但在处理大数据量时有特定短板。

### 1. 响应式的代价
Vue 2 用 `Object.defineProperty`，Vue 3 用 `Proxy`。它们都会**深度遍历**数据对象。
*   **Case Study: 巨大表格的初始化**
    *   **场景**：从接口拉取了 5000 条数据，直接 `this.tableData = data`。
    *   **现象**：接口很快返回了，但浏览器卡死 2 秒才显示内容。
    *   **火焰图分析**：主线程被 `reactiveGetter` 和 `reactiveSetter` 占满。Vue 正在努力把这 5000 条数据的每个属性都变成响应式的。
    *   **Fix**：`shallowRef` (Vue 3) 或 `Object.freeze` (Vue 2)。
    *   **原理**：告诉 Vue，我只要最外层替换时响应，内部属性变化不需要监听。

### 2. 虚拟滚动 (Virtual Scroller) 实现原理
当 DOM 节点数量超过 3000 个，浏览器渲染就需要几百毫秒。滚动时 Recalculate Style 因为节点多，更是卡顿。
*   **核心逻辑**：
    *   计算可视区域高度（如 500px）。
    *   计算单行高度（如 50px）。
    *   得出可视数量：10 条。
    *   **只渲染**：`startIndex` 到 `endIndex` 之间的数据。
    *   利用 `padding-top` 和 `padding-bottom` 把滚动条撑开，模拟真实高度。
*   **效果**：无论数据是 1 万条还是 100 万条，DOM 节点始终只有 20 个。FPS 稳定在 60。

---

**(下一章预告)**：前端不仅仅是切图和调 API。Server-Side Rendering (SSR) 能让首屏快如闪电，WebAssembly 能让浏览器跑视频剪辑。未来已来。
