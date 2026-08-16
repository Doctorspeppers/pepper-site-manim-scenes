from manim import *

# Explicit body font (never rely on Pango's empty-string default — it is
# inconsistent across environments). The user compared Noto Sans / P052 /
# Nimbus Roman / URW Gothic rendered side by side and initially picked P052,
# but it still showed the low-resolution spacing artifact once rendered in
# a real scene — URW Gothic (a geometric sans, heavier/simpler strokes than
# Noto Sans) held up better and is the current standard body font. Fira Code
# stays reserved for terminal_box() via _mono_font(), which passes font=
# explicitly and so overrides this default correctly for that one case.
Text.set_default(font="URW Gothic")

# Shared color language for the whole 9-video LLM series:
#   BLUE   = encoder / bidirectional path
#   ORANGE = decoder / autoregressive path
#   YELLOW = the paper's core novel mechanism (attention, selective state, etc.)
#   GREEN  = feed-forward / MLP / expert layers
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
        # A blank separator line is a Rectangle spacer, never Text("") —
        # an empty Text mobject has no points, which corrupts arrange()'s
        # spacing for every row after it.
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
    """A (box, label) pair sized to fit `text_str` at a fixed, legible
    font_size with real margin on every side — the box grows to fit the
    text, the text itself is never scaled down to fit a pre-picked box size
    (that geometric shrink is what reintroduces the illegible, uneven-spacing
    artifact that a >=16pt font_size is supposed to prevent). Accepts both
    `color`/`text_color` for the label, both `box_color`/`fill_color` for the
    box fill, and both `fill_opacity`/`box_opacity` for its opacity —
    different call sites across this series settled on different names for
    the same thing; all are honored so any of them work."""
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
    """Visible bounding frame every data-driven/multi-part diagram is built
    inside — Manim's default frame is only 8 units tall and ~14.2 wide, so
    anything not explicitly bounded like this can silently render off-screen."""
    return RoundedRectangle(corner_radius=0.15, width=width, height=height, color=GRAY_D, stroke_width=1.5).shift(UP * y_shift)


def assert_on_screen(mobj, label=""):
    """Fail the render loudly (exact coordinates, in the render script's
    stderr) instead of silently producing a video with something clipped
    off-frame. Generic, permanent check — call on every top-level group
    right before it's faded in, instead of trusting hand-computed coordinates."""
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
    """Fail loudly if two groups' bounding boxes intersect — catches the
    'diagram/caption drawn on top of another element' class of bug
    generically, instead of relying on eyeballing coordinates."""
    a_l, a_r, a_t, a_b = a.get_left()[0], a.get_right()[0], a.get_top()[1], a.get_bottom()[1]
    b_l, b_r, b_t, b_b = b.get_left()[0], b.get_right()[0], b.get_top()[1], b.get_bottom()[1]
    overlap_x = a_l < b_r and b_l < a_r
    overlap_y = a_b < b_t and b_b < a_t
    assert not (overlap_x and overlap_y), (
        f"{label}: groups overlap on screen — a=[{a_l:.2f},{a_r:.2f}]x[{a_b:.2f},{a_t:.2f}] "
        f"b=[{b_l:.2f},{b_r:.2f}]x[{b_b:.2f},{b_t:.2f}]"
    )


def diagram_row(diagram, label_text, sub_text, label_color=WHITE, sub_color=GRAY_B,
                label_font_size=18, sub_font_size=16, max_width=12.4, gap=0.6):
    """A generic 'small diagram + two-line caption' row: label stacked above
    sub with a real buff (never overlapping by construction), placed beside
    the diagram. If the combined row is too wide, only the diagram (never
    the caption text) is shrunk to fit. Returns the assembled row group —
    use `stack_rows()` to lay several of these out vertically without
    guessing buff sizes by hand."""
    label = Text(label_text, font_size=label_font_size, color=label_color)
    sub = Text(sub_text, font_size=sub_font_size, color=sub_color, line_spacing=1.1)
    caption = VGroup(label, sub).arrange(DOWN, buff=0.12, aligned_edge=LEFT)
    row = VGroup(diagram, caption).arrange(RIGHT, buff=gap)
    if row.width > max_width:
        diagram.scale_to_fit_width(diagram.width * max_width / row.width)
        row = VGroup(diagram, caption).arrange(RIGHT, buff=gap)
    return row


