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


class MistralScene(Scene):
    def construct(self):
        title = Text("Mistral 7B", font_size=42, color=WHITE)
        subtitle = Text("Jiang et al., Mistral AI, 2023", font_size=24, color=GRAY_B)
        subtitle.next_to(title, DOWN, buff=0.35)
        self.play(Write(title))
        self.play(FadeIn(subtitle))
        self.wait(2.5)
        self.play(FadeOut(title), FadeOut(subtitle))

        # --- 1. O espectro: MHA -> MQA -> GQA ---
        c1 = callout("Um espectro de escolhas: quantos heads de query dividem o mesmo Key/Value?")
        self.play(FadeIn(c1))

        container1 = safe_container()
        self.play(Create(container1))

        # Laid out as 3 stacked ROWS (not 3 side-by-side columns) specifically
        # so the widest element (MHA's 4-box K/V row) plus its full-width
        # caption never has to compete horizontally with the other two
        # variants — each row only needs to fit container1's width on its
        # own. Only the small decorative rectangles (Q/K/V boxes, not text)
        # are shrunk to help this fit; every Text stays at its declared
        # font_size, never scaled down afterward.
        def make_variant_diagram(n_kv, kv_color_opacity):
            qs = VGroup(*[
                RoundedRectangle(corner_radius=0.05, width=0.45, height=0.32, color=MECHANISM, fill_color=MECHANISM, fill_opacity=0.35)
                for _ in range(4)
            ]).arrange(RIGHT, buff=0.1)
            if n_kv == 1:
                kvs = VGroup(RoundedRectangle(corner_radius=0.05, width=1.9, height=0.32, color=ENCODER, fill_color=ENCODER, fill_opacity=kv_color_opacity))
            else:
                kvs = VGroup(*[
                    RoundedRectangle(corner_radius=0.05, width=0.85, height=0.32, color=ENCODER, fill_color=ENCODER, fill_opacity=kv_color_opacity)
                    for _ in range(n_kv)
                ]).arrange(RIGHT, buff=0.15)
            kvs.next_to(qs, DOWN, buff=0.3)
            conn = VGroup()
            per_kv = 4 // n_kv
            for i in range(4):
                target = kvs[i // per_kv] if n_kv > 1 else kvs[0]
                conn.add(Line(qs[i].get_bottom(), target.get_top(), color=GRAY_B, stroke_width=1.5))
            return VGroup(qs, kvs, conn)

        mha_row = diagram_row(make_variant_diagram(4, 0.35), "MHA", "cada head, seu próprio K/V (mais qualidade, cache maior)", sub_color=GRAY_B)
        gqa_row = diagram_row(make_variant_diagram(2, 0.5), "GQA", "grupos de heads compartilham (o meio-termo do Mistral)", sub_color=MECHANISM)
        mqa_row = diagram_row(make_variant_diagram(1, 0.6), "MQA", "todos os heads, 1 só K/V (cache mínimo, pode perder qualidade)", sub_color=GRAY_B)

        # stack_rows uses a generous explicit buff and asserts adjacent rows
        # don't collide — this is what caught (and now prevents) the earlier
        # "captions overlapping between rows" bug.
        variants = stack_rows([mha_row, gqa_row, mqa_row], buff=0.55)
        variants.move_to(container1.get_center())
        assert_on_screen(variants, "mistral spectrum variants")
        self.play(FadeIn(mha_row))
        self.wait(1.5)
        self.play(FadeIn(gqa_row))
        self.wait(1.5)
        self.play(FadeIn(mqa_row))
        self.wait(4.5)

        spectrum_group = VGroup(container1, variants)
        self.play(FadeOut(c1), FadeOut(spectrum_group))

        # --- 2. Por que o cache K/V importa ---
        c2 = callout("Por que isso importa: o cache K/V é o gargalo real da geração autoregressiva", color=MECHANISM)
        self.play(FadeIn(c2))

        term_cache = terminal_box([
            "gerando token a token, a GPU guarda o K e o V de CADA token já visto:",
            "",
            "  token 1    -> cache: [K1,V1]                  (1 entrada)",
            "  token 2    -> cache: [K1,V1, K2,V2]            (2 entradas)",
            "  ...",
            "  token 1000 -> cache: 1000 pares K/V guardados na GPU",
            "",
            "GQA encolhe CADA entrada -> menos memória por token",
            "-> mais requisições cabem no mesmo lote (batch) ao mesmo tempo",
        ], font_size=17).shift(DOWN * 0.1)
        self.play(FadeIn(term_cache))
        self.wait(5.5)

        self.play(FadeOut(c2), FadeOut(term_cache))

        # --- 3. GQA em detalhe: Mistral na prática ---
        c3 = callout("Grouped-Query Attention na prática: a escolha do Mistral 7B")
        self.play(FadeIn(c3))

        q_heads = VGroup(*[
            RoundedRectangle(corner_radius=0.06, width=1.1, height=0.5, color=MECHANISM).set_fill(MECHANISM, opacity=0.3)
            for _ in range(4)
        ]).arrange(RIGHT, buff=0.25)
        q_labels = VGroup(*[Text(f"Q{i+1}", font_size=16, color=WHITE).move_to(b) for i, b in enumerate(q_heads)])
        q_group = VGroup(q_heads, q_labels).shift(UP * 1.0)

        kv_label = Text("K, V (compartilhado)", font_size=16, color=WHITE)
        kv_box = RoundedRectangle(
            corner_radius=0.08, width=kv_label.width + 0.6, height=kv_label.height + 0.5, color=ENCODER
        ).set_fill(ENCODER, opacity=0.35)
        kv_label.move_to(kv_box.get_center())
        kv_group = VGroup(kv_box, kv_label).shift(DOWN * 0.6)

        arrows = VGroup(*[
            Arrow(q.get_bottom(), kv_box.get_top() + RIGHT * (i - 1.5) * 0.3, buff=0.08, color=GRAY_B, stroke_width=2)
            for i, q in enumerate(q_heads)
        ])

        self.play(FadeIn(q_group))
        self.play(FadeIn(kv_group))
        self.play(LaggedStart(*[GrowArrow(a) for a in arrows], lag_ratio=0.2))
        gqa_note = Text("menos memória de cache -> lotes maiores durante a geração", font_size=17, color=GRAY_B)
        gqa_note.next_to(kv_group, DOWN, buff=0.8)
        self.play(FadeIn(gqa_note))
        self.wait(4.5)

        gqa_group = VGroup(q_group, kv_group, arrows, gqa_note)
        self.play(FadeOut(c3), FadeOut(gqa_group))

        # --- 4. Sliding Window Attention ---
        c4 = callout("Sliding Window Attention: cada token só atende a uma janela W de tokens anteriores", color=MECHANISM)
        self.play(FadeIn(c4))

        tokens = ["O", "gato", "preto", "dormiu", "cedo", "ontem"]
        dots = VGroup(*[Dot(radius=0.11, color=DECODER) for _ in tokens]).arrange(RIGHT, buff=0.9).shift(UP * 0.9)
        labels = VGroup(*[Text(t, font_size=16, color=WHITE).next_to(d, DOWN, buff=0.2) for t, d in zip(tokens, dots)])
        self.play(FadeIn(dots), FadeIn(labels))

        w = 2

        def window_view(idx):
            wl = VGroup()
            for j in range(max(0, idx - w), idx):
                wl.add(Line(dots[idx].get_center(), dots[j].get_center(), color=MECHANISM, stroke_width=3))
            fl = VGroup()
            for j in range(0, max(0, idx - w)):
                fl.add(DashedVMobject(
                    Line(dots[idx].get_center(), dots[j].get_center(), color=OLD, stroke_width=1.5, stroke_opacity=0.3),
                    num_dashes=10,
                ))
            hl = Circle(radius=0.2, color=WHITE).move_to(dots[idx].get_center())
            return wl, fl, hl

        wl1, fl1, hl1 = window_view(3)
        self.play(Create(hl1))
        self.play(LaggedStart(*[Create(l) for l in fl1], lag_ratio=0.1))
        self.play(LaggedStart(*[Create(l) for l in wl1], lag_ratio=0.2))
        sw_note1 = Text(f"janela W={w}: 'dormiu' só vê diretamente os {w} tokens mais recentes", font_size=16, color=GRAY_B)
        sw_note1.next_to(dots, DOWN, buff=0.9)
        if sw_note1.width > 12.6:
            sw_note1.scale_to_fit_width(12.6)
        self.play(FadeIn(sw_note1))
        self.wait(3.5)

        self.play(FadeOut(wl1), FadeOut(fl1), FadeOut(hl1))
        wl2, fl2, hl2 = window_view(5)
        self.play(Create(hl2))
        self.play(LaggedStart(*[Create(l) for l in fl2], lag_ratio=0.1))
        self.play(LaggedStart(*[Create(l) for l in wl2], lag_ratio=0.2))
        sw_note2 = Text(f"'ontem' também só vê {w} tokens diretamente — custo linear, não quadrático", font_size=16, color=GRAY_B)
        sw_note2.next_to(dots, DOWN, buff=0.9)
        if sw_note2.width > 12.6:
            sw_note2.scale_to_fit_width(12.6)
        self.play(ReplacementTransform(sw_note1, sw_note2))
        self.wait(4)

        sw_group1 = VGroup(dots, labels, wl2, fl2, hl2, sw_note2)
        self.play(FadeOut(c4), FadeOut(sw_group1))

        # --- 5. O campo receptivo cresce com a profundidade ---
        c5 = callout("Mas indiretamente, a informação viaja mais longe: o campo receptivo cresce a cada camada", color=MECHANISM)
        self.play(FadeIn(c5))

        container2 = safe_container(height=5.0, y_shift=-0.2)
        self.play(Create(container2))

        n_layers = 3
        layer_rows = VGroup()
        reach_per_layer = w
        for layer_i in range(n_layers):
            row_dots = VGroup(*[Dot(radius=0.09, color=DECODER) for _ in tokens]).arrange(RIGHT, buff=0.9)
            reach = min(len(tokens) - 1, reach_per_layer * (layer_i + 1))
            span_line = Line(row_dots[len(tokens) - 1].get_center(), row_dots[len(tokens) - 1 - reach].get_center(), color=MECHANISM, stroke_width=4)
            layer_label = Text(f"camada {layer_i + 1}: alcance efetivo = {reach} tokens", font_size=16, color=GRAY_B)
            layer_label.next_to(row_dots, LEFT, buff=0.4)
            layer_row = VGroup(span_line, row_dots, layer_label)
            layer_rows.add(layer_row)
        layer_rows.arrange(DOWN, buff=0.55).move_to(container2.get_center() + UP * 0.2)
        if layer_rows.width > 12.4:
            layer_rows.scale_to_fit_width(12.4)

        for row in layer_rows:
            self.play(FadeIn(row), run_time=0.8)
        depth_note = Text("W por camada, mas W x profundidade no total — daí a janela ser suficiente na prática", font_size=16, color=GRAY_B)
        depth_note.next_to(layer_rows, DOWN, buff=0.4)
        if depth_note.width > 12.4:
            depth_note.scale_to_fit_width(12.4)
        self.play(FadeIn(depth_note))
        self.wait(5)

        depth_group = VGroup(container2, layer_rows, depth_note)
        self.play(FadeOut(c5), FadeOut(depth_group))

        # --- 6. Result callout ---
        c6 = callout("O resultado direto do paper:")
        self.play(FadeIn(c6))
        term = terminal_box([
            '"Mistral 7B supera o melhor modelo aberto',
            ' de 13B (Llama 2) em todos os benchmarks avaliados"',
        ], font_size=19).shift(DOWN * 0.1)
        self.play(FadeIn(term))
        self.wait(4.5)
        self.play(FadeOut(c6), FadeOut(term))

        # --- 7. Mixtral: MoE on top, roteamento por token ---
        c7 = callout("Mixtral (mesma equipe): Mixture-of-Experts em cima da mesma base", color=MECHANISM)
        self.play(FadeIn(c7))

        router = RoundedRectangle(corner_radius=0.08, width=2.0, height=0.6, color=MECHANISM).set_fill(MECHANISM, opacity=0.4).shift(UP * 1.3)
        router_label = Text("Router", font_size=16, color=WHITE).move_to(router)

        experts = VGroup(*[
            RoundedRectangle(corner_radius=0.08, width=1.5, height=0.9, color=FFN).set_fill(FFN, opacity=0.15)
            for _ in range(8)
        ]).arrange(RIGHT, buff=0.25).shift(DOWN * 0.4)
        expert_labels = VGroup(*[Text(f"E{i+1}", font_size=16, color=GRAY_B).move_to(b) for i, b in enumerate(experts)])

        self.play(FadeIn(router), FadeIn(router_label))
        self.play(FadeIn(experts), FadeIn(expert_labels))

        token_a_label = Text('token: "gato"', font_size=16, color=WHITE).next_to(router, UP, buff=0.3)
        active_a = [1, 5]
        route_arrows_a = VGroup(*[
            Arrow(router.get_bottom(), experts[i].get_top(), buff=0.1, color=FFN, stroke_width=3)
            for i in active_a
        ])
        self.play(FadeIn(token_a_label))
        for i in active_a:
            self.play(experts[i].animate.set_fill(FFN, opacity=0.6).set_stroke(FFN, width=3), expert_labels[i].animate.set_color(WHITE), GrowArrow(route_arrows_a[active_a.index(i)]), run_time=0.6)
        moe_note = Text("só 2 dos 8 especialistas ativados por token — custo de um modelo bem menor", font_size=16, color=GRAY_B)
        moe_note.next_to(experts, DOWN, buff=0.7)
        self.play(FadeIn(moe_note))
        self.wait(3.5)

        # reset colors and route a second, different token
        self.play(
            *[experts[i].animate.set_fill(FFN, opacity=0.15).set_stroke(FFN, width=2) for i in active_a],
            *[expert_labels[i].animate.set_color(GRAY_B) for i in active_a],
            FadeOut(route_arrows_a),
        )
        token_b_label = Text('token: "equação"', font_size=16, color=WHITE).next_to(router, UP, buff=0.3)
        active_b = [2, 6]
        route_arrows_b = VGroup(*[
            Arrow(router.get_bottom(), experts[i].get_top(), buff=0.1, color=FFN, stroke_width=3)
            for i in active_b
        ])
        self.play(ReplacementTransform(token_a_label, token_b_label))
        for i in active_b:
            self.play(experts[i].animate.set_fill(FFN, opacity=0.6).set_stroke(FFN, width=3), expert_labels[i].animate.set_color(WHITE), GrowArrow(route_arrows_b[active_b.index(i)]), run_time=0.6)
        moe_note2 = Text("o roteamento é por token e depende do conteúdo — cada palavra pode escolher especialistas diferentes", font_size=16, color=MECHANISM)
        moe_note2.next_to(experts, DOWN, buff=0.7)
        if moe_note2.width > 12.6:
            moe_note2.scale_to_fit_width(12.6)
        self.play(ReplacementTransform(moe_note, moe_note2))
        self.wait(5)

        moe_group = VGroup(router, router_label, experts, expert_labels, route_arrows_b, moe_note2, token_b_label)
        self.play(FadeOut(c7), FadeOut(moe_group))

        # --- Closing ---
        backdrop = RoundedRectangle(corner_radius=0.2, width=13, height=3.4, fill_color="#111111", fill_opacity=0.9, stroke_width=0)
        closing = Text(
            "GQA e sliding window atacam o custo da atenção sem trocar de paradigma;\n"
            "Mixtral prova que roteamento condicional funciona em produção —\n"
            "o caminho que a DeepSeek leva ainda mais longe.",
            font_size=25, color=WHITE, line_spacing=1.3,
        ).move_to(ORIGIN)
        if closing.width > 12.4:
            closing.scale_to_fit_width(12.4)
        self.play(FadeIn(backdrop))
        self.play(Write(closing))
        self.wait(4.5)
        self.play(FadeOut(backdrop), FadeOut(closing))
