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


# Hard legibility floor: at the render service's fixed 720p output, text
# below this renders with visibly uneven letter spacing — a rasterization
# problem, not a code problem. This has now shipped for real more than
# once (most recently a plain caption Text at font_size=13 in the JEPA
# overview scene, caught only after publishing) despite being documented
# in prose here for a while — prose alone didn't stop it from recurring.
# Every helper below that creates Text asserts against this floor instead
# of silently accepting a too-small size, so a violation is a loud,
# immediate AssertionError at scene-authoring time (with the offending
# helper named), not a video a human has to notice is broken after it's
# already rendered and published.
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
    """The preferred way to build a long running caption/note, in place of
    the ad hoc `if t.width > cap: t.scale_to_fit_width(cap)` pattern
    scattered across earlier scenes — that pattern silently shrinks text
    below the legibility floor whenever a caption runs long, which is
    exactly how the recurring letter-spacing bug kept coming back even
    with every individual font_size already >= 16. This asserts loudly
    instead of shrinking: split the caption across lines with a literal
    '\\n' (which Text, unlike Tex/MathTex, honors correctly as a real line
    break) or shorten it, rather than let it auto-shrink into illegibility."""
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


def assert_within(inner, outer, label=""):
    """Fail loudly if `inner`'s bounding box is not fully contained within
    `outer`'s — catches an element spilling past a drawn safe-area container
    (e.g. safe_container()) even when it's still technically inside the raw
    render frame, which reads as an overflow bug to a viewer regardless."""
    i_l, i_r, i_t, i_b = inner.get_left()[0], inner.get_right()[0], inner.get_top()[1], inner.get_bottom()[1]
    o_l, o_r, o_t, o_b = outer.get_left()[0], outer.get_right()[0], outer.get_top()[1], outer.get_bottom()[1]
    assert i_l >= o_l - 0.05 and i_r <= o_r + 0.05 and i_b >= o_b - 0.05 and i_t <= o_t + 0.05, (
        f"{label}: inner=[{i_l:.2f},{i_r:.2f}]x[{i_b:.2f},{i_t:.2f}] not within outer=[{o_l:.2f},{o_r:.2f}]x[{o_b:.2f},{o_t:.2f}]"
    )


def diagram_row(diagram, label_text, sub_text, label_color=WHITE, sub_color=GRAY_B,
                label_font_size=18, sub_font_size=16, max_width=12.4, gap=0.6):
    """A generic 'small diagram + two-line caption' row: label stacked above
    sub with a real buff (never overlapping by construction), placed beside
    the diagram. If the combined row is too wide, only the diagram (never
    the caption text) is shrunk to fit. Returns the assembled row group —
    use `stack_rows()` to lay several of these out vertically without
    guessing buff sizes by hand."""
    _assert_font_floor(label_font_size, "diagram_row label")
    _assert_font_floor(sub_font_size, "diagram_row sub")
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
    _assert_font_floor(font_size, "uniform_boxes")
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
    _assert_font_floor(font_size, "sized_circle")
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
from manim import *

# ANOTHER copy-paste header, independent of mosaic_manim_helpers.py — depends
# only on llm_manim_helpers.py's color constants and font default. A scene
# can use these chart/graph/table helpers without adopting the mosaic/camera
# pattern, and vice versa.
#
# These are thin, project-styled wrappers over Manim Community's own
# built-in graphing/table mobjects — the goal is to stop hand-rolling bar
# charts out of Rectangle + next_to (as scenes/llms/09_rwkv.py and
# 02_gpt.py currently do) when the library already ships a real one.


def styled_bar_chart(values, bar_names, colors=None, y_range=None, x_length=10, y_length=4, **kwargs):
    """Wrapper over Manim's built-in BarChart, defaulting to this project's
    palette instead of the ad hoc Rectangle-based bars scenes/llms/09_rwkv.py
    and 02_gpt.py currently hand-roll. `colors` defaults to a single
    MECHANISM-colored repeat matching those existing hand-rolled charts;
    pass a list to color bars individually (e.g. one OLD + one DECODER bar
    for an old-vs-new comparison, as in 02_gpt.py's GPT-1→GPT-3 params
    chart)."""
    colors = colors or [MECHANISM] * len(values)
    return BarChart(values=values, bar_names=bar_names, y_range=y_range,
                     x_length=x_length, y_length=y_length,
                     bar_colors=colors, bar_fill_opacity=0.6, bar_stroke_width=2, **kwargs)


