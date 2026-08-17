from manim import *

# ============================================================================
# HEADER 1/3 — copied verbatim from llm_manim_helpers.py (repo root).
# ============================================================================

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
    label = Text(label_text, font_size=label_font_size, color=label_color)
    sub = Text(sub_text, font_size=sub_font_size, color=sub_color, line_spacing=1.1)
    caption = VGroup(label, sub).arrange(DOWN, buff=0.12, aligned_edge=LEFT)
    row = VGroup(diagram, caption).arrange(RIGHT, buff=gap)
    if row.width > max_width:
        diagram.scale_to_fit_width(diagram.width * max_width / row.width)
        row = VGroup(diagram, caption).arrange(RIGHT, buff=gap)
    return row


def uniform_boxes(texts, font_size=16, box_color=WHITE, box_opacity=0.3, margin=0.3, line_spacing=1.0, buff=0.3):
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
    label = Text(text_str, font_size=font_size, color=color, line_spacing=line_spacing)
    radius = max(label.width, label.height) / 2 + margin
    circle = Circle(radius=radius, color=circle_color, fill_color=circle_color, fill_opacity=fill_opacity)
    label.move_to(circle.get_center())
    return VGroup(circle, label)


def stack_rows(rows, buff=0.5, aligned_edge=LEFT):
    group = VGroup(*rows).arrange(DOWN, buff=buff, aligned_edge=aligned_edge)
    for i in range(len(rows) - 1):
        assert_no_overlap(rows[i], rows[i + 1], f"stack_rows: row {i} vs row {i+1}")
    return group


# ============================================================================
# HEADER 2/3 — copied verbatim from mosaic_manim_helpers.py (repo root).
# ============================================================================

def workspace_zone(width=12.8, height=5.2, y_shift=1.1):
    return RoundedRectangle(corner_radius=0.15, width=width, height=height,
                             color=GRAY_D, stroke_width=1.0, stroke_opacity=0.35).shift(UP * y_shift)


def enter_workspace(camera_frame, workspace, margin=1.0):
    scale = max((workspace.width + margin * 2) / camera_frame.width,
                (workspace.height + margin * 2) / camera_frame.height)
    camera_frame.scale(scale).move_to(workspace.get_center())


def mosaic_strip(n_slots, width=13.2, height=1.7, y_shift=4.2, gap=0.25):
    slot_w = (width - gap * (n_slots - 1)) / n_slots
    slots = VGroup(*[Rectangle(width=slot_w, height=height, stroke_opacity=0) for _ in range(n_slots)])
    slots.arrange(RIGHT, buff=gap).shift(DOWN * y_shift)
    return slots


def archive_to_slot(scene, beat_group, slot, run_time=1.2):
    scale = min(slot.width / beat_group.width, slot.height / beat_group.height)
    scene.play(beat_group.animate.scale(scale).move_to(slot.get_center()), run_time=run_time)


def zoomout_reveal(scene, camera_frame, mosaic_group, run_time=2.5):
    scale = max((mosaic_group.width + 1.2) / camera_frame.width,
                (mosaic_group.height + 1.2) / camera_frame.height)
    camera_frame.generate_target()
    camera_frame.target.scale(scale).move_to(mosaic_group.get_center())
    scene.play(MoveToTarget(camera_frame), run_time=run_time)


def assert_within_camera(inner, camera_frame, label=""):
    l, r = camera_frame.get_left()[0], camera_frame.get_right()[0]
    t, b = camera_frame.get_top()[1], camera_frame.get_bottom()[1]
    i_l, i_r = inner.get_left()[0], inner.get_right()[0]
    i_t, i_b = inner.get_top()[1], inner.get_bottom()[1]
    assert i_l >= l - 0.05 and i_r <= r + 0.05, (
        f"{label}: overflows current camera view horizontally [{i_l:.2f},{i_r:.2f}] vs camera ±[{l:.2f},{r:.2f}]"
    )
    assert i_b >= b - 0.05 and i_t <= t + 0.05, (
        f"{label}: overflows current camera view vertically [{i_b:.2f},{i_t:.2f}] vs camera ±[{b:.2f},{t:.2f}]"
    )


# ============================================================================
# HEADER 3/3 — copied verbatim from chart_manim_helpers.py (repo root).
# Only styled_bar_chart is actually used below (beat_cost_comparison), but
# the whole file is copied per the "copy verbatim" convention, not just the
# one function a given scene happens to need.
# ============================================================================

def styled_bar_chart(values, bar_names, colors=None, y_range=None, x_length=10, y_length=4, **kwargs):
    colors = colors or [MECHANISM] * len(values)
    return BarChart(values=values, bar_names=bar_names, y_range=y_range,
                     x_length=x_length, y_length=y_length,
                     bar_colors=colors, bar_fill_opacity=0.6, bar_stroke_width=2, **kwargs)


