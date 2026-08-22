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
