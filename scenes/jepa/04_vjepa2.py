from manim import *

# Explicit body font (never rely on Pango's empty-string default — it is
# inconsistent across environments). URW Gothic is the standard body font
# for this series (Noto Sans and P052 were tried and both showed the
# low-resolution letter-spacing artifact once actually rendered in a real
# scene). Fira Code stays reserved for terminal_box() via _mono_font(),
# which passes font= explicitly and so overrides this default correctly.
Text.set_default(font="URW Gothic")

# Shared color language for this series:
#   BLUE   = frozen/trained vision (encoder) path
#   ORANGE = LLM / decoder / language path
#   YELLOW = the paper's core novel mechanism
#   GREEN  = feed-forward / projection / adapter layers
#   PURPLE = normalization
#   PINK   = positional information
#   RED    = output / logits / prediction
#   GRAY   = older-generation component being replaced

ENCODER = BLUE
DECODER = ORANGE
MECHANISM = YELLOW
FFN = GREEN
NORM = PURPLE
POSITION = PINK
OUTPUT = RED
OLD = GRAY


def _mono_font():
    return "Fira Code"


# Hard legibility floor: text below this renders with visibly uneven
# letter spacing at the render service's fixed 720p output (a
# rasterization problem, not a code problem — confirmed to reappear even
# when nothing else is wrong, e.g. a plain caption Text at font_size=13).
# Every helper below that creates Text asserts against this floor instead
# of silently accepting a too-small size, so the failure is a loud,
# immediate AssertionError at scene-authoring time, not a video a human
# has to notice is broken after it's already rendered and published.
MIN_FONT_SIZE = 16


def _assert_font_floor(font_size, label=""):
    assert font_size >= MIN_FONT_SIZE, (
        f"{label}: font_size={font_size} is below the {MIN_FONT_SIZE}pt legibility "
        f"floor — text this small reads with visibly uneven letter spacing once "
        f"actually rendered at the service's fixed 720p output, even though it "
        f"looks fine as source code. Raise font_size, don't lower the floor."
    )


def callout(text, width=12.6, font_size=26, color=WHITE):
    _assert_font_floor(font_size, "callout")
    t = Text(text, font_size=font_size, color=color)
    if t.width > width:
        t.scale_to_fit_width(width)
    return t.to_edge(UP, buff=0.4)


def safe_caption(text, font_size=16, max_width=12.6, color=WHITE, **kwargs):
    """The preferred way to build a long running caption/note. Unlike the
    ad hoc `if t.width > cap: t.scale_to_fit_width(cap)` pattern scattered
    across earlier scenes — which silently shrinks text below the
    legibility floor whenever a caption runs long, exactly the bug that
    kept recurring — this asserts loudly instead, forcing the caption to
    be shortened or split across lines (with a literal '\\n', which Text
    honors correctly) rather than auto-shrunk into illegibility."""
    _assert_font_floor(font_size, "safe_caption")
    t = Text(text, font_size=font_size, color=color, **kwargs)
    assert t.width <= max_width, (
        f"safe_caption: width={t.width:.2f} exceeds max_width={max_width} — "
        f"shorten the text or split it across lines with '\\n', don't let it "
        f"auto-shrink below the {MIN_FONT_SIZE}pt floor."
    )
    return t


def terminal_box(lines, width=11.6, height=None, font_size=18):
    _assert_font_floor(font_size, "terminal_box")

    def make_row(line):
        if line:
            return Text(line, font=_mono_font(), font_size=font_size, color=WHITE)
        return Rectangle(width=0.01, height=font_size / 72, stroke_opacity=0, fill_opacity=0)

    text_group = VGroup(*[make_row(line) for line in lines]).arrange(DOWN, aligned_edge=LEFT, buff=0.14)
    if text_group.width > width - 0.6:
        text_group.scale_to_fit_width(width - 0.6)
    if height is None:
        height = text_group.height + 0.8
    box = RoundedRectangle(
        corner_radius=0.15, width=width, height=height, fill_color="#1e1e1e", fill_opacity=1, stroke_color=GRAY_D
    )
    dots = VGroup(*[Dot(radius=0.06, color=c) for c in ["#ff5f56", "#ffbd2e", "#27c93f"]])
    dots.arrange(RIGHT, buff=0.12).move_to(box.get_corner(UL) + RIGHT * 0.35 + DOWN * 0.2)
    text_group.move_to(box.get_center()).align_to(box, LEFT).shift(RIGHT * 0.3)
    return VGroup(box, dots, text_group)


