# 第五部分：框架特有优化 —— 以主流框架为例

框架封装了底层操作，同时也“隐藏”了开销。理解框架的调度机制，是实现高性能的关键。

## 5.1 React：对抗不必要的渲染

React 的核心心智模型是：`UI = f(state)`。当 State 变化，默认行为是**全量递归渲染子树**。

### 1. Visualizing Re-renders (可视化重渲染)
建议在开发环境安装 **React DevTools**，开启 "Highlight updates when components render"。
*   **现象**：在输入框输入字符，整个页面的 Header、Sidebar、Footer 均出现绿色闪烁框（重渲染）。
*   **后果**：虽然 Virtual DOM 会通过 Diff 避免真实 DOM 操作，但生成 Virtual DOM 树本身（JS执行）就是纯纯的 CPU 浪费。
*   **Fix**: 善用 `React.memo`。虽然包裹组件有微小开销，但对于大型列表项或复杂子树，它是防止“父组件手抖，子组件地震”的银弹。

### 1a. 深入底层：Fiber 架构与时间分片 (Time Slicing)
React 15 的递归渲染一旦开始就无法中断，会导致卡顿。React 16+ 引入了 Fiber 架构。
*   **核心逻辑**：将渲染任务拆分为微小的“工作单元 (Fiber Nodes)”。每执行完一个单元，React 都会询问浏览器：“是否存在更高优先级的任务（如用户点击）？”若有，React 会让出主线程。
*   **[Diagram Trigger]**: *插入 React Fiber 链表图：展示任务如何被切分并具备优先级。*
```mermaid
graph TD
    subgraph Fiber_Tree [Fiber 链表结构]
    Root[FiberRoot] --> HostRoot
    HostRoot --> App
    App --> Header
    App --> List
    List --> Item1
    List --> Item2
    Item1 --> p1
    end

    subgraph Scheduler [调度器]
    TaskQueue[任务队列] -- 分片执行 --> Fiber_Tree
    Browser[浏览器主线程] -- 1. Yield (让出) --> Scheduler
    Scheduler -- 2. Continue (恢复) --> Fiber_Tree
    UserInput[用户高优交互] -- 插队 --> TaskQueue
    end

    style Scheduler fill:#e1f5fe,stroke:#01579b
    style Fiber_Tree fill:#fff9c4,stroke:#fbc02d
```

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
    *   **Bug**：快速输入时，因 `heavyFilter` 执行缓慢（如 100ms），导致输入框卡顿，字符上屏延迟 (INP 变差)。
    *   **即使加了防抖 (Debounce) 也没用**：防抖只能减少请求次数，不能解决“一旦开始渲染就卡死主线程”的问题。
    *   **Fix with `useDeferredValue`**:
        ```javascript
        const deferredQuery = useDeferredValue(query);
        // 使用 memo 确保 heavyFilter 不会在无关渲染中重复执行
        // 列表渲染使用的是“延迟版”query (低优先级)，输入框使用的是“实时版”query (高优先级)
        const list = useMemo(() => heavyFilter(items, deferredQuery), [deferredQuery]);
        ```
        ```javascript
        const deferredQuery = useDeferredValue(query);
        // 列表渲染使用的是“延迟版”query，输入框使用的是“实时版”query
    *   **效果**：输入框始终流畅（高优先级），列表更新可以稍后一点点（低优先级，可被中断）。

## 5.2 Vue：精细的响应式系统

### 0. 编译时黑科技：Static Hoisting (静态提升)
Vue 3 相比 React 的性能优势很大程度上来自于编译器。
*   **静态提升**：Vue 的编译器甚至能分析出模板中哪些部分是永远不会变的（静态节点），直接将它们定义在渲染函数之外。
*   **Patch Flags**：对于动态节点，编译器会打上标记（如 `TEXT`, `CLASS`）。
*   **实战意义**：React 的 Diff 是全量遍历，而 Vue 的 Diff 是“跳跃式”的。它只追踪带标记的动态节点，完全跳过静态子树，实现了极其高效的 DOM 更新。

Vue 的依赖收集机制让它天生比 React 更少发生“无脑重渲染”，但在处理大数据量时有特定短板。

### 1. 响应式的代价
Vue 2 用 `Object.defineProperty`，Vue 3 用 `Proxy`。它们都会**深度遍历**数据对象。
*   **[Diagram Trigger]**: *插入 Proxy 响应式原理图：展示依赖收集 (Track) 与触发更新 (Trigger) 的过程。*
```mermaid
graph LR
    subgraph Reactive_System [响应式系统 (Proxy)]
    Component(组件渲染) -- 1. Read/Getter --> Handler
    Handler{Proxy Handler}
    Handler -- 2. Track (收集依赖) --> Dep[Dep Map]
    
    DataChange(数据修改) -- 3. Write/Setter --> Handler
    Handler -- 4. Trigger (触发更新) --> Effect[Effect Scheduler]
    Effect -- 5. Update --> Component
    end

    style Reactive_System fill:#f3e5f5,stroke:#7b1fa2
    style Dep fill:#fff9c4,stroke:#fbc02d
