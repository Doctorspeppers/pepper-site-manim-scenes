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


class TransformerScene(Scene):
    def construct(self):
        title = Text("Attention Is All You Need", font_size=40, color=WHITE)
        subtitle = Text("Vaswani et al., Google Brain / Google Research, 2017", font_size=24, color=GRAY_B)
        subtitle.next_to(title, DOWN, buff=0.35)
        self.play(Write(title))
        self.play(FadeIn(subtitle))
        self.wait(3)
        self.play(FadeOut(title), FadeOut(subtitle))

        # --- 1. The problem: sequential recurrence ---
        c1 = callout("Antes: RNNs processam a sequência token a token")
        self.play(FadeIn(c1))

        tokens = ["O", "gato", "dormiu"]
        rnn_boxes = VGroup(*[
            RoundedRectangle(corner_radius=0.1, width=1.6, height=1.0, color=OLD).set_fill(OLD, opacity=0.25)
            for _ in tokens
        ]).arrange(RIGHT, buff=1.2).shift(UP * 0.3)
        rnn_labels = VGroup(*[
            Text(tok, font_size=22, color=WHITE).move_to(box) for tok, box in zip(tokens, rnn_boxes)
        ])
        rnn_arrows = VGroup(*[
            Arrow(rnn_boxes[i].get_right(), rnn_boxes[i + 1].get_left(), buff=0.1, color=OLD, stroke_width=4)
            for i in range(len(rnn_boxes) - 1)
        ])
        self.play(LaggedStart(*[FadeIn(b) for b in rnn_boxes], lag_ratio=0.3), FadeIn(rnn_labels))
        self.play(LaggedStart(*[GrowArrow(a) for a in rnn_arrows], lag_ratio=0.5))
        seq_note = Text("cada passo só começa depois que o anterior termina — sem paralelismo", font_size=18, color=OLD)
        seq_note.next_to(rnn_boxes, DOWN, buff=0.5)
        self.play(FadeIn(seq_note))
        self.wait(3)

        # NEW: why this specifically breaks down on long sequences
        decay_note = Text(
            "e quanto mais distante a informação precisa viajar, mais ela se degrada\n"
            "no caminho (o problema do gradiente que desaparece)",
            font_size=17, color=OLD, line_spacing=1.3,
        )
        decay_note.next_to(seq_note, DOWN, buff=0.4)
        if decay_note.width > 12.6:
            decay_note.scale_to_fit_width(12.6)
        fade_arrow = Arrow(rnn_boxes[0].get_top(), rnn_boxes[-1].get_top(), buff=0.1, color=OLD, stroke_width=3)
        fade_arrow.shift(UP * 0.5)
        fade_arrow.set_stroke(opacity=0.5)
        long_note = Text("dependência de longo alcance: 'gato' precisa 'lembrar' de 'O' vários passos depois", font_size=16, color=GRAY_B)
        long_note.next_to(decay_note, DOWN, buff=0.35)
        if long_note.width > 12.6:
            long_note.scale_to_fit_width(12.6)
        self.play(GrowArrow(fade_arrow))
        self.play(FadeIn(decay_note))
        self.play(FadeIn(long_note))
        self.wait(4.5)

        rnn_group = VGroup(rnn_boxes, rnn_labels, rnn_arrows, seq_note, decay_note, fade_arrow, long_note)
        self.play(FadeOut(c1), FadeOut(rnn_group))

        # --- 2. Self-attention: all-to-all in parallel ---
        c2 = callout("Depois: self-attention — todo token atende a todos, ao mesmo tempo", color=MECHANISM)
        self.play(FadeIn(c2))

        dots = VGroup(*[Dot(radius=0.14, color=ENCODER) for _ in tokens]).arrange(RIGHT, buff=1.6).shift(DOWN * 0.2)
        dot_labels = VGroup(*[
            Text(tok, font_size=20, color=WHITE).next_to(d, DOWN, buff=0.25) for tok, d in zip(tokens, dots)
        ])
        self.play(LaggedStart(*[FadeIn(d) for d in dots], lag_ratio=0.2), FadeIn(dot_labels))

        pairs = [(i, j) for i in range(len(dots)) for j in range(len(dots)) if i != j]
        attn_lines = VGroup(*[
            Line(dots[i].get_center(), dots[j].get_center(), color=MECHANISM, stroke_width=2, stroke_opacity=0.7)
            for i, j in pairs
        ])
        self.play(LaggedStart(*[Create(l) for l in attn_lines], lag_ratio=0.05, run_time=2))
        par_note = Text("todas as conexões existem simultaneamente — o mesmo cálculo paraleliza", font_size=18, color=MECHANISM)
        par_note.next_to(dots, DOWN, buff=0.9)
        self.play(FadeIn(par_note))
        self.wait(3.5)

        attn_group = VGroup(dots, dot_labels, attn_lines, par_note)
        self.play(FadeOut(c2), FadeOut(attn_group))

        # --- 3. Scaled dot-product attention formula ---
        c3 = callout("Scaled dot-product attention: cada token vira uma Query, uma Key e um Value")
        self.play(FadeIn(c3))

        formula = MathTex(
            r"\text{Attention}(Q,K,V) = \text{softmax}\left(\frac{QK^T}{\sqrt{d_k}}\right)V",
            font_size=40,
            color=WHITE,
        ).shift(UP * 1.6)
        self.play(Write(formula))
        self.wait(2.5)

        term = terminal_box([
            "Q · Kᵀ  → quão relevante cada token é para os outros",
            "/ sqrt(d_k)  → estabiliza a escala antes do softmax",
            "softmax(...)  → converte em pesos que somam 1",
            "... · V  → combina os Values pesados pela atenção",
        ]).next_to(formula, DOWN, buff=0.5)
        self.play(FadeIn(term))
        self.wait(4.5)

        self.play(FadeOut(c3), FadeOut(formula), FadeOut(term))

        # NEW: worked toy numeric example
        c3b = callout("Um exemplo numérico de verdade: 'gato' como query, contra 3 keys")
        self.play(FadeIn(c3b))

        toy_term = terminal_box([
            "query = 'gato'   keys = ['O', 'gato', 'dormiu']",
            "",
            "similaridade (Q·Kᵀ/√dk):    2.1        4.8         1.3",
            "após softmax(...):          0.09       0.85        0.06",
            "",
            "saída = 0.09·V(O) + 0.85·V(gato) + 0.06·V(dormiu)",
            "         -> a saída é dominada pelo próprio 'gato' (peso 0.85)",
        ], font_size=17).shift(DOWN * 0.3)
        self.play(FadeIn(toy_term))
        self.wait(5.5)

        self.play(FadeOut(c3b), FadeOut(toy_term))

        # --- 4. Multi-head attention ---
        c4 = callout("Multi-head attention: várias 'cabeças' atendem em paralelo, cada uma focando em algo diferente")
        self.play(FadeIn(c4))

        head_colors = [MECHANISM, "#f9a825", "#ffd54f", "#fff176"]
        heads = VGroup()
        for i, hc in enumerate(head_colors):
            head_dots = VGroup(*[Dot(radius=0.09, color=ENCODER) for _ in tokens]).arrange(RIGHT, buff=0.8)
            head_lines = VGroup(*[
                Line(head_dots[a].get_center(), head_dots[b].get_center(), color=hc, stroke_width=2, stroke_opacity=0.8)
                for a in range(len(head_dots)) for b in range(len(head_dots)) if a != b
            ])
            head_box = VGroup(head_lines, head_dots)
            heads.add(head_box)
        heads.arrange(DOWN, buff=0.35).scale(0.9).shift(DOWN * 0.2)
        self.play(LaggedStart(*[FadeIn(h) for h in heads], lag_ratio=0.3))
        concat_arrow = Arrow(heads.get_right() + RIGHT * 0.3, heads.get_right() + RIGHT * 1.6, color=WHITE)
        concat_label = Text("concat + projeção linear", font_size=18, color=WHITE).next_to(concat_arrow, RIGHT, buff=0.2)
        self.play(GrowArrow(concat_arrow), FadeIn(concat_label))
        self.wait(3.5)

        mha_group = VGroup(heads, concat_arrow, concat_label)
        self.play(FadeOut(c4), FadeOut(mha_group))

        # NEW: why multiple heads help — each can specialize
        c4b = callout("Por que várias cabeças? Cada uma pode aprender um tipo diferente de relação")
        self.play(FadeIn(c4b))

        example_sentence = "O gato que estava com fome comeu a ração"
        sent_text = Text(example_sentence, font_size=20, color=WHITE).shift(UP * 1.4)
        self.play(Write(sent_text))

        head1_note = terminal_box([
            "cabeça 1 (sintaxe):    'comeu' <-> 'gato'  (sujeito do verbo)",
        ], font_size=16).shift(UP * 0.1)
        head1_note[0].set_stroke(MECHANISM, width=2)
        self.play(FadeIn(head1_note))
        self.wait(3)

        head2_note = terminal_box([
            "cabeça 2 (correferência):    'que' <-> 'gato'  (mesmo referente)",
        ], font_size=16).next_to(head1_note, DOWN, buff=0.3)
        head2_note[0].set_stroke("#f9a825", width=2)
        self.play(FadeIn(head2_note))
        spec_note = Text("cada cabeça aprende seu próprio padrão de atenção durante o treino", font_size=16, color=GRAY_B)
        spec_note.next_to(head2_note, DOWN, buff=0.5)
        if spec_note.width > 12.6:
            spec_note.scale_to_fit_width(12.6)
        self.play(FadeIn(spec_note))
        self.wait(4.5)

        heads_example_group = VGroup(sent_text, head1_note, head2_note, spec_note)
        self.play(FadeOut(c4b), FadeOut(heads_example_group))

        # --- 5. Positional encoding ---
        c5 = callout("Atenção não tem noção de ordem — posição é somada às embeddings", color=POSITION)
        self.play(FadeIn(c5))

        emb_boxes = VGroup(*[
            RoundedRectangle(corner_radius=0.08, width=1.4, height=0.7, color=ENCODER).set_fill(ENCODER, opacity=0.3)
            for _ in tokens
        ]).arrange(RIGHT, buff=1.0).shift(UP * 0.3)
        emb_labels = VGroup(*[Text(t, font_size=18, color=WHITE).move_to(b) for t, b in zip(tokens, emb_boxes)])
        pos_boxes = VGroup(*[
            RoundedRectangle(corner_radius=0.08, width=1.4, height=0.7, color=POSITION).set_fill(POSITION, opacity=0.3).next_to(b, DOWN, buff=0.8)
            for b in emb_boxes
        ])
        pos_labels = VGroup(*[
            Text(f"pos {i}", font_size=16, color=WHITE).move_to(b) for i, b in enumerate(pos_boxes)
        ])
        plus_signs = VGroup(*[
            Text("+", font_size=24, color=WHITE).move_to((e.get_center() + p.get_center()) / 2)
            for e, p in zip(emb_boxes, pos_boxes)
        ])
        self.play(FadeIn(emb_boxes), FadeIn(emb_labels))
        self.play(FadeIn(pos_boxes), FadeIn(pos_labels), FadeIn(plus_signs))
        pe_note = Text("codificação senoidal: cada posição vira um padrão fixo de seno/cosseno", font_size=17, color=POSITION)
        pe_note.next_to(pos_boxes, DOWN, buff=0.6)
        self.play(FadeIn(pe_note))
        self.wait(3.5)

        pe_group = VGroup(emb_boxes, emb_labels, pos_boxes, pos_labels, plus_signs, pe_note)
        self.play(FadeOut(c5), FadeOut(pe_group))

        # --- 6. Full architecture: encoder-decoder stack ---
        c6 = callout("A arquitetura completa: pilhas de encoder e decoder, cada uma com N=6 camadas")
        self.play(FadeIn(c6))

        def make_stack(color, label_text, sublayers):
            # Block width/height are sized to comfortably fit the longest
            # label ("Masked Self-Attention", 21 chars) at font_size=16 with
            # real margin on all sides — the whole stack is then positioned
            # by shifting only (no group .scale() afterward), since scaling
            # an assembled VGroup shrinks its text below the 16pt floor just
            # as surely as calling .scale()/.scale_to_fit_width() on the
            # Text directly would.
            layer = VGroup()
            blocks = VGroup()
            for name, block_color in sublayers:
                b = RoundedRectangle(corner_radius=0.08, width=4.0, height=0.6, color=block_color).set_fill(block_color, opacity=0.3)
                t = Text(name, font_size=16, color=WHITE).move_to(b)
                blocks.add(VGroup(b, t))
            blocks.arrange(DOWN, buff=0.1)
            outline = SurroundingRectangle(blocks, color=color, buff=0.2, corner_radius=0.1)
            label = Text(label_text, font_size=18, color=color).next_to(outline, UP, buff=0.15)
            nx = Text("× N", font_size=16, color=GRAY_B).next_to(outline, DOWN, buff=0.1)
            return VGroup(outline, blocks, label, nx)

        enc_stack = make_stack(ENCODER, "Encoder", [
            ("Self-Attention", MECHANISM),
            ("Add & Norm", NORM),
            ("Feed-Forward", FFN),
            ("Add & Norm", NORM),
        ])
        dec_stack = make_stack(DECODER, "Decoder", [
            ("Masked Self-Attention", MECHANISM),
            ("Add & Norm", NORM),
            ("Cross-Attention", MECHANISM),
            ("Add & Norm", NORM),
            ("Feed-Forward", FFN),
            ("Add & Norm", NORM),
        ])
        enc_stack.shift(LEFT * 3.4 + DOWN * 0.1)
        dec_stack.shift(RIGHT * 3.0 + DOWN * 0.35)

        cross_arrow = Arrow(
            enc_stack.get_right(), dec_stack.get_left(), color=WHITE, stroke_width=3, buff=0.1
        )

        # Placed BELOW the whole two-stack group (not above the arrow, which
        # sits at the stacks' vertical midpoint and collided with the taller
        # decoder stack's own blocks) — with its own dark backdrop so it
        # reads cleanly even this close to the diagram.
        stacks_group = VGroup(enc_stack, dec_stack)
        cross_label = Text("saída do encoder alimenta cada camada do decoder", font_size=16, color=WHITE)
        if cross_label.width > 12.6:
            cross_label.scale_to_fit_width(12.6)
        cross_label.next_to(stacks_group, DOWN, buff=0.45)
        cross_label_bg = RoundedRectangle(
            corner_radius=0.08, width=cross_label.width + 0.5, height=cross_label.height + 0.35,
            color=GRAY_D, fill_color="#000000", fill_opacity=0.75, stroke_width=0,
        ).move_to(cross_label)

        assert_on_screen(VGroup(stacks_group, cross_arrow), "transformer arch stacks+arrow")
        assert_on_screen(cross_label_bg, "cross_label_bg")
        assert_no_overlap(stacks_group, cross_label_bg, "stacks vs cross_label")

        self.play(FadeIn(enc_stack))
        self.play(FadeIn(dec_stack))
        self.play(GrowArrow(cross_arrow))
        self.play(FadeIn(cross_label_bg), FadeIn(cross_label))
        self.wait(4.2)

        arch_group = VGroup(enc_stack, dec_stack, cross_arrow, cross_label_bg, cross_label)
        self.play(FadeOut(c6), FadeOut(arch_group))

        # NEW: end-to-end translation walkthrough
        c7 = callout("De ponta a ponta: como 'O gato' vira 'The cat', passo a passo")
        self.play(FadeIn(c7))

        container = RoundedRectangle(corner_radius=0.15, width=12.8, height=5.2, color=GRAY_D, stroke_width=1.5).shift(DOWN * 0.4)
        self.play(Create(container))

        enc_box = RoundedRectangle(corner_radius=0.1, width=3.2, height=1.6, color=ENCODER).set_fill(ENCODER, opacity=0.3)
        enc_box.move_to(container.get_left() + RIGHT * 2.4 + UP * 1.1)
        enc_in = Text("O gato", font_size=18, color=WHITE).next_to(enc_box, UP, buff=0.2)
        enc_out_label = Text("Encoder", font_size=16, color=ENCODER).move_to(enc_box)

        dec_box = RoundedRectangle(corner_radius=0.1, width=3.2, height=1.6, color=DECODER).set_fill(DECODER, opacity=0.3)
        dec_box.move_to(container.get_right() + LEFT * 2.8 + UP * 1.1)
        dec_label = Text("Decoder", font_size=16, color=DECODER).move_to(dec_box)

        cross_arrow2 = Arrow(enc_box.get_right(), dec_box.get_left(), buff=0.1, color=WHITE, stroke_width=3)

        self.play(FadeIn(enc_box), FadeIn(enc_out_label), FadeIn(enc_in))
        self.play(GrowArrow(cross_arrow2))
        self.play(FadeIn(dec_box), FadeIn(dec_label))
        self.wait(2.5)

        term_out = terminal_box([
            "passo 1: decoder recebe <início> + saída do encoder  -> gera 'The'",
            "passo 2: decoder recebe <início> The  + saída do encoder  -> gera 'cat'",
            "passo 3: decoder recebe <início> The cat  + saída do encoder  -> gera <fim>",
        ], font_size=16, width=11.8).next_to(VGroup(enc_box, dec_box), DOWN, buff=0.6)
        self.play(FadeIn(term_out))
        walk_note = Text("o decoder nunca para de 'olhar' para a saída do encoder, token após token", font_size=16, color=GRAY_B)
        walk_note.next_to(term_out, DOWN, buff=0.3)
        if walk_note.width > 12.4:
            walk_note.scale_to_fit_width(12.4)
        self.play(FadeIn(walk_note))
        self.wait(5.5)

        walk_group = VGroup(container, enc_box, enc_out_label, enc_in, dec_box, dec_label, cross_arrow2, term_out, walk_note)
        self.play(FadeOut(c7), FadeOut(walk_group))

        # --- Closing ---
        backdrop = RoundedRectangle(corner_radius=0.2, width=13, height=3.2, fill_color="#111111", fill_opacity=0.9, stroke_width=0)
        closing = Text(
            "Encoder, decoder e atenção multi-head:\nquase todo modelo desta série herda uma dessas peças.",
            font_size=28, color=WHITE, line_spacing=1.3,
        ).move_to(ORIGIN)
        self.play(FadeIn(backdrop))
        self.play(Write(closing))
        self.wait(4.2)
        self.play(FadeOut(backdrop), FadeOut(closing))
