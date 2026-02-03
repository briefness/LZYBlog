# 13. 进阶性能：并发与架构

在上一章中，学习了如何用 `memo` 拦截不必要的渲染。这属于**CPU 维度的减法**（少做事）。

本章将进入深水区，探讨 React 性能优化的另外三个维度：
1.  **分包 (Code Splitting)**：网络维度的减法。
2.  **并发 (Concurrency)**：CPU 维度的调度。
3.  **状态下放 (State Colocation)**：架构维度的重构。

## 1. 懒加载：按需配送 (Code Splitting)

如果应用是一个巨大的超市，用户只想买一个苹果，却非要开着 18 轮大卡车把整个超市的货都拉到他家门口，这显然很慢。

在 React 中，默认的打包工具（Webpack/Vite）会把所有代码打包成一个巨大的 JS 文件。
即使是一个用户可能永远不会点开的“设置页面”，其代码也会在首屏加载时下载。

### 心理模型：按需配送

需要把应用切分成无数个小包裹。只有当用户点击了某个按钮，才去服务器下载对应的代码。

```javascript
import { lazy, Suspense } from 'react';

// ❌ 静态导入：不管用不用，先下载下来
// import SettingsPage from './SettingsPage';

// ✅ 懒加载：只有渲染这个组件时，才去网络请求代码
const SettingsPage = lazy(() => import('./SettingsPage'));

function App() {
  return (
    // Suspense 是必须的：在下载代码的几百毫秒里，展示什么 loading？
    <Suspense fallback={<Spinner />}>
       {showSettings && <SettingsPage />}
    </Suspense>
  );
}
```

## 2. 并发模式：VIP 通道 (Concurrency)

在 React 18 之前，渲染是**同步**的。一旦开始，无法中断。
如果列表过滤需要 200ms，那么这 200ms 内页面会完全卡死，用户的打字输入无法响应。

React 18 引入了并发渲染，允许将更新分为两类：
1.  **高优先级（紧急）**：打字、点击、拖拽。需要立即反馈。
2.  **低优先级（过渡）**：搜索结果列表渲染、图表绘制。可以慢一点，可以被打断。

### useTransition

```javascript
import { useState, useTransition } from 'react';

function SearchBox() {
  const [text, setText] = useState('');
  const [list, setList] = useState([]);
  const [isPending, startTransition] = useTransition();

  function handleChange(e) {
    // 1. 紧急：立刻更新输入框的值，不能卡
    setText(e.target.value);

    // 2. 过渡：将“过滤列表”这个繁重任务标记为低优先级
    startTransition(() => {
      const filtered = filterBigList(e.target.value);
      setList(filtered);
    });
  }

  return (
    <>
      <input value={text} onChange={handleChange} />
      {isPending ? 'Loading list...' : <List items={list} />}
    </>
  );
}
```

### 心理模型：VIP 通道

*   `setText` 走了 VIP 通道，React 优先处理它。
*   `startTransition` 里的更新走了普通通道。
*   如果 CPU 忙不过来，React 会暂停处理普通通道的任务，先响应用户的打字。感觉上就是页面“更丝滑”了。

## 3. 架构优化：控制爆炸半径

很多时候，性能问题不是因为计算慢，而是因为**受影响的组件太多**。

### 心理模型：爆炸半径

```javascript
// ❌ 坏架构：State 在最顶层
function App() {
  const [inputValue, setInputValue] = useState(''); // 这里的 state 变化会导致 App 重新渲染
  
  return (
    <div>
      <input value={inputValue} onChange={e => setInputValue(e.target.value)} />
      <ExpensiveTree /> {/* 这个昂贵组件被迫陪跑 */}
    </div>
  );
}
```

即使给 `ExpensiveTree` 加了 `memo`，这依然是不好的架构。更好的方法是：**把状态移到它真正被需要的地方**。

```javascript
// ✅ 好架构：State 下放 (State Colocation)
function InputBox() {
  const [inputValue, setInputValue] = useState('');
  return <input value={inputValue} onChange={e => setInputValue(e.target.value)} />;
}

function App() {
  return (
    <div>
      <InputBox /> {/* 它的渲染局限在自己内部 */}
      <ExpensiveTree /> {/* 完全不受影响，哪怕不加 memo */}
    </div>
  );
}
```

通过将 State “下放”到叶子节点，可以将渲染的“爆炸半径”控制在最小范围，从而保护了应用的其他部分。

## 总结

性能优化是一个系统工程：

1.  **Network**: 使用 `lazy` + `Suspense` 切分代码，减少首屏体积。
2.  **CPU (Scheduling)**: 使用 `useTransition` 将重任务标记为低优先级，保持界面响应。
3.  **CPU (Structure)**: 主要靠 **状态下放** 来隔离渲染，次要靠 `memo` 来拦截渲染。
