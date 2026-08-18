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

class QwenVLScene(Scene):
    def construct(self):
        title = Text("Qwen-VL", font_size=44, color=WHITE)
        subtitle = Text("A Versatile Vision-Language Model — Bai et al., Alibaba, 2023", font_size=19, color=GRAY_B)
        if subtitle.width > 12.8:
            subtitle.scale_to_fit_width(12.8)
        subtitle.next_to(title, DOWN, buff=0.35)
        self.play(Write(title))
        self.play(FadeIn(subtitle))
        self.wait(5.6)
        self.play(FadeOut(title), FadeOut(subtitle))

        # --- 1. The architecture: ViT + adapter + Qwen LLM ---
        c1 = callout("A base: ViT + um adaptador de atenção cruzada + um LLM Qwen")
        self.play(FadeIn(c1))

        vision = sized_box("ViT", font_size=18, color=WHITE, box_color=ENCODER, box_opacity=0.35, min_width=2.2, min_height=1.2)
        vision.shift(LEFT * 4.2)
        adapter = sized_box("adaptador\n(cross-attn,\n256 tokens)", font_size=14, color=WHITE, box_color=MECHANISM, box_opacity=0.45, min_width=2.4, min_height=1.5, line_spacing=1.1)
        llm = sized_box("Qwen LLM", font_size=18, color=WHITE, box_color=DECODER, box_opacity=0.35, min_width=2.4, min_height=1.2)
        llm.shift(RIGHT * 4.2)

        arrow1 = Arrow(vision.get_right(), adapter.get_left(), buff=0.1, color=ENCODER, stroke_width=3)
        arrow2 = Arrow(adapter.get_right(), llm.get_left(), buff=0.1, color=DECODER, stroke_width=3)

        base_group = VGroup(vision, adapter, llm, arrow1, arrow2)
        assert_on_screen(base_group, "qwenvl base architecture")
        self.play(FadeIn(vision))
        self.play(GrowArrow(arrow1), FadeIn(adapter))
        self.play(GrowArrow(arrow2), FadeIn(llm))
        note1 = Text("o adaptador comprime as features de imagem para um comprimento fixo antes do LLM", font_size=16, color=MECHANISM)
        note1.next_to(base_group, DOWN, buff=0.7)
        if note1.width > 12.6:
            note1.scale_to_fit_width(12.6)
        self.play(FadeIn(note1))
        self.wait(8)

        self.play(FadeOut(c1), FadeOut(base_group), FadeOut(note1))

        # --- 2. What sets it apart: grounding ---
        c2 = callout("A diferença: grounding visual fino — localizar objetos, não só descrevê-los", color=MECHANISM)
        self.play(FadeIn(c2))

        img_box = Rectangle(width=3.2, height=2.2, color=GRAY_D)
        obj_box = Rectangle(width=1.1, height=0.9, color=OUTPUT, stroke_width=3).move_to(img_box.get_center() + RIGHT * 0.6 + DOWN * 0.3)
        img_group = VGroup(img_box, obj_box).shift(LEFT * 3.2)
        coords = Text("(120, 80, 230, 190)", font_size=15, color=OUTPUT, font="Fira Code")
        coords.next_to(img_group, DOWN, buff=0.3)

        term = terminal_box([
            "entrada: 'onde está o gato na imagem?'",
            "saída:   '<gato> em (120, 80, 230, 190)'",
            "",
            "caixas delimitadoras codificadas como TEXTO —",
            "o mesmo LLM que descreve também localiza",
        ], font_size=15, width=7.0)
        term.next_to(img_group, RIGHT, buff=0.6)

        grounding_group = VGroup(img_group, coords, term)
        if grounding_group.width > 12.8:
            grounding_group.scale_to_fit_width(12.8)
        assert_on_screen(grounding_group, "qwenvl grounding diagram")
        self.play(FadeIn(img_group))
        self.play(FadeIn(coords))
        self.play(FadeIn(term))
        self.wait(9)

        self.play(FadeOut(c2), FadeOut(grounding_group))

        # --- 2b. Multi-image, multi-turn dialogue ---
        c2b = callout("Além de uma imagem só: múltiplas imagens, múltiplos turnos de diálogo", color=MECHANISM)
        self.play(FadeIn(c2b))

        term_multi = terminal_box([
            "turno 1: [imagem A] [imagem B] 'qual das duas é mais recente?'",
            "turno 2: 'e o que mudou entre as duas?'",
            "",
            "-> o modelo mantém contexto de imagens anteriores",
            "   entre turnos, não só dentro de uma única pergunta",
        ], font_size=15).shift(DOWN * 0.1)
        assert_on_screen(term_multi, "qwenvl multi-image dialogue terminal")
        self.play(FadeIn(term_multi))
        self.wait(8.4)

        self.play(FadeOut(c2b), FadeOut(term_multi))

        # --- 3. Multilingual, multi-stage training ---
        c3 = callout("Treino em 3 estágios, sobre um corpus multilíngue (chinês e inglês)")
        self.play(FadeIn(c3))

        term2 = terminal_box([
            "estágio 1: pré-treino em pares imagem-texto de baixa resolução",
            "estágio 2: pré-treino multitarefa (VQA, grounding, leitura de texto)",
            "estágio 3: ajuste fino por instrução (diálogo, chat multimodal)",
        ], font_size=16).shift(DOWN * 0.1)
        assert_on_screen(term2, "qwenvl training stages terminal")
        self.play(FadeIn(term2))
        self.wait(8.4)
        self.play(FadeOut(c3), FadeOut(term2))

        # --- 4. Result ---
        c4 = callout("O resultado citado no próprio paper:", color=MECHANISM)
        self.play(FadeIn(c4))
        term3 = terminal_box([
            '"estabelece novos recordes para modelos generalistas',
            ' em escalas de modelo similares" — em captioning, VQA',
            ' e grounding visual, zero-shot e few-shot',
        ], font_size=17).shift(DOWN * 0.1)
        assert_on_screen(term3, "qwenvl result terminal")
        self.play(FadeIn(term3))
        self.wait(9)
        self.play(FadeOut(c4), FadeOut(term3))

        # --- Closing: recap the whole VLM group ---
        backdrop = RoundedRectangle(corner_radius=0.2, width=13, height=3.6, fill_color="#111111", fill_opacity=0.9, stroke_width=0)
        closing = Text(
            "Contraste, patches, resampler com portão, projeção linear,\nQ-Former, adaptador com grounding: seis respostas diferentes\npara a mesma pergunta — como ligar visão e linguagem.",
            font_size=24, color=WHITE, line_spacing=1.3,
        ).move_to(ORIGIN)
        if closing.width > 12.4:
            closing.scale_to_fit_width(12.4)
        self.play(FadeIn(backdrop))
        self.play(Write(closing))
        self.wait(9)
        self.play(FadeOut(backdrop), FadeOut(closing))