def styled_axes(x_range, y_range, x_length=10, y_length=5, **kwargs):
    """Wrapper over Axes with stroke/color consistent with the rest of this
    series' diagrams — for plotting curves (loss over training steps, a
    cost-vs-sequence-length comparison) instead of hand-placing Dots and
    Lines to fake a graph."""
    return Axes(x_range=x_range, y_range=y_range, x_length=x_length, y_length=y_length,
                axis_config={"color": GRAY_B, "stroke_width": 2}, **kwargs)


def highlight_cell(table_or_matrix, pos, color=MECHANISM, is_table=True):
    """Highlights one cell of a Table (is_table=True, via
    Table.add_highlighted_cell — mutates and returns table_or_matrix) or one
    entry of a Matrix (is_table=False, via a SurroundingRectangle around
    Matrix.get_entries()[pos] — returns the rectangle to add/animate
    alongside the matrix). The built-in version of the 'draw a rectangle
    around the cell I'm narrating' idiom, useful for Q/K/V matrices,
    confusion matrices, or permission tables in future long-form videos."""
    if is_table:
        table_or_matrix.add_highlighted_cell(pos, color=color)
        return table_or_matrix
    entry = table_or_matrix.get_entries()[pos]
    return SurroundingRectangle(entry, color=color, buff=0.1)


def dimension_brace(mobj, direction, text, font_size=18, color=WHITE):
    """Wraps Brace(...).get_text(...) with this project's default label
    size/color — the standard way to label a dimension or range (e.g.
    bracing a row of matrix entries to name it 'd_model')."""
    brace = Brace(mobj, direction=direction)
    label = brace.get_text(text, font_size=font_size, color=color)
    return VGroup(brace, label)


def styled_code_block(src, language="python", font_size=18, **kwargs):
    """Wraps Manim's Code mobject (real Pygments syntax highlighting) for
    when actual syntax color matters — an exploit snippet, a training loop —
    as an alternative to terminal_box() (llm_manim_helpers.py), which stays
    the right choice for plain command-line transcripts with no syntax
    coloring. NOTE: the Code mobject's constructor kwargs have changed
    across Manim Community releases — verified 2026-08-22 against the actual
    render service: current signature takes `code_string=` (not `code=`),
    font size only via `paragraph_config={"font_size": ...}` (no direct
    `font_size=` kwarg), and exposes its lines via `.code_lines` (not
    `.code`). Re-verify against whatever version the render service runs if
    this starts failing again — see README, "Verifying against the render
    service"."""
    return Code(code_string=src, language=language, paragraph_config={"font_size": font_size},
                background="rectangle", tab_width=2, **kwargs)


# Not implemented in this module: a node/edge diagram helper (circles for
# nodes, edges colored/weighted by relationship strength) inspired by
# 3b1b's hand-rolled NetworkMobject (github.com/3b1b/videos,
# _2017/nn/part1.py / helpers.py). Valuable for both ML architecture
# diagrams and cybersecurity attack-graph visuals, but left as a documented
# future extension rather than built speculatively here.
from manim import *

# ANOTHER copy-paste header, independent of mosaic_manim_helpers.py — depends
# only on llm_manim_helpers.py's color constants, font default, and
# `_assert_font_floor` being copied in above this file (same convention as
# chart_manim_helpers.py).
#
# Generalized visual-explanation techniques for the math underlying a paper
# (vectors, matrices, linear transformations) — inspired by the LOGIC
# 3Blue1Brown uses in "Essence of Linear Algebra" (github.com/3b1b/videos,
# _2016/eola/) and his transformer helpers (_2024/transformers/helpers.py),
# never his visual identity or code verbatim. Where Manim Community already
# ships the real thing (`LinearTransformationScene`, `DecimalMatrix`), these
# are thin wrappers over it — same philosophy as chart_manim_helpers.py:
# stop hand-rolling what the library already provides.


def value_to_color(value, low_color=BLUE_E, high_color=BLUE_B,
                    low_negative_color=RED_E, high_negative_color=RED_B, max_value=1.0):
    """Maps a signed value to a color on a diverging scale — blue-ish for
    positive, red-ish for negative, saturation proportional to
    |value| / max_value. The generalized idea behind every colored-number
    matrix/embedding/attention-weight visualization in this toolkit (3b1b's
    `value_to_color`, _2024/transformers/helpers.py); reused by
    neural_net_manim_helpers.py and transformer_viz_manim_helpers.py instead
    of each re-deriving its own gradient."""
    alpha = float(np.clip(abs(value) / max_value, 0, 1)) if max_value else 0.0
    colors = (low_color, high_color) if value >= 0 else (low_negative_color, high_negative_color)
    return interpolate_color(*colors, alpha)


