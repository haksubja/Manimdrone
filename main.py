from manim import *
import numpy as np
import random
from dataclasses import dataclass, field

random.seed(7)

# a - b
# |   |
# d - c
@dataclass(frozen=True)
class Pos:
    a: np.ndarray = field(default_factory=lambda: np.array([-4.0, 1.8, 0]))
    b: np.ndarray = field(default_factory=lambda: np.array([3.4, 1, 0]))
    c: np.ndarray = field(default_factory=lambda: np.array([3.4, -3, 0]))
    d: np.ndarray = field(default_factory=lambda: np.array([-4.0, -3, 0]))
# ...existing code...

# ---------- Palette ----------
BG = "#0B1220"
NAVY = "#13233A"
PANEL_DIRTY = "#5C4A38"
PANEL_CLEAN = "#1E5FA8"
PANEL_SHINE = "#5FA8E8"
DUST = "#8A6E4E"
ACCENT = "#2ECC71"
WARN = "#E0763C"
WHITE_T = "#F2F4F8"
GREY = "#8A93A6"

config.background_color = BG





def make_panel(width=1.0, height=0.55, angle=0, fill=PANEL_DIRTY):
    p = Rectangle(width=width, height=height, fill_color=fill, fill_opacity=1,
                  stroke_color="#0A1726", stroke_width=2)
    # grid lines for a "solar cell" look
    lines = VGroup()
    for i in range(1, 3):
        x = -width / 2 + i * width / 3
        lines.add(Line([x, -height / 2, 0], [x, height / 2, 0], stroke_color="#0A1726", stroke_width=1))
    grp = VGroup(p, lines)
    grp.rotate(angle)
    return grp


def make_drone(scale=0.42):
    body = RoundedRectangle(corner_radius=0.08, width=0.9, height=0.32,
                             fill_color="#D8DEE9", fill_opacity=1, stroke_color="#3A4255", stroke_width=2)
    arms = VGroup(*[
        Line([-0.45, 0.18 * s, 0], [-0.85, 0.4 * s, 0], stroke_color="#3A4255", stroke_width=4)
        for s in (1, -1)
    ], *[
        Line([0.45, 0.18 * s, 0], [0.85, 0.4 * s, 0], stroke_color="#3A4255", stroke_width=4)
        for s in (1, -1)
    ])
    rotors = VGroup(*[
        Ellipse(width=0.5, height=0.07, fill_color="#9AA5B8", fill_opacity=0.85, stroke_width=0)
        .move_to([x, 0.4 * s, 0])
        for x, s in [(-0.85, 1), (-0.85, -1), (0.85, 1), (0.85, -1)]
    ])
    boom = Line([0, -0.16, 0], [0, -0.55, 0], stroke_color="#3A4255", stroke_width=3)
    brush = RoundedRectangle(corner_radius=0.03, width=0.55, height=0.12,
                              fill_color="#4FB0E0", fill_opacity=1, stroke_width=0).move_to([0, -0.62, 0])
    drone = VGroup(arms, rotors, body, boom, brush)
    drone.scale(scale)
    return drone


def dust_cluster(n=4, spread=(0.35, 0.15)):
    pts = VGroup()
    for _ in range(n):
        d = Dot(radius=random.uniform(0.025, 0.05), color=DUST, fill_opacity=0.9)
        d.move_to([random.uniform(-spread[0], spread[0]), random.uniform(-spread[1], spread[1]), 0])
        pts.add(d)
    return pts


