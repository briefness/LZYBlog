"""
Agent 记忆三层架构动画 - Agent 实战系列第 17 篇配套动画

运行方式：
  manim -pql memory_architecture_animation.py MemoryArchitecture

环境要求：
  pip install manim
"""

from manim import *


class MemoryArchitecture(Scene):
    def construct(self):
        # ========== 标题 ==========
        title = Text("Agent 记忆三层架构", font_size=36, color=WHITE)
        title.to_edge(UP, buff=0.5)
        self.play(Write(title))
        self.wait(0.5)

        # ========== 三层记忆节点 ==========
        working = self._create_layer(
            "⚡ 工作记忆", "当前 messages 列表",
            "#FFA726", UP * 1
        )
        short = self._create_layer(
            "📋 短期记忆", "会话内对话历史",
            "#42A5F5", ORIGIN + DOWN * 0.5
        )
        long_mem = self._create_layer(
            "🧠 长期记忆", "跨会话持久化存储",
            "#66BB6A", DOWN * 2
        )

        layers = [working, short, long_mem]
        self.play(*[FadeIn(l) for l in layers])
        self.wait(0.5)

        # ========== 数据流动箭头 ==========
        # 工作 → 短期
        arrow_ws = Arrow(
            working.get_bottom(), short.get_top(),
            color=ORANGE, buff=0.15, stroke_width=3,
        )
        label_ws = Text("循环结束", font_size=14, color=ORANGE)
        label_ws.next_to(arrow_ws, RIGHT, buff=0.1)

        # 短期 → 长期
        arrow_sl = Arrow(
            short.get_bottom(), long_mem.get_top(),
            color=BLUE, buff=0.15, stroke_width=3,
        )
        label_sl = Text("会话结束提取", font_size=14, color=BLUE)
        label_sl.next_to(arrow_sl, RIGHT, buff=0.1)

        # 长期 → 工作（回路）
        arrow_lw = CurvedArrow(
            long_mem.get_left() + LEFT * 0.3,
            working.get_left() + LEFT * 0.3,
            color=GREEN, angle=-TAU / 4,
        )
        label_lw = Text("新会话检索", font_size=14, color=GREEN)
        label_lw.next_to(arrow_lw, LEFT, buff=0.1)

        arrows = [(arrow_ws, label_ws), (arrow_sl, label_sl), (arrow_lw, label_lw)]
        for arrow, label in arrows:
            self.play(GrowArrow(arrow), FadeIn(label), run_time=0.6)

        self.wait(1)

        # ========== 演示：数据在三层间流动 ==========
        demo_title = Text(
            "数据生命周期演示", font_size=24, color=YELLOW_A,
        )
        demo_title.to_edge(UP, buff=0.3)
        self.play(FadeOut(title), FadeIn(demo_title))

        steps = [
            (working, "用户说: 我叫张三"),
            (working, "Agent 处理中..."),
            (short, "对话追加到会话历史"),
            (working, "用户说: 我偏好顺丰"),
            (short, "2 轮对话已记录"),
            (long_mem, "提取事实: 姓名=张三, 快递=顺丰"),
            (working, "新会话: 张三再次访问"),
            (long_mem, "检索记忆 → 注入 Prompt"),
        ]

        step_text = Text("", font_size=18)
        step_text.to_edge(DOWN, buff=0.6)

        for node, desc in steps:
            new_text = Text(desc, font_size=18, color=WHITE)
            new_text.to_edge(DOWN, buff=0.6)

            highlight = node[0].copy()
            highlight.set_stroke(YELLOW, width=5)

            self.play(
                Create(highlight),
                Transform(step_text, new_text),
                run_time=0.7,
            )
            self.wait(0.6)
            self.play(FadeOut(highlight), run_time=0.2)

        # ========== 结束 ==========
        final = Text(
            "记忆 = 工作 × 短期 × 长期",
            font_size=32, color=GOLD,
        )
        final.move_to(ORIGIN)

        self.play(
            *[FadeOut(m) for m in self.mobjects],
            run_time=0.5,
        )
        self.play(Write(final))
        self.wait(2)

    def _create_layer(self, title_text: str, subtitle_text: str,
                       color_hex: str, position):
        """创建一个带标题和副标题的记忆层级节点"""
        rect = RoundedRectangle(
            corner_radius=0.15,
            width=4.5, height=1.0,
            fill_color=color_hex,
            fill_opacity=0.25,
            stroke_color=color_hex,
            stroke_width=2,
        )
        title = Text(title_text, font_size=18, color=WHITE)
        subtitle = Text(subtitle_text, font_size=13, color=GREY_B)
        text_group = VGroup(title, subtitle).arrange(DOWN, buff=0.08)
        group = VGroup(rect, text_group)
        group.move_to(position)
        return group
