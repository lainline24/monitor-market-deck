"""반론 검증: 크기 효과는 OLED 착시인가? — 설명력(R²) 비교 + OLED 제외 상관계수."""
import json
import os

from manim import *

HERE = os.path.dirname(os.path.abspath(__file__))
V = json.load(open(os.path.join(HERE, "data.json"), encoding="utf-8"))["v2"]
FONT = "Malgun Gothic"
BG, FG, MUTED, ACCENT, WARN = "#0B1220", "#E5E7EB", "#94A3B8", "#3B82F6", "#F59E0B"
config.background_color = BG


def T(s, scale=0.5, color=FG):
    return Text(s, font=FONT, color=color).scale(scale)


class R2Bars(Scene):
    def construct(self):
        title = T("가격 차이를 얼마나 설명하나? (설명력 R²)", 0.68).to_edge(UP, buff=0.55)
        sub = T("1에 가까울수록 그 변수만으로 30종의 가격 차이를 잘 설명", 0.38, MUTED).next_to(title, DOWN, 0.22)
        self.play(FadeIn(title, shift=DOWN * 0.3), FadeIn(sub), run_time=0.8)

        rows = [("크기만", V["r2"]["size"], MUTED), ("패널(OLED 여부)만", V["r2"]["panel"], ACCENT),
                ("패널 + 크기", V["r2"]["both"], "#93C5FD")]
        x0, width, step = -2.6, 8.0, 1.05
        axis = Line([x0, 1.75, 0], [x0, 1.75 - step * len(rows), 0], color=MUTED, stroke_width=2)
        self.play(Create(axis), run_time=0.3)
        bars = []
        for i, (name, val, col) in enumerate(rows):
            y = 1.25 - i * step
            lab = T(name, 0.48).move_to([x0 - 0.3, y, 0], aligned_edge=RIGHT)
            tr = ValueTracker(0.001)
            bar = always_redraw(lambda t=tr, y=y, c=col: Rectangle(width=max(t.get_value() * width, 0.001), height=0.6,
                                fill_color=c, fill_opacity=0.95, stroke_width=0).move_to([x0 + t.get_value() * width / 2, y, 0]))
            num = always_redraw(lambda t=tr, y=y: T(f"{t.get_value():.2f}", 0.5).move_to([x0 + t.get_value() * width + 0.5, y, 0]))
            self.add(bar, num)
            self.play(FadeIn(lab, shift=RIGHT * 0.2), tr.animate.set_value(val), run_time=1.0, rate_func=smooth)
            bars.append(bar)
        box = SurroundingRectangle(bars[1], color=WARN, buff=0.1, corner_radius=0.08)
        n1 = T(f"패널 하나가 크기보다 2배 넘게 설명한다", 0.46, WARN).to_edge(DOWN, buff=1.25)
        self.play(Create(box), Write(n1), run_time=1.0)
        self.wait(1.4)

        # 2단계: OLED를 빼도 크기 효과가 남는가
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.6)
        q = T("그럼 크기 효과는 OLED 때문에 생긴 착시일까?", 0.64).to_edge(UP, buff=0.9)
        self.play(FadeIn(q, shift=DOWN * 0.3), run_time=0.7)
        left = VGroup(T("30종 전체", 0.46, MUTED), T(f"r = {V['corrAll']:.2f}", 1.1, MUTED)).arrange(DOWN, buff=0.3)
        right = VGroup(T(f"OLED {V['nOled']}종 제외 ({V['nNonOled']}종)", 0.46, ACCENT),
                       T(f"r = {V['corrNonOled']:.2f}", 1.1, ACCENT)).arrange(DOWN, buff=0.3)
        left.move_to(LEFT * 3.2 + DOWN * 0.1)
        right.move_to(RIGHT * 3.2 + DOWN * 0.1)
        arrow = Arrow(LEFT * 1.2, RIGHT * 1.2, color=FG, stroke_width=6).move_to(DOWN * 0.1)
        cap = T("크기 ↔ 가격 상관계수", 0.42, MUTED).next_to(arrow, UP, 0.3)
        self.play(FadeIn(left), run_time=0.6)
        self.play(GrowArrow(arrow), FadeIn(cap), run_time=0.6)
        self.play(FadeIn(right, shift=LEFT * 0.3), run_time=0.8)
        a1 = T("아닙니다. OLED를 빼면 오히려 더 뚜렷해집니다.", 0.5, WARN).to_edge(DOWN, buff=1.5)
        a2 = T(f"→ 패널이 먼저 가르고, OLED가 아닌 {V["nNonOled"]}종 안에서는 1인치당 약 {V['slopeNonOled']:.0f}만 원", 0.46, FG).next_to(a1, DOWN, 0.3)
        self.play(Write(a1), run_time=0.9)
        self.play(FadeIn(a2, shift=UP * 0.2), run_time=0.7)
        self.wait(2.5)
