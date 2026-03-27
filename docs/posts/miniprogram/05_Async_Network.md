# 05. 异步编程：wx.request 与网络请求封装

小程序的网络请求 API `wx.request()` 基于回调模式，不支持 Promise。直接用回调写业务逻辑，很快就会陷入"回调地狱"——请求嵌套请求，错误处理散落各处，代码难以维护。

本篇的目标是：**把 wx.request 封装成一套完整的请求层**，包括 Promise 化、拦截器、自动管理 Token、错误统一处理。

> **环境：** 微信开发者工具 latest，小程序基础库 3.x

---

## 1. wx.request 基础回顾

### 1.1 基本用法

```javascript
wx.request({
  url: 'https://api.example.com/users',
  method: 'GET',
  data: { page: 1, size: 20 },
  header: {
    'content-type': 'application/json',
    'Authorization': 'Bearer ' + token,
  },
  success(res) {
    // res.statusCode: HTTP 状态码
    // res.data: 后端返回数据
    // res.header: 响应头
    if (res.statusCode === 200) {
      console.log('数据：', res.data);
    }
  },
  fail(err) {
    // 网络错误或请求被拦截
    console.error('请求失败：', err);
  },
  complete() {
    // 无论成功失败都会执行（类似 finally）
    wx.hideLoading();
  },
});
```

### 1.2 wx.request 的限制

```javascript
// 小程序请求有严格的安全限制：

// 1. 域名必须备案，且在小程序后台添加（开发阶段可关闭校验）
wx.request({
  url: 'https://api.example.com/data',
  // project.config.json 中设置 "urlCheck": false 可临时绕过
});

// 2. 单次请求超时时间（默认 60s）
wx.request({
  url: '...',
  timeout: 30000, // 30 秒超时
});

// 3. 并发请求数量限制（iOS 5个、Android 10个）
// 超出限制的请求会排队等待

// 4. POST 请求默认 content-type 是 application/x-www-form-urlencoded
// 如需 JSON，需要显式设置
wx.request({
  method: 'POST',
  header: { 'content-type': 'application/json' },
  data: JSON.stringify({ name: '张三', age: 18 }),
});
```

---

## 2. Promise 封装：告别回调地狱

### 2.1 基础 Promise 封装

```javascript
// utils/request.js

/**
 * Promise 化的 wx.request
 * @param {Object} options - 同 wx.request 参数
 * @returns {Promise}
 */
const request = (options) => {
  return new Promise((resolve, reject) => {
    wx.request({
      ...options,
      success: (res) => {
        if (res.statusCode >= 200 && res.statusCode < 300) {
          resolve(res.data);
        } else {
          reject(res);
        }
      },
      fail: (err) => {
        reject(err);
      },
    });
  });
};

export default request;
```

### 2.2 带错误码统一处理

```javascript
// utils/request.js

const CODE_SUCCESS = 0;
const CODE_UNAUTHORIZED = 401;

const request = (options) => {
  return new Promise((resolve, reject) => {
    wx.request({
      ...options,
      success: (res) => {
        const { statusCode, data } = res;

        if (statusCode >= 200 && statusCode < 300) {
          // 假设后端返回格式为 { code, data, message }
          if (data.code === CODE_SUCCESS) {
            resolve(data.data);
          } else if (data.code === CODE_UNAUTHORIZED) {
            // Token 过期，跳转登录
            handleUnauthorized();
            reject(data);
          } else {
            // 业务错误
            reject(data);
          }
        } else {
          reject({ message: `HTTP ${statusCode} 错误`, res });
        }
      },
      fail: (err) => {
        wx.showToast({
          title: '网络连接失败',
          icon: 'none',
          duration: 2000,
        });
        reject({ message: '网络错误', err });
      },
    });
  });
};

// 统一的未授权处理
const handleUnauthorized = () => {
  wx.removeStorageSync('token');
  wx.redirectTo({ url: '/pages/login/login' });
};

export default request;
```

---

## 3. 请求拦截器：全局 Loading + Token 注入

### 3.1 请求拦截器

