"""
异步网络请求动画 - 微信小程序系列第五篇配套动画

运行方式：
  manim -pql 05_async_flow_animation.py AsyncFlow

环境要求：
  pip install manim
"""

from manim import *


class AsyncFlow(Scene):
    def construct(self):
        # ========== 标题 ==========
        title = Text("wx.request 异步请求完整时序", font_size=32, color=WHITE)
        title.to_edge(UP, buff=0.5)
        self.play(Write(title))
        self.wait(0.5)

        # ========== 节点定义 ==========
        page = self._create_node("Page\n(页面逻辑)", "#42A5F5", LEFT * 4 + UP * 1)
        wx_api = self._create_node("wx.request\n(微信API)", "#07C160", ORIGIN + UP * 1)
        network = self._create_node("Backend\nServer", "#FF6B6B", RIGHT * 4 + UP * 1)
        callback = self._create_node("Callback\n(回调处理)", "#FFA726", ORIGIN + DOWN * 2)
        ui_update = self._create_node("UI 更新", "#9B59B6", LEFT * 4 + DOWN * 2)

        nodes = [page, wx_api, network, callback, ui_update]
        self.play(*[FadeIn(n) for n in nodes])
        self.wait(0.5)

        # ========== 箭头标注 ==========
        # Page -> wx.request
        arrow_p2w = Arrow(
            page.get_right(), wx_api.get_left(),
            color=YELLOW, buff=0.2, stroke_width=3,
        )
        label_p2w = Text("调用", font_size=14, color=YELLOW)
        label_p2w.next_to(arrow_p2w, UP, buff=0.1)

        # wx.request -> Backend
        arrow_w2n = Arrow(
            wx_api.get_right(), network.get_left(),
            color=ORANGE, buff=0.2, stroke_width=3,
        )
        label_w2n = Text("HTTP 请求", font_size=14, color=ORANGE)
        label_w2n.next_to(arrow_w2n, UP, buff=0.1)

        # Backend -> Callback
        arrow_n2c = Arrow(
            network.get_bottom(), callback.get_top(),
            color=GREEN, buff=0.3, stroke_width=3,
        )
        label_n2c = Text("响应数据", font_size=14, color=GREEN)
        label_n2c.next_to(arrow_n2c, RIGHT, buff=0.1)

        # Callback -> UI
        arrow_c2u = Arrow(
            callback.get_left(), ui_update.get_right(),
            color=PURPLE, buff=0.2, stroke_width=3,
        )
        label_c2u = Text("setData", font_size=14, color=PURPLE)
        label_c2u.next_to(arrow_c2u, DOWN, buff=0.1)

        arrows = [arrow_p2w, arrow_w2n, arrow_n2c, arrow_c2u]
        labels = [label_p2w, label_w2n, label_n2c, label_c2u]

        for arrow, label in zip(arrows, labels):
            self.play(GrowArrow(arrow), FadeIn(label), run_time=0.6)

        self.wait(1)

        # ========== 动态执行演示 ==========
        demo_title = Text("完整请求流程", font_size=24, color=YELLOW_A)
        demo_title.to_edge(UP, buff=0.3)
        self.play(FadeOut(title), FadeIn(demo_title))

        # 流程步骤
        steps = [
            (page, "setData({ loading: true })"),
            (arrow_p2w, "调用 wx.request()"),
            (wx_api, "微信 API 封装请求"),
            (arrow_w2n, "发起网络请求..."),
            (network, "后端处理并返回 JSON"),
            (arrow_n2c, "回调触发 (success/fail)"),
            (callback, "数据解析 + 错误处理"),
            (arrow_c2u, "调用 this.setData()"),
            (ui_update, "页面重新渲染"),
        ]

        step_text = Text("", font_size=18)
        step_text.to_edge(DOWN, buff=0.6)

        for target, desc in steps:
            new_text = Text(desc, font_size=20, color=WHITE)
            new_text.to_edge(DOWN, buff=0.6)

            if hasattr(target, '__getitem__') and len(target) > 0:
                highlight = target[0].copy()
                highlight.set_stroke(YELLOW, width=6)
                self.play(Create(highlight), run_time=0.3)

            self.play(
                Transform(step_text, new_text),
                run_time=0.5,
            )
            self.wait(0.6)

            if hasattr(target, '__getitem__') and len(target) > 0:
                self.play(FadeOut(highlight), run_time=0.2)

        # ========== 结束 ==========
        final = Text(
            "Promise 封装 = 更优雅的异步",
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
            width=2.5,
            height=1.2,
            fill_color=color_hex,
            fill_opacity=0.3,
            stroke_color=color_hex,
            stroke_width=2,
        )
        label = Text(label_text, font_size=16, color=WHITE)
        group = VGroup(rect, label)
        group.move_to(position)
        return group