def uniform_boxes(texts, font_size=16, box_color=WHITE, box_opacity=0.3, margin=0.3, line_spacing=1.0, buff=0.3):
    """A row of boxes all sharing ONE size — computed from the longest text
    among them at font_size, with real margin — so a grid of short labels
    (token pieces, step numbers, expert IDs) reads as visually uniform
    without any individual box needing to shrink its own text to fit."""
    labels = [Text(t, font_size=font_size, color=WHITE, line_spacing=line_spacing) for t in texts]
    width = max(label.width for label in labels) + margin * 2
    height = max(label.height for label in labels) + margin * 2
    boxes = []
    for label in labels:
        box = RoundedRectangle(corner_radius=0.08, width=width, height=height, color=box_color,
                                fill_color=box_color, fill_opacity=box_opacity)
        label.move_to(box.get_center())
        boxes.append(VGroup(box, label))
    return VGroup(*boxes).arrange(RIGHT, buff=buff)


def sized_circle(text_str, font_size=16, color=WHITE, circle_color=WHITE, fill_opacity=0.3, margin=0.35, line_spacing=1.0):
    """Circle equivalent of sized_box() — sized to fit `text_str` with real
    margin, text never scaled down to fit a pre-picked radius."""
    label = Text(text_str, font_size=font_size, color=color, line_spacing=line_spacing)
    radius = max(label.width, label.height) / 2 + margin
    circle = Circle(radius=radius, color=circle_color, fill_color=circle_color, fill_opacity=fill_opacity)
    label.move_to(circle.get_center())
    return VGroup(circle, label)


def stack_rows(rows, buff=0.5, aligned_edge=LEFT):
    """Stack pre-built rows vertically with a generous, explicit buff, then
    verify (via `assert_no_overlap`) that no two adjacent rows actually
    collide — the check is baked into the act of stacking, so any scene using
    this helper gets the safety net for free instead of relying on hand-
    computed spacing being right on the first try."""
    group = VGroup(*rows).arrange(DOWN, buff=buff, aligned_edge=aligned_edge)
    for i in range(len(rows) - 1):
        assert_no_overlap(rows[i], rows[i + 1], f"stack_rows: row {i} vs row {i+1}")
    return group


