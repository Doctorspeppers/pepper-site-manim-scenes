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
