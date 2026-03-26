# Vue 3 核心原理（十二）—— 高级设计模式与实战技巧

> **环境：** Vue 3.3+ 泛型系统，TypeScript 5.x，Pinia 2.x

当你能用 Vue 做出正常的功能页面，下一个门槛是：如何构建**团队级可复用**的组件和架构？

本文聚焦三个高频痛点：
- 泛型组件：如何让 `any` 消失
- Pinia 私有状态：如何对外部隐藏内部数据
- Store 在 Vue Router / Axios 拦截器中的正确调用方式

---

## 1. 泛型组件：`script setup` 里的 TypeScript 模板

### 痛点

封装一个通用列表组件时，传入的 `items` 是用户自定义的数据结构。

不用泛型：

```typescript
// ❌ Item 被强压成 any，编辑器里悬停看不到任何属性提示
defineProps<{
  items: any[]
}>()
```

用泛型后：

```vue
<!-- GenericList.vue -->
<script setup lang="ts" generic="T extends { id: number | string }">
//                                            ↑ 声明类型参数
defineProps<{
  items: T[]
  selected: T
}>()

const emit = defineEmits<{
  (e: 'select', item: T): void
}>()
</script>

<template>
  <div v-for="item in items" @click="emit('select', item)">
    {{ item.name }} <!-- 悬停可看到完整类型提示 -->
  </div>
</template>
```

父组件使用时：

```vue
<!-- 父组件 -->
<GenericList
  :items="userList"
  :selected="currentUser"
  @select="handleSelect"
/>
```

父组件传入 `userList: User[]`，泛型参数 `T` 自动推导为 `User`，模板中 `item.name` 就有类型提示了。

**Trade-offs**：
- 优势：IDE 自动完成、类型安全、refactor 时报错提示
- 代价：`<script setup generic>` 仅支持 Vue 3.3+；团队成员需熟悉 TypeScript 泛型

### 多泛型参数

```vue
<script setup lang="ts" generic="T extends Item, U extends string">
// 两个类型参数：T 是列表项类型，U 是排序字段
defineProps<{
  items: T[]
  sortKey: U
}>()
```

---

## 2. Pinia 的私有状态：Setup Store 的隐藏变量

Pinia 的 Setup Store 语法基于函数闭包。这带来一个关键特性：**未在 `return` 中暴露的变量，外部完全无法访问**。

```typescript
// useAuthStore.ts
export const useAuthStore = defineStore('auth', () => {
  // 对外暴露：模板中可直接使用
  const userInfo = ref<User | null>(null)

  // 私有变量：外部无法访问、无法通过 DevTools 修改
  let _encryptedToken = ''

  function attemptLogin(token: string) {
    _encryptedToken = encrypt(token)
    userInfo.value = parseToken(token)
  }

  function logout() {
    _encryptedToken = ''
    userInfo.value = null
  }

  // 只有 userInfo 和 logout 对外暴露
  // _encryptedToken 永远无法被外部读取或篡改
  return { userInfo, logout }
})
```

**Trade-offs**：
- 优势：闭包天然防泄露，比 `Object.freeze()` 更可靠
- 劣势：状态无法在 DevTools 中直接查看，调试时需要借助 `$state` 补丁

### 在拦截器中使用 Store

Pinia 的初始化时机决定了 Store 必须在正确的上下文调用。

**错误做法**：在模块顶层直接调用 Store

```typescript
// ❌ 在 main.ts 执行前，Pinia 还未初始化，此处调用会抛出
// Error: getActivePinia() was called with no active Pinia
import { useAuthStore } from './stores/auth'

// axios 拦截器在模块加载时就执行了，此时 Pinia 还不存在
const store = useAuthStore() // 崩溃
```

**正确做法**：在回调函数内部调用

```typescript
// axios.ts
import axios from 'axios'
import { useAuthStore } from './stores/auth'

const api = axios.create({ baseURL: '/api' })

// ✅ 在请求拦截器中，Pinia 已经初始化完毕
api.interceptors.request.use((config) => {
  const authStore = useAuthStore() // 此时 Pinia 一定已挂载
  if (authStore.userInfo) {
    config.headers.Authorization = `Bearer ${authStore.userInfo.token}`
  }
  return config
})

// ✅ Router 导航守卫同理：Pinia 在 router 安装前就已初始化
router.beforeEach((to) => {
  const authStore = useAuthStore()
  if (to.meta.requiresAuth && !authStore.userInfo) {
    return { name: 'Login' }
  }
})
```

