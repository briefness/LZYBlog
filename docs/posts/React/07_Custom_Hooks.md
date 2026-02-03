# 07. 自定义 Hook：逻辑复用

在 React 出现之前，复用“UI” (View) 很容易，但复用“逻辑” (Logic) 却很困难。
Mixins, HOCs (高阶组件), Render Props... 历史上出现过各种模式，但都很复杂。

Hooks 的出现改变了一切。它允许从组件中提取状态逻辑，就像提取普通函数一样简单。

## 心理模型：安装插件 (Installing Skills)

如果说组件是游戏里的角色，那么自定义 Hook 就是**技能书**或者**装备**。

*   **普通函数**：只能复用无状态的计算逻辑（比如算出两个日期的差值）。
*   **组件**：复用 UI 模版（比如一个按钮的样式）。
*   **Hook**：复用**有状态的行为**（Stateful Behavior）。

当调用 `useWindowWidth()` 时，就像给组件安装了一个“感知窗口宽度”的技能。组件内部自动获得了一个会随窗口大小改变而更新的 state。

## 提取逻辑：从组件到 Hook

假设在两个组件里都写了“检测在线状态”的代码：

```javascript
function StatusBar() {
  const [isOnline, setIsOnline] = useState(true);
  useEffect(() => {
    // ... 监听 window.ononline ...
  }, []);
  // ...
}

function SaveButton() {
  const [isOnline, setIsOnline] = useState(true);
  useEffect(() => {
    // ... 监听 window.ononline ...
  }, []);
  // ...
}
```

这违反了 DRY (Don't Repeat Yourself) 原则。
可以把这段逻辑提取出来，命名为 `useOnlineStatus`。

```javascript
// ✅ 自定义 Hook (必须以 use 开头)
function useOnlineStatus() {
  const [isOnline, setIsOnline] = useState(true); // 1. 拥有自己的 State

  useEffect(() => { 
    // 2. 拥有自己的 Effect
    function handleOnline() { setIsOnline(true); }
    function handleOffline() { setIsOnline(false); }
    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);
    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  return isOnline; // 3. 返回数据，而不是 UI
}
```

现在组件变得极其干净：

```javascript
function StatusBar() {
  const isOnline = useOnlineStatus(); // 装备技能
  return <h1>{isOnline ? 'Online' : 'Disconnected'}</h1>;
}

function SaveButton() {
  const isOnline = useOnlineStatus(); // 装备技能
  return <button disabled={!isOnline}>Save Progress</button>;
}
```

## 关键规则：独立状态 (Independent State)

这是 Hook 最神奇，也最容易被误解的地方。

**复用 Hook，复用的是“逻辑”，而不是“状态值”。**

如果在两个组件里分别调用了 `useOnlineStatus()`，这相当于它们**各自**创建了一套 `useState` 和 `useEffect`。它们只是共用了同一套“蓝图”，但在运行时是完全独立的。

这就像两个人都买了同一本《食谱》（复用逻辑），各自在家做菜。A 把菜烧糊了（改变状态 A），并不会影响 B 的菜（状态 B）。

如果真的想要在组件之间共享同一个内存中的状态值（比如全局用户数据），需要把 Hook 和 **Context** 结合使用。

## 什么时候写 Hook？

当发现自己在写 `useEffect` 时，请停下来想一想：
**“这段 Effect 的意图是什么？”**

如果是“连接聊天室”，那就提取成 `useChatRoom`。
如果是“获取数据”，那就提取成 `useFetch`。
如果是“监听键盘”，那就提取成 `useKeyPress`。

把具体的 `useEffect` 隐藏在具有语义化名称的自定义 Hook 后面，能让组件代码从“一堆复杂的连线”变成“一份清晰的功能清单”。

## 总结

1.  **自定义 Hook** 允许像提取函数一样提取状态逻辑。函数名必须以 `use` 开头。
2.  **复用逻辑，不复用状态**。每次调用 Hook 都会生成一份全新的、独立的状态。
3.  **组合优于继承**。可以像搭积木一样，在一个 Hook 里调用另一个 Hook，构建出极其强大的功能。
