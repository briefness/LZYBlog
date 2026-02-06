# 第七部分：体系建设篇 —— 让优化可持续

> "Performance is not a checklist, it's a continuous mindset."

如果没有监控和卡点，你今天辛苦优化的 500ms，明天就会被同事引入的一个巨大的 `moment.js` 包吃掉。

## 7.1 RUM (Real User Monitoring) 实战

### 1. 上报什么？
Lab 数据（Lighthouse）只能代表你开发者电脑上的表现。RUM 数据代表真实用户（不同手机、不同弱网环境）的痛苦。
*   **关键指标**：LCP, FID (INP), CLS, FCP, TTFB, Resource Timing.
*   **维度**：Device Type (Mobile/Desktop), Network (4G/Wifi/3G), Region (Geo).

### 2. 代码实现
不管是自建监控还是用 Sentry / Datadog，核心 API 都是 PerformanceObserver。

```javascript
// 核心监控代码示例
const reportWebVital = (metric) => {
  const body = JSON.stringify(metric);
  // 使用 navigator.sendBeacon 确保页面关闭/跳转前数据能发出去
  // 别用 fetch/axios，可能会被 cancel
  navigator.sendBeacon('/analytics', body);
};

// 监听可交互时间 (LCP)
new PerformanceObserver((entryList) => {
  const entries = entryList.getEntries();
  const lastEntry = entries[entries.length - 1];
  reportWebVital({ name: 'LCP', value: lastEntry.startTime });
}).observe({ type: 'largest-contentful-paint', buffered: true });
```

## 7.2 性能防腐化：把性能当成一种测试

### 1. Performance Budgets (性能预算)
在构建阶段（Build Time）就拦截性能劣化。
*   **配置**：在 webpack 或 vite 配置中设定阈值。
    ```json
    // package.json (使用 size-limit 库)
    "size-limit": [
      {
        "path": "dist/index.js",
        "limit": "150 KB" // 超过就报错，CI 红灯
      }
    ]
    ```

### 2. Lighthouse CI
在 GitLab CI / GitHub Actions 里跑无头浏览器。
*   **Assert**：如果 `performance-score < 90`，不允许 Merge。
*   **Diff**：不仅仅看绝对值，还要对比。比如这次 PR 导致 LCP 增加了 10%，机器人自动评论警告。

## 7.3 总结：性能优化的终局

性能优化是一个**漏斗**模型：
1.  **网络层**：HTTP/2, CDN, Gzip —— 确保资源下得快。
2.  **构建层**：Tree Shaking, SplitChunks —— 确保资源体积小。
3.  **渲染层**：CRP 优化, GPU 合成 —— 确保画得快。
4.  **框架层**：Memo, Virtual List —— 确保交互流畅。
5.  **制度层**：RUM, CI/CD —— 确保不退步。

愿你的页面永远丝般顺滑。
