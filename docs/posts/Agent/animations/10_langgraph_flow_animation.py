"""
LangGraph 图状态流转动画 - Agent 实战系列第 10 篇配套动画

运行方式：
  manim -pql langgraph_flow_animation.py LangGraphFlow

环境要求：
  pip install manim
"""

from manim import *


class LangGraphFlow(Scene):
    def construct(self):
        # ========== 标题 ==========
        title = Text("LangGraph：图状态流转", font_size=36, color=WHITE)
        title.to_edge(UP, buff=0.5)
        self.play(Write(title))
        self.wait(0.5)

        # ========== 节点 ==========
        gen_node = self._create_node("💻 生成代码", "#FFA726", LEFT * 3)
        review_node = self._create_node("🔍 审查代码", "#42A5F5", RIGHT * 0)
        test_node = self._create_node("🧪 运行测试", "#66BB6A", RIGHT * 3)

        nodes = [gen_node, review_node, test_node]
        self.play(*[FadeIn(n) for n in nodes])

        # ========== 边 ==========
        arrow_gr = Arrow(gen_node.get_right(), review_node.get_left(),
                         color=WHITE, buff=0.2, stroke_width=3)
        arrow_rt = Arrow(review_node.get_right(), test_node.get_left(),
                         color=GREEN, buff=0.2, stroke_width=3)
        label_pass = Text("通过", font_size=14, color=GREEN)
        label_pass.next_to(arrow_rt, UP, buff=0.1)

        # 循环回路
        arrow_back = CurvedArrow(
            review_node.get_bottom() + DOWN * 0.1,
            gen_node.get_bottom() + DOWN * 0.1,
            color=RED, angle=TAU / 5,
        )
        label_fail = Text("不通过", font_size=14, color=RED)
        label_fail.next_to(arrow_back, DOWN, buff=0.1)

        self.play(GrowArrow(arrow_gr), run_time=0.5)
        self.play(GrowArrow(arrow_rt), FadeIn(label_pass), run_time=0.5)
        self.play(GrowArrow(arrow_back), FadeIn(label_fail), run_time=0.5)
        self.wait(0.5)

        # ========== 状态标签 ==========
        state_label = Text("State: {code: '', review: '', retry: 0}",
                           font_size=14, color=GREY_B)
        state_label.to_edge(DOWN, buff=1.5)
        self.play(FadeIn(state_label))

        # ========== 动态执行演示 ==========
        demo_title = Text("执行演示：代码生成 → 审查循环", font_size=22, color=YELLOW_A)
        demo_title.to_edge(UP, buff=0.3)
        self.play(FadeOut(title), FadeIn(demo_title))

        step_info = Text("", font_size=16)
        step_info.to_edge(DOWN, buff=0.6)

        flow_steps = [
            (gen_node, "生成: def sort_list(lst): ...", "State: {code: '...', retry: 1}"),
            (review_node, "审查: 缺少类型注解，打回", "State: {review: '不通过', retry: 1}"),
            (gen_node, "重写: def sort_list(lst: list) -> list: ...", "State: {code: '...v2', retry: 2}"),
            (review_node, "审查: 通过 ✅", "State: {review: '通过', retry: 2}"),
            (test_node, "测试: 3/3 passed ✅", "State: {test: 'passed', retry: 2}"),
        ]

        for node, desc, state_str in flow_steps:
            new_info = Text(desc, font_size=16, color=WHITE)
            new_info.to_edge(DOWN, buff=0.6)

            new_state = Text(state_str, font_size=14, color=GREY_B)
            new_state.to_edge(DOWN, buff=1.5)

            highlight = node[0].copy()
            highlight.set_stroke(YELLOW, width=6)

            self.play(
                Create(highlight),
                Transform(step_info, new_info),
                Transform(state_label, new_state),
                run_time=0.8,
            )
            self.wait(0.7)
            self.play(FadeOut(highlight), run_time=0.2)

        # ========== 结束 ==========
        final = Text(
            "图编排 = 节点 × 条件边 × 共享状态",
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
            corner_radius=0.2,
            width=2.8, height=1.0,
            fill_color=color_hex, fill_opacity=0.3,
            stroke_color=color_hex, stroke_width=2,
        )
        label = Text(label_text, font_size=18, color=WHITE)
        group = VGroup(rect, label)
        group.move_to(position)
        return group
