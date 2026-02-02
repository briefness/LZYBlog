# 06. 迈向专业：工程化与最佳实践入门

构建 Demo 较为简单，但维护一个几万行代码的 Flutter 项目极具挑战。
本篇作为系列的终章，将探讨如何构建“干净”、“健壮”且“高性能”的代码。

## 告别面条代码：分层架构

由于 Flutter 嵌套地狱（Widget Hell）的特性，若将逻辑（Http 请求、数据处理）与 UI 混淆，代码可维护性将显著降低。

建议采用简化的 **Clean Architecture** 分层思想：

```mermaid
graph TD
    UI[UI Layer (Widgets)] --> Logic[Logic Layer (Provider/Bloc)]
    Logic --> Repo[Repository Layer]
    Repo --> Data[Data Layer (API/DB)]
```

### 1. UI Layer (视图层)
*   只负责 `build`。
*   **严禁** 在这里写 HTTP 请求。
*   **严禁** 在这里做复杂的数据转换。
*   只管从 Logic 层拿状态显示，把用户点击事件转发给 Logic 层。

### 2. Logic Layer (逻辑层)
*   State Management 的主战场（ViewModel / Store）。
*   持有 UI 状态。
*   响应 UI 事件，调用 Repository，处理业务逻辑，更新状态。

### 3. 告别 build_runner：Dart Macros

旧版本中，从 JSON 转对象需要用 `json_serializable` 并运行慢吞吞的 `build_runner`。
现在，Dart 3.x 引入了 **Macros (宏)**。

```dart
// 新写法：没有 .g.dart 文件，没有 build_runner
@JsonCodable()
class User {
  final String name;
  final int age;
}

// 编译器会在编译时自动生成 toJson/fromJson，零等待。
```

### 4. 长列表的内存杀手

使用 `ListView.builder` 而不是 `ListView(children: [...])`。
*   `ListView.builder`: 懒加载。仅渲染当前视窗可见的 Item。
*   `ListView(children: ...)`: 一次性构建所有 Item。若包含大量 Item，将导致内存激增。

### 5. Repository Layer (仓库层)
*   **数据的单一信源**。
*   UI 与 Logic 无需关注数据来源细节，Repository 应负责屏蔽差异。
*   提供干净的数据接口，如 `Future<User> getUser()`。

## 6. 导航策略：GoRouter

在多页面应用中，除了数据分层，**路由管理**至关重要。
建议弃用原生的 `Navigator.push`，拥抱声明式路由 **GoRouter**。

*   **URL 驱动**: 每個页面都有 URL（如 `/users/123`），完美支持 Web 和 Deep Link。
*   **重定向**: 支持顶层处理登录守卫（Guard）。

```dart
final router = GoRouter(
  initialLocation: '/home',
  routes: [
    GoRoute(path: '/home', builder: (_, __) => HomePage()),
    GoRoute(
      path: '/details/:id',
      builder: (context, state) => DetailsPage(id: state.pathParameters['id']!),
    ),
  ],
  redirect: (context, state) {
    // 全局守卫：没登录就踢去登录页
    if (!isLoggedIn) return '/login';
    return null;
  },
);
```

## 性能优化进阶 (Advanced Performance)

之前的“黄金法则”只是入门，真正的高性能需要理解引擎的渲染成本。


### 1. 渲染层级的双刃剑：`RepaintBoundary`

你可能听过“用 `RepaintBoundary` 隔离频繁变化的组件”，但你知道为什么吗？以及它的代价是什么？

*   **原理**: `RepaintBoundary` 会强制其子树创建一个独立的 `Layer` (PictureLayer)。
*   **收益**: 当子树重绘时，Pipeline 只需要更新这个 Layer 的绘制指令，而不需要重绘父级 Layer。复合 (Composite) 阶段会将这些 Layer 合成。
*   **代价**: 每个 Layer 都需要 GPU 显存。如果你给每个 Item 都包一个 RepaintBoundary，显存会爆炸，反而导致 GPU 抖动。
*   **最佳场景**: 只有当**频繁重绘的区域**（如进度条、秒表）与**静态背景**重叠时，才使用。

