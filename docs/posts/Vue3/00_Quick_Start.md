# Vue 3 核心原理（零）—— 快速起步与 SFC 编译机制

> **环境：** Node.js 20+, Vue 3.4+, Vite 5.x

从 jQuery 或 React 转来接手 Vue 3 项目时，`ref` 的 `.value` 访问规则和 `.vue` 单文件格式是最常见的困惑点。这篇解释这两个问题背后的机制，以及 `npm create vue@latest` 之后工具链实际做了什么。

---

## 1. 启动引擎：Vite 开发服务器

```bash
npm create vue@latest
```

这个命令触发 `create-vue` 脚手架，项目默认使用 **Vite** 作为开发服务器。Vite 不在启动前预打包项目文件，而是利用浏览器原生支持的 ESM 按需编译，启动速度与项目文件数量无关。

**Trade-offs**：Vite 不支持 IE11 开箱即用（需要额外插件）。换来的是毫秒级冷启动和单模块粒度的 HMR。

> **验证**：启动 `npm run dev` 后，在 Chrome Network 面板查看 `.vue` 文件请求。响应头 `Content-Type: application/javascript`——Vite 实时把模板编译成了 JS 渲染函数返回给浏览器。

## 2. SFC 单文件组件：三段式结构

`.vue` 文件（Single-File Component）把逻辑、结构、样式放在一个文件里：

```html
<!-- 1. JS 逻辑 -->
<script setup>
  import { ref } from 'vue'
</script>

<!-- 2. UI 结构 -->
<template>
  <div class="container">
    <button>Submit</button>
  </div>
</template>

<!-- 3. 样式 -->
<style scoped>
  .container { color: red; }
</style>
```

**`<script setup>` 的编译行为**：`<script setup>` 是编译宏，不是普通脚本块。顶层声明的所有变量会被编译器提取放入 `setup()` 函数并自动 return 给模板——不需要手动写 return。

## 3. 核心 API：响应式变量与视图更新

普通 JS 变量赋值不会触发视图更新。`ref` 把基础类型包裹为响应式对象，修改时 Vue 能感知并触发重新渲染。

### `ref`

```javascript
<script setup>
import { ref } from 'vue'

const count = ref(0) // 包裹基础类型
const name = ref('Jack')

function add() {
  count.value++ // JS 中访问 ref 值需要 .value
}
</script>

<template>
  <h1>{{ name }}</h1>
  <!-- 模板中自动解包，直接写 count 而不是 count.value -->
  <button @click="add">Count is: {{ count }}</button>
</template>
```

## 4. 父子组件通信

### 父传子 (`defineProps`)

子组件用 `defineProps` 声明接收的 props。这是编译宏，不需要从 vue import。

```javascript
/* ChildBtn.vue */
<script setup>
const props = defineProps({
  title: String
})
</script>
```

### 子传父 (`defineEmits`)

子组件用 `defineEmits` 声明可以向上 emit 的事件。

```javascript
/* ChildBtn.vue */
<script setup>
const emit = defineEmits(['submit'])

function onClick() {
  emit('submit', 'Payload Data')
}
</script>
```

## 5. 常见坑点

**解构 `reactive` 对象后失去响应性**

从 `reactive` 对象或 Pinia Store 中直接解构，拿到的是普通值，失去与源对象的响应式连接：

```javascript
const { currentStatus } = myComplexReactiveState
// currentStatus 是普通字符串/数字，不再响应变化
```

正确做法是直接访问属性 `myComplexReactiveState.currentStatus`，或用 `toRefs` 转换后再解构。

## 6. 延伸

Vue 的模板约束让编译器可以在构建阶段做静态分析，对纯静态节点跳过 diff（Static Hoisting）。这是 Vue 性能优化的核心机制之一，在后续文章中详细展开。

## 7. 总结

- Vite 利用浏览器原生 ESM 按需编译，开发启动速度与项目文件数量无关。
- `<script setup>` 是编译宏，顶层变量自动放入 `setup()` 并暴露给模板。
- `ref` 包裹基础类型，JS 中用 `.value` 访问，模板中自动解包。

## 8. 参考

- [Vue 3 官方文档 - 创建一个 Vue 应用](https://cn.vuejs.org/guide/quick-start.html)
- [Vite 原理与为什么这么快](https://cn.vitejs.dev/guide/why.html)
