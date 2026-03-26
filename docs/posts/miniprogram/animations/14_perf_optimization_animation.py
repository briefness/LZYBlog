"""
性能优化对比动画 - 微信小程序系列第十四篇配套动画

运行方式：
  manim -pql 14_perf_optimization_animation.py PerfOptimization

环境要求：
  pip install manim
"""

from manim import *


class PerfOptimization(Scene):
    def construct(self):
        # ========== 标题 ==========
        title = Text("渲染链路优化对比", font_size=36, color=WHITE)
        title.to_edge(UP, buff=0.5)
        self.play(Write(title))
        self.wait(0.5)

        # ========== 左侧：优化前 ==========
        left_title = Text("优化前", font_size=24, color=RED)
        left_title.next_to(ORIGIN, LEFT * 4 + UP * 2.5)

        # 慢速加载链
        long_loading = self._create_loading_bar("完整包加载", RED, LEFT * 4 + UP * 1.5, scale=0.8)
        self.play(FadeIn(left_title), FadeIn(long_loading))
        self.wait(0.3)

        blank_screen = self._create_node("白屏等待\n(2-5秒)", "#E74C3C", LEFT * 4 + UP * 0.2)
        self.play(FadeIn(blank_screen))

        all_images = self._create_node("加载全部图片\n(卡顿)", "#E74C3C", LEFT * 4 + DOWN * 1.0)
        self.play(FadeIn(all_images))

        no_cache = self._create_node("无骨架屏\n用户焦虑", "#E74C3C", LEFT * 4 + DOWN * 2.2)
        self.play(FadeIn(no_cache))

        arrow_left = [
            Arrow(long_loading.get_bottom(), blank_screen.get_top(), color=RED, buff=0.1, stroke_width=2),
            Arrow(blank_screen.get_bottom(), all_images.get_top(), color=RED, buff=0.1, stroke_width=2),
            Arrow(all_images.get_bottom(), no_cache.get_top(), color=RED, buff=0.1, stroke_width=2),
        ]
        for a in arrow_left:
            self.play(GrowArrow(a), run_time=0.3)
        self.wait(0.5)

        # ========== 右侧：优化后 ==========
        right_title = Text("优化后", font_size=24, color=GREEN)
        right_title.next_to(ORIGIN, RIGHT * 4 + UP * 2.5)

        # 分包加载
        subpackage = self._create_loading_bar("分包加载", GREEN, RIGHT * 4 + UP * 1.5, scale=0.8)
        self.play(FadeIn(right_title), FadeIn(subpackage))
        self.wait(0.3)

        skeleton = self._create_node("骨架屏显示\n(即时)", "#2ECC71", RIGHT * 4 + UP * 0.2)
        self.play(FadeIn(skeleton))

        lazy_img = self._create_node("图片懒加载\n(按需)", "#2ECC71", RIGHT * 4 + DOWN * 1.0)
        self.play(FadeIn(lazy_img))

        cdn = self._create_node("CDN 加速\n+ WebP", "#2ECC71", RIGHT * 4 + DOWN * 2.2)
        self.play(FadeIn(cdn))

        arrow_right = [
            Arrow(subpackage.get_bottom(), skeleton.get_top(), color=GREEN, buff=0.1, stroke_width=2),
            Arrow(skeleton.get_bottom(), lazy_img.get_top(), color=GREEN, buff=0.1, stroke_width=2),
            Arrow(lazy_img.get_bottom(), cdn.get_top(), color=GREEN, buff=0.1, stroke_width=2),
        ]
        for a in arrow_right:
            self.play(GrowArrow(a), run_time=0.3)
        self.wait(0.5)

        # ========== 时间对比 ==========
        time_compare = Text(
            "首屏时间: 3-5秒  →  0.5-1秒",
            font_size=28, color=YELLOW,
        )
        time_compare.move_to(ORIGIN + DOWN * 3)
        self.play(Write(time_compare))
        self.wait(1)

        # ========== 动态演示 ==========
        demo_title = Text("优化技术一览", font_size=20, color=YELLOW_A)
        demo_title.to_edge(UP, buff=0.3)
        self.play(FadeOut(title), FadeIn(demo_title))

        optimizations = [
            ("分包加载", "主包体积 < 2MB，页面按需加载"),
            ("骨架屏", "Loading 占位，消除白屏焦虑"),
            ("图片懒加载", "只加载视口内图片，节省流量"),
            ("CDN + WebP", "边缘节点加速，格式优化 30%"),
        ]

        step_text = Text("", font_size=18)
        step_text.to_edge(DOWN, buff=0.8)

        for tech, desc in optimizations:
            new_text = Text(f"{tech}：{desc}", font_size=20, color=WHITE)
            new_text.to_edge(DOWN, buff=0.8)

            self.play(
                Transform(step_text, new_text),
                run_time=0.6,
            )
            self.wait(0.8)

        # ========== 结束 ==========
        final = Text(
            "优化 = 体积 × 加载策略 × 渲染效率",
            font_size=28, color=GOLD,
        )
        final.move_to(ORIGIN)

        self.play(
            *[FadeOut(m) for m in self.mobjects],
            run_time=0.5,
        )
        self.play(Write(final))
        self.wait(2)

    def _create_node(self, label_text: str, color_hex: str, position, width=2.2, height=1.0):
        """创建带圆角矩形背景的节点"""
        rect = RoundedRectangle(
            corner_radius=0.15,
            width=width,
            height=height,
            fill_color=color_hex,
            fill_opacity=0.3,
            stroke_color=color_hex,
            stroke_width=2,
        )
        label = Text(label_text, font_size=14, color=WHITE)
        group = VGroup(rect, label)
        group.move_to(position)
        return group

    def _create_loading_bar(self, label_text: str, color_hex: str, position, scale=1.0):
        """创建加载条"""
        rect = RoundedRectangle(
            corner_radius=0.15,
            width=2.5 * scale,
            height=0.6 * scale,
            fill_color=color_hex,
            fill_opacity=0.5,
            stroke_color=color_hex,
            stroke_width=2,
        )
        label = Text(label_text, font_size=14, color=WHITE)
        group = VGroup(rect, label)
        group.move_to(position)
        return group
