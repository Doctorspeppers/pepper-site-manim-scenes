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

class ViTScene(Scene):
    def construct(self):
        title = Text("An Image is Worth 16x16 Words", font_size=32, color=WHITE)
        if title.width > 12.8:
            title.scale_to_fit_width(12.8)
        subtitle = Text("ViT — Dosovitskiy et al., Google Research, 2020", font_size=22, color=GRAY_B)
        subtitle.next_to(title, DOWN, buff=0.35)
        self.play(Write(title))
        self.play(FadeIn(subtitle))
        self.wait(5.6)
        self.play(FadeOut(title), FadeOut(subtitle))

        # --- 1. The premise: CNNs still dominant ---
        c1 = callout("Até então: convolução era indispensável, atenção só complementava")
        self.play(FadeIn(c1))

        cnn_box = sized_box("CNN\n(convolução)", font_size=18, color=WHITE, box_color=OLD, box_opacity=0.25, min_width=3.4, min_height=1.6, line_spacing=1.2)
        cnn_box.shift(LEFT * 3.0)
        plus = Text("+", font_size=32, color=WHITE)
        attn_box = sized_box("atenção\n(complemento)", font_size=16, color=WHITE, box_color=MECHANISM, box_opacity=0.2, min_width=2.6, min_height=1.2, line_spacing=1.2)
        combo = VGroup(cnn_box, plus, attn_box).arrange(RIGHT, buff=0.5)
        assert_on_screen(combo, "vit old paradigm")
        self.play(FadeIn(combo))
        note1 = Text("um Transformer puro, sem nenhuma convolução, funcionaria em imagens?", font_size=17, color=MECHANISM)
        note1.next_to(combo, DOWN, buff=0.7)
        self.play(FadeIn(note1))
        self.wait(7)

        self.play(FadeOut(c1), FadeOut(combo), FadeOut(note1))

        # --- 2. Patchify: image as a sequence ---
        c2 = callout("A ideia central: cortar a imagem em patches e tratá-los como tokens", color=MECHANISM)
        self.play(FadeIn(c2))

        grid = VGroup(*[
            Square(side_length=0.7, color=ENCODER, fill_color=ENCODER, fill_opacity=0.15 + 0.05 * (i % 3))
            for i in range(9)
        ]).arrange_in_grid(rows=3, cols=3, buff=0.05)
        grid.shift(LEFT * 3.5)
        grid_label = Text("imagem\n(patches 16x16)", font_size=16, color=GRAY_B, line_spacing=1.1).next_to(grid, DOWN, buff=0.3)

        arrow = Arrow(grid.get_right(), grid.get_right() + RIGHT * 1.3, color=WHITE, stroke_width=3)

        tokens = VGroup(*[
            Rectangle(width=0.5, height=0.9, color=ENCODER, fill_color=ENCODER, fill_opacity=0.3)
            for _ in range(9)
        ]).arrange(RIGHT, buff=0.1).next_to(arrow, RIGHT, buff=0.2)
        tokens_label = Text("sequência de patches achatados", font_size=16, color=GRAY_B).next_to(tokens, DOWN, buff=0.3)

        patch_group = VGroup(grid, grid_label, arrow, tokens, tokens_label)
        if patch_group.width > 12.6:
            patch_group.scale_to_fit_width(12.6)
        assert_on_screen(patch_group, "vit patchify diagram")
        self.play(FadeIn(grid), FadeIn(grid_label))
        self.play(GrowArrow(arrow))
        self.play(FadeIn(tokens), FadeIn(tokens_label))
        self.wait(8.4)

        self.play(FadeOut(c2), FadeOut(patch_group))

        # --- 2b. Why patch size trades off resolution vs. sequence length ---
        c2b = callout("O tamanho do patch é um trade-off direto: menor patch, sequência mais longa", color=MECHANISM)
        self.play(FadeIn(c2b))

        term_patch = terminal_box([
            "imagem 224x224, patch 16x16 -> 14x14 = 196 patches",
            "imagem 224x224, patch 32x32 -> 7x7  = 49 patches",
            "",
            "menos patches: mais rápido, perde detalhe fino",
            "mais patches: mais caro (atenção escala ao quadrado), mais detalhe",
        ], font_size=16).shift(DOWN * 0.1)
        assert_on_screen(term_patch, "vit patch size tradeoff terminal")
        self.play(FadeIn(term_patch))
        self.wait(8.4)

        self.play(FadeOut(c2b), FadeOut(term_patch))

        # --- 3. CLS token + positional embeddings ---
        c3 = callout("Um token [CLS] extra (herdado do BERT) e posições aprendidas, iguais a um token")
        self.play(FadeIn(c3))

        cls_box = Rectangle(width=0.6, height=0.9, color=OUTPUT, fill_color=OUTPUT, fill_opacity=0.4)
        patch_boxes = VGroup(*[
            Rectangle(width=0.6, height=0.9, color=ENCODER, fill_color=ENCODER, fill_opacity=0.3)
            for _ in range(5)
        ])
        seq = VGroup(cls_box, *patch_boxes).arrange(RIGHT, buff=0.15)
        cls_label = Text("[CLS]", font_size=16, color=WHITE).move_to(cls_box)
        patch_labels = VGroup(*[Text(f"p{i+1}", font_size=16, color=WHITE).move_to(b) for i, b in enumerate(patch_boxes)])

        pos_row = VGroup(*[
            Text(f"+pos{i}", font_size=16, color=POSITION).next_to(b, DOWN, buff=0.2)
            for i, b in enumerate(seq)
        ])

        cls_seq_group = VGroup(seq, cls_label, patch_labels, pos_row)
        assert_on_screen(cls_seq_group, "vit cls+pos sequence")
        self.play(FadeIn(seq), FadeIn(cls_label), FadeIn(patch_labels))
        self.play(FadeIn(pos_row))
        note2 = Text("saída final do [CLS] -> usada para classificação (mesma lógica do BERT)", font_size=16, color=OUTPUT)
        note2.next_to(cls_seq_group, DOWN, buff=0.7)
        self.play(FadeIn(note2))
        self.wait(8.4)

        self.play(FadeOut(c3), FadeOut(cls_seq_group), FadeOut(note2))

        # --- 4. Result ---
        c4 = callout("O resultado citado no próprio paper:")
        self.play(FadeIn(c4))
        term = terminal_box([
            '"um Transformer puro aplicado diretamente a sequências de',
            ' patches de imagem pode ter um desempenho muito bom" —',
            ' igualando CNNs de ponta com menos recursos computacionais',
            ' de treino (ImageNet, CIFAR-100, VTAB, entre outros)',
        ], font_size=17).shift(DOWN * 0.1)
        assert_on_screen(term, "vit result terminal")
        self.play(FadeIn(term))
        self.wait(9)
        self.play(FadeOut(c4), FadeOut(term))

        # --- Closing ---
        backdrop = RoundedRectangle(corner_radius=0.2, width=13, height=3.4, fill_color="#111111", fill_opacity=0.9, stroke_width=0)
        closing = Text(
            "Nenhuma convolução: só patches, posição e atenção.\nO ViT vira o encoder de imagem padrão para quase todo modelo que segue.",
            font_size=26, color=WHITE, line_spacing=1.3,
        ).move_to(ORIGIN)
        if closing.width > 12.4:
            closing.scale_to_fit_width(12.4)
        self.play(FadeIn(backdrop))
        self.play(Write(closing))
        self.wait(8.4)
        self.play(FadeOut(backdrop), FadeOut(closing))
