# Vue 3 极速入门 (零基础篇) —— 10分钟上手

本篇针对从未接触过 Vue 或刚从 jQuery/React 转型的开发者。旨在跳过复杂概念，提供 Vue 3 快速启动与应用开发指南。

## 1. 环境准备与启动

环境配置只需一行命令。在终端（Terminal）执行：

```bash
npm create vue@latest
```

*   项目名：`vue-demo`
*   其他选项：直接回车（选 No），或按需开启 TypeScript。

```bash
cd vue-demo
npm install
npm run dev
```

浏览器访问显示的地址（通常是 `http://localhost:5173`），Vue 应用随即启动。

## 2. Vue 组件结构 (SFC)

Vue 使用 `.vue` 文件，即**单文件组件 (Single File Component)**。它由三部分组成：

```html
<!-- 1. JS 逻辑 (Script Setup) -->
<script setup>
  import { ref } from 'vue'
  // 定义状态和函数
</script>

<!-- 2. HTML 模板 (Template) -->
<template>
  <div class="container">
    <!-- UI 结构 -->
  </div>
</template>

<!-- 3. CSS 样式 (Style) -->
<style scoped>
  /* scoped 表示样式只在这个组件内生效 */
  .container { color: red; }
</style>
```

## 3. 核心 API：定义数据

在 Vue 3 的 `<script setup>` 中，使用 **组合式 API (Composition API)**。

### `ref`：定义响应式变量

页面上需要变化的数据，需使用 `ref` 包裹。

```javascript
<script setup>
import { ref } from 'vue'

const count = ref(0) // 定义数字，初始值 0
const name = ref('Jack') // 定义字符串

function add() {
  count.value++ // 注意：在 script 中修改值需加 .value
}
</script>

<template>
  <h1>{{ name }}</h1>
  <button @click="add">Count is: {{ count }}</button> <!-- 模板中自动解包，无需 .value -->
</template>
```

## 4. 模板语法：HTML 编写规则

### 显示内容 (`{{ }}`)

```html
<p>Message: {{ msg }}</p>
```

### 绑定属性 (`v-bind` 或 `:`)

将变量绑定到 HTML 标签属性（如 `src`, `class`, `disabled`）：

```html
<!-- 完整写法 -->
<img v-bind:src="imageUrl" />

<!-- 常用缩写 -->
<img :src="imageUrl" />
<div :class="{ active: isActive }"></div>
```

### 绑定事件 (`v-on` 或 `@`)

```html
<!-- 完整写法 -->
<button v-on:click="doSomething">Click me</button>

<!-- 常用缩写 -->
<button @click="doSomething">Click me</button>
```

### 条件渲染 (`v-if` / `v-else`)

```html
<div v-if="isValid">若为 True 显示此内容</div>
<div v-else>否则显示此内容</div>
```

### 列表渲染 (`v-for`)

```html
<ul>
  <li v-for="item in list" :key="item.id">
    {{ item.name }}
  </li>
</ul>
```

### 双向绑定 (`v-model`)

常用于表单，实现 JS 变量与输入框内容实时同步。

```html
<input v-model="text" />
<p>输入内容: {{ text }}</p>
```

## 5. 生命周期：页面加载逻辑

组件挂载完成后（页面显示后）请求后端接口示例：

```javascript
<script setup>
import { onMounted, ref } from 'vue'

const data = ref(null)

onMounted(async () => {
  console.log('页面加载完毕！')
  // const res = await fetch('/api/data')
  // data.value = await res.json()
})
</script>
```

## 6. 响应式进阶：处理复杂逻辑

### 计算属性 (`computed`)

当需要根据现有数据“运算”出新数据时，建议使用 `computed`。其具备缓存特性，性能更优。

```javascript
/* 购物车逻辑 */
const price = ref(100)
const count = ref(2)

// total 自动跟随 price 或 count 变化
/* 需引入 import { computed } from 'vue' */
const total = computed(() => price.value * count.value) 
```

### 监听器 (`watch`)

当需要在数据变化时**执行副作用**（如打印日志、发请求），使用 `watch`。

```javascript
/* 需引入 import { watch } from 'vue' */
const question = ref('')

// question 变化时自动执行
watch(question, (newVal) => {
  console.log('搜索内容变更:', newVal)
  // fetchAnswer(newVal)
})
```

## 7. 跨组件数据共享：Pinia

当组件层级较深或兄弟组件需通信时，props 传参较为繁琐。此时推荐使用 Pinia。

### 1. 定义 Store

```javascript
/* stores/counter.js */
import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useCounterStore = defineStore('counter', () => {
  const count = ref(0)
  function increment() {
    count.value++
  }
  return { count, increment }
})
```

### 2. 在组件中使用

```javascript
/* AnyComponent.vue */
import { useCounterStore } from '@/stores/counter'

const counter = useCounterStore()

// 直接读写，均为响应式
console.log(counter.count)
counter.increment()
```

## 8. 父子组件：页面拼装

### 引入组件

直接 import 即可在 template 中使用。

```javascript
/* App.vue */
<script setup>
import MyButton from './MyButton.vue'
</script>

<template>
  <MyButton title="提交" @submit="handleSubmit" />
</template>
```

### 父传子 (`defineProps`)

子组件接收数据。

```javascript
/* MyButton.vue */
<script setup>
const props = defineProps({
  title: String
})
</script>

<template>
  <button>{{ title }}</button>
</template>
```

### 子传父 (`defineEmits`)

子组件通知父组件。

```javascript
/* MyButton.vue */
<script setup>
const emit = defineEmits(['submit'])

function onClick() {
  emit('submit', 'Payload Data')
}
</script>
```

## 9. 结语

至此，已覆盖 Vue 3 90% 的常用语法。

*   **深入理解 `ref` 与 `.value`：** 请参考 [第 2 篇：响应式原理](./02_Reactivity_Essentials.md)。
*   **优雅的组件通信方案：** 请参考 [第 3 篇：组件化技巧](./03_Component_Deep_Dive.md)。
*   **Pinia 高级用法：** 请参考 [第 6 篇：Pinia 状态管理](./06_Pinia_State_Management.md)。
*   **Template 到 DOM 的底层转换：** 请参考 [第 10 篇：源码解析](./10_Internal_Mechanics.md)。

准备开启深度精通之旅。
