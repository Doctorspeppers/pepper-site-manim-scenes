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

class LLaVAScene(Scene):
    def construct(self):
        title = Text("Visual Instruction Tuning", font_size=34, color=WHITE)
        subtitle = Text("LLaVA — Liu et al., 2023", font_size=22, color=GRAY_B)
        subtitle.next_to(title, DOWN, buff=0.35)
        self.play(Write(title))
        self.play(FadeIn(subtitle))
        self.wait(2.8)
        self.play(FadeOut(title), FadeOut(subtitle))

        # --- 1. The simplicity bet ---
        c1 = callout("A aposta: qual é a ponte mínima entre um encoder de visão e um LLM?")
        self.play(FadeIn(c1))

        vision = sized_box("CLIP\n(congelado)", font_size=17, color=WHITE, box_color=ENCODER, box_opacity=0.35, min_width=2.8, min_height=1.2, line_spacing=1.1)
        vision.shift(LEFT * 4.2)
        proj = sized_box("Projeção\nLinear", font_size=16, color=WHITE, box_color=MECHANISM, box_opacity=0.5, min_width=2.0, min_height=1.0, line_spacing=1.1)
        llm = sized_box("LLM\n(Vicuna)", font_size=17, color=WHITE, box_color=DECODER, box_opacity=0.35, min_width=2.8, min_height=1.2, line_spacing=1.1)
        llm.shift(RIGHT * 4.2)

        row = VGroup(vision, proj, llm).arrange(RIGHT, buff=1.0)
        arrow1 = Arrow(vision.get_right(), proj.get_left(), buff=0.1, color=GRAY_B, stroke_width=3)
        arrow2 = Arrow(proj.get_right(), llm.get_left(), buff=0.1, color=GRAY_B, stroke_width=3)

        bridge_group = VGroup(row, arrow1, arrow2)
        assert_on_screen(bridge_group, "llava bridge diagram")
        self.play(FadeIn(vision))
        self.play(GrowArrow(arrow1), FadeIn(proj))
        self.play(GrowArrow(arrow2), FadeIn(llm))
        note1 = Text("uma única camada — sem resampler, sem atenção cruzada, sem módulo novo de verdade", font_size=16, color=MECHANISM)
        note1.next_to(bridge_group, DOWN, buff=0.7)
        if note1.width > 12.6:
            note1.scale_to_fit_width(12.6)
        self.play(FadeIn(note1))
        self.wait(4.2)

        self.play(FadeOut(c1), FadeOut(bridge_group), FadeOut(note1))

        # --- 2. The real innovation: GPT-4 generated data ---
        c2 = callout("A inovação real não é arquitetural — está nos dados de treino", color=MECHANISM)
        self.play(FadeIn(c2))

        term = terminal_box([
            "entrada: legendas + caixas delimitadoras de imagens existentes (só texto)",
            "",
            "GPT-4 (só texto, nunca vê a imagem) gera:",
            "  -> perguntas e respostas detalhadas sobre a cena",
            "  -> diálogos de instrução multimodal completos",
            "",
            "resultado: dados de instrução visual, sem anotação humana nova",
        ], font_size=16).shift(DOWN * 0.1)
        assert_on_screen(term, "llava data generation terminal")
        self.play(FadeIn(term))
        self.wait(4.8)

        self.play(FadeOut(c2), FadeOut(term))

        # --- 3. Training: two stages ---
        c3 = callout("Treino em duas etapas: alinhamento, depois instrução de ponta a ponta")
        self.play(FadeIn(c3))

        stage1 = sized_box("Etapa 1: alinhamento\n(só a projeção linear treina)", font_size=15, color=WHITE, box_color=MECHANISM, box_opacity=0.3, min_width=5.6, min_height=1.1, line_spacing=1.2)
        stage2 = sized_box("Etapa 2: instrução\n(projeção + LLM treinam juntos)", font_size=15, color=WHITE, box_color=DECODER, box_opacity=0.3, min_width=5.6, min_height=1.1, line_spacing=1.2)
        stages = stack_rows([stage1, stage2], buff=0.4)
        assert_on_screen(stages, "llava training stages")
        self.play(FadeIn(stage1))
        self.wait(1.5)
        self.play(FadeIn(stage2))
        self.wait(3.5)

        self.play(FadeOut(c3), FadeOut(stages))

        # --- 4. Result ---
        c4 = callout("O resultado citado no próprio paper:")
        self.play(FadeIn(c4))
        term2 = terminal_box([
            '"pontuação relativa de 85,1% comparado ao GPT-4"',
            ' em benchmark multimodal sintético',
            '',
            '"92,53% de acurácia" em Science QA,',
            ' combinado com GPT-4',
        ], font_size=17).shift(DOWN * 0.1)
        assert_on_screen(term2, "llava result terminal")
        self.play(FadeIn(term2))
        self.wait(4.5)
        self.play(FadeOut(c4), FadeOut(term2))

        # --- Closing ---
        backdrop = RoundedRectangle(corner_radius=0.2, width=13, height=3.4, fill_color="#111111", fill_opacity=0.9, stroke_width=0)
        closing = Text(
            "A ponte pode ser trivial — uma camada linear —\nse os dados de treino carregarem o peso da complexidade.",
            font_size=27, color=WHITE, line_spacing=1.3,
        ).move_to(ORIGIN)
        if closing.width > 12.4:
            closing.scale_to_fit_width(12.4)
        self.play(FadeIn(backdrop))
        self.play(Write(closing))
        self.wait(4.2)
        self.play(FadeOut(backdrop), FadeOut(closing))
