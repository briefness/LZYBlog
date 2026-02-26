# Vue 3 核心原理（五）—— Vue Router 4：动态路由劫持与微加载防抖

> **环境：** Vue Router Version 4.x+, 权限认证体系对接闭环

很多人觉得前端单页应用的路由也就是写一个 `import` 再套个 `path: '/admin'` 映射表。
直到你接手了一套有 15 个层级权限、甚至需要在点击按钮进去前拉取数百项极其复杂的物料包以至于要在转圈黑屏里挂住三秒的极地地狱级中后台应用。没有深彻掌握拦路守卫（Navigation Guards）与挂载微时刻管控能力的你，只会看着疯狂狂弹重复挂载的烂摊子页面抓狂倒地。

---

## 1. 拦截换柱：`addRoute` 与权限的角逐厮杀战

一个真正靠谱的后端主导权限控制系统中，前台前端在初始启动时所拿到的包裹里，除了一条通向死亡登录大门的 `/login` 路由映射表之外，可以说是家徒四壁不剩一瓦的。

所有高达几十个内部神秘功能的 URL，都必须等到携带通行证 Token 获取到对应角色等级后，在代码内存运行时里被粗暴强硬动态嫁接着压入路引指南中。

### 运行时路标灌注的致命裂隙死循环

你拿到了权限表，调用了 `router.addRoute()` 把新页面接驳了进去。这时候如果啥都不干直给，系统大概率会抛出一个血淋淋的白屏 `Not Found`。

```javascript
/* src/permission.js 全局门神 */
router.beforeEach(async (to, from, next) => {
  if (hasToken && !hasRolesFetched) {
    try {
      // 1. 去老巢获取拥有进入哪些密室权限列表
      const accessRoutes = await store.dispatch('fetchRoles')
      
      // 2. 依次按头强行压入中枢神经脉络
      accessRoutes.forEach(route => router.addRoute(route))

      // <--- 坑点核心排雷：如果这里你写普通的 next()，极高概率白屏进异次元！
      // 解法：因为 addRoute 的后台压入组装是非常异步繁杂的宏微任务交织耗时操作，
      // 你放行时 Vue 可能根本没把刚修好的路纳入巡检雷达探测图谱！
      // 必须带 replace 原地爆破重启式让重定向触发新一遍全流程扫描打断！
      next({ ...to, replace: true }) 
      
    } catch (err) {
      next(`/login`)
    }
  } else {
    next() // 畅通无阻的正常常规放行
  }
})
```

## 2. 拦截纵深：守卫的执行微距时差学

大部分初阶开发者一辈子只用过 `beforeEach` 用来卡死阻断看门狗鉴定检查。事实上由于整个页面解析拆散装配到下载异地 JS 碎片块。Vue Router 提供了一套极度繁枝茂叶的回调深水探针。

### `beforeResolve`：最后的安全数据输血点

假设你要进一个重型报表页面 `Report.vue`。如果你选择在其自身内部的 `onMounted` 里才发起抓取 200MB 的后台报表数据指令。用户会先目睹网页咔擦干裂撕扯跳转成一块巨大的带有骨架屏的白板死肉，然后才去苦等出菊花图案转圈。

如果你想做到“不拿到数据老子今天绝不仅翻转放行哪怕一步切页”的窒息压迫感平滑无缝切换。你必须拦在所有异步页签被拼装完成准备抛头露面的最后一扇大门前哨卡：`beforeResolve`。

```javascript
router.beforeResolve(async to => {
  // 如果当前路牌被刻了需要提前垫底吸血补魔
  if (to.meta.requiresDataPrefetch) {
    try {
      await fetchHugeDashboardDataFor(to.params.id) // 阻断式全吞噬等候卡位
    } catch (error) {
      // 一旦报错拉跨拉不上数据卡断崩毁，直接遣返回退拒绝翻页切换，页面纹丝未动呆在原地
      return false 
    }
  }
})
```

> **观测验证**：使用这个 Hook 执行网络查询时你打开浏览器抓包页面网络层录屏。你会发现原本点击立刻闪现白色的 URL 变向没有发生。原本停驻的页卡鼠标按下去后出现了极其短暂的滞留呆板暂停呆滞期（此期正在发起并接收你注入等待的 Request 堵塞请求处理回声）。完毕后，一帧丝滑切进目标成品无需二次加载闪烁填空。

## 3. 过渡动效：组件骨架留存的生死交替跳动

利用 Vue 3 的 `<Transition>` 可以把干巴巴的闪现切卡变成史诗级大作翻页滑润表现。但这其中包含一个常年排在 issue 首页置顶的严重视觉灾难：布局坍塌抖动。

```html
<router-view v-slot="{ Component, route }">
  <!-- <--- 核心解药：绝命阻拦模式 mode="out-in" -->
  <transition name="fade" mode="out-in">
    <component :is="Component" :key="route.path" />
  </transition>
</router-view>
```

**显式权衡（Trade-offs）**：
不加 `mode="out-in"` 会有什么惨剧？在切换交错的中间那零点几秒的物理动画过渡窗帧内空间，**老页面那个组件 DOM 其实还没被杀掉抽走拆除离场销毁，而新组件的新 DOM 实体却因为动画强制混搭被提前挂载在了树干页面流最下面挤入**！这会立刻暴雷导致撑爆原本严丝合缝的长宽版式容器发生不可名状地扭曲错位弹射跳动。加了 `out-in` 虽牺牲了半秒干等前任彻底凉透离场所导致的串行等待，却完美捍卫守住了这块脆弱渲染引擎遮羞布遮挡。

## 4. 常见坑点

**忽视了 Keep-Alive 下的神出鬼没的复用截断钩子失效问题**
如果你在路由底下裹了一层 `<KeepAlive>` 并指望切换来回时不销毁填过的搜索表格。你会发现当用户第二次带着不同的 URL Query 参数 `?id=999` 点进这同一个被冻结缓存着的列表外壳时。
**原理解释**：`created` 甚至全局的某些重加载钩子统统变成了**完全死寂未唤醒触发**！因为 Vue 觉得外壳没碎肉身重现无需繁琐再生复苏。
**解法必修**：你必须死死利用被唤醒出坟时绝配的专属诈尸特权挂载锚点钩子 `onActivated` 或者更严苛地在深层组件直接去 `watch(() => route.query)` ，才能探听到外头参数已经变天重设发了请求。

## 5. 延伸思考

传统的 Web 后台鉴权把所有的防波堤筑死立在了全局的 `beforeEach` 这一个死关口。如果权限分支繁复多达三百路由，导致光是循环判断比对就需要耗掉几十毫秒堵塞了页面渲染出字的时评帧率？
微前端和当前流行火爆推进的服务端 SSR 端直给直吐模式出现破局点。既然在发给浏览器包裹时 URL 权属就已经被判定拦截阻击。前端还需要背上这沉重几十 KB 乃至兆比的超级大本营总路由判断查询引擎映射图谱文件负载前行吗？

## 6. 总结

- 抛弃在登录时定死的残废路由观念，引入被动补加重启式打断 `addRoute` 填鸭防空手段。
- 在 `beforeResolve` 卡死并吸纳巨量阻塞式首屏依赖加载数据拦截操作。
- `mode="out-in"` 永远是你修复动画错杂乱炖撑爆屏幕流淌惨案的第一防线。

## 7. 参考

- [Vue Router 导航守卫执行全钩子顺序深度解读](https://router.vuejs.org/zh/guide/advanced/navigation-guards.html)
- [动态路由与 addRoute 重定向刷新机制](https://router.vuejs.org/zh/guide/advanced/dynamic-routing.html)
