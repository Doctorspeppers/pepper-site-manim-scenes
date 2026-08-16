from manim import *

# Explicit body font (never rely on Pango's empty-string default — it is
# inconsistent across environments). The user compared Noto Sans / P052 /
# Nimbus Roman / URW Gothic rendered side by side and initially picked P052,
# but it still showed the low-resolution spacing artifact once rendered in
# a real scene — URW Gothic (a geometric sans, heavier/simpler strokes than
# Noto Sans) held up better and is the current standard body font. Fira Code
# stays reserved for terminal_box() via _mono_font(), which passes font=
# explicitly and so overrides this default correctly for that one case.
Text.set_default(font="URW Gothic")

# Shared color language for the whole 9-video LLM series:
#   BLUE   = encoder / bidirectional path
#   ORANGE = decoder / autoregressive path
#   YELLOW = the paper's core novel mechanism (attention, selective state, etc.)
#   GREEN  = feed-forward / MLP / expert layers
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
        # A blank separator line is a Rectangle spacer, never Text("") —
        # an empty Text mobject has no points, which corrupts arrange()'s
        # spacing for every row after it.
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
    """A (box, label) pair sized to fit `text_str` at a fixed, legible
    font_size with real margin on every side — the box grows to fit the
    text, the text itself is never scaled down to fit a pre-picked box size
    (that geometric shrink is what reintroduces the illegible, uneven-spacing
    artifact that a >=16pt font_size is supposed to prevent). Accepts both
    `color`/`text_color` for the label, both `box_color`/`fill_color` for the
    box fill, and both `fill_opacity`/`box_opacity` for its opacity —
    different call sites across this series settled on different names for
    the same thing; all are honored so any of them work."""
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
    """Visible bounding frame every data-driven/multi-part diagram is built
    inside — Manim's default frame is only 8 units tall and ~14.2 wide, so
    anything not explicitly bounded like this can silently render off-screen."""
    return RoundedRectangle(corner_radius=0.15, width=width, height=height, color=GRAY_D, stroke_width=1.5).shift(UP * y_shift)


def assert_on_screen(mobj, label=""):
    """Fail the render loudly (exact coordinates, in the render script's
    stderr) instead of silently producing a video with something clipped
    off-frame. Generic, permanent check — call on every top-level group
    right before it's faded in, instead of trusting hand-computed coordinates."""
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
    """Fail loudly if two groups' bounding boxes intersect — catches the
    'diagram/caption drawn on top of another element' class of bug
    generically, instead of relying on eyeballing coordinates."""
    a_l, a_r, a_t, a_b = a.get_left()[0], a.get_right()[0], a.get_top()[1], a.get_bottom()[1]
    b_l, b_r, b_t, b_b = b.get_left()[0], b.get_right()[0], b.get_top()[1], b.get_bottom()[1]
    overlap_x = a_l < b_r and b_l < a_r
    overlap_y = a_b < b_t and b_b < a_t
    assert not (overlap_x and overlap_y), (
        f"{label}: groups overlap on screen — a=[{a_l:.2f},{a_r:.2f}]x[{a_b:.2f},{a_t:.2f}] "
        f"b=[{b_l:.2f},{b_r:.2f}]x[{b_b:.2f},{b_t:.2f}]"
    )


def diagram_row(diagram, label_text, sub_text, label_color=WHITE, sub_color=GRAY_B,
                label_font_size=18, sub_font_size=16, max_width=12.4, gap=0.6):
    """A generic 'small diagram + two-line caption' row: label stacked above
    sub with a real buff (never overlapping by construction), placed beside
    the diagram. If the combined row is too wide, only the diagram (never
    the caption text) is shrunk to fit. Returns the assembled row group —
    use `stack_rows()` to lay several of these out vertically without
    guessing buff sizes by hand."""
    label = Text(label_text, font_size=label_font_size, color=label_color)
    sub = Text(sub_text, font_size=sub_font_size, color=sub_color, line_spacing=1.1)
    caption = VGroup(label, sub).arrange(DOWN, buff=0.12, aligned_edge=LEFT)
    row = VGroup(diagram, caption).arrange(RIGHT, buff=gap)
    if row.width > max_width:
        diagram.scale_to_fit_width(diagram.width * max_width / row.width)
        row = VGroup(diagram, caption).arrange(RIGHT, buff=gap)
    return row