---

## 3. 常见坑点

**1. `script setup generic` 中不能用 `extends` 约束模板中的属性访问**

```vue
<!-- ❌ TypeScript 在模板中无法识别 item 的具体属性 -->
<script setup lang="ts" generic="T">
defineProps<{ items: T[] }>()
</script>

<template>
  <div>{{ item.name }}</div> <!-- T.name 不存在，编译报错 -->
</template>
```

**解法**：在 `extends` 中明确约束结构，或在模板中使用类型守卫：

```vue
<!-- ✅ 约束 T 至少包含 id 和 name -->
<script setup lang="ts" generic="T extends { id: number, name: string }">
defineProps<{ items: T[] }>()
</script>
```

**2. Setup Store 的私有变量不可被序列化**

```typescript
// ❌ 私有变量 _token 不会出现在 Pinia DevTools 的 state 中
// 如果页面刷新，_token 丢失
export const useAuthStore = defineStore('auth', () => {
  let _token = ''
  const userInfo = ref<User | null>(null)
  // ...
})
```

**解法**：需要持久化的数据必须放在 `return` 里的 `state` 中，并配合 Pinia 插件（如 `pinia-plugin-persistedstate`）实现持久化：

```typescript
import { defineStore } from 'pinia'
import { persist } from 'pinia-plugin-persistedstate'

export const useAuthStore = defineStore('auth', () => {
  const userInfo = ref<User | null>(null)

  function attemptLogin(token: string) {
    userInfo.value = parseToken(token)
  }

  return { userInfo, attemptLogin }
}, {
  persist: {
    key: 'auth',
    storage: localStorage
  }
})
```

**3. Pinia 在 SSR（Nuxt）环境中的多实例问题**

在 Nuxt 3 中，每个请求都会创建独立的 Pinia 实例。Store 中的普通变量（非响应式 `ref`）在不同请求间会共享，导致数据串门。

```typescript
// ❌ 这是一个普通变量，所有请求共享
export const useCounterStore = defineStore('counter', () => {
  let count = 0 // 非响应式，且跨请求共享
  return { count }
})

// ✅ 正确：所有状态必须是响应式的
export const useCounterStore = defineStore('counter', () => {
  const count = ref(0) // 每个请求独立的响应式状态
  return { count }
})
```

---

## 4. 延伸思考

Vue 3 的 Composition API 让逻辑复用从 Mixin（被 Vuex 官方废弃）演进到了 Composable 函数。但这也带来了一个问题：

当一个组件依赖十几个 Composable 时，数据来源变得难以追踪。相比 Vuex 的集中式状态树，Composables 的"分散即插拔"特性在带来灵活性的同时，也提高了代码可追溯性的门槛。

实际项目中如何权衡？建议：
- 全局共享状态（如用户信息、主题）→ Pinia
- 组件内可复用逻辑（如分页、拖拽状态）→ Composable
- 业务数据聚合（如表单验证规则）→ Composable + Pinia 混用

---

## 5. 总结

- **`script setup generic`** 让组件类型安全化，IDE 悬停提示覆盖模板，提升大型团队 refactor 效率。
- **Setup Store 闭包**是 Pinia 原生支持的私有变量机制，适合存放 Token、中间计算结果等敏感数据。
- **在拦截器中使用 Store**：必须在 Pinia 初始化后的回调函数内调用，模块顶层直接调用会崩溃。
- **SSR 环境**：所有状态必须用 `ref/reactive` 声明，否则跨请求串门。

## 6. 参考

- [Vue 3 `<script setup>` 泛型官方文档](https://cn.vuejs.org/api/sfc-script-setup.html#generics)
- [Pinia 文档：Store 外部调用](https://pinia.vuejs.org/zh/core-concepts/outside-component-usage.html)
- [Pinia 持久化插件 pinia-plugin-persistedstate](https://github.com/prazdevs/pinia-plugin-persistedstate)
