# 前端性能优化：从入门到卓越（系列大纲）

> 💡 **写作小建议**：
> - 带上 Case Study：每一篇文章最好能结合一个实际的 Bug 或优化前后的对比。
> - 可视化数据：多用火焰图（Flame Chart）和瀑布图（Waterfall）截图来解释。
> - 避开“玄学”：尽量用底层的浏览器源码或规范说明为什么要这么做。

## 目录

### [第一部分：认知篇 —— 为什么要优化？](./01_Cognition.md)
1.1 性能与业务的关系：转化率、留存率与加载时间的“黄金定律”。
1.2 性能指标演进：从 DOMContentLoaded 到 Web Vitals（LCP, FID, CLS, INP）。
1.3 性能测量工具：如何熟练使用 Lighthouse, WebPageTest, 和 Chrome DevTools (Performance/Network)。

### [第二部分：网络传输优化 —— 越快越小越好](./02_Network.md)
2.1 HTTP 协议优化：
   - 从 HTTP/1.1 到 HTTP/2/3（多路复用、头部压缩、QUIC）。
   - 开启 Gzip / Brotli 压缩。
2.2 缓存策略：
   - 强缓存与协商缓存的深度解析。
   - Service Worker 与 PWA 离线缓存。
2.3 CDN 的奥秘：边缘计算与就近访问，减少网络往返时间（RTT）。

### [第三部分：资源构建优化 —— 现代工程化方案](./03_Build.md)
3.1 包体积瘦身：
   - Tree Shaking 的原理与失效场景。
   - 代码分割（Code Splitting）与按需加载。
3.2 图片专项优化：
   - 响应式图片（srcset）、WebP/AVIF 格式转换。
   - 懒加载（Lazy Loading）的最佳实践。
3.3 字体与图标：防止字体闪烁（FOIT/FOUT）及 Iconfont vs SVG 选型。

### [第四部分：渲染性能优化 —— 丝滑般的交互体验](./04_Rendering.md)
4.1 关键渲染路径（CRP）：
   - 理解 DOM -> CSSOM -> Layout -> Paint -> Composite。
4.2 回流（Reflow）与重绘（Repaint）：如何通过合成层（GPU 加速）避开昂贵的计算。
4.3 脚本执行优化：
   - defer 与 async 的区别。
   - 长任务处理：Web Workers 与时间分片（Time Slicing）。

### [第五部分：框架特有优化 —— 以主流框架为例](./05_Frameworks.md)
5.1 React 篇：虚拟 DOM 瓶颈、memo/useMemo/useCallback 的正确姿势、React 18 Concurrent Mode。
5.2 Vue 篇：响应式原理开销、v-show vs v-if、长列表虚拟滚动（Virtual List）。
5.3 跨端/混合开发（选读）：Electron 或 Flutter 项目中的特殊优化技巧。

### [第六部分：前沿技术与未来趋势](./06_Advanced.md)
6.1 预渲染技术：SSR（服务端渲染）、SSG（静态生成）与 ISR。
6.2 WebAssembly：在前端处理重计算场景（如视频转码、图像处理）的优势。
6.3 浏览器新技术：Priority Hints（优先级提示）、Speculative Rules（猜测规则）。

### [第七部分：体系建设篇 —— 让优化可持续](./07_System.md)
7.1 性能监控体系（RUM）：如何上报真实用户数据。
7.2 性能防腐化：在 CI/CD 中集成性能卡点（Performance Budgets）。
7.3 总结：性能优化没有终点，只有权衡。
