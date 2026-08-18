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

class IJEPAScene(Scene):
    def construct(self):
        title = Text("I-JEPA", font_size=44, color=WHITE)
        subtitle = Text("Self-Supervised Learning from Images with a JEPA — Assran et al., Meta AI/FAIR, 2023", font_size=17, color=GRAY_B)
        if subtitle.width > 12.8:
            subtitle.scale_to_fit_width(12.8)
        subtitle.next_to(title, DOWN, buff=0.35)
        self.play(Write(title))
        self.play(FadeIn(subtitle))
        self.wait(5.6)
        self.play(FadeOut(title), FadeOut(subtitle))

        # --- 1. Two prior approaches, and their costs ---
        c1 = callout("Duas famílias anteriores de self-supervised learning em visão, e seus custos")
        self.play(FadeIn(c1))

        inv_box = sized_box("invariância (contrastive)\naugmentations feitas à mão\n-> viés indesejado", font_size=14, color=WHITE, box_color=OLD, box_opacity=0.25, min_width=4.6, min_height=1.5, line_spacing=1.2)
        inv_box.shift(LEFT * 3.4)
        gen_box = sized_box("generativo (MAE)\nreconstrói pixels\n-> gasta capacidade no imprevisível", font_size=14, color=WHITE, box_color=OLD, box_opacity=0.25, min_width=4.6, min_height=1.5, line_spacing=1.2)
        gen_box.shift(RIGHT * 3.4)
        prior_row = VGroup(inv_box, gen_box)
        assert_on_screen(prior_row, "ijepa prior approaches")
        self.play(FadeIn(inv_box))
        self.play(FadeIn(gen_box))
        self.wait(7)
        self.play(FadeOut(c1), FadeOut(prior_row))

        # --- 2. The architecture: context, target, predictor ---
        c2 = callout("A arquitetura: context encoder, target encoder (EMA), predictor no meio", color=MECHANISM)
        self.play(FadeIn(c2))

        ctx = sized_box("Context\nEncoder", font_size=16, color=WHITE, box_color=ENCODER, box_opacity=0.35, min_width=2.6, min_height=1.2, line_spacing=1.1)
        ctx.shift(LEFT * 4.2)
        pred = sized_box("Predictor", font_size=17, color=WHITE, box_color=MECHANISM, box_opacity=0.5, min_width=2.4, min_height=1.2)
        tgt = sized_box("Target\nEncoder (EMA)", font_size=15, color=WHITE, box_color=ENCODER, box_opacity=0.2, min_width=2.8, min_height=1.2, line_spacing=1.1)
        tgt.shift(RIGHT * 4.2)

        arrow1 = Arrow(ctx.get_right(), pred.get_left(), buff=0.1, color=ENCODER, stroke_width=3)
        arrow2 = Arrow(pred.get_right(), tgt.get_left(), buff=0.1, color=MECHANISM, stroke_width=3)
        # Routed over the TOP as an explicit elbow (up / across / down),
        # not a curved Arrow with path_arc — a curved arrow's stroke and
        # arrowhead extend past its two given endpoints in ways that are
        # awkward to bound in advance (two failed curve attempts both
        # dipped back down into the predictor box despite elevated
        # endpoints). A straight elbow's geometry is exact: the vertical
        # stubs sit at ctx/tgt's x (outside pred's x-range), and the
        # horizontal bar sits well above pred's top — no heuristics needed.
        clearance = pred.get_top()[1] + 0.4
        ctx_up = np.array([ctx.get_top()[0], clearance, 0])
        tgt_up = np.array([tgt.get_top()[0], clearance, 0])
        ema_stub1 = Line(ctx.get_top(), ctx_up, color=GRAY_B, stroke_width=2)
        ema_bar = Line(ctx_up, tgt_up, color=GRAY_B, stroke_width=2)
        ema_stub2 = Arrow(tgt_up, tgt.get_top(), buff=0.0, color=GRAY_B, stroke_width=2)
        ema_arrow = VGroup(ema_stub1, ema_bar, ema_stub2)
        assert_no_overlap(ema_arrow, pred, "ema_arrow vs predictor box")

        arch_group = VGroup(ctx, pred, tgt, arrow1, arrow2, ema_arrow)
        assert_on_screen(arch_group, "ijepa architecture diagram")
        self.play(FadeIn(ctx))
        self.play(GrowArrow(arrow1), FadeIn(pred))
        self.play(GrowArrow(arrow2), FadeIn(tgt))
        self.play(Create(ema_arrow))
        note1 = Text("o predictor prevê a REPRESENTAÇÃO do alvo — nunca o target encoder é treinado por gradiente", font_size=15, color=MECHANISM)
        note1.next_to(arch_group, DOWN, buff=0.7)
        if note1.width > 12.6:
            note1.scale_to_fit_width(12.6)
        self.play(FadeIn(note1))
        self.wait(8.4)

        self.play(FadeOut(c2), FadeOut(arch_group), FadeOut(note1))

        # --- 3. The EMA update rule (real math -> MathTex) ---
        c3 = callout("Como o target encoder aprende: uma média móvel exponencial dos pesos do context encoder")
        self.play(FadeIn(c3))

        ema_formula = MathTex(
            r"\theta_{\text{target}} \leftarrow m\,\theta_{\text{target}} + (1-m)\,\theta_{\text{context}}",
            font_size=38, color=WHITE,
        )
        assert_on_screen(ema_formula, "ijepa ema formula")
        self.play(Write(ema_formula))
        note_ema = Text("m próximo de 1: o target encoder muda devagar, gerando alvos estáveis para o predictor", font_size=16, color=GRAY_B)
        note_ema.next_to(ema_formula, DOWN, buff=0.7)
        if note_ema.width > 12.6:
            note_ema.scale_to_fit_width(12.6)
        self.play(FadeIn(note_ema))
        self.wait(8.4)

        self.play(FadeOut(c3), FadeOut(ema_formula), FadeOut(note_ema))

        # --- 4. Masking strategy matters ---
        c4 = callout("A estratégia de máscara é o que garante representações semânticas, não superficiais", color=MECHANISM)
        self.play(FadeIn(c4))
        term = terminal_box([
            "bloco-alvo: precisa ter escala grande o suficiente (semântico,",
            "  não um patch minúsculo e trivial de prever)",
            "bloco-contexto: precisa ser espacialmente distribuído",
            "  (informativo, não uma região pequena e local)",
        ], font_size=16).shift(DOWN * 0.1)
        assert_on_screen(term, "ijepa masking terminal")
        self.play(FadeIn(term))
        self.wait(8)
        self.play(FadeOut(c4), FadeOut(term))

        # --- 4.5 Benchmarks against the two prior families, with real numbers ---
        c4b = callout("Contra as duas famílias anteriores, com números do próprio paper:", color=MECHANISM)
        self.play(FadeIn(c4b))
        term_bench = terminal_box([
            "I-JEPA supera o MAE (reconstrução de pixels) em linear",
            "  probing no ImageNet-1K, em semi-supervisionado com 1%",
            "  dos rótulos, e em transferência semântica",
            "pré-treinar um ViT-H/14 leva menos de 1200 horas de GPU:",
            "  2,5x mais rápido que um ViT-S/16 treinado com iBOT,",
            "  e 10x mais eficiente que um ViT-H/14 treinado com MAE",
        ], font_size=15).shift(DOWN * 0.1)
        assert_on_screen(term_bench, "ijepa benchmark terminal")
        self.play(FadeIn(term_bench))
        self.wait(8.4)
        self.play(FadeOut(c4b), FadeOut(term_bench))

        # --- 5. Result ---
        c5 = callout("O resultado de eficiência citado no próprio paper:")
        self.play(FadeIn(c5))
        term2 = terminal_box([
            '"treinamos um ViT-Huge/14 no ImageNet usando 16 GPUs A100',
            ' em menos de 72 horas" — com bom desempenho em classificação',
            ' linear, contagem de objetos e previsão de profundidade',
        ], font_size=17).shift(DOWN * 0.1)
        assert_on_screen(term2, "ijepa result terminal")
        self.play(FadeIn(term2))
        self.wait(8.4)
        self.play(FadeOut(c5), FadeOut(term2))

        # --- Closing ---
        backdrop = RoundedRectangle(corner_radius=0.2, width=13, height=3.4, fill_color="#111111", fill_opacity=0.9, stroke_width=0)
        closing = Text(
            "Nem contrastive, nem reconstrução de pixels:\nprever representações de blocos mascarados — a tese de LeCun, tornada concreta.",
            font_size=25, color=WHITE, line_spacing=1.3,
        ).move_to(ORIGIN)
        if closing.width > 12.4:
            closing.scale_to_fit_width(12.4)
        self.play(FadeIn(backdrop))
        self.play(Write(closing))
        self.wait(8.4)
        self.play(FadeOut(backdrop), FadeOut(closing))
