# Vue 3 深度精通 (二) —— 响应式系统的进阶精通

响应式系统是 Vue 3 的灵魂。我们知道 `ref` 是为了统一基本类型（primitive）和对象（reactive）在逻辑层的访问方式，但你是否知道 `shallowRef`、`markRaw` 等高阶 API 呢？

## `reactive`：基于 Proxy 的魔法

`reactive` 创建一个代理对象（Proxy），拦截对对象属性的所有读写操作。

### 为什么数组索引修改可以被监听到？

在 Vue 2 中，由于 `Object.defineProperty` 的限制，无法监听数组索引和长度的变化，导致我们只能用 `$set`。
Vue 3 的 `reactive` 是通过 Proxy 拦截数组的所有操作（包括 `.push`, `.splice` 等，因为这些方法是隐式访问了 `length` 和索引的）。

```javascript
/* 内部实现概览 */
function createReactive(target) {
  return new Proxy(target, {
    get(target, key, receiver) {
      track(target, key) // 收集副作用
      return Reflect.get(target, key, receiver)
    },
    set(target, key, value, receiver) {
      const res = Reflect.set(target, key, value, receiver)
      trigger(target, key) // 触发副作用
      return res
    }
  })
}
```

## 响应性丢失的陷阱与解法

### `toRefs`：解构的救星

当你从 `props` 或者 `reactive` 对象中解构数据时，响应性会丢失。

```javascript
const state = reactive({ count: 0 })
const { count } = state // count 变成了 0，不是 ref，与 state 断开连接
```

**解法**：使用 `toRefs` 将 reactive 对象的所有属性转换为 ref。

```javascript
import { toRefs } from 'vue'

const stateRefs = toRefs(state)
const { count } = stateRefs // count 是一个 ref(0)，修改它会同步修改 state.count
```

**注意**：`toRef` 用于取出单个属性，它比 `toRefs` 更轻量。

## 高阶响应式 API

### `shallowRef` & `triggerRef`：性能优化利器

如果你的状态非常庞大且不需要深度响应式（例如一个巨大的列表，你只会在列表整体替换时才更新），请使用 `shallowRef`。

```javascript
import { shallowRef, triggerRef } from 'vue'

const hugeList = shallowRef([])

// 这样会触发更新（替换整个 value）
hugeList.value = await fetchHugeData()

// 这样不会触发更新（修改 value 内部属性）
hugeList.value[0].name = 'Modified'

// 如果一定要手动触发更新：
triggerRef(hugeList)
```

### `markRaw`：告诉 Vue 不要碰我

对于有些第三方库实例（如 ECharts 实例、Three.js 场景对象），它们本身非常复杂且不需要变成响应式。如果你把它们放在 `data` 或 `ref` 中，Vue 会尝试递归代理它们，造成巨大的性能开销甚至溢出。

```javascript
import { markRaw } from 'vue'
import * as echarts from 'echarts' // 从 echarts v5+ 引入

const chart = markRaw(echarts.init(document.getElementById('chart')))
// 把它存到 ref 里也没事，Vue 会跳过对 chart 的代理
const chartRef = ref(chart)
```

### `customRef`：实现防抖响应式

`customRef` 允许你显式控制依赖追踪（track）和触发（trigger）的时机。这是一个经典的防抖 Ref 实现：

```javascript
import { customRef } from 'vue'

function useDebouncedRef(value, delay = 200) {
  let timeout
  return customRef((track, trigger) => {
    return {
      get() {
        track() // 告诉 Vue 追踪这个 ref
        return value
      },
      set(newValue) {
        clearTimeout(timeout)
        timeout = setTimeout(() => {
          value = newValue
          trigger() // 等一下再告诉 Vue 更新
        }, delay)
      }
    }
  })
}

const text = useDebouncedRef('hello', 500)
```

在模板中绑定 `<input v-model="text">`，用户的输入会立即反映在输入框中（因为这是原生 input 的行为），但组件的更新（比如依赖 text 的 computed）会被防抖。

## 响应式调试

Vue 3 提供了 `onRenderTracked` 和 `onRenderTriggered` 两个调试钩子，可以告诉你到底是哪个变量触发了组件更新。

```javascript
import { onRenderTriggered } from 'vue'

onRenderTriggered((e) => {
  debugger
  console.log('Who triggered update?', e.key, e.target)
})
```

利用这些工具，我们可以精准定位多余的渲染。

## 下一章预告

掌握了响应式的底层逻辑，接下来我们要进入 **组件核心**。我们将深入探讨透传 Attributes、递归组件、以及如何利用这些高阶特性构建复杂的 UI 库。
