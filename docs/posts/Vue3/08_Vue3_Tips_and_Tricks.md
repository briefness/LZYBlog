# Vue 3 深度精通 (八) —— 鲜为人知的顶级技巧 (Skill & Hacks)

有些 API 虽然低调，但在特定场景下有着化腐朽为神奇的力量。这一章，我们将挖掘这些鲜为人知的宝藏。

## `script setup` 的语法糖魔法

### `defineModel` (Vue 3.4+)

终于，我们可以像定义 props 一样简单地定义双向绑定的值了。

**以前：**
```javascript
const props = defineProps(['modelValue'])
const emit = defineEmits(['update:modelValue'])
function update(val) { emit('update:modelValue', val) }
```

**现在：**
```javascript
const model = defineModel()
model.value = 'New Value' // 自动 emit update:modelValue
```

如果有多重 v-model：`const title = defineModel('title')`。

### `defineOptions` (Vue 3.3+)

在 `<script setup>` 中，如果你想声明组件名或禁用 Attributes 透传，以前可能需要再写一个 `<script>` 块。现在不需要了。

```javascript
/* MyComponent.vue */
<script setup>
defineOptions({
  name: 'MyComponent',
  inheritAttrs: false // 禁止自动透传
})
</script>
```

### `defineSlots`

仅用于类型声明，让父组件在使用 slot 时获得极致的类型提示。

```typescript
const slots = defineSlots<{
  default(props: { msg: string }): any
  item(props: { id: number }): any
}>()
```

## 内置组件的隐藏用法

### `<Teleport>`：任意传送门

不仅可以把 Modal 传送到 `body`，还可以传送到任何 DOM 节点（只要该节点已存在）。

```html
<Teleport to="#modal-container" :disabled="isMobile">
  <!-- 当 isMobile 为 true 时，不传送，留在原地 -->
  <MyModal />
</Teleport>
```

### `<Suspense>`：异步的优雅回落

虽然是实验性特性，但在处理异步组件加载时真的不可替代。配合 `onErrorCaptured` 可以构建极其健壮的错误边界。

```javascript
<onErrorCaptured>
  <Suspense>
    <AsyncComponent /> <!-- 内部 await -->
    <template #fallback>Loading...</template>
  </Suspense>
  <template #error>Load Failed</template>
</onErrorCaptured>
```

## 自定义指令的高阶用法

除了简单的 `v-focus`，指令还可以通过参数传递函数。

### v-click-outside

一个经典的指令，点击元素外部触发回调。

```javascript
/* directives/click-outside.js */
export default {
  mounted(el, binding) {
    el._clickOutsideHandler = (event) => {
      if (!(el === event.target || el.contains(event.target))) {
        binding.value(event) // 执行回调
      }
    }
    document.addEventListener('click', el._clickOutsideHandler)
  },
  unmounted(el) {
    document.removeEventListener('click', el._clickOutsideHandler)
  }
}
```

```html
<div v-click-outside="closeMenu">Menu</div>
```

## Render Function & JSX

有些时候，模板语法真的不够灵活（特别是递归组件或动态生成大量相同结构的组件）。这时候，直接写渲染函数（或者 JSX）是更好的选择。

```javascript
import { h } from 'vue'

const MyComponent = (props, { slots }) => {
  return h('div', props.attrs, [
    h('h1', 'Hello World'),
    slots.default && slots.default()
  ])
}
```

在 Vite 插件 `vite-plugin-vue-jsx` 的支持下，我们可以直接享用 React 式的开发体验，但保留 Vue 的响应式系统。

## 结语
这些技巧能让你的 Vue 代码更简洁、更强大。下一篇，我们将进入最重要的环节——**性能调优**，看看如何在海量数据面前保持应用丝滑流畅。
