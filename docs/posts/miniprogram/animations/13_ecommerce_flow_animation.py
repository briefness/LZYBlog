"""
电商购物流程状态机动画 - 微信小程序系列第十三篇配套动画

运行方式：
  manim -pql 13_ecommerce_flow_animation.py EcommerceFlow

环境要求：
  pip install manim
"""

from manim import *


class EcommerceFlow(Scene):
    def construct(self):
        # ========== 标题 ==========
        title = Text("电商购物流程状态机", font_size=36, color=WHITE)
        title.to_edge(UP, buff=0.5)
        self.play(Write(title))
        self.wait(0.5)

        # ========== 六个状态节点 ==========
        browse = self._create_node("浏览商品", "#42A5F5", LEFT * 4 + UP * 2)
        cart = self._create_node("加入购物车", "#07C160", LEFT * 4 + DOWN * 0.5)
        confirm = self._create_node("确认订单", "#FFA726", ORIGIN)
        pay = self._create_node("发起支付", "#FF6B6B", RIGHT * 4 + UP * 2)
        backend = self._create_node("后端验证", "#9B59B6", RIGHT * 4 + ORIGIN)
        success = self._create_node("支付成功", "#2ECC71", RIGHT * 4 + DOWN * 2)
        fail = self._create_node("支付失败", "#E74C3C", ORIGIN + DOWN * 2)

        all_nodes = [browse, cart, confirm, pay, backend, success, fail]
        self.play(*[FadeIn(n) for n in all_nodes])
        self.wait(0.5)

        # ========== 主路径箭头 ==========
        arrows_main = [
            (browse, cart, "添加商品"),
            (cart, confirm, "去结算"),
            (confirm, pay, "提交订单"),
            (pay, backend, "调用支付"),
            (backend, success, "验证通过"),
        ]

        for from_node, to_node, label_text in arrows_main:
            arrow = Arrow(
                from_node.get_right(), to_node.get_left(),
                color=YELLOW, buff=0.2, stroke_width=3,
            )
            label = Text(label_text, font_size=14, color=YELLOW)
            label.next_to(arrow, UP if "验证" in label_text else DOWN, buff=0.1)
            self.play(GrowArrow(arrow), FadeIn(label), run_time=0.5)

        # 失败路径
        arrow_fail = CurvedArrow(
            backend.get_bottom(), fail.get_top(),
            color=RED, buff=0.2, stroke_width=3,
            angle=-TAU / 4,
        )
        label_fail = Text("验证失败", font_size=14, color=RED)
        label_fail.next_to(arrow_fail, LEFT, buff=0.1)
        self.play(GrowArrow(arrow_fail), FadeIn(label_fail), run_time=0.5)

        # 失败 -> 重新结算
        arrow_retry = Arrow(
            fail.get_right(), confirm.get_bottom(),
            color=ORANGE, buff=0.2, stroke_width=2,
            path_arc=-0.3,
        )
        label_retry = Text("重新结算", font_size=12, color=ORANGE)
        label_retry.next_to(arrow_retry, RIGHT, buff=0.1)
        self.play(GrowArrow(arrow_retry), FadeIn(label_retry), run_time=0.4)

        self.wait(1)

        # ========== 动态执行演示 ==========
        demo_title = Text("购物流程演示", font_size=24, color=YELLOW_A)
        demo_title.to_edge(UP, buff=0.3)
        self.play(FadeOut(title), FadeIn(demo_title))

        # 成功路径
        steps_success = [
            (browse, "用户浏览商品列表"),
            (cart, "点击「加入购物车」"),
            (confirm, "进入确认订单页，核对商品"),
            (pay, "提交订单，微信支付调起"),
            (backend, "后端接收支付结果，签名验证"),
            (success, "支付成功！更新订单状态"),
        ]

        step_text = Text("", font_size=18)
        step_text.to_edge(DOWN, buff=0.6)

        for node, desc in steps_success:
            new_text = Text(desc, font_size=20, color=WHITE)
            new_text.to_edge(DOWN, buff=0.6)

            highlight = node[0].copy()
            highlight.set_stroke(GREEN, width=6)

            self.play(
                Create(highlight),
                Transform(step_text, new_text),
                run_time=0.8,
            )
            self.wait(0.8)
            self.play(FadeOut(highlight), run_time=0.3)

        # 失败路径
        fail_desc = Text("验证签名失败", font_size=20, color=RED)
        fail_desc.to_edge(DOWN, buff=0.6)

        highlight_fail = backend[0].copy()
        highlight_fail.set_stroke(RED, width=6)
        self.play(Create(highlight_fail), Transform(step_text, fail_desc), run_time=0.8)
        self.wait(0.8)

        # ========== 结束 ==========
        final = Text(
            "状态机 = 清晰的状态流转",
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
            height=1.0,
            fill_color=color_hex,
            fill_opacity=0.3,
            stroke_color=color_hex,
            stroke_width=2,
        )
        label = Text(label_text, font_size=16, color=WHITE)
        group = VGroup(rect, label)
        group.move_to(position)
        return group
