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

class VJEPAScene(Scene):
    def construct(self):
        title = Text("V-JEPA", font_size=44, color=WHITE)
        subtitle = Text("Revisiting Feature Prediction for Video — Bardes et al., FAIR at Meta, 2024", font_size=18, color=GRAY_B)
        if subtitle.width > 12.8:
            subtitle.scale_to_fit_width(12.8)
        subtitle.next_to(title, DOWN, buff=0.35)
        self.play(Write(title))
        self.play(FadeIn(subtitle))
        self.wait(5.6)
        self.play(FadeOut(title), FadeOut(subtitle))

        # --- 1. From 2D blocks to spatio-temporal tubes ---
        c1 = callout("A diferença central: mascarar tubos espaço-temporais, não blocos 2D", color=MECHANISM)
        self.play(FadeIn(c1))

        frames = VGroup(*[
            Square(side_length=0.9, color=ENCODER, fill_color=ENCODER, fill_opacity=0.15).shift(RIGHT * i * 1.1)
            for i in range(5)
        ])
        tube = Rectangle(width=0.5, height=0.5, color=MECHANISM, fill_color=MECHANISM, fill_opacity=0.6)
        tubes = VGroup(*[tube.copy().move_to(f.get_center()) for f in frames])
        stack = VGroup(frames, tubes).shift(LEFT * 2.5)
        frame_label = Text("frames consecutivos de vídeo", font_size=15, color=GRAY_B).next_to(stack, DOWN, buff=0.3)

        tube_group = VGroup(stack, frame_label)
        assert_on_screen(tube_group, "vjepa spatiotemporal tube diagram")
        self.play(FadeIn(frames))
        self.play(FadeIn(tubes), FadeIn(frame_label))
        note1 = Text("o mesmo patch, mascarado ao longo de vários frames -> o \"tubo\" a ser previsto", font_size=16, color=MECHANISM)
        note1.next_to(tube_group, DOWN, buff=0.6)
        if note1.width > 12.6:
            note1.scale_to_fit_width(12.6)
        self.play(FadeIn(note1))
        self.wait(8.4)

        self.play(FadeOut(c1), FadeOut(tube_group), FadeOut(note1))

        # --- 2. No supervision of any kind ---
        c2 = callout("Sem nenhuma fonte de supervisão externa")
        self.play(FadeIn(c2))
        term = terminal_box([
            "sem encoders de imagem pré-treinados",
            "sem texto",
            "sem exemplos negativos",
            "sem reconstrução de pixels",
            "-> só o objetivo de predição de features, sobre 2 milhões de vídeos",
        ], font_size=16).shift(DOWN * 0.1)
        assert_on_screen(term, "vjepa no supervision terminal")
        self.play(FadeIn(term))
        self.wait(8.4)
        self.play(FadeOut(c2), FadeOut(term))

        # --- 3. Frozen backbone, versatile representation ---
        c3 = callout("Um backbone congelado já basta — para movimento E para aparência", color=MECHANISM)
        self.play(FadeIn(c3))

        motion_box = sized_box("Kinetics-400\n(reconhecimento de ação)", font_size=15, color=WHITE, box_color=MECHANISM, box_opacity=0.35, min_width=4.2, min_height=1.2, line_spacing=1.15)
        motion_box.shift(LEFT * 3.4)
        appearance_box = sized_box("ImageNet1K\n(classificação de imagem)", font_size=15, color=WHITE, box_color=ENCODER, box_opacity=0.35, min_width=4.2, min_height=1.2, line_spacing=1.15)
        appearance_box.shift(RIGHT * 3.4)
        tasks_row = VGroup(motion_box, appearance_box)
        assert_on_screen(tasks_row, "vjepa frozen backbone tasks")
        self.play(FadeIn(motion_box))
        self.play(FadeIn(appearance_box))
        note2 = Text("mesma representação, backbone congelado, sem ajuste de peso por tarefa", font_size=16, color=GRAY_B)
        note2.next_to(tasks_row, DOWN, buff=0.7)
        self.play(FadeIn(note2))
        self.wait(8)
        self.play(FadeOut(c3), FadeOut(tasks_row), FadeOut(note2))

        # --- 3.5. Attentive probing: the evaluation protocol itself matters ---
        c3b = callout('Avaliação por "attentive probing": um probe leve de atenção, não um único linear', color=MECHANISM)
        self.play(FadeIn(c3b))
        term_probe = terminal_box([
            "backbone V-JEPA congelado -> features fixas",
            "  + um probe de cross-attention pequeno e treinável em cima",
            "  (mais expressivo que um único linear layer, mas o",
            "   backbone continua 100% congelado)",
            'resultado: "+6% de acurácia" no Something-Something-v2',
            "  sobre os outros métodos comparados nesse protocolo",
        ], font_size=14).shift(DOWN * 0.1)
        assert_on_screen(term_probe, "vjepa attentive probing terminal")
        self.play(FadeIn(term_probe))
        self.wait(8.4)
        self.play(FadeOut(c3b), FadeOut(term_probe))

        # --- 4. Result ---
        c4 = callout("O resultado citado no próprio paper:")
        self.play(FadeIn(c4))
        term2 = terminal_box([
            '"81,9% no Kinetics-400"',
            '"72,2% no Something-Something-v2"',
            '"77,9% no ImageNet1K"',
            '— o mesmo ViT-H/16, backbone congelado, sem rótulos no treino',
        ], font_size=17).shift(DOWN * 0.1)
        assert_on_screen(term2, "vjepa result terminal")
        self.play(FadeIn(term2))
        self.wait(8.4)
        self.play(FadeOut(c4), FadeOut(term2))

        # --- Closing ---
        backdrop = RoundedRectangle(corner_radius=0.2, width=13, height=3.4, fill_color="#111111", fill_opacity=0.9, stroke_width=0)
        closing = Text(
            "A mesma ideia do I-JEPA, só trocando o espaço a mascarar:\nde blocos de uma imagem para tubos ao longo do tempo.",
            font_size=27, color=WHITE, line_spacing=1.3,
        ).move_to(ORIGIN)
        if closing.width > 12.4:
            closing.scale_to_fit_width(12.4)
        self.play(FadeIn(backdrop))
        self.play(Write(closing))
        self.wait(8.4)
        self.play(FadeOut(backdrop), FadeOut(closing))
