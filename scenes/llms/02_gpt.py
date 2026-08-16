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


class GPTScene(Scene):
    def construct(self):
        title = Text("Language Models are Few-Shot Learners", font_size=34, color=WHITE)
        subtitle = Text("Brown et al., OpenAI, 2020 — a linhagem GPT desde 2018", font_size=22, color=GRAY_B)
        subtitle.next_to(title, DOWN, buff=0.35)
        self.play(Write(title))
        self.play(FadeIn(subtitle))
        self.wait(3)
        self.play(FadeOut(title), FadeOut(subtitle))

        # --- 1. Decoder-only: metade do Transformer ---
        c1 = callout("GPT usa só a metade decoder do Transformer: autoregressiva, esquerda-para-direita")
        self.play(FadeIn(c1))

        names = ["Masked Self-Attention", "Add & Norm", "Feed-Forward", "Add & Norm"]
        colors_by_name = [MECHANISM, NORM, FFN, NORM]
        name_labels = [Text(n, font_size=16, color=WHITE) for n in names]
        block_width = max(3.0, max(l.width for l in name_labels) + 0.5)
        block_height = max(0.6, max(l.height for l in name_labels) + 0.4)
        labeled = VGroup()
        for label, c in zip(name_labels, colors_by_name):
            b = RoundedRectangle(corner_radius=0.08, width=block_width, height=block_height, color=c).set_fill(c, opacity=0.3)
            label.move_to(b)
            labeled.add(VGroup(b, label))
        labeled.arrange(DOWN, buff=0.18)
        outline = SurroundingRectangle(labeled, color=DECODER, buff=0.25, corner_radius=0.1)
        stack_label = Text("Decoder (GPT)", font_size=20, color=DECODER).next_to(outline, UP, buff=0.15)
        nx = Text("× N (12 em GPT-1, 96 em GPT-3)", font_size=16, color=GRAY_B).next_to(outline, DOWN, buff=0.12)
        stack = VGroup(outline, labeled, stack_label, nx).shift(DOWN * 0.2)
        self.play(FadeIn(stack))
        self.wait(4.5)

        self.play(FadeOut(c1), FadeOut(stack))

        # --- 2. Tokenização: subword / BPE ---
        c2a = callout("Antes de qualquer camada: o texto vira tokens de subpalavra (Byte-Pair Encoding)", color=POSITION)
        self.play(FadeIn(c2a))

        raw_text = Text('"tokenização"', font_size=22, color=WHITE).shift(UP * 1.6)
        arrow_tok = Arrow(raw_text.get_bottom(), raw_text.get_bottom() + DOWN * 0.9, color=GRAY_B, stroke_width=3)
        pieces = ["token", "ização"]
        piece_group = uniform_boxes(pieces, font_size=18, box_color=POSITION, box_opacity=0.3, margin=0.3)
        piece_group.arrange(RIGHT, buff=0.25).next_to(arrow_tok, DOWN, buff=0.3)
        ids_label = Text("→ ids: [14827, 3900]  (vocabulário fixo, ~50k entradas)", font_size=16, color=GRAY_B)
        ids_label.next_to(piece_group, DOWN, buff=0.5)
        if ids_label.width > 12.6:
            ids_label.scale_to_fit_width(12.6)

        self.play(FadeIn(raw_text))
        self.play(GrowArrow(arrow_tok))
        self.play(FadeIn(piece_group))
        self.play(FadeIn(ids_label))
        bpe_note = Text("palavras raras viram várias peças; palavras comuns viram uma peça só", font_size=16, color=GRAY_B)
        bpe_note.next_to(ids_label, DOWN, buff=0.4)
        if bpe_note.width > 12.6:
            bpe_note.scale_to_fit_width(12.6)
        self.play(FadeIn(bpe_note))
        self.wait(4.5)

        tok_group = VGroup(raw_text, arrow_tok, piece_group, ids_label, bpe_note)
        self.play(FadeOut(c2a), FadeOut(tok_group))

        # --- 3. Causal masking ---
        c2 = callout("Máscara causal: cada token só pode olhar para trás, nunca para a frente", color=MECHANISM)
        self.play(FadeIn(c2))

        tokens = ["O", "gato", "dormiu", "cedo"]
        dots = VGroup(*[Dot(radius=0.13, color=DECODER) for _ in tokens]).arrange(RIGHT, buff=1.3).shift(UP * 0.4)
        labels = VGroup(*[
            Text(t, font_size=18, color=WHITE).next_to(d, DOWN, buff=0.25) for t, d in zip(tokens, dots)
        ])
        self.play(FadeIn(dots), FadeIn(labels))

        allowed = VGroup()
        blocked = VGroup()
        for i in range(len(dots)):
            for j in range(len(dots)):
                if i == j:
                    continue
                line = Line(dots[i].get_center(), dots[j].get_center(), stroke_width=2)
                if j < i:
                    line.set_color(MECHANISM).set_stroke(opacity=0.8)
                    allowed.add(line)
                else:
                    line.set_color(OLD).set_stroke(opacity=0.25)
                    blocked.add(DashedVMobject(line, num_dashes=8))
        self.play(LaggedStart(*[Create(l) for l in allowed], lag_ratio=0.1))
        self.play(LaggedStart(*[Create(l) for l in blocked], lag_ratio=0.1))
        note = Text("linhas sólidas = permitido (passado)  |  tracejado = bloqueado (futuro)", font_size=16, color=GRAY_B)
        note.next_to(dots, DOWN, buff=0.9)
        self.play(FadeIn(note))
        self.wait(4.5)

        mask_group = VGroup(dots, labels, allowed, blocked, note)
        self.play(FadeOut(c2), FadeOut(mask_group))

        # --- 4. Do vetor de saída à distribuição de probabilidade ---
        c2b = callout("A última camada vira uma distribuição de probabilidade sobre todo o vocabulário", color=MECHANISM)
        self.play(FadeIn(c2b))

        candidates = [("cedo", 0.55), ("rápido", 0.25), ("bem", 0.12), ("triste", 0.08)]
        prob_bars = VGroup()
        max_h = 2.6
        base_y = DOWN * 0.6
        for i, (word, p) in enumerate(candidates):
            h = 0.3 + max_h * p
            bar = Rectangle(width=1.1, height=h, color=MECHANISM, fill_color=MECHANISM, fill_opacity=0.5)
            bar.move_to(base_y + RIGHT * (i - 1.5) * 1.8 + UP * (h / 2))
            word_label = Text(word, font_size=16, color=WHITE).next_to(bar, DOWN, buff=0.15)
            pct_label = Text(f"{int(p*100)}%", font_size=16, color=MECHANISM).next_to(bar, UP, buff=0.1)
            prob_bars.add(VGroup(bar, word_label, pct_label))
        prob_base_line = Line(LEFT * 4.2, RIGHT * 4.2, color=GRAY_D).move_to(base_y)
        self.play(Create(prob_base_line))
        self.play(LaggedStart(*[FadeIn(b) for b in prob_bars], lag_ratio=0.25))
        softmax_note = Text('softmax converte "scores" em probabilidades que somam 100%', font_size=16, color=GRAY_B)
        softmax_note.next_to(prob_bars, DOWN, buff=0.8)
        self.play(FadeIn(softmax_note))
        sample_note = Text("amostragem: temperatura baixa favorece o topo (\"cedo\"); alta permite mais variedade", font_size=16, color=GRAY_B)
        sample_note.next_to(softmax_note, DOWN, buff=0.3)
        if sample_note.width > 12.6:
            sample_note.scale_to_fit_width(12.6)
        self.play(FadeIn(sample_note))
        self.wait(5)

        prob_group = VGroup(prob_base_line, prob_bars, softmax_note, sample_note)
        self.play(FadeOut(c2b), FadeOut(prob_group))

        # --- 5. Autoregressive generation loop ---
        c3 = callout("Geração autoregressiva: um token por vez, cada saída realimenta a entrada")
        self.play(FadeIn(c3))

        term = terminal_box([
            "entrada: O gato",
            "prevê:   dormiu   → entrada: O gato dormiu",
            "prevê:   cedo     → entrada: O gato dormiu cedo",
            "prevê:   .        → entrada: O gato dormiu cedo .",
        ], font_size=19).shift(DOWN * 0.1)
        self.play(FadeIn(term))
        loop_note = Text("cada nova previsão custa uma passada inteira pela rede pelo histórico todo", font_size=16, color=GRAY_B)
        loop_note.next_to(term, DOWN, buff=0.5)
        if loop_note.width > 12.6:
            loop_note.scale_to_fit_width(12.6)
        self.play(FadeIn(loop_note))
        self.wait(5)

        self.play(FadeOut(c3), FadeOut(term), FadeOut(loop_note))

        # --- 6. Pré-treino + fine-tuning (2018) vs. few-shot (2020) ---
        c3b = callout("Dois paradigmas: GPT-1 ainda dependia de fine-tuning; GPT-3 dispensa esse passo")
        self.play(FadeIn(c3b))

        container_p = RoundedRectangle(corner_radius=0.15, width=12.8, height=5.2, color=GRAY_D, stroke_width=1.5).shift(DOWN * 0.4)
        self.play(Create(container_p))

        # Both step-1 boxes and both step-2 boxes share one size each (measured
        # from the actual longest label in that row, with real margin) so
        # nothing is cramped or overflowing regardless of text length.
        step1_texts = ["pré-treino generativo\n(texto não rotulado)", "pré-treino generativo\n(texto não rotulado)"]
        step2_texts = ["fine-tuning supervisionado\n(dados rotulados da tarefa)", "exemplos só no prompt\n(sem gradientes)"]
        step1_boxes = uniform_boxes(step1_texts, font_size=16, box_color=WHITE, margin=0.3, line_spacing=1.1)
        step2_boxes = uniform_boxes(step2_texts, font_size=16, box_color=WHITE, margin=0.3, line_spacing=1.1)
        old_step1, new_step1 = step1_boxes
        old_step2, new_step2 = step2_boxes
        old_step1[0].set_color(OLD).set_fill(OLD, opacity=0.25)
        new_step1[0].set_color(DECODER).set_fill(DECODER, opacity=0.25)
        old_step2[0].set_color(OLD).set_fill(OLD, opacity=0.5)
        new_step2[0].set_color(MECHANISM).set_fill(MECHANISM, opacity=0.5)

        old_title = Text("GPT-1 (2018)", font_size=18, color=OLD).move_to(container_p.get_top() + DOWN * 0.6 + LEFT * 3.2)
        old_step1.next_to(old_title, DOWN, buff=0.35)
        old_arrow = Arrow(old_step1.get_bottom(), old_step1.get_bottom() + DOWN * 0.7, color=GRAY_B, stroke_width=3)
        old_step2.next_to(old_arrow, DOWN, buff=0.1)

        new_title = Text("GPT-3 (2020)", font_size=18, color=DECODER).move_to(container_p.get_top() + DOWN * 0.6 + RIGHT * 3.2)
        new_step1.next_to(new_title, DOWN, buff=0.35)
        new_arrow = Arrow(new_step1.get_bottom(), new_step1.get_bottom() + DOWN * 0.7, color=MECHANISM, stroke_width=3)
        new_step2.next_to(new_arrow, DOWN, buff=0.1)

        self.play(FadeIn(old_title), FadeIn(new_title))
        self.play(FadeIn(old_step1), FadeIn(new_step1))
        self.play(GrowArrow(old_arrow), GrowArrow(new_arrow))
        self.play(FadeIn(old_step2), FadeIn(new_step2))
        self.wait(5.5)

        paradigm_group = VGroup(
            container_p, old_title, old_step1, old_arrow, old_step2,
            new_title, new_step1, new_arrow, new_step2,
        )
        self.play(FadeOut(c3b), FadeOut(paradigm_group))

        # --- 7. Scaling GPT-1 -> GPT-2 -> GPT-3 ---
        c4 = callout("A mesma receita, escalada: GPT-1 → GPT-2 → GPT-3")
        self.play(FadeIn(c4))

        container_s = RoundedRectangle(corner_radius=0.15, width=12.8, height=5.4, color=GRAY_D, stroke_width=1.5).shift(DOWN * 0.3)
        self.play(Create(container_s))

        gens = [("GPT-1\n2018", 117, "117M"), ("GPT-2\n2019", 1500, "1.5B"), ("GPT-3\n2020", 175000, "175B")]
        max_params = max(g[1] for g in gens)
        baseline_y = container_s.get_bottom()[1] + 0.7
        max_bar_height = container_s.height / 2 - 1.0
        bars = VGroup()
        for i, (name, params_val, params_label) in enumerate(gens):
            h = 0.3 + (max_bar_height - 0.3) * (params_val / max_params)
            bar = Rectangle(width=1.4, height=h, color=DECODER, fill_color=DECODER, fill_opacity=0.5)
            bar.move_to(RIGHT * (i - 1) * 2.8 + UP * (baseline_y + h / 2))
            label = Text(name, font_size=16, color=WHITE).next_to(bar, DOWN, buff=0.15)
            param_label = Text(params_label, font_size=16, color=DECODER).next_to(bar, UP, buff=0.1)
            bars.add(VGroup(bar, label, param_label))
        base_line = Line(LEFT * 4.5, RIGHT * 4.5, color=GRAY_D).move_to(UP * baseline_y)
        self.play(Create(base_line))
        self.play(LaggedStart(*[FadeIn(b) for b in bars], lag_ratio=0.4))
        scale_note = Text("~1500x mais parâmetros em 2 anos — sem mudar a arquitetura básica", font_size=17, color=GRAY_B)
        scale_note.next_to(base_line, DOWN, buff=1.4)
        self.play(FadeIn(scale_note))
        self.wait(5)

        scale_group = VGroup(container_s, base_line, bars, scale_note)
        self.play(FadeOut(c4), FadeOut(scale_group))

        # --- 8. Zero-shot vs. few-shot in-context learning ---
        c5a = callout("Zero-shot: só a instrução, sem exemplo nenhum", color=MECHANISM)
        self.play(FadeIn(c5a))

        term_zero = terminal_box([
            "Traduza para inglês: livro ->",
            "                              → \"book\"  (às vezes erra sem contexto)",
        ], font_size=18).shift(DOWN * 0.1)
        self.play(FadeIn(term_zero))
        self.wait(3.5)
        self.play(FadeOut(c5a), FadeOut(term_zero))

        c5 = callout("Few-shot: alguns exemplos no próprio prompt já bastam para acertar a tarefa", color=MECHANISM)
        self.play(FadeIn(c5))

        term2 = terminal_box([
            "Traduza para inglês:",
            "  casa -> house",
            "  gato -> cat",
            "  livro -> ",
            "                                  → \"book\"  (completado, 0 gradientes)",
        ], font_size=18).shift(DOWN * 0.1)
        self.play(FadeIn(term2))
        no_grad = Text("nenhum peso do modelo muda — o \"aprendizado\" acontece só no contexto", font_size=16, color=MECHANISM)
        no_grad.next_to(term2, DOWN, buff=0.5)
        self.play(FadeIn(no_grad))
        self.wait(5)

        fewshot_group = VGroup(term2, no_grad)
        self.play(FadeOut(c5), FadeOut(fewshot_group))

        # --- Closing ---
        backdrop = RoundedRectangle(corner_radius=0.2, width=13, height=3.2, fill_color="#111111", fill_opacity=0.9, stroke_width=0)
        closing = Text(
            "Decoder-only, causal, autoregressivo:\na receita que praticamente todo LLM de geração de texto segue.",
            font_size=27, color=WHITE, line_spacing=1.3,
        ).move_to(ORIGIN)
        if closing.width > 12.4:
            closing.scale_to_fit_width(12.4)
        self.play(FadeIn(backdrop))
        self.play(Write(closing))
        self.wait(4.5)
        self.play(FadeOut(backdrop), FadeOut(closing))
