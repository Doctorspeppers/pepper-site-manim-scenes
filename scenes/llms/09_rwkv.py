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


class RWKVScene(Scene):
    def construct(self):
        title = Text("RWKV: Reinventing RNNs for the Transformer Era", font_size=28, color=WHITE)
        if title.width > 12.8:
            title.scale_to_fit_width(12.8)
        subtitle = Text("Peng et al., EleutherAI e colaboradores, 2023", font_size=22, color=GRAY_B)
        subtitle.next_to(title, DOWN, buff=0.35)
        self.play(Write(title))
        self.play(FadeIn(subtitle))
        self.wait(2.8)
        self.play(FadeOut(title), FadeOut(subtitle))

        # --- 1. O problema: custo quadrático ---
        c1 = callout('"Transformers sofrem de complexidade que escala quadraticamente com o comprimento"')
        self.play(FadeIn(c1))

        # Safe content area: every diagram is built to fit inside this visible
        # frame, so it never runs off the edges of the render regardless of
        # how the underlying values scale (here, n^2 growth).
        container = RoundedRectangle(corner_radius=0.15, width=12.8, height=5.4, color=GRAY_D, stroke_width=1.5).shift(DOWN * 0.3)
        self.play(Create(container))

        n_values = [4, 8, 16]
        max_n = max(n_values)
        baseline_y = container.get_bottom()[1] + 0.7
        max_bar_height = container.height / 2 - 1.0
        bars = VGroup()
        for i, n in enumerate(n_values):
            h = 0.4 + (max_bar_height - 0.4) * (n * n) / (max_n * max_n)
            bar = Rectangle(width=1.2, height=h, color=OLD, fill_color=OLD, fill_opacity=0.4)
            bar.move_to(RIGHT * (i - 1) * 2.8 + UP * (baseline_y + h / 2))
            label = Text(f"seq={n}", font_size=16, color=WHITE).next_to(bar, DOWN, buff=0.15)
            cost = Text(f"{n*n} ops", font_size=16, color=OLD).next_to(bar, UP, buff=0.1)
            bars.add(VGroup(bar, label, cost))
        base_line = Line(LEFT * 4.6, RIGHT * 4.6, color=GRAY_D).move_to(UP * baseline_y)
        self.play(Create(base_line))
        self.play(LaggedStart(*[FadeIn(b) for b in bars], lag_ratio=0.3))
        self.wait(3.5)

        double_note = Text("dobrar o contexto quadruplica o custo — o gargalo que motiva RWKV", font_size=16, color=GRAY_B)
        double_note.move_to(container.get_bottom() + UP * 0.35)
        self.play(FadeIn(double_note))
        self.wait(3)

        quad_group = VGroup(container, base_line, bars, double_note)
        self.play(FadeOut(c1), FadeOut(quad_group))

        # --- 2. Volta às RNNs, mas reinventadas ---
        c2 = callout("A saída: voltar para RNNs — a família que o Transformer havia substituído em 2017", color=MECHANISM)
        self.play(FadeIn(c2))

        # Build both labels first, then size BOTH boxes to whichever label is
        # larger, so the comparison stays visually symmetric and neither label
        # is ever cramped against its own box edges.
        rnn_label_text = Text("RNN\nclássica", font_size=20, color=WHITE, line_spacing=1.2)
        transf_label_text = Text("treino\nparalelizável", font_size=18, color=WHITE, line_spacing=1.2)
        pair_margin = 0.35
        pair_width = max(rnn_label_text.width, transf_label_text.width) + pair_margin * 2
        pair_height = max(rnn_label_text.height, transf_label_text.height) + pair_margin * 2

        rnn_box = RoundedRectangle(corner_radius=0.1, width=pair_width, height=pair_height, color=DECODER).set_fill(DECODER, opacity=0.3)
        rnn_label = rnn_label_text.move_to(rnn_box)
        rnn_con = Text("rápida e barata na\ninferência, lenta e serial\nno treino", font_size=16, color=GRAY_B, line_spacing=1.15)

        plus = Text("+", font_size=36, color=WHITE)

        transf_box = RoundedRectangle(corner_radius=0.1, width=pair_width, height=pair_height, color=ENCODER).set_fill(ENCODER, opacity=0.3)
        transf_label = transf_label_text.move_to(transf_box)
        transf_con = Text("rápido no treino,\nmas caro e crescente\nna inferência", font_size=16, color=GRAY_B, line_spacing=1.15)

        left_col = VGroup(rnn_box, rnn_label)
        right_col = VGroup(transf_box, transf_label)
        combo = VGroup(left_col, plus, right_col).arrange(RIGHT, buff=0.6).shift(UP * 0.9)
        rnn_con.next_to(left_col, DOWN, buff=0.35)
        transf_con.next_to(right_col, DOWN, buff=0.35)

        self.play(FadeIn(left_col))
        self.play(FadeIn(rnn_con))
        self.wait(1.5)
        self.play(FadeIn(plus))
        self.play(FadeIn(right_col))
        self.play(FadeIn(transf_con))
        self.wait(3.5)

        goal_note = Text("RWKV: pegar o melhor dos dois mundos, sem os dois defeitos", font_size=17, color=MECHANISM)
        goal_note.next_to(VGroup(rnn_con, transf_con), DOWN, buff=0.5)
        self.play(FadeIn(goal_note))
        self.wait(3)

        combo_group = VGroup(combo, rnn_con, transf_con, goal_note)
        self.play(FadeOut(c2), FadeOut(combo_group))

        # --- 3. O mecanismo: média ponderada com decaimento aprendido ---
        c3 = callout("Por baixo do capô: uma média ponderada do passado, com decaimento aprendido por canal", color=MECHANISM)
        self.play(FadeIn(c3))

        term_wkv = terminal_box([
            "estado[t] = decaimento * estado[t-1]  +  peso_novo * valor[t]",
            "",
            "'decaimento' é aprendido por canal — não é fixo nem hardcoded",
            "tokens antigos pesam cada vez menos, mas nunca são zerados de vez",
            "matematicamente equivalente a uma soma ponderada de toda a história",
        ], font_size=17).shift(DOWN * 0.1)
        self.play(FadeIn(term_wkv))
        self.wait(5)

        equiv_note = Text("essa equivalência é o que permite DUAS formas de calcular a mesma coisa", font_size=16, color=GRAY_B)
        equiv_note.next_to(term_wkv, DOWN, buff=0.5)
        if equiv_note.width > 12.6:
            equiv_note.scale_to_fit_width(12.6)
        self.play(FadeIn(equiv_note))
        self.wait(3)

        self.play(FadeOut(c3), FadeOut(term_wkv), FadeOut(equiv_note))

        # --- 4. Time-mixing e channel-mixing ---
        c4 = callout("Duas peças por bloco: time-mixing e channel-mixing — o equivalente RNN de atenção + MLP")
        self.play(FadeIn(c4))

        tm_box = RoundedRectangle(corner_radius=0.1, width=5.6, height=2.3, color=MECHANISM).set_fill(MECHANISM, opacity=0.28).shift(LEFT * 3.1 + UP * 0.2)
        tm_title = Text("Time-mixing", font_size=19, color=WHITE).move_to(tm_box.get_top() + DOWN * 0.4)
        tm_desc = Text("mistura recorrente do token atual\ncom o estado acumulado do passado\n(o papel da atenção, em forma de RNN)", font_size=16, color=WHITE, line_spacing=1.25)
        tm_desc.move_to(tm_box.get_center() + DOWN * 0.2)

        cm_box = RoundedRectangle(corner_radius=0.1, width=5.6, height=2.3, color=FFN).set_fill(FFN, opacity=0.28).shift(RIGHT * 3.1 + UP * 0.2)
        cm_title = Text("Channel-mixing", font_size=19, color=WHITE).move_to(cm_box.get_top() + DOWN * 0.4)
        cm_desc = Text("processamento posição-a-posição,\nmisturando os canais internos\n(o papel do feed-forward/MLP)", font_size=16, color=WHITE, line_spacing=1.25)
        cm_desc.move_to(cm_box.get_center() + DOWN * 0.2)

        self.play(FadeIn(tm_box), FadeIn(tm_title))
        self.play(FadeIn(tm_desc))
        self.wait(2.5)
        self.play(FadeIn(cm_box), FadeIn(cm_title))
        self.play(FadeIn(cm_desc))
        self.wait(2.5)

        analogy = Text("mesma dupla de papéis de um bloco Transformer — implementada de forma recorrente", font_size=16, color=GRAY_B)
        analogy.next_to(VGroup(tm_box, cm_box), DOWN, buff=0.6)
        if analogy.width > 12.6:
            analogy.scale_to_fit_width(12.6)
        self.play(FadeIn(analogy))
        self.wait(3.5)

        tmcm_group = VGroup(tm_box, tm_title, tm_desc, cm_box, cm_title, cm_desc, analogy)
        self.play(FadeOut(c4), FadeOut(tmcm_group))

        # --- 5. Treino paralelo, inferência recorrente ---
        c5 = callout("Duas formulações matematicamente equivalentes: paralela no treino, recorrente na inferência")
        self.play(FadeIn(c5))

        term = terminal_box([
            "treino:      forma paralela (tipo Transformer)  -> usa toda a GPU de uma vez",
            "inferência:  forma recorrente (tipo RNN)         -> um token por vez",
            "                                                     custo constante, não cresce com o contexto",
            "",
            "resultado: treina rápido, e depois roda barato pra sempre",
        ], font_size=16).shift(DOWN * 0.1)
        self.play(FadeIn(term))
        self.wait(5.5)

        self.play(FadeOut(c5), FadeOut(term))

        # --- 6. Custo constante vs crescente ---
        c6 = callout("Na prática: memória de inferência constante, não crescente com o contexto", color=MECHANISM)
        self.play(FadeIn(c6))

        tf_label = Text("Transformer (cache K/V)", font_size=16, color=OLD).shift(UP * 1.7 + LEFT * 3.0)
        tf_bars = VGroup(*[
            Rectangle(width=0.5, height=0.3 + i * 0.25, color=OLD, fill_color=OLD, fill_opacity=0.4)
            for i in range(5)
        ]).arrange(RIGHT, buff=0.15, aligned_edge=DOWN).next_to(tf_label, DOWN, buff=0.3)

        rwkv_label = Text("RWKV (estado recorrente)", font_size=16, color=MECHANISM).shift(UP * 1.7 + RIGHT * 3.0)
        rwkv_bars = VGroup(*[
            Rectangle(width=0.5, height=0.5, color=MECHANISM, fill_color=MECHANISM, fill_opacity=0.4)
            for _ in range(5)
        ]).arrange(RIGHT, buff=0.15, aligned_edge=DOWN)
        rwkv_bars.next_to(rwkv_label, DOWN, buff=0.3)

        self.play(FadeIn(tf_label), FadeIn(rwkv_label))
        self.play(LaggedStart(*[FadeIn(b) for b in tf_bars], lag_ratio=0.2))
        self.play(LaggedStart(*[FadeIn(b) for b in rwkv_bars], lag_ratio=0.2))
        mem_note = Text("cache cresce a cada token novo  vs.  estado de tamanho fixo, sempre", font_size=16, color=GRAY_B)
        mem_note.next_to(VGroup(tf_bars, rwkv_bars), DOWN, buff=0.7)
        if mem_note.width > 12.6:
            mem_note.scale_to_fit_width(12.6)
        self.play(FadeIn(mem_note))
        self.wait(3.5)

        deploy_note = Text("em tese, gera sequências arbitrariamente longas — documentos inteiros, diálogos", font_size=16, color=GRAY_B)
        deploy_note2 = Text("extensos — sem o custo crescente que eventualmente limita um Transformer", font_size=16, color=GRAY_B)
        deploy_group = VGroup(deploy_note, deploy_note2).arrange(DOWN, buff=0.12)
        deploy_group.next_to(mem_note, DOWN, buff=0.4)
        if deploy_group.width > 12.6:
            deploy_group.scale_to_fit_width(12.6)
        self.play(FadeIn(deploy_group))
        self.wait(4)

        mem_group = VGroup(tf_label, tf_bars, rwkv_label, rwkv_bars, mem_note, deploy_group)
        self.play(FadeOut(c6), FadeOut(mem_group))

        # --- 7. Convergência com Mamba ---
        c7 = callout("RWKV e Mamba chegam ao mesmo diagnóstico por rotas diferentes, no mesmo ano")
        self.play(FadeIn(c7))

        rwkv_path = RoundedRectangle(corner_radius=0.1, width=3.8, height=1.5, color=DECODER).set_fill(DECODER, opacity=0.3).shift(LEFT * 3.0 + UP * 0.5)
        rwkv_path_label = Text("RWKV: RNN\nreformulada", font_size=17, color=WHITE, line_spacing=1.2).move_to(rwkv_path)
        mamba_path = RoundedRectangle(corner_radius=0.1, width=3.8, height=1.5, color=MECHANISM).set_fill(MECHANISM, opacity=0.3).shift(RIGHT * 3.0 + UP * 0.5)
        mamba_path_label = Text("Mamba: SSM\nseletivo", font_size=17, color=WHITE, line_spacing=1.2).move_to(mamba_path)

        converge_point = Text("atenção deixa de ser consenso automático", font_size=18, color=WHITE)
        converge_point.shift(DOWN * 1.1)
        if converge_point.width > 12.4:
            converge_point.scale_to_fit_width(12.4)

        arrow1 = Arrow(rwkv_path.get_bottom(), converge_point.get_top() + LEFT * 1.2, buff=0.15, color=GRAY_B)
        arrow2 = Arrow(mamba_path.get_bottom(), converge_point.get_top() + RIGHT * 1.2, buff=0.15, color=GRAY_B)

        self.play(FadeIn(rwkv_path), FadeIn(rwkv_path_label))
        self.play(FadeIn(mamba_path), FadeIn(mamba_path_label))
        self.play(GrowArrow(arrow1), GrowArrow(arrow2))
        self.play(Write(converge_point))
        self.wait(3)

        distinction = Text("rotas diferentes, mesmo alvo: custo linear sem abrir mão de contexto longo", font_size=16, color=GRAY_B)
        distinction.next_to(converge_point, DOWN, buff=0.45)
        if distinction.width > 12.6:
            distinction.scale_to_fit_width(12.6)
        self.play(FadeIn(distinction))
        self.wait(3.5)

        converge_group = VGroup(rwkv_path, rwkv_path_label, mamba_path, mamba_path_label, arrow1, arrow2, converge_point, distinction)
        self.play(FadeOut(c7), FadeOut(converge_group))

        # --- 8. Fechamento da série de 9: recapitulação completa ---
        recap_title = Text("A jornada completa desta série", font_size=24, color=WHITE)
        self.play(Write(recap_title))
        self.wait(1.5)
        self.play(FadeOut(recap_title))

        # Each entry is its own two-line block (name, then description indented
        # below it) so no line ever needs to be squeezed to make a wide single
        # row fit — a blanket .scale(0.92) on the whole grid used to do exactly
        # that, quietly pushing already-floor-level 16-17pt text below it.
        recap_lines = [
            ("Transformer (2017)", "uniu tudo sob um único mecanismo: atenção", ENCODER),
            ("GPT & BERT (2018)", "dividiram a arquitetura em gerar vs. entender", DECODER),
            ("LLaMA & Mistral (2023)", "baratearam o decoder sem trocar de paradigma", DECODER),
            ("DeepSeek (2024-25)", "escalou MoE e ensinou raciocínio via RL puro", MECHANISM),
            ("PaLM & Gemini", "escalaram bruto, depois somaram multimodalidade", ENCODER),
            ("Mamba & RWKV (2023)", "perguntaram se atenção era mesmo necessária", MECHANISM),
        ]
        rows = VGroup()
        for name, desc, color in recap_lines:
            dot = Dot(radius=0.08, color=color)
            name_t = Text(name, font_size=17, color=color)
            name_row = VGroup(dot, name_t).arrange(RIGHT, buff=0.25)
            desc_t = Text(desc, font_size=16, color=WHITE)
            if desc_t.width > 12.0:
                desc_t.scale_to_fit_width(12.0)
            desc_t.next_to(name_row, DOWN, buff=0.1).align_to(name_t, LEFT)
            rows.add(VGroup(name_row, desc_t))
        rows.arrange(DOWN, buff=0.2, aligned_edge=LEFT)
        rows.move_to(ORIGIN + DOWN * 0.1)

        self.play(LaggedStart(*[FadeIn(r) for r in rows], lag_ratio=0.35, run_time=4))
        self.wait(5.5)

        self.play(FadeOut(rows))

        # --- Closing ---
        backdrop = RoundedRectangle(corner_radius=0.2, width=13, height=3.6, fill_color="#111111", fill_opacity=0.9, stroke_width=0)
        closing = Text(
            "Nove papers, uma pergunta em comum: como pesar\n"
            "custo, contexto e escala. Atenção venceu essa disputa em 2017 —\n"
            "Mamba e RWKV são os primeiros a levá-la a sério de novo.",
            font_size=24, color=WHITE, line_spacing=1.35,
        ).move_to(ORIGIN)
        if closing.width > 12.4:
            closing.scale_to_fit_width(12.4)
        self.play(FadeIn(backdrop))
        self.play(Write(closing))
        self.wait(4.5)
        self.play(FadeOut(backdrop), FadeOut(closing))