```javascript
// utils/http.js

/**
 * 请求配置
 */
const config = {
  baseURL: 'https://api.example.com',
  timeout: 30000,
};

/**
 * 通用请求方法
 * @param {string} url - 请求路径
 * @param {Object} options - 请求选项
 */
const http = (url, options = {}) => {
  return new Promise(async (resolve, reject) => {
    // ========== 请求拦截：构建完整配置 ==========
    const token = wx.getStorageSync('token');
    const header = {
      'content-type': 'application/json',
      ...options.header, // 允许外部覆盖
    };

    // 自动注入 Token（如果有）
    if (token) {
      header['Authorization'] = `Bearer ${token}`;
    }

    // 全局 Loading（可选）
    if (options.showLoading !== false) {
      wx.showLoading({ title: '加载中...', mask: true });
    }

    const requestOptions = {
      url: url.startsWith('http') ? url : config.baseURL + url,
      method: options.method || 'GET',
      data: options.data || {},
      header,
      timeout: options.timeout || config.timeout,
    };

    // ========== 发起请求 ==========
    wx.request({
      ...requestOptions,
      success: (res) => {
        wx.hideLoading();

        // ========== 响应拦截：处理业务错误 ==========
        if (res.statusCode === 200) {
          const { code, data, message } = res.data;
          if (code === 0) {
            resolve(data);
          } else if (code === 401) {
            // Token 过期
            handleUnauthorized();
            reject({ code, message });
          } else {
            // 业务错误，显示后端返回的消息
            if (options.showError !== false) {
              wx.showToast({ title: message || '请求失败', icon: 'none' });
            }
            reject({ code, message });
          }
        } else {
          wx.showToast({ title: `服务器错误 (${res.statusCode})`, icon: 'none' });
          reject({ statusCode: res.statusCode });
        }
      },
      fail: (err) => {
        wx.hideLoading();
        wx.showToast({ title: '网络异常', icon: 'none' });
        reject({ message: '网络请求失败', err });
      },
    });
  });
};

// ========== 快捷方法 ==========
export const get = (url, data, options = {}) => {
  return http(url, { method: 'GET', data, ...options });
};

export const post = (url, data, options = {}) => {
  return http(url, { method: 'POST', data, ...options });
};

export const put = (url, data, options = {}) => {
  return http(url, { method: 'PUT', data, ...options });
};

export const del = (url, data, options = {}) => {
  return http(url, { method: 'DELETE', data, ...options });
};

export default http;
```

### 3.2 使用方式

```javascript
// pages/index/index.js
import { get, post } from '../../utils/http.js';

Page({
  data: {
    list: [],
    loading: false,
  },

  onLoad() {
    this.fetchList();
  },

  async fetchList() {
    this.setData({ loading: true });
    try {
      const data = await get('/api/users', { page: 1, size: 20 });
      this.setData({ list: data.list });
    } catch (err) {
      console.error('获取列表失败', err);
    } finally {
      this.setData({ loading: false });
    }
  },

  async submitForm() {
    try {
      const result = await post('/api/submit', {
        name: '张三',
        age: 18,
      });
      wx.showToast({ title: '提交成功' });
    } catch (err) {
      console.error('提交失败', err);
    }
  },
});
```

---

## 4. 异步请求的时序图

```mermaid
sequenceDiagram
    participant Page as 页面逻辑
    participant HTTP as http 请求层
    participant WX as wx.request
    participant Server as 后端服务器
    participant UI as 界面更新

    Page->>HTTP: await get('/api/users')
    HTTP->>WX: wx.request({ url, header })
    WX->>Server: HTTP GET /api/users
    Server-->>WX: HTTP 200 + JSON
    WX->>HTTP: success callback
    HTTP->>HTTP: 响应拦截：检查 code
    HTTP-->>Page: resolve(data)
    Page->>UI: this.setData({ list: data })
    UI-->>Page: 页面重新渲染
```

---

### 可视化：异步网络请求完整时序

下面通过图示展示 `wx.request` 异步请求的完整流程。

#### 请求流程架构图

```mermaid
flowchart LR
    P["Page\n(页面逻辑)"] --> WX["wx.request\n(微信API)"]
    WX --> S["Backend\nServer"]
    S --> CB["Callback\n回调处理"]
    CB --> UI["UI 更新\nsetData"]

    style P fill:#42A5F5,stroke:#1976D2,color:#fff
    style WX fill:#07C160,stroke:#06ad57,color:#fff
    style S fill:#FF6B6B,stroke:#ee5a5a,color:#fff
    style CB fill:#FFA726,stroke:#f57c00,color:#fff
    style UI fill:#9B59B6,stroke:#8e44ad,color:#fff
```

