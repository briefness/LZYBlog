# 03. 状态快照与服务员模型

如果说组件是函数，那么 `State`（状态）就是这个函数唯一的、随时间变化的“记忆”。

初学者最容易掉进去的陷阱之一，就是把 React 的 State 当作普通的 JavaScript 变量来看待。

```javascript
// ❌ 这种思维模型是错误的
state.count = 5;
console.log(state.count); // 5
```

在 React 中，State 的行为更像是**一张张底片**或者**一帧帧画面**。

## 心理模型：快照 (Snapshot)

当 React 调用组件函数时，它会提供一张当前时刻的 **State 快照**。这组 Props 和 State 是不可变的，它们就像一张照片定格了那一瞬间。

请看这个经典的“陷阱”题：

```javascript
export default function Counter() {
  const [number, setNumber] = useState(0);

  return (
    <>
      <h1>{number}</h1>
      <button onClick={() => {
        setNumber(number + 1);
        setNumber(number + 1);
        setNumber(number + 1);
      }}>+3</button>
    </>
  );
}
```

点击按钮后，`number` 会变成多少？
A) 1
B) 3

答案是 **A) 1**。

为什么？套用“快照”模型。

1.  **初始渲染**：`number` 是 0。React 给 onClick 处理函数拍了一张快照。在这张快照里，`number` **永远是 0**。
2.  **执行点击**：
    *   第一行：`setNumber(0 + 1)` -> 告诉 React 准备把下次的 number 变成 1。
    *   第二行：`setNumber(0 + 1)` -> 告诉 React 准备把下次的 number 变成 1。
    *   第三行：`setNumber(0 + 1)` -> 告诉 React 准备把下次的 number 变成 1。
3.  **下一次渲染**：React 仅仅记得“让它变成 1”。于是新的一次渲染，`number` 变成了 1。

对于组件的这一次运行（这一帧）来说，`number` 就像常量一样被“冻结”了。无论调用多少次 setNumber，只要在这一帧里引用 `number`，它就一定是 0。

## 心理模型：餐厅服务员 (The Waiter)

那么，如果确实想在一个事件里连加三次怎么办？需要通过“更新函数”来传达指令。

这就引入了第二个心理模型：**Batching（批处理）与服务员**。

调用 `setState` 时，React 并不会立即停止手头的工作去更新 DOM。相反，它像一个餐厅服务员。

1.  发出指令：“服务员，点菜！（setNumber）”
2.  服务员记下来，但没动。
3.  又发出指令：“再加个菜！（setNumber）”
4.  服务员继续记。
5.  等这桌完全点完（事件处理函数执行完毕），服务员才会一次性把单子送到厨房（Render）。

这就是**自动批处理 (Automatic Batching)**。无论写了多少个 `setState`，React 只会重新渲染一次。这极大地提高了性能。

### 如何修正上面的 Bug？

如果想基于“最新的状态”进行更新，而不是基于“这一帧的快照”，需要给服务员递一张“便条”，而不是直接报菜名。

```javascript
<button onClick={() => {
  setNumber(n => n + 1); // 这里的 n 是“上一刻计算出的最新值”
  setNumber(n => n + 1);
  setNumber(n => n + 1);
}}>+3</button>
```

这次的执行流程是：
1.  React 接到指令：`n => n + 1`。放入队列。
2.  React 接到指令：`n => n + 1`。放入队列。
3.  React 接到指令：`n => n + 1`。放入队列。

当渲染发生时，React 会依次运行队列：
*   0 -> 0 + 1 = 1
*   1 -> 1 + 1 = 2
*   2 -> 2 + 1 = 3

最终结果：3。

## 状态也是时间旅行

理解“快照”不仅能帮助解决 Bug，还能帮助构建“时光机”应用。

因为每一次渲染都有自己独立的 Props 和 State，所以：

```javascript
  const [message, setMessage] = useState('');

  function handleSend() {
    setTimeout(() => {
      alert('刚才说了: ' + message);
    }, 5000);
  }
```

假设输入“Hello”，点击发送，然后迅速把输入框改为“World”。
5秒后，alert 会弹出什么？

答案是 **"Hello"**。

因为当点击发送的那一刻，React “捕获”了那次渲染的 `message`（它是 "Hello"）。无论之后 `message` 怎么变，那个已经触发的 `setTimeout` 里原本的闭包永远锁住了由于点击那一刻产生的快照。

这保证了 UI 的一致性：用户点击发送时看到的是什么，发送的内容就是什么，不会因为手快改了字而发生错误。

## 总结

1.  **State 不是变量**，它是每一次渲染中被固定住的常量（快照）。
2.  **设置 State 是发起一次更新请求**，而不是立即修改值的操作。
3.  **React 会对状态更新进行批处理**（服务员模型），等多条更新都排队完毕后，才进行一次渲染。
4.  如果需要依赖上一次计算的结果，请使用**函数式更新** `setNumber(n => n + 1)`。
