# 第二部分：网络传输优化 —— 越快越小越好

浏览器渲染页面的前提是拿到 HTML、CSS 和 JS。在这一层，每一毫秒的延迟都源于物理距离和协议开销。我们的目标是战胜 TCP/IP 的物理限制。

## 2.1 HTTP 协议优化：从线头阻塞到多路复用

### 1. 为什么 HTTP/1.1 慢？(底层原理)
除了众所周知的**队头阻塞 (Head-of-Line Blocking)**，还有一个容易被忽视的机制：**TCP 慢启动 (Slow Start)**。
*   **CWND (Congestion Window)**：TCP 连接刚建立时，服务器不敢发太多数据，通常只有 10 个 TCP 段（约 14KB）。只有收到客户端的 ACK 确认后，窗口才会倍增。
*   **影响**：如果你的 `index.html` 有 100KB，它至少需要 4 次 RTT（往返）才能下完。这就是为什么我们要极力控制首屏 HTML 在 **14KB** 以内（Critical Chunk）。

### 2. HTTP/2 的多路复用详解
HTTP/2 引入了 **二进制分帧层 (Binary Framing Layer)**。
*   **可视化想象**：
    *   *HTTP/1.1*：是一条单行道。前车（大图片）坏了，后车（关键 CSS）只能干等。
    *   *HTTP/2*：把大图片切碎成一个个带 ID 的小包裹（Frame），和 CSS 的小包裹在同一条路上混着跑。浏览器收到后根据 ID 重新组装。
*   **Case Study: 某新闻门户**
    *   **问题**：首页有 50+ 张缩略图，导致 CSS 加载被挂起（Pending），首屏样式错乱（FOUC）。
    *   **优化前**：Waterfall 图中看到明显的阶梯状请求（6 个一组）。
    *   **优化后**：开启 HTTP/2。
    *   **结果**：Waterfall 图中 50 个图片请求几乎**同时开始**（Start Time 相同）。LCP 提升 300ms。

### 3. HTTP/3 (QUIC)
解决 TCP 在操作系统内核层面的阻塞。基于 UDP，在用户态实现了可靠传输。对于丢包率高的弱网环境（如电梯、地铁），提升巨大。

## 2.2 缓存策略：多级缓存防线

请求资源的最佳路径：Memory Cache -> Disk Cache -> Service Worker -> CDN -> Origin Server。

### Case Study: 304 Not Modified 的陷阱
**场景**：某 JS 文件配置了协商缓存（Example: `Etag: "v1"`）。
**分析**：虽然 304 没传 Body，但还是要发一次 HTTP 请求去问服务器。这次网络往返（RTT）本身就是开销（可能是 100ms）。
**优化**：对于带 Hash 指纹的静态资源（如 `app.8f9a2b.js`），**完全不应该走协商缓存**，而应该直接走强缓存 `Cache-Control: max-age=31536000, immutable`。
**原理**：`immutable` 指令明确告诉浏览器：“只要指纹没变，这个文件这辈子都不会变，别来烦服务器”。

### Service Worker：不仅是离线
它是一个能够拦截网络请求的 **Programmable Network Proxy**。
```javascript
// sw.js
self.addEventListener('fetch', event => {
  // 甚至可以拦截图片请求，替换成本地占位图，或者做 WebP 自动降级！
  if (/\.jpg$/.test(event.request.url)) {
    event.respondWith(fetch(event.request.url.replace('.jpg', '.webp')));
  }
});
```

## 2.3 CDN 的核心：关键不在“分发”，在“边缘”

### 1. 减少 RTT
光速是有限的。从北京请求纽约的数据，光纤往返最快也要 100ms+。
CDN 将内容推送到离用户只有 5ms 的“家门口”基站。

### 2. 动静分离与动态加速
*   **静态资源**：推送到边缘节点存储。
*   **动态 API**：虽然不能缓存，但可以使用 CDN 的**链路优化**（回源线路优化）。CDN 厂商通常有高质量的专线网络，比公网直连更稳定。

### 3. HTTP/2 Push vs 103 Early Hints
*   **HTTP/2 Push**：那是服务器强塞给你。问题是服务器不知道浏览器缓存里有没有，容易浪费带宽推送重复资源。已被 Chrome 废弃。
*   **103 Early Hints**：HTTP 状态码。服务器在处理 HTML（需要几百毫秒）的同时，先发一个 103 响应，告诉浏览器：“别干等，先去下载 CSS 和 Logo，一会 HTML 就好”。

---

**(下一章预告)**：资源下载回来了，但如果你的 JS 包有 5MB，再快的 5G 也没用。下一章深入构建环节，看 Tree Shaking 如何像园丁一样修剪代码枯枝。