#### 请求时序图

```mermaid
sequenceDiagram
    participant P as Page
    participant WX as wx.request
    participant S as Backend Server
    participant CB as Callback
    participant UI as UI 更新

    P->>P: setData({ loading: true })
    P->>WX: 调用 wx.request()
    Note over WX: 微信 API 封装请求

    WX->>S: HTTP GET /api/users
    Note over S: 后端处理并返回 JSON

    S-->>WX: HTTP 200 + JSON
    WX->>WX: success callback 触发

    WX->>CB: 数据解析 + 错误处理
    CB-->>P: resolve(data)

    P->>UI: this.setData({ list: data })
    UI-->>P: 页面重新渲染
```

#### 完整请求流程动画

下方演示 `wx.request` 的完整请求过程：

```html
<div class="async-demo">
  <div class="demo-title">wx.request 异步请求流程</div>

  <div class="flow-nodes">
    <div class="flow-node" id="fn-page">
      <div class="node-icon">📱</div>
      <div class="node-name">Page</div>
      <div class="node-desc">页面逻辑</div>
    </div>
    <div class="flow-arrow" id="fa1">→</div>
    <div class="flow-node" id="fn-wx">
      <div class="node-icon">🔧</div>
      <div class="node-name">wx.request</div>
      <div class="node-desc">微信 API</div>
    </div>
    <div class="flow-arrow" id="fa2">→</div>
    <div class="flow-node" id="fn-server">
      <div class="node-icon">🖥️</div>
      <div class="node-name">Backend</div>
      <div class="node-desc">后端服务器</div>
    </div>
    <div class="flow-arrow" id="fa3">↓</div>
    <div class="flow-node" id="fn-cb" style="grid-column: 2;">
      <div class="node-icon">📋</div>
      <div class="node-name">Callback</div>
      <div class="node-desc">回调处理</div>
    </div>
    <div class="flow-arrow" id="fa4">←</div>
    <div class="flow-node" id="fn-ui" style="grid-column: 3;">
      <div class="node-icon">🎨</div>
      <div class="node-name">UI 更新</div>
      <div class="node-desc">页面渲染</div>
    </div>
  </div>

  <div class="log-panel">
    <div class="log-title">执行日志</div>
    <div class="log-content" id="asyncLog"></div>
  </div>

  <div class="controls">
    <button class="btn" onclick="asyncStep()">▶ 下一步</button>
    <button class="btn" onclick="asyncPlay()">⏵ 自动播放</button>
    <button class="btn" onclick="asyncReset()">↺ 重置</button>
  </div>
</div>

<style>
.async-demo {
  background: #1a1a2e;
  border-radius: 12px;
  padding: 24px;
  font-family: 'SF Mono', 'Fira Code', monospace;
  color: #e0e0e0;
  max-width: 700px;
  margin: 0 auto;
}
.demo-title {
  text-align: center;
  font-size: 16px;
  color: #ffd700;
  margin-bottom: 20px;
}
.flow-nodes {
  display: grid;
  grid-template-columns: 1fr auto 1fr auto 1fr;
  grid-template-rows: auto auto;
  align-items: center;
  gap: 8px;
  margin-bottom: 20px;
}
.flow-node {
  background: #16213e;
  border: 2px solid #0f3460;
  border-radius: 10px;
  padding: 14px 12px;
  text-align: center;
  transition: all 0.4s ease;
}
.node-icon { font-size: 24px; margin-bottom: 6px; }
.node-name { font-size: 13px; font-weight: bold; color: #cdd6f4; margin-bottom: 2px; }
.node-desc { font-size: 11px; color: #6c7086; }
.flow-arrow {
  font-size: 20px;
  color: #4a4a6a;
  text-align: center;
  transition: all 0.3s;
}
#fa3 {
  grid-column: 2;
  writing-mode: vertical-rl;
  text-orientation: mixed;
}
#fa4 { grid-column: 3; }
.flow-node.active {
  border-color: #ffd700;
  background: #2a2a4a;
  box-shadow: 0 0 20px rgba(255, 215, 0, 0.3);
  transform: scale(1.05);
}
.flow-node.done {
  border-color: #00ff88;
  background: #0a3d2a;
}
.flow-node.done .node-name { color: #00ff88; }
.flow-arrow.active {
  color: #ffd700;
  text-shadow: 0 0 8px rgba(255, 215, 0, 0.5);
}
.log-panel {
  background: #0d1117;
  border: 1px solid #30363d;
  border-radius: 8px;
  padding: 12px;
  max-height: 100px;
  overflow-y: auto;
  margin-bottom: 16px;
}
.log-title { font-size: 12px; color: #6c7086; margin-bottom: 8px; }
.log-entry {
  font-size: 12px;
  line-height: 1.6;
  opacity: 0;
  animation: fadeIn 0.3s forwards;
  color: #cdd6f4;
}
.log-entry .phase { color: #ffd700; font-weight: bold; }
.log-entry .result { color: #00ff88; }
@keyframes fadeIn { to { opacity: 1; } }
.controls {
  display: flex;
  justify-content: center;
  gap: 12px;
}
.btn {
  background: #4a4a6a;
  border: none;
  color: #fff;
  padding: 8px 20px;
  border-radius: 6px;
  cursor: pointer;
  font-family: inherit;
  font-size: 13px;
  transition: background 0.2s;
}
.btn:hover { background: #6a6a8a; }
</style>

<script>
const asyncSteps = [
  { node: 'fn-page', arrow: null, log: '<span class="phase">[Page]</span> setData({ loading: true }) — 显示加载中' },
  { node: 'fn-wx', arrow: 'fa1', log: '<span class="phase">[API]</span> 调用 wx.request() — 发起网络请求' },
  { node: 'fn-server', arrow: 'fa2', log: '<span class="phase">[Server]</span> 后端接收请求，处理并返回 JSON' },
  { node: 'fn-cb', arrow: 'fa3', log: '<span class="phase">[Callback]</span> success 回调触发 — 数据解析 + 错误处理' },
  { node: 'fn-ui', arrow: 'fa4', log: '<span class="phase">[UI]</span> this.setData() — 页面重新渲染，数据显示完成' },
];
let asyncIdx = 0;
let asyncTimer = null;

function asyncActivate(idx) {
  if (idx < 0 || idx >= asyncSteps.length) return;
  const s = asyncSteps[idx];
  if (s.arrow) document.getElementById(s.arrow).classList.add('active');
  document.getElementById(s.node).classList.add('active');
  const log = document.getElementById('asyncLog');
  log.innerHTML += `<div class="log-entry">${s.log}</div>`;
  log.scrollTop = log.scrollHeight;
  setTimeout(() => {
    document.getElementById(s.node).classList.remove('active');
    document.getElementById(s.node).classList.add('done');
    if (s.arrow) document.getElementById(s.arrow).classList.remove('active');
  }, 600);
}

function asyncStep() {
  if (asyncTimer) { clearTimeout(asyncTimer); asyncTimer = null; }
  asyncActivate(asyncIdx);
  asyncIdx++;
  if (asyncIdx >= asyncSteps.length) asyncIdx = 0;
}

function asyncPlay() {
  if (asyncTimer) { clearTimeout(asyncTimer); asyncTimer = null; }
  asyncIdx = 0;
  document.querySelectorAll('.flow-node, .flow-arrow').forEach(n => n.classList.remove('active','done'));
  document.getElementById('asyncLog').innerHTML = '';
  function next() {
    if (asyncIdx >= asyncSteps.length) { asyncIdx = 0; return; }
    asyncActivate(asyncIdx);
    asyncIdx++;
    asyncTimer = setTimeout(next, 1400);
  }
  next();
}

function asyncReset() {
  if (asyncTimer) { clearTimeout(asyncTimer); asyncTimer = null; }
  asyncIdx = 0;
  document.querySelectorAll('.flow-node, .flow-arrow').forEach(n => n.classList.remove('active','done'));
  document.getElementById('asyncLog').innerHTML = '';
}
</script>
```

