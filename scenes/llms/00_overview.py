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

class LLMOverviewScene(Scene):
    def construct(self):
        # --- 1. Opening ---
        title = Text("LLMs", font_size=52, color=WHITE)
        subtitle = Text("Do Transformer aos modelos sem atenção — visão geral da série", font_size=22, color=GRAY_B)
        if subtitle.width > 12.8:
            subtitle.scale_to_fit_width(12.8)
        subtitle.next_to(title, DOWN, buff=0.35)
        tag = Text("nove arquiteturas, um fio condutor: como processar sequências de forma eficiente", font_size=17, color=MECHANISM)
        tag.next_to(subtitle, DOWN, buff=0.5)
        if tag.width > 12.6:
            tag.scale_to_fit_width(12.6)
        self.play(Write(title, run_time=1.6))
        self.play(FadeIn(subtitle))
        self.play(FadeIn(tag))
        self.wait(12)
        self.play(FadeOut(title), FadeOut(subtitle), FadeOut(tag))

        # --- 2. RNNs (sequential) vs Attention (parallel) ---
        c1 = callout("O problema que o Transformer resolveu: processamento sequencial")
        self.play(FadeIn(c1))

        rnn_box = sized_box("RNN / LSTM\nprocessa token por token, em ordem\n-> não paraleliza, esquece o passado distante", font_size=16, color=WHITE, box_color=OLD, box_opacity=0.25, min_width=5.6, min_height=1.6, line_spacing=1.2)
        rnn_box.shift(LEFT * 3.2)
        attn_box = sized_box("Atenção (Transformer)\ncada token olha para todos os outros de uma vez\n-> paraleliza, captura dependências longas", font_size=16, color=WHITE, box_color=MECHANISM, box_opacity=0.4, min_width=5.6, min_height=1.6, line_spacing=1.2)
        attn_box.shift(RIGHT * 3.2)
        vs_row = VGroup(rnn_box, attn_box)
        assert_on_screen(vs_row, "overview rnn vs attention")
        self.play(FadeIn(rnn_box))
        self.play(FadeIn(attn_box))
        self.wait(16)
        self.play(FadeOut(c1), FadeOut(vs_row))

        # --- 3. The attention formula, term by term ---
        c2 = callout("O cálculo: atenção escalar por produto interno (Vaswani et al., 2017)", color=MECHANISM)
        self.play(FadeIn(c2))

        attn_formula = MathTex(
            r"\text{Attention}(Q, K, V) = \text{softmax}\!\left(",
            r"\frac{QK^T}{\sqrt{d_k}}",
            r"\right)",
            r"V",
            font_size=36, color=WHITE,
        )
        assert_on_screen(attn_formula, "overview attention formula")
        self.play(Write(attn_formula, run_time=2.2))
        self.wait(4)

        scores_term = attn_formula[1]
        box_scores = SurroundingRectangle(scores_term, color=MECHANISM, buff=0.08)
        label_scores = Text("QK^T: o quão relevante cada token é para cada outro; /sqrt(d_k) estabiliza a escala", font_size=16, color=MECHANISM)
        label_scores.next_to(attn_formula, DOWN, buff=0.7)
        if label_scores.width > 12.4:
            label_scores.scale_to_fit_width(12.4)
        self.play(Create(box_scores), FadeIn(label_scores))
        self.wait(8)
        self.play(FadeOut(box_scores), FadeOut(label_scores))

        v_term = attn_formula[3]
        box_v = SurroundingRectangle(v_term, color=ENCODER, buff=0.08)
        label_v = Text("V: a informação de fato somada, ponderada pelos pesos de atenção (softmax)", font_size=16, color=ENCODER)
        label_v.next_to(attn_formula, DOWN, buff=0.7)
        if label_v.width > 12.4:
            label_v.scale_to_fit_width(12.4)
        self.play(Create(box_v), FadeIn(label_v))
        self.wait(8)
        self.play(FadeOut(box_v), FadeOut(label_v))
        self.play(FadeOut(c2), FadeOut(attn_formula))

        # --- 4. A real attention-score heatmap ---
        c3 = callout("Na prática: uma matriz de pesos de atenção entre tokens", color=MECHANISM)
        self.play(FadeIn(c3))

        weights = [
            [0.7, 0.1, 0.1, 0.1],
            [0.2, 0.6, 0.1, 0.1],
            [0.1, 0.2, 0.5, 0.2],
            [0.1, 0.1, 0.3, 0.5],
        ]
        cell_size = 0.9
        grid = VGroup()
        for i, row in enumerate(weights):
            for j, w in enumerate(row):
                cell = Square(side_length=cell_size, color=MECHANISM, fill_color=MECHANISM, fill_opacity=w, stroke_width=1)
                cell.move_to(RIGHT * j * cell_size + DOWN * i * cell_size)
                grid.add(cell)
        grid.move_to(ORIGIN)
        tokens_lbl = ["O", "gato", "dormiu", "cedo"]
        row_labels = VGroup(*[Text(t, font_size=16, color=GRAY_B) for t in tokens_lbl]).arrange(DOWN, buff=cell_size - 0.35)
        row_labels.next_to(grid, LEFT, buff=0.35)
        col_labels = VGroup(*[Text(t, font_size=16, color=GRAY_B) for t in tokens_lbl]).arrange(RIGHT, buff=cell_size - 0.35)
        col_labels.next_to(grid, UP, buff=0.35)

        heatmap = VGroup(grid, row_labels, col_labels)
        assert_on_screen(heatmap, "overview attention heatmap")
        self.play(FadeIn(grid))
        self.play(FadeIn(row_labels), FadeIn(col_labels))
        note1 = Text("cada célula é o peso de atenção de uma palavra sobre a outra — mais escuro, mais peso", font_size=16, color=GRAY_B)
        note1.next_to(heatmap, DOWN, buff=0.6)
        if note1.width > 12.6:
            note1.scale_to_fit_width(12.6)
        self.play(FadeIn(note1))
        self.wait(16)
        self.play(FadeOut(c3), FadeOut(heatmap), FadeOut(note1))

        # --- 4.5. A worked numeric example of one attention score ---
        c3b = callout("Em números: calculando um único peso de atenção", color=MECHANISM)
        self.play(FadeIn(c3b))
        worked = terminal_box([
            'q = [1.0, 0.0]   k = [0.8, 0.6]   (vetores de dimensão d_k=2)',
            "produto interno: q . k = 1.0*0.8 + 0.0*0.6 = 0.8",
            "escala por sqrt(d_k): 0.8 / sqrt(2) = 0.566",
            "softmax sobre todos os scores da linha -> peso final da célula",
            "-> exatamente o número que colore uma célula do heatmap anterior",
        ], font_size=16).shift(DOWN * 0.1)
        assert_on_screen(worked, "overview attention worked example")
        self.play(FadeIn(worked))
        self.wait(16)
        self.play(FadeOut(c3b), FadeOut(worked))

        # --- 5. Three architectural families ---
        c4 = callout("Três famílias nascidas da mesma peça: onde a atenção é usada", color=MECHANISM)
        self.play(FadeIn(c4))

        enc_box = sized_box("Encoder-only\n(BERT)\nbidirecional, entende o\ntexto inteiro de uma vez", font_size=16, color=WHITE, box_color=ENCODER, box_opacity=0.35, min_width=4.0, min_height=1.6, line_spacing=1.1)
        enc_box.shift(LEFT * 4.3)
        dec_box = sized_box("Decoder-only\n(GPT)\nautoregressivo, gera um\ntoken por vez", font_size=16, color=WHITE, box_color=DECODER, box_opacity=0.35, min_width=4.0, min_height=1.6, line_spacing=1.1)
        encdec_box = sized_box("Encoder-Decoder\n(Transformer original)\nencoder lê, decoder\ngera condicionado nele", font_size=16, color=WHITE, box_color=MECHANISM, box_opacity=0.4, min_width=4.0, min_height=1.6, line_spacing=1.1)
        encdec_box.shift(RIGHT * 4.3)
        families_row = VGroup(enc_box, dec_box, encdec_box)
        assert_no_overlap(enc_box, dec_box, "overview llm families enc vs dec")
        assert_no_overlap(dec_box, encdec_box, "overview llm families dec vs encdec")
        assert_on_screen(families_row, "overview llm three families")
        self.play(FadeIn(enc_box))
        self.play(FadeIn(dec_box))
        self.play(FadeIn(encdec_box))
        self.wait(16.8)
        self.play(FadeOut(c4), FadeOut(families_row))

        # --- 5.5. Different objectives train different families ---
        c4b = callout("A arquitetura muda o que dá para treinar como objetivo", color=MECHANISM)
        self.play(FadeIn(c4b))

        mlm_box = sized_box("BERT: Masked Language Model\nesconde ~15% dos tokens, prevê\ncada um usando contexto dos DOIS lados", font_size=16, color=WHITE, box_color=ENCODER, box_opacity=0.3, min_width=6.0, min_height=1.5, line_spacing=1.15)
        mlm_box.shift(UP * 1.0)
        ntp_box = sized_box("GPT: Next-Token Prediction\nprevê o próximo token usando\nSÓ o contexto à esquerda", font_size=16, color=WHITE, box_color=DECODER, box_opacity=0.3, min_width=6.0, min_height=1.5, line_spacing=1.15)
        ntp_box.shift(DOWN * 1.0)
        obj_col = VGroup(mlm_box, ntp_box)
        assert_no_overlap(mlm_box, ntp_box, "overview objectives mlm vs ntp")
        assert_on_screen(obj_col, "overview training objectives")
        self.play(FadeIn(mlm_box))
        self.play(FadeIn(ntp_box))
        note_obj = Text('"a loss de treino é a soma da probabilidade média do MLM e da previsão da próxima frase" (BERT, 2018)', font_size=16, color=GRAY_B)
        note_obj.next_to(obj_col, DOWN, buff=0.4)
        if note_obj.width > 12.6:
            note_obj.scale_to_fit_width(12.6)
        assert_no_overlap(obj_col, note_obj, "overview objectives vs citation note")
        self.play(FadeIn(note_obj))
        self.wait(16)
        self.play(FadeOut(c4b), FadeOut(obj_col), FadeOut(note_obj))

        # --- 5.7. How order gets encoded: positional encoding, plotted ---
        c4c = callout("Atenção não sabe a ordem dos tokens — é preciso injetar posição", color=MECHANISM)
        self.play(FadeIn(c4c))

        pe_formula = MathTex(
            r"PE_{(pos, 2i)} = \sin\!\left(\frac{pos}{10000^{2i/d}}\right)",
            font_size=32, color=WHITE,
        ).shift(UP * 2.0)
        assert_on_screen(pe_formula, "overview positional encoding formula")
        self.play(Write(pe_formula, run_time=1.6))

        axes_pe = Axes(
            x_range=[0, 50, 10], y_range=[-1, 1, 0.5],
            x_length=8.0, y_length=2.6,
            axis_config={"color": GRAY_B, "stroke_width": 2, "include_tip": False},
        ).shift(DOWN * 1.1)
        curve_fast = axes_pe.plot(lambda x: np.sin(x / 3), x_range=[0, 50], color=MECHANISM, stroke_width=4)
        curve_slow = axes_pe.plot(lambda x: np.sin(x / 25), x_range=[0, 50], color=ENCODER, stroke_width=4)
        # Positioned below the full plotted curves (not just the axis line) —
        # the sine curves dip well below the x_axis itself, and a label
        # placed relative to the axis alone landed right on top of the
        # curve's trough.
        plotted = VGroup(axes_pe, curve_fast, curve_slow)
        pe_label = Text("posição no texto", font_size=16, color=GRAY_B).next_to(plotted, DOWN, buff=0.35)
        pe_graph = VGroup(plotted, pe_label)
        assert_no_overlap(pe_formula, pe_graph, "overview pe formula vs graph")
        assert_no_overlap(pe_label, plotted, "overview pe label vs plotted curves")
        assert_on_screen(pe_graph, "overview positional encoding graph")
        self.play(Create(axes_pe), FadeIn(pe_label))
        self.play(Create(curve_fast), Create(curve_slow))

        legend_pe = VGroup(
            VGroup(Dot(color=MECHANISM, radius=0.07), Text("dimensão de alta frequência", font_size=15, color=GRAY_B)).arrange(RIGHT, buff=0.15),
            VGroup(Dot(color=ENCODER, radius=0.07), Text("dimensão de baixa frequência", font_size=15, color=GRAY_B)).arrange(RIGHT, buff=0.15),
        ).arrange(RIGHT, buff=0.8)
        legend_pe.next_to(pe_graph, DOWN, buff=0.3)
        assert_no_overlap(pe_graph, legend_pe, "overview pe graph vs legend")
        self.play(FadeIn(legend_pe))
        self.wait(16.8)
        self.play(FadeOut(c4c), FadeOut(pe_formula), FadeOut(pe_graph), FadeOut(legend_pe))

        # --- 6. The cost of attention, plotted ---
        c5 = callout("O preço da atenção: custo quadrático no tamanho da sequência", color=MECHANISM)
        self.play(FadeIn(c5))

        axes1 = Axes(
            x_range=[0, 10, 2], y_range=[0, 10, 2],
            x_length=7.6, y_length=3.2,
            axis_config={"color": GRAY_B, "stroke_width": 2, "include_tip": False},
        ).shift(UP * 0.3)
        x_label1 = Text("comprimento da sequência", font_size=16, color=GRAY_B).next_to(axes1.x_axis, DOWN, buff=0.2)
        quad_curve = axes1.plot(lambda x: 0.1 * x ** 2, x_range=[0, 9.7], color=OLD, stroke_width=5)
        lin_curve = axes1.plot(lambda x: x, x_range=[0, 10], color=MECHANISM, stroke_width=5)

        graph1 = VGroup(axes1, x_label1, quad_curve, lin_curve)
        assert_on_screen(graph1, "overview cost graph")
        self.play(Create(axes1), FadeIn(x_label1))
        self.play(Create(quad_curve))
        self.play(Create(lin_curve))

        legend_a = VGroup(Dot(color=OLD, radius=0.08), Text('atenção padrão: O(n^2) — "quadratic to the sequence length" (BERT, Mistral)', font_size=16, color=GRAY_B)).arrange(RIGHT, buff=0.2)
        legend_b = VGroup(Dot(color=MECHANISM, radius=0.08), Text("Mamba (SSM seletivo): quase-linear, escala até sequências de 1M de tokens", font_size=16, color=GRAY_B)).arrange(RIGHT, buff=0.2)
        legend = VGroup(legend_a, legend_b).arrange(DOWN, buff=0.18, aligned_edge=LEFT)
        legend.next_to(graph1, DOWN, buff=0.4)
        if legend.width > 12.4:
            legend.scale_to_fit_width(12.4)
        assert_on_screen(legend, "overview cost legend")
        assert_no_overlap(graph1, legend, "overview cost graph vs legend")
        self.play(FadeIn(legend))
        self.wait(18)
        self.play(FadeOut(c5), FadeOut(graph1), FadeOut(legend))

        # --- 6.5. The equation behind the linear alternative ---
        c5b = callout("O cálculo por trás da linha reta: a recorrência do Mamba (SSM seletivo)", color=MECHANISM)
        self.play(FadeIn(c5b))

        ssm_formula = MathTex(
            r"h_t = ",
            r"A(x_t)\, h_{t-1}",
            r"+",
            r"B(x_t)\, x_t",
            font_size=34, color=WHITE,
        )
        assert_on_screen(ssm_formula, "overview ssm recurrence formula")
        self.play(Write(ssm_formula, run_time=2))
        self.wait(3)

        a_term = ssm_formula[1]
        box_a = SurroundingRectangle(a_term, color=ENCODER, buff=0.08)
        label_a = Text("carrega o estado anterior — a 'memória' que resume tudo que já foi visto", font_size=16, color=ENCODER)
        label_a.next_to(ssm_formula, DOWN, buff=0.7)
        if label_a.width > 12.4:
            label_a.scale_to_fit_width(12.4)
        self.play(Create(box_a), FadeIn(label_a))
        self.wait(7)
        self.play(FadeOut(box_a), FadeOut(label_a))

        b_term = ssm_formula[3]
        box_b = SurroundingRectangle(b_term, color=MECHANISM, buff=0.08)
        label_b = Text("A e B dependem do input — a 'seleção' que dá nome ao Mamba (S6)", font_size=16, color=MECHANISM)
        label_b.next_to(ssm_formula, DOWN, buff=0.7)
        if label_b.width > 12.4:
            label_b.scale_to_fit_width(12.4)
        self.play(Create(box_b), FadeIn(label_b))
        self.wait(7)
        self.play(FadeOut(box_b), FadeOut(label_b))

        note_ssm = Text("cada passo é O(1): um estado de tamanho fixo, nunca uma matriz n x n de atenção", font_size=16, color=GRAY_B)
        note_ssm.next_to(ssm_formula, DOWN, buff=0.7)
        if note_ssm.width > 12.6:
            note_ssm.scale_to_fit_width(12.6)
        self.play(FadeIn(note_ssm))
        self.wait(8)
        self.play(FadeOut(c5b), FadeOut(ssm_formula), FadeOut(note_ssm))

        # --- 7. MoE: bigger models, fewer active parameters ---
        c6 = callout("Mixture-of-Experts: crescer o modelo sem pagar o custo inteiro por token", color=MECHANISM)
        self.play(FadeIn(c6))

        chart = BarChart(
            values=[37, 671],
            bar_names=["parâmetros ativados", "parâmetros totais"],
            y_range=[0, 700, 100],
            x_length=7.0, y_length=4.0,
            bar_colors=[MECHANISM, OLD],
        ).shift(DOWN * 0.2 + LEFT * 0.5)
        chart_caption = Text("DeepSeek-V3: bilhões de parâmetros", font_size=16, color=GRAY_B)
        chart_caption.next_to(chart, UP, buff=0.25)

        chart_group = VGroup(chart, chart_caption)
        assert_on_screen(chart_group, "overview moe bar chart")
        self.play(FadeIn(chart_caption))
        self.play(Create(chart))
        note2 = Text('"671B parâmetros totais e 37B ativados, treinado em 14,8T de tokens"', font_size=16, color=MECHANISM)
        note2.next_to(chart, DOWN, buff=0.4)
        if note2.width > 12.6:
            note2.scale_to_fit_width(12.6)
        assert_no_overlap(chart_group, note2, "overview moe chart vs caption note")
        self.play(FadeIn(note2))
        self.wait(16)
        self.play(FadeOut(c6), FadeOut(chart_group), FadeOut(note2))

        # --- 8. Timeline across the nine models ---
        c7 = callout("A linhagem: nove arquiteturas, uma evolução contínua", color=MECHANISM)
        self.play(FadeIn(c7))

        steps = [
            ("Transformer\n(2017)", "encoder-decoder,\natenção pura", MECHANISM),
            ("GPT / BERT\n(2018)", "decoder-only vs.\nencoder-only", ENCODER),
            ("LLaMA\n(2023)", "decoder aberto,\nRMSNorm, RoPE", DECODER),
            ("Mistral/DeepSeek\n(2023-24)", "MoE: escala sem\ncusto total por token", MECHANISM),
            ("Mamba/RWKV\n(2023)", "sem atenção:\nSSM / RNN linear", OLD),
        ]
        step_boxes = VGroup(*[
            sized_box(f"{name}\n{desc}", font_size=16, color=WHITE, box_color=color, box_opacity=0.35, min_width=2.3, min_height=1.7, line_spacing=1.0)
            for name, desc, color in steps
        ]).arrange(RIGHT, buff=0.2)
        assert_on_screen(step_boxes, "overview llm timeline boxes width check")
        timeline_arrows = VGroup(*[
            Arrow(step_boxes[i].get_right(), step_boxes[i + 1].get_left(), buff=0.06, color=GRAY_B, stroke_width=2)
            for i in range(len(step_boxes) - 1)
        ])
        timeline = VGroup(step_boxes, timeline_arrows)
        assert_on_screen(timeline, "overview llm timeline")
        self.play(LaggedStart(*[FadeIn(b) for b in step_boxes], lag_ratio=0.15))
        self.play(*[GrowArrow(a) for a in timeline_arrows])
        self.wait(18)
        self.play(FadeOut(c7), FadeOut(timeline))

        # --- Closing ---
        backdrop = RoundedRectangle(corner_radius=0.2, width=13, height=4.0, fill_color="#111111", fill_opacity=0.9, stroke_width=0)
        closing = Text(
            "Atenção resolveu a paralelização, mas custa O(n^2);\n"
            "MoE resolve escala sem pagar por todo parâmetro a cada token;\n"
            "Mamba e RWKV perguntam se a atenção era mesmo necessária.\n"
            "A seguir, cada uma das nove arquiteturas em detalhe.",
            font_size=22, color=WHITE, line_spacing=1.35,
        ).move_to(ORIGIN)
        if closing.width > 12.4:
            closing.scale_to_fit_width(12.4)
        self.play(FadeIn(backdrop))
        self.play(Write(closing, run_time=2))
        self.wait(9)
        self.play(FadeOut(backdrop), FadeOut(closing))
