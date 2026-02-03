# 09. 上下文：数据传送门

Props 是 React 数据流的血脉。但如果组件层级很深，一层一层地传递 Props（Prop Drilling）会让人痛不欲生。

想象要把这行字传给曾曾曾孙组件：
`<GrandGrandGrandChild theme="dark" />`

需要经过许多完全不关心这个 props 的中间组件。这显然不合理。

React 提供了 **Context (上下文)** 来解决这个问题。

## 心理模型：传送门 (The Teleporter)

如果说 Props 是**走楼梯**，一层一层往下送。
那么 Context 就是**传送门**或者**广播塔**。

1.  在顶层建立一个**发射站** (Provider)。
2.  曾曾曾孙组件建立一个**接收器** (Consumer / useContext)。
3.  数据直接“瞬间移动”到了底部，完全绕过了中间的楼层。

## 如何使用 Context

Context 分为三步：**创建、提供、使用**。

### 1. 创建 (Create)
一般在一个单独的文件里，或者组件外部。

```javascript
import { createContext } from 'react';

// 创建一个“主题”传送门，默认值是 'light'
export const ThemeContext = createContext('light');
```

### 2. 提供 (Provide)
在组件树的上方，圈出一块“信号覆盖区”。

```javascript
import { ThemeContext } from './ThemeContext';

function App() {
  const [theme, setTheme] = useState('dark');

  return (
    // 这里的 value 就是发射出去的信号
    <ThemeContext.Provider value={theme}>
      <Toolbar /> 
      {/* Toolbar 内部可能包含了成百上千个组件 */}
    </ThemeContext.Provider>
  );
}
```

### 3. 使用 (Use)
在任何被覆盖的子组件里，直接读取信号。

```javascript
import { useContext } from 'react';
import { ThemeContext } from './ThemeContext';

function MyButton() {
  // 直接拿到 'dark'，不需要父组件传 Props 也行
  const theme = useContext(ThemeContext);
  
  return <button className={theme}>I am styled!</button>;
}
```

## Context + Reducer：终极状态管理

还记得之前说的 `useReducer` 吗？如果把 Reducer 的 `dispatch` 函数也放进 Context 里，会有什么效果？

任何组件，无论藏得多深，都可以：
1.  通过 Context 读取全局 State。
2.  通过 Context 获取 `dispatch` 函数，向全局发送指令。

```javascript
// 这是一个极简版的 Redux
const [state, dispatch] = useReducer(reducer, initialState);

<TasksContext.Provider value={state}>
  <DispatchContext.Provider value={dispatch}>
    <DeepComponent />
  </DispatchContext.Provider>
</TasksContext.Provider>
```

这就是很多大型 React 应用（如果不使用 Redux/Zustand）所采用的架构：**Context 用于分发数据，Reducer 用于管理逻辑。**

## 警告：不要滥用 Context

Context 很强大，但有一个缺点：**它破坏了组件的复用性**。

如果 `MyButton` 依赖了 `ThemeContext`，那它就没法单独拿出来在别的地方用了（除非那个地方也提供了 ThemeContext）。它变得不再纯粹，而是产生了“环境依赖”。

**使用原则**：
1.  **优先使用 Props**。显式的数据流最清晰。
2.  **只有通过了很多层组件，且这些组件确实不应该关心这个数据时**，才考虑 Context。
3.  常见的 Context 用例：
    *   主题 (Theme)
    *   当前登录用户 (CurrentUser)
    *   路由 (Routing)
    *   全局状态管理

## 总结

1.  **Context 解决了 Prop Drilling 问题**。它像传送门一样让数据直达深层组件。
2.  **createContext** 创建频道，**Provider** 发射信号，**useContext** 接收信号。
3.  配合 **useReducer**，可以构建强大的全局状态管理方案。
4.  **谨慎使用**。不要为了省去传递两个 props 就引入 Context，这会增加组件的耦合度。
