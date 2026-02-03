# 05. 状态架构：提升与归约

在理解了“UI = f(state)”之后，开发者面临的最大挑战通常是：“这个 state 应该放在哪里？”

如果放错了位置，应用就会变成一团乱麻：Props 传得到处都是，状态不同步，Bug 频出。

本章提供两个核心工具来驯服状态：**Lifting State Up (状态提升)** 和 **Reducers (状态归约)**。

## 心理模型：水流与电线

React 的数据流向非常严格：**单向数据流**。

*   **Props 就像瀑布的水流**：只能从上往下流（父组件 -> 子组件）。水流可以分叉，但永远不会倒流。
*   **Events 就像电线回路**：只能从下往上触发（子组件 -> 父组件）。子组件按下开关，父组件接收信号。

## 核心原则：单一数据源 (Single Source of Truth)

假设有两个组件：`List` (展示列表) 和 `Count` (展示数量)。
如果在 `List` 里存一份数据，在 `Count` 里存一份数字... 很快它们就会不同步。

正确的做法是：**找到它们最近的共同父组件**，把 State 放在那里，然后像分发水源一样通过 Props 传给它们。

这就是 **状态提升**。状态应该尽量“往高处放”，直到它能覆盖所有需要用到它的子组件。

## 复杂的逻辑：useReducer

当状态更新逻辑变得复杂时（比如：更新 A 字段需要同时参考 B 字段和 C 字段），散落在各处的 `setState` 会让代码变得难以理解。

这时候，需要引入一个新的心理模型：**状态归约 (Reducer)**。

### 心理模型：公园检票闸机 (The Turnstile)

想象一个公园的检票闸机。它是一个简单的机器，它的状态转换逻辑是固定的。
它并不关心是谁推了它，它只关心收到了什么“动作”。

*   当前状态：**LOCKED** (锁定)
    *   动作：**PUT_COIN** (投币) -> 变成 **UNLOCKED**
    *   动作：**PUSH** (推) -> 保持 **LOCKED** (并报警)
*   当前状态：**UNLOCKED** (解锁)
    *   动作：**PUT_COIN** (投币) -> 保持 **UNLOCKED** (退币)
    *   动作：**PUSH** (推) -> 变成 **LOCKED**

在 React 中，`useReducer` 就是这个闸机逻辑的集中管理器。

### 对比 useState vs useReducer

**使用 useState (分散的指令)**：
指挥官亲自下令修改数据。
*   “把 count 加 1”
*   “把 count 设为 0”
*   “把 isLoading 设为 true”

**使用 useReducer (事件驱动)**：
不再直接指挥数据的变化，只负责**广播事件**。
*   “发生了 [Increment] 事件”
*   “发生了 [Reset] 事件”
*   “发生了 [FetchStart] 事件”

至于“发生了 [Increment] 事件后数据该怎么变”，这段逻辑被统一封装在了 **Reducer 函数** 里。这实现了 UI (组件) 与 业务逻辑 (Reducer) 的彻底分离。

```javascript
// Reducer 函数：纯纯的逻辑，不涉及任何 UI
function counterReducer(state, action) {
  switch (action.type) {
    case 'increment':
      return { count: state.count + 1 };
    case 'reset':
      return { count: 0 };
    default:
      return state;
  }
}

// 组件：只负责展示和发出信号
function Counter() {
  const [state, dispatch] = useReducer(counterReducer, { count: 0 });

  return (
    <>
      Ping: {state.count}
      <button onClick={() => dispatch({ type: 'increment' })}>+</button>
      <button onClick={() => dispatch({ type: 'reset' })}>0</button>
    </>
  );
}
```

## 总结

1.  **React 数据流是单向的**。Props 向下流，Events 向上触发。
2.  **单一数据源**。不要复制 State，而是把它提升到最近的共同父组件。
3.  **useReducer** 是管理复杂状态逻辑的神器。它将“做什么 (Action)”和“怎么做 (Reducer)”分离开来，让逻辑更加清晰、可测试。
