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

class JEPAOverviewScene(Scene):
    def construct(self):
        # --- 1. Opening ---
        title = Text("JEPA", font_size=52, color=WHITE)
        subtitle = Text("Joint-Embedding Predictive Architecture — visão geral da série", font_size=22, color=GRAY_B)
        if subtitle.width > 12.8:
            subtitle.scale_to_fit_width(12.8)
        subtitle.next_to(title, DOWN, buff=0.35)
        tag = Text("quatro papers, uma ideia central: prever representações, não pixels", font_size=17, color=MECHANISM)
        tag.next_to(subtitle, DOWN, buff=0.5)
        if tag.width > 12.6:
            tag.scale_to_fit_width(12.6)
        self.play(Write(title, run_time=1.6))
        self.play(FadeIn(subtitle))
        self.play(FadeIn(tag))
        self.wait(12)
        self.play(FadeOut(title), FadeOut(subtitle), FadeOut(tag))

        # --- 2. The core contrast: pixels vs representations ---
        c1 = callout("A ideia central que atravessa toda a série")
        self.play(FadeIn(c1))

        pixel_box = sized_box("prever PIXELS\n(reconstrução completa,\ndetalhe imprevisível incluso)", font_size=15, color=WHITE, box_color=OLD, box_opacity=0.25, min_width=4.8, min_height=1.6, line_spacing=1.2)
        pixel_box.shift(LEFT * 3.4)
        rep_box = sized_box("prever REPRESENTAÇÕES\n(estrutura semântica,\nsem gastar capacidade no ruído)", font_size=15, color=WHITE, box_color=MECHANISM, box_opacity=0.4, min_width=4.8, min_height=1.6, line_spacing=1.2)
        rep_box.shift(RIGHT * 3.4)
        vs_row = VGroup(pixel_box, rep_box)
        assert_on_screen(vs_row, "overview pixels vs reps")
        self.play(FadeIn(pixel_box))
        self.play(FadeIn(rep_box))
        note1 = Text("a textura exata de uma folha é imprevisível — a estrutura do mundo não precisa ser", font_size=15, color=GRAY_B)
        note1.next_to(vs_row, DOWN, buff=0.7)
        if note1.width > 12.6:
            note1.scale_to_fit_width(12.6)
        self.play(FadeIn(note1))
        self.wait(16)
        self.play(FadeOut(c1), FadeOut(vs_row), FadeOut(note1))

        # --- 3. Energy-Based Models: why "collapse" is the enemy ---
        c2 = callout("Por que colapso é o inimigo: a intuição por trás do design (Energy-Based Models)", color=MECHANISM)
        self.play(FadeIn(c2))

        axes1 = Axes(
            x_range=[-3, 3, 1], y_range=[0, 3, 1],
            x_length=7.6, y_length=3.0,
            axis_config={"color": GRAY_B, "stroke_width": 2, "include_tip": False},
        ).shift(UP * 0.35)
        x_label1 = Text("compatibilidade entre x e y", font_size=14, color=GRAY_B).next_to(axes1.x_axis, DOWN, buff=0.2)
        y_label1 = Text("energia", font_size=14, color=GRAY_B).rotate(90 * DEGREES).next_to(axes1.y_axis, LEFT, buff=0.15)
        collapsed_curve = axes1.plot(lambda x: 2.4, color=OLD, stroke_width=5)
        healthy_curve = axes1.plot(lambda x: 0.3 + 2.3 * (1 - np.exp(-(x ** 2) / 1.2)), color=MECHANISM, stroke_width=5)

        graph1 = VGroup(axes1, x_label1, y_label1, collapsed_curve, healthy_curve)
        assert_on_screen(graph1, "overview energy landscape graph")
        self.play(Create(axes1), FadeIn(x_label1), FadeIn(y_label1))
        self.play(Create(collapsed_curve))
        self.play(Create(healthy_curve))

        legend_a = VGroup(Dot(color=OLD, radius=0.08), Text("colapso: energia achatada — o encoder ignora a entrada e aprende nada", font_size=13, color=GRAY_B)).arrange(RIGHT, buff=0.2)
        legend_b = VGroup(Dot(color=MECHANISM, radius=0.08), Text("objetivo real: vale de baixa energia só nos pares compatíveis", font_size=13, color=GRAY_B)).arrange(RIGHT, buff=0.2)
        legend = VGroup(legend_a, legend_b).arrange(DOWN, buff=0.18, aligned_edge=LEFT)
        legend.next_to(graph1, DOWN, buff=0.4)
        if legend.width > 12.4:
            legend.scale_to_fit_width(12.4)
        assert_on_screen(legend, "overview energy legend")
        assert_no_overlap(graph1, legend, "overview energy graph vs legend")
        self.play(FadeIn(legend))
        self.wait(18)
        self.play(FadeOut(c2), FadeOut(graph1), FadeOut(legend))

        # --- 4. Three families of self-supervised architecture ---
        c3 = callout("LeCun enquadra isso como três famílias de arquitetura", color=MECHANISM)
        self.play(FadeIn(c3))

        je_box = sized_box("Joint-Embedding\n(x, y compatíveis -> embeddings\nsemelhantes; risco: colapso)", font_size=13, color=WHITE, box_color=OLD, box_opacity=0.25, min_width=4.0, min_height=1.5, line_spacing=1.15)
        je_box.shift(LEFT * 4.3)
        gen_box = sized_box("Generativa\n(decoder reconstrói y\na partir de x, pixel a pixel)", font_size=13, color=WHITE, box_color=OLD, box_opacity=0.25, min_width=4.0, min_height=1.5, line_spacing=1.15)
        jepa_box = sized_box("Joint-Embedding\nPREDICTIVE (JEPA)\n(predictor prevê a\nrepresentação de y)", font_size=13, color=WHITE, box_color=MECHANISM, box_opacity=0.4, min_width=4.0, min_height=1.5, line_spacing=1.1)
        jepa_box.shift(RIGHT * 4.3)
        families_row = VGroup(je_box, gen_box, jepa_box)
        assert_no_overlap(je_box, gen_box, "overview family boxes je vs gen")
        assert_no_overlap(gen_box, jepa_box, "overview family boxes gen vs jepa")
        assert_on_screen(families_row, "overview three families row")
        self.play(FadeIn(je_box))
        self.play(FadeIn(gen_box))
        self.play(FadeIn(jepa_box))
        self.play(Indicate(jepa_box, color=MECHANISM, scale_factor=1.08))
        note2 = Text("JEPA combina o melhor das duas: aprende no espaço de embeddings, mas prediz — não só compara", font_size=15, color=MECHANISM)
        note2.next_to(families_row, DOWN, buff=0.6)
        if note2.width > 12.6:
            note2.scale_to_fit_width(12.6)
        self.play(FadeIn(note2))
        self.wait(16.8)
        self.play(FadeOut(c3), FadeOut(families_row), FadeOut(note2))

        # --- 5. The loss: the actual calculation JEPA uses ---
        c4 = callout("O cálculo: a loss de predição usada pelas variantes JEPA", color=MECHANISM)
        self.play(FadeIn(c4))

        loss_formula = MathTex(
            r"\mathcal{L} = \frac{1}{M} \sum_{i=1}^{M} \Big\|",
            r"P_\phi(s_x, z_i)",
            r"-",
            r"\text{sg}\big(s_{y}^{(i)}\big)",
            r"\Big\|_2^2",
            font_size=34, color=WHITE,
        )
        assert_on_screen(loss_formula, "overview loss formula")
        self.play(Write(loss_formula, run_time=2.2))
        self.wait(4)

        pred_term = loss_formula[1]
        sg_term = loss_formula[3]

        box_pred = SurroundingRectangle(pred_term, color=MECHANISM, buff=0.08)
        label_pred = Text("predictor: prevê a representação do alvo a partir do contexto", font_size=14, color=MECHANISM)
        label_pred.next_to(loss_formula, DOWN, buff=0.7)
        if label_pred.width > 12.4:
            label_pred.scale_to_fit_width(12.4)
        self.play(Create(box_pred), FadeIn(label_pred))
        self.wait(8)
        self.play(FadeOut(box_pred), FadeOut(label_pred))

        box_sg = SurroundingRectangle(sg_term, color=ENCODER, buff=0.08)
        label_sg = Text("stop-gradient: o alvo nunca recebe gradiente direto do predictor", font_size=14, color=ENCODER)
        label_sg.next_to(loss_formula, DOWN, buff=0.7)
        if label_sg.width > 12.4:
            label_sg.scale_to_fit_width(12.4)
        self.play(Create(box_sg), FadeIn(label_sg))
        self.wait(8)
        self.play(FadeOut(box_sg), FadeOut(label_sg))

        note3 = Text("sem o stop-gradient, o sistema inteiro colapsa para a saída constante da Seção anterior", font_size=15, color=GRAY_B)
        note3.next_to(loss_formula, DOWN, buff=0.7)
        if note3.width > 12.6:
            note3.scale_to_fit_width(12.6)
        self.play(FadeIn(note3))
        self.wait(14)
        self.play(FadeOut(c4), FadeOut(loss_formula), FadeOut(note3))

        # --- 6. The generic architecture, colors matching the formula ---
        c5 = callout("O padrão arquitetural que se repete nos quatro papers", color=MECHANISM)
        self.play(FadeIn(c5))

        ctx = sized_box("Context\nEncoder\n(gera s_x)", font_size=15, color=WHITE, box_color=ENCODER, box_opacity=0.35, min_width=2.7, min_height=1.35, line_spacing=1.05)
        ctx.shift(LEFT * 4.2)
        pred = sized_box("Predictor\nP_phi", font_size=16, color=WHITE, box_color=MECHANISM, box_opacity=0.5, min_width=2.4, min_height=1.35, line_spacing=1.05)
        tgt = sized_box("Target Encoder\n(EMA, stop-grad)", font_size=14, color=WHITE, box_color=ENCODER, box_opacity=0.2, min_width=2.9, min_height=1.35, line_spacing=1.05)
        tgt.shift(RIGHT * 4.2)

        arrow1 = Arrow(ctx.get_right(), pred.get_left(), buff=0.1, color=ENCODER, stroke_width=3)
        arrow2 = Arrow(pred.get_right(), tgt.get_left(), buff=0.1, color=MECHANISM, stroke_width=3)
        clearance = pred.get_top()[1] + 0.4
        ctx_up = np.array([ctx.get_top()[0], clearance, 0])
        tgt_up = np.array([tgt.get_top()[0], clearance, 0])
        ema_stub1 = Line(ctx.get_top(), ctx_up, color=GRAY_B, stroke_width=2)
        ema_bar = Line(ctx_up, tgt_up, color=GRAY_B, stroke_width=2)
        ema_stub2 = Arrow(tgt_up, tgt.get_top(), buff=0.0, color=GRAY_B, stroke_width=2)
        ema_arrow = VGroup(ema_stub1, ema_bar, ema_stub2)
        assert_no_overlap(ema_arrow, pred, "overview ema_arrow vs predictor box")

        arch_group = VGroup(ctx, pred, tgt, arrow1, arrow2, ema_arrow)
        assert_on_screen(arch_group, "overview generic architecture diagram")
        self.play(FadeIn(ctx))
        self.play(GrowArrow(arrow1), FadeIn(pred))
        self.play(GrowArrow(arrow2), FadeIn(tgt))
        self.play(Create(ema_arrow))
        note4 = Text("as mesmas cores da fórmula: azul = ramo do contexto, amarelo = predictor", font_size=15, color=MECHANISM)
        note4.next_to(arch_group, DOWN, buff=0.7)
        if note4.width > 12.6:
            note4.scale_to_fit_width(12.6)
        self.play(FadeIn(note4))
        self.wait(16.8)
        self.play(FadeOut(c5), FadeOut(arch_group), FadeOut(note4))

        # --- 7. The EMA momentum schedule, plotted ---
        c6 = callout("A EMA em números: o schedule de momentum, do próprio paper do I-JEPA", color=MECHANISM)
        self.play(FadeIn(c6))

        ema_formula = MathTex(
            r"\theta_{\text{target}} \leftarrow m\,\theta_{\text{target}} + (1-m)\,\theta_{\text{context}}",
            font_size=30, color=WHITE,
        ).shift(UP * 2.1)
        assert_on_screen(ema_formula, "overview ema formula")
        self.play(Write(ema_formula, run_time=1.6))

        axes2 = Axes(
            x_range=[0, 1, 0.25], y_range=[0.996, 1.0, 0.001],
            x_length=7.6, y_length=2.6,
            axis_config={"color": GRAY_B, "stroke_width": 2, "include_tip": False},
        ).shift(DOWN * 1.0)
        x_label2 = Text("progresso do pré-treino", font_size=13, color=GRAY_B).next_to(axes2.x_axis, DOWN, buff=0.2)
        momentum_curve = axes2.plot(lambda x: 0.996 + 0.004 * x, color=MECHANISM, stroke_width=5, x_range=[0, 1])
        start_label = Text("m = 0,996", font_size=14, color=MECHANISM).next_to(axes2.c2p(0, 0.996), DOWN + LEFT, buff=0.15)
        end_label = Text("m -> 1,0", font_size=14, color=MECHANISM).next_to(axes2.c2p(1, 1.0), UP + RIGHT, buff=0.12)

        graph2 = VGroup(axes2, x_label2, momentum_curve, start_label, end_label)
        assert_no_overlap(ema_formula, graph2, "overview ema formula vs momentum graph")
        assert_on_screen(graph2, "overview momentum schedule graph")
        self.play(Create(axes2), FadeIn(x_label2))
        self.play(Create(momentum_curve), FadeIn(start_label), FadeIn(end_label))
        note5 = Text('"usamos um valor de momentum de 0,996 e o aumentamos linearmente até 1,0" — quanto mais perto de 1, mais devagar o alvo muda, gerando alvos estáveis', font_size=13, color=GRAY_B, line_spacing=1.2)
        note5.next_to(graph2, DOWN, buff=0.35)
        if note5.width > 12.6:
            note5.scale_to_fit_width(12.6)
        full6 = VGroup(ema_formula, graph2, note5)
        assert_on_screen(full6, "overview full ema section")
        self.play(FadeIn(note5))
        self.wait(18)
        self.play(FadeOut(c6), FadeOut(ema_formula), FadeOut(graph2), FadeOut(note5))

        # --- 7.5. A worked numeric example of one EMA update ---
        c6b = callout("Em números: uma única atualização do target encoder", color=MECHANISM)
        self.play(FadeIn(c6b))
        worked = terminal_box([
            "m = 0,996  (início do pré-treino)",
            "peso do context encoder muda: 0,5000 -> 0,5200 nesta iteração",
            "novo peso do target encoder:",
            "  0,996 x 0,5000  +  0,004 x 0,5200  =  0,50008",
            "-> o target encoder mal se move (+0,00008), mesmo o context",
            "   encoder tendo mudado 250x mais (+0,02) — alvo estável",
        ], font_size=15).shift(DOWN * 0.1)
        assert_on_screen(worked, "overview ema worked example")
        self.play(FadeIn(worked))
        self.wait(16)
        self.play(FadeOut(c6b), FadeOut(worked))

        # --- 8. Timeline across the four papers ---
        c7 = callout("O que muda de paper para paper: o domínio do alvo mascarado", color=MECHANISM)
        self.play(FadeIn(c7))

        steps = [
            ("LeCun\n(2022)", "tese de\nposicionamento", OLD),
            ("I-JEPA\n(2023)", "blocos 2D\nem imagens", ENCODER),
            ("V-JEPA\n(2024)", "tubos espaço-\ntemporais em vídeo", MECHANISM),
            ("V-JEPA 2\n(2025)", "estados futuros\ncondicionados por ação", DECODER),
        ]
        step_boxes = VGroup(*[
            sized_box(f"{name}\n{desc}", font_size=13, color=WHITE, box_color=color, box_opacity=0.35, min_width=3.0, min_height=1.5, line_spacing=1.1)
            for name, desc, color in steps
        ]).arrange(RIGHT, buff=0.55)
        if step_boxes.width > 12.8:
            step_boxes.scale_to_fit_width(12.8)
        timeline_arrows = VGroup(*[
            Arrow(step_boxes[i].get_right(), step_boxes[i + 1].get_left(), buff=0.08, color=GRAY_B, stroke_width=2)
            for i in range(len(step_boxes) - 1)
        ])
        timeline = VGroup(step_boxes, timeline_arrows)
        assert_on_screen(timeline, "overview timeline")
        self.play(LaggedStart(*[FadeIn(b) for b in step_boxes], lag_ratio=0.2))
        self.play(*[GrowArrow(a) for a in timeline_arrows])
        note6 = Text("imagem estática -> vídeo -> planejamento de ações no mundo físico —\na mesma predição em representação, aplicada a domínios cada vez mais ricos", font_size=15, color=GRAY_B, line_spacing=1.2)
        note6.next_to(timeline, DOWN, buff=0.6)
        if note6.width > 12.6:
            note6.scale_to_fit_width(12.6)
        self.play(FadeIn(note6))
        self.wait(18)
        self.play(FadeOut(c7), FadeOut(timeline), FadeOut(note6))

        # --- 8.5. What actually gets masked, side by side ---
        c7b = callout("O que é mascarado, lado a lado, nos três instanciamentos", color=MECHANISM)
        self.play(FadeIn(c7b))

        ijepa_m = sized_box("I-JEPA\nblocos 2D em UMA imagem\n(4 alvos, 1 contexto)", font_size=13, color=WHITE, box_color=ENCODER, box_opacity=0.3, min_width=4.0, min_height=1.5, line_spacing=1.15)
        ijepa_m.shift(LEFT * 4.3)
        vjepa_m = sized_box("V-JEPA\ntubos espaço-temporais\nao longo de VÁRIOS frames", font_size=13, color=WHITE, box_color=MECHANISM, box_opacity=0.35, min_width=4.0, min_height=1.5, line_spacing=1.15)
        vjepa2_m = sized_box("V-JEPA 2\nestado futuro dado o\nestado atual + AÇÕES", font_size=13, color=WHITE, box_color=DECODER, box_opacity=0.3, min_width=4.0, min_height=1.5, line_spacing=1.15)
        vjepa2_m.shift(RIGHT * 4.3)
        masking_row = VGroup(ijepa_m, vjepa_m, vjepa2_m)
        assert_no_overlap(ijepa_m, vjepa_m, "overview masking ijepa vs vjepa")
        assert_no_overlap(vjepa_m, vjepa2_m, "overview masking vjepa vs vjepa2")
        assert_on_screen(masking_row, "overview masking comparison row")
        self.play(FadeIn(ijepa_m))
        self.play(FadeIn(vjepa_m))
        self.play(FadeIn(vjepa2_m))
        note7 = Text("mesmo predictor, mesma loss — só o domínio do que está \"escondido\" cresce a cada paper", font_size=15, color=GRAY_B)
        note7.next_to(masking_row, DOWN, buff=0.6)
        if note7.width > 12.6:
            note7.scale_to_fit_width(12.6)
        self.play(FadeIn(note7))
        self.wait(16)
        self.play(FadeOut(c7b), FadeOut(masking_row), FadeOut(note7))

        # --- 9. Results, plotted as a real bar chart ---
        c8 = callout("Por que isso funciona na prática: eficiência de computação, em barras", color=MECHANISM)
        self.play(FadeIn(c8))

        chart = BarChart(
            values=[1, 2.5, 10],
            bar_names=["I-JEPA\n(ViT-H/14)", "iBOT\n(ViT-S/16)", "MAE\n(ViT-H/14)"],
            y_range=[0, 11, 2],
            x_length=8.6, y_length=4.0,
            bar_colors=[MECHANISM, ENCODER, OLD],
        ).shift(DOWN * 0.2)
        y_axis_label = Text("horas de GPU necessárias (normalizado, I-JEPA = 1x)", font_size=13, color=GRAY_B)
        y_axis_label.next_to(chart, UP, buff=0.25)
        if y_axis_label.width > 12.4:
            y_axis_label.scale_to_fit_width(12.4)

        chart_group = VGroup(chart, y_axis_label)
        assert_on_screen(chart_group, "overview results bar chart")
        self.play(FadeIn(y_axis_label))
        self.play(Create(chart))
        self.wait(18)
        self.play(FadeOut(c8), FadeOut(chart_group))

        c9 = callout("E os resultados de tarefa citados no próprio paper:")
        self.play(FadeIn(c9))
        term = terminal_box([
            "V-JEPA:   81,9% Kinetics-400 / 72,2% SSv2 / 77,9% ImageNet1K",
            "          — mesmo backbone congelado, sem rótulos no treino",
            "V-JEPA 2: zero-shot em braços robóticos Franka reais,",
            "          sem coletar dado nenhum desses robôs específicos",
        ], font_size=15).shift(DOWN * 0.1)
        assert_on_screen(term, "overview results terminal")
        self.play(FadeIn(term))
        self.wait(16.8)
        self.play(FadeOut(c9), FadeOut(term))

        # --- Closing: bridge into the four deep-dive scenes ---
        backdrop = RoundedRectangle(corner_radius=0.2, width=13, height=4.2, fill_color="#111111", fill_opacity=0.9, stroke_width=0)
        closing = Text(
            "Um encoder de contexto, um predictor, um target encoder por EMA —\n"
            "e uma loss que nunca deixa o sistema colapsar.\n"
            "A seguir, cada um dos quatro papers em detalhe:\n"
            "a tese de LeCun, e as três instanciações que a tornaram concreta.",
            font_size=22, color=WHITE, line_spacing=1.35,
        ).move_to(ORIGIN)
        if closing.width > 12.4:
            closing.scale_to_fit_width(12.4)
        self.play(FadeIn(backdrop))
        self.play(Write(closing, run_time=2))
        self.wait(16.8)
        self.play(FadeOut(backdrop), FadeOut(closing))