def uniform_boxes(texts, font_size=16, box_color=WHITE, box_opacity=0.3, margin=0.3, line_spacing=1.0, buff=0.3):
    """A row of boxes all sharing ONE size — computed from the longest text
    among them at font_size, with real margin — so a grid of short labels
    (token pieces, step numbers, expert IDs) reads as visually uniform
    without any individual box needing to shrink its own text to fit."""
    labels = [Text(t, font_size=font_size, color=WHITE, line_spacing=line_spacing) for t in texts]
    width = max(label.width for label in labels) + margin * 2
    height = max(label.height for label in labels) + margin * 2
    boxes = []
    for label in labels:
        box = RoundedRectangle(corner_radius=0.08, width=width, height=height, color=box_color,
                                fill_color=box_color, fill_opacity=box_opacity)
        label.move_to(box.get_center())
        boxes.append(VGroup(box, label))
    return VGroup(*boxes).arrange(RIGHT, buff=buff)


def sized_circle(text_str, font_size=16, color=WHITE, circle_color=WHITE, fill_opacity=0.3, margin=0.35, line_spacing=1.0):
    """Circle equivalent of sized_box() — sized to fit `text_str` with real
    margin, text never scaled down to fit a pre-picked radius."""
    label = Text(text_str, font_size=font_size, color=color, line_spacing=line_spacing)
    radius = max(label.width, label.height) / 2 + margin
    circle = Circle(radius=radius, color=circle_color, fill_color=circle_color, fill_opacity=fill_opacity)
    label.move_to(circle.get_center())
    return VGroup(circle, label)


def stack_rows(rows, buff=0.5, aligned_edge=LEFT):
    """Stack pre-built rows vertically with a generous, explicit buff, then
    verify (via `assert_no_overlap`) that no two adjacent rows actually
    collide — the check is baked into the act of stacking, so any scene using
    this helper gets the safety net for free instead of relying on hand-
    computed spacing being right on the first try."""
    group = VGroup(*rows).arrange(DOWN, buff=buff, aligned_edge=aligned_edge)
    for i in range(len(rows) - 1):
        assert_no_overlap(rows[i], rows[i + 1], f"stack_rows: row {i} vs row {i+1}")
    return group


