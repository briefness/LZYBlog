# 第三部分：资源构建优化 —— 现代工程化方案

构建工具（Webpack/Vite）不仅是打包器，更是代码的“抽脂机”。优化的核心在于：**只给用户看他们当前需要看的代码**。

## 3.1 包体积瘦身：像外科医生一样精准分割

### 1. Tree Shaking 的底层原理与失效陷阱
Tree Shaking 依赖于 ES Modules 的**静态结构**。Bundler 会构建一个 Module Graph，标记哪些 export 被引用了，没被引用的就是 "Dead Code"。

#### 💀 为什么你的 Tree Shaking 没生效？(Case Study)
*   **Bug 现象**：即使只用了 `lodash` 的一个函数 `import { merge } from 'lodash'`, 打包体积依然巨大。
*   **原因分析**：
    1.  **模块规范**：老版本的 `lodash` 导出的是 CommonJS。Webpack 无法静态分析 CommonJS 的依赖关系，只能全量打包。
        *   *Fix*: 使用 `lodash-es`。
    2.  **Side Effects（副作用）**：如果一个文件里写了 `Date.prototype.format = ...`，Webpack 不敢删它，怕删了导致原型链方法丢失。
        *   *Fix*: 在 `package.json` 显式声明 `"sideEffects": false`，告诉 Webpack：“我的包很纯净，放心删”。

### 2. Code Splitting：策略重于技术
不要一股脑全拆，或者拆得太碎。

*   **Granular Chunking (细粒度拆分)**：
    *   Vite/Rollup 默认策略较好。Webpack 需要调优 `SplitChunksPlugin`。
*   **Case Study: Next.js 的按需加载**
    *   Next.js 针对每个 Page 自动做拆分。但在 Page 内部，假设有一个巨大的 `HeavyChart` 组件，只有用户点某个按钮才显示。
    *   *Bad*: `import HeavyChart from './HeavyChart'` (导致首屏 Bundle 包含了图表库)。
    *   *Good*: Dynamic Import。
        ```javascript
        const HeavyChart = dynamic(() => import('./HeavyChart'), {
          loading: () => <p>Loading...</p>
        })
        ```
    *   **效果**：首屏 JS 体积减少 200KB。

## 3.2 图片专项优化：AVIF 与 响应式

### Case Study: 某新闻落地页的图片优化复盘
*   **背景**：页面包含大量高清新闻图，LCP 长达 3s。Lighthouse 提示 "Serve images in next-gen formats"。
*   **动作 1：格式升级**
    *   原图：JPEG (1.2MB)。
    *   WebP (Quality 80): 800KB。
    *   AVIF (Quality 65): **400KB**。包含同样的视觉细节，体积只有原来的 1/3。
*   **动作 2：响应式加载 (Responsive Images)**
    *   移动端用户真的需要 4K 图片吗？不需要。
    *   使用 `srcset` 让浏览器根据屏幕密度（DPR）和视口宽度选图。
    ```html
    <img src="small.jpg"
         srcset="small.jpg 500w, medium.jpg 1000w, large.jpg 2000w"
         sizes="(max-width: 600px) 100vw, 50vw"
         alt="News">
    ```
    *   **结果**：移动端流量消耗降低 60%，LCP 提升 1s。

## 3.3 字体优化：肉眼可见的体验提升

### 1. 字体子集化 (Subsetting)
中文字体包动辄 5MB+，全量加载是不现实的。
*   **技术**：`font-spider` 或 Google Fonts 的 `unicode-range`。只把页面上用到的几百个字打包。
*   **效果**：字体文件从 5MB -> 60KB。

### 2. `font-display: swap` 的取舍
*   **FOIT (Flash of Invisible Text)**：文字隐形，体验极差。
*   **FOUT (Flash of Unstyled Text)**：文字先用 Arial 显示，字体下好后变成自定义字体。
*   **建议**：始终使用 `swap`。宁可文字丑一秒，不能让用户看空着一秒。

---

**(下一章预告)**：代码发到浏览器了。接下来是浏览器最忙碌的时刻——渲染流水线。为什么改一个 `width` 会让浏览器累得半死，而改 `transform` 却很轻松？我们将解读浏览器的“图层合成”机制。