```

*   **Case Study: 巨大表格的初始化**
    *   **场景**：从接口拉取了 5000 条数据，直接 `this.tableData = data`。
    *   **现象**：接口很快返回了，但浏览器卡死 2 秒才显示内容。
    *   **火焰图分析**：主线程被 `reactiveGetter` 和 `reactiveSetter` 占满。Vue 正在努力把这 5000 条数据的每个属性都变成响应式的。
    *   **Fix**：`shallowRef` (Vue 3) 或 `Object.freeze` (Vue 2)。
    *   **Tip**: Vue 3.4 引入了 **Computed Stability** 优化。如果不改变计算结果，计算属性不会触发副作用。
    *   **原理**：明确告知 Vue 仅需在最外层替换时响应，内部属性变化无需监听。

### 2. 虚拟滚动 (Virtual Scroller) 实现原理
当 DOM 节点数量超过 3000 个，浏览器渲染就需要几百毫秒。滚动时 Recalculate Style 因为节点多，更是卡顿。
*   **核心逻辑**：
    *   计算可视区域高度（如 500px）。
    *   计算单行高度（如 50px）。
    *   得出可视数量：10 条。
    *   **只渲染**：`startIndex` 到 `endIndex` 之间的数据。
    *   利用 `padding-top` 和 `padding-bottom` 把滚动条撑开，模拟真实高度。
*   **效果**：无论数据是 1 万条还是 100 万条，DOM 节点始终只有 20 个。FPS 稳定在 60。
*   **[Diagram Trigger]**: *插入虚拟滚动原理图：展示可视区 (Viewport) 与实际 DOM (List) 的对应关系。*
```mermaid
graph TD
    subgraph Virtual_List [虚拟列表容器]
    TotalHeight[占位高度 (padding-top + padding-bottom)]
    
    subgraph Viewport [可视区域 (window)]
    RenderedItems[实际渲染节点 (Item 100-110)]
    end
    
    TotalHeight -- 包含 --> Viewport
    end
    
    Data[百万条数据源] -- 计算 slice(start, end) --> RenderedItems
    Scroll[滚动事件] -- 重新计算 start 索引 --> Data
```

#### ⚠️ 避坑：为什么不能用 index 做 key？
    *   **原理**：若在列表头部插入了一个元素，所有后续元素的 `index` 都会变化。Vue/React 会判定**所有组件状态变更**，从而触发全量 Patch（原地复用 DOM 但更新内容）。
*   **后果**：性能血崩。始终使用唯一的 `id` 作为 key，这样 Diff 算法才能识别出“这只是一个移动操作”，仅执行一次 DOM `insertBefore`。

#### 💡 现代浏览器原生特性
*   **`content-visibility: auto`**：一行 CSS 就能让浏览器跳过视口外元素的内容渲染（Layout/Paint），效果类似虚拟滚动但成本极低。
*   **`object-fit: contain`**：配合 `aspect-ratio` 使用，防止图片加载过程中的布局跳动。

## 5.3 总结：心智负担 vs 自动优化

*   **React**：默认“暴力”重渲染。
    *   **优化策略**：**“减法优化”**。
    *   **手段**：开发者需要手动使用 `memo`、`useCallback` 和并发 API (Concurrent Features) 来避免不必要的更新。
*   **Vue**：默认“精细”追踪。
    *   **优化策略**：**“脱钩优化”**。
    *   **手段**：在处理非 UI 相关的巨量纯数据时，开发者需要使用 `shallowRef` 来跳过响应式系统的深度追踪，减轻内存和 CPU 负担。

---

**(下一章预告)**：前端不仅仅是切图和调 API。Server-Side Rendering (SSR) 能让首屏快如闪电，WebAssembly 能让浏览器跑视频剪辑。未来已来。
