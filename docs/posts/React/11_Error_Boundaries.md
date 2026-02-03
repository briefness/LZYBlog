# 11. 错误边界：优雅降级

在大多数 JS 应用中，如果一个函数报错了，整个脚本可能会停止运行。
在 React 中，如果组件树中某一个深层组件渲染报错（比如读取了 `undefined.name`），会导致**整个 React 组件树被卸载**，用户看到的是让人绝望的白屏。

这是不可接受的。侧边栏的一个图标渲染失败，不应该导致顶部导航栏和主内容区也一起消失。

## 心理模型：保险丝 (The Fuse)

**Error Boundary (错误边界)** 就像电路里的保险丝。
如果不装保险丝，短路会烧毁整个房子的电路。
如果在每个房间（每个主要组件区域）都装了保险丝，那么只有那个房间会断电，其他房间依然灯火通明。

## 如何使用

React 目前（2026年）**仍然**只支持通过 Class Component 来编写错误边界（这可能是现在唯一需要写 Class 的理由）。

```javascript
class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error) {
    // 1. 渲染出错时，更新 state，让下一次渲染显示备用 UI
    return { hasError: true };
  }

  componentDidCatch(error, errorInfo) {
    // 2. 可以在这里把错误日志上报给服务器
    logErrorToService(error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      // 3. 渲染备用 UI (Fallback UI)
      return <h1>Something went wrong.</h1>;
    }

    return this.props.children; 
  }
}
```

### 使用方式：包裹组件

```javascript
<nav>
  <ErrorBoundary>
    <Sidebar /> 
    {/* 如果 Sidebar 崩溃，Nav 和 MainContent 完全不受影响 */}
  </ErrorBoundary>
</nav>

<main>
  <ErrorBoundary>
    <Feed />
  </ErrorBoundary>
</main>
```

## 现代方式：react-error-boundary

虽然 Class 组件能用，但写起来很繁琐。社区标准做法是使用 `react-error-boundary` 库。

```javascript
import { ErrorBoundary } from 'react-error-boundary';

function Fallback({ error, resetErrorBoundary }) {
  return (
    <div role="alert">
      <p>Something went wrong:</p>
      <pre>{error.message}</pre>
      <button onClick={resetErrorBoundary}>Try again</button>
    </div>
  );
}

function App() {
  return (
    <ErrorBoundary 
      FallbackComponent={Fallback}
      onReset={() => {
        // 重置时要做的事情（比如重置某些 State）
      }}
    >
      <MyComponent />
    </ErrorBoundary>
  );
}
```

不仅提供了备用 UI，还获得了一个“重试 (Try again)”按钮。这让应用具备了**自愈能力**——用户也许只是遇到了一个偶发的网络错误，点一下重试就好了，而不需要刷新整个页面。

## 总结

1.  **白屏是不可接受的**。永远不要让局部错误导致整个应用崩溃。
2.  **错误边界是声明式的**。就像 `<Suspense>` 处理 loading 一样，`<ErrorBoundary>` 处理 error。
3.  **粒度控制**。不要只在最顶层包一个。在关键的 UI 块（如侧边栏、列表项、主画布）周围分别包裹，实现“舱室隔离”。
