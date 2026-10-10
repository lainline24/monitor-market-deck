"""가격을 결정하는 요인: 최저가와 각 변수의 상관계수가 자라는 manim 애니메이션."""
import json
import os

from manim import *

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = json.load(open(os.path.join(HERE, "data.json"), encoding="utf-8"))
FONT = "Malgun Gothic"
BG, FG, MUTED, ACCENT = "#0B1220", "#E5E7EB", "#94A3B8", "#3B82F6"
config.background_color = BG

LABELS = {"인치": "화면 크기", "주사율Hz": "주사율", "평점": "평점", "리뷰수": "리뷰 수", "판매몰수": "판매몰 수"}


class CorrBars(Scene):
    def construct(self):
        items = sorted(DATA["corr"].items(), key=lambda kv: -kv[1])
        title = Text("최저가와 가장 함께 움직이는 변수는?", font=FONT, color=FG).scale(0.75).to_edge(UP, buff=0.6)
        sub = Text("피어슨 상관계수 (1에 가까울수록 강한 양의 관계)", font=FONT, color=MUTED).scale(0.4).next_to(title, DOWN, 0.25)
        self.play(FadeIn(title, shift=DOWN * 0.3), FadeIn(sub), run_time=0.8)

        x0, width, step = -3.2, 9.0, 0.95
        axis = Line([x0, 1.6, 0], [x0, 1.6 - step * len(items) + 0.2, 0], color=MUTED, stroke_width=2)
        self.play(Create(axis), run_time=0.4)

        bars, nums = VGroup(), VGroup()
        for i, (k, v) in enumerate(items):
            y = 1.2 - i * step
            color = ACCENT if i == 0 else MUTED
            label = Text(LABELS[k], font=FONT, color=FG).scale(0.5)
            label.move_to([x0 - 0.35, y, 0], aligned_edge=RIGHT)
            tracker = ValueTracker(0.001)
            bar = always_redraw(lambda t=tracker, y=y, c=color: Rectangle(
                width=max(t.get_value() * width, 0.001), height=0.55, fill_color=c, fill_opacity=0.95,
                stroke_width=0).move_to([x0 + t.get_value() * width / 2, y, 0]))
            num = always_redraw(lambda t=tracker, y=y, c=color: Text(
                f"{t.get_value():.2f}", font=FONT, color=FG if c == ACCENT else MUTED).scale(0.5)
                .move_to([x0 + t.get_value() * width + 0.55, y, 0]))
            self.add(bar, num)
            self.play(FadeIn(label, shift=RIGHT * 0.2), tracker.animate.set_value(v), run_time=0.9, rate_func=smooth)
            bars.add(bar)
            nums.add(num)

        top_k, top_v = items[0]
        box = SurroundingRectangle(bars[0], color="#F59E0B", buff=0.12, corner_radius=0.08)
        note = Text(f"크기가 커질수록 가격이 오른다 (r = {top_v:.2f})", font=FONT, color="#F59E0B").scale(0.5)
        note.to_edge(DOWN, buff=0.55)
        self.play(Create(box), Write(note), run_time=1.0)
        self.wait(2.5)
