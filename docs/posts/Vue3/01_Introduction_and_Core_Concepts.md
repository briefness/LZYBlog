# Vue 3 核心原理（一）—— 核心架构：响应式、编译器与渲染器的三位一体

> **环境：** Vue 3.4+ 源码架构级认知，适用所有现代组件化框架纵向对比

长列表卡顿、第三方图表库挂载后内存持续攀升——这类问题的根源往往不在组件逻辑，而在对 Vue 3 底层架构的理解缺口。这篇从响应式系统、编译器、渲染器三个维度拆解 Vue 3 的核心机制。

---

## 1. 架构概览：三个独立模块

Vue 3 的核心由三个可独立使用的模块构成，在极端定制场景下可以单独拆出来用。

1. **响应式系统 (`@vue/reactivity`)**：纯数据流引擎，与宿主环境无关。可以在 Node.js 后端独立使用，做依赖追踪和计算触发。
2. **编译器 (`@vue/compiler-*`)**：把模板文本经过 Parser → Transform → Codegen 三阶段，输出高效的 JavaScript 渲染函数。
3. **运行时渲染器 (`@vue/runtime-core`)**：接收渲染函数产出的 VNode 树，负责创建、比对、更新真实 DOM（或其他宿主平台）。

### 从 `new Vue()` 到 `createApp()`

Vue 2 的 `Vue.use()` 是全局注册——路由、状态管理等插件挂在唯一的全局 Vue 对象上。同一页面运行两个配置不同的 Vue 应用时，它们共享插件状态，互相干扰。

Vue 3 的 `createApp()` 返回独立的应用实例，每个实例有自己的插件、全局组件和配置，互不影响。

```javascript
import { createApp } from 'vue'
import App from './App.vue'

// 两个实例完全隔离，插件和配置互不影响
const appInstanceA = createApp(App)
const appInstanceB = createApp(App)

appInstanceA.use(RouterA)
appInstanceB.mount('#other-container')
```

## 2. 渲染机制

### VNode

`<template>` 里的内容经过 Compiler 处理后，传给运行时的不是 HTML 标签，而是 VNode 对象树。

```javascript
import { h } from 'vue'

const dummyVnode = h('div', { id: 'foo' }, 'Hello')
/*
VNode 结构:
{
  type: 'div',
  props: { id: 'foo' },
  children: 'Hello',
  el: null,       // 挂载前为 null，挂载后指向真实 DOM 节点
  shapeFlag: 1,   // 位运算枚举，标识节点类型（普通元素）
  patchFlag: 0    // 编译器静态分析结果，0 表示完全静态，diff 时可跳过
}
*/
```

### 渲染器的跨平台能力

`@vue/runtime-core` 里不存在 `document.createElement`——所有 DOM 操作通过可替换的渲染器接口传入。

**Trade-offs**：平台解耦增加了抽象层数和函数调用开销。换来的是渲染器可替换——同一套组件逻辑可以渲染到 Canvas、终端，或对接原生移动端 View。

## 3. 模板编译与静态提升

模板的格式约束让编译器可以在构建阶段做静态分析：对不会变化的节点打上 `patchFlag: 0`，diff 时直接跳过，不参与比对。

### `v-memo`

两万行长表格做列高亮切换时，每次高亮变化会触发整个列表的 diff。Vue 3.2 的 `v-memo` 可以在依赖项未变化时跳过整棵子树。

```html
<!-- 依赖数组未变化时，整个 div 及其所有子节点跳过 diff -->
<div v-for="item in list" :key="item.id" v-memo="[item.id === selectedId]">
  <p>复杂图表渲染：{{ item.heavyCalc }}</p>
</div>
```

只要依赖数组的值未变化，Vue 在 diff 走到这个节点时会直接跳过整棵子树，不进入子节点比对。

## 4. 常见坑点

**手写渲染函数丢失编译优化**

模板编译器给静态节点打 `patchFlag`，diff 时跳过这些节点。手写 `h()` 绕过了编译器，所有节点没有 `patchFlag`，每次更新走全量 diff。性能敏感场景优先用 `.vue` 模板。

## 5. 延伸

`@vue/reactivity` 与 DOM 无关，可以在 Node.js 后端独立使用。将依赖追踪引入后端状态机——状态变化时自动触发关联计算——在流式数据处理场景中有实际应用价值。

## 6. 总结

- 响应式系统、编译器、渲染器三模块解耦，每个模块可独立使用或替换。
- `createApp()` 实例隔离解决了 Vue 2 全局插件状态污染的问题。
- 模板约束换来编译期静态分析，`patchFlag` 和 `v-memo` 是实际可用的性能优化手段。

## 7. 参考

- [Vue 3 渲染机制解析文档](https://cn.vuejs.org/guide/extras/rendering-mechanism.html)
- [How Vue Reactivity Works Under the Hood](https://www.danvega.dev/blog/vue-reactivity)
