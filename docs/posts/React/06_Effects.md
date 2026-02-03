# 06. 同步与副作用：逃生舱

如果 React 的世界也是完美的，那么所有组件都应该是纯函数。
但现实世界是不完美的。组件需要连接服务器、监听键盘事件、操作 DOM、对接第三方地图 SDK...

这些不属于 React 清爽的“渲染公式”的部分，被称为 **Side Effects (副作用)**。

而在 React 中，处理副作用的主要工具是 **Effects (useEffect)**。

## 心理模型：逃生舱 (Escape Hatches)

将 React 想象成一个高度自动化的**无菌实验室**（纯渲染世界）。在这里，一切都是可预测的，尘埃不染。
但偶尔，需要把手伸出窗外去拿个快递，或者在泥地里打个滚。

`useEffect` 就是这个**逃生舱**。它允许组件暂时离开 React 的纯粹逻辑，去连接外部系统。

*   **内部系统**：State, Props, Context (React 能够完全控制)。
*   **外部系统**：Browser DOM API, `window.addEventListener`, `fetch`, `setInterval` (React 无法控制)。

**Effects 的唯一目的就是：将 React 组件与外部系统同步 (Synchronize)。**

## 效果的生命周期

Effect 的思考方式与组件不同。它不是“渲染时发生什么”，而是“如何同步”。

### 1. 挂载 (Mount) - 开始同步
当组件第一次出现在屏幕上时，Effect 会运行。这是建立连接的时候。
*   比如：`connection.connect()`
*   比如：`window.addEventListener('scroll', handler)`

### 2. 更新 (Update) - 重新同步
如果 Effect 依赖的数据（Dependencies）变了，React 需要先断开上一次的连接，然后建立新的连接。
这是一个非常关键的概念：**为了保持同步，必须先清理旧的，再建立新的。**

### 3. 卸载 (Unmount) - 停止同步
当组件从屏幕上消失时，React 会最后一次运行清理函数，彻底断开连接。

### 心理模型：插座与插头

想象给手机充电。

*   **Mount**: 把充电器插到插座上（开始充电）。
*   **Dependency Change**: 若要换个房间充电。不能直接瞬移。必须**先拔掉插头 (Cleanup)**，走到新房间，然后**再插上插头 (Setup)**。
*   **Unmount**: 充满电了，把插头拔掉。

## 依赖数组 (Dependency Array) 的真相

`useEffect` 的第二个参数 `[]` 经常被误解为“让这个 Effect 什么时候运行”。
这是一个错误的思维模式。

正确的思维是：**“Effect 代码里用到了 React 里的哪些变量？”**

```javascript
function ChatRoom({ roomId }) {
  useEffect(() => {
    const connection = createConnection(roomId);
    connection.connect(); // Setup

    return () => {
      connection.disconnect(); // Cleanup
    };
  }, [roomId]); // ✅ 必须包含 roomId，因为代码里用了它
}
```

如果欺骗 React，比如代码里用了 `roomId` 但数组里写了 `[]`，就会发生 Bug：
用户切换了房间（`roomId` 变了），但 React 以为没变，所以**没有拔掉旧房间的连接，也没有连上新房间**。用户就在一个错误的聊天室里说话。

## 什么时候并不需要 Effect？

新手最大的误区是滥用 `useEffect`。

**误区 1：用于计算数据**
```javascript
// ❌ 别这么写
useEffect(() => {
  setFullName(firstName + ' ' + lastName);
}, [firstName, lastName]);

// ✅ 直接在渲染过程中计算
const fullName = firstName + ' ' + lastName;
```
如果一个值可以根据现有的 Props 或 State 计算出来，**不要用 Effect**。直接算。

**误区 2：响应用户交互**
如果逻辑是为了响应“用户点击”，那么代码应该写在 **Event Handler (onClick)** 里，而不是 Effect 里。
Effect 是为了响应“因为状态变了，所以需要同步外部系统”，而不是响应“用户刚刚点了按钮”。

## 总结

1.  **Effect 是逃生舱**，用于连接 React 之外的外部系统（API、DOM、事件）。
2.  **核心不仅仅是运行，而是同步**。重点在于如何正确地 Setup 和 Cleanup。
3.  **依赖数组是诚实列表**。它必须如实列出用到的所有 React 变量。
4.  **不要滥用 Effect**。如果在渲染期间能算出结果，或者逻辑是响应用户点击的，那就别用 Effect。
