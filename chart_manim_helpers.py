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
    across Manim Community releases — verify `code=`/`code_string=`/
    `file_name=` and `background=` against whatever version the render
    service actually runs (see README, "Verifying against the render
    service") before relying on this in a real render."""
    return Code(code=src, language=language, font_size=font_size,
                background="rectangle", tab_width=2, **kwargs)


# Not implemented in this module: a node/edge diagram helper (circles for
# nodes, edges colored/weighted by relationship strength) inspired by
# 3b1b's hand-rolled NetworkMobject (github.com/3b1b/videos,
# _2017/nn/part1.py / helpers.py). Valuable for both ML architecture
# diagrams and cybersecurity attack-graph visuals, but left as a documented
# future extension rather than built speculatively here.