def styled_axes(x_range, y_range, x_length=10, y_length=5, **kwargs):
    return Axes(x_range=x_range, y_range=y_range, x_length=x_length, y_length=y_length,
                axis_config={"color": GRAY_B, "stroke_width": 2}, **kwargs)


def highlight_cell(table_or_matrix, pos, color=MECHANISM, is_table=True):
    if is_table:
        table_or_matrix.add_highlighted_cell(pos, color=color)
        return table_or_matrix
    entry = table_or_matrix.get_entries()[pos]
    return SurroundingRectangle(entry, color=color, buff=0.1)


def dimension_brace(mobj, direction, text, font_size=18, color=WHITE):
    brace = Brace(mobj, direction=direction)
    label = brace.get_text(text, font_size=font_size, color=color)
    return VGroup(brace, label)


# ============================================================================
# DEMO-SPECIFIC CODE — the BEATS list + beat_fn(scene, workspace) -> VGroup
# convention described in README.md, "Video format 2". This is the part a
# real future scene file actually edits/reorders; everything above this
# point is unchanged copy-paste header.
# ============================================================================

def _anchor_callout(text, workspace, color=WHITE):
    """callout() (header 1/3) places its Text via .to_edge(UP, ...), which
    is computed against the STATIC default frame — not the live
    camera_frame, which this format moves/scales every beat. Anchoring to
    `workspace` instead (a mobject whose world position never changes) keeps
    the callout correctly placed relative to the beat's own content
    regardless of where the camera has drifted to by the time this beat
    runs. Placed just INSIDE workspace's own top edge (not stacked above
    it, as an initial version of this helper did) — stacking above pushed
    the callout past the default camera frame's own top edge before the
    camera ever moves, caught immediately by assert_within_camera() against
    the real render service."""
    c = callout(text, color=color)
    c.move_to(workspace.get_top() + DOWN * (c.height / 2 + 0.15))
    return c


def beat_attention(scene, workspace):
    """Adapted from scenes/llms/01_transformer.py's self-attention beat."""
    tokens = ["O", "gato", "dormiu"]
    c = _anchor_callout("Self-attention: todo token atende a todos, ao mesmo tempo", workspace, color=MECHANISM)

    dots = VGroup(*[Dot(radius=0.14, color=ENCODER) for _ in tokens]).arrange(RIGHT, buff=1.6)
    dots.move_to(workspace.get_center() + DOWN * 0.3)
    dot_labels = VGroup(*[
        Text(tok, font_size=20, color=WHITE).next_to(d, DOWN, buff=0.25) for tok, d in zip(tokens, dots)
    ])
    pairs = [(i, j) for i in range(len(dots)) for j in range(len(dots)) if i != j]
    attn_lines = VGroup(*[
        Line(dots[i].get_center(), dots[j].get_center(), color=MECHANISM, stroke_width=2, stroke_opacity=0.7)
        for i, j in pairs
    ])

    group = VGroup(c, dots, dot_labels, attn_lines)
    assert_within_camera(group, scene.camera.frame, "beat_attention")

    scene.play(FadeIn(c))
    scene.play(LaggedStart(*[FadeIn(d) for d in dots], lag_ratio=0.2), FadeIn(dot_labels))
    scene.play(LaggedStart(*[Create(l) for l in attn_lines], lag_ratio=0.05, run_time=1.5))
    scene.wait(1)
    return group


def beat_decoder_stack(scene, workspace):
    """Adapted from scenes/llms/02_gpt.py's decoder-only stack beat."""
    c = _anchor_callout("GPT: metade decoder do Transformer, autoregressivo", workspace, color=DECODER)

    names = ["Masked Self-Attention", "Add & Norm", "Feed-Forward", "Add & Norm"]
    colors_by_name = [MECHANISM, NORM, FFN, NORM]
    name_labels = [Text(n, font_size=16, color=WHITE) for n in names]
    block_width = max(3.0, max(l.width for l in name_labels) + 0.5)
    block_height = max(0.6, max(l.height for l in name_labels) + 0.4)
    labeled = VGroup()
    for label, col in zip(name_labels, colors_by_name):
        b = RoundedRectangle(corner_radius=0.08, width=block_width, height=block_height, color=col).set_fill(col, opacity=0.3)
        label.move_to(b)
        labeled.add(VGroup(b, label))
    labeled.arrange(DOWN, buff=0.14)
    outline = SurroundingRectangle(labeled, color=DECODER, buff=0.2, corner_radius=0.1)
    stack_label = Text("Decoder (GPT)", font_size=18, color=DECODER).next_to(outline, UP, buff=0.12)
    nx = Text("× N", font_size=14, color=GRAY_B).next_to(outline, DOWN, buff=0.1)
    stack = VGroup(outline, labeled, stack_label, nx).move_to(workspace.get_center() + DOWN * 0.2)

    group = VGroup(c, stack)
    assert_within_camera(group, scene.camera.frame, "beat_decoder_stack")

    scene.play(FadeIn(c))
    scene.play(FadeIn(stack))
    scene.wait(1)
    return group


