# 15. 服务端组件 (RSC)：后端的反攻

在 React 诞生后的前 7 年里，遵循着“客户端渲染 (CSR)”的模式：浏览器下载一个空白 HTML 和一个巨大的 JS 包，然后在用户电脑上从零开始组装页面。

这种模式有两个痛点：
1.  **包体积过大**：为了渲染 Markdown，需要把整个 markdown-parser 库（20KB）下载到用户手机上。
2.  **网络瀑布流**：组件加载 -> useEffect fetch -> 等待 API -> 渲染子组件 -> 子组件 fetch...

React 团队在 2020 年提出了革命性的 **React Server Components (RSC)**。

## 心理模型：三明治 (The Sandwich)

以前，React 应用要么全在客户端（CSR），要么全在服务端（SSR，生成 HTML 字符串）。
RSC 引入了一个全新的概念：**组件是可以在服务器上运行的**。

想象一个三明治：
*   **服务端组件 (面包)**：负责 layout、数据获取、静态展示。
*   **客户端组件 (肉)**：负责交互、点击、状态。

React 现在允许**混合使用**这两种组件。

### RSC 的超能力

服务端组件 (默认组件) 有几个惊人的特性：

1.  **零 Bundle Size**：它们的代码**永远不会**被发送到浏览器。
    *   这意味着可以直接引入巨大的数据库 ORM、Markdown 解析器、甚至读取本地文件系统。
    *   用户下载的 JS 包里，只有渲染结果（UI），没有库代码。

2.  **直接访问后端**：不再需要 `fetch('/api/data')`。
    *   可以直接写 `await db.query()`。因为代码就是在服务器上跑的。

```javascript
// app/page.tsx (这是一个 Server Component)
import db from './db'; 

// ✅ 这是一个 async 组件，直接读取数据库
export default async function Page() {
  const data = await db.query('SELECT * FROM posts');
  
  return (
    <main>
      <h1>Blog Posts</h1>
      {/* 直接渲染数据，这一行是在服务器完成的 */}
      <ul>
        {data.map(post => <li key={post.id}>{post.title}</li>)}
      </ul>
      
      {/* 只有像 SearchBar 这种需要交互的组件，才会被发送到浏览器 */}
      <SearchBar /> 
    </main>
  );
}
```

## 客户端组件：Client Boundary

但是，服务器上没有 `window`，没有 `onClick`，没有 `useState`（因为服务器只跑一次）。
如果需要交互（比如点击按钮、输入框），需要显式地声明一个“客户端边界”。

```javascript
// components/SearchBar.tsx
'use client'; // 👈 这行指令告诉 React：从这里开始，打包发送到浏览器

import { useState } from 'react';

export default function SearchBar() {
  const [text, setText] = useState(''); // ✅ 可以使用 State
  return <input onChange={e => setText(e.target.value)} />;
}
```

## 总结

1.  **React 不再只是前端库**。RSC 让 React 跨越了服务器和客户端的边界。
2.  **默认全在服务端**。为了性能，默认组件都是 Server Component。
3.  **交互需要客户端**。只有当需要 `onClick`, `useState`, `useEffect` 时，才加上 `'use client'`。
4.  **数据获取前置**。在 Server Component 里直接 await 数据，消灭了客户端的 useEffect Waterfall。
