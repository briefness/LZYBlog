# Vue 3 深度精通 (六) —— Pinia：重塑状态管理

Pinia 不是 Vuex 5，它是 Vue 3 时代的最佳状态管理方案。如果 Vuex 让你感到繁重，Pinia 会让你重新爱上全局状态。

## 为什么选择 Pinia？

Pinia 的真正优势在于：
1.  **极简 API**：没有 mutations，只有 state, getters, actions。
2.  **类型推断**：无论是 payload 还是 store 结构，TS 支持几乎是完美的。
3.  **模块化**：每个 Store 都是独立的，按需加载，无需像 Vuex 那样嵌套 modules。
4.  **Devtools 支持**：可以直接在 Vue Devtools 中调试 Store，甚至可以时间旅行（Time Travel）。

## Setup Store 模式：Composition API 的完美复刻

虽然 Pinia 支持 Options API 写法（类似 Vuex），但我强烈推荐使用 **Setup Store**。

```typescript
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useUserStore = defineStore('user', () => {
  const name = ref('Eduardo')
  const isAdmin = ref(true)
  
  const doubleName = computed(() => name.value.repeat(2))
  
  function changeName(newName: string) {
    name.value = newName
  }

  function login(user: string, password: string) {
    // 异步 actions 就像普通函数一样写 async/await
    const userData = await api.login(user, password)
    this.userData = userData
    this.router.push('/')
  }

  return { name, isAdmin, doubleName, changeName, login }
})
```

**为什么 Setup Store 更好？**
它允许你在 Store 内部使用其他的 Composable！例如 `useLocalStorage`，或者其他的 Store。这是 Options API 无法做到的。

## Store 的重置与插件机制

### 重置状态：`$reset` 的替代

setup store 默认不支持 `$reset()`。我们需要通过插件或者手动实现。

最简单的手动重置：

```typescript
import { useUserStore } from './user'
const store = useUserStore()

store.$patch({ name: 'Eduardo', isAdmin: true }) // 批量修改
```

或者使用插件：

```typescript
// main.ts
import { createPinia } from 'pinia'

const pinia = createPinia()

pinia.use(({ store }) => {
  const initialState = JSON.parse(JSON.stringify(store.$state))
  store.$reset = () => {
    store.$patch(initialState)
  }
})
```

### 数据持久化：`pinia-plugin-persistedstate`

无需手写 `localStorage.setItem`。

1.  安装 `npm i pinia-plugin-persistedstate`
2.  配置：

```typescript
import { createPinia } from 'pinia'
import piniaPluginPersistedstate from 'pinia-plugin-persistedstate'

const pinia = createPinia()
pinia.use(piniaPluginPersistedstate)
```

3.  在 Store 中启用：

```typescript
defineStore('user', () => {
  // ...
}, {
  persist: true
})
```

## 测试 Store

Pinia 的测试非常简单，因为它就是普通的 JS 对象。但为了更严谨的单元测试，我们需要 setActivePinia。

```typescript
import { setActivePinia, createPinia } from 'pinia'
import { useCounterStore } from './counter'

describe('Counter Store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  it('increments', () => {
    const counter = useCounterStore()
    expect(counter.count).toBe(0)
    counter.increment()
    expect(counter.count).toBe(1)
  })
})
```

## 结语

Pinia 将状态管理的复杂度降到了最低。有了它，我们几乎不再需要通过 props 层层传递数据。下一篇，我们将探讨 Vue 3 的工程化基石——**Vite 与 TypeScript 的高阶配置**。
