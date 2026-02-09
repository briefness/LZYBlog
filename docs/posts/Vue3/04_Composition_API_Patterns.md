# Vue 3 深度精通 (四) —— Composition API 生产级实战指南

如果说 Vue 2 的 Mixins 是“黑魔法”，那么 Vue 3 的 Composition API 则是“炼金术”。它让我们可以显式地组织、抽离和复用逻辑，但如何写出高质量的 Composable 却是一门艺术。

## 什么是真正的 Composables？

一个标准的 Composable 应该是一个以 `use` 开头的函数，它接收响应式或非响应式的参数，并返回响应式的状态或方法。

### 规则与模式

1.  **参数灵活性**：接受纯值或 Ref。
    ```javascript
    import { unref, isRef } from 'vue'

    export function useTitle(title: MaybeRef<string>) {
      // 内部通过 unref 或 toValue 统一解包
      const titleRef = ref(title)
      
      watch(() => unref(title), (newTitle) => {
        document.title = newTitle
      }, { immediate: true })
    }
    ```

    Vue 3.3+ 推荐直接使用 `toValue`：

    ```javascript
    import { toValue } from 'vue'

    const val = toValue(maybeRefOrGetter)
    ```

2.  **副作用清理**：必须在 `onUnmounted` 或 `onScopeDispose` 中清理定时器、事件监听器。

3.  **返回对象还是数组？**
    VueUse 等库普遍倾向于返回对象，因为解构方便且无顺序限制。

    ```javascript
    const { x, y } = useMouse()
    ```

    如果只返回单一主要值，可以考虑直接返回 ref（如 `useTitle`）。

## 状态共享模式

Composables 不仅仅是针对组件内部的逻辑复用，它还是极简的状态管理方案。

### 全局逻辑复用

如果在文件作用域外创建响应式状态，那么所有引入该组件的实例将**共享**这个状态。这是极简版的 Store。

```javascript
/* useGlobalState.js */
const state = reactive({ count: 0 }) // 在模块顶级初始化

export function useGlobalState() {
  const increment = () => state.count++
  return { state, increment }
}
```

任何组件里 import 进来，`state.count` 都是同一个。这就是 Pinia 的基础原理。

## 依赖注入：`provide` / `inject` 的高阶用法

当需要在非常深的组件树中共享状态，又不希望使用全局 Store 时，Composition API 的 `provide/inject` 是最佳选择。

### Symbol Keys 与类型安全

为了避免命名冲突和获得良好的类型提示，一定要使用 `InjectionKey`。

```typescript
import { InjectionKey, Ref } from 'vue'

export interface UserContext {
  name: Ref<string>
  updateName: (name: string) => void
}

export const UserKey: InjectionKey<UserContext> = Symbol('User')
```

在父组件：

```javascript
provide(UserKey, { name, updateName })
```

在子组件：

```javascript
const user = inject(UserKey) 
// user 的类型会自动推断为 UserContext | undefined
```

**小贴士**：如果不提供默认值，inject 可能返回 undefined。为了更好的体验，可以封装一个 hooks：

```javascript
function useUser() {
  const context = inject(UserKey)
  if (!context) {
    throw new Error('useUser must be used within a UserProvider')
  }
  return context
}
```

## `defineMock` 与 Composable 测试

Composition API 的一大优势是极其容易测试。我们只需要调用函数，不需要挂载组件。

```javascript
// useCounter.spec.js
import { useCounter } from './useCounter'

test('should increment', () => {
  const { count, inc } = useCounter()
  expect(count.value).toBe(0)
  inc()
  expect(count.value).toBe(1)
})
```

如果涉及生命周期（如 `onMounted`），可以使用 `withSetup` 辅助函数（Vue Test Utils 提供的测试模式）或直接手动 mock 相关的生命周期钩子。

## 结语

Composition API 是 Vue 3 的精髓。掌握了它，意味着你掌握了以函数式编程思想构建 UI 的能力。下一篇，我们将进入大型应用的必备技能——**Vue Router 4 的深度路由管理**。