### 2. 隐形杀手：`saveLayer` 与 Offscreen Rendering

有些 Widget 会在底层触发 `Canvas.saveLayer()`，这会导致 GPU 进行**离屏渲染 (Off-screen Rendering)**。
流程是：GPU 分配一块新缓冲区 -> 切换 Context -> 渲染内容 -> 切回主缓冲区 -> 混合。这极其昂贵。

*   **触发者**:
    *   `Opacity` (尤其是非 0.0 或 1.0 的透明度)。
    *   `ShaderMask`。
    *   `ClipRRect` (圆角裁剪，视具体情况而定)。
*   **优化方案**:
    *   能用 `Container(color: Colors.black.withOpacity(0.5))` 就别用 `Opacity` Widget。
    *   图片圆角：尽量让设计切带圆角的图，或者使用 `ClipPath` 代替复杂的 `ClipRRect`。

### 3. 图片内存优化

Flutter 默认会解码图片的**原尺寸**。
如果你展示一个 100x100 的头像，但网络图片是 4000x3000 的高清图，Flutter 会把整张 4000x3000 的图解码到内存中，占用几十 MB。

*   **解法**: 使用 `cacheWidth` / `cacheHeight`。

```dart
Image.network(
  url,
  cacheWidth: 150, // 告诉引擎：解码成 150 宽就行了，别解全图
)
```

### 4. 复用昂贵子树：GlobalKey

当 Widget 从 Element Tree 的一个位置移动到另一个位置时（例如移除 Loading 页面，显示主内容，但主内容里有个复杂的视频播放器不想重建），默认会销毁并重建。

*   **解法**: 给该 Widget 一个 `GlobalKey`。
*   **原理**: `GlobalKey` 把 Element 存到了一个全局 Map 中。当 Tree 发生变化时，如果发现 Key 匹配，直接把那个 Element (及其 RenderObject) 嫁接过来，完全跳过 Build/Layout/Paint，只做 Composite。
*   **代价**: `GlobalKey` 也很昂贵，不要滥用。

### 5. 列表性能：RelayoutBoundary

当列表中的一个 Item 尺寸改变时，是否会触发整个列表甚至页面的 Layout？
取决于该 Item 是否 是 **RelayoutBoundary**。

*   **规则**: 如果一个 RenderObject 的尺寸完全由父级决定（Tight Constraints），或者它的尺寸变化不会影响父级尺寸，那么它就是 RelayoutBoundary。
*   **优化**: 给 Item 固定宽高（如果可能），阻断 Layout 脏链向上传播。


## 错误处理与日志

避免仅依赖 `print()`。在生产环境，`print` 既影响性能且容易丢。

建议封装 LogUtil：
*   开发模式 (Debug): `print` 到控制台。
*   生产模式 (Release): 上报到 Sentry / Firebase Crashlytics，或者直接静默。

同时，利用 `FlutterError.onError` 和 `runZonedGuarded` 捕获全局未处理异常。

```dart
void main() {
  runZonedGuarded(() {
    runApp(MyApp());
  }, (error, stackTrace) {
    // 上报崩溃信息到服务器
    reportError(error, stackTrace);
  });
}
```

## 系列结语

至此，Flutter 深入浅出之旅暂告一段落。

1.  从 **架构** 出发，解析 **三棵树** 的协作。
2.  阐述了 **Constraints** 传递的布局奥义。
3.  剖析了 **渲染管线** 的各个环节。
4.  梳理了 **状态** 的流动与管理。
5.  明确了 **单线程** 下的异步模型。
6.  最终通过 **分层** 与 **规范** 实现工程化。

Flutter 不仅仅是一个画 UI 的工具，它是一套极其精密且优雅的现代 GUI 系统。理解这些原理，不仅仅是编写代码，更是在设计系统。

Happy Coding!