def sized_box(text_str, font_size=16, text_color=None, color=WHITE, box_color=WHITE, fill_color=None,
              fill_opacity=None, box_opacity=0.3, min_width=1.0, min_height=0.6, margin=0.3,
              corner_radius=0.08, line_spacing=1.0):
    _assert_font_floor(font_size, "sized_box")
    text_color = text_color if text_color is not None else color
    fill_color = fill_color if fill_color is not None else box_color
    fill_opacity = fill_opacity if fill_opacity is not None else box_opacity
    label = Text(text_str, font_size=font_size, color=text_color, line_spacing=line_spacing)
    width = max(min_width, label.width + margin * 2)
    height = max(min_height, label.height + margin * 2)
    box = RoundedRectangle(corner_radius=corner_radius, width=width, height=height, color=box_color,
                            fill_color=fill_color, fill_opacity=fill_opacity)
    label.move_to(box.get_center())
    return VGroup(box, label)


def safe_container(width=12.8, height=5.4, y_shift=-0.3):
    return RoundedRectangle(corner_radius=0.15, width=width, height=height, color=GRAY_D, stroke_width=1.5).shift(UP * y_shift)


def assert_on_screen(mobj, label=""):
    fw, fh = config.frame_width, config.frame_height
    left, right = mobj.get_left()[0], mobj.get_right()[0]
    top, bottom = mobj.get_top()[1], mobj.get_bottom()[1]
    assert left >= -fw / 2 - 0.05 and right <= fw / 2 + 0.05, (
        f"{label}: overflows horizontally [{left:.2f},{right:.2f}] vs frame ±{fw/2:.2f}"
    )
    assert bottom >= -fh / 2 - 0.05 and top <= fh / 2 + 0.05, (
        f"{label}: overflows vertically [{bottom:.2f},{top:.2f}] vs frame ±{fh/2:.2f}"
    )


def assert_no_overlap(a, b, label=""):
    a_l, a_r, a_t, a_b = a.get_left()[0], a.get_right()[0], a.get_top()[1], a.get_bottom()[1]
    b_l, b_r, b_t, b_b = b.get_left()[0], b.get_right()[0], b.get_top()[1], b.get_bottom()[1]
    overlap_x = a_l < b_r and b_l < a_r
    overlap_y = a_b < b_t and b_b < a_t
    assert not (overlap_x and overlap_y), (
        f"{label}: groups overlap on screen — a=[{a_l:.2f},{a_r:.2f}]x[{a_b:.2f},{a_t:.2f}] "
        f"b=[{b_l:.2f},{b_r:.2f}]x[{b_b:.2f},{b_t:.2f}]"
    )


def assert_within(inner, outer, label=""):
    i_l, i_r, i_t, i_b = inner.get_left()[0], inner.get_right()[0], inner.get_top()[1], inner.get_bottom()[1]
    o_l, o_r, o_t, o_b = outer.get_left()[0], outer.get_right()[0], outer.get_top()[1], outer.get_bottom()[1]
    assert i_l >= o_l - 0.05 and i_r <= o_r + 0.05 and i_b >= o_b - 0.05 and i_t <= o_t + 0.05, (
        f"{label}: inner=[{i_l:.2f},{i_r:.2f}]x[{i_b:.2f},{i_t:.2f}] not within outer=[{o_l:.2f},{o_r:.2f}]x[{o_b:.2f},{o_t:.2f}]"
    )


