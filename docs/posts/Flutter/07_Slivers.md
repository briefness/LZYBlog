# 07. 滑动的艺术：Slivers 与 Viewport

只要你想做那种“随着滚动缩放头部”或者是“复杂嵌套滚动”的效果，**Slivers** 为必经之路。

开发者常局限于 `ListView`，一旦需求变复杂（比如 GridView 上面接一个 Header），便难以应对。原因在于受限于 Box 协议的世界，未进入 Sliver 协议的领域。

## 两个世界：RenderBox vs RenderSliver

Flutter 有两套独立的布局协议：

1.  **RenderBox (盒子协议)**
    *   **原则**: "Constraints down, Size up".
    *   **特点**: 笛卡尔坐标系 (x, y)，宽高确定。
    *   **代表**: `Container`, `Row`, `Column`。

2.  **RenderSliver (切片协议)**
    *   **原则**: "RenderSliverConstraints down, RenderSliverGeometry up".
    *   **特点**: **按需加载**，无需知晓总长度，仅关注当前视窗显示内容。主轴 (MainAxis) 与 纵轴 (CrossAxis)。
    *   **代表**: `SliverList`, `SliverGrid`, `SliverAppBar`。

`ListView` 本质上就是 `CustomScrollView` + `SliverList` 的封装。

## Viewport：视窗的魔法

Slivers 必须依附于 **Viewport**。
Viewport 如同相框，Slivers 则是无限长卷。

```mermaid
graph TD
    Scrollable[Scrollable (处理手势)] --> Viewport[Viewport (视窗)]
    Viewport --> Center[Shim]
    Viewport --> SliverA[SliverAppBar]
    Viewport --> SliverB[SliverList]
    Viewport --> SliverC[SliverGrid]
```

### RenderSliverConstraints

父级（Viewport）传给 Sliver 的约束不再是 min/max width，而是：
*   `scrollOffset`: 滚动距离。
*   `overlap`: 前序 Sliver 遮挡情况。
*   `remainingPaintExtent`: 剩余绘制空间。

Slivers 根据这些信息，决定自己画哪一部分。这就是 **懒加载 (Lazy Loading)** 的原理：不在视窗内（paintExtent=0）的 Sliver 可不进行绘制。

## 实战：CustomScrollView 的力量

组合不同滚动列表时，避免嵌套 `ListView`（会报错 Vertical viewport was given unbounded height）。
建议使用 `CustomScrollView`：

```dart
CustomScrollView(
  slivers: [
    SliverAppBar(
      expandedHeight: 200.0,
      flexibleSpace: FlexibleSpaceBar(title: Text('Sliver Power')),
      pinned: true, // 核心：吸顶
    ),
    SliverToBoxAdapter(
      child: Container(height: 100, color: Colors.red), // 适配普通 Box 为 Sliver
    ),
    SliverGrid(
      delegate: SliverChildBuilderDelegate(
        (ctx, index) => Card(child: Text('$index')),
        childCount: 20,
      ),
      gridDelegate: SliverGridDelegateWithFixedCrossAxisCount(crossAxisCount: 3),
    ),
    SliverList(
      delegate: SliverChildBuilderDelegate(
        (ctx, index) => ListTile(title: Text('Item $index')),
        childCount: 50,
      ),
    ),
  ],
)
```

## 进阶视角 (Advanced Insight)

### 1. SliverToBoxAdapter 的性能陷阱

`SliverToBoxAdapter` 功能强大，能把任何 Widget 塞进滚动视图。
但注意：**其为一次性 layout 并 paint 的**。
若在 adapter 里放了一个无限长的 Column，或者超大的 Container，无论它是否在屏幕内，它只要被创建，就会消耗资源。对于长列表，建议使用 `SliverList`。

### 2. CacheExtent (预加载区)

Viewport 不仅渲染屏幕内的部分，通常会上下多渲染一点区域（默认约 250px），这叫 `cacheExtent`。
*   **目的**: 确保快速滑动时，新的图片已经准备好了，避免白屏。
*   **优化**: 若 Item 开销巨大（比如视频播放器），建议把 cacheExtent 设小；如果是纯文本，可适当增大。

### 3. KeepAlive 机制

当 Item 滑出屏幕时，Element 一般会被销毁。
若需保留状态（比如输入框里的字），可给该 Item 混入 `AutomaticKeepAliveClientMixin` 并返回 `wantKeepAlive = true`。
Sliver 协议允许把这些“不可见但需保活”的 Slivers 扔到 KeepAlive Bucket 里，暂存内存，而不销毁。
