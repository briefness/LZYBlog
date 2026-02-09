# Vue 3 深度精通 (一) —— 核心架构与设计哲学

仅仅掌握 `createApp` 和 `v-if` 是不够的。要成为 Vue 3 专家，需深入理解其背后的设计哲学和运行机制。

## 全系列目录

1.  **核心架构与设计哲学**
2.  **响应式系统的进阶精通**
3.  **组件化高阶技巧**
4.  **Composition API 生产级实战指南**
5.  **Vue Router 4 的路由哲学**
6.  **Pinia：重塑状态管理**
7.  **工程化基石与最佳实践**
8.  **鲜为人知的顶级技巧 (Tips & Tricks)**
9.  **极致性能优化终极指南**
10. **源码级解析与核心原理**
11. **全栈生态与未来展望**
12. **高级设计模式与实战技巧 (Advanced Skills)**

---

## 架构概览：三位一体

Vue 3 的核心由三个主要部分组成，它们既协同工作，又能独立使用：

1.  **响应式系统 (Reactivity System)**：独立于 UI 的状态管理库。甚至可以在 Node.js 中单独使用 `@vue/reactivity`。
2.  **编译器 (Compiler)**：将模板字符串编译为 JavaScript 渲染函数。它包含了解析 (Parser)、转换 (Transform) 和代码生成 (Codegen) 三个阶段。
3.  **运行时 (Runtime)**：即渲染器 (Renderer)。它负责创建虚拟 DOM (VNode)、挂载 DOM、更新 DOM。

### 为什么是从 `new Vue` 到 `createApp`？

在 Vue 2 中，全局配置（如 `Vue.use`、`Vue.mixin`）直接挂载在 `Vue` 构造函数上。这意味着若在同一个页面启动两个 Vue 应用，它们会共享这些全局配置，造成污染。

Vue 3 引入了 `createApp`，返回一个应用实例 `app`。所有的全局配置都限制在这个实例上：

```javascript
import { createApp } from 'vue'
import App from './App.vue'

const app = createApp(App)
const otherApp = createApp(App)

app.use(Router) // 仅影响 app
otherApp.mount('#other-container')
```

## 深入渲染机制

### 虚拟 DOM (VNode) 的本质

Vue 组件的模板最终都会被编译成渲染函数 `render()`。渲染函数返回的不是真实的 DOM，而是 VNode（Virtual Node）。

```javascript
import { h } from 'vue'

const vnode = h('div', { id: 'foo' }, 'Hello')
/*
vnode 大致结构:
{
  type: 'div',
  props: { id: 'foo' },
  children: 'Hello',
  el: null, // 真实 DOM 的引用，挂载后才有值
  shapeFlag: 1, // 这是一个 div 元素
  patchFlag: 0 // 补丁标记，用于优化 Update
}
*/
```

### 渲染器 (Renderer) 不仅仅是 DOM

Vue 3 的运行时核心是 `@vue/runtime-core`，它不包含任何平台特定的代码（如 `document.createElement`）。
这意味着可以编写自定义渲染器，将 Vue 渲染到 Canvas、WebGL 甚至终端上。

`createApp` 其实是 `createRenderer` 的一个特例实现。

```javascript
import { createRenderer } from '@vue/runtime-core'

const { render, createApp } = createRenderer({
  createElement(tag) { /* ... */ },
  patchProp(el, key, prevValue, nextValue) { /* ... */ },
  insert(el, parent) { /* ... */ }
})
```

## 模板编译与指令进阶

### `v-memo`：性能优化的隐藏宝石

Vue 3.2 引入的 `v-memo` 是手动优化性能的利器。它接收一个依赖数组，只有当数组中的值发生变化时，才会重新渲染该元素及其子树。

```html
<div v-for="item in list" :key="item.id" v-memo="[item.id === selectedId]">
  <p>ID: {{ item.id }}</p>
  <p>Status: {{ item.status }}</p>
</div>
```

在这个例子中，如果 `item.id === selectedId` 的结果没有变（比如从 `false` 变 `false`），且 `item` 的其他属性变了，Vue 也会跳过更新。这对于长列表优化非常有用。

### 为什么 `script setup` 不仅仅是语法糖？

可能认为 `<script setup>` 只是减少了 `export default {}` 的板代码。但它还有更深层的优势：

1.  **更好的运行时性能**：模板会被编译成同一作用域的渲染函数，没有任何中间代理。这意味着模板中访问变量时，是直接访问的局部变量，而不是 `this.xxx`（Proxy）。
2.  **更好的类型推断**：对 TypeScript 及其友好，IDE 可以利用 CSS 作用域和 Props 类型进行完美的推断。

## 总结与思考

Vue 3 不仅仅是一个框架的升级，它是对现代前端工程化的回应。从模块化的架构到基于 Proxy 的响应式，每一处设计都是为了更好的性能和扩展性。

下一章将深入 **响应式系统** 的深水区，探讨 `shallowRef`、`customRef` 等高阶 API 的应用场景。
