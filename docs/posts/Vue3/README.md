# Vue 3 深度精通系列 (Deep Mastery of Vue 3)

Vue 3 深度精通系列是一套专为进阶开发者打造的权威指南，旨在帮助开发者从 API 使用者晋升为框架专家。

本系列文章深入源码底层，剖析设计哲学，并结合生产环境的最佳实践，全方位解析 Vue 3 的精髓。

## 📚 目录导航 (Table of Contents)

### 第零阶段：极速入门 (Beginner Friendly)
*   **[00. 极速入门 (零基础篇)](./00_Quick_Start.md)** 🆕
    *   核心指令速查：`v-if`, `v-for`, `v-model`。
    *   响应式进阶：`computed`, `watch` 的使用时机。
    *   状态管理：`Pinia` 最简上手指南。
    *   组件拼装：`defineProps`与`defineEmits`最简用法。

### 第一阶段：核心基础与思维重构
*   **[01. 核心架构与设计哲学](./01_Introduction_and_Core_Concepts.md)**
    *   理解 Vue 3 的"三位一体"架构（响应式、编译器、运行时）。
    *   掌握 `createApp` 与 `v-memo` 等核心设计理念。
*   **[02. 响应式系统的进阶精通](./02_Reactivity_Essentials.md)**
    *   深入 Proxy 机制与 `RefImpl` 实现。
    *   掌握 `shallowRef`、`customRef`、`markRaw` 等高阶 API 及其应用场景。
*   **[03. 组件化高阶技巧](./03_Component_Deep_Dive.md)**
    *   玩转多重 `v-model` 与自定义修饰符。
    *   透传 Attributes (`$attrs`) 与递归组件的最佳实践。
*   **[04. Composition API 生产级实战指南](./04_Composition_API_Patterns.md)**
    *   告别 "Logic Scatter"（逻辑分散），拥抱高内聚。
    *   掌握依赖注入 (`provide`/`inject`) 与 Composable 的封装艺术。
*   **[05. Vue Router 4 的路由哲学](./05_Vue_Router_Mastery.md)**
    *   动态路由权限控制的完整实现流程。
    *   导航守卫 (`Navigation Guards`) 的最佳实践与坑点规避。

### 第二阶段：全家桶与工程化
*   **[06. Pinia：重塑状态管理](./06_Pinia_State_Management.md)**
    *   抛弃 Vuex，拥抱更轻量、类型更安全的 Pinia。
    *   Setup Store 模式、插件机制与数据持久化。
*   **[07. 工程化基石与最佳实践](./07_Tooling_and_Best_Practices.md)**
    *   Vite 插件开发入门。
    *   TypeScript 高级类型 (`defineProps`, `withDefaults`)。
    *   现代 Linter 配置 (ESLint Flat Config + Antfu)。

### 第三阶段：性能与黑科技
*   **[08. 鲜为人知的顶级技巧 (Tips & Tricks)](./08_Vue3_Tips_and_Tricks.md)**
    *   `defineModel` (Vue 3.4+)、`defineOptions` 等语法糖。
    *   `Teleport`、`Suspense` 与自定义指令的高阶用法。
*   **[09. 极致性能优化终极指南](./09_Performance_Optimization.md)**
    *   网络层优化 (Bundle Analysis, Prefetch)。
    *   运行时优化 (Web Workers, 虚拟列表原理)。

### 第四阶段：源码、生态与未来 (Mastery Level)
*   **[10. 源码级解析与核心原理](./10_Internal_Mechanics.md)** 🔥 *Hardcore*
    *   **响应式地图**：`WeakMap -> Map -> Set` 的可视化解析。
    *   **Diff 算法**：双端对比与最长递增子序列 (LIS) 的完整流程图解。
    *   **编译器魔法**：Block Tree 与 PatchFlags 如何实现靶向更新。
    *   **调度器**：异步队列的去重与排序机制。
*   **[11. 全栈生态与未来展望](./11_Ecosystem_and_Future.md)**
    *   **Vite HMR** 原理 (O(1) 复杂度)。
    *   **Nuxt 3** 全栈：文件路由、SSR 数据获取 (`useFetch`) 与 Nitro 引擎。
    *   **测试策略**：Vitest 单元测试与 Vue Test Utils 组件测试。
    *   **未来**：Vapor Mode (无虚拟 DOM) 前瞻。
*   **[12. 高级设计模式与实战技巧 (Advanced Skills)](./12_Advanced_Patterns_and_Skills.md)** 💎 *New*
    *   **Composable 设计**：参数归一化 (`toValue`) 与副作用管理 (`onScopeDispose`)。
    *   **泛型组件**：打造类型安全的通用 UI 库。
    *   **Pinia 进阶**：私有状态与 Store 组合模式。

## 🌟 系列特色

*   **深度**：直击源码核心，不留死角。
*   **图解**：包含大量 Mermaid 流程图，可视化复杂逻辑（Diff 算法、HMR 流程等）。
*   **前沿**：涵盖 Vue 3.4+ 最新特性 (defineModel) 与未来趋势 (Vapor Mode)。
*   **实战**：所有代码示例均源自真实的生产环境。

---
