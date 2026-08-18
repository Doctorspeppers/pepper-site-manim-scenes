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


def callout(text, width=12.6, font_size=26, color=WHITE):
    t = Text(text, font_size=font_size, color=color)
    if t.width > width:
        t.scale_to_fit_width(width)
    return t.to_edge(UP, buff=0.4)


def terminal_box(lines, width=11.6, height=None, font_size=18):
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

class LeCunScene(Scene):
    def construct(self):
        title = Text("A Path Towards Autonomous Machine Intelligence", font_size=28, color=WHITE)
        if title.width > 12.8:
            title.scale_to_fit_width(12.8)
        subtitle = Text("Yann LeCun, 2022 — texto de posicionamento, OpenReview", font_size=20, color=GRAY_B)
        subtitle.next_to(title, DOWN, buff=0.35)
        self.play(Write(title))
        self.play(FadeIn(subtitle))
        self.wait(5.6)
        self.play(FadeOut(title), FadeOut(subtitle))

        # --- 1. The core argument: pixels vs representations ---
        c1 = callout("O argumento central: prever pixels desperdiça capacidade em detalhe imprevisível")
        self.play(FadeIn(c1))

        pixel_box = sized_box("prever PIXELS\n(reconstrução completa)", font_size=16, color=WHITE, box_color=OLD, box_opacity=0.25, min_width=4.6, min_height=1.3, line_spacing=1.2)
        pixel_box.shift(LEFT * 3.4)
        rep_box = sized_box("prever REPRESENTAÇÕES\n(estrutura semântica)", font_size=16, color=WHITE, box_color=MECHANISM, box_opacity=0.4, min_width=4.6, min_height=1.3, line_spacing=1.2)
        rep_box.shift(RIGHT * 3.4)
        vs_row = VGroup(pixel_box, rep_box)
        assert_on_screen(vs_row, "lecun pixels vs reps")
        self.play(FadeIn(pixel_box))
        self.play(FadeIn(rep_box))
        note1 = Text("a textura exata de uma folha é imprevisível — a estrutura do mundo não precisa ser", font_size=16, color=GRAY_B)
        note1.next_to(vs_row, DOWN, buff=0.8)
        if note1.width > 12.6:
            note1.scale_to_fit_width(12.6)
        self.play(FadeIn(note1))
        self.wait(8)

        self.play(FadeOut(c1), FadeOut(vs_row), FadeOut(note1))

        # --- 1.5. Three families of self-supervised architecture ---
        c1b = callout("O próprio LeCun enquadra isso como três famílias de arquitetura", color=MECHANISM)
        self.play(FadeIn(c1b))

        je_box = sized_box("Joint-Embedding\n(x, y compatíveis -> embeddings\nsemelhantes; risco: colapso)", font_size=13, color=WHITE, box_color=OLD, box_opacity=0.25, min_width=4.0, min_height=1.5, line_spacing=1.15)
        je_box.shift(LEFT * 4.3)
        gen2_box = sized_box("Generativa\n(decoder reconstrói y\na partir de x, pixel a pixel)", font_size=13, color=WHITE, box_color=OLD, box_opacity=0.25, min_width=4.0, min_height=1.5, line_spacing=1.15)
        jepa_box = sized_box("Joint-Embedding\nPREDICTIVE (JEPA)\n(predictor prevê a\nrepresentação de y)", font_size=13, color=WHITE, box_color=MECHANISM, box_opacity=0.4, min_width=4.0, min_height=1.5, line_spacing=1.1)
        jepa_box.shift(RIGHT * 4.3)
        families_row = VGroup(je_box, gen2_box, jepa_box)
        assert_no_overlap(je_box, gen2_box, "lecun family boxes je vs gen")
        assert_no_overlap(gen2_box, jepa_box, "lecun family boxes gen vs jepa")
        assert_on_screen(families_row, "lecun three families row")
        self.play(FadeIn(je_box))
        self.play(FadeIn(gen2_box))
        self.play(FadeIn(jepa_box))
        note1b = Text("JEPA combina o melhor das duas: aprende no espaço de embeddings, mas prediz — não só compara", font_size=15, color=MECHANISM)
        note1b.next_to(families_row, DOWN, buff=0.6)
        if note1b.width > 12.6:
            note1b.scale_to_fit_width(12.6)
        self.play(FadeIn(note1b))
        self.wait(8.4)

        self.play(FadeOut(c1b), FadeOut(families_row), FadeOut(note1b))

        # --- 2. The 6-module architecture ---
        c2 = callout("A arquitetura proposta: seis módulos para aprender do mundo por observação", color=MECHANISM)
        self.play(FadeIn(c2))

        modules = [
            ("Percepção", ENCODER),
            ("Modelo de Mundo", MECHANISM),
            ("Custo", OUTPUT),
            ("Ator", DECODER),
            ("Memória de\nCurto Prazo", NORM),
            ("Configurador", FFN),
        ]
        boxes = VGroup(*[
            sized_box(name, font_size=14, color=WHITE, box_color=color, box_opacity=0.35, min_width=2.4, min_height=1.0, line_spacing=1.1)
            for name, color in modules
        ]).arrange_in_grid(rows=2, cols=3, buff=0.35)
        assert_on_screen(boxes, "lecun 6 modules grid")
        self.play(LaggedStart(*[FadeIn(b) for b in boxes], lag_ratio=0.15))
        note2 = Text("o Modelo de Mundo prevê como o mundo evolui — o núcleo compartilhado com o JEPA", font_size=16, color=MECHANISM)
        note2.next_to(boxes, DOWN, buff=0.6)
        if note2.width > 12.6:
            note2.scale_to_fit_width(12.6)
        self.play(FadeIn(note2))
        self.wait(8.4)

        self.play(FadeOut(c2), FadeOut(boxes), FadeOut(note2))

        # --- 3. The name: Joint-Embedding Predictive Architecture ---
        c3 = callout("O nome que essa ideia recebe: Joint-Embedding Predictive Architecture (JEPA)")
        self.play(FadeIn(c3))

        term = terminal_box([
            "'joint-embedding': duas entradas (contexto e alvo) mapeadas",
            "  para o MESMO espaço de representações",
            "'predictive': um módulo prevê a representação do alvo",
            "  a partir da representação do contexto — não o dado bruto",
        ], font_size=17).shift(DOWN * 0.1)
        assert_on_screen(term, "lecun jepa name terminal")
        self.play(FadeIn(term))
        self.wait(8)
        self.play(FadeOut(c3), FadeOut(term))

        # --- Closing ---
        backdrop = RoundedRectangle(corner_radius=0.2, width=13, height=3.4, fill_color="#111111", fill_opacity=0.9, stroke_width=0)
        closing = Text(
            "Um texto de posicionamento, não um paper com experimentos —\nmas o esqueleto teórico que os três papers seguintes tornam concreto.",
            font_size=26, color=WHITE, line_spacing=1.3,
        ).move_to(ORIGIN)
        if closing.width > 12.4:
            closing.scale_to_fit_width(12.4)
        self.play(FadeIn(backdrop))
        self.play(Write(closing))
        self.wait(8.4)
        self.play(FadeOut(backdrop), FadeOut(closing))
