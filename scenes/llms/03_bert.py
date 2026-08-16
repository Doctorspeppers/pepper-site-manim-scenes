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


class BERTScene(Scene):
    def construct(self):
        title = Text("BERT: Pre-training of Deep Bidirectional Transformers", font_size=30, color=WHITE)
        subtitle = Text("Devlin et al., Google AI Language, 2018", font_size=22, color=GRAY_B)
        if title.width > 12.8:
            title.scale_to_fit_width(12.8)
        subtitle.next_to(title, DOWN, buff=0.35)
        self.play(Write(title))
        self.play(FadeIn(subtitle))
        self.wait(2.8)
        self.play(FadeOut(title), FadeOut(subtitle))

        # --- 1. Encoder-only: a outra metade ---
        c1 = callout("BERT usa só a metade encoder do Transformer: bidirecional, sem geração")
        self.play(FadeIn(c1))

        names = ["Self-Attention (bidirecional)", "Add & Norm", "Feed-Forward", "Add & Norm"]
        name_labels = [Text(n, font_size=16, color=WHITE) for n in names]
        block_width = max(n.width for n in name_labels) + 0.56  # real margin on both sides
        block_height = max(n.height for n in name_labels) + 0.36
        blocks = VGroup(*[
            RoundedRectangle(corner_radius=0.08, width=block_width, height=block_height, color=c).set_fill(c, opacity=0.3)
            for c in [MECHANISM, NORM, FFN, NORM]
        ])
        labeled = VGroup(*[
            VGroup(b, lbl.move_to(b)) for b, lbl in zip(blocks, name_labels)
        ]).arrange(DOWN, buff=0.18)
        outline = SurroundingRectangle(labeled, color=ENCODER, buff=0.25, corner_radius=0.1)
        stack_label = Text("Encoder (BERT)", font_size=20, color=ENCODER).next_to(outline, UP, buff=0.15)
        nx = Text("× N (12 em BERT-base, 24 em BERT-large)", font_size=16, color=GRAY_B).next_to(outline, DOWN, buff=0.12)
        stack = VGroup(outline, labeled, stack_label, nx).shift(DOWN * 0.2)
        self.play(FadeIn(stack))
        self.wait(3.8)

        self.play(FadeOut(c1), FadeOut(stack))

        # --- 2. Bidirectional attention (contrast with causal) ---
        c2 = callout("Sem máscara causal: cada token vê o contexto inteiro, dos dois lados", color=MECHANISM)
        self.play(FadeIn(c2))

        tokens = ["O", "gato", "[MASK]", "cedo"]
        dots = VGroup(*[Dot(radius=0.13, color=ENCODER) for _ in tokens]).arrange(RIGHT, buff=1.3).shift(DOWN * 0.1)
        colors_labels = [WHITE, WHITE, MECHANISM, WHITE]
        labels = VGroup(*[
            Text(t, font_size=18, color=c).next_to(d, DOWN, buff=0.25) for t, d, c in zip(tokens, dots, colors_labels)
        ])
        self.play(FadeIn(dots), FadeIn(labels))

        all_lines = VGroup()
        for i in range(len(dots)):
            for j in range(len(dots)):
                if i == j:
                    continue
                line = Line(dots[i].get_center(), dots[j].get_center(), color=MECHANISM, stroke_width=2, stroke_opacity=0.6)
                all_lines.add(line)
        self.play(LaggedStart(*[Create(l) for l in all_lines], lag_ratio=0.05, run_time=2))
        note = Text("todas as direções permitidas — inclusive olhar 'para a frente'", font_size=16, color=GRAY_B)
        note.next_to(dots, DOWN, buff=0.9)
        self.play(FadeIn(note))
        self.wait(3.8)

        bidir_group = VGroup(dots, labels, all_lines, note)
        self.play(FadeOut(c2), FadeOut(bidir_group))

        # --- 3. Por que isso importa: causal vs bidirecional, lado a lado ---
        c3 = callout("Por que a direção importa: o mesmo [MASK], dois modelos diferentes", color=MECHANISM)
        self.play(FadeIn(c3))

        container3 = RoundedRectangle(corner_radius=0.15, width=12.8, height=5.2, color=GRAY_D, stroke_width=1.5).shift(DOWN * 0.4)
        self.play(Create(container3))

        left_title = Text("Modelo causal (esquerda -> direita)", font_size=17, color=OLD)
        left_title.move_to(container3.get_top() + DOWN * 0.6 + LEFT * 3.2)
        left_term = terminal_box([
            "entrada até o ponto de previsão:",
            '  "O [MASK]"',
            "contexto visível: só 'O'",
            "previsão: quase adivinhação",
            "  (\"cachorro\"? \"gato\"? \"carro\"?)",
        ], width=5.6, font_size=16)
        left_term.move_to(container3.get_center() + LEFT * 3.2 + DOWN * 0.3)

        right_title = Text("BERT (bidirecional)", font_size=17, color=MECHANISM)
        right_title.move_to(container3.get_top() + DOWN * 0.6 + RIGHT * 3.2)
        right_term = terminal_box([
            "entrada completa:",
            '  "O [MASK] estava latindo"',
            "contexto visível: 'O' E 'estava latindo'",
            "previsão: \"cachorro\" (alta confiança)",
        ], width=5.6, font_size=16)
        right_term.move_to(container3.get_center() + RIGHT * 3.2 + DOWN * 0.3)

        self.play(FadeIn(left_title), FadeIn(right_title))
        self.play(FadeIn(left_term))
        self.wait(1.2)
        self.play(FadeIn(right_term))
        divider = Line(container3.get_top() + DOWN * 0.3, container3.get_bottom() + UP * 0.3, color=GRAY_D)
        self.play(Create(divider))
        contrast_note = Text("ver os dois lados transforma adivinhação em previsão informada", font_size=16, color=MECHANISM)
        contrast_note.next_to(container3, DOWN, buff=0.35)
        self.play(FadeIn(contrast_note))
        self.wait(4.5)

        contrast_group = VGroup(container3, left_title, right_title, left_term, right_term, divider, contrast_note)
        self.play(FadeOut(c3), FadeOut(contrast_group))

        # --- 4. Masked Language Modeling ---
        c4 = callout("Pré-treino, tarefa 1: Masked Language Modeling (MLM)")
        self.play(FadeIn(c4))

        term = terminal_box([
            "entrada:  O gato [MASK] cedo",
            "contexto: olha 'O gato' (esquerda) e 'cedo' (direita) ao mesmo tempo",
            "previsão: [MASK] -> \"dormiu\"",
            "",
            "~15% dos tokens mascarados por exemplo de treino:",
            "  80% viram [MASK], 10% viram um token aleatório,",
            "  10% permanecem inalterados (evita que o modelo",
            "  só aprenda a reconhecer o símbolo [MASK])",
        ], font_size=17).shift(DOWN * 0.1)
        self.play(FadeIn(term))
        self.wait(5.5)

        self.play(FadeOut(c4), FadeOut(term))

        # --- 5. Next Sentence Prediction ---
        c5 = callout("Pré-treino, tarefa 2: Next Sentence Prediction (NSP)", color=MECHANISM)
        self.play(FadeIn(c5))

        term5a = terminal_box([
            "Sentença A: \"O gato dormiu na janela.\"",
            "Sentença B: \"Ele acordou com o barulho da rua.\"",
            "",
            "[CLS] A [SEP] B [SEP]  ->  IsNext? SIM",
        ], font_size=17).shift(UP * 1.1)
        term5b = terminal_box([
            "Sentença A: \"O gato dormiu na janela.\"",
            "Sentença B: \"O Brasil é o maior país da América do Sul.\"",
            "",
            "[CLS] A [SEP] B [SEP]  ->  IsNext? NÃO (aleatória)",
        ], font_size=17).shift(DOWN * 1.6)
        self.play(FadeIn(term5a))
        self.wait(1.5)
        self.play(FadeIn(term5b))
        nsp_note = Text("50% dos pares são consecutivos de verdade, 50% são sentenças aleatórias", font_size=16, color=GRAY_B)
        nsp_note.next_to(term5b, DOWN, buff=0.3)
        self.play(FadeIn(nsp_note))
        self.wait(4.8)

        nsp_group = VGroup(term5a, term5b, nsp_note)
        self.play(FadeOut(c5), FadeOut(nsp_group))

        # --- 6. O token [CLS] ---
        c6 = callout("O token [CLS]: uma posição extra cuja saída resume a sequência inteira", color=MECHANISM)
        self.play(FadeIn(c6))

        seq_tokens = ["[CLS]", "O", "gato", "dormiu"]
        seq_dots = VGroup(*[Dot(radius=0.12, color=ENCODER) for _ in seq_tokens]).arrange(RIGHT, buff=1.2).shift(UP * 0.4)
        seq_dots[0].set_color(MECHANISM)
        seq_labels = VGroup(*[
            Text(t, font_size=16, color=(MECHANISM if i == 0 else WHITE)).next_to(d, DOWN, buff=0.2)
            for i, (t, d) in enumerate(zip(seq_tokens, seq_dots))
        ])
        self.play(FadeIn(seq_dots), FadeIn(seq_labels))

        arrow_up = Arrow(seq_dots[0].get_top(), seq_dots[0].get_top() + UP * 1.2, color=MECHANISM, stroke_width=4)
        cls_out_group = sized_box("representação da sequência inteira", font_size=16, color=WHITE, box_color=MECHANISM, margin=0.3)
        cls_out_group[0].set_fill(MECHANISM, opacity=0.35)
        cls_out_group.next_to(arrow_up, UP, buff=0.1)
        cls_out, cls_out_label = cls_out_group
        self.play(GrowArrow(arrow_up))
        self.play(FadeIn(cls_out), FadeIn(cls_out_label))
        cls_note = Text("nenhuma palavra real — existe só para acumular contexto de toda a sentença", font_size=16, color=GRAY_B)
        cls_note.next_to(seq_dots, DOWN, buff=1.0)
        if cls_note.width > 12.6:
            cls_note.scale_to_fit_width(12.6)
        self.play(FadeIn(cls_note))
        self.wait(4.5)

        cls_group = VGroup(seq_dots, seq_labels, arrow_up, cls_out, cls_out_label, cls_note)
        self.play(FadeOut(c6), FadeOut(cls_group))

        # --- 7. Usos típicos, com um exemplo completo ---
        c7 = callout("Sem decoder — BERT produz representações para tarefas de entendimento")
        self.play(FadeIn(c7))

        tasks = ["Classificação\nde sentimento", "Resposta a\nperguntas (QA)", "Similaridade\nde sentenças", "Reconhecimento\nde entidades (NER)"]
        task_boxes = VGroup()
        for t in tasks:
            b = RoundedRectangle(corner_radius=0.1, width=2.8, height=1.3, color=ENCODER).set_fill(ENCODER, opacity=0.25)
            lbl = Text(t, font_size=16, color=WHITE, line_spacing=1.1).move_to(b)
            task_boxes.add(VGroup(b, lbl))
        task_boxes.arrange(RIGHT, buff=0.4).shift(UP * 0.9)
        if task_boxes.width > 12.6:
            task_boxes.scale_to_fit_width(12.6)
        self.play(LaggedStart(*[FadeIn(b) for b in task_boxes], lag_ratio=0.2))
        self.wait(2.2)

        pipeline_term = terminal_box([
            "exemplo — classificação de sentimento:",
            '  entrada: "[CLS] Esse filme foi excelente [SEP]"',
            "  [CLS] final  ->  camada linear  ->  positivo (0.94)",
        ], font_size=16).next_to(task_boxes, DOWN, buff=0.5)
        self.play(FadeIn(pipeline_term))
        no_gen_note = Text("sem geração de texto livre — só entendimento de texto já existente", font_size=16, color=GRAY_B)
        no_gen_note.next_to(pipeline_term, DOWN, buff=0.35)
        self.play(FadeIn(no_gen_note))
        self.wait(5.0)

        tasks_group = VGroup(task_boxes, pipeline_term, no_gen_note)
        self.play(FadeOut(c7), FadeOut(tasks_group))

        # --- Closing ---
        backdrop = RoundedRectangle(corner_radius=0.2, width=13, height=3.6, fill_color="#111111", fill_opacity=0.9, stroke_width=0)
        closing = Text(
            "Encoder-only, bidirecional, pré-treinado com MLM + NSP,\n"
            "resumido no token [CLS]: o caminho oposto ao do GPT,\n"
            "para tarefas de entender em vez de gerar.",
            font_size=25, color=WHITE, line_spacing=1.3,
        ).move_to(ORIGIN)
        if closing.width > 12.4:
            closing.scale_to_fit_width(12.4)
        self.play(FadeIn(backdrop))
        self.play(Write(closing))
        self.wait(4.5)
        self.play(FadeOut(backdrop), FadeOut(closing))
