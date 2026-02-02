# 12. 游戏开发：Flame 与 Casual Toolkit

Flutter 不仅仅能做 App。凭借其高性能的 Skia/Impeller 渲染引擎，它在 2D 游戏开发领域也占据了一席之地。

## 1. 为什么用 Flutter 做游戏？

*   **跨平台**: 写一次，发布到 iOS, Android, Web, Desktop。
*   **UI 强项**: 游戏的菜单、设置页、排行榜，用 Flutter Widget 写比用 Unity GUI 快十倍。
*   **生态**: 可以无缝接入 AdMob, Firebase, IAP。

## 2. 两条路线

### 路线 A: Casual Games Toolkit (轻量级)

若开发**数独、填字、卡牌、2048** 这种非动作类游戏，则无需游戏引擎。
直接使用 Flutter 标准组件 (`Stack`, `AnimatedPositioned`, `GestureDetector`) 即可。

Google 官方推出的 **Casual Games Toolkit** 提供了一套模板，包含：
*   音频管理 (AudioPlayers)。
*   主菜单与设置页。
*   集成好的 AdMob 和 Game Center。
*   Crashlytics 监控。

### 路线 B: Flame Engine (专业级)

若开发**马里奥、坦克大战、RPG** 这种需要物理碰撞、粒子效果、复杂精灵动画的游戏，需引入 **Flame**。

#### Game Loop (游戏循环)
App 为**事件驱动** (Event Driven)，响应式执行。
Flame 为**帧驱动** (Frame Driven / Game Loop)，逐帧执行高频计算：`update()` -> `render()`。

```dart
class MyGame extends FlameGame {
  @override
  void update(double dt) {
    //每一帧更新位置：位置 = 速度 * 时间差
    player.position += player.velocity * dt;
  }
}
```

#### 核心组件 (ECS 系统)
*   **Component**: 游戏里的所有东西（人、树、子弹）都是 Component。
*   **Sprite**: 精灵图（角色的贴图）。
*   **Forge2D**: 物理引擎（重力、摩擦力、碰撞回弹）。
*   **Parallax**: 视差背景（背景移动慢，前景移动快）。

## 3. 混合开发 (Hybrid)

Flutter 游戏开发的核心优势在于：**Game Widget 和普通 Widget 可以共存**。

可在同一页面内混合使用 `GameWidget` (Flame 渲染的游戏区域) 与常规 Widget（如 `Row`，包含三个 `ElevatedButton` 控制攻击/跳跃）。
这使得“游戏逻辑”和“UI 交互”完美分离，发挥各自的特长。

## 4. 游戏服务 (Game Services)

开发游戏仅为第一步，留住玩家需要社交。
无需自行构建服务器来实现排行榜。

*   **Games Services**: 使用 `games_services` 包，一键接入 iOS Game Center 和 Android Play Games。
    *   **Leaderboards (排行榜)**: 全球排名，好友排名。
    *   **Achievements (成就系统)**: "首杀"、"百人斩" 弹出徽章。
*   **Multiplayer (联机对战)**:
    *   简单的回合制（如五子棋）可以用 **Firebase Realtime Database**。
    *   实时动作类（如吃鸡）推荐接入 **Nakama** (开源游戏后端) 或 **Agones** (K8s 游戏服托管)。

## 总结

*   **工具类/棋牌类**: 选 Casual Games Toolkit (纯 Flutter Widget)。

*   **动作/射击/RPG**: 选 Flame (Game Loop + Physics)。
*   无论选择何种方案，均可享受到 Dart 语言带来的开发效率红利。

> **官方资源**: [Flutter Games](https://flutter.dev/games)