class LLaMAScene(Scene):
    def construct(self):
        title = Text("LLaMA: Open and Efficient Foundation Language Models", font_size=28, color=WHITE)
        if title.width > 12.8:
            title.scale_to_fit_width(12.8)
        subtitle = Text("Touvron et al., Meta AI, 2023", font_size=22, color=GRAY_B)
        subtitle.next_to(title, DOWN, buff=0.35)
        self.play(Write(title))
        self.play(FadeIn(subtitle))
        self.wait(3)
        self.play(FadeOut(title), FadeOut(subtitle))

        # --- 1. Chinchilla-style premise: dados > parâmetros ---
        c1 = callout("A premissa: mais dados por parâmetro compensa mais que só escalar parâmetros")
        self.play(FadeIn(c1))

        left_box = RoundedRectangle(corner_radius=0.1, width=4.2, height=2.4, color=OLD).set_fill(OLD, opacity=0.2).shift(LEFT * 3.2)
        left_label = Text("GPT-3\n175B parâmetros", font_size=20, color=OLD, line_spacing=1.2).move_to(left_box)
        right_box = RoundedRectangle(corner_radius=0.1, width=3.9, height=1.8, color=DECODER).set_fill(DECODER, opacity=0.35).shift(RIGHT * 3.4)
        right_label = Text("LLaMA-13B\ntreinado com mais\ntokens por parâmetro", font_size=17, color=WHITE, line_spacing=1.2).move_to(right_box)
        vs = Text("supera em benchmarks", font_size=18, color=MECHANISM).move_to(ORIGIN + DOWN * 1.6)
        self.play(FadeIn(left_box), FadeIn(left_label))
        self.play(FadeIn(right_box), FadeIn(right_label))
        self.play(FadeIn(vs))
        note = Text('"LLaMA-13B supera o GPT-3 (175B) na maioria dos benchmarks" — dez vezes menor', font_size=17, color=GRAY_B)
        note.next_to(VGroup(left_box, right_box), DOWN, buff=1.3)
        if note.width > 12.6:
            note.scale_to_fit_width(12.6)
        self.play(FadeIn(note))
        self.wait(5)

        premise_group = VGroup(left_box, left_label, right_box, right_label, vs, note)
        self.play(FadeOut(c1), FadeOut(premise_group))

        # --- 2. Three architectural swaps: overview ---
        c2 = callout("Três trocas que viraram padrão em quase todo LLM decoder-only aberto desde então")
        self.play(FadeIn(c2))

        swaps = [
            ("LayerNorm", "RMSNorm", NORM, "normaliza só a escala, mais barato"),
            ("ReLU (FFN)", "SwiGLU", FFN, "ativação suave, melhor desempenho"),
            ("posição absoluta", "RoPE", POSITION, "posição relativa via rotação"),
        ]
        rows = VGroup()
        for old_name, new_name, color, desc in swaps:
            old_box = RoundedRectangle(corner_radius=0.08, width=2.9, height=0.75, color=OLD).set_fill(OLD, opacity=0.2)
            old_t = Text(old_name, font_size=16, color=OLD).move_to(old_box)
            arrow = Arrow(LEFT * 0.4, RIGHT * 0.4, color=WHITE, stroke_width=3)
            new_box = RoundedRectangle(corner_radius=0.08, width=2.9, height=0.75, color=color).set_fill(color, opacity=0.35)
            new_t = Text(new_name, font_size=16, color=WHITE).move_to(new_box)
            desc_t = Text(desc, font_size=16, color=GRAY_B)
            row = VGroup(VGroup(old_box, old_t), arrow, VGroup(new_box, new_t), desc_t).arrange(RIGHT, buff=0.25)
            rows.add(row)
        rows.arrange(DOWN, buff=0.35).shift(DOWN * 0.1)
        if rows.width > 12.8:
            rows.scale_to_fit_width(12.8)
        self.play(LaggedStart(*[FadeIn(r) for r in rows], lag_ratio=0.35))
        self.wait(5)
        deep_dive_note = Text("vamos ver cada uma das três de perto", font_size=17, color=GRAY_B)
        deep_dive_note.next_to(rows, DOWN, buff=0.5)
        self.play(FadeIn(deep_dive_note))
        self.wait(2.5)

        self.play(FadeOut(c2), FadeOut(rows), FadeOut(deep_dive_note))

        # --- 2a. RMSNorm deep dive ---
        c2a = callout("RMSNorm: por que normalizar só a escala é mais barato", color=NORM)
        self.play(FadeIn(c2a))

        ln_box = RoundedRectangle(corner_radius=0.1, width=6.0, height=2.4, color=OLD).set_fill(OLD, opacity=0.15).shift(LEFT * 3.5 + UP * 0.2)
        ln_title = Text("LayerNorm", font_size=18, color=OLD).next_to(ln_box, UP, buff=0.15)
        ln_body = VGroup(
            Text("1. calcula a média μ", font_size=16, color=WHITE),
            Text("2. calcula a variância σ²", font_size=16, color=WHITE),
            Text("3. re-centra (subtrai μ)", font_size=16, color=WHITE),
            Text("4. re-escala (divide por σ)", font_size=16, color=WHITE),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.16).move_to(ln_box)

        rms_box = RoundedRectangle(corner_radius=0.1, width=6.0, height=2.4, color=NORM).set_fill(NORM, opacity=0.3).shift(RIGHT * 3.5 + UP * 0.2)
        rms_title = Text("RMSNorm", font_size=18, color=NORM).next_to(rms_box, UP, buff=0.15)
        rms_body = VGroup(
            Text("1. calcula a raiz média quadrática", font_size=16, color=WHITE),
            Text("   (root-mean-square)", font_size=16, color=WHITE),
            Text("2. re-escala por ela", font_size=16, color=WHITE),
            Text("   (sem re-centrar — pula μ)", font_size=16, color=MECHANISM),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.16).move_to(rms_box)

        self.play(FadeIn(ln_box), FadeIn(ln_title), FadeIn(ln_body))
        self.wait(2.5)
        self.play(FadeIn(rms_box), FadeIn(rms_title), FadeIn(rms_body))
        rms_note = Text("menos uma estatística pra calcular por camada, em todo forward pass", font_size=17, color=GRAY_B)
        rms_note.next_to(VGroup(ln_box, rms_box), DOWN, buff=0.6)
        if rms_note.width > 12.6:
            rms_note.scale_to_fit_width(12.6)
        self.play(FadeIn(rms_note))
        self.wait(5.5)

        rms_group = VGroup(ln_box, ln_title, ln_body, rms_box, rms_title, rms_body, rms_note)
        self.play(FadeOut(c2a), FadeOut(rms_group))

        # --- 2b. SwiGLU deep dive ---
        c2b = callout("SwiGLU: uma ativação com um portão (gate) aprendido, em vez de um corte fixo", color=FFN)
        self.play(FadeIn(c2b))

        input_box = RoundedRectangle(corner_radius=0.08, width=2.2, height=0.8, color=WHITE).set_fill(WHITE, opacity=0.1).shift(LEFT * 4.8)
        input_label = Text("entrada", font_size=16, color=WHITE).move_to(input_box)

        half_a = RoundedRectangle(corner_radius=0.08, width=2.0, height=0.8, color=FFN).set_fill(FFN, opacity=0.35).shift(LEFT * 1.5 + UP * 1.0)
        half_a_label = Text("metade A", font_size=16, color=WHITE).move_to(half_a)
        half_b = RoundedRectangle(corner_radius=0.08, width=2.0, height=0.8, color=FFN).set_fill(FFN, opacity=0.15).shift(LEFT * 1.5 + DOWN * 1.0)
        half_b_label = Text("metade B", font_size=16, color=WHITE).move_to(half_b)

        swish_box = RoundedRectangle(corner_radius=0.08, width=2.2, height=1.05, color=MECHANISM).set_fill(MECHANISM, opacity=0.4).shift(RIGHT * 1.3 + UP * 1.0)
        swish_label = Text("SiLU(A)\n= \"portão\"", font_size=16, color=WHITE, line_spacing=1.0).move_to(swish_box)

        gate_symbol = Text("×", font_size=32, color=WHITE).shift(RIGHT * 3.6)
        output_box = RoundedRectangle(corner_radius=0.08, width=2.2, height=0.8, color=FFN).set_fill(FFN, opacity=0.5).shift(RIGHT * 5.8)
        output_label = Text("saída", font_size=16, color=WHITE).move_to(output_box)

        arrow_in_a = Arrow(input_box.get_right(), half_a.get_left(), buff=0.1, color=GRAY_B, stroke_width=2)
        arrow_in_b = Arrow(input_box.get_right(), half_b.get_left(), buff=0.1, color=GRAY_B, stroke_width=2)
        arrow_a_swish = Arrow(half_a.get_right(), swish_box.get_left(), buff=0.1, color=GRAY_B, stroke_width=2)
        arrow_swish_gate = Arrow(swish_box.get_right(), gate_symbol.get_left(), buff=0.1, color=GRAY_B, stroke_width=2)
        arrow_b_gate = Arrow(half_b.get_right(), gate_symbol.get_left() + DOWN * 0.3, buff=0.1, color=GRAY_B, stroke_width=2)
        arrow_gate_out = Arrow(gate_symbol.get_right(), output_box.get_left(), buff=0.1, color=GRAY_B, stroke_width=2)

        self.play(FadeIn(input_box), FadeIn(input_label))
        self.play(GrowArrow(arrow_in_a), GrowArrow(arrow_in_b), FadeIn(half_a), FadeIn(half_a_label), FadeIn(half_b), FadeIn(half_b_label))
        self.wait(2)
        self.play(GrowArrow(arrow_a_swish), FadeIn(swish_box), FadeIn(swish_label))
        self.wait(2)
        self.play(GrowArrow(arrow_swish_gate), GrowArrow(arrow_b_gate), FadeIn(gate_symbol))
        self.play(GrowArrow(arrow_gate_out), FadeIn(output_box), FadeIn(output_label))
        swiglu_note = Text("o portão decide, dimensão a dimensão, quanto de B passa adiante", font_size=17, color=GRAY_B)
        swiglu_note.to_edge(DOWN, buff=0.5)
        if swiglu_note.width > 12.6:
            swiglu_note.scale_to_fit_width(12.6)
        self.play(FadeIn(swiglu_note))
        self.wait(5)

        swiglu_group = VGroup(
            input_box, input_label, half_a, half_a_label, half_b, half_b_label, swish_box, swish_label,
            gate_symbol, output_box, output_label, arrow_in_a, arrow_in_b, arrow_a_swish, arrow_swish_gate,
            arrow_b_gate, arrow_gate_out, swiglu_note,
        )
        self.play(FadeOut(c2b), FadeOut(swiglu_group))

        # --- 2c. RoPE deep dive ---
        c2c = callout("RoPE: em vez de somar posição, rotaciona o vetor por um ângulo proporcional a ela", color=POSITION)
        self.play(FadeIn(c2c))

        # Built centered (using the full frame width) first, so every label
        # has room to breathe — then shrunk and slid to the LEFT as one
        # animated step, which *guarantees* the right half of the frame is
        # empty before the terminal box ever appears there, rather than
        # relying on hand-computed coordinates for two independently-placed
        # groups to not collide (that's what caused the circle/terminal
        # overlap here before).
        circle = Circle(radius=1.8, color=GRAY_D, stroke_width=1.5)
        center_dot = Dot(circle.get_center(), color=WHITE, radius=0.05)
        vec_m = Arrow(circle.get_center(), circle.get_center() + np.array([1.8 * np.cos(0.4), 1.8 * np.sin(0.4), 0]), buff=0, color=POSITION, stroke_width=4)
        vec_m_label = Text("token na posição m", font_size=16, color=POSITION).next_to(vec_m.get_end(), UR, buff=0.1)
        vec_n = Arrow(circle.get_center(), circle.get_center() + np.array([1.8 * np.cos(1.3), 1.8 * np.sin(1.3), 0]), buff=0, color=MECHANISM, stroke_width=4)
        vec_n_label = Text("token na posição n", font_size=16, color=MECHANISM).next_to(vec_n.get_end(), UL, buff=0.1)
        angle_arc = Arc(radius=0.6, start_angle=0.4, angle=1.3 - 0.4, arc_center=circle.get_center(), color=WHITE)
        angle_label = Text("ângulo ∝ (m - n)", font_size=16, color=WHITE).next_to(angle_arc, RIGHT, buff=0.2)

        rope_diagram = VGroup(circle, center_dot, vec_m, vec_m_label, vec_n, vec_n_label, angle_arc, angle_label)

        self.play(Create(circle), FadeIn(center_dot))
        self.play(GrowArrow(vec_m), FadeIn(vec_m_label))
        self.wait(2)
        self.play(GrowArrow(vec_n), FadeIn(vec_n_label))
        self.wait(2)
        self.play(Create(angle_arc), FadeIn(angle_label))
        self.wait(2.5)

        # Shrink + slide left, clearing the right half of the frame. (Exact
        # gap verified via assert_no_overlap below — measured overlap of the
        # first attempt showed the diagram's right edge at x=-0.09 against
        # the terminal's left edge at x=-0.50; shifting the diagram an
        # additional 0.8 units left clears it with real margin.)
        self.play(rope_diagram.animate.scale(0.72).shift(LEFT * 4.0))

        rope_term = terminal_box([
            "cada par de dimensões do vetor Q/K",
            "gira por um ângulo proporcional",
            "à posição do token",
            "",
            "produto escalar entre vetores rotacionados",
            "-> codifica a distância relativa (m - n),",
            "   não a posição absoluta",
        ], font_size=16, width=7.4).shift(RIGHT * 3.2)
        assert_on_screen(rope_diagram, "rope_diagram")
        assert_on_screen(rope_term, "rope_term")
        assert_no_overlap(rope_diagram, rope_term, "rope_diagram vs rope_term")
        self.play(FadeIn(rope_term))
        self.wait(5.5)

        rope_group = VGroup(rope_diagram, rope_term)
        self.play(FadeOut(c2c), FadeOut(rope_group))

        # --- 3. Decoder-only stack recap with the new pieces ---
        c3 = callout("O bloco decoder do LLaMA, com as três peças novas no lugar")
        self.play(FadeIn(c3))

        blocks = VGroup(*[
            RoundedRectangle(corner_radius=0.08, width=3.7, height=0.65, color=c).set_fill(c, opacity=0.3)
            for c in [NORM, MECHANISM, NORM, FFN]
        ])
        names = ["RMSNorm", "Self-Attention + RoPE", "RMSNorm", "SwiGLU Feed-Forward"]
        labeled = VGroup(*[
            VGroup(b, Text(n, font_size=16, color=WHITE).move_to(b)) for b, n in zip(blocks, names)
        ]).arrange(DOWN, buff=0.18)
        outline = SurroundingRectangle(labeled, color=DECODER, buff=0.25, corner_radius=0.1)
        stack_label = Text("Decoder (LLaMA)", font_size=20, color=DECODER).next_to(outline, UP, buff=0.15)
        nx = Text("× N (32 camadas no LLaMA-7B)", font_size=16, color=GRAY_B).next_to(outline, DOWN, buff=0.12)
        stack = VGroup(outline, labeled, stack_label, nx).shift(DOWN * 0.2)
        self.play(FadeIn(stack))
        self.wait(4.5)

        self.play(FadeOut(c3), FadeOut(stack))

        # --- 4. Release strategy: multiple sizes together ---
        c4 = callout("A estratégia de lançamento importou tanto quanto a arquitetura em si")
        self.play(FadeIn(c4))

        sizes = ["7B", "13B", "33B", "65B"]
        size_boxes = VGroup(*[
            RoundedRectangle(corner_radius=0.08, width=2.2, height=1.4 + i * 0.35, color=DECODER).set_fill(DECODER, opacity=0.2 + i * 0.12)
            for i in range(len(sizes))
        ]).arrange(RIGHT, buff=0.4, aligned_edge=DOWN).shift(DOWN * 0.3)
        size_labels = VGroup(*[Text(s, font_size=18, color=WHITE).move_to(b) for s, b in zip(sizes, size_boxes)])
        self.play(LaggedStart(*[FadeIn(VGroup(b, l)) for b, l in zip(size_boxes, size_labels)], lag_ratio=0.25))
        release_note = Text("todos lançados juntos — cada equipe escolhe o tamanho pelo seu orçamento de compute", font_size=17, color=GRAY_B)
        release_note.next_to(size_boxes, DOWN, buff=0.7)
        if release_note.width > 12.6:
            release_note.scale_to_fit_width(12.6)
        self.play(FadeIn(release_note))
        self.wait(5)

        release_group = VGroup(size_boxes, size_labels, release_note)
        self.play(FadeOut(c4), FadeOut(release_group))

        # --- 5. Open training data ---
        c5 = callout("Treinado só com dados publicamente disponíveis — sem corpora proprietários", color=MECHANISM)
        self.play(FadeIn(c5))

        term = terminal_box([
            "fontes: CommonCrawl, C4, GitHub, Wikipedia,",
            "        livros, ArXiv, StackExchange",
            "",
            "resultado: pesos redistribuíveis pela comunidade —",
            "a base de quase todo fine-tune aberto que veio depois",
        ], font_size=17, width=12.4).shift(DOWN * 0.1)
        self.play(FadeIn(term))
        self.wait(5.5)

        self.play(FadeOut(c5), FadeOut(term))

        # --- Closing ---
        backdrop = RoundedRectangle(corner_radius=0.2, width=13, height=3.4, fill_color="#111111", fill_opacity=0.9, stroke_width=0)
        closing = Text(
            "RMSNorm, SwiGLU e RoPE: a base decoder-only que quase\ntodo LLM aberto usa desde 2023 — e pesos abertos, em vários\ntamanhos, que a comunidade pôde de fato rodar e adaptar.",
            font_size=26, color=WHITE, line_spacing=1.3,
        ).move_to(ORIGIN)
        if closing.width > 12.4:
            closing.scale_to_fit_width(12.4)
        self.play(FadeIn(backdrop))
        self.play(Write(closing))
        self.wait(5)
        self.play(FadeOut(backdrop), FadeOut(closing))
