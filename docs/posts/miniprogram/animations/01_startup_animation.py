"""
小程序启动流程动画 - 微信小程序系列第一篇配套动画

运行方式：
  manim -pql 01_startup_animation.py StartupFlow

环境要求：
  pip install manim
"""

from manim import *


class StartupFlow(Scene):
    def construct(self):
        # ========== 标题 ==========
        title = Text("微信小程序启动流程", font_size=36, color=WHITE)
        title.to_edge(UP, buff=0.5)
        self.play(Write(title))
        self.wait(0.5)

        # ========== 微信客户端节点 ==========
        wechat = self._create_node("微信客户端", "#07C160", UP * 3 + LEFT * 4)
        self.play(FadeIn(wechat))

        # ========== 双线程节点 ==========
        render_thread = self._create_node("渲染层\nWebView", "#FF6B6B", DOWN * 0.5 + LEFT * 2)
        logic_thread = self._create_node("逻辑层\nJS Engine", "#4ECDC4", DOWN * 0.5 + RIGHT * 2)

        threads = [render_thread, logic_thread]
        self.play(*[FadeIn(t) for t in threads])
        self.wait(0.5)

        # ========== 连接箭头：微信 -> 双线程 ==========
        arrow_w2r = Arrow(
            wechat.get_bottom(), render_thread.get_top(),
            color=YELLOW, buff=0.2, stroke_width=3,
        )
        arrow_w2l = Arrow(
            wechat.get_bottom(), logic_thread.get_top(),
            color=YELLOW, buff=0.2, stroke_width=3,
        )
        label_bridge = Text("双线程初始化", font_size=14, color=YELLOW)
        label_bridge.next_to(wechat, DOWN, buff=0.1)

        for arrow in [arrow_w2r, arrow_w2l]:
            self.play(GrowArrow(arrow), run_time=0.6)
        self.play(FadeIn(label_bridge))
        self.wait(1)

        # ========== 桥接层 ==========
        bridge = self._create_small_node("Native\nBridge", "#9B59B6", ORIGIN)
        self.play(FadeIn(bridge))

        # 连接双线程到桥接层
        arrow_r2b = Arrow(
            render_thread.get_bottom(), bridge.get_top(),
            color=ORANGE, buff=0.3, stroke_width=2,
        )
        arrow_l2b = Arrow(
            logic_thread.get_bottom(), bridge.get_top(),
            color=ORANGE, buff=0.3, stroke_width=2,
        )
        for arrow in [arrow_r2b, arrow_l2b]:
            self.play(GrowArrow(arrow), run_time=0.5)
        self.wait(0.5)

        # ========== 三层标注 ==========
        render_label = Text("渲染层 (WebView)", font_size=14, color="#FF6B6B")
        render_label.next_to(render_thread, LEFT, buff=0.3)
        logic_label = Text("逻辑层 (JS)", font_size=14, color="#4ECDC4")
        logic_label.next_to(logic_thread, RIGHT, buff=0.3)

        self.play(FadeIn(render_label), FadeIn(logic_label))

        # ========== 动态演示：启动步骤 ==========
        demo_title = Text("启动阶段分解", font_size=24, color=YELLOW_A)
        demo_title.to_edge(UP, buff=0.3)
        self.play(FadeOut(title), FadeIn(demo_title))

        steps = [
            (wechat, "1. 用户打开小程序，微信加载分包"),
            (bridge, "2. 初始化 Native Bridge 通信层"),
            (render_thread, "3. 渲染层 WebView 就绪"),
            (logic_thread, "4. 逻辑层 JS Engine 启动"),
            (render_thread, "5. WXML/WXSS 解析为 DOM 树"),
            (logic_thread, "6. app.js 全局逻辑执行"),
        ]

        step_text = Text("", font_size=18)
        step_text.to_edge(DOWN, buff=0.8)

        for node, desc in steps:
            new_text = Text(desc, font_size=20, color=WHITE)
            new_text.to_edge(DOWN, buff=0.8)

            highlight = node[0].copy()
            highlight.set_stroke(YELLOW, width=6)

            self.play(
                Create(highlight),
                Transform(step_text, new_text),
                run_time=0.8,
            )
            self.wait(0.8)
            self.play(FadeOut(highlight), run_time=0.3)

        # ========== 结束 ==========
        final = Text(
            "小程序 = 渲染层 + 逻辑层 + Native",
            font_size=32, color=GOLD,
        )
        final.move_to(ORIGIN)

        self.play(
            *[FadeOut(m) for m in self.mobjects],
            run_time=0.5,
        )
        self.play(Write(final))
        self.wait(2)

    def _create_node(self, label_text: str, color_hex: str, position):
        """创建带圆角矩形背景的状态节点"""
        rect = RoundedRectangle(
            corner_radius=0.2,
            width=2.8,
            height=1.2,
            fill_color=color_hex,
            fill_opacity=0.3,
            stroke_color=color_hex,
            stroke_width=2,
        )
        label = Text(label_text, font_size=18, color=WHITE)
        group = VGroup(rect, label)
        group.move_to(position)
        return group

    def _create_small_node(self, label_text: str, color_hex: str, position):
        """创建小型节点"""
        rect = RoundedRectangle(
            corner_radius=0.15,
            width=2.0,
            height=0.9,
            fill_color=color_hex,
            fill_opacity=0.3,
            stroke_color=color_hex,
            stroke_width=2,
        )
        label = Text(label_text, font_size=14, color=WHITE)
        group = VGroup(rect, label)
        group.move_to(position)
        return group