def diagram_row(diagram, label_text, sub_text, label_color=WHITE, sub_color=GRAY_B,
                label_font_size=18, sub_font_size=16, max_width=12.4, gap=0.6):
    label = Text(label_text, font_size=label_font_size, color=label_color)
    sub = Text(sub_text, font_size=sub_font_size, color=sub_color, line_spacing=1.1)
    caption = VGroup(label, sub).arrange(DOWN, buff=0.12, aligned_edge=LEFT)
    row = VGroup(diagram, caption).arrange(RIGHT, buff=gap)
    if row.width > max_width:
        diagram.scale_to_fit_width(diagram.width * max_width / row.width)
        row = VGroup(diagram, caption).arrange(RIGHT, buff=gap)
    return row


def stack_rows(rows, buff=0.5, aligned_edge=LEFT):
    group = VGroup(*rows).arrange(DOWN, buff=buff, aligned_edge=aligned_edge)
    for i in range(len(rows) - 1):
        assert_no_overlap(rows[i], rows[i + 1], f"stack_rows: row {i} vs row {i+1}")
    return group

class VJEPA2Scene(Scene):
    def construct(self):
        title = Text("V-JEPA 2", font_size=44, color=WHITE)
        subtitle = Text("Self-Supervised Video Models Enable Understanding, Prediction and Planning — Assran et al., FAIR at Meta, 2025", font_size=16, color=GRAY_B)
        if subtitle.width > 12.8:
            subtitle.scale_to_fit_width(12.8)
        subtitle.next_to(title, DOWN, buff=0.35)
        self.play(Write(title))
        self.play(FadeIn(subtitle))
        self.wait(5.6)
        self.play(FadeOut(title), FadeOut(subtitle))

        # --- 1. Closing the loop with LeCun's thesis ---
        c1 = callout('O próprio paper abre citando "(LeCun, 2022)" — fechando o círculo teórico')
        self.play(FadeIn(c1))
        term = terminal_box([
            '"um grande desafio para a IA moderna é aprender a entender',
            ' o mundo e aprender a agir, majoritariamente por observação"',
            '                                              — (LeCun, 2022)',
        ], font_size=17).shift(DOWN * 0.1)
        assert_on_screen(term, "vjepa2 lecun citation terminal")
        self.play(FadeIn(term))
        self.wait(8)
        self.play(FadeOut(c1), FadeOut(term))

        # --- 2. Two-phase training: action-free, then action-conditioned ---
        c2 = callout("Duas fases: pré-treino livre de ação, depois ajuste condicionado por ação", color=MECHANISM)
        self.play(FadeIn(c2))

        phase1 = sized_box("Fase 1: V-JEPA 2 (livre de ação)\n+1 milhão de horas de vídeo da internet", font_size=16, color=WHITE, box_color=MECHANISM, box_opacity=0.3, min_width=7.0, min_height=1.1, line_spacing=1.2)
        phase2 = sized_box("Fase 2: condicionado por ação\npequena quantidade de trajetórias de robôs reais", font_size=16, color=WHITE, box_color=DECODER, box_opacity=0.3, min_width=7.0, min_height=1.1, line_spacing=1.2)
        phases = stack_rows([phase1, phase2], buff=0.4)
        assert_on_screen(phases, "vjepa2 training phases")
        self.play(FadeIn(phase1))
        self.wait(2)
        self.play(FadeIn(phase2))
        self.wait(7)
        self.play(FadeOut(c2), FadeOut(phases))

        # --- 3. Planning by imagining outcomes ---
        c3 = callout("Planejar: escolher a ação cuja representação futura prevista é mais desejável", color=MECHANISM)
        self.play(FadeIn(c3))

        state = sized_box("estado\natual", font_size=16, color=WHITE, box_color=ENCODER, box_opacity=0.35, min_width=1.8, min_height=1.0, line_spacing=1.1)
        state.shift(LEFT * 4.6)
        actions = VGroup(*[
            sized_box(f"ação {i+1}", font_size=16, color=WHITE, box_color=DECODER, box_opacity=0.3, min_width=1.4, min_height=0.7)
            for i in range(3)
        ]).arrange(DOWN, buff=0.25)
        futures = VGroup(*[
            sized_box(f"repr.\nfutura {i+1}", font_size=16, color=WHITE, box_color=MECHANISM, box_opacity=0.3 if i != 1 else 0.6, min_width=1.6, min_height=0.9, line_spacing=1.0)
            for i in range(3)
        ]).arrange(DOWN, buff=0.25)

        row = VGroup(state, actions, futures).arrange(RIGHT, buff=1.1)
        arrows1 = VGroup(*[Arrow(state.get_right(), a.get_left(), buff=0.08, color=GRAY_B, stroke_width=2) for a in actions])
        arrows2 = VGroup(*[Arrow(a.get_right(), f.get_left(), buff=0.08, color=GRAY_B, stroke_width=2) for a, f in zip(actions, futures)])

        plan_group = VGroup(row, arrows1, arrows2)
        if plan_group.width > 12.6:
            plan_group.scale_to_fit_width(12.6)
        assert_on_screen(plan_group, "vjepa2 planning diagram")
        self.play(FadeIn(state))
        self.play(FadeIn(actions), *[GrowArrow(a) for a in arrows1])
        self.play(FadeIn(futures), *[GrowArrow(a) for a in arrows2])
        note1 = Text("nenhum pixel é gerado — só representações previstas, comparadas por custo desejado", font_size=16, color=MECHANISM)
        note1.next_to(plan_group, DOWN, buff=0.6)
        if note1.width > 12.6:
            note1.scale_to_fit_width(12.6)
        self.play(FadeIn(note1))
        self.wait(8.4)

        self.play(FadeOut(c3), FadeOut(plan_group), FadeOut(note1))

        # --- 3.5. Concrete robot setup: what was actually tested ---
        c3b = callout("O teste concreto: braços robóticos Franka, em dois laboratórios diferentes", color=MECHANISM)
        self.play(FadeIn(c3b))
        term_robot = terminal_box([
            "V-JEPA 2-AC: pós-treinado com menos de 62 horas de vídeo",
            "  de robôs não rotulado (dataset Droid)",
            "implantado ZERO-SHOT em braços Franka em 2 laboratórios",
            "  distintos -> pick-and-place de objetos por planejamento",
            "  com metas em imagem (image goals)",
            "sem coletar NENHUM dado desses robôs específicos,",
            "  e sem treino ou recompensa específicos para a tarefa",
        ], font_size=16).shift(DOWN * 0.1)
        assert_on_screen(term_robot, "vjepa2 robot setup terminal")
        self.play(FadeIn(term_robot))
        self.wait(8.4)
        self.play(FadeOut(c3b), FadeOut(term_robot))

        # --- 4. Result ---
        c4 = callout("O resultado citado no próprio paper:")
        self.play(FadeIn(c4))
        term2 = terminal_box([
            '"77,3% top-1 no Something-Something v2" (entendimento de movimento)',
            '"39,7 recall-at-5 no Epic-Kitchens-100" (antecipação de ação),',
            ' superando modelos específicos para essa tarefa',
        ], font_size=16).shift(DOWN * 0.1)
        assert_on_screen(term2, "vjepa2 result terminal")
        self.play(FadeIn(term2))
        self.wait(8.4)
        self.play(FadeOut(c4), FadeOut(term2))

        # --- Closing: recap the whole JEPA group ---
        backdrop = RoundedRectangle(corner_radius=0.2, width=13, height=3.6, fill_color="#111111", fill_opacity=0.9, stroke_width=0)
        closing = Text(
            "LeCun propôs prever representações, não pixels;\nI-JEPA tornou isso concreto em imagens; V-JEPA levou a vídeo;\nV-JEPA 2 fechou o ciclo — de observar o mundo a planejar ações nele.",
            font_size=23, color=WHITE, line_spacing=1.3,
        ).move_to(ORIGIN)
        if closing.width > 12.4:
            closing.scale_to_fit_width(12.4)
        self.play(FadeIn(backdrop))
        self.play(Write(closing))
        self.wait(9)
        self.play(FadeOut(backdrop), FadeOut(closing))