> **说明**：点击「下一步」逐步演示 wx.request 异步请求的完整流程；Promise 封装可以让回调写法更优雅。

---

## 6. 常见网络相关 API 补充

### 6.1 文件上传与下载

```javascript
// 上传文件
wx.chooseImage({
  count: 1,
  success(res) {
    const filePath = res.tempFilePaths[0];
    wx.uploadFile({
      url: 'https://api.example.com/upload',
      filePath,
      name: 'file',
      header: { Authorization: `Bearer ${token}` },
      success(res) {
        const data = JSON.parse(res.data);
        console.log('上传成功：', data.url);
      },
    });
  },
});

// 下载文件
wx.downloadFile({
  url: 'https://example.com/image.jpg',
  success(res) {
    // res.tempFilePath: 临时文件路径
    wx.saveImageToPhotosAlbum({
      filePath: res.tempFilePath,
      success() {
        wx.showToast({ title: '保存成功' });
      },
    });
  },
});
```

### 6.2 WebSocket 实时通信

```javascript
// 建立连接
wx.connectSocket({
  url: 'wss://api.example.com/ws',
  header: { Authorization: `Bearer ${token}` },
});

// 监听消息
wx.onSocketMessage((res) => {
  console.log('收到消息：', res.data);
  const data = JSON.parse(res.data);
  // 处理实时消息
});

// 发送消息
wx.sendSocketMessage({
  data: JSON.stringify({ type: 'ping' }),
});

// 断开连接
wx.closeSocket();
```

