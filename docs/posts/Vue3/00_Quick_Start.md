# Vue 3 核心原理（零）—— 极速起步与 SFC 编译黑盒

> **环境：** Node.js 20+, Vue 3.4+, Vite 5.x

刚从 jQuery 或 React 转来接手 Vue 3 项目的开发者，常常被满屏幕的 `ref` 和漏写的 `.value` 搞得晕头转向。
为什么我们需要单独搞一个 `.vue` 后缀的单文件组件？为什么不能像 React 一样直接在纯 JS 函数里写 HTML 返回？在命令行敲下的第一行启动脚本背后，工具链到底帮我们隐瞒了多少肮脏的脏活？

---

## 1. 启动引擎：脚手架背后的 Vite 代理

前端早已脱离了在 HTML 里引入一个 `<script>` 标签就能跑的时代。
在终端执行这行号称“10分钟上手”的启动代码时：

```bash
npm create vue@latest
```

它其实不是在下载 Vue 本身，而是触发了 `create-vue` 脚手架。这个脚手架抛弃了老旧沉重的 Webpack，全面拥抱了以原生 ES Module 为基础的 **Vite** 预构建体系。

**显式权衡（Trade-offs）**：
采用 Vite 作为底层底座，**牺牲了对极老旧浏览器（IE11）的开箱即用兼容性**。但换来的是开发环境下毫秒级的服务器冷启动速度和 HMR（模块热替换）。因为 Vite 不需要在启动前把整个数十万行的项目打包揉碎成一个巨型 JS bundle，而是利用浏览器自带的 ESM 解析能力，按需请求拦截编译。

> **观测验证**：启动 `npm run dev` 后，在 Chrome 打开 Network 面板，点击任意一个 `.vue` 文件请求。你会发现服务器返回的 Content-Type 被 Vite 强行劫持修改为了 `application/javascript`，原本的 HTML 模板被实时转换成了纯 JS 的 `render` 渲染函数。

## 2. SFC 单文件组件：三段式手术刀

`.vue` 文件格式（Single-File Component，SFC）是 Vue 的标志性基因。

```html
<!-- 1. JS 逻辑 (Script Setup) -->
<script setup>
  import { ref } from 'vue'
</script>

<!-- 2. UI 结构 (Template) -->
<template>
  <div class="container">
    <button>Submit</button>
  </div>
</template>

<!-- 3. 生效样式 (Style) -->
<style scoped>
  .container { color: red; }
</style>
```

**剥开语法糖的伪装**：
`<script setup>` 表面上看着像是一个普通的脚本块，但实际上它是 Vue 编译阶段的**宏（Macro）**。
你在这里顶层声明的所有变量（比如上文导入的 `ref` 或者手写的普通常量），在最终打包时，会被 Vue 的编译器直接暴力提取，硬塞进行一个巨大的 `setup()` 闭包函数执行上下文中，并强行将它们 return 暴露给下面的 Template 去使用。

## 3. 核心 API：变量劫持与模板更新

当你在普通 JS 里写 `let age = 18; age = 19;` 时，除了内存里的数字变了，屏幕上的文字不可能自己刷新。
Vue 3 全面启用了**组合式 API（Composition API）**来解决组件间的逻辑复用黑盒。

### `ref`：为基础数据戴上监听面具

```javascript
<script setup>
import { ref } from 'vue'

const count = ref(0) // <--- 核心：用 ref 包围基础类型
const name = ref('Jack')

function add() {
  count.value++ // 在 JS 里修改必须带上 .value 拆包
}
</script>

<template>
  <h1>{{ name }}</h1>
  <!-- 模板内部调用触发自动浅层解包，严禁脱裤子放屁写 {{ count.value }} -->
  <button @click="add">Count is: {{ count }}</button> 
</template>
```

## 4. 组件互殴：父子血脉通信

在拼装页面时，上层老子如何给下层儿子传数据？下层儿子挨了揍如何通知上面？

### 父传子 (`defineProps`)
儿子张开嘴接收数据。注意这也是个编译宏，不需要额外从 vue 去 import。

```javascript
/* ChildBtn.vue */
<script setup>
const props = defineProps({
  title: String
})
</script>
```

### 子传父 (`defineEmits`)
儿子受了委屈往外广播事件。

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

**1. 脱衣解构带来的响应式彻底暴毙**
这是刚上手 Composition API 造成大面积恐慌的头号杀手。
你从 Pinia Store 或者一个外部 `reactive` 大对象里，愉快地使用 ES6 语法解构变量：
`const { currentStatus } = myComplexReactiveState;`
**原理解释**：在 JS 底层，你这就等于直接把一个普通内存里存的字面量 String 或者 Number 拷贝拔拔出来赋值给了局部常量而已！你剥夺了包在它外层的那个用来通知 Vue "我变了"的监视器代理（Proxy）。这个 `currentStatus` 从此跟原始对象彻底失去连接，变成了一具死尸。
**解法**：老老实实写 `myComplexReactiveState.currentStatus`，或者利用 `toRefs` 强行为它套上抢救心电图。

## 6. 延伸思考

Vue 选择了一条极其独特的模板（Template）编译流派，而不是像 React 一样让开发者在 JS 文件里面用 JSX 自由挥洒 HTML 标签。
这种看似限制了各种动态组装高阶组件灵活性的"模板约束"，除了让代码看起来更像传统 HTML 外，它在 Vue 3 内部隐藏了一个关于"预编译静态提升机制"（Static Hoisting）的巨型性能彩蛋。你能猜到把模板限死在固定格式里，编译器能以此在后台做多少逆天的提前运算吗？

## 7. 总结

- Vite 底座替换了沉重打包链路，利用现代浏览器的 ESM 机制实现了毫秒级代理接管。
- `<script setup>` 表面优雅，底层是粗暴的编译宏闭包包裹与隐式变量推流。
- 基础数值被修改必须加上 `.value` 去刺穿 Proxy 对象的手动隔离层操作。

## 8. 参考

- [Vue 3 官方文档 - 创建一个 Vue 应用](https://cn.vuejs.org/guide/quick-start.html)
- [Vite 原理与为什么这么快](https://cn.vitejs.dev/guide/why.html)
