# 鸿蒙开发进阶（七）：独有交互体验 (Unique Interactions)

> 🔗 **项目地址**：[https://github.com/briefness/HarmonyDemo](https://github.com/briefness/HarmonyDemo)

HarmonyOS 与 Android/iOS 最大的区别在于其独特的多设备交互和智慧感知能力。
本章将深入探讨鸿蒙独有的“黑科技”交互：**闪控球 (Flash Control Ball)**、**隔空手势/智感握姿 (Smart Sensing)** 以及 **碰一碰 (OneHop)**。

## 一、闪控球 (Flash Control Ball)

闪控球是一种系统级的悬浮交互形态，允许应用以小窗形式悬浮在屏幕边缘，随时呼出。常用于抢单、比价、即时笔记等场景。

### 1.1 核心 API

使用 `ohos.window.floatingBall` 模块管理闪控球。

### 1.2 开发步骤

1.  **权限申请**：配置 `ohos.permission.USE_FLOAT_BALL`。
2.  **创建控制器**：

```typescript
import { floatingBall } from '@kit.ArkUI';
import { BusinessError } from '@kit.BasicServicesKit';

// 检查是否支持
if (floatingBall.isFloatingBallSupported()) {
  floatingBall.create((err: BusinessError, controller: floatingBall.FloatingBallController) => {
    if (err) {
      console.error(`Failed to create: ${err.message}`);
      return;
    }
    
    // 启动闪控球
    controller.show({
      icon: $r('app.media.ball_icon'), // 自定义图标
      bubbleContent: '抢单中...',    // 气泡文字
      onClick: () => {
        console.info('Flash Ball clicked!');
        // 可以在这里拉起应用主界面
      }
    });
  });
}
```

> **⚠️ 开发注意**：
> 1.  **权限限制**：`ohos.permission.USE_FLOAT_BALL` 和系统级悬浮窗属于**特权权限**。AppGallery 对第三方普通应用申请此权限审核非常严格。
> 2.  **最佳实践**：对于大多数“后台任务可视化”场景（如打车、外卖、录音），官方推荐使用 **实况窗 (Live View Kit)** 而非自行创建悬浮球。实况窗能以标准化的胶囊/卡片形态展示在状态栏和锁屏，体验更佳且符合规范。
> 3.  **演示说明**：Demo 代码中通常是在应用内模拟悬浮效果（例如使用 `Stack` 布局），而非调用受限的系统 API。


## 二、智感与隔空交互 (Multimodal Awareness)

HarmonyOS 的 **MultimodalAwarenessKit** (多模态感知服务) 赋予了设备“感知”用户的能力。

### 2.1 智感握姿 (Intelligent Grip)

识别用户是左手握持、右手握持，还是平放。这对于优化单手操作界面至关重要。

```typescript
import { motion } from '@kit.MultimodalAwarenessKit';

// 订阅握姿变化
motion.on('holdingHandChanged', (hand: motion.Hand) => {
  if (hand === motion.Hand.LEFT) {
    // 调整 UI 按钮到左侧
    this.buttonAlign = Alignment.BottomStart;
  } else if (hand === motion.Hand.RIGHT) {
    // 调整 UI 按钮到右侧
    this.buttonAlign = Alignment.BottomEnd;
  }
});
```

### 2.2 隔空手势 (Air Gestures)

通过前置摄像头识别用户的手势（如挥手、抓取），实现免接触操作。常用于烹饪、吃饭等不方便触碰屏幕的场景。

> **注意**：该功能高度依赖硬件支持（通常需要 ToF 摄像头或专用传感器）。

## 三、碰一碰 (OneHop / NFC)

“碰一碰”是 HarmonyOS 分布式能力的标志性交互。利用 NFC 瞬间拉起原子化服务或传输数据。

### 3.1 场景

*   **设备配网**：手机碰路由器，直接连 WiFi。
*   **内容接续**：手机查看的文档，碰一下 MatePad 继续编辑。
*   **服务直达**：碰一下商家标签，直接拉起点餐小程序。

### 3.2 实现原理

核心是 **Product ID** 与 **NFC 标签** 的绑定。

1.  **标签写入**：将特定格式的 URI 写入 NFC 标签。
    *   URI 格式: `https://hapjs.org/app/<package_name>`
2.  **应用处理**：
    在 `EntryAbility` 的 `onCreate` 或 `onNewWant` 中解析 NFC 传递的参数。

```typescript
import { Want } from '@kit.AbilityKit';

export default class EntryAbility extends UIAbility {
  onNewWant(want: Want) {
    // 检查是否由 NFC 触发
    if (want.parameters?.['ohos.extra.param.key.nfc_tag']) {
      console.info('Launched by OneHop!');
      // 解析业务数据，跳转到指定页面
    }
  }
}
```

## 四、实况窗 (Live View)

虽然类似 iOS 的灵动岛，但 HarmonyOS 的实况窗更强调**任务的连续性**。
通过 **Live View Kit**，应用可以将外卖进度、打车距离等实时信息展示在左上角或胶囊位置。

| 特性 | 闪控球 (Flash Ball) | 实况窗 (Live View) |
| :--- | :--- | :--- |
| **定位** | 悬浮小窗，强调交互操作 | 状态栏胶囊/卡片，强调信息展示 |
| **场景** | 抢单、笔记、侧边栏工具 | 打车、外卖、录音、通话 |
| **权限** | 特权权限 (USE_FLOAT_BALL) | 后台运行权限 (Background) |
| **推荐度** | ⚠️ 低 (审核严格，不推荐普通应用) | ✅ 高 (官方推荐的标准形态) |

> **👉 提示**：实况窗的详细开发实战（LiveViewKit）将在下一章 **[智慧功能 (Smart Features)](./SmartFeatures.md)** 中专门讲解。


## 五、总结

HarmonyOS 的交互不仅仅局限于屏幕内的点击和滑动：
*   **空间延伸**：通过隔空手势和闪控球，打破了屏幕边界。
*   **设备延伸**：通过碰一碰，打破了设备边界。
*   **感知延伸**：通过智感握姿，让应用“知道”用户怎么拿着手机。

利用好这些特性，能让你的应用显得非常有“鸿蒙味”。