def styled_vector(coords, color=WHITE, label=None, label_font_size=20, **kwargs):
    """A Vector/Arrow from the origin with an optional text label near its
    tip — the "arrow" half of 3b1b's arrow<->list-of-numbers duality for
    representing a vector (Essence of Linear Algebra, _2016/eola/chapter1.py,
    `CoordinateSystemWalkthrough`)."""
    vec = Vector(coords, color=color, **kwargs)
    if label is None:
        return vec
    _assert_font_floor(label_font_size, "styled_vector label")
    text = Text(label, font_size=label_font_size, color=color)
    text.next_to(vec.get_end(), UR, buff=0.1)
    return VGroup(vec, text)


def decompose_vector(vector, x_color=GREEN, y_color=RED, origin=ORIGIN):
    """Draws the x/y component lines of `vector` (an Arrow/Vector starting at
    `origin`) — the "decompose into components" beat from
    `CoordinateSystemWalkthrough.show_vector_coordinates` in 3b1b's Essence
    of Linear Algebra series (_2016/eola/chapter1.py)."""
    tip = vector.get_end()
    corner = np.array([tip[0], origin[1], 0])
    x_line = Line(origin, corner, color=x_color, stroke_width=3)
    y_line = Line(corner, tip, color=y_color, stroke_width=3)
    return VGroup(x_line, y_line)


def matrix_vector_product_animation(scene, matrix, vector, color=YELLOW, run_time_per_row=0.6):
    """Animates a matrix-vector product row by row: for each row of `matrix`
    (a Manim `Matrix`/`DecimalMatrix`), briefly highlights that row and the
    full `vector` together before moving to the next — the row-by-row reveal
    from 3b1b's `show_matrix_vector_product`/`show_symbolic_matrix_vector_product`
    (_2024/transformers/helpers.py), translated to Manim Community's own
    `Matrix` instead of ManimGL's. The caller is responsible for building/
    placing the "=" and result vector; this only drives the row-highlight
    animation."""
    last_rects = VGroup()
    for row in matrix.get_rows():
        rect_row = SurroundingRectangle(row, color=color, buff=0.08)
        rect_vec = SurroundingRectangle(vector, color=color, buff=0.08)
        scene.play(FadeOut(last_rects), Create(rect_row), Create(rect_vec), run_time=run_time_per_row)
        last_rects = VGroup(rect_row, rect_vec)
    scene.play(FadeOut(last_rects))


def linear_transform_grid(scene, matrix, run_time=3):
    """Animates the scene's plane deforming under a 2x2 linear
    transformation, basis vectors included — the generalized idea behind
    every grid-deformation shot in 3b1b's Essence of Linear Algebra series,
    as a thin wrapper over Manim Community's own `LinearTransformationScene`/
    `VectorScene` machinery (`apply_matrix`) instead of reimplementing grid
    deformation. `scene` must be a `LinearTransformationScene`:
        class YourScene(LinearTransformationScene):
            def construct(self):
                linear_transform_grid(self, [[2, 1], [1, 2]])
    """
    scene.apply_matrix(matrix, run_time=run_time)
from manim import *

# ANOTHER copy-paste header, independent of the others — depends only on
# llm_manim_helpers.py's font default/`_assert_font_floor` being copied in
# above this file if the calling scene also uses text labels on top of these
# shapes (not required by these functions themselves, which take no text).
#
# Generalized neuron/network-diagram techniques, inspired by the LOGIC
# behind 3b1b's `NetworkMobject`/`NetworkScene` (github.com/3b1b/videos,
# _2017/nn/part1.py) — never his visual identity: neurons as circles in
# per-layer columns, activation shown via fill opacity (not a fixed color),
# and a signal-propagation flash built on Manim Community's own
# `ShowPassingFlash` instead of reimplementing the sliver-reveal effect.


def build_network(layer_sizes, neuron_radius=0.15, neuron_color=WHITE, edge_color=GRAY_B,
                   layer_buff=1.5, neuron_buff=0.35):
    """Builds a layered neuron-network diagram — neurons as Circles arranged
    in vertical columns per layer, edges as Lines between every pair of
    neurons in consecutive layers. The Manim Community equivalent of 3b1b's
    `NetworkMobject` (_2017/nn/part1.py), generalized: any paper with a
    dense/MLP block can reuse this, not just a neural-networks-101 video.
    Returns (network, layers, edge_groups) — `layers` is a list of VGroups
    of neurons (one per layer), `edge_groups` a list of VGroups of edges
    (one per consecutive-layer pair), so callers can pass them straight to
    `activate_layer`/`pulse_edges` below."""
    layers = []
    for size in layer_sizes:
        neurons = VGroup(*[
            Circle(radius=neuron_radius, color=neuron_color, fill_color=neuron_color, fill_opacity=0)
            for _ in range(size)
        ]).arrange(DOWN, buff=neuron_buff)
        layers.append(neurons)
    layer_group = VGroup(*layers).arrange(RIGHT, buff=layer_buff)

    edge_groups = []
    for l1, l2 in zip(layers[:-1], layers[1:]):
        edges = VGroup(*[
            Line(n1.get_center(), n2.get_center(), buff=neuron_radius, color=edge_color, stroke_width=1.5)
            for n1 in l1 for n2 in l2
        ])
        edge_groups.append(edges)

    network = VGroup(VGroup(*edge_groups), layer_group)
    return network, layers, edge_groups


