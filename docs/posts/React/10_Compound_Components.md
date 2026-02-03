# 10. 设计模式：复合组件 (Compound Components)

当开始编写可复用的组件库时，会有到一个经典问题：**如何设计 API？**

新手通常设计成这样：

```javascript
// ❌ 配置地狱 (Configuration Hell)
<Select 
  options={['A', 'B', 'C']} 
  selected="A" 
  onSelect={...}
  optionStyle={{ color: 'red' }}
  renderOption={(opt) => <b>{opt}</b>}
/>
```

这种“巨石组件”非常僵硬。如果想给其中一个选项加个图标？或者给选项分组？得不断加新的 props（比如 `optionIcon`、`groupBy`），直到 props 列表比组件本身代码还长。

## 心理模型：乐高积木 (Lego Bricks)

**Compound Components (复合组件)** 模式建议将巨石打碎成一组可以自由组合的小积木。

```javascript
// ✅ 复合组件：清晰、灵活、声明式
<Select>
  <Select.Trigger />
  <Select.List>
    <Select.Option value="A">Item A</Select.Option>
    <Select.Option value="B">
       <Icon name="star" /> {/* 想怎么定制都行 */}
       Item B
    </Select.Option>
  </Select.List>
</Select>
```

这就是 HTML `<select>` 和 `<option>` 的原生设计哲学。React 组件复刻了这种体验。

## 原理：隐式状态共享

可能会问：`Select.Option` 怎么知道当前被选中的是哪个？`Select` 并没有把 `selectedValue` 显式传给 `Select.Option` 啊？

答案是：**Context**。

在这个模式中，父组件 `<Select>` 实际上是一个 Context Provider。它在内部维护了状态（selected value），并通过 Context 悄悄地把状态和回调函数传给了所有的子组件。

```javascript
// 1. 创建 Context
const SelectContext = createContext();

// 2. 父组件：管理状态，提供 Context
function Select({ children, onChange }) {
  const [value, setValue] = useState(null);
  
  return (
    <SelectContext.Provider value={{ value, setValue, onChange }}>
      <div className="select-root">{children}</div>
    </SelectContext.Provider>
  );
}

// 3. 子组件：消费 Context
Select.Option = function Option({ value, children }) {
  const context = useContext(SelectContext);
  const isActive = context.value === value;

  return (
    <div 
      className={isActive ? 'active' : ''}
      onClick={() => context.setValue(value)}
    >
      {children}
    </div>
  );
};
```

## 这种模式的好处

1.  **UI 与逻辑分离**：`<Select>` 负责逻辑（谁被选中了），而渲染长什么样完全交给使用者决定。
2.  **避免 Prop Drilling**：不需要把 props 传给 Select 再传给 List 再传给 Option。
3.  **极其灵活**：使用者可以在 Option 之间插入 `<hr />`，或者把 List 包裹在额外的 `<div>` 里，结构随心所欲，只要在 Context 树下即可。

## 总结

1.  **拒绝巨石组件**。不要把所有 UI 逻辑都写在一个组件里并通过巨大的 props 对象配置。
2.  **像 HTML 一样思考**。`<select>` 配合 `<option>`，`<table>` 配合 `<tr>` `<td>`。这是最好的 API 设计老师。
3.  **Context 是胶水**。它让父子组件在不需要显式传递 props 的情况下进行“隐式通信”。
