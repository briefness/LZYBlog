# 鸿蒙开发进阶（八）：智慧功能 (Smart Features)

> 🔗 **项目地址**：[https://github.com/briefness/HarmonyDemo](https://github.com/briefness/HarmonyDemo)

HarmonyOS NEXT 不仅有独特的交互，更内置了强大的 AI 能力和实时信息展示机制。
本章将介绍如何利用 **实况窗 (Live View)** 和 **系统原生 AI (Vision/Speech)** 让应用变得更“聪明”。

## 一、实况窗 (Live View)

实况窗是 HarmonyOS 呈现长时任务（Long-term Task）的核心形态，如打车进度、外卖配送、录音时长等。
它比普通通知更持久，比前台应用更轻量，能在锁屏、通知中心和胶囊位展示。

### 1.1 核心概念

*   **LiveViewManager**: 管理实况窗的生命周期（创建、更新、结束）。
*   **LiveViewData**: 数据模型，包含进度、状态文本等。

### 1.2 开发实战

使用 `LiveViewKit` 构建一个简单的计时器实况窗。

```typescript
import { liveViewManager } from '@kit.LiveViewKit';

// 1. 构建初始数据
const liveViewData: liveViewManager.LiveViewData = {
  id: 1001, // 业务ID
  content: {
    title: "正在录音",
    text: "00:15",
    type: liveViewManager.ViewType.CAPSULE | liveViewManager.ViewType.CARD, // 支持胶囊和卡片
  },
  // 胶囊特有配置
  capsule: {
    status: liveViewManager.CapsuleStatus.RUNNING,
    icon: $r('app.media.ic_mic_on'),
    backgroundColor: '#FF0000'
  }
};

// 2. 启动实况窗
liveViewManager.startLiveView(liveViewData).then(() => {
  console.info('LiveView started!');
});

// 3. 更新进度
setInterval(() => {
  liveViewData.content.text = "00:16";
  liveViewManager.updateLiveView(liveViewData);
}, 1000);
```

> **注意**：实况窗需要申请 `ohos.permission.KEEP_BACKGROUND_RUNNING` 权限，并通常配合后台任务使用。

## 二、AI 视觉 (Vision Kit)

HarmonyOS 提供了系统级的视觉能力，无需集成庞大的第三方 SDK 即可实现 OCR 和图像识别。

### 2.1 文本识别 (Text Recognition)

直接从图片中提取文字，支持多语言。

```typescript
import { textRecognition } from '@kit.VisionKit';

async function recognizeText(pixelMap: PixelMap) {
  try {
    const result = await textRecognition.recognizeText(pixelMap);
    console.info(`识别结果: ${result.value}`);
    // result.value 包含提取的所有文本
  } catch (error) {
    console.error('OCR failed:', error);
  }
}
```

### 2.2 视觉控件 (Vision Component)

可以直接在 UI 中嵌入系统提供的拍摄控件，自动完成身份证、银行卡扫描。

```typescript
import { RecognizerComponent } from '@kit.VisionKit';

@Component
struct IDCardScanner {
  build() {
    Column() {
       // 系统预置的身份证扫描组件
      RecognizerComponent({
        type: textRecognition.RecognizerType.ID_CARD,
        onComplete: (res) => {
          console.info('姓名:', res.result.name);
          console.info('号码:', res.result.idNum);
        }
      })
    }
  }
}
```

## 三、AI 语音 (Core Speech Kit)

无需联网，基于端侧大模型实现语音转文字。

### 3.1 语音听写 (Speech Recognizer)

```typescript
import { speechRecognizer } from '@kit.CoreSpeechKit';

let asrEngine = await speechRecognizer.createEngine({
  language: 'zh-CN',
  online: 0 // 0 表示离线模式，隐私更安全
});

// 开始监听
asrEngine.startListening({
  onResult: (result) => {
    console.info('实时转写:', result.transcript);
  }
});
```

## 四、总结

*   **实况窗**: 让用户不再反复打开 App 确认进度，提升信息获取效率。
*   **VisionKit**: 极简代码实现 OCR，减小 App 体积。
*   **CoreSpeechKit**: 离线语音识别，保护隐私且响应极快。

结合上一章的“独有交互”，你的应用现在既具备了“有趣的皮囊”（闪控球、碰一碰），又拥有了“智慧的灵魂”（AI、实况窗）。

下一篇，我们将回归架构设计，讨论如何管理日益复杂的代码——**组件化与工程架构**。