def activate_layer(layer, values, color=YELLOW):
    """Sets each neuron's fill_opacity to its activation value (0-1) — the
    generalized "how do you show a value flowing through a neuron" idea from
    3b1b's `activate_layer` (_2017/nn/part1.py): opacity encodes magnitude
    instead of picking a new color per value. Mutates `layer` in place and
    returns it for chaining; wrap the call in `Transform`/`.animate` at the
    call site to animate the change instead of setting it instantly."""
    for neuron, value in zip(layer, values):
        neuron.set_fill(color=color, opacity=float(np.clip(value, 0, 1)))
    return layer


def pulse_edges(edges, color=YELLOW, run_time=1.0, lag_ratio=0.05, time_width=0.3):
    """Returns a signal-propagation flash Animation over `edges` (a VGroup of
    Lines) — the generalized "show a value flowing along a connection" idea
    from 3b1b's `get_edge_propogation_animations`/`ContextAnimation`
    (_2017/nn/part1.py, _2024/transformers/helpers.py), built here on
    Manim Community's own `ShowPassingFlash` instead of reimplementing the
    effect. Pass the result straight to `scene.play(...)`."""
    flashes = edges.copy().set_stroke(color=color, width=3)
    return LaggedStart(*[ShowPassingFlash(e, time_width=time_width) for e in flashes],
                        lag_ratio=lag_ratio, run_time=run_time)
from manim import *

# ANOTHER copy-paste header. Depends on linalg_manim_helpers.py
# (value_to_color) being copied in above this file, and on
# llm_manim_helpers.py's color constants (ENCODER, DECODER, MECHANISM, FFN),
# font default, `_assert_font_floor`, and `assert_on_screen` above that —
# same layered-dependency convention as the format-2 mosaic header order
# (see README, "Header copy order").
#
# Generalized transformer/LLM-explanation techniques inspired by the LOGIC
# behind 3b1b's transformer videos (github.com/3b1b/videos,
# _2024/transformers/{helpers,attention,embedding,network_flow}.py) — never
# his visual identity or code verbatim: tokens as colored boxes, embeddings
# as colored-number columns, attention as a weighted grid + weighted arcs,
# architecture as stacked labeled blocks with animated data flow.


