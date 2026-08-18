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

class FlamingoScene(Scene):
    def construct(self):
        title = Text("Flamingo", font_size=42, color=WHITE)
        subtitle = Text("a Visual Language Model for Few-Shot Learning — Alayrac et al., DeepMind, 2022", font_size=18, color=GRAY_B)
        if subtitle.width > 12.8:
            subtitle.scale_to_fit_width(12.8)
        subtitle.next_to(title, DOWN, buff=0.35)
        self.play(Write(title))
        self.play(FadeIn(subtitle))
        self.wait(5.6)
        self.play(FadeOut(title), FadeOut(subtitle))

        # --- 1. The goal: connect two frozen giants ---
        c1 = callout("O objetivo: ligar um modelo de visão e um LLM já prontos, sem retreinar nenhum")
        self.play(FadeIn(c1))

        vision_box = sized_box("Encoder de Visão\n(congelado)", font_size=17, color=WHITE, box_color=ENCODER, box_opacity=0.35, min_width=3.4, min_height=1.3, line_spacing=1.2)
        vision_box.shift(LEFT * 3.2)
        lock1 = Text("🔒", font_size=20, color=WHITE)
        lock1_fallback = Text("[fixo]", font_size=14, color=OLD).next_to(vision_box, UP, buff=0.1)
        llm_box = sized_box("LLM (Chinchilla)\n(congelado)", font_size=17, color=WHITE, box_color=DECODER, box_opacity=0.35, min_width=3.4, min_height=1.3, line_spacing=1.2)
        llm_box.shift(RIGHT * 3.2)
        lock2_fallback = Text("[fixo]", font_size=14, color=OLD).next_to(llm_box, UP, buff=0.1)
        question = Text("?", font_size=40, color=MECHANISM).move_to(ORIGIN)

        frozen_group = VGroup(vision_box, lock1_fallback, llm_box, lock2_fallback, question)
        assert_on_screen(frozen_group, "flamingo frozen goal")
        self.play(FadeIn(vision_box), FadeIn(lock1_fallback))
        self.play(FadeIn(llm_box), FadeIn(lock2_fallback))
        self.play(Write(question))
        note1 = Text("meta: adaptação few-shot rápida — poucos exemplos anotados, sem fine-tuning", font_size=16, color=GRAY_B)
        note1.next_to(frozen_group, DOWN, buff=0.9)
        if note1.width > 12.6:
            note1.scale_to_fit_width(12.6)
        self.play(FadeIn(note1))
        self.wait(8)

        self.play(FadeOut(c1), FadeOut(frozen_group), FadeOut(note1))

        # --- 2. Perceiver Resampler ---
        c2 = callout("Peça 1: Perceiver Resampler — comprime features visuais variáveis em um número fixo", color=MECHANISM)
        self.play(FadeIn(c2))

        variable_feats = VGroup(*[
            Rectangle(width=0.4, height=0.7, color=ENCODER, fill_color=ENCODER, fill_opacity=0.25)
            for _ in range(7)
        ]).arrange(RIGHT, buff=0.1).shift(LEFT * 3.2 + UP * 0.5)
        variable_label = Text("features visuais\n(número variável)", font_size=14, color=GRAY_B, line_spacing=1.1).next_to(variable_feats, DOWN, buff=0.3)

        resampler = sized_box("Perceiver\nResampler", font_size=16, color=WHITE, box_color=MECHANISM, box_opacity=0.4, min_width=2.2, min_height=1.3, line_spacing=1.1)
        resampler.next_to(variable_feats, RIGHT, buff=1.0)

        fixed_feats = VGroup(*[
            Rectangle(width=0.4, height=0.7, color=MECHANISM, fill_color=MECHANISM, fill_opacity=0.4)
            for _ in range(3)
        ]).arrange(RIGHT, buff=0.1).next_to(resampler, RIGHT, buff=1.0)
        fixed_label = Text("tokens fixos", font_size=14, color=MECHANISM).next_to(fixed_feats, DOWN, buff=0.3)

        arrow1 = Arrow(variable_feats.get_right(), resampler.get_left(), buff=0.1, color=GRAY_B, stroke_width=2)
        arrow2 = Arrow(resampler.get_right(), fixed_feats.get_left(), buff=0.1, color=MECHANISM, stroke_width=2)

        resampler_group = VGroup(variable_feats, variable_label, resampler, fixed_feats, fixed_label, arrow1, arrow2)
        if resampler_group.width > 12.6:
            resampler_group.scale_to_fit_width(12.6)
        assert_on_screen(resampler_group, "flamingo resampler diagram")
        self.play(FadeIn(variable_feats), FadeIn(variable_label))
        self.play(FadeIn(resampler), GrowArrow(arrow1))
        self.play(FadeIn(fixed_feats), FadeIn(fixed_label), GrowArrow(arrow2))
        self.wait(8)

        self.play(FadeOut(c2), FadeOut(resampler_group))

        # --- 3. Gated cross-attention ---
        c3 = callout("Peça 2: cross-attention com portão, inserida entre os blocos congelados do LLM", color=MECHANISM)
        self.play(FadeIn(c3))

        blocks = VGroup()
        names = ["LLM block", "Gated Cross-Attn", "LLM block", "Gated Cross-Attn", "LLM block"]
        colors = [DECODER, MECHANISM, DECODER, MECHANISM, DECODER]
        for name, color in zip(names, colors):
            b = sized_box(name, font_size=14, color=WHITE, box_color=color, box_opacity=0.3 if color == DECODER else 0.45, min_width=3.0, min_height=0.55)
            blocks.add(b)
        stack = VGroup(*blocks).arrange(DOWN, buff=0.12)
        assert_on_screen(stack, "flamingo gated stack")
        self.play(FadeIn(stack))

        tanh_note = Text("portão = tanh(parâmetro), inicializado ~0 -> LLM começa idêntico ao original", font_size=15, color=MECHANISM)
        tanh_note.next_to(stack, DOWN, buff=0.5)
        if tanh_note.width > 12.6:
            tanh_note.scale_to_fit_width(12.6)
        self.play(FadeIn(tanh_note))
        self.wait(9)

        gated_group = VGroup(stack, tanh_note)
        self.play(FadeOut(c3), FadeOut(gated_group))

        # --- 3b. Few-shot in context: interleaved image+text prompt ---
        c3b = callout("Few-shot em contexto: exemplos e a pergunta viram um único prompt intercalado", color=MECHANISM)
        self.play(FadeIn(c3b))

        term_fewshot = terminal_box([
            "[imagem 1] essa é uma coruja",
            "[imagem 2] esse é um golfinho",
            "[imagem 3] esse é um _______  <- pergunta real",
            "",
            "-> nenhum peso muda entre os exemplos e a pergunta",
            "   o modelo já viu o padrão suficiente para completar",
        ], font_size=15).shift(DOWN * 0.1)
        assert_on_screen(term_fewshot, "flamingo interleaved fewshot terminal")
        self.play(FadeIn(term_fewshot))
        self.wait(9)

        self.play(FadeOut(c3b), FadeOut(term_fewshot))

        # --- 4. What this enables ---
        c4 = callout("O que isso viabiliza:")
        self.play(FadeIn(c4))
        term = terminal_box([
            "lida com sequências arbitrariamente intercaladas de imagem e texto",
            "ingere imagens OU vídeos como entrada",
            "treina em corpora web multimodais em larga escala",
            "-> aprendizado few-shot em contexto, sem fine-tuning",
        ], font_size=17).shift(DOWN * 0.1)
        assert_on_screen(term, "flamingo capabilities terminal")
        self.play(FadeIn(term))
        self.wait(9)
        self.play(FadeOut(c4), FadeOut(term))

        # --- Closing ---
        backdrop = RoundedRectangle(corner_radius=0.2, width=13, height=3.4, fill_color="#111111", fill_opacity=0.9, stroke_width=0)
        closing = Text(
            "Dois modelos congelados, uma ponte treinável entre eles:\nFlamingo mostra que não é preciso retreinar um LLM do zero para ele enxergar.",
            font_size=25, color=WHITE, line_spacing=1.3,
        ).move_to(ORIGIN)
        if closing.width > 12.4:
            closing.scale_to_fit_width(12.4)
        self.play(FadeIn(backdrop))
        self.play(Write(closing))
        self.wait(8.4)
        self.play(FadeOut(backdrop), FadeOut(closing))