class SolarDroneDemo(Scene):
    def construct(self):

        position = Pos()

        # Title
        title = Text("SolarBee", font="Arial", weight=BOLD, color=WHITE_T).scale(1.3)
        tagline = Text("Drone limpador de placas solares", font="Arial", color=GREY).scale(0.55)
        tagline.next_to(title, DOWN, buff=0.35)
        underline = Line(LEFT, RIGHT, color=ACCENT, stroke_width=3).set_width(title.width).next_to(title, DOWN, buff=0.15)

        self.play(FadeIn(title, shift=UP * 0.3), run_time=1.2)
        self.play(Create(underline), run_time=0.5)
        self.play(FadeIn(tagline, shift=UP * 0.2), run_time=0.8)
        self.wait(5.0)
        self.play(FadeOut(VGroup(title, tagline, underline), shift=UP * 0.5), run_time=0.9)

        # Main Scene
        problem_head = Text("O problema", font="Arial", weight=BOLD, color=WARN).scale(0.7)
        problem_head.to_edge(UP, buff=0.6)
        self.play(FadeIn(problem_head, shift=DOWN * 0.2), run_time=0.7)

        ground = Line([-7, -3, 0], [7, -3, 0], color=GREY, stroke_width=3)
        wall_left = Line(position.d, position.a, color=GREY, stroke_width=3)
        wall_right = Line(position.c, position.b, color=GREY, stroke_width=3)
        roof_a = np.array(position.a)
        roof_b = np.array(position.b)
        roof_line = Line(roof_a, roof_b, color="#3A4255", stroke_width=10)
        roof_under = Polygon(roof_a + DOWN * 0.18, roof_b + DOWN * 0.18, roof_b, roof_a,
                              fill_color="#283248", fill_opacity=1, stroke_width=0)

        sun = VGroup(
            Circle(radius=0.45, color="#F4C95D", fill_opacity=1, stroke_width=0),
            *[
                Line(ORIGIN, RIGHT * 0.25, color="#F4C95D", stroke_width=3)
                .shift(RIGHT * 0.55)
                .rotate(a, about_point=ORIGIN)
                for a in np.linspace(0, TAU, 8, endpoint=False)
            ]
        )
        sun.move_to([4.8, 2.6, 0])

        self.play(Create(ground), Create(wall_left), Create(wall_right), Create(roof_under), Create(roof_line), FadeIn(sun), run_time=1.4)

        # Panels
        angle = angle_of_vector(roof_b - roof_a)
        n_panels = 6
        panels = VGroup()
        dusts = VGroup()
        for i in range(n_panels):
            t = (i + 0.5) / n_panels
            center = interpolate(roof_a, roof_b, t) + rotate_vector(UP, angle) * 0.32
            panel = make_panel(width=1.05, height=0.55, angle=angle, fill=PANEL_CLEAN)
            panel.move_to(center)
            panels.add(panel)
            d = dust_cluster(n=random.randint(4, 6))
            d.rotate(angle)
            d.move_to(center)
            dusts.add(d)

        self.play(LaggedStart(*[FadeIn(p, scale=0.9) for p in panels], lag_ratio=0.12), run_time=1.4)

        # Efficiency tracker
        eff_label = Text("Eficiência", font="Arial", color=GREY).scale(0.5)
        eff_label.to_corner(UL, buff=0.7)
        eff_tracker = ValueTracker(100)
        eff_color_tracker = {"color": WHITE_T}
        eff_value = always_redraw(
            lambda: Text(f"{eff_tracker.get_value():.0f}%", font="Arial",
                          color=eff_color_tracker["color"]).scale(1.1)
            .next_to(eff_label, DOWN, buff=0.15)
        )
        eff_group = VGroup(eff_label, eff_value)
        self.play(
            FadeIn(eff_label),
            FadeIn(eff_value),
            run_time=1
        )

        # Gradually dirty the panels as efficiency decreases
        for i in range(n_panels):
            dirty_panel = make_panel(
                width=1.05,
                height=0.55,
                angle=angle,
                fill=interpolate_color(
                    ManimColor(PANEL_CLEAN),
                    ManimColor(PANEL_DIRTY),
                    (i + 1) / n_panels
                )
            )
            dirty_panel.move_to(panels[i].get_center())

            self.play(
                Transform(panels[i], dirty_panel),
                FadeIn(dusts[i]),
                eff_tracker.animate.set_value(
                    100 - (24 * (i + 1) / n_panels)
                ),
                run_time=0.35,
            )

        def set_eff_color(c):
            eff_color_tracker["color"] = c

        self.play(eff_tracker.animate.set_value(76), run_time=1.6)
        set_eff_color(WARN)

        warn_text = Text("Poeira e resíduos podem reduzir a eficiência em até 25%", font="Arial", color=WARN).scale(0.5)
        warn_bg = RoundedRectangle(
            corner_radius=0.1,
            width=warn_text.width + 0.4,
            height=warn_text.height + 0.2,
            fill_color=BG,
            fill_opacity=1,
            stroke_width=0
        )

        solution_head = Text("A solução", font="Arial", weight=BOLD, color=ACCENT).scale(0.7)
        solution_head.to_edge(UP, buff=0.6)

        warn_group = VGroup(warn_bg, warn_text)
        warn_group.next_to(solution_head, DOWN*10, buff=0.4)

        self.play(FadeIn(warn_group, shift=UP * 0.2), run_time=0.8)
        self.wait(5.0)

        self.play(FadeOut(VGroup(problem_head, warn_group)), run_time=0.6)

        # Solution
        self.play(FadeIn(solution_head, shift=DOWN * 0.2), run_time=0.7)

        drone = make_drone(scale=0.9)
        drone.move_to([-7.5, 3.0, 0])
        intro_label = Text("Um drone para a limpeza de painéis", font="Arial", color=ACCENT).scale(0.55)
        intro_label.next_to(solution_head, DOWN*10, buff=0.4)
        self.play(FadeIn(intro_label), run_time=0.6)
        self.wait(5)

        self.play(drone.animate.move_to([-3.0, 3, 0]), run_time=1.3, rate_func=smooth)
        self.play(FadeOut(intro_label), run_time=0.5)
        self.wait(1)

        # Cleaning
        progress_bg = RoundedRectangle(corner_radius=0.08, width=4.2, height=0.32,
                                        fill_color=NAVY, fill_opacity=1, stroke_color=GREY, stroke_width=1.5)
        progress_fill = RoundedRectangle(corner_radius=0.08, width=0.01, height=0.32,
                                          fill_color=ACCENT, fill_opacity=1, stroke_width=0)
        progress_fill.align_to(progress_bg, LEFT)
        progress_fill.match_y(progress_bg)
        progress_label = Text("Limpando 0 / 6 painéis", font="Arial", color=GREY).scale(0.42)
        progress_group = VGroup(progress_bg, progress_fill).next_to(solution_head, DOWN*10, buff=0.4)
        progress_label.next_to(progress_group, UP, buff=0.15)
        self.play(FadeIn(progress_group), FadeIn(progress_label), run_time=0.5)

        for i in range(n_panels):
            hover_point = panels[i].get_center() + rotate_vector(UP, angle) * 0.55
            self.play(drone.animate.move_to(hover_point), run_time=0.7, rate_func=smooth)

            new_panel = make_panel(width=1.05, height=0.55, angle=angle, fill=PANEL_CLEAN)
            new_panel.move_to(panels[i].get_center())
            shine = Ellipse(width=1.05, height=0.18, color=PANEL_SHINE, fill_opacity=0.55, stroke_width=0)
            shine.rotate(angle).move_to(panels[i].get_center())

            new_width = 4.2 * (i + 1) / n_panels
            new_fill = RoundedRectangle(corner_radius=0.08, width=max(new_width, 0.05), height=0.32,
                                         fill_color=ACCENT, fill_opacity=1, stroke_width=0)
            new_fill.align_to(progress_bg, LEFT)
            new_fill.match_y(progress_bg)
            new_label = Text(f"Limpando {i + 1} / {n_panels} painés", font="Arial", color=GREY).scale(0.42)
            new_label.next_to(progress_group, UP, buff=0.15)

            self.play(
                FadeOut(dusts[i], shift=DOWN * 0.4, scale=0.5),
                Transform(panels[i], new_panel),
                FadeIn(shine, scale=1.2),
                Transform(progress_fill, new_fill),
                Transform(progress_label, new_label),
                run_time=0.8,
            )
            self.play(FadeOut(shine), run_time=0.35)

        self.play(drone.animate.move_to(sun.get_center() + DOWN * 2), run_time=0.8)
        self.play(FadeOut(progress_group), FadeOut(progress_label), run_time=0.5)
        self.play(FadeOut(solution_head), run_time=0.4)

        # Efficiency
        recovery_head = Text("Resultados", font="Arial", weight=BOLD, color=ACCENT).scale(0.7)
        recovery_head.to_edge(UP, buff=0.6)
        self.play(FadeIn(recovery_head, shift=DOWN * 0.2), run_time=0.6)
        set_eff_color(ACCENT)
        self.play(eff_tracker.animate.set_value(99), run_time=1.6)

        recovered_text = Text("Geração de energia restaurada para próxima ao pico de performance", font="Arial", color=WHITE).scale(0.48)
        recovered_bg = RoundedRectangle(
            corner_radius=0.08,
            width=recovered_text.width + 0.4,
            height=recovered_text.height + 0.2,
            fill_color=BG,
            fill_opacity=1,
            stroke_width=0
        )
        recovered_group = VGroup(recovered_bg, recovered_text)
        recovered_group.next_to(solution_head, DOWN*10, buff=0.4)

        self.play(FadeIn(recovered_group, shift=UP * 0.2), run_time=2)
        self.wait(1.4)

        self.play(FadeOut(VGroup(recovery_head, recovered_group, eff_group, drone)), run_time=0.7)
        self.play(FadeOut(VGroup(ground, wall_left, wall_right, roof_under, roof_line, sun, panels)), run_time=0.7)

        # Ending
        closing_title = Text("SolarBee", font="Arial", weight=BOLD, color=WHITE_T).scale(1.0)
        closing_title.to_edge(UP, buff=1.0)

        bullets = VGroup(*[
            Text(t, font="Arial", color=WHITE_T).scale(0.55)
            for t in [
                "Sem escadas. Sem risco de acesso ao telhado.",
                "Ciclos de limpeza autônomos e programados",
                "Maximiza a geração de energia a longo prazo e o retorno sobre investimento",
            ]
        ])
        dots = VGroup(*[Dot(color=ACCENT).scale(0.8) for _ in bullets])
        rows = VGroup(*[
            VGroup(dots[i], bullets[i]).arrange(RIGHT, buff=0.3)
            for i in range(len(bullets))
        ]).arrange(DOWN, buff=0.45, aligned_edge=LEFT)
        rows.move_to(ORIGIN)

        self.play(FadeIn(closing_title, shift=UP * 0.2), run_time=0.8)
        self.play(LaggedStart(*[FadeIn(r, shift=RIGHT * 0.3) for r in rows], lag_ratio=0.3), run_time=1.8)
        self.wait(1.2)

        final_tag = Text("Painéis limpos. Sem esforço. Em qualquer altura.", font="Arial", color=ACCENT).scale(0.6)
        final_tag.to_edge(DOWN, buff=1.0)
        self.play(FadeIn(final_tag, shift=UP * 0.2), run_time=2)
        self.wait(5)

        self.play(FadeOut(VGroup(closing_title, rows, final_tag)), run_time=2.0)