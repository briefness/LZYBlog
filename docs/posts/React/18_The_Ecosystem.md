# 18. 生态与框架：如何启动

在 2026 年，如果去 React 官网点击 "Get Started"，会发现官方不再推荐 `create-react-app` (CRA)。
相反，官方推荐使用 **Next.js**, **Remix**, 或者 **Vite**。

这让很多新手感到困惑：如果只是想写个 Hello World，为什么需要这么多复杂的框架？

## 心理模型：交通工具选择

选择 React 的启动方式，就像选择交通工具。

### 1. Vite：轻量级跑车 (The Sedan)

*   **特点**：极速启动，结构简单，纯客户端渲染 (CSR)。
*   **适用场景**：
    *   后台管理系统 (Dashboard)。
    *   需要被打包嵌入到这其他系统的组件。
    *   不需要 SEO 的单页应用。
*   **本质**：它生成的产物是 `index.html` + `bundle.js`。将其往任何一个静态服务器（Nginx, S3）上一扔就能跑。

```bash
# 启动一辆跑车
npm create vite@latest my-app -- --template react
```

### 2. Next.js / Remix：重型卡车 (The Truck)

*   **特点**：全栈框架，支持服务端渲染 (SSR, RSC)，支持 API 路由，自带路由系统。
*   **适用场景**：
    *   电商网站、博客、新闻门户（需要 SEO）。
    *   全栈应用（直接连接数据库）。
    *   追求极致首屏性能的应用。
*   **本质**：它不仅生成静态文件，还包含一个 **Node.js 服务器**。需要部署到 Vercel 或者 Docker 容器里运行。

```bash
# 启动一辆卡车
npx create-next-app@latest
```

## 为什么要用框架？

可能会问：“为什么不能只用 React 库本身？”

可以，但这就像**自己买零件组装汽车**。开发者需要自己配置 Webpack，自己配置 Babel，自己配置路由 (React Router)，自己处理 CSS 压缩...

React 官方现在的态度是：**React 是一个库 (Library)，但为了最好的体验，应该在一个框架 (Framework) 中使用它。**

框架解决了：
*   **路由**：文件即路由 (File-system routing)。
*   **数据获取**：RSC 和 Server Actions。
*   **性能**：自动的代码分割 (Code Splitting) 和图片优化。

## 总结

1.  **别再用 CRA**。`create-react-app` 已经过时且停止维护。
2.  **默认选 Next.js**。如果不确定选什么，Next.js 是最安全的选择，它既能做静态网站，也能做全栈应用。
3.  **轻量选 Vite**。如果确定只需要一个纯前端 SPA，或者在学习 demo，Vite 是最快最简单的选择。
4.  **React 已经不仅是 UI 库**。它已经演变成了一个**操作系统**，而 Next.js/Remix 是运行这个操作系统的**电脑**。
