# React 核心原理：心智模型构建

本系列文章旨在通过构建准确的“心智模型”来深入理解 React。不罗列 API，而是探索 React 设计背后的“为什么”。

## 目录

### [01. 渲染公式：UI = f(state)](./01_Rendering_Equation.md)
React 的核心方程。理解声明式编程与命令式编程的区别，建立“画家与画布”的心智模型。

### [02. 组件纯度与生命周期](./02_Component_Purity.md)
为什么组件必须是纯函数？严格模式的双重检查是如何帮助发现副作用 Bug 的？

### [03. 状态快照与服务员模型](./03_State_Snapshots.md)
State 不是普通变量，而是时间切片上的快照。理解 React 的自动批处理机制（服务员模型）。

### [04. 厨房与餐桌：渲染与提交](./04_Render_Commit.md)
渲染 (Render) 并不等于更新 DOM (Commit)。深入了解 React 的三步工作流：触发 -> 渲染 -> 提交。

### [05. 状态架构：提升与归约](./05_State_Architecture.md)
单一数据源原则。如何通过状态提升 (Lifting State Up) 和 useReducer (有限状态机) 来管理复杂状态。

### [06. 同步与副作用：逃生舱](./06_Effects.md)
useEffect 的本质不是生命周期钩子，而是与外部系统的同步工具。理解依赖数组的真实含义。

### [07. 自定义 Hook：逻辑复用](./07_Custom_Hooks.md)
如何像复用函数一样复用有状态的逻辑。Hook 是“装备”而非“状态共享”。

### [08. 引用与 DOM：脱离渲染循环](./08_Refs.md)
useRef 是“口袋”。在不触发组件渲染的情况下保存数据或直接操作 DOM。

### [09. 上下文：数据传送门](./09_Context.md)
useContext 是“传送门”。解决 Prop Drilling 问题，让数据直达深层组件。

---

## 工程美学：设计与稳定

### [10. 设计模式：复合组件 (Compound Components)](./10_Compound_Components.md)
像乐高积木一样构建组件。利用隐式 Context 共享状态，告别 Props 配置地狱。

### [11. 错误边界：优雅降级 (Error Boundaries)](./11_Error_Boundaries.md)
应用的“保险丝”。防止局部 JS 错误导致整个页面白屏，提供自愈重试机制。

---

## 性能三部曲：从手动到自动

### [12. 性能优化：缓存与记忆](./12_Performance.md)
React.memo, useMemo, useCallback 三剑客。理解 React 的渲染机制，使用“卫兵”和“备忘录”阻止不必要的重复渲染。

### [13. 进阶性能：并发与架构](./13_Advanced_Performance.md)
性能优化的深水区。代码分包 (Code Splitting)、并发模式 (Concurrency) 与状态下放 (State Colocation)。

### [14. React Compiler： 自动驾驶](./14_React_Compiler.md)
自动记忆化 (Automatic Memoization)。编译器如何在构建时自动优化代码，消灭 useMemo 和 useCallback。

---

## 现代架构：全栈 React

### [15. 服务端组件 (RSC)：后端的反攻](./15_React_Server_Components.md)
打破客户端渲染的限制。零 Bundle 组件、直接访问数据库。三明治架构模型。

### [16. 服务端动作 (Server Actions)：告别 useEffect](./16_Server_Actions.md)
函数即 API。告别手动 fetch，像调用本地函数一样调用服务器逻辑。

### [17. The use Hook：统一异步与上下文](./17_The_Use_Hook.md)
React 数据流的终极统一。一个 Hook 同时处理 Context 和 Promise，支持在 if 和循环中使用。

### [18. 生态与框架：如何启动](./18_The_Ecosystem.md)
Vite vs Next.js vs Remix。理解为什么 React 官方推荐使用框架，以及如何选择适合的“交通工具”。
