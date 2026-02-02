# 15. 灵动交互：动画与转场

若 Layout 决定骨架，Paint 决定皮囊，**Animation** 则赋予灵魂。
Flutter 的动画系统强大且分层清晰，从简单的淡入淡出到复杂的物理模拟都能胜任。

## 1. 隐式动画 (Implicit Animations)

这是最简单、最推荐的动画方式。
仅需改变属性值（如 `width`），Flutter 将自动计算差值并播放动画。

*   **关键词**: `AnimatedContainer`, `AnimatedOpacity`, `AnimatedPadding`。
*   **特点**: 无需 `AnimationController`，亦无需 `setState`（除了触发属性变化的那一次）。

```dart
AnimatedContainer(
  duration: Duration(seconds: 1),
  curve: Curves.easeInOut,
  width: selected ? 200.0 : 100.0, // 修改数值自动触发动画
  child: ...
)
```

## 2. 显式动画 (Explicit Animations)

若需更精细的控制（暂停、倒放、无限循环、交错动画）时，需使用显式动画。

*   **核心**: `AnimationController`。
*   **原理**: Controller 在每一帧 V-Sync 信号时生成一个 0.0 到 1.0 的数字，通过 `Tween` 映射成你需要的范围（如 0 到 100 像素），再通过 `AnimatedBuilder` 更新 UI。

```dart
// 1. 定义 Controller
controller = AnimationController(duration: Duration(seconds: 1), vsync: this);
// 2. 定义动画曲线和范围
animation = Tween(begin: 0.0, end: 100.0).animate(controller);
// 3. 构建 UI
AnimatedBuilder(
  animation: animation,
  builder: (ctx, child) => Container(width: animation.value),
)
```

## 3. 英雄动画 (Hero Animations)

在页面跳转时，让共有元素（如列表页的小图 -> 详情页的大图）平滑过渡。
只需要给两个页面的组件加上相同的 `tag`。

```dart
// Page A
Hero(tag: 'avatar_1', child: Image.asset('cat.jpg'))

// Page B
Hero(tag: 'avatar_1', child: Image.network('cat_hd.jpg'))
```

## 4. 物理模拟与 Lottie

*   **SpringSimulation**: 模拟弹簧阻尼效果，让交互更符合物理直觉（如拖拽回弹）。
*   **Lottie**: 支持 AE 动画导出 JSON 并直接渲染。比 GIF 极小，且支持矢量缩放。

## 总结

*   **优先使用隐式动画**：代码量显著降低。
*   **Hero** 是提升 App 质感的捷径。
*   **Rive / Lottie**：复杂矢量动画的最佳伴侣。

> **官方资源**: [Animation & Motion](https://docs.flutter.dev/ui/animations)

