from manim import *

# SECOND copy-paste header for the accumulating-mosaic video format (see
# README.md, "Video format 2"). A scene using this format copies
# llm_manim_helpers.py's full contents first (colors, fonts, terminal_box,
# sized_box, callout, assert_no_overlap, ...), then this file's full contents
# appended below it — the functions here assume WHITE / GRAY_D /
# assert_no_overlap already exist from that first header.
#
# This is the one place in the repo that uses a moving camera
# (MovingCameraScene / self.camera.frame) — every scene in scenes/llms/ and
# scenes/vlms/ stays a plain Scene. That is a deliberate, scoped exception
# for this new format, not a new repo-wide rule.
#
# Camera model: the camera stays FIXED, tightly framed on workspace_zone()
# for the entire main build loop — archived beats live in mosaic_strip()'s
# slots, positioned deliberately OUTSIDE that tight frame, so a beat visibly
# disappears off-screen as archive_to_slot() sends it there, while the next
# beat builds in the now-empty workspace still in view. zoomout_reveal() is
# the ONLY camera move in the whole scene: one widen at the very end that
# brings every archived beat back into view at once, alongside the last
# beat still in the workspace.


def workspace_zone(width=12.8, height=5.2, y_shift=1.1):
    """Rectangle marking the fixed region where the CURRENT beat is built —
    deliberately close to safe_container()'s own default height (5.4),
    since a beat in this format is the same kind of content safe_container()
    already bounds comfortably today. Draw once, as a faint outline, at the
    top of construct(); every beat's own diagram is placed/asserted
    relative to it exactly like beats in the existing per-paper format use
    safe_container()."""
    return RoundedRectangle(corner_radius=0.15, width=width, height=height,
                             color=GRAY_D, stroke_width=1.0, stroke_opacity=0.35).shift(UP * y_shift)


def enter_workspace(camera_frame, workspace, margin=1.0):
    """Sets camera_frame to a tight, FIXED framing around `workspace` plus a
    small margin — call this once at the start of construct(), right after
    building workspace_zone() and before the first beat. This is an instant
    jump (not animated — nothing archived exists yet to cut away from), and
    it's the frame the camera returns to and stays at for the entire main
    loop. mosaic_strip()'s slots must sit fully outside this frame (see its
    own docstring) so archived beats are genuinely off-screen until
    zoomout_reveal().

    Resizes via ONE uniform `.scale()` (never separate `.set(width=...)`
    then `.set(height=...)` calls): each of those individually rescales the
    frame proportionally to hit ONE target dimension, so a second call
    aimed at the other dimension silently undoes the first and leaves
    camera_frame's aspect ratio no longer matching the render's fixed pixel
    output — a real distortion bug, not just an approximation. Taking the
    larger of the two required per-axis scale factors and applying it once
    guarantees both the required width AND height are met while preserving
    the frame's original aspect ratio exactly. zoomout_reveal() uses the
    same approach."""
    scale = max((workspace.width + margin * 2) / camera_frame.width,
                (workspace.height + margin * 2) / camera_frame.height)
    camera_frame.scale(scale).move_to(workspace.get_center())


def mosaic_strip(n_slots, width=13.2, height=1.7, y_shift=4.2, gap=0.25):
    """Precomputes n_slots equal-size, invisible Rectangle placeholders in
    one row, positioned well below workspace_zone() — specifically below
    enter_workspace()'s tight frame, not just below workspace_zone() itself,
    so the strip stays fully off-screen during the main build loop and only
    enters view via zoomout_reveal(). With the default workspace_zone()
    (height=5.2, y_shift=1.1) and enter_workspace() margin=1.0, the tight
    frame's bottom edge sits at y=-2.5; y_shift=4.2 puts this strip's top
    edge at y=-3.35, comfortably below that. If workspace_zone()'s size or
    enter_workspace()'s margin change, re-check this clearance (a failing
    assert_within_camera() on the FIRST beat, before anything is archived,
    is the tell that a slot is poking into the tight frame). n_slots is
    decided up front by the scene author — simply len(BEATS) (see README) —
    and never recomputed at runtime, so archive_to_slot() always has one
    pre-known destination per beat."""
    slot_w = (width - gap * (n_slots - 1)) / n_slots
    slots = VGroup(*[Rectangle(width=slot_w, height=height, stroke_opacity=0) for _ in range(n_slots)])
    slots.arrange(RIGHT, buff=gap).shift(DOWN * y_shift)
    return slots


def archive_to_slot(scene, beat_group, slot, run_time=1.2):
    """Shrinks+moves `beat_group` (the just-finished beat's live VGroup —
    never FadeOut) into `slot`'s footprint. Deliberately does NOT touch the
    camera: `slot` lives outside the tight workspace frame enter_workspace()
    set up, so this animation visibly carries the beat off-screen as it
    heads to its slot — "disappearing" while the next beat builds in the
    now-empty workspace. zoomout_reveal() is what brings every archived
    beat back into view, all at once, at the end.

    Shrinking archived text below this repo's "never scale text to fit a
    box" floor (see sized_box() in llm_manim_helpers.py) is a deliberate,
    scoped exception: that rule protects content while it's the active,
    being-read beat. Once archived, a beat is a recognizable thumbnail
    marker, not something meant to be read letter-by-letter — do not "fix"
    this by un-shrinking archived slots."""
    scale = min(slot.width / beat_group.width, slot.height / beat_group.height)
    scene.play(beat_group.animate.scale(scale).move_to(slot.get_center()), run_time=run_time)


def zoomout_reveal(scene, camera_frame, mosaic_group, run_time=2.5):
    """The one camera move in the whole scene: widens/recenters camera_frame
    to frame the ENTIRE mosaic_group (workspace + all slots) with margin —
    the moment every beat sent off-screen by archive_to_slot() comes back
    into view together. Computes the target from mosaic_group's actual
    bounding box rather than any fixed guess, so it works regardless of how
    many beats/slots were archived or how far below the tight frame
    mosaic_strip() placed them. Uses the same single-uniform-scale approach
    as enter_workspace() (max of the two required per-axis factors, one
    `.scale()` call) to grow the frame without distorting its aspect
    ratio."""
    scale = max((mosaic_group.width + 1.2) / camera_frame.width,
                (mosaic_group.height + 1.2) / camera_frame.height)
    camera_frame.generate_target()
    camera_frame.target.scale(scale).move_to(mosaic_group.get_center())
    scene.play(MoveToTarget(camera_frame), run_time=run_time)


def assert_within_camera(inner, camera_frame, label=""):
    """Camera-aware sibling of assert_on_screen() (llm_manim_helpers.py):
    fails loudly if `inner`'s bounding box extends past the LIVE
    camera_frame's current bounding box, instead of the static
    config.frame_width/frame_height. Use this for every beat, since
    enter_workspace() puts the camera in a non-default tight frame before
    the first beat even builds — assert_on_screen() (checked against the
    static default frame) is only valid for content built before
    enter_workspace() runs (e.g. an opening title card). assert_no_overlap()
    and assert_within() need no camera-aware equivalent: they compare two
    groups' bboxes to each other, independent of any frame."""
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