---

## 7. 常见坑点

**1. 请求参数 data 未序列化**

```javascript
// 错误：POST JSON 时没序列化
wx.request({
  method: 'POST',
  data: { name: '张三' }, // 默认被序列化为 key=value&key=value
});

// 正确：指定 content-type + 序列化
wx.request({
  method: 'POST',
  data: JSON.stringify({ name: '张三' }),
  header: { 'content-type': 'application/json' },
});
```

**2. 在真机上请求失败，但开发者工具正常**

```javascript
// 原因一：域名未备案或未添加到后台
// 解决：开发阶段在 project.config.json 设置 urlCheck: false

// 原因二：TLS 版本不兼容（Android 要求 TLS 1.2+）
// 解决：服务端升级 TLS 配置

// 原因三：使用了 HTTP（非 HTTPS）
// 解决：微信基础库 2.0+ 禁止非 HTTPS 请求（开发阶段可关闭）
```

**3. 请求并发超限导致队列阻塞**

```javascript
// 错误：一次性发 20 个请求
Promise.all([
  get('/api/1'), get('/api/2'), get('/api/3'),
  get('/api/4'), get('/api/5'), get('/api/6'),
  // ... 共 20 个
]);

// 正确：分批并发，最多 5-10 个
const chunks = arrayChunk(items, 5);
for (const chunk of chunks) {
  await Promise.all(chunk.map(item => get(`/api/${item.id}`)));
}
```

**4. onLoad 中同时发起多个请求，只处理部分返回**

```javascript
// 错误：竞态条件
onLoad() {
  this.fetchUser();   // 异步，不知道何时完成
  this.fetchConfig(); // 异步，不知道何时完成
  // data 中的 user 和 config 可能都还没准备好
}

// 正确：用 Promise.all 等待所有请求完成
async onLoad() {
  try {
    const [user, config] = await Promise.all([
      get('/api/user'),
      get('/api/config'),
    ]);
    this.setData({ user, config });
  } catch (err) {
    console.error(err);
  }
}
```

---

## 延伸思考

请求封装的设计，本质上是在"便利性"和"可控性"之间做权衡。

完全不用封装，直接裸调用 `wx.request`，代码可读性差、错误处理重复、Token 管理散落。过度封装（引入 axios-like 的完整拦截器系统），在小程序的受限环境下又过于重量，而且小程序不支持标准 npm axios（因为 axios 底层用 XMLHttpRequest）。

实践中，**拦截器 + Promise 化 + 统一错误处理** 这三件事就够了，复杂的请求取消、请求重试、缓存策略，在小程序场景下不是核心需求。

---

## 总结

- `wx.request` 基于回调，Promise 封装是工程化的第一步
- 响应拦截器负责统一处理 `code !== 0` 的业务错误
- 请求拦截器统一注入 `Authorization` Token 和展示 Loading
- `Promise.all` 可解决多请求竞态问题
- 小程序请求有域名白名单、TLS 版本、并发数量等限制

---

## 参考

- [wx.request 官方文档](https://developers.weixin.qq.com/miniprogram/dev/api/network/request/wx.request.html)
- [网络请求使用说明](https://developers.weixin.qq.com/miniprogram/dev/framework/ability/network.html)
- [wx.connectSocket WebSocket](https://developers.weixin.qq.com/miniprogram/dev/api/network/websocket/wx.connectSocket.html)

---

**下一篇**进入 **数据流与状态管理：Page Data 的正确姿势**——跨页面通信、全局 Store、组件间数据流。
