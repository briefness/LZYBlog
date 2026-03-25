"""
ReAct 循环动画 - Agent 实战系列第一篇配套动画

运行方式：
  manim -pql react_loop_animation.py ReActLoop

环境要求：
  pip install manim
"""

from manim import *


class ReActLoop(Scene):
    def construct(self):
        # ========== 标题 ==========
        title = Text("ReAct 循环：Agent 的思考引擎", font_size=36, color=WHITE)
        title.to_edge(UP, buff=0.5)
        self.play(Write(title))
        self.wait(0.5)

        # ========== 四个状态节点 ==========
        thought = self._create_node("🧠 Thought", "#42A5F5", LEFT * 3 + UP * 0.5)
        action = self._create_node("⚡ Action", "#FFA726", RIGHT * 3 + UP * 0.5)
        observation = self._create_node("👁 Observation", "#66BB6A", RIGHT * 3 + DOWN * 2)
        answer = self._create_node("✅ Answer", "#EF5350", LEFT * 3 + DOWN * 2)

        nodes = [thought, action, observation, answer]
        self.play(*[FadeIn(n) for n in nodes])
        self.wait(0.5)

        # ========== 连接箭头 ==========
        arrow_ta = Arrow(
            thought.get_right(), action.get_left(),
            color=YELLOW, buff=0.2, stroke_width=3,
        )
        label_ta = Text("需要工具", font_size=16, color=YELLOW)
        label_ta.next_to(arrow_ta, UP, buff=0.1)

        arrow_ao = Arrow(
            action.get_bottom(), observation.get_top(),
            color=ORANGE, buff=0.2, stroke_width=3,
        )
        label_ao = Text("执行", font_size=16, color=ORANGE)
        label_ao.next_to(arrow_ao, RIGHT, buff=0.1)

        arrow_ot = Arrow(
            observation.get_left(), thought.get_bottom() + DOWN * 0.3,
            color=GREEN, buff=0.2, stroke_width=3,
            path_arc=-0.5,
        )
        label_ot = Text("结果送回", font_size=16, color=GREEN)
        label_ot.next_to(arrow_ot, DOWN, buff=0.1)

        arrow_ans = Arrow(
            thought.get_bottom(), answer.get_top(),
            color=RED, buff=0.2, stroke_width=3,
        )
        label_ans = Text("信息充足", font_size=16, color=RED)
        label_ans.next_to(arrow_ans, LEFT, buff=0.1)

        arrows = [arrow_ta, arrow_ao, arrow_ot, arrow_ans]
        labels = [label_ta, label_ao, label_ot, label_ans]

        for arrow, label in zip(arrows, labels):
            self.play(GrowArrow(arrow), FadeIn(label), run_time=0.6)

        self.wait(1)

        # ========== 动态执行演示 ==========
        demo_title = Text(
            "执行演示：查天气 → 取消会议",
            font_size=24, color=YELLOW_A,
        )
        demo_title.to_edge(UP, buff=0.3)
        self.play(FadeOut(title), FadeIn(demo_title))

        # 高亮循环：Thought → Action → Observation → Thought → Action → Observation → Answer
        steps = [
            (thought, "分析任务：先查天气"),
            (action, "调用 get_weather('北京')"),
            (observation, "返回：中雨 12°C"),
            (thought, "需要取消会议"),
            (action, "调用 cancel_meeting()"),
            (observation, "返回：已取消"),
            (thought, "任务全部完成"),
            (answer, "回复用户结果"),
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
            "Agent = LLM × 工具 × 循环",
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
        """创建一个带圆角矩形背景的状态节点"""
        rect = RoundedRectangle(
            corner_radius=0.2,
            width=2.8,
            height=1.0,
            fill_color=color_hex,
            fill_opacity=0.3,
            stroke_color=color_hex,
            stroke_width=2,
        )
        label = Text(label_text, font_size=20, color=WHITE)
        group = VGroup(rect, label)
        group.move_to(position)
        return group