class DeepSeekScene(Scene):
    def construct(self):
        title = Text("DeepSeek-V3 / DeepSeek-R1", font_size=38, color=WHITE)
        subtitle = Text("DeepSeek-AI, 2024 / 2025", font_size=24, color=GRAY_B)
        subtitle.next_to(title, DOWN, buff=0.35)
        self.play(Write(title))
        self.play(FadeIn(subtitle))
        self.wait(3)
        self.play(FadeOut(title), FadeOut(subtitle))

        # --- 1. Scale: 671B total, 37B active ---
        c1 = callout("671B parâmetros totais — só 37B ativados por token")
        self.play(FadeIn(c1))

        total_badge = sized_circle("671B\ntotal", font_size=22, color=OLD, circle_color=OLD, fill_opacity=0.15, margin=0.45)
        total_badge.shift(LEFT * 2.6)
        total_circle, total_label = total_badge
        active_badge = sized_circle("37B\nativo", font_size=18, color=WHITE, circle_color=MECHANISM, fill_opacity=0.5, margin=0.4)
        active_badge.shift(RIGHT * 2.6)
        active_circle, active_label = active_badge
        arrow = Arrow(total_circle.get_right() + RIGHT * 0.1, active_circle.get_left() + LEFT * 0.1, color=WHITE)
        arrow_label = Text("por token", font_size=16, color=GRAY_B).next_to(arrow, UP, buff=0.1)

        self.play(FadeIn(total_circle), FadeIn(total_label))
        self.play(GrowArrow(arrow), FadeIn(arrow_label))
        self.play(FadeIn(active_circle), FadeIn(active_label))
        pct_note = Text("cada token ativa só ~5,5% dos parâmetros totais do modelo", font_size=17, color=GRAY_B)
        pct_note.next_to(VGroup(total_circle, active_circle), DOWN, buff=0.9)
        if pct_note.width > 12.6:
            pct_note.scale_to_fit_width(12.6)
        self.play(FadeIn(pct_note))
        self.wait(4.5)

        scale_group = VGroup(total_circle, total_label, active_circle, active_label, arrow, arrow_label, pct_note)
        self.play(FadeOut(c1), FadeOut(scale_group))

        # --- 2. O problema do MoE tradicional: perda auxiliar competindo ---
        c2 = callout("Antes: balancear especialistas custava uma perda auxiliar competindo com o treino principal")
        self.play(FadeIn(c2))

        container2 = RoundedRectangle(corner_radius=0.15, width=12.8, height=5.2, color=GRAY_D, stroke_width=1.5).shift(DOWN * 0.3)
        self.play(Create(container2))

        main_loss_box = sized_box("perda principal\n(prever o próximo token)", font_size=16, box_color=ENCODER, fill_opacity=0.3, min_width=3.4, min_height=1.1)
        main_loss_box.shift(LEFT * 3.6 + UP * 0.9)
        main_loss, main_loss_label = main_loss_box
        aux_loss_box = sized_box("perda auxiliar\n(balancear especialistas)", font_size=16, box_color=OLD, fill_opacity=0.3, min_width=3.4, min_height=1.1)
        aux_loss_box.shift(RIGHT * 3.6 + UP * 0.9)
        aux_loss, aux_loss_label = aux_loss_box
        vs_arrows = VGroup(
            Arrow(main_loss.get_bottom(), main_loss.get_bottom() + DOWN * 0.7 + RIGHT * 0.5, color=OLD, stroke_width=3),
            Arrow(aux_loss.get_bottom(), aux_loss.get_bottom() + DOWN * 0.7 + LEFT * 0.5, color=OLD, stroke_width=3),
        )
        clash_label = Text("as duas competem pelo mesmo gradiente — uma pode prejudicar a outra", font_size=16, color=OLD)
        clash_label.next_to(vs_arrows, DOWN, buff=0.4)
        if clash_label.width > 12.4:
            clash_label.scale_to_fit_width(12.4)

        self.play(FadeIn(main_loss), FadeIn(main_loss_label))
        self.play(FadeIn(aux_loss), FadeIn(aux_loss_label))
        self.play(LaggedStart(*[GrowArrow(a) for a in vs_arrows], lag_ratio=0.3))
        self.play(FadeIn(clash_label))
        self.wait(5)

        old_moe_group = VGroup(container2, main_loss, main_loss_label, aux_loss, aux_loss_label, vs_arrows, clash_label)
        self.play(FadeOut(c2), FadeOut(old_moe_group))

        # --- 3. DeepSeekMoE: bias-based balancing, sem perda extra ---
        c3 = callout("DeepSeekMoE: um viés por especialista, ajustado pelo uso recente — sem segunda perda", color=MECHANISM)
        self.play(FadeIn(c3))

        experts = VGroup(*[
            RoundedRectangle(corner_radius=0.08, width=1.3, height=0.8, color=FFN).set_fill(FFN, opacity=0.35)
            for _ in range(6)
        ]).arrange(RIGHT, buff=0.3).shift(UP * 0.7)
        expert_labels = VGroup(*[Text(f"E{i+1}", font_size=16, color=WHITE).move_to(b) for i, b in enumerate(experts)])
        shared_group = sized_box("Compartilhado", font_size=16, box_color=ENCODER, fill_opacity=0.35, min_height=0.8)
        shared_group.next_to(experts, DOWN, buff=0.5)
        shared_expert, shared_label = shared_group

        self.play(FadeIn(experts), FadeIn(expert_labels))
        self.play(FadeIn(shared_group))
        bias_note = Text("especialista sobrecarregado -> viés cai; especialista ocioso -> viés sobe", font_size=16, color=MECHANISM)
        bias_note.next_to(shared_group, DOWN, buff=0.55)
        if bias_note.width > 12.6:
            bias_note.scale_to_fit_width(12.6)
        self.play(FadeIn(bias_note))
        clean_note = Text("balanceamento vem do roteamento — não de uma perda extra competindo com o treino", font_size=16, color=GRAY_B)
        clean_note.next_to(bias_note, DOWN, buff=0.3)
        if clean_note.width > 12.6:
            clean_note.scale_to_fit_width(12.6)
        self.play(FadeIn(clean_note))
        self.wait(5)

        moe_group = VGroup(experts, expert_labels, shared_group, bias_note, clean_note)
        self.play(FadeOut(c3), FadeOut(moe_group))

        # --- 4. MLA: por que comprimir K/V ingenuamente não funciona ---
        c4 = callout("Multi-head Latent Attention: por que simplesmente comprimir K/V não funciona")
        self.play(FadeIn(c4))

        naive_group = sized_box("compressão ingênua:\ncache menor, mas perde qualidade", font_size=16, box_color=OLD, fill_opacity=0.25, min_width=4.4, min_height=1.3)
        naive_group.shift(UP * 0.8)
        naive_box, naive_label = naive_group
        x_mark = Text("X", font_size=32, color=RED).next_to(naive_box, RIGHT, buff=0.4)

        self.play(FadeIn(naive_box), FadeIn(naive_label))
        self.play(Write(x_mark))
        naive_note = Text("descartar informação do K/V direto degrada a qualidade da atenção", font_size=16, color=OLD)
        naive_note.next_to(naive_box, DOWN, buff=1.0)
        if naive_note.width > 12.6:
            naive_note.scale_to_fit_width(12.6)
        self.play(FadeIn(naive_note))
        self.wait(4.5)

        naive_group = VGroup(naive_box, naive_label, x_mark, naive_note)
        self.play(FadeOut(c4), FadeOut(naive_group))

        # --- 5. MLA: compressão de baixo posto + absorção matemática ---
        c5 = callout("A solução: compressão conjunta de baixo posto, 'absorvida' de volta no cálculo da atenção", color=MECHANISM)
        self.play(FadeIn(c5))

        container5 = RoundedRectangle(corner_radius=0.15, width=13.2, height=4.6, color=GRAY_D, stroke_width=1.5).shift(DOWN * 0.3)
        self.play(Create(container5))

        kv_full_group = sized_box("Cache K/V\ncompleto", font_size=17, color=OLD, box_color=OLD, fill_opacity=0.2, min_width=2.6, min_height=1.2)
        kv_full_group.shift(LEFT * 4.6 + UP * 0.3)
        kv_full, kv_full_label = kv_full_group
        compress_arrow = Arrow(kv_full.get_right(), kv_full.get_right() + RIGHT * 1.4, color=MECHANISM, stroke_width=4)
        latent_group = sized_box("latente\n(baixo posto)", font_size=16, box_color=MECHANISM, fill_opacity=0.5, min_width=1.5, min_height=0.8, margin=0.3)
        latent_group.next_to(compress_arrow, RIGHT, buff=0.1)
        latent, latent_label = latent_group
        absorb_arrow = Arrow(latent.get_right(), latent.get_right() + RIGHT * 1.4, color=MECHANISM, stroke_width=4)
        recovered_group = sized_box("atenção\nrecuperada", font_size=17, box_color=ENCODER, fill_opacity=0.35, min_width=2.6, min_height=1.2)
        recovered_group.next_to(absorb_arrow, RIGHT, buff=0.1)
        recovered, recovered_label = recovered_group

        self.play(FadeIn(kv_full), FadeIn(kv_full_label))
        self.play(GrowArrow(compress_arrow))
        self.play(FadeIn(latent), FadeIn(latent_label))
        self.play(GrowArrow(absorb_arrow))
        self.play(FadeIn(recovered), FadeIn(recovered_label))
        absorb_note = Text("a projeção é absorvida matematicamente nos pesos de atenção — sem recalcular o K/V cheio", font_size=16, color=GRAY_B)
        absorb_note.next_to(VGroup(kv_full, recovered), DOWN, buff=1.0)
        if absorb_note.width > 12.8:
            absorb_note.scale_to_fit_width(12.8)
        self.play(FadeIn(absorb_note))
        self.wait(5.5)

        mla_group = VGroup(container5, kv_full, kv_full_label, compress_arrow, latent, latent_label, absorb_arrow, recovered, recovered_label, absorb_note)
        self.play(FadeOut(c5), FadeOut(mla_group))

        # --- 6. Custo de treino ---
        c6 = callout('O resultado prático: treinar o modelo inteiro custou "apenas" 2.788M horas de GPU H800')
        self.play(FadeIn(c6))

        term_cost = terminal_box([
            "671B parâmetros, 14.8T tokens de treino",
            "2.788M horas de GPU H800 no total",
            "",
            '"nenhum pico de perda irrecuperável" durante todo o treino',
        ], font_size=17).shift(DOWN * 0.1)
        self.play(FadeIn(term_cost))
        self.wait(4.5)

        self.play(FadeOut(c6), FadeOut(term_cost))

        # --- 7. R1: RL puro com recompensa verificável ---
        c7 = callout("DeepSeek-R1: raciocínio incentivado via RL puro, sem trajetórias humanas rotuladas", color=MECHANISM)
        self.play(FadeIn(c7))

        term = terminal_box([
            "treino tradicional: imitar exemplos de raciocínio humano",
            "R1: recompensa só pela resposta final (RL puro)",
            "",
            "recompensa verificável, não um modelo de recompensa aprendido:",
            "  matemática -> a resposta final bate com o gabarito?",
            "  código     -> passou nos testes unitários?",
        ], font_size=16).shift(DOWN * 0.3)
        self.play(FadeIn(term))
        emergent_note = Text("efeito emergente: autoverificação, autocorreção, adaptação dinâmica de estratégia", font_size=16, color=MECHANISM)
        emergent_note.next_to(term, DOWN, buff=0.5)
        if emergent_note.width > 12.6:
            emergent_note.scale_to_fit_width(12.6)
        self.play(FadeIn(emergent_note))
        self.wait(5.5)

        r1_group = VGroup(term, emergent_note)
        self.play(FadeOut(c7), FadeOut(r1_group))

        # --- 8. Distillation ---
        c8 = callout("Destilação: o raciocínio do R1 é transferido para modelos bem menores")
        self.play(FadeIn(c8))

        container8 = RoundedRectangle(corner_radius=0.15, width=12.8, height=5.4, color=GRAY_D, stroke_width=1.5).shift(DOWN * 0.3)
        self.play(Create(container8))

        big_group = sized_box("R1\n(671B)", font_size=18, box_color=DECODER, fill_opacity=0.35, min_width=2.2, min_height=2.0)
        big_group.shift(LEFT * 4.6)
        big, big_label = big_group

        def distill_size_box(s):
            # min_width/min_height comfortably cover the longest label here ("1.5B");
            # shorter labels (7B/8B/14B/32B/70B) just land on that same floor, so the
            # whole row stays visually uniform without guessing each label's width.
            return sized_box(s, font_size=16, box_color=DECODER, fill_opacity=0.5, min_width=1.6, min_height=0.7, margin=0.25)

        row1 = VGroup(*[distill_size_box(s) for s in ["1.5B", "7B", "8B"]]).arrange(RIGHT, buff=0.3)
        row2 = VGroup(*[distill_size_box(s) for s in ["14B", "32B", "70B"]]).arrange(RIGHT, buff=0.3)
        small_models = VGroup(row1, row2).arrange(DOWN, buff=0.3).shift(RIGHT * 2.3)
        distill_arrow = Arrow(big.get_right(), small_models.get_left(), color=MECHANISM, stroke_width=3)

        self.play(FadeIn(big), FadeIn(big_label))
        self.play(GrowArrow(distill_arrow))
        self.play(FadeIn(small_models))
        base_note = Text("baseados em Qwen e Llama — o menor (1.5B) já supera modelos maiores sem destilação", font_size=16, color=GRAY_B)
        base_note.next_to(VGroup(big, small_models), DOWN, buff=0.9)
        if base_note.width > 12.8:
            base_note.scale_to_fit_width(12.8)
        self.play(FadeIn(base_note))
        self.wait(5)

        distill_group = VGroup(container8, big, big_label, small_models, distill_arrow, base_note)
        self.play(FadeOut(c8), FadeOut(distill_group))

        # --- Closing ---
        backdrop = RoundedRectangle(corner_radius=0.2, width=13, height=3.4, fill_color="#111111", fill_opacity=0.9, stroke_width=0)
        closing = Text(
            "MoE sem perdas competindo, atenção latente absorvida matematicamente,\ne raciocínio emergente via RL verificável — tudo em duas gerações.",
            font_size=26, color=WHITE, line_spacing=1.3,
        ).move_to(ORIGIN)
        if closing.width > 12.4:
            closing.scale_to_fit_width(12.4)
        self.play(FadeIn(backdrop))
        self.play(Write(closing))
        self.wait(4.5)
        self.play(FadeOut(backdrop), FadeOut(closing))
