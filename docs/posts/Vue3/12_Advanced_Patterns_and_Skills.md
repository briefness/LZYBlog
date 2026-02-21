# Vue 3 深度精通 (十二) —— 高级设计模式与实战技巧 (Advanced Skills)

在掌握基础原理与生态之后，区分"熟练工"与"架构师"的关键在于代码的设计模式与细节处理。本章汇集了 Vue 3 社区前沿的实战技巧 (Skills) 与 Pinia 的高级用法，旨在编写更优雅、更健壮的代码。

## 1. Composable 设计的艺术 (The Art of Composables)

Composable 是 Vue 3 的灵魂，但写好它并不容易。

### 1.1 参数归一化：`MaybeRefOrGetter`与`toValue`

一个优秀的 Composable 应该尽可能宽容。它应该能接受：原始值、Ref、甚至 Getter 函数。
Vue 3.3+ 引入了 `toValue` 工具，是规范化参数的最佳实践。

```typescript
import { toValue, type MaybeRefOrGetter, watchEffect } from 'vue'

// 接收 url，它可以是字符串，也可以是随时变化的 ref，甚至是 computed
function useFetch(url: MaybeRefOrGetter<string>) {
  watchEffect(() => {
    // toValue 会自动解包：
    // Ref -> value
    // Getter -> return value
    // Value -> value
    const urlValue = toValue(url)
    console.log(`Fetching ${urlValue}...`)
  })
}

// 用法灵活：
useFetch('https://api.com/user') // 静态字符串
useFetch(id) // Ref
useFetch(() => `https://api.com/user/${props.id}`) // Getter Function
```

### 1.2 副作用管理：`onScopeDispose`

如果在 Composable 中创建了全局监听器（如 `addEventListener`），必须确保在组件卸载时清理。
虽然 `onUnmounted` 可以用，但如果 Composable 是在 `effectScope` 中独立运行的（而非绑定组件），`onUnmounted` 就不会触发。

**最佳实践**：始终使用 `onScopeDispose`。

```typescript
import { onScopeDispose } from 'vue'

export function useMouse() {
  const handler = (e) => { /* ... */ }
  window.addEventListener('mousemove', handler)

  // 无论是在组件中、还是在独立 EffectScope 中，都能正确清理
  onScopeDispose(() => {
    window.removeEventListener('mousemove', handler)
  })
}
```

---

## 2. Vue 3 高级特性实战

### 2.1 泛型组件 (Generic Components)

在 Vue 3.3+ 中，可为组件定义泛型。这在编写通用的 Table、List 组件时至关重要。

```vue
<!-- GenericList.vue -->
<script setup lang="ts" generic="T extends { id: number, name: string }">
defineProps<{
  items: T[]
  selected: T
}>()
</script>

<template>
  <ul>
    <li v-for="item in items" :key="item.id">
      {{ item.name }}
    </li>
  </ul>
</template>
```

在使用该组件时，TypeScript 会自动推断 `T` 的类型，让你获得完美的类型补全。

### 2.2 `v-memo`：极致性能的模板缓存

对于超长列表（如虚拟滚动不可用的场景），`v-memo` 是最后的性能救星。它允许显式控制 DOM 更新的时机。

```html
<div v-for="item in bigList" :key="item.id">
  <!-- 只有当 item.status 或 item.selected 变化时，才会重新 Diff 和渲染这块 DOM -->
  <div v-memo="[item.status, item.selected]">
    <ComplexComponent :data="item" />
  </div>
</div>
```

如果数组中的依赖项没变，Vue 会完全跳过这块 VDOM 的创建和对比过程（类似 React 的 `useMemo`，但作用于模板）。

---

## 3. Pinia 进阶 Skills

### 3.1 Setup Stores 中的私有状态 (Private State)

在 Setup Store 中，`return` 的内容即为外部可访问内容。利用闭包特性，可轻松实现私有状态。

```typescript
export const useAuthStore = defineStore('auth', () => {
  // 公有状态
  const user = ref(null)
  
  // 私有状态：不 return 出去
  let _token = localStorage.getItem('token')

  function login(token) {
    _token = token // 内部修改
    localStorage.setItem('token', token)
    user.value = parseToken(token)
  }

  // 外部无法直接修改 _token，只能通过 action
  return { user, login }
})
```

### 3.2 组合式 Store (Composing Stores)

Store 之间是可以互相引用的。这比 Vuex 的 `modules` 更加灵活且无环形依赖风险（只要逻辑不循环）。

```typescript
import { useUserStore } from './user'

export const useCartStore = defineStore('cart', () => {
  const userStore = useUserStore() // 直接调用！

  function checkout() {
    if (!userStore.isLoggedIn) {
      throw new Error('Please login first')
    }
    // ...
  }

  return { checkout }
})
```

### 3.3 在组件外部使用 Store

常见报错：`"getActivePinia was called with no active Pinia"`。
原因为在 `createApp(App).use(pinia)` 之前尝试调用了 `useStore()`。

**场景**：在 Router 守卫或 Axios 拦截器中使用 Store。

**解决方案**：不要在顶层调用，而是在函数内部调用。

```typescript
// router.ts
import { createRouter } from 'vue-router'
// 不要在这里 const store = useAuthStore() ❌

const router = createRouter({ /* ... */ })

router.beforeEach((to) => {
  // 在函数执行时，Pinia 肯定已经挂载了
  const store = useAuthStore() // ✅
  
  if (to.meta.requiresAuth && !store.isLoggedIn) {
    return '/login'
  }
})
```

---

## 4. VueUse 深度整合

虽然不是 Vue 核心库，但 VueUse 已经是事实上的标准库。掌握这几个核心 API 能极大提升开发效率。

### 4.1 `useVModel`：封装双向绑定

在封装组件时，手动实现 `props` + `emit` 的双向绑定很繁琐。但是 `defineModel` (Vue 3.4) 已经解决了大部分问题。
如果需要更复杂的控制（比如防抖），可以使用 `useVModel`。

### 4.2 `useAsyncState`：优雅处理异步

无需再手动声明 `isLoading`、`data`、`error`。

```typescript
import { useAsyncState } from '@vueuse/core'

const { state, isReady, isLoading, error, execute } = useAsyncState(
  (args) => fetchUser(args),
  { id: 0, name: 'Guest' }, // 初始值
  {
    delay: 200, // 防抖延迟
    resetOnExecute: false // 重新请求时不重置数据（避免闪烁）
  }
)
```

## 全系列结语 (Conclusion)

### 回顾路径

从第一篇的**核心架构**，到**响应式系统**的底层原理；从**组件化**的高阶技巧，到 **Composition API** 的实战范式；再到**工程化**、**性能优化**、**源码解析**以及本篇的**高级模式**。

这套 Vue 3 深度精通系列，旨在构建一个个完整的知识体系，而非零散的 API 文档。

### 真正的精通

所谓“精通”，不仅仅是记住了多少 API，而是：

1.  **知其然**：能熟练使用框架提供的工具解决业务问题。
2.  **知其所以然**：理解框架背后的权衡（Trade-offs）与设计哲学，在遇到 bug 或性能瓶颈时能一眼看穿本质。
3.  **无招胜有招**：不拘泥于固定模式，根据场景灵活运用 `Provide/Inject`、`Composables`、`Pinia` 甚至直接操作 DOM（配合 Vapor Mode）。

前端技术日新月异，Vue 也在不断进化（如 Vapor Mode、Rust 工具链）。保持对底层原理的敬畏，保持对新技术的敏锐，方能在 Vue 的世界里游刃有余。

愿代码既有**架构师的宏大**，又有**工匠的细腻**。Coding Happy!
