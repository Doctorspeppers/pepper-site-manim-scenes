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


class MambaScene(Scene):
    def construct(self):
        title = Text("Mamba: Linear-Time Sequence Modeling", font_size=32, color=WHITE)
        subtitle = Text("with Selective State Spaces — Gu & Dao, CMU/Princeton, 2023", font_size=20, color=GRAY_B)
        if subtitle.width > 12.8:
            subtitle.scale_to_fit_width(12.8)
        subtitle.next_to(title, DOWN, buff=0.35)
        self.play(Write(title))
        self.play(FadeIn(subtitle))
        self.wait(3)
        self.play(FadeOut(title), FadeOut(subtitle))

        # --- 1. A pergunta fundamental ---
        c1 = callout("A pergunta por trás do paper: atenção é realmente necessária?", color=MECHANISM)
        self.play(FadeIn(c1))
        big_q = Text("E se não for?", font_size=44, color=MECHANISM)
        self.play(Write(big_q))
        self.wait(3)
        self.play(FadeOut(c1), FadeOut(big_q))

        # --- 2. O que é um State Space Model ---
        c2 = callout("Antes da seletividade: o que é um State Space Model?")
        self.play(FadeIn(c2))

        area2 = safe_container()
        self.play(Create(area2))

        x_group = sized_box("entrada xₜ", font_size=18, box_color=ENCODER, fill_color=ENCODER, fill_opacity=0.3, min_width=1.8, min_height=0.9)
        x_group.move_to(LEFT * 4.3 + UP * 0.3)
        x_box, x_label = x_group

        h_group = sized_box("estado oculto hₜ", font_size=18, box_color=MECHANISM, fill_color=MECHANISM, fill_opacity=0.35, min_width=2.2, min_height=1.1)
        h_group.move_to(UP * 0.3)
        h_box, h_label = h_group

        y_group = sized_box("saída yₜ", font_size=18, box_color=OUTPUT, fill_color=OUTPUT, fill_opacity=0.3, min_width=1.8, min_height=0.9)
        y_group.move_to(RIGHT * 4.3 + UP * 0.3)
        y_box, y_label = y_group

        arrow_xh = Arrow(x_group.get_right(), h_group.get_left(), buff=0.15, color=WHITE, stroke_width=3)
        arrow_hy = Arrow(h_group.get_right(), y_group.get_left(), buff=0.15, color=WHITE, stroke_width=3)
        recur_arrow = CurvedArrow(
            h_box.get_top() + RIGHT * 0.3, h_box.get_top() + LEFT * 0.3, color=GRAY_B, angle=-2.6
        ).shift(UP * 0.15)
        recur_label = Text("hₜ depende de hₜ₋₁ e xₜ", font_size=16, color=GRAY_B).next_to(recur_arrow, UP, buff=0.15)

        self.play(FadeIn(x_group))
        self.play(GrowArrow(arrow_xh), FadeIn(h_group))
        self.play(Create(recur_arrow), FadeIn(recur_label))
        self.play(GrowArrow(arrow_hy), FadeIn(y_group))

        ssm_note = Text(
            "origem: sistemas de controle/processamento de sinais clássicos —\num estado interno que resume tudo que já foi visto, atualizado passo a passo",
            font_size=17, color=GRAY_B, line_spacing=1.2,
        )
        ssm_note.next_to(VGroup(x_group, h_group, y_group), DOWN, buff=0.9)
        if ssm_note.width > 12.4:
            ssm_note.scale_to_fit_width(12.4)
        self.play(FadeIn(ssm_note))
        self.wait(5)

        ssm_group = VGroup(area2, x_group, h_group, y_group, arrow_xh, arrow_hy, recur_arrow, recur_label, ssm_note)
        self.play(FadeOut(c2), FadeOut(ssm_group))

        # --- 3. SSMs anteriores: parâmetros fixos ---
        c3 = callout("SSMs anteriores tinham parâmetros fixos — não decidiam o que propagar ou esquecer")
        self.play(FadeIn(c3))

        area3 = safe_container()
        self.play(Create(area3))

        tokens = ["O", "gato", "irrelevante", "dormiu"]
        dots = VGroup(*[Dot(radius=0.12, color=OLD) for _ in tokens]).arrange(RIGHT, buff=1.5).shift(UP * 0.2)
        labels = VGroup(*[Text(t, font_size=16, color=WHITE).next_to(d, DOWN, buff=0.2) for t, d in zip(tokens, dots)])
        state_line = Line(dots[0].get_center(), dots[-1].get_center(), color=OLD, stroke_width=6)
        self.play(FadeIn(dots), FadeIn(labels))
        self.play(Create(state_line))
        fixed_note = Text(
            "todo token passa pelo estado com o mesmo peso fixo — mesmo o irrelevante.\nas matrizes que controlam a atualização do estado nunca olham para o conteúdo do token",
            font_size=16, color=GRAY_B, line_spacing=1.2,
        )
        fixed_note.next_to(dots, DOWN, buff=0.9)
        if fixed_note.width > 12.4:
            fixed_note.scale_to_fit_width(12.4)
        self.play(FadeIn(fixed_note))
        self.wait(5)

        fixed_group = VGroup(area3, dots, labels, state_line, fixed_note)
        self.play(FadeOut(c3), FadeOut(fixed_group))

        # --- 4. Selective SSM: parâmetros viram função da entrada ---
        c4 = callout("Mamba: os parâmetros do SSM viram função do próprio token — seletivo", color=MECHANISM)
        self.play(FadeIn(c4))

        area4 = safe_container()
        self.play(Create(area4))

        dots2 = VGroup(*[Dot(radius=0.12, color=DECODER) for _ in tokens]).arrange(RIGHT, buff=1.5).shift(UP * 0.6)
        labels2 = VGroup(*[Text(t, font_size=16, color=WHITE).next_to(d, DOWN, buff=0.2) for t, d in zip(tokens, dots2)])
        widths = [6, 6, 1, 6]
        segs = VGroup()
        for i in range(len(dots2) - 1):
            seg = Line(dots2[i].get_center(), dots2[i + 1].get_center(), color=MECHANISM, stroke_width=widths[i])
            segs.add(seg)
        self.play(FadeIn(dots2), FadeIn(labels2))
        self.play(LaggedStart(*[Create(s) for s in segs], lag_ratio=0.3))
        sel_note = Text("'irrelevante' é filtrado — a espessura do fluxo de estado varia por conteúdo", font_size=16, color=MECHANISM)
        sel_note.next_to(dots2, DOWN, buff=0.7)
        if sel_note.width > 12.4:
            sel_note.scale_to_fit_width(12.4)
        self.play(FadeIn(sel_note))
        self.wait(3)

        term4 = terminal_box([
            "Δ, B, C (parâmetros do SSM) = função(xₜ)  — não pesos fixos e compartilhados",
            "'irrelevante' -> Δ pequeno -> quase nada entra/atualiza o estado",
            "'gato', 'dormiu' -> Δ grande -> o estado é atualizado de verdade",
            "",
            "analogia: como um portão de entrada/esquecimento decidido pelo próprio token",
        ], font_size=16, width=12.2).next_to(sel_note, DOWN, buff=0.4)
        self.play(FadeIn(term4))
        self.wait(5)

        sel_group = VGroup(area4, dots2, labels2, segs, sel_note, term4)
        self.play(FadeOut(c4), FadeOut(sel_group))

        # --- 5. Trade-off: hardware-aware parallel scan ---
        c5 = callout("O preço: perde a convolução eficiente — resolvido com um algoritmo paralelo hardware-aware")
        self.play(FadeIn(c5))

        term5 = terminal_box([
            "SSM linear clássico:  paralelizável via convolução",
            "SSM seletivo:         parâmetros variam por passo -> sem convolução direta",
            "solução Mamba:        scan paralelo hardware-aware",
        ], font_size=16).shift(UP * 1.3)
        self.play(FadeIn(term5))
        self.wait(4)

        gpu_box = RoundedRectangle(corner_radius=0.1, width=8.5, height=2.6, color=GRAY_B).set_fill(GRAY_B, opacity=0.08).shift(DOWN * 1.6)
        gpu_label = Text("GPU", font_size=16, color=GRAY_B).next_to(gpu_box, UP, buff=0.1).align_to(gpu_box, LEFT).shift(RIGHT*0.2)
        sram_group = sized_box("SRAM\n(rápida, pequena)", font_size=16, box_color=MECHANISM, fill_color=MECHANISM, fill_opacity=0.4, min_width=3.0, min_height=1.6, line_spacing=1.15)
        sram_group.move_to(gpu_box.get_center() + LEFT * 2.2)
        sram_box, sram_label = sram_group
        hbm_group = sized_box("HBM\n(grande, lenta)", font_size=16, box_color=OLD, fill_color=OLD, fill_opacity=0.25, min_width=3.4, min_height=2.0, line_spacing=1.15)
        hbm_group.move_to(gpu_box.get_center() + RIGHT * 2.3)
        hbm_box, hbm_label = hbm_group
        scan_note = Text("o scan mantém o estado inteiro dentro da SRAM — evita ida e volta pela HBM a cada passo", font_size=16, color=MECHANISM)
        scan_note.next_to(gpu_box, DOWN, buff=0.4)
        if scan_note.width > 12.4:
            scan_note.scale_to_fit_width(12.4)

        self.play(FadeIn(gpu_box), FadeIn(gpu_label))
        self.play(FadeIn(hbm_box), FadeIn(hbm_label))
        self.play(FadeIn(sram_box), FadeIn(sram_label))
        self.play(FadeIn(scan_note))
        hw_note = Text('a maior parte do ganho prático de velocidade vem daqui — não só do custo linear "no papel"', font_size=16, color=GRAY_B)
        hw_note.next_to(scan_note, DOWN, buff=0.3)
        if hw_note.width > 12.4:
            hw_note.scale_to_fit_width(12.4)
        self.play(FadeIn(hw_note))
        self.wait(5)

        hw_group = VGroup(term5, gpu_box, gpu_label, sram_box, sram_label, hbm_box, hbm_label, scan_note, hw_note)
        self.play(FadeOut(c5), FadeOut(hw_group))

        # --- 6. Memória de inferência: cache crescente vs. estado fixo ---
        c6 = callout("Na prática: memória de inferência constante, não crescente com o contexto", color=MECHANISM)
        self.play(FadeIn(c6))

        area6 = safe_container()
        self.play(Create(area6))

        tf_label = Text("Transformer (cache K/V)", font_size=16, color=OLD).shift(UP * 1.7 + LEFT * 3.0)
        tf_bars = VGroup(*[
            Rectangle(width=0.5, height=0.3 + i * 0.25, color=OLD, fill_color=OLD, fill_opacity=0.4)
            for i in range(5)
        ]).arrange(RIGHT, buff=0.15, aligned_edge=DOWN).next_to(tf_label, DOWN, buff=0.3)

        mamba_label = Text("Mamba (estado fixo)", font_size=16, color=MECHANISM).shift(UP * 1.7 + RIGHT * 3.0)
        mamba_bars = VGroup(*[
            Rectangle(width=0.5, height=0.5, color=MECHANISM, fill_color=MECHANISM, fill_opacity=0.4)
            for _ in range(5)
        ]).arrange(RIGHT, buff=0.15, aligned_edge=DOWN)
        mamba_bars.next_to(mamba_label, DOWN, buff=0.3)

        self.play(FadeIn(tf_label), FadeIn(mamba_label))
        self.play(LaggedStart(*[FadeIn(b) for b in tf_bars], lag_ratio=0.2))
        self.play(LaggedStart(*[FadeIn(b) for b in mamba_bars], lag_ratio=0.2))
        mem_note = Text(
            "cache K/V cresce a cada token novo processado  vs.\nMamba carrega um único estado de tamanho fixo, token após token, para sempre",
            font_size=16, color=GRAY_B, line_spacing=1.2,
        )
        mem_note.next_to(VGroup(tf_bars, mamba_bars), DOWN, buff=0.7)
        if mem_note.width > 12.4:
            mem_note.scale_to_fit_width(12.4)
        self.play(FadeIn(mem_note))
        self.wait(5)

        mem_group = VGroup(area6, tf_label, tf_bars, mamba_label, mamba_bars, mem_note)
        self.play(FadeOut(c6), FadeOut(mem_group))

        # --- 7. Sem attention, sem MLP ---
        c7 = callout("Resultado: um bloco sem attention e sem MLP, com custo linear no comprimento")
        self.play(FadeIn(c7))

        block_group = sized_box("Selective SSM Block", font_size=18, box_color=MECHANISM, fill_color=MECHANISM, fill_opacity=0.3, min_width=3.4, min_height=1.4)
        block, block_label = block_group
        outline = SurroundingRectangle(block, color=DECODER, buff=0.3, corner_radius=0.12)
        stack_label = Text("Mamba", font_size=20, color=DECODER).next_to(outline, UP, buff=0.15)
        nx = Text("× N — sem atenção, sem feed-forward separado", font_size=16, color=GRAY_B).next_to(outline, DOWN, buff=0.12)
        stack = VGroup(outline, block, block_label, stack_label, nx).shift(DOWN * 0.1)
        self.play(FadeIn(stack))
        perf_note = Text('"5x mais throughput de inferência que Transformers" (Mamba-3B)', font_size=16, color=MECHANISM)
        perf_note.next_to(stack, DOWN, buff=0.6)
        if perf_note.width > 12.6:
            perf_note.scale_to_fit_width(12.6)
        self.play(FadeIn(perf_note))
        self.wait(5)

        mamba_group = VGroup(stack, perf_note)
        self.play(FadeOut(c7), FadeOut(mamba_group))

        # --- Closing ---
        backdrop = RoundedRectangle(corner_radius=0.2, width=13, height=3.6, fill_color="#111111", fill_opacity=0.9, stroke_width=0)
        closing = Text(
            "Um estado oculto que decide, por conta própria, o que vale a pena\nlembrar — mantido inteiramente na memória rápida da GPU.\nA primeira resposta séria à pergunta 'atenção é mesmo necessária?'",
            font_size=25, color=WHITE, line_spacing=1.3,
        ).move_to(ORIGIN)
        if closing.width > 12.4:
            closing.scale_to_fit_width(12.4)
        self.play(FadeIn(backdrop))
        self.play(Write(closing))
        self.wait(5)
        self.play(FadeOut(backdrop), FadeOut(closing))
