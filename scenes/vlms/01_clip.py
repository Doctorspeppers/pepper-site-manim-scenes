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


class CLIPScene(Scene):
    def construct(self):
        title = Text("Learning Transferable Visual Models", font_size=34, color=WHITE)
        if title.width > 12.8:
            title.scale_to_fit_width(12.8)
        subtitle = Text("CLIP — Radford et al., OpenAI, 2021", font_size=22, color=GRAY_B)
        subtitle.next_to(title, DOWN, buff=0.35)
        self.play(Write(title))
        self.play(FadeIn(subtitle))
        self.wait(5.6)
        self.play(FadeOut(title), FadeOut(subtitle))

        # --- 1. The old paradigm: fixed category classifiers ---
        c1 = callout("Antes: classificadores treinados para um conjunto fixo de categorias")
        self.play(FadeIn(c1))

        img_box = sized_box("imagem", font_size=18, color=WHITE, box_color=ENCODER, box_opacity=0.3, min_width=2.2, min_height=1.4)
        img_box.shift(LEFT * 3.5)
        arrow1 = Arrow(img_box.get_right(), img_box.get_right() + RIGHT * 1.5, color=GRAY_B, stroke_width=3)
        cats = VGroup(*[
            sized_box(c, font_size=14, color=OLD, box_color=OLD, box_opacity=0.15, min_width=1.5, min_height=0.5)
            for c in ["gato", "cachorro", "carro", "..."]
        ]).arrange(DOWN, buff=0.15).next_to(arrow1, RIGHT, buff=0.2)
        fixed_group = VGroup(img_box, arrow1, cats)
        assert_on_screen(fixed_group, "clip fixed categories")
        self.play(FadeIn(img_box))
        self.play(GrowArrow(arrow1), FadeIn(cats))
        note1 = Text("categoria nova? precisa coletar e rotular mais dados de treino", font_size=17, color=OLD)
        note1.next_to(fixed_group, DOWN, buff=0.6)
        self.play(FadeIn(note1))
        self.wait(7)

        self.play(FadeOut(c1), FadeOut(fixed_group), FadeOut(note1))

        # --- 1b. Scale comparison: what "broader supervision" means concretely ---
        c1b = callout("A escala que isso viabiliza: milhões de pares (imagem, texto) da internet, sem curadoria")
        self.play(FadeIn(c1b))

        old_scale = sized_box("ImageNet\n1,28 milhão de imagens\n1000 categorias fixas", font_size=15, color=WHITE, box_color=OLD, box_opacity=0.2, min_width=4.4, min_height=1.6, line_spacing=1.25)
        new_scale = sized_box("CLIP\n400 milhões de pares\nnenhuma categoria fixa", font_size=15, color=WHITE, box_color=MECHANISM, box_opacity=0.35, min_width=4.4, min_height=1.6, line_spacing=1.25)
        scale_row = VGroup(old_scale, new_scale).arrange(RIGHT, buff=1.0)
        assert_on_screen(scale_row, "clip scale comparison")
        self.play(FadeIn(old_scale))
        self.play(FadeIn(new_scale))
        note1b = Text("a supervisão vem da própria legenda da web — não de um rótulo escolhido a dedo", font_size=16, color=GRAY_B)
        note1b.next_to(scale_row, DOWN, buff=0.7)
        if note1b.width > 12.6:
            note1b.scale_to_fit_width(12.6)
        self.play(FadeIn(note1b))
        self.wait(8.4)

        self.play(FadeOut(c1b), FadeOut(scale_row), FadeOut(note1b))

        # --- 2. The idea: joint embedding space via contrastive pretraining ---
        c2 = callout("A ideia: imagem e texto no mesmo espaço de embeddings, aprendido por contraste", color=MECHANISM)
        self.play(FadeIn(c2))

        img_enc = sized_box("Image\nEncoder", font_size=17, color=WHITE, box_color=ENCODER, box_opacity=0.35, min_width=2.4, min_height=1.1, line_spacing=1.1)
        img_enc.shift(LEFT * 3.2 + UP * 1.0)
        txt_enc = sized_box("Text\nEncoder", font_size=17, color=WHITE, box_color=DECODER, box_opacity=0.35, min_width=2.4, min_height=1.1, line_spacing=1.1)
        txt_enc.shift(LEFT * 3.2 + DOWN * 1.0)

        space = Ellipse(width=5.5, height=3.4, color=MECHANISM, stroke_width=1.5).shift(RIGHT * 2.2)
        space_label = Text("espaço de embeddings\ncompartilhado", font_size=15, color=MECHANISM, line_spacing=1.1)
        space_label.next_to(space, UP, buff=0.15)

        img_arrow = Arrow(img_enc.get_right(), space.get_left() + UP * 0.6, buff=0.1, color=ENCODER, stroke_width=3)
        txt_arrow = Arrow(txt_enc.get_right(), space.get_left() + DOWN * 0.6, buff=0.1, color=DECODER, stroke_width=3)

        joint_group = VGroup(img_enc, txt_enc, space, space_label, img_arrow, txt_arrow)
        assert_on_screen(joint_group, "clip joint embedding diagram")
        self.play(FadeIn(img_enc), FadeIn(txt_enc))
        self.play(Create(space), FadeIn(space_label))
        self.play(GrowArrow(img_arrow), GrowArrow(txt_arrow))
        self.wait(7)

        self.play(FadeOut(c2), FadeOut(joint_group))

        # --- 3. Worked example: the contrastive similarity matrix ---
        c3 = callout("Perda contrastiva: aproxima o par certo, afasta todos os errados no mesmo lote")
        self.play(FadeIn(c3))

        images = ["[gato]", "[cachorro]", "[carro]"]
        texts = ["'um gato'", "'um cachorro'", "'um carro'"]
        img_dots = VGroup(*[Text(t, font_size=16, color=WHITE) for t in images]).arrange(DOWN, buff=1.0).shift(LEFT * 4.2)
        txt_dots = VGroup(*[Text(t, font_size=16, color=WHITE) for t in texts]).arrange(DOWN, buff=1.0).shift(RIGHT * 4.2)

        lines = VGroup()
        for i in range(3):
            for j in range(3):
                color = MECHANISM if i == j else OLD
                opacity = 0.9 if i == j else 0.2
                width = 3 if i == j else 1
                line = Line(img_dots[i].get_right(), txt_dots[j].get_left(), color=color, stroke_width=width, stroke_opacity=opacity)
                lines.add(line)
        matrix_group = VGroup(img_dots, txt_dots, lines)
        assert_on_screen(matrix_group, "clip similarity matrix")
        self.play(FadeIn(img_dots), FadeIn(txt_dots))
        self.play(LaggedStart(*[Create(l) for l in lines], lag_ratio=0.08, run_time=2))
        note2 = Text("cosseno(imagem, texto) / temperatura -> softmax -> peso 1 na diagonal, ~0 fora dela", font_size=16, color=MECHANISM)
        note2.next_to(matrix_group, DOWN, buff=0.7)
        if note2.width > 12.6:
            note2.scale_to_fit_width(12.6)
        self.play(FadeIn(note2))
        self.wait(8.4)

        self.play(FadeOut(c3), FadeOut(matrix_group), FadeOut(note2))

        # --- 4. Zero-shot classification via prompt templates ---
        c4 = callout("Zero-shot: nenhum peso muda — a nova categoria vira só um prompt de texto", color=MECHANISM)
        self.play(FadeIn(c4))

        term = terminal_box([
            "templates: \"uma foto de um {categoria}\"",
            "",
            "categorias: gato | cachorro | carro | avião | ...",
            "-> compara a imagem contra cada prompt gerado",
            "-> categoria com maior similaridade de cosseno vence",
        ], font_size=17).shift(DOWN * 0.1)
        assert_on_screen(term, "clip zero-shot terminal")
        self.play(FadeIn(term))
        self.wait(9)

        self.play(FadeOut(c4), FadeOut(term))

        # --- 5. Result ---
        c5 = callout("O resultado citado no próprio paper:")
        self.play(FadeIn(c5))
        term2 = terminal_box([
            '"igualamos a acurácia do ResNet-50 original no ImageNet',
            ' zero-shot, sem usar nenhum dos 1,28 milhão de exemplos',
            ' de treino" — testado em mais de 30 datasets diferentes',
        ], font_size=17).shift(DOWN * 0.1)
        assert_on_screen(term2, "clip result terminal")
        self.play(FadeIn(term2))
        self.wait(9)
        self.play(FadeOut(c5), FadeOut(term2))

        # --- Closing ---
        backdrop = RoundedRectangle(corner_radius=0.2, width=13, height=3.4, fill_color="#111111", fill_opacity=0.9, stroke_width=0)
        closing = Text(
            "Um espaço de embeddings compartilhado, aprendido por contraste:\na base que quase todo modelo de visão-linguagem desta lista usa como ponto de partida.",
            font_size=26, color=WHITE, line_spacing=1.3,
        ).move_to(ORIGIN)
        if closing.width > 12.4:
            closing.scale_to_fit_width(12.4)
        self.play(FadeIn(backdrop))
        self.play(Write(closing))
        self.wait(8.4)
        self.play(FadeOut(backdrop), FadeOut(closing))
