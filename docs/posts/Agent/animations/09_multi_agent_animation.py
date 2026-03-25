"""
多 Agent 协作通信动画 - Agent 实战系列第 9 篇配套动画

运行方式：
  manim -pql multi_agent_animation.py MultiAgentHandoff

环境要求：
  pip install manim
"""

from manim import *


class MultiAgentHandoff(Scene):
    def construct(self):
        # ========== 标题 ==========
        title = Text("多 Agent 协作：路由与委派", font_size=36, color=WHITE)
        title.to_edge(UP, buff=0.5)
        self.play(Write(title))
        self.wait(0.5)

        # ========== 用户 ==========
        user = self._create_node("👤 用户", "#78909C", LEFT * 5 + UP * 0.5)
        self.play(FadeIn(user))

        # ========== 路由 Agent ==========
        router = self._create_node("🎯 路由 Agent", "#42A5F5", LEFT * 1.5 + UP * 0.5)
        self.play(FadeIn(router))

        # ========== 专家 Agents ==========
        order_agent = self._create_node("📦 订单 Agent", "#FFA726", RIGHT * 2.5 + UP * 2)
        tech_agent = self._create_node("🔧 技术 Agent", "#66BB6A", RIGHT * 2.5 + UP * 0)
        chat_agent = self._create_node("💬 闲聊 Agent", "#AB47BC", RIGHT * 2.5 + DOWN * 2)

        experts = [order_agent, tech_agent, chat_agent]
        self.play(*[FadeIn(e) for e in experts])
        self.wait(0.3)

        # ========== 静态连线 ==========
        arrow_ur = Arrow(user.get_right(), router.get_left(), color=WHITE, buff=0.2, stroke_width=2)
        arrows_re = [
            Arrow(router.get_right(), order_agent.get_left(), color=ORANGE, buff=0.2, stroke_width=2),
            Arrow(router.get_right(), tech_agent.get_left(), color=GREEN, buff=0.2, stroke_width=2),
            Arrow(router.get_right(), chat_agent.get_left(), color=PURPLE, buff=0.2, stroke_width=2),
        ]
        self.play(GrowArrow(arrow_ur))
        for a in arrows_re:
            self.play(GrowArrow(a), run_time=0.3)
        self.wait(0.5)

        # ========== 动态演示 ==========
        demo_title = Text("演示：订单查询流程", font_size=24, color=YELLOW_A)
        demo_title.to_edge(UP, buff=0.3)
        self.play(FadeOut(title), FadeIn(demo_title))

        step_text = Text("", font_size=18)
        step_text.to_edge(DOWN, buff=0.7)

        steps = [
            (user, "用户: 我的 ORD-12345 到哪了？", YELLOW),
            (router, "路由: 识别为订单问题", BLUE),
            (order_agent, "委派给订单 Agent", ORANGE),
            (order_agent, "订单 Agent: 调用 query_order()", ORANGE),
            (order_agent, "结果: 已发货，明天到达", GREEN),
            (router, "路由: 转发结果给用户", BLUE),
            (user, "用户收到回复 ✅", GREEN),
        ]

        for node, desc, color in steps:
            new_text = Text(desc, font_size=18, color=WHITE)
            new_text.to_edge(DOWN, buff=0.7)

            highlight = node[0].copy()
            highlight.set_stroke(color, width=6)

            self.play(
                Create(highlight),
                Transform(step_text, new_text),
                run_time=0.7,
            )
            self.wait(0.6)
            self.play(FadeOut(highlight), run_time=0.2)

        # ========== 结束 ==========
        final = Text(
            "路由分派 × 专家执行 × 结果汇总",
            font_size=30, color=GOLD,
        )
        final.move_to(ORIGIN)

        self.play(
            *[FadeOut(m) for m in self.mobjects],
            run_time=0.5,
        )
        self.play(Write(final))
        self.wait(2)

    def _create_node(self, label_text: str, color_hex: str, position):
        rect = RoundedRectangle(
            corner_radius=0.15,
            width=2.6, height=0.9,
            fill_color=color_hex, fill_opacity=0.3,
            stroke_color=color_hex, stroke_width=2,
        )
        label = Text(label_text, font_size=17, color=WHITE)
        group = VGroup(rect, label)
        group.move_to(position)
        return group
