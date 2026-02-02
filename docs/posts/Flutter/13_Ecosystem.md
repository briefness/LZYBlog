# 13. 变现与集成：Ads, IAP & Ecosystem

成功 App 不仅依赖优质代码，更需具备商业化能力。
本篇介绍如何在 Flutter 中变现以及集成 Google 的全家桶生态。

## 1. 广告变现 (Google Mobile Ads)

接入 **AdMob** 是最直接的变现方式。Flutter 官方插件 `google_mobile_ads` 支持多种格式：

### 广告类型
*   **Banner Ads**: 贴在屏幕底部的横幅。实现简单，可以使用 `AdWidget` 直接嵌入 Widget Tree。
*   **Interstitial Ads (插屏)**: 全屏广告，通常在关卡结束时展示。需要预加载 (`load`)，展示时会覆盖当前 UI。
*   **Native Ads (原生广告)**: 最难但体验最好。支持定制广告的字体、颜色、布局，使其自然融入 App 界面。这得益于 Flutter 的 Platform View 技术。

## 2. 应用内购买 (In-App Purchase)

## 2. 应用内购买 (In-App Purchase)

若销售虚拟商品（VIP 会员、游戏金币），必须通过 Apple/Google 的 IAP 通道（否则会被下架）。
插件：`in_app_purchase`。

### 核心流程
IAP 并非简单的 HTTP 请求，而是**离线优先**的事务系统：
1.  **Query Products**: 从商店获取商品信息（价格、本地化描述）。
2.  **Purchase**: 用户发起购买。
3.  **Listen to Stream**: 关键点！必须全生命周期监听 `purchaseStream`。
    *   `pending`: 等待支付。
    *   `purchased`: 支付成功 -> **服务器验单** -> 验单通过 -> 给用户发货 -> **调用 `completePurchase`**。
    *   `error`: 支付失败。

> **警告**: 若未调用 `completePurchase`，商店将认定未发货，并在 3 天后自动退款给用户。

## 3. Firebase 全家桶

Flutter 与 Firebase 均为 Google 旗下产品，结合紧密。

*   **Authentication**: 一行代码搞定 Google/Apple/微信 登录。
*   **Cloud Firestore**: 实时 NoSQL 数据库。不仅存储数据，更支持实时同步（部分即时通讯场景无需独立后端）。
*   **Remote Config**: A/B 测试神器。不发版也能动态修改 App 的文案、颜色、功能开关。
*   **Crashlytics**: 崩溃监控。能捕获 Dart 异常报错堆栈，这对线上稳定性至关重要。

## 4. Google 关键集成

除了 Firebase，Google 还有几张王牌必须掌握：

### Google Maps
使用 `google_maps_flutter`。
它采用 **Platform View** 技术，直接把原生的高性能地图嵌入 Flutter 视图中。
*   支持自定义 Marker, Polyline, Polygon。
*   支持地图样式定制 (JSON Styling)。

### Google Pay / Apple Pay
使用 `pay` 包。
这是转化率最高的支付方式，用户无需输入信用卡号（直接调起系统绑定的卡）。
*   **优点**: 极简流程，指纹确认即支付。
*   **注意**: 这属于“实物商品支付”渠道，不同于 IAP（虚拟商品）。需严格区分，否则将导致审核被拒。

### Google Sign In
使用 `google_sign_in`。
即便拥有一套账号体系，亦**强烈建议**接入。
数据表明，提供 "Sign in with Google" 能显著降低用户的注册门槛，提高转化率。

## 系列结语

从底层的渲染原理，到上层的 AI 智能与商业变现。
期望这 13 篇文章能成为 Flutter 职业生涯的一块垫脚石。

技术在变（Skia -> Impeller, build_runner -> Macros），但核心的工程思想（分层、状态管理、异步模型）是永恒的。

愿代码优雅且具有商业价值。

> **官方资源**: [Monetization](https://flutter.dev/monetization) | [Google Integrations](https://flutter.dev/google-integrations)

