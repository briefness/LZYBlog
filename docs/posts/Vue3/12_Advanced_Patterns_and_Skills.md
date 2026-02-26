# Vue 3 核心原理（十二）—— 终极禁术：泛型组件与架构级 Composable 炼丹

> **环境：** Vue 3.3+ 泛型强化系统，TS 深层次融合，Pinia 黑箱架构

当你可以看着文档跌跌撞撞搓出一个能点能滚动的电商页面。你觉得自己懂 Vue 可以出师领头了。
但如果让你去维护封装一个供三千前端团队调用的极其复杂的联动型带排序超巨型表格，或者是要求你在离开界面跳转在半空路由悬停拦截时去操控那些原本依附于组件生死的生命线变量钩子。如果你不具备操控 TypeScript 泛型深切组件、以及让函数从闭包地界逃离的手段。你的架构终极依然只配做成一坨到处标黑着 `any` 和满天飞面条调用的补丁浆糊屎山。

---

## 1. 泛型下放：构建防核弹级的强类型通用插槽

在过去封装类似于 Dropdown 或者表格列表这类的通用 UI 模板组件时，最让人极其头皮吐血的就在于 `Props` 数组中传递那个未知的列表 `list` 究竟是个怎样的形体。

没有泛型，你只能可悲地下挂弱鸡类型 `type: Array as PropType<any[]>` 苟且偷生装聋作哑，并在回调点击选中的方法里，默默忍受被当场丢失抹除掉所有变量名字典提醒字段提示服务的待遇。

### `<script setup generic>`：宣告强磁暴防护场降临

在 Vue 3.3 中，宏指令加入了一把能封锁未知领域的神剑：让整个 `.vue` 文件彻底化身成为一个带着缺口变量参数孔的 TypeScript 模板！

```vue
<!-- GenericList.vue -->
<!-- <--- 核心禁术：在此抛出铁桶般不可侵犯的神圣通配泛化限定词 -->
<!-- 它不仅框死了 T 必须是一个包含 id 的实体，这股力量甚至能穿透蔓延全境模板里的 {{ item.xxx }} -->
<script setup lang="ts" generic="T extends { id: number, name: string }">
defineProps<{
  items: T[] // 我不指望知道里面具体的其他附带结构，但你得全交给我连着带状保护
  selected: T 
}>()

const emit = defineEmits<{
  (e: 'select', item: T): void // 点击回抛，外面的父组件接手绝不含糊丢失一寸提示
}>()
</script>

<template>
  <div v-for="item in items">
    {{ item.name }} <!-- 在编辑器里悬停，绝不再是阴冷的 any！ -->
  </div>
</template>
```

当父层级在导入调用时写入 `<GenericList :items="complexUserList">` 时，那个犹如变形金刚一样的 `T` 会顺着传进来的对象全盘吸收固化变身，直接撑满起一整块铜墙铁壁一样的智能语法约束护罩。

## 2. 闭包大墓地：Pinia 里的不可见私有内战

很多没弄明白 Setup Store 是脱胎于单文件闭包理念框架的新手。还保留着 Vuex 时代强迫症写出一长篇 `state`, `getters`, `actions` 三块大平层铺满在最外边的蠢相。

Setup Store 不仅仅是用来暴露给大家调用，它更能成为一个极度排外、深渊锁死的绝对防外接防毒内卷密室。

**不放入 `return` 的那面叹息之墙：私有特种武器库存放处！**

```typescript
export const useAuthStore = defineStore('auth', () => {
  const userInfo = ref(null) // 交给界面的可怜暴露傀儡
  
  // <--- 核心黑墙：没有任何 return 能摸到这一段。
  // 它作为一个带着极度隐私敏感性的毒药源，
  // 只能存活并在整个系统运转时游荡在这个沙盒工厂函数幽魂深海闭包栈中。
  let _jwtEncryptedToken = localStorage.getItem('__secretKey')

  function attemptLogin(token) {
    _jwtEncryptedToken = token // 在这里秘密交易
    localStorage.setItem('__secretKey', token)
    userInfo.value = decryptMask(token)
  }

  // 想来读或者强制篡改覆盖令牌？不好意思，接口这并没有给大门留下钥匙孔！
  return { userInfo, attemptLogin } 
})
```

利用不导出给面子的残缺引配设计，你实现了极其牢靠并拒绝通过大魔道插件工具抓取查检渗透的局部不可见污染层强数据保驾防改护心镜结构！

## 3. 常见坑点

**在纯生命外场外使用无名 Store 引发的惨烈空指针崩盘**
当你把一些通用的用户校验动作从页面上剥离开，单独挂靠丢去给 Vue Router 或者直接交接给 Axios 的全局拦截断口里。当你在文件顶端 `const store = useUserStore()` 顺手抛出初始化预备就绪。
你马上在浏览框里领略到底层报错 `getActivePinia was called with no active Pinia` 的鲜红判决无死角糊脸大字死亡连击击打。
**原理解释**：Store 系统必须仰仗挂接在初始化后、那株以 `app.use(pinia)` 组建大盘成型的实体上。如果你把这段请求塞在了其他游标 `.js` 文件的导入顶格执行域：当 JS 解析机顺藤摸瓜在这扫码运行抓捕创建的时候它像一个死胎弃儿根本还没轮得着在 `main.ts` 里发育成形挂进全息系统网络里去接壤报备入籍户口！此时在半空向源头伸手直接必定引来万丈深空无尽虚空失重抛接断空空指针大错误。
**解法必循**：不能在外部模块直接粗鲁地用函数执行宣告拦截夺取，所有调集使用必须放置在 **拦截动作正真实发启动被激活的那个箭头函数作用闭环包裹体之中（例如 `router.beforeEach(() => { const store = xxx })`）**，在这个时期那棵名叫 Pinia 的生命树老爹肯定早就存活并繁茂招展静候传调指令下达执行差遣。

## 4. 延伸思考

当所有逻辑都被抽出成为高度抽象可以脱离任何 HTML 和组件绑架牵制的纯状态勾连闭环大网 `useComposables` 和各种多端平行的 Pinia 树结构。代码虽然得到了近乎恐怖的灵活分段接驳打散拼接极效。但如果面对一个接手没有文档项目的人，看着组件里面从三十多条管道抽引拼接混杂出来的状态大杂烩集合网。他们还会像老式从上扒下条分块析一目了然顺着寻找定位来得更加清晰可预见追踪嘛？为了工程组件极限的液态分散力，我们在交替换代的可追溯可视度上做出了哪般等阶重量置换筹码付出考量抉择？这极度考验架构规范化引导之手。

## 5. 总结

- 斩断 `Any` 触角的 `script generic` 为不可理喻千变莫幻极深套娃列表提供了绝不能失联的强雷达护甲罩底片。
- 借助没有暴露漏洞破绽的不回吐暗坑隐藏闭包链引法，可死防外部探寻针直接打碎数据核心修改防范防线。
- 对于所有在无组件包裹真真空裸露环境依赖，延迟其抓拿手探入时期使其落位确立存活是唯一的通融执行接道准则。

## 6. 参考

- [Vue 组件内建泛型声明运用大系官方定档文献](https://cn.vuejs.org/api/sfc-script-setup.html#generics)
- [绕过局限：Pinia 组件外围环境呼出正确起跳姿势指南](https://pinia.vuejs.org/zh/core-concepts/outside-component-usage.html)
