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

class VLMOverviewScene(Scene):
    def construct(self):
        # --- 1. Opening ---
        title = Text("VLMs", font_size=52, color=WHITE)
        subtitle = Text("De CLIP a Qwen-VL — visão geral da série", font_size=22, color=GRAY_B)
        if subtitle.width > 12.8:
            subtitle.scale_to_fit_width(12.8)
        subtitle.next_to(title, DOWN, buff=0.35)
        tag = Text("seis arquiteturas, um problema central: alinhar dois espaços de representação", font_size=17, color=MECHANISM)
        tag.next_to(subtitle, DOWN, buff=0.5)
        if tag.width > 12.6:
            tag.scale_to_fit_width(12.6)
        self.play(Write(title, run_time=1.6))
        self.play(FadeIn(subtitle))
        self.play(FadeIn(tag))
        self.wait(12)
        self.play(FadeOut(title), FadeOut(subtitle), FadeOut(tag))

        # --- 2. The core problem: two separate spaces ---
        c1 = callout("O problema central: imagem e texto vivem em espaços diferentes")
        self.play(FadeIn(c1))

        img_box = sized_box("espaço de imagens\n(pixels, texturas,\nformas)", font_size=16, color=WHITE, box_color=ENCODER, box_opacity=0.35, min_width=4.6, min_height=1.6, line_spacing=1.15)
        img_box.shift(LEFT * 3.4)
        txt_box = sized_box("espaço de texto\n(tokens, sintaxe,\nsemântica)", font_size=16, color=WHITE, box_color=DECODER, box_opacity=0.35, min_width=4.6, min_height=1.6, line_spacing=1.15)
        txt_box.shift(RIGHT * 3.4)
        gap_arrow = DoubleArrow(img_box.get_right(), txt_box.get_left(), buff=0.15, color=MECHANISM, stroke_width=3)
        vs_row = VGroup(img_box, txt_box, gap_arrow)
        assert_on_screen(vs_row, "overview two spaces")
        self.play(FadeIn(img_box))
        self.play(FadeIn(txt_box))
        self.play(GrowArrow(gap_arrow))
        note1 = Text("cada um dos seis papers é uma forma diferente de construir essa ponte", font_size=16, color=MECHANISM)
        note1.next_to(vs_row, DOWN, buff=0.7)
        if note1.width > 12.6:
            note1.scale_to_fit_width(12.6)
        self.play(FadeIn(note1))
        self.wait(16)
        self.play(FadeOut(c1), FadeOut(vs_row), FadeOut(note1))

        # --- 3. CLIP's contrastive loss, from the paper's own pseudocode ---
        c2 = callout("O cálculo do CLIP: similaridade de cosseno com temperatura (Radford et al., 2021)", color=MECHANISM)
        self.play(FadeIn(c2))

        clip_formula = MathTex(
            r"\text{logits} = ",
            r"(I_e \cdot T_e^T)",
            r"\cdot",
            r"e^{\,t}",
            font_size=36, color=WHITE,
        )
        assert_on_screen(clip_formula, "overview clip formula")
        self.play(Write(clip_formula, run_time=2))
        self.wait(3)

        sim_term = clip_formula[1]
        box_sim = SurroundingRectangle(sim_term, color=ENCODER, buff=0.08)
        label_sim = Text("similaridade de cosseno entre TODOS os pares imagem-texto do batch", font_size=16, color=ENCODER)
        label_sim.next_to(clip_formula, DOWN, buff=0.7)
        if label_sim.width > 12.4:
            label_sim.scale_to_fit_width(12.4)
        self.play(Create(box_sim), FadeIn(label_sim))
        self.wait(7)
        self.play(FadeOut(box_sim), FadeOut(label_sim))

        temp_term = clip_formula[3]
        box_temp = SurroundingRectangle(temp_term, color=MECHANISM, buff=0.08)
        label_temp = Text("temperatura aprendida: afia ou suaviza a distribuição antes do softmax", font_size=16, color=MECHANISM)
        label_temp.next_to(clip_formula, DOWN, buff=0.7)
        if label_temp.width > 12.4:
            label_temp.scale_to_fit_width(12.4)
        self.play(Create(box_temp), FadeIn(label_temp))
        self.wait(7)
        self.play(FadeOut(box_temp), FadeOut(label_temp))

        note_clip = Text("a loss final é cross-entropy simétrica: uma vez por linha, uma vez por coluna da matriz", font_size=16, color=GRAY_B)
        note_clip.next_to(clip_formula, DOWN, buff=0.7)
        if note_clip.width > 12.6:
            note_clip.scale_to_fit_width(12.6)
        self.play(FadeIn(note_clip))
        self.wait(8)
        self.play(FadeOut(c2), FadeOut(clip_formula), FadeOut(note_clip))

        # --- 4. The similarity matrix, plotted as a real heatmap ---
        c3 = callout("Na prática: uma matriz de similaridade imagem x texto, no mesmo batch", color=MECHANISM)
        self.play(FadeIn(c3))

        n = 4
        sims = [
            [0.9, 0.1, 0.05, 0.05],
            [0.1, 0.85, 0.1, 0.1],
            [0.05, 0.1, 0.8, 0.15],
            [0.05, 0.1, 0.1, 0.88],
        ]
        cell_size = 0.9
        grid = VGroup()
        for i in range(n):
            for j in range(n):
                is_diag = (i == j)
                color = MECHANISM if is_diag else ENCODER
                cell = Square(side_length=cell_size, color=color, fill_color=color, fill_opacity=sims[i][j], stroke_width=1)
                cell.move_to(RIGHT * j * cell_size + DOWN * i * cell_size)
                grid.add(cell)
        grid.move_to(ORIGIN)
        img_labels = VGroup(*[Text(f"img{i+1}", font_size=16, color=GRAY_B) for i in range(n)]).arrange(DOWN, buff=cell_size - 0.35)
        img_labels.next_to(grid, LEFT, buff=0.35)
        txt_labels = VGroup(*[Text(f"txt{i+1}", font_size=16, color=GRAY_B) for i in range(n)]).arrange(RIGHT, buff=cell_size - 0.35)
        txt_labels.next_to(grid, UP, buff=0.35)

        heatmap = VGroup(grid, img_labels, txt_labels)
        assert_on_screen(heatmap, "overview clip similarity heatmap")
        self.play(FadeIn(grid))
        self.play(FadeIn(img_labels), FadeIn(txt_labels))
        note2 = Text("a diagonal (pares verdadeiros) deve ter alta similaridade; fora dela, baixa", font_size=16, color=MECHANISM)
        note2.next_to(heatmap, DOWN, buff=0.6)
        if note2.width > 12.6:
            note2.scale_to_fit_width(12.6)
        self.play(FadeIn(note2))
        self.wait(16)
        self.play(FadeOut(c3), FadeOut(heatmap), FadeOut(note2))

        # --- 5. ViT: how an image becomes a sequence ---
        c4 = callout("Antes de comparar: como uma imagem se torna uma sequência (ViT)", color=MECHANISM)
        self.play(FadeIn(c4))

        patch_grid = VGroup(*[
            Square(side_length=0.55, color=ENCODER, fill_color=ENCODER, fill_opacity=0.2, stroke_width=1)
            for _ in range(16)
        ]).arrange_in_grid(rows=4, cols=4, buff=0.05)
        patch_grid.shift(LEFT * 3.6)
        patch_grid_label = Text("imagem\n(patches 16x16)", font_size=16, color=GRAY_B, line_spacing=1.1).next_to(patch_grid, DOWN, buff=0.3)

        seq_boxes = VGroup(*[
            sized_box(f"p{i+1}", font_size=16, color=WHITE, box_color=ENCODER, box_opacity=0.3, min_width=0.8, min_height=0.7)
            for i in range(6)
        ]).arrange(RIGHT, buff=0.15)
        seq_boxes.shift(RIGHT * 2.6)
        seq_label = Text("sequência de patches\n(+ posição, como no Transformer)", font_size=16, color=GRAY_B, line_spacing=1.1).next_to(seq_boxes, DOWN, buff=0.3)

        arrow_vit = Arrow(patch_grid.get_right(), seq_boxes.get_left(), buff=0.3, color=MECHANISM, stroke_width=3)

        vit_group = VGroup(patch_grid, patch_grid_label, seq_boxes, seq_label, arrow_vit)
        assert_no_overlap(patch_grid, seq_boxes, "overview vit patches vs sequence")
        assert_on_screen(vit_group, "overview vit diagram")
        self.play(FadeIn(patch_grid), FadeIn(patch_grid_label))
        self.play(GrowArrow(arrow_vit))
        self.play(FadeIn(seq_boxes), FadeIn(seq_label))
        self.wait(16)
        self.play(FadeOut(c4), FadeOut(vit_group))

        # --- 6. Four strategies for the same bridge ---
        c5 = callout("Quatro estratégias diferentes para construir a mesma ponte", color=MECHANISM)
        self.play(FadeIn(c5))

        strat1 = sized_box("CLIP\ncontrastive:\nencoders separados,\nespaço compartilhado", font_size=16, color=WHITE, box_color=MECHANISM, box_opacity=0.35, min_width=3.0, min_height=1.7, line_spacing=1.05)
        strat2 = sized_box("Flamingo\ncross-attention:\nLLM congelado \"olha\"\npara features visuais", font_size=16, color=WHITE, box_color=ENCODER, box_opacity=0.35, min_width=3.0, min_height=1.7, line_spacing=1.05)
        strat3 = sized_box("LLaVA\nprojeção linear:\nfeatures visuais como\ntokens no LLM", font_size=16, color=WHITE, box_color=DECODER, box_opacity=0.35, min_width=3.0, min_height=1.7, line_spacing=1.05)
        strat4 = sized_box("BLIP-2\nQ-Former:\nqueries aprendidas\ncomprimem a imagem", font_size=16, color=WHITE, box_color=OLD, box_opacity=0.35, min_width=3.0, min_height=1.7, line_spacing=1.05)
        strat_row = VGroup(strat1, strat2, strat3, strat4).arrange(RIGHT, buff=0.3)
        assert_on_screen(strat_row, "overview four fusion strategies")
        self.play(LaggedStart(*[FadeIn(b) for b in strat_row], lag_ratio=0.2))
        self.wait(18)
        self.play(FadeOut(c5), FadeOut(strat_row))

        # --- 6.4. The trend hidden in those four strategies: freeze more, train less ---
        c5a = callout("O eixo escondido nessas quatro estratégias: quanto treinar do zero", color=MECHANISM)
        self.play(FadeIn(c5a))

        frozen_full = sized_box("CLIP\ntreina os DOIS\nencoders do zero", font_size=16, color=WHITE, box_color=OLD, box_opacity=0.3, min_width=3.6, min_height=1.5, line_spacing=1.15)
        frozen_full.shift(LEFT * 4.2)
        frozen_partial = sized_box("Flamingo / BLIP-2\nvisão E LLM congelados —\nsó a ponte é treinada", font_size=16, color=WHITE, box_color=ENCODER, box_opacity=0.3, min_width=4.0, min_height=1.5, line_spacing=1.15)
        frozen_minimal = sized_box("LLaVA / Qwen-VL\numa projeção linear\nbasta como ponte", font_size=16, color=WHITE, box_color=MECHANISM, box_opacity=0.35, min_width=3.6, min_height=1.5, line_spacing=1.15)
        frozen_minimal.shift(RIGHT * 4.2)
        frozen_row = VGroup(frozen_full, frozen_partial, frozen_minimal)
        assert_no_overlap(frozen_full, frozen_partial, "overview frozen trend full vs partial")
        assert_no_overlap(frozen_partial, frozen_minimal, "overview frozen trend partial vs minimal")
        assert_on_screen(frozen_row, "overview frozen trend row")
        self.play(FadeIn(frozen_full))
        self.play(FadeIn(frozen_partial))
        self.play(FadeIn(frozen_minimal))
        note_frozen = Text("cada geração treina uma fração menor do modelo total — a ponte é onde o aprendizado real acontece", font_size=16, color=GRAY_B)
        note_frozen.next_to(frozen_row, DOWN, buff=0.6)
        if note_frozen.width > 12.6:
            note_frozen.scale_to_fit_width(12.6)
        self.play(FadeIn(note_frozen))
        self.wait(16)
        self.play(FadeOut(c5a), FadeOut(frozen_row), FadeOut(note_frozen))

        # --- 6.5. Compressing the image into fewer tokens ---
        c5b = callout("O outro eixo de eficiência: quantos tokens uma imagem realmente precisa", color=MECHANISM)
        self.play(FadeIn(c5b))

        chart = BarChart(
            values=[576, 256, 32],
            bar_names=["patches ViT\n(imagem 384x384)", "adaptador\nQwen-VL", "queries\nQ-Former (BLIP-2)"],
            y_range=[0, 600, 100],
            x_length=8.6, y_length=4.0,
            bar_colors=[ENCODER, DECODER, MECHANISM],
        ).shift(DOWN * 0.2 + LEFT * 0.3)
        chart_caption = Text("número de tokens visuais entregues ao LLM, por estratégia", font_size=16, color=GRAY_B)
        chart_caption.next_to(chart, UP, buff=0.25)
        chart_group = VGroup(chart, chart_caption)
        assert_on_screen(chart_group, "overview token compression bar chart")
        self.play(FadeIn(chart_caption))
        self.play(Create(chart))
        note_chart = Text("menos tokens visuais = contexto mais barato para o LLM processar por imagem", font_size=16, color=MECHANISM)
        note_chart.next_to(chart, DOWN, buff=0.35)
        if note_chart.width > 12.6:
            note_chart.scale_to_fit_width(12.6)
        assert_no_overlap(chart_group, note_chart, "overview token chart vs caption note")
        self.play(FadeIn(note_chart))
        self.wait(16)
        self.play(FadeOut(c5b), FadeOut(chart_group), FadeOut(note_chart))

        # --- 7. Timeline across the six models ---
        c6 = callout("A linhagem: seis arquiteturas, cada vez mais eficientes em unir as duas modalidades", color=MECHANISM)
        self.play(FadeIn(c6))

        steps = [
            ("ViT (2020)", "imagem como\nsequência de patches", ENCODER),
            ("CLIP (2021)", "espaço compartilhado\npor contraste", MECHANISM),
            ("Flamingo (2022)", "cross-attention,\nLLM congelado", ENCODER),
            ("BLIP-2 (2023)", "Q-Former: poucos\ntokens comprimidos", OLD),
            ("LLaVA/Qwen-VL\n(2023-24)", "projeção direta", DECODER),
        ]
        step_boxes = VGroup(*[
            sized_box(f"{name}\n{desc}", font_size=16, color=WHITE, box_color=color, box_opacity=0.35, min_width=2.1, min_height=1.7, margin=0.22, line_spacing=1.0)
            for name, desc, color in steps
        ]).arrange(RIGHT, buff=0.15)
        assert_on_screen(step_boxes, "overview vlm timeline width check")
        timeline_arrows = VGroup(*[
            Arrow(step_boxes[i].get_right(), step_boxes[i + 1].get_left(), buff=0.06, color=GRAY_B, stroke_width=2)
            for i in range(len(step_boxes) - 1)
        ])
        timeline = VGroup(step_boxes, timeline_arrows)
        assert_on_screen(timeline, "overview vlm timeline")
        self.play(LaggedStart(*[FadeIn(b) for b in step_boxes], lag_ratio=0.15))
        self.play(*[GrowArrow(a) for a in timeline_arrows])
        self.wait(18)
        self.play(FadeOut(c6), FadeOut(timeline))

        # --- 8. Worked example: one CLIP similarity score, in numbers ---
        c7 = callout("Em números: calculando um único score de similaridade", color=MECHANISM)
        self.play(FadeIn(c7))
        worked = terminal_box([
            "I_e = [0.6, 0.8]   T_e = [0.8, 0.6]   (embeddings L2-normalizados)",
            "similaridade de cosseno: I_e . T_e = 0.6*0.8 + 0.8*0.6 = 0.96",
            "escala pela temperatura aprendida: 0.96 * e^t  (t ~ 4.6 no paper)",
            "softmax dessa linha inteira -> probabilidade de cada par ser o certo",
        ], font_size=16).shift(DOWN * 0.1)
        assert_on_screen(worked, "overview clip worked example")
        self.play(FadeIn(worked))
        self.wait(16)
        self.play(FadeOut(c7), FadeOut(worked))

        # --- 9. Results ---
        c8 = callout("O resultado citado no próprio paper do CLIP:")
        self.play(FadeIn(c8))
        term = terminal_box([
            '"melhora a acurácia no ImageNet de uma prova de conceito de',
            ' 11,5% para 76,2%" — sem usar nenhum dos 1,28 milhão de',
            ' exemplos rotulados do dataset (zero-shot)',
            '"95% de acurácia top-5" — no nível de um Inception-V4 supervisionado',
        ], font_size=16).shift(DOWN * 0.1)
        assert_on_screen(term, "overview clip results terminal")
        self.play(FadeIn(term))
        self.wait(16)
        self.play(FadeOut(c8), FadeOut(term))

        # --- Closing ---
        backdrop = RoundedRectangle(corner_radius=0.2, width=13, height=4.0, fill_color="#111111", fill_opacity=0.9, stroke_width=0)
        closing = Text(
            "CLIP alinhou os dois espaços por contraste;\n"
            "Flamingo e BLIP-2 aprenderam a conectá-los a um LLM já pronto;\n"
            "LLaVA e Qwen-VL simplificaram a ponte até virar só uma projeção.\n"
            "A seguir, cada uma das seis arquiteturas em detalhe.",
            font_size=22, color=WHITE, line_spacing=1.35,
        ).move_to(ORIGIN)
        if closing.width > 12.4:
            closing.scale_to_fit_width(12.4)
        self.play(FadeIn(backdrop))
        self.play(Write(closing, run_time=2))
        self.wait(9)
        self.play(FadeOut(backdrop), FadeOut(closing))
