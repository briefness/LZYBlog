# 10. 守护质量：测试金字塔与 CI/CD

> “代码可用即可”不仅非专业态度。专业项目必须依靠自动化测试来保证长期的可维护性。

Flutter 提供了极其完善的测试框架，完美契合**测试金字塔**模型。

## 1. Unit Test (单元测试)

*   **目标**: 验证单一函数、类或模块的逻辑。
*   **特点**: 不依赖 UI，不依赖模拟器，跑在电脑本地 Dart VM 上，速度极快（毫秒级）。
*   **适用**: 验证算法、JSON 解析、Validator、ViewModel 状态流转。

```dart
test('Counter value should be incremented', () {
  final counter = Counter();
  counter.increment();
  expect(counter.value, 1);
});
```

## 2. Widget Test (组件测试)

此为 Flutter 的核心优势。无需启动浏览器或模拟器。
它在一个**虚拟的 UI 环境**中构建 Widget 树。

*   **目标**: 验证 UI 构建逻辑、交互响应。
*   **特点**: **不依赖真机渲染**（Headless），但能模拟点击、滑动。速度快（秒级）。
*   **Finder**: 通过 text, key, icon 找到组件。
*   **Matcher**: 验证组件是否存在 (`findsOneWidget`), 颜色对不对。

```dart
testWidgets('MyWidget has a title and message', (WidgetTester tester) async {
  await tester.pumpWidget(MyWidget(title: 'T', message: 'M'));
  
  expect(find.text('T'), findsOneWidget);
  expect(find.text('M'), findsOneWidget);
  
  await tester.tap(find.byType(FloatingActionButton));
  await tester.pump(); // 触发 rebuild
});
```

## 3. Integration Test (集成测试)

*   **目标**: 端到端 (E2E) 验证完整 User Flow。
*   **特点**: **必须跑在真机或模拟器上**。由 `flutter_driver` (老) 或 `integration_test` (新) 驱动。
*   **代价**: 慢，不稳定。通常只覆盖核心路径（如登录 -> 下单 -> 支付）。

## 4. Golden Test (黄金快照测试)

UI 逻辑正确之外，像素级还原同样重要。
Golden Test 将当前的 UI 渲染成一张 png 图片，并与仓库里存好的“黄金标准图”进行逐像素比对。

*   **命令**: `flutter test --update-goldens` 生成基准图。
*   **坑**: Mac 和 Linux 渲染字体的抗锯齿算法不同，导致 CI 失败。
*   **解法**: 使用 `Alibaba/flutter_box` 或 `eBay/flutter_golder_test` 等库消除平台差异，或者统一 CI 环境。

## 进阶视角 (Advanced Insight)

### Mocking (模拟)

测试过程中，应避免真实去请求网络接口。
使用 `Mockito` 或 `Mocktail` 来 Mock 你的 Repository。
通过依赖注入 (Dependency Injection)，在测试时注入 Mock 对象，确保测试环境可控。

```dart
class MockApi extends Mock implements Api {}

// 当调用 fetchUser 时，返回假数据
when(mockApi.fetchUser()).thenAnswer((_) async => User('Test'));
```

至此，Flutter 系列解析圆满完成。从架构原理的深潜，到手势与滑动的微操，再到原生交互的破壁，最后以工程化测试收尾。这不仅是 Flutter 的旅程，更是现代客户端开发的缩影。
