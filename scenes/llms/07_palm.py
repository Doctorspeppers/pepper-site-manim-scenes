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


class PaLMScene(Scene):
    def construct(self):
        title = Text("PaLM: Scaling Language Modeling with Pathways", font_size=28, color=WHITE)
        if title.width > 12.8:
            title.scale_to_fit_width(12.8)
        subtitle = Text("Chowdhery et al., Google, 2022", font_size=22, color=GRAY_B)
        subtitle.next_to(title, DOWN, buff=0.35)
        self.play(Write(title))
        self.play(FadeIn(subtitle))
        self.wait(3)
        self.play(FadeOut(title), FadeOut(subtitle))

        # --- 1. Same recipe, brute scale ---
        c1 = callout("Nenhum truque arquitetural novo: um decoder denso, levado ao limite de infraestrutura")
        self.play(FadeIn(c1))

        blocks = VGroup(*[
            RoundedRectangle(corner_radius=0.08, width=2.8, height=0.55, color=c).set_fill(c, opacity=0.3)
            for c in [MECHANISM, NORM, FFN, NORM]
        ])
        names = ["Self-Attention", "Add & Norm", "Feed-Forward", "Add & Norm"]
        labeled = VGroup(*[
            VGroup(b, Text(n, font_size=16, color=WHITE).move_to(b)) for b, n in zip(blocks, names)
        ]).arrange(DOWN, buff=0.15)
        outline = SurroundingRectangle(labeled, color=DECODER, buff=0.22, corner_radius=0.1)
        stack_label = Text("Decoder (PaLM)", font_size=20, color=DECODER).next_to(outline, UP, buff=0.15)
        nx = Text("× 118 camadas — 540B parâmetros", font_size=16, color=GRAY_B).next_to(outline, DOWN, buff=0.12)
        # Not scaled down as a whole group (that would shrink the 16pt labels below the
        # legible floor) — the group already fits the available vertical space at its
        # natural size, so it's just repositioned.
        stack = VGroup(outline, labeled, stack_label, nx).shift(DOWN * 0.15)
        self.play(FadeIn(stack))
        self.wait(4)

        self.play(FadeOut(c1), FadeOut(stack))

        # --- 2. Por que treinar em 2 pods é difícil ---
        c2 = callout("Por que isso é difícil: treino distribuído depende de sincronização rápida de gradientes")
        self.play(FadeIn(c2))

        container2 = RoundedRectangle(corner_radius=0.15, width=12.8, height=5.4, color=GRAY_D, stroke_width=1.5).shift(DOWN * 0.3)
        self.play(Create(container2))

        normal_group = sized_box(
            "1 pod contíguo\ninterconexão rápida entre chips",
            font_size=16, color=WHITE, box_color=ENCODER, box_opacity=0.25,
            min_width=4.4, min_height=1.9, margin=0.35, line_spacing=1.2,
        ).shift(UP * 0.9)
        normal_pod, normal_label = normal_group
        normal_note = Text("caso comum: todo chip troca gradientes com todo chip, a cada passo de treino", font_size=16, color=GRAY_B)
        normal_note.next_to(normal_pod, DOWN, buff=0.4)
        if normal_note.width > 12.4:
            normal_note.scale_to_fit_width(12.4)
        self.play(FadeIn(normal_pod), FadeIn(normal_label))
        self.play(FadeIn(normal_note))
        self.wait(3.5)

        problem_note = Text("2 pods fisicamente separados = conexão bem mais lenta entre eles", font_size=17, color=MECHANISM)
        problem_note.next_to(normal_note, DOWN, buff=0.6)
        if problem_note.width > 12.4:
            problem_note.scale_to_fit_width(12.4)
        self.play(FadeIn(problem_note))
        self.wait(3.5)

        why_group = VGroup(container2, normal_pod, normal_label, normal_note, problem_note)
        self.play(FadeOut(c2), FadeOut(why_group))

        # --- 3. Pathways: decoupling onde roda de como é orquestrado ---
        c3 = callout("A saída do Pathways: separar ONDE a computação roda de COMO ela é orquestrada", color=MECHANISM)
        self.play(FadeIn(c3))

        pod_a = RoundedRectangle(corner_radius=0.1, width=3.2, height=1.8, color=ENCODER).set_fill(ENCODER, opacity=0.2).shift(LEFT * 3.0)
        pod_a_label = Text("TPU Pod A\n3072 chips", font_size=17, color=WHITE, line_spacing=1.2).move_to(pod_a)
        pod_b = RoundedRectangle(corner_radius=0.1, width=3.2, height=1.8, color=ENCODER).set_fill(ENCODER, opacity=0.2).shift(RIGHT * 3.0)
        pod_b_label = Text("TPU Pod B\n3072 chips", font_size=17, color=WHITE, line_spacing=1.2).move_to(pod_b)
        link = DoubleArrow(pod_a.get_right(), pod_b.get_left(), color=MECHANISM, stroke_width=4, buff=0.1)
        link_label = Text("Pathways: coordena os dois pods como um só job lógico", font_size=16, color=MECHANISM)
        link_label.next_to(VGroup(pod_a, pod_b), UP, buff=0.35)
        if link_label.width > 12.4:
            link_label.scale_to_fit_width(12.4)

        self.play(FadeIn(pod_a), FadeIn(pod_a_label))
        self.play(FadeIn(pod_b), FadeIn(pod_b_label))
        self.play(GrowArrow(link), FadeIn(link_label))
        total_note = Text("6144 chips TPU v4 no total — a conexão lenta nunca vira o gargalo", font_size=17, color=GRAY_B)
        total_note.next_to(VGroup(pod_a, pod_b), DOWN, buff=0.6)
        if total_note.width > 12.6:
            total_note.scale_to_fit_width(12.6)
        self.play(FadeIn(total_note))
        self.wait(4.5)

        pathways_group = VGroup(pod_a, pod_a_label, pod_b, pod_b_label, link, link_label, total_note)
        self.play(FadeOut(c3), FadeOut(pathways_group))

        # --- 4. Continued benefits of scale ---
        c4 = callout("O paper enquadra o resultado como confirmação: os benefícios da escala continuam")
        self.play(FadeIn(c4))

        term = terminal_box([
            "PaLM 540B em few-shot (sem ajuste de pesos):",
            "  supera o estado da arte com fine-tuning em tarefas",
            "  de raciocínio multi-etapa (chain-of-thought)",
            "  supera a performance humana média no BIG-bench",
        ], font_size=17).shift(DOWN * 0.1)
        self.play(FadeIn(term))
        self.wait(4.5)

        self.play(FadeOut(c4), FadeOut(term))

        # --- 5. Chain-of-thought: exemplo concreto ---
        c5 = callout("Chain-of-thought: pedir o raciocínio passo a passo, não só a resposta final", color=MECHANISM)
        self.play(FadeIn(c5))

        direct_term = terminal_box([
            "prompt direto:",
            '  "João tinha 5 maçãs, comprou mais 7 e comeu 3."',
            '  "Quantas sobraram?"',
            "  resposta: 8   <- errado, sem mostrar o raciocínio",
        ], font_size=16, width=12.6).shift(UP * 1.5)
        self.play(FadeIn(direct_term))
        self.wait(3.5)

        cot_term = terminal_box([
            "prompt com chain-of-thought:",
            '  "...explique o raciocínio passo a passo antes de responder"',
            "  5 + 7 = 12 maçãs; depois 12 - 3 = 9 maçãs",
            "  resposta: 9   <- correto — o passo intermediário guia o modelo",
        ], font_size=16, width=12.6).shift(DOWN * 1.7)
        self.play(FadeIn(cot_term))
        self.wait(4.5)

        cot_group = VGroup(direct_term, cot_term)
        self.play(FadeOut(c5), FadeOut(cot_group))

        # --- 6. BIG-bench: contexto ---
        c6 = callout("BIG-bench: mais de 200 tarefas desenhadas para serem difíceis para modelos de linguagem")
        self.play(FadeIn(c6))

        bb_term = terminal_box([
            "BIG-bench: benchmark colaborativo, 200+ tarefas diversas",
            "  lógica, matemática, senso comum, vieses sociais, linguística...",
            "  desenhado deliberadamente para ser difícil para LLMs",
            "",
            "PaLM 540B (few-shot): supera a média humana no conjunto",
        ], font_size=16).shift(DOWN * 0.1)
        self.play(FadeIn(bb_term))
        self.wait(4.5)

        self.play(FadeOut(c6), FadeOut(bb_term))

        # --- 7. Gemini lineage ---
        c7 = callout("O sucessor: Gemini — mesma aposta em escala, com multimodalidade nativa desde o início", color=MECHANISM)
        self.play(FadeIn(c7))

        text_icon = RoundedRectangle(corner_radius=0.08, width=1.6, height=1.0, color=ENCODER).set_fill(ENCODER, opacity=0.3).shift(LEFT * 3.2 + UP * 0.3)
        text_label = Text("texto", font_size=16, color=WHITE).move_to(text_icon)
        img_icon = RoundedRectangle(corner_radius=0.08, width=1.6, height=1.0, color=FFN).set_fill(FFN, opacity=0.3).shift(LEFT * 3.2 + DOWN * 1.0)
        img_label = Text("imagem", font_size=16, color=WHITE).move_to(img_icon)
        audio_icon = RoundedRectangle(corner_radius=0.08, width=1.6, height=1.0, color=NORM).set_fill(NORM, opacity=0.3).shift(LEFT * 3.2 + DOWN * 2.3)
        audio_label = Text("áudio", font_size=16, color=WHITE).move_to(audio_icon)

        gemini_box = RoundedRectangle(corner_radius=0.1, width=3.0, height=3.0, color=MECHANISM).set_fill(MECHANISM, opacity=0.25).shift(RIGHT * 2.0 + DOWN * 0.7)
        gemini_label = Text("Gemini\n(treino conjunto\ndesde o início)", font_size=16, color=WHITE, line_spacing=1.2).move_to(gemini_box)

        arrows_in = VGroup(*[
            Arrow(icon.get_right(), gemini_box.get_left() + UP * (0.9 - i * 0.9), buff=0.1, color=GRAY_B, stroke_width=2)
            for i, icon in enumerate([text_icon, img_icon, audio_icon])
        ])

        self.play(FadeIn(VGroup(text_icon, text_label, img_icon, img_label, audio_icon, audio_label)))
        self.play(LaggedStart(*[GrowArrow(a) for a in arrows_in], lag_ratio=0.2))
        self.play(FadeIn(gemini_box), FadeIn(gemini_label))
        gemini_note = Text("não um encoder de visão acoplado depois — multimodal desde a primeira etapa de treino", font_size=16, color=GRAY_B)
        gemini_note.to_edge(DOWN, buff=0.4)
        if gemini_note.width > 12.6:
            gemini_note.scale_to_fit_width(12.6)
        self.play(FadeIn(gemini_note))
        self.wait(4.5)

        gemini_group = VGroup(text_icon, text_label, img_icon, img_label, audio_icon, audio_label, arrows_in, gemini_box, gemini_label, gemini_note)
        self.play(FadeOut(c7), FadeOut(gemini_group))

        # --- 8. Por que treinar junto ajuda ---
        c8 = callout("Por que treinar junto ajuda: associações cross-modais aprendidas desde o início", color=MECHANISM)
        self.play(FadeIn(c8))

        # Both boxes share one width (the wider of the two labels + margin) so the
        # old-vs-new comparison still reads as a matched pair, without ever shrinking
        # either label below its declared font_size to force-fit a guessed box size.
        old_label_text = Text("abordagem antiga: treinar um LLM de texto,\ndepois acoplar um encoder de visão já pronto", font_size=16, color=OLD, line_spacing=1.3)
        new_label_text = Text("Gemini: texto, imagem e áudio no mesmo\ntreino, desde o primeiro passo", font_size=16, color=WHITE, line_spacing=1.3)
        margin = 0.35
        shared_width = max(old_label_text.width, new_label_text.width) + margin * 2

        old_way = RoundedRectangle(corner_radius=0.1, width=shared_width, height=old_label_text.height + margin * 2, color=OLD).set_fill(OLD, opacity=0.2).shift(UP * 1.3)
        old_label = old_label_text.move_to(old_way)
        old_note = Text("dois espaços de representação treinados separado — alinhar depois é mais difícil", font_size=16, color=GRAY_B)
        old_note.next_to(old_way, DOWN, buff=0.3)
        if old_note.width > 12.4:
            old_note.scale_to_fit_width(12.4)

        new_way = RoundedRectangle(corner_radius=0.1, width=shared_width, height=new_label_text.height + margin * 2, color=MECHANISM).set_fill(MECHANISM, opacity=0.3).shift(DOWN * 2.0)
        new_label = new_label_text.move_to(new_way)

        self.play(FadeIn(old_way), FadeIn(old_label))
        self.play(FadeIn(old_note))
        self.wait(3.5)
        self.play(FadeIn(new_way), FadeIn(new_label))
        self.wait(4.5)

        joint_group = VGroup(old_way, old_label, old_note, new_way, new_label)
        self.play(FadeOut(c8), FadeOut(joint_group))

        # --- Closing ---
        backdrop = RoundedRectangle(corner_radius=0.2, width=13, height=3.8, fill_color="#111111", fill_opacity=0.9, stroke_width=0)
        closing = Text(
            "PaLM mostrou até onde a mesma receita escala — em parâmetros,\ninfraestrutura distribuída e raciocínio multi-etapa.\nGemini herda essa escala e soma multimodalidade nativa desde o treino.",
            font_size=24, color=WHITE, line_spacing=1.3,
        ).move_to(ORIGIN)
        if closing.width > 12.4:
            closing.scale_to_fit_width(12.4)
        self.play(FadeIn(backdrop))
        self.play(Write(closing))
        self.wait(4.5)
        self.play(FadeOut(backdrop), FadeOut(closing))
