# 12. 性能优化：缓存与记忆

“React 太慢了！”
这通常不是 React 的错，而是因为组件在做无用功。

本章将深入 React 的渲染机制，学习如何使用 **Memoization (记忆化)** 三剑客：`memo`, `useMemo`, `useCallback` 来阻止不必要的渲染。

## 核心机制：为什么会重新渲染？

在 React 中，组件重新渲染的原因主要有两个：
1.  **State 变了** (组件自己要求更新)。
2.  **Parent 渲染了** (因为父组件更新，子组件被迫陪跑)。

重点在第二点。默认情况下，如果父组件渲染了，它内部的**所有**子组件（哪怕 Props 根本没变）都会递归地重新渲染。

这是为了确保 UI 永远是最新的（宁可错杀一千，不放过一个），但在大型应用中，这会导致性能问题。

## 心理模型：卫兵 (The Guard) - React.memo

怎么阻止这种连带效应？需要给子组件门口站一个卫兵。

```javascript
const MemoizedChild = memo(Child);
```

这个卫兵 (`memo`) 会拦截父组件发来的渲染请求，并进行检查：
*   **“站住！新 Props 和旧 Props 有变化吗？”**
*   如果没有变化（全等比较 `prevProps === nextProps`），卫兵就会把请求挡回去：“不用渲染了，直接用上次的结果。”
*   只有当 Props 真的变了，才会放行。

## 心理模型：记忆化 (Memoization)

仅仅加了 `memo` 还不够。因为在 JavaScript 中，`{}` 不等于 `{}`，`function(){}` 不等于 `function(){}`。

如果父组件在每次渲染时都创建新的对象或函数传给子组件，那么卫兵的检查永远会失效（因为每次引用的地址都变了）。

这时需要两个工具来“缓存”这些值，保证它们在不同渲染之间保持引用稳定。

### 1. useMemo：缓存计算结果

想象在做一道很难的数学题（昂贵的计算）。

```javascript
// ❌ 每次渲染都重新算一遍，太慢了！
const visibleTodos = filterTodos(todos, tab);

// ✅ 只有当 todos 或 tab 变了，才重算。否则直接读上次的答案。
const visibleTodos = useMemo(() => {
  return filterTodos(todos, tab);
}, [todos, tab]);
```

**useMemo** 就像**备忘录**。如果题目（依赖项）没变，就直接抄之前的答案，而不用重新开动大脑（运行函数）。

### 2. useCallback：缓存函数引用

假设要传给子组件一个回调函数。

```javascript
// ❌ 每次父组件渲染，handleClick 都是一个全新的函数地址
// 导致 MemoizedChild 的卫兵认为 Props 变了，于是重新渲染
function Parent() {
  const handleClick = () => { console.log('Clicked'); };
  return <MemoizedChild onClick={handleClick} />;
}

// ✅ 只要依赖没变，handleClick 永远指向同一个函数地址
// 卫兵看到 Props 没变，成功拦截渲染
function Parent() {
  const handleClick = useCallback(() => {
    console.log('Clicked');
  }, []); // 依赖为空，永远不变
  return <MemoizedChild onClick={handleClick} />;
}
```

**useCallback** 并不执行函数，它只是**冻结**了这个函数的身份 ID。

## 总结图谱

性能优化不是魔法，它是**三个环节的配合**：

1.  **React.memo**：给子组件穿上防弹衣（只有 Props 变了才渲染）。
2.  **useCallback**：保证传给子组件的**函数**不会变。
3.  **useMemo**：保证传给子组件的**对象/数组**不会变。

缺一不可。如果只用了 `memo` 但没用 `useCallback`，防弹衣就会被击穿。如果只用了 `useCallback` 但子组件没加 `memo`，那做了也是白做（因为子组件本来就会跟着父组件渲染）。

## 什么时候优化？

不要过早优化。

**大部分时候，不需要这些工具。** React 已经足够快了。
只有当发现打字卡顿、动画掉帧时，打开 React DevTools 的 Profiler，找到那个渲染时间最长的组件，然后对症下药。

滥用 memoization 也是有代价的（需要消耗内存来存旧值，需要消耗 CPU 来对比依赖项）。

## 6. 实战工具：Profiler 深度解读

不要只凭借感觉去优化。使用 **React DevTools Profiler**。

1.  **记录 (Record)**：点击圆形按钮开始录制，操作页面，点击停止。
2.  **火焰图 (Flamegraph)**：
    *   **灰色**：未渲染 (Good)。
    *   **绿色**：渲染速度快 (OK)。
    *   **黄色/红色**：渲染极慢 (Need Optimization)。
3.  **Why did this render?**：
    *   勾选设置里的 "Record why each component rendered while profiling"。
    *   Hover 到组件上，DevTools 会告诉你原因："Props changed: (style)" -> 说明你可能传入了内联样式对象。

## 7. 避坑指南 (Anti-Patterns)

*   **内联对象地狱**：
    `style={{ color: 'red' }}` 或 `options={['a', 'b']}`。每次渲染都会生成新引用，导致 memo 失效。
    **解法**：提到组件外定义常量，或使用 `useMemo`。
*   **Props 穿透**：
    把不知名的 `{...props}` 一股脑传下去，导致子组件接收了无关的属性变化。
    **解法**：明确 Props 定义。

## 8. 总结 Checklist

在提交代码前，过一遍这个清单：

1.  [ ] **是否有明显卡顿？** (没有就别动！)
2.  [ ] **Profiler 检查**：是否有组件无缘无故渲染了？
3.  [ ] **Props 稳定性**：传递给 memo 组件的 props (对象/函数) 是否用 `useMemo`/`useCallback` 包裹了？
4.  [ ] **Context 粒度**：是否有 Context Value 变动导致全树重绘？(考虑拆分 Context)。
5.  [ ] **Key 的唯一性**：列表渲染是否用了 Index 做 Key？(大忌)。

## 9. 总结

1.  **React 默认行为**：父组件渲染，子组件无条件跟着渲染。
2.  **memo**：阻止不必要的子组件渲染（仅当 Props 变化时）。
3.  **useMemo**：缓存昂贵的计算结果。
4.  **useCallback**：缓存函数的引用地址，配合 `memo` 使用。
5.  **性能优化原则**：先跑通，再探测瓶颈，最后才优化。