def beat_selective_state(scene, workspace):
    """Adapted from scenes/llms/08_mamba.py's selective-SSM beat, reusing
    terminal_box() as the explicit example the user asked to lean on."""
    tokens = ["O", "gato", "irrelevante", "dormiu"]
    c = _anchor_callout("Mamba: os parâmetros do SSM viram função do próprio token", workspace, color=MECHANISM)

    dots2 = VGroup(*[Dot(radius=0.12, color=DECODER) for _ in tokens]).arrange(RIGHT, buff=1.3)
    dots2.move_to(workspace.get_center() + UP * 0.9)
    labels2 = VGroup(*[
        Text(t, font_size=15, color=WHITE).next_to(d, DOWN, buff=0.18) for t, d in zip(tokens, dots2)
    ])
    widths = [6, 6, 1, 6]
    segs = VGroup(*[
        Line(dots2[i].get_center(), dots2[i + 1].get_center(), color=MECHANISM, stroke_width=widths[i])
        for i in range(len(dots2) - 1)
    ])
    term4 = terminal_box([
        "Δ, B, C (parâmetros do SSM) = função(xₜ)",
        "'irrelevante' -> Δ pequeno -> quase nada atualiza o estado",
        "'gato', 'dormiu' -> Δ grande -> o estado é atualizado de verdade",
    ], font_size=15, width=10.5).next_to(dots2, DOWN, buff=0.8)

    group = VGroup(c, dots2, labels2, segs, term4)
    assert_within_camera(group, scene.camera.frame, "beat_selective_state")

    scene.play(FadeIn(c))
    scene.play(FadeIn(dots2), FadeIn(labels2))
    scene.play(LaggedStart(*[Create(s) for s in segs], lag_ratio=0.3))
    scene.play(FadeIn(term4))
    scene.wait(1)
    return group


def beat_cost_comparison(scene, workspace):
    """Adapted from scenes/llms/09_rwkv.py's quadratic-cost bar chart, but
    rebuilt with the new styled_bar_chart() (built-in BarChart) instead of
    hand-rolled Rectangles — exercises the chart toolkit and the mosaic
    pattern in the same beat."""
    c = _anchor_callout("Custo quadrático: dobrar o contexto quadruplica o trabalho", workspace, color=OLD)

    n_values = [4, 8, 16]
    costs = [n * n for n in n_values]
    chart = styled_bar_chart(
        costs, bar_names=[f"seq={n}" for n in n_values], colors=[OLD, OLD, OLD], x_length=8, y_length=3.0,
    )
    chart.move_to(workspace.get_center() + DOWN * 0.2)
    note = Text(
        "o mesmo custo que motivou RWKV a abandonar a atenção quadrática", font_size=15, color=GRAY_B,
    ).next_to(chart, DOWN, buff=0.4)

    group = VGroup(c, chart, note)
    assert_within_camera(group, scene.camera.frame, "beat_cost_comparison")

    scene.play(FadeIn(c))
    scene.play(Create(chart))
    scene.play(FadeIn(note))
    scene.wait(1)
    return group


# The "escolher as cenas" mechanism: an ordered, editable list. Reorder or
# swap entries here to assemble a different lineage video from the same
# beat vocabulary.
BEATS = [beat_attention, beat_decoder_stack, beat_selective_state, beat_cost_comparison]


class LineageOfLLMsDemo(MovingCameraScene):
    def construct(self):
        title = Text("Uma linhagem de LLMs, em uma tela só", font_size=32, color=WHITE)
        subtitle = Text("prova de conceito: mosaico acumulativo + zoomout final", font_size=20, color=GRAY_B)
        subtitle.next_to(title, DOWN, buff=0.35)
        self.play(Write(title))
        self.play(FadeIn(subtitle))
        self.wait(2)
        self.play(FadeOut(title), FadeOut(subtitle))

        workspace = workspace_zone()
        slots = mosaic_strip(n_slots=len(BEATS))
        assert_no_overlap(workspace, slots, "workspace vs mosaic strip")
        enter_workspace(self.camera.frame, workspace)
        self.play(Create(workspace))

        for i, beat_fn in enumerate(BEATS):
            beat_group = beat_fn(self, workspace)
            archive_to_slot(self, beat_group, slots[i])

        zoomout_reveal(self, self.camera.frame, VGroup(workspace, slots))

        closing = Text(
            "Do Transformer ao Mamba: tudo que ficou pelo caminho, de volta numa imagem só.",
            font_size=20, color=WHITE,
        ).move_to(workspace.get_center())
        if closing.width > workspace.width - 1.0:
            closing.scale_to_fit_width(workspace.width - 1.0)
        self.play(FadeIn(closing))
        self.wait(2.5)
