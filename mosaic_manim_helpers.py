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


def workspace_zone(width=12.8, height=5.2, y_shift=1.1):
    """Rectangle marking the fixed region (in the scene's default coordinate
    system) where the CURRENT beat is built — deliberately close to
    safe_container()'s own default height (5.4), since a beat in this format
    is the same kind of content safe_container() already bounds comfortably
    today. Draw once, as a faint outline, at the top of construct(); every
    beat's own diagram is placed/asserted relative to it exactly like beats
    in the existing per-paper format use safe_container()."""
    return RoundedRectangle(corner_radius=0.15, width=width, height=height,
                             color=GRAY_D, stroke_width=1.0, stroke_opacity=0.35).shift(UP * y_shift)


def mosaic_strip(n_slots, width=13.2, height=1.7, y_shift=3.0, gap=0.25):
    """Precomputes n_slots equal-size, invisible Rectangle placeholders in
    one row below workspace_zone(). n_slots is decided up front by the scene
    author — simply len(BEATS) (see README) — and never recomputed at
    runtime, so archive_to_slot() always has one pre-known destination per
    beat."""
    slot_w = (width - gap * (n_slots - 1)) / n_slots
    slots = VGroup(*[Rectangle(width=slot_w, height=height, stroke_opacity=0) for _ in range(n_slots)])
    slots.arrange(RIGHT, buff=gap).shift(DOWN * y_shift)
    return slots


def archive_to_slot(scene, camera_frame, beat_group, slot, workspace, filled_slots, run_time=1.4):
    """Shrinks+moves `beat_group` (the just-finished beat's live VGroup —
    never FadeOut) into `slot`'s footprint, while widening/recentering
    `camera_frame` in the SAME self.play so the workspace + every
    already-filled slot + this new one stay comfortably framed. Mutates
    beat_group in place and appends it to `filled_slots`.

    camera_frame.set(width=...) / .set(height=...) each scale the frame
    uniformly (aspect-ratio preserving), so setting width then conditionally
    growing height never distorts the shot — it just grows the frame enough
    to satisfy whichever dimension needs more room.

    Shrinking archived text below this repo's "never scale text to fit a
    box" floor (see sized_box() in llm_manim_helpers.py) is a deliberate,
    scoped exception: that rule protects content while it's the active,
    being-read beat. Once archived, a beat is a recognizable thumbnail
    marker, not something meant to be read letter-by-letter — do not "fix"
    this by un-shrinking archived slots."""
    scale = min(slot.width / beat_group.width, slot.height / beat_group.height)
    beat_group.generate_target()
    beat_group.target.scale(scale).move_to(slot.get_center())

    camera_frame.generate_target()
    visible = VGroup(workspace, *filled_slots, slot)
    camera_frame.target.set(width=max(visible.width + 1.0, camera_frame.width))
    if camera_frame.target.height < visible.height + 1.0:
        camera_frame.target.set(height=visible.height + 1.0)
    camera_frame.target.move_to(visible.get_center())

    scene.play(MoveToTarget(beat_group), MoveToTarget(camera_frame), run_time=run_time)
    filled_slots.append(beat_group)


def zoomout_reveal(scene, camera_frame, mosaic_group, run_time=2.5):
    """Final wide shot: widens/recenters camera_frame to frame the ENTIRE
    mosaic_group (workspace + all filled slots) with margin. Deliberately
    does NOT use Restore(camera_frame) after a save_state() — that only
    returns to whatever was captured at the very start of construct(),
    which is "big enough" only by coincidence if the mosaic never grew past
    the default frame. This computes the target from mosaic_group's actual
    bounding box instead, so it works regardless of how many beats/slots
    were archived. (Restore() is still a legitimate simpler alternative in
    a scene where the author knows for certain the mosaic stays within the
    default frame — but this generic helper is the one to reach for by
    default.)"""
    camera_frame.generate_target()
    camera_frame.target.set(width=mosaic_group.width + 1.2)
    if camera_frame.target.height < mosaic_group.height + 1.2:
        camera_frame.target.set(height=mosaic_group.height + 1.2)
    camera_frame.target.move_to(mosaic_group.get_center())
    scene.play(MoveToTarget(camera_frame), run_time=run_time)


def assert_within_camera(inner, camera_frame, label=""):
    """Camera-aware sibling of assert_on_screen() (llm_manim_helpers.py):
    fails loudly if `inner`'s bounding box extends past the LIVE
    camera_frame's current bounding box, instead of the static
    config.frame_width/frame_height. Use this instead of assert_on_screen()
    for every beat after the first, since the camera stops being in its
    default state the moment archive_to_slot() runs once —
    assert_on_screen() only stays valid for content built before the camera
    has moved (e.g. an opening title card). assert_no_overlap() and
    assert_within() need no camera-aware equivalent: they compare two
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
