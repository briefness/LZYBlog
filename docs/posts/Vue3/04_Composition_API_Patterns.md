# Vue 3 核心原理（四）—— 组合式 API：Composable 炼金术与全局状态幻觉

> **环境：** Vue 3 Composition API 全量机制，替代 Mixins 的高维抽象范式

在 Vue 2 的老年代，所有人都经历过被 `Mixins` 支配的恐怖时刻：五个混入文件往组件里一怼，你的代码里突然冒出来上百个找不到来源的拼图变量 `$data.xxx` 互相倾轧覆盖碰撞，维护人员犹如在拆盲盒地雷。

Composition API（组合式 API）这套由 React Hooks 启发而来的破茧产物。不仅仅是让你把代码全挪到 `setup` 顶层而已。它的精锐尽出，在于能将带有副作用的**状态图谱和生命周期钩子，抽离打包成可以随意拔插组合的纯函数（Composables）套件**。

---

## 1. 炼金规约：如何打造顶级的 Composable？

市面上 90% 的初学者写的 `useXXX()` 函数，充其量只能叫工具类封装。
一个血统纯正的 Composable 必须兼顾极其苛刻的响应式生命脉门衔接和全自动垃圾回收兜底机制。

### 1. 应对“量子态”的防御解包（`toValue`）
因为你不知道调用者传进来的变量，到底是写死的固定数字字面量，还是一个活蹦乱跳带有观测引线的 `ref()`。作为一个高阶容器库接驳方，你必须全盘通吃。

```javascript
// <--- 核心：使用 Vue 3.3+ 极其强悍但常被忽视的防御性解包器
import { toValue, watch } from 'vue'

export function useDynamicTitle(titleInput) {
  // 不管传进门的是 ref 还是 字符串常量，甚至是个 Getter 函数。
  // toValue 全部碾碎取出最新纯净值，并且不弄断原有牵引器！
  watch(() => toValue(titleInput), (newTitle) => {
    document.title = newTitle
  }, { immediate: true })
}
```

### 2. 擦屁股艺术：生命周期自尽
但凡在纯函数里使用了诸如 `addEventListener` 或者开启了 `setInterval` 这个滴答炸弹。
必须在其本体里挂靠就近连结同频组件的销毁钩子：

```javascript
export function useAutoRefresh() {
  const timer = setInterval(() => {}, 1000)
  // 当谁调用了这个纯函数，这段销毁逻辑就会自动挂在谁的刑架上同生共死
  onUnmounted(() => clearInterval(timer)) 
}
```

## 2. 状态倒灌：造就简易版全局 Store 幻像

除了在内部圈定组件的自身小领地。
利用 Composition API 不再依赖 `this` 和组件实体生命宿主的超脱属性。如果在 `.js` 文件的极点顶部，把一个包含有内部状态的 `reactive` 或 `ref` 晾在导出函数的主体外部空间？

**这就直接涌现出了一个微缩霸道的全应用单例存续空间：**

```javascript
/* useSharedCount.js */
import { ref } from 'vue'

// <--- 危险而迷人：脱离组件生命周期存活在外层模块全局空间里的孤立源
const globalCounter = ref(0) 

export function useSharedCount() {
  const increment = () => globalCounter.value++
  return { counter: globalCounter, increment }
}
```

任何引用并调用这个 `useSharedCount()` 的所有几十个毫不相干的边缘小组件，它们拿到手里并且修改的，将是完全指向同样物理内存的绝对唯一 `globalCounter`。这就等同于你随手就写出了一个去中心化免除重型 Pinia 安装架设的跨页面级传导通道！

## 3. 暗度陈仓：Provide / Inject 的隔山打牛

有些时候全局的跨组件传送并不能满足安全需求（比如一个多开的商品详情页卡，他们想内部跨 10 层组件共用当前鞋子的颜色选框信息，但又不想干扰并排开着的另一双袜子的详情页）。
我们需要这套**存在血缘关系覆盖范围**的 `Provide / Inject` 隐身虫洞。

**显式权衡（Trade-offs）**：
这种注入机制彻底干掉了中间 10 层组件毫无意义的 `Props` 层层串联包裹搬运体力活。
但**代价是极其隐晦的依赖耦合关联**：最底层的子组件仿佛变成了一个不接受明面参数传导只知道从虚空中吞信息的黑盒。如果哪天被人粗心拷贝移出这个有 Provide 庇护的老爹树林子，它会当场崩溃暴毙连错在哪都因为没有 `Props` 显式约束而无迹可查。

```typescript
// 利用 Symbol 加挂泛型斩断字符串重名覆盖和类型 Any 的诅咒
import type { InjectionKey, Ref } from 'vue'
export const ShoeColorKey: InjectionKey<Ref<string>> = Symbol('shoeColor')
```

## 4. 常见坑点

**在纯异步 `setTimeout` 或者网络回调归来后再去调用 `inject` 导致天塌陷**
很多开发者会在发请求回来后，再去 `inject` 提取全局信息准备组装发送二次日志。然后直接抛出了刺眼的 `Injection "Symbol(xxx)" not found`。
**原理解释**：`inject` 和 `provide` 寻找树干上文家族族谱的依赖。是强行借靠紧巴巴连着当前组件正在同步执行 `setup()` 跑线初始化时 Vue 内部切置挂载好的**临时当前实例全局游标**！一旦让出主线程跑去了异步。等几秒后回调再次苏醒试图 `inject` 时，这个游标早就跑去伺候别的兄弟组件甚至清空归零为空档了，寻根链路当场崩断失联致死无计可施。
**解法约束**：一切带有这种树状层级探寻特性的 API 调用（包括 `inject`, `onMounted` 等生命周期挂靠），必须死死卡在 `setup()` 同步执行的主线队列最开头处提前执行取值抓取保留。

## 5. 延伸思考

如果 VueUse 这样汇聚了全世界奇思妙想庞大的几百个 Composable 函数库，几乎涵盖了你对于浏览器所有原生的包裹观测包装。
你在享受这种像乐高积木一样随便 `import` 调用即拥有魔力的时候。你觉得相较于曾经直接操控裸奔的 DOM 侦听和对象，这种到处在后台静默建立几百个 `Ref` 牵涉点和侦听回调池的高维度抽象，真的不会把业务运行变成不堪重负的大象踩积木拖慢速度吗？

## 6. 总结

- 利用 `toValue` 和 `onUnmounted` 闭环编织的函数套件才是带有极强自适应性和免死金牌免疫生命泄露的高阶纯模块。
- 模块极顶外围隔离引出的孤儿 `Ref` 会演变进化为波及全局的简易黑帮单例派发中心。
- 借由 `Provide/Inject` 虫洞体系免除了深度下穿时那令人作呕恶心想吐逐层拔毛转接流水帐。

## 7. 参考

- [Vue 官方 Composables 编写指南](https://cn.vuejs.org/guide/reusability/composables.html)
- [VueUse: Collection of Essential Vue Composition Utilities](https://vueuse.org/)