def tokenize_and_highlight(text, tokens, colors=None, font_size=20, buff=0.08):
    """Splits `text` into a row of colored boxes, one per string in `tokens`
    — the generalized "show text breaking into model-visible pieces" idea
    from 3b1b's `break_into_tokens`/`get_piece_rectangles`
    (_2024/transformers/embedding.py). `colors` defaults to a repeating
    cycle so adjacent tokens are visually distinct; pass an explicit list to
    color specific tokens (e.g. highlight one homonym across contexts)."""
    _assert_font_floor(font_size, "tokenize_and_highlight")
    palette = colors or ([MECHANISM, ENCODER, DECODER, FFN] * (len(tokens) // 4 + 1))[:len(tokens)]
    boxes = VGroup()
    for token, color in zip(tokens, palette):
        label = Text(token, font_size=font_size, color=WHITE)
        box = RoundedRectangle(corner_radius=0.06, width=label.width + 0.3, height=label.height + 0.25,
                                color=color, fill_color=color, fill_opacity=0.25)
        label.move_to(box.get_center())
        boxes.add(VGroup(box, label))
    return boxes.arrange(RIGHT, buff=buff)


def embedding_vector(values, label=None, font_size=16, max_value=None):
    """A column of decimal numbers colored by `value_to_color` —
    Manim Community's `DecimalMatrix` standing in for 3b1b's hand-rolled
    `WeightMatrix`/`NumericEmbedding` (_2024/transformers/helpers.py).
    `max_value` defaults to the largest absolute value actually in `values`
    so the color gradient always spans the data shown. NOTE: `DecimalMatrix`
    entry-styling kwargs can vary across Manim Community releases — verify
    against whatever version the render service runs (see README,
    "Verifying against the render service") before trusting this in a real
    render, same caveat already documented for styled_code_block()."""
    _assert_font_floor(font_size, "embedding_vector")
    values = np.array(values, dtype=float).reshape(-1, 1)
    scale = max_value if max_value is not None else max(float(np.abs(values).max()), 1e-6)
    matrix = DecimalMatrix(values, element_to_mobject_config={"num_decimal_places": 1, "font_size": font_size})
    for entry, value in zip(matrix.get_entries(), values.flatten()):
        entry.set_color(value_to_color(value, max_value=scale))
    if label is None:
        return matrix
    _assert_font_floor(font_size, "embedding_vector label")
    text = Text(label, font_size=font_size, color=WHITE)
    text.next_to(matrix, UP, buff=0.2)
    return VGroup(matrix, text)


def embedding_space_3d(vectors, labels, colors=None, axis_length=4):
    """Builds a 3D axes with one labeled Arrow per vector in `vectors` (each
    an (x, y, z) coordinate — the caller reduces a real high-dim embedding
    to 3D first, e.g. via PCA/`np.linalg.svd`, matching 3b1b's
    `get_principle_components`, _2024/transformers/embedding.py). Requires
    the scene to be a `ThreeDScene`. Returns (axes, VGroup of labeled
    vector-arrow groups) — pass two of the returned arrows' coordinates into
    `vector_arithmetic_demo` below."""
    axes = ThreeDAxes(x_range=[-axis_length, axis_length], y_range=[-axis_length, axis_length],
                       z_range=[-axis_length, axis_length])
    colors = colors or [MECHANISM] * len(vectors)
    arrows = VGroup()
    for coords, label, color in zip(vectors, labels, colors):
        arrow = Arrow(axes.get_origin(), axes.c2p(*coords), color=color, buff=0)
        text = Text(label, font_size=20, color=color)
        text.next_to(arrow.get_end(), UR, buff=0.05)
        arrows.add(VGroup(arrow, text))
    return axes, arrows


def vector_arithmetic_demo(scene, axes, v1, v2, v3, result_color=MECHANISM, run_time=2):
    """Animates `v1 + v2` geometrically (head-to-tail) on `axes` and compares
    it against the true `v3` — the "semantic vector arithmetic" beat from
    3b1b's `KingQueenExample` (_2024/transformers/embedding.py, e.g.
    king - man + woman ~= queen). `v1`/`v2`/`v3` are (x, y, z) coordinate
    tuples in `axes` space; any gap between "predicted" (v1+v2) and "actual"
    (v3, dashed) stays visible on screen rather than being hidden."""
    a1 = Arrow(axes.get_origin(), axes.c2p(*v1), color=ENCODER, buff=0)
    a2 = Arrow(axes.c2p(*v1), axes.c2p(*(np.array(v1) + np.array(v2))), color=DECODER, buff=0)
    predicted = Arrow(axes.get_origin(), axes.c2p(*(np.array(v1) + np.array(v2))), color=result_color, buff=0)
    actual = DashedVMobject(Arrow(axes.get_origin(), axes.c2p(*v3), color=WHITE, buff=0))
    scene.play(GrowArrow(a1), run_time=run_time / 2)
    scene.play(GrowArrow(a2), run_time=run_time / 2)
    scene.play(TransformFromCopy(VGroup(a1, a2), predicted), run_time=run_time)
    scene.play(Create(actual))
    return VGroup(a1, a2, predicted, actual)


def attention_grid(weights, row_labels, col_labels, color=MECHANISM, cell_size=0.9, font_size=16):
    """A grid of squares whose fill_opacity is each cell's attention weight
    (0-1), with row/column token labels — the exact generalized pattern
    behind 3b1b's attention-heatmap beats (_2024/transformers/attention.py),
    already hand-rolled once in this repo's own scenes/llms/00_overview.py;
    this replaces that copy-pasted block with a single call. `weights` is a
    list of rows of floats in [0, 1]."""
    _assert_font_floor(font_size, "attention_grid")
    grid = VGroup()
    for i, row in enumerate(weights):
        for j, w in enumerate(row):
            cell = Square(side_length=cell_size, color=color, fill_color=color, fill_opacity=w, stroke_width=1)
            cell.move_to(RIGHT * j * cell_size + DOWN * i * cell_size)
            grid.add(cell)
    grid.move_to(ORIGIN)
    row_group = VGroup(*[Text(t, font_size=font_size, color=GRAY_B) for t in row_labels])
    row_group.arrange(DOWN, buff=cell_size - 0.35).next_to(grid, LEFT, buff=0.35)
    col_group = VGroup(*[Text(t, font_size=font_size, color=GRAY_B) for t in col_labels])
    col_group.arrange(RIGHT, buff=cell_size - 0.35).next_to(grid, UP, buff=0.35)
    heatmap = VGroup(grid, row_group, col_group)
    assert_on_screen(heatmap, "attention_grid")
    return heatmap


def attention_arcs(sources, targets, strengths, color=MECHANISM, max_stroke_width=5, path_arc=PI / 3):
    """Returns curved-arc Lines from each source to its matching target,
    stroke width/opacity proportional to `strengths` (0-1) — the generalized
    "which tokens is this one attending to" idea from 3b1b's
    `ContextAnimation` (_2024/transformers/helpers.py), as a static VGroup
    here (wrap individual arcs in `ShowPassingFlash` at the call site, same
    as `pulse_edges` in neural_net_manim_helpers.py, for an animated flow
    instead of a static weighted-arc diagram)."""
    arcs = VGroup()
    for source, target, strength in zip(sources, targets, strengths):
        arc = ArcBetweenPoints(source.get_center(), target.get_center(), angle=path_arc)
        arc.set_stroke(color=color, width=max_stroke_width * float(np.clip(strength, 0, 1)),
                        opacity=float(np.clip(strength, 0.15, 1)))
        arcs.add(arc)
    return arcs


def model_block(title, width=2.2, height=1.4, color=MECHANISM, font_size=18):
    """A single labeled rectangle representing one layer/module in an
    architecture diagram — the 2D analogue of 3b1b's 3D `get_block()`
    (_2024/transformers/network_flow.py), kept flat/2D since every scene in
    this repo (outside `embedding_space_3d` above) is a plain `Scene`, not
    `ThreeDScene`."""
    _assert_font_floor(font_size, "model_block")
    box = RoundedRectangle(corner_radius=0.1, width=width, height=height, color=color,
                            fill_color=color, fill_opacity=0.25)
    label = Text(title, font_size=font_size, color=WHITE)
    if label.width > width - 0.3:
        label.scale_to_fit_width(width - 0.3)
    label.move_to(box.get_center())
    return VGroup(box, label)


def stack_blocks(blocks, direction=UP, offset=0.35, buff=0.5):
    """Arranges `blocks` (from `model_block`) in a column with each one
    shifted by `offset` perpendicular to `direction`, faking depth without a
    real 3D scene — the flattened analogue of 3b1b's z-offset layer stacking
    in `get_next_layer_array` (_2024/transformers/network_flow.py)."""
    perp = np.array([direction[1], -direction[0], 0])
    group = VGroup()
    for i, block in enumerate(blocks):
        block.shift(direction * i * buff + perp * i * offset)
        group.add(block)
    return group


def flow_arrow(source, target, color=WHITE, animated=True, run_time=1.0):
    """An Arrow (or, if `animated`, a `GrowArrow` Animation) from `source` to
    `target` — the generic "data flows from this block to that one" edge for
    architecture diagrams, matching 3b1b's arrow-based data-flow shots in
    `network_flow.py`. Pass the result straight to `scene.play(...)` when
    `animated=True`; otherwise it's a plain Mobject to `.add()`."""
    start = source.get_bottom() if hasattr(source, "get_bottom") else source
    end = target.get_top() if hasattr(target, "get_top") else target
    arrow = Arrow(start, end, color=color, buff=0.1)
    return GrowArrow(arrow, run_time=run_time) if animated else arrow
from manim import *

# ANOTHER copy-paste header. Depends on chart_manim_helpers.py's
# styled_code_block() being copied in above this file if used, and on
# llm_manim_helpers.py's font default/`_assert_font_floor` above that — same
# layered-dependency convention as transformer_viz_manim_helpers.py.
#
# Bridges a diagram to the code/data-structure it corresponds to: syncing a
# code-line highlight with a diagram beat, and animating a tensor's shape as
# it reshapes/transposes. Not drawn from a single 3b1b video — it follows
# the same "morph, don't cut" transition logic found across his work (see
# README, "Visual-explanation toolkit") applied to the code/programming half
# of explaining a paper, which the math-focused helpers elsewhere in this
# toolkit don't cover.


def highlight_code_lines(code_block, line_range, color=MECHANISM):
    """Returns a SurroundingRectangle around lines `line_range` (a
    `(start, end)` tuple, 0-indexed, end exclusive) of a
    `styled_code_block()`/`Code` mobject — the "point at the line being
    discussed" idiom, generalized so it isn't hand-rolled per scene.
    NOTE: `.code_lines` is the Code mobject's line-grouping attribute as of
    the version verified 2026-08-22 against the actual render service (an
    older/different Manim Community release used `.code` instead) — same
    caveat already documented for styled_code_block() in
    chart_manim_helpers.py. Re-verify if this starts failing again."""
    start, end = line_range
    return SurroundingRectangle(code_block.code_lines[start:end], color=color, buff=0.08)


def sync_code_with_diagram(scene, code_block, line_range, diagram_anim, color=MECHANISM, run_time=1.5):
    """Plays a code-line highlight and a diagram animation in the SAME
    `self.play` call — never sequentially — matching the "bundle the
    content change into one beat" transition convention this toolkit
    follows throughout (see README, "Visual-explanation toolkit"). Returns
    the highlight rectangle so the caller can fade it out later."""
    rect = highlight_code_lines(code_block, line_range, color=color)
    scene.play(Create(rect), diagram_anim, run_time=run_time)
    return rect


def tensor_shape_blocks(shape, labels=None, color=ENCODER, unit=0.5, font_size=16):
    """Represents a tensor's shape as a row of labeled blocks, one per
    dimension (e.g. `shape=(batch, seq_len, d_model)` -> 3 blocks sized/
    labeled accordingly) — a generic, code-adjacent counterpart to the
    matrix/embedding visuals elsewhere in this toolkit, for explaining a
    reshape/transpose/concat op without drawing every individual number."""
    _assert_font_floor(font_size, "tensor_shape_blocks")
    labels = labels or [str(d) for d in shape]
    blocks = VGroup()
    for dim, label_text in zip(shape, labels):
        width = max(0.8, unit * np.log2(dim + 1))
        box = RoundedRectangle(corner_radius=0.06, width=width, height=0.9, color=color,
                                fill_color=color, fill_opacity=0.25)
        text = Text(label_text, font_size=font_size, color=WHITE)
        if text.width > width - 0.2:
            text.scale_to_fit_width(width - 0.2)
        text.move_to(box.get_center())
        blocks.add(VGroup(box, text))
    return blocks.arrange(RIGHT, buff=0.15)


def reshape_animation(scene, blocks, new_shape, new_labels=None, run_time=1.5):
    """Animates `blocks` (from `tensor_shape_blocks`) morphing into a new
    arrangement matching `new_shape` — `Transform`s the same block mobjects
    into their new sizes/positions rather than fading old ones out and new
    ones in, following the "morph, don't cut" convention this toolkit
    follows throughout. Handles a different number of dimensions too (a real
    reshape usually merges or splits axes, e.g. `(batch, seq, d_model)` ->
    `(batch, seq * d_model)`): the trailing old blocks merge into the last
    new block, or the last old block splits into the trailing new blocks.
    Returns the new block group."""
    new_blocks = tensor_shape_blocks(new_shape, labels=new_labels, color=blocks[0][0].get_color())
    new_blocks.move_to(blocks.get_center())
    old_n, new_n = len(blocks), len(new_blocks)
    if old_n == new_n:
        anims = [ReplacementTransform(old, new) for old, new in zip(blocks, new_blocks)]
    elif old_n > new_n:
        anims = [ReplacementTransform(old, new) for old, new in zip(blocks[:new_n - 1], new_blocks[:new_n - 1])]
        anims.append(ReplacementTransform(VGroup(*blocks[new_n - 1:]), new_blocks[new_n - 1]))
    else:
        anims = [ReplacementTransform(old, new) for old, new in zip(blocks[:old_n - 1], new_blocks[:old_n - 1])]
        anims.append(ReplacementTransform(blocks[old_n - 1].copy(), VGroup(*new_blocks[old_n - 1:])))
        anims.append(FadeOut(blocks[old_n - 1]))
    scene.play(*anims, run_time=run_time)
    return new_blocks


def transpose_animation(scene, blocks, dims, run_time=1.5):
    """Animates `blocks` (from `tensor_shape_blocks`) swapping the on-screen
    positions of the two dimensions named by the `(i, j)` index pair `dims`
    — a special case of the reshape idea above for the specific "swap two
    axes" op, so the caller doesn't have to hand-build the reordered shape/
    labels themselves. Mutates `blocks`' ordering in place and returns it."""
    i, j = dims
    pos_i, pos_j = blocks[i].get_center().copy(), blocks[j].get_center().copy()
    scene.play(blocks[i].animate.move_to(pos_j), blocks[j].animate.move_to(pos_i), run_time=run_time)
    blocks[i], blocks[j] = blocks[j], blocks[i]
    return blocks




class VisualToolkitDemo(Scene):
    """Synthetic proof-of-concept for the visual-explanation toolkit (see
    README, "Visual-explanation toolkit") — exercises all 4 new helper files
    together: tokenize -> embedding -> attention -> matrix product -> neuron
    activation -> code synced with a tensor reshape. Not a real paper
    explanation; a template + render-service validation for the toolkit
    itself."""

    def construct(self):
        # --- 1. Tokenize ---
        c1 = callout("Passo 1: o texto vira tokens", color=MECHANISM)
        self.play(FadeIn(c1))
        tokens = tokenize_and_highlight("O gato dormiu", ["O", "gato", "dormiu"], font_size=24)
        assert_on_screen(tokens, "demo tokens")
        self.play(FadeIn(tokens))
        self.wait(2)
        self.play(FadeOut(c1), FadeOut(tokens))

        # --- 2. Embedding vector ---
        c2 = callout("Passo 2: cada token vira um vetor de embedding", color=ENCODER)
        self.play(FadeIn(c2))
        emb = embedding_vector([1.2, -0.4, 0.9, -1.6, 0.1], label="embedding(\"gato\")", font_size=18)
        assert_on_screen(emb, "demo embedding")
        self.play(FadeIn(emb))
        self.wait(2)
        self.play(FadeOut(c2), FadeOut(emb))

        # --- 3. Attention grid ---
        c3 = callout("Passo 3: atenção entre os tokens", color=MECHANISM)
        self.play(FadeIn(c3))
        weights = [
            [0.7, 0.2, 0.1],
            [0.1, 0.8, 0.1],
            [0.2, 0.3, 0.5],
        ]
        heatmap = attention_grid(weights, ["O", "gato", "dormiu"], ["O", "gato", "dormiu"], font_size=18)
        self.play(FadeIn(heatmap))
        arcs = attention_arcs(
            [heatmap[0][0], heatmap[0][3]],
            [heatmap[0][4], heatmap[0][8]],
            [0.7, 0.5],
        )
        self.play(*[Create(a) for a in arcs])
        self.wait(2)
        self.play(FadeOut(c3), FadeOut(heatmap), FadeOut(arcs))

        # --- 4. Matrix-vector product ---
        c4 = callout("Passo 4: produto matriz-vetor (ex: projeção Q)", color=MECHANISM)
        self.play(FadeIn(c4))
        m = DecimalMatrix([[0.5, -0.2], [0.1, 0.9]], element_to_mobject_config={"num_decimal_places": 1})
        v = DecimalMatrix([[1.0], [0.5]], element_to_mobject_config={"num_decimal_places": 1})
        eq_group = VGroup(m, v).arrange(RIGHT, buff=0.6)
        assert_on_screen(eq_group, "demo matrix-vector")
        self.play(FadeIn(eq_group))
        matrix_vector_product_animation(self, m, v)
        self.wait(1)
        self.play(FadeOut(c4), FadeOut(eq_group))

        # --- 5. Neuron activation + signal flash ---
        c5 = callout("Passo 5: ativação se propagando por uma rede", color=FFN)
        self.play(FadeIn(c5))
        network, layers, edge_groups = build_network([3, 4, 2])
        network.move_to(ORIGIN)
        assert_on_screen(network, "demo network")
        self.play(FadeIn(network))
        activate_layer(layers[0], [0.9, 0.3, 0.6])
        self.play(*[layers[0][i].animate.set_fill(opacity=v) for i, v in enumerate([0.9, 0.3, 0.6])])
        self.play(pulse_edges(edge_groups[0]))
        activate_layer(layers[1], [0.4, 0.8, 0.2, 0.5])
        self.play(*[layers[1][i].animate.set_fill(opacity=v) for i, v in enumerate([0.4, 0.8, 0.2, 0.5])])
        self.wait(1)
        self.play(FadeOut(c5), FadeOut(network))

        # --- 6. Code synced with a tensor reshape ---
        c6 = callout("Passo 6: o código e a estrutura de dados lado a lado", color=DECODER)
        self.play(FadeIn(c6))
        code = styled_code_block("x = x.reshape(batch, seq_len * d_model)", font_size=16)
        code.to_edge(UP, buff=1.2)
        blocks = tensor_shape_blocks((8, 32, 64), labels=["batch", "seq_len", "d_model"])
        blocks.next_to(code, DOWN, buff=0.8)
        group = VGroup(code, blocks)
        assert_on_screen(group, "demo code + tensor blocks")
        self.play(FadeIn(code), FadeIn(blocks))
        rect = sync_code_with_diagram(self, code, (0, 1), Indicate(blocks), color=DECODER)
        self.wait(0.5)
        self.play(FadeOut(rect))
        reshape_animation(self, blocks, (8, 2048), new_labels=["batch", "seq_len * d_model"])
        self.wait(2)
        self.play(FadeOut(c6), FadeOut(code), FadeOut(blocks))
