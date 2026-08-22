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
