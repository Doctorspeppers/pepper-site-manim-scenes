# pepper-site-manim-scenes

Manim (Community Edition, Python) scene sources for the AI-architectures explainer
video series published on [pepper.dev.br](https://pepper.dev.br)'s tech blog. Each
scene is the video companion to a blog post covering a landmark paper's architecture.

Currently live: **`scenes/llms/`** — 9 scenes covering the lineage of LLM
architectures, written for the post *"Do Transformer aos modelos sem atenção: a
linhagem dos LLMs"*:

| File | Paper / architecture |
|---|---|
| `01_transformer.py` | Transformer ("Attention Is All You Need") |
| `02_gpt.py` | GPT |
| `03_bert.py` | BERT |
| `04_llama.py` | LLaMA |
| `05_mistral.py` | Mistral / Mixtral |
| `06_deepseek.py` | DeepSeek-V3 / R1 |
| `07_palm.py` | PaLM / Gemini |
| `08_mamba.py` | Mamba |
| `09_rwkv.py` | RWKV |

More groups are planned as separate subdirectories under `scenes/` — e.g. VLMs,
JEPA, generative models, self-supervised learning, GNNs, world-models/RL — each
following the same one-file-per-scene layout as `scenes/llms/`.

**`scenes/vlms/`** and **`scenes/jepa/`** are also live. `scenes/jepa/00_overview.py`
is the reference example for a new standard: every future group should open with
one long-form (~5 minutes), deeply explanatory overview scene — inserted before
its group's per-paper deep dives — built in a 3Blue1Brown-influenced style: real
plotted graphs (`Axes`/`.plot()`, `BarChart`) instead of only box diagrams, the
actual math in `MathTex` with individual terms highlighted and explained one at a
time (build multi-term formulas as several `MathTex(...)` string arguments so each
term is a safely indexable submobject — never slice a single compiled `MathTex` by
guessed character offsets), and at least one worked numeric example plugging real
numbers into a real formula. Length comes from genuine added depth (more real
beats, doubled hold times), not padding.

## Render pipeline, and why every scene file is self-contained

Scenes are rendered by an internal-only render service that accepts exactly one
self-contained Python script per scene (a single `sceneCode` string) and runs it
roughly as:

```
manim render -qm <script>.py <SceneName>
```

`-qm` = medium quality, **720p30**. The service's container has `Fira Code` and
`URW Gothic` installed as fonts, but nothing else beyond Manim itself — no package
installation step, and no support for relative/local imports. That means a scene
script cannot `import llm_manim_helpers` even though every scene in this repo uses
the exact same helpers.

**`llm_manim_helpers.py` (at the repo root) is the canonical source of that shared
header** — the color constants, font setup, and layout helpers below. It is never
imported at render time. Instead, when a new scene is written, its full contents are
copied verbatim into the top of the new scene file, and the `class YourScene(Scene):
def construct(self): ...` body is written underneath using those names. Every file
in `scenes/llms/` duplicates this header on purpose, byte-for-byte, at render time —
**this is intentional and required by the render service's API, not an oversight.
Do not "fix" it by turning any scene's header into a real `import
llm_manim_helpers` — that import will not exist in the render container and the
render will fail.**

`llm_manim_helpers.py` is kept in sync with what's actually copied into scenes by
hand — if a helper changes, it's updated here first and then re-copied into
whichever scene files need the change.

## Shared visual identity

### Color language

One consistent color meaning is used across every scene in the series, so a viewer
who has seen one video already reads color in every later one:

| Color | Meaning |
|---|---|
| `BLUE` (`ENCODER`) | encoder / bidirectional path |
| `ORANGE` (`DECODER`) | decoder / autoregressive path |
| `YELLOW` (`MECHANISM`) | the paper's core novel mechanism (attention, selective state, etc.) |
| `GREEN` (`FFN`) | feed-forward / MLP / expert layers |
| `PURPLE` (`NORM`) | normalization |
| `PINK` (`POSITION`) | positional information |
| `RED` (`OUTPUT`) | output / logits / prediction |
| `GRAY` (`OLD`) | older-generation component being replaced |

### Fonts

- **URW Gothic** — the default body/label font, set globally via
  `Text.set_default(font="URW Gothic")`. It's a geometric sans with heavier,
  simpler strokes than alternatives that were tried (Noto Sans, P052, Nimbus Roman).
- **Fira Code** — reserved for terminal-style code mockups (`terminal_box()`, via
  `_mono_font()`), which passes `font=` explicitly to override the default for
  that one case.

### Why fonts and box sizing matter this much here

The render service only renders at **`-qm` = 720p30** — a fairly low resolution
for text-heavy diagrams. At that resolution, small text, or text that was scaled
down (`.scale()`/`.scale_to_fit_width()`) *after* being placed to fit a pre-picked
box, comes out with visibly uneven letter spacing — an artifact that's easy to
miss on a large development monitor but reads as broken once actually rendered at
final size. Font choice and box-sizing discipline (below) both exist specifically
to avoid that.

## Layout-safety helpers, and the rule they encode

`llm_manim_helpers.py` provides:

- **`assert_on_screen(mobj, label)`** — fails the render (with the exact
  overflowing coordinates) if a group's bounding box extends past the visible
  frame.
- **`assert_no_overlap(a, b, label)`** — fails the render (with both groups'
  exact bounding boxes) if two groups' bounding boxes intersect on screen.
- **`diagram_row(...)`** / **`stack_rows(...)`** — generic composition helpers for
  "diagram + caption" rows and vertical stacks of rows, with `stack_rows` calling
  `assert_no_overlap` on every adjacent pair automatically as part of stacking.

These encode one hard rule used throughout every scene: **box sizes are always
computed FROM the text, never the reverse.** `sized_box()`, `sized_circle()`,
`uniform_boxes()`, and `terminal_box()` all measure the rendered text first and
then size the box/circle around it with real margin — text is never shrunk after
creation to fit a box whose size was picked in advance. That's the same underlying
issue as the font notes above: shrinking text after the fact is what reintroduces
the illegible, uneven-spacing artifact at 720p.

The corollary: any group placed on screen relative to another (a caption next to a
diagram, a new row below an existing stack, etc.) should be run through
`assert_no_overlap` before the scene fades it in. That way a bad layout fails the
render loudly, with exact coordinates in stderr, instead of silently shipping a
video with overlapping or clipped elements.

### The font-size floor is now enforced in code, not just in this doc

`MIN_FONT_SIZE = 16` and `_assert_font_floor(font_size, label)` in
`llm_manim_helpers.py` make the rule above self-enforcing: `callout()`,
`terminal_box()`, `sized_box()`, `sized_circle()`, `uniform_boxes()`, and
`diagram_row()` all call `_assert_font_floor()` on every `font_size` they're
given, so passing anything below 16 fails the render immediately with an
`AssertionError` naming the offending helper — instead of silently shipping a
scene where the artifact only shows up once someone actually watches the
rendered video. This exists because the documentation alone didn't stop the bug
from recurring: the JEPA-group overview scene shipped a plain `Text(...,
font_size=13)` caption above a bar chart that rendered with visibly overlapping
letters, caught only after publishing. Prefer **`safe_caption(text, font_size=16,
max_width=12.6, ...)`** for any long running caption/note instead of the older
`if t.width > cap: t.scale_to_fit_width(cap)` pattern still visible in some
existing scenes — that pattern is exactly how a caption already at 16pt+ can
still end up shrunk below the floor once its content runs long. `safe_caption`
asserts instead of shrinking: split the text across lines with a literal `\n`
(which `Text` honors as a real line break, unlike `Tex`/`MathTex`) or shorten it.

## How to add a new scene

1. Open `llm_manim_helpers.py` and copy its **entire contents** verbatim into the
   top of your new scene file (same imports, same `Text.set_default(...)` call,
   same color constants, same helper function definitions — unchanged).
2. Below that header, write:
   ```python
   class YourSceneName(Scene):
       def construct(self):
           ...
   ```
   using the shared colors (`ENCODER`, `DECODER`, `MECHANISM`, `FFN`, `NORM`,
   `POSITION`, `OUTPUT`, `OLD`) and layout helpers (`callout`, `terminal_box`,
   `sized_box`, `sized_circle`, `uniform_boxes`, `safe_container`, `diagram_row`,
   `stack_rows`, `assert_on_screen`, `assert_no_overlap`) from the header.
3. Save the file under the appropriate `scenes/<group>/` subdirectory (e.g.
   `scenes/llms/10_something.py`, or a new `scenes/vlms/...` for a future group).
4. The whole file — header plus scene body — is what gets sent to the render
   service as one `sceneCode` string. There is nothing else to package: no
   `requirements.txt`, no local imports, no build step.

## Video format 2: accumulating-mosaic deep dives

Everything above is video format 1 — one paper, one video, beats that fade out as
they go. Format 2 is for **future, longer-form posts** (planned: LLM-internals and
cybersecurity deep dives) that need to hold several sub-topics on screen
*simultaneously* instead of one at a time. **It does not replace format 1** —
`scenes/llms/` and `scenes/vlms/` keep working exactly as documented above.

### The pattern

Instead of `self.play(FadeOut(beat_group))` between beats, a finished beat's
diagram shrinks and slides into a fixed slot in a horizontal filmstrip — but the
camera stays fixed, tightly framed on just the workspace, for the whole main
loop. Since the filmstrip's slots live outside that tight frame on purpose, a beat
visibly **disappears off-screen** as it's archived, while the next beat builds in
the now-empty workspace still in view. The video closes with one camera
pull-back — the only camera move in the whole scene — that widens to frame the
workspace *and* every archived slot at once: everything sent off-screen comes back
into view together, all at the end. This is adapted from the camera technique
3blue1brown uses for build-up/reveal sequences in
[3b1b/videos](https://github.com/3b1b/videos) (ManimGL's `self.frame`
target-animation idiom), translated to Manim Community's `MovingCameraScene` /
`self.camera.frame`.

### Header copy order

A format-2 scene copies **three** files verbatim, in this order, before its own
`BEATS`/`class ...(MovingCameraScene)` code:

1. `llm_manim_helpers.py` (colors, fonts, `callout`, `terminal_box`, `sized_box`, ...)
2. `mosaic_manim_helpers.py` (`workspace_zone`, `enter_workspace`, `mosaic_strip`,
   `archive_to_slot`, `zoomout_reveal`, `assert_within_camera`)
3. `chart_manim_helpers.py` (`styled_bar_chart`, `styled_axes`, `highlight_cell`,
   `dimension_brace`, `styled_code_block`) — only needed if the scene actually
   plots/tabulates something; still copied in full per the existing "copy the
   whole file, not just what you need" convention.

This is the **only place in the repo that uses a moving camera**
(`MovingCameraScene`) — every format-1 scene stays a plain `Scene`. That's a
deliberate, scoped exception for format 2, not a new repo-wide rule.

### Authoring convention: `BEATS`

A format-2 scene defines its content as small functions,
`beat_fn(scene, workspace) -> VGroup`, each building and animating in one beat's
diagram using the existing shared helpers (colors, `terminal_box`, `callout`,
etc.) and returning the finished group **without** fading it out. An ordered
`BEATS` list drives `construct()`:

```python
BEATS = [beat_attention, beat_decoder_stack, beat_selective_state, beat_cost_comparison]

class YourDeepDive(MovingCameraScene):
    def construct(self):
        workspace = workspace_zone()
        slots = mosaic_strip(n_slots=len(BEATS))
        assert_no_overlap(workspace, slots, "workspace vs mosaic strip")
        enter_workspace(self.camera.frame, workspace)  # tight, fixed frame for the main loop

        for i, beat_fn in enumerate(BEATS):
            beat_group = beat_fn(self, workspace)
            archive_to_slot(self, beat_group, slots[i])  # beat shrinks off-screen into its slot

        zoomout_reveal(self, self.camera.frame, VGroup(workspace, slots))  # everything comes back
```

Choosing/reordering which beats go into a given video is exactly editing this
list — that's the "pick your scenes" mechanism for this format.

**Anchor callouts to `workspace`, not to the frame edge.** `callout()` places its
text via `.to_edge(UP, ...)`, which is computed against the *static* default
frame — but `enter_workspace()` puts the camera in a smaller, non-default frame
before the first beat even builds. Reposition each beat's callout relative to
`workspace` instead (e.g. just inside its top edge), since `workspace` never moves
in world coordinates even as the camera later zooms out for the reveal. See
`_anchor_callout()` in the reference demo — and note it nests the callout
*inside* `workspace`'s top edge rather than stacking above it, which is what
`assert_within_camera()` caught failing during actual verification (see
"Verifying against the render service" below).

**Camera resizes must use one uniform `.scale()`, never separate
`.set(width=...)` / `.set(height=...)` calls.** Each of those rescales the whole
frame proportionally to hit just the one dimension given, so a second call aimed
at the other dimension silently undoes the first and leaves the frame's aspect
ratio no longer matching the render's fixed pixel output — a real distortion bug.
`enter_workspace()` and `zoomout_reveal()` both take the larger of the two
required per-axis scale factors and apply it once, which hits both minimums
without distorting anything.

### Why a horizontal strip along the bottom

The vertical axis (8 units) is already the tighter one today — `safe_container()`'s
own default height (5.4) already uses ~68% of it — so it's the right axis to
compress for the filmstrip. A side column would instead force every beat's
diagrams to be re-authored narrower, fighting the width `terminal_box`/`callout`/
`safe_container` already assume is available.

### `assert_within_camera` vs `assert_on_screen`

`assert_on_screen()` checks a group's bounding box against the *static*
`config.frame_width`/`frame_height` — correct only for content built before
`enter_workspace()` puts the camera in its (smaller, non-default) tight frame
(e.g. an opening title card). Every beat after that should be checked with
`assert_within_camera(group, scene.camera.frame, label)` instead.
`assert_no_overlap()`/`assert_within()` need no camera-aware equivalent — they
compare two groups to each other, independent of any frame.

### Reference example

`demos/lineage_of_llms_demo.py` is a working, self-contained proof-of-concept:
four beats adapted from `scenes/llms/01_transformer.py`, `02_gpt.py`, `08_mamba.py`,
and `09_rwkv.py` (attention, decoder stack, selective state, and a
`styled_bar_chart()`-based cost comparison), stitched with the `BEATS` pattern
above. It lives in `demos/`, not `scenes/`, because it's a pattern-validation
prototype, not a real episode — real format-2 posts go under
`scenes/deep_dives/` (created when the first one is written) once the pattern
has been rendered and checked against the actual render service (see
"Verifying against the render service" below).

### Verifying against the render service

Nothing in this repo pins a `manim` version, and `MovingCameraScene` is new API
surface here (no scene used a camera before format 2). Before trusting a
format-2 render:

1. Confirm which `manim` version the render service actually runs, and match it
   locally: `python3 -m venv .venv && source .venv/bin/activate && pip install
   manim==<that version>` (needs `libcairo2-dev`, `libpango1.0-dev`, `ffmpeg`,
   `pkg-config` as system deps first).
2. Confirm `URW Gothic` and `Fira Code` are actually installed locally
   (`fc-list | grep -i "urw gothic"` / `fc-list | grep -i "fira code"`) — if not,
   treat any text-width-sensitive assertion result as unverified until it's
   checked with the real fonts.
3. Fast smoke test: `manim -ql --disable_caching demos/lineage_of_llms_demo.py
   LineageOfLLMsDemo` (480p15) — watch stderr for `AssertionError`s (they print
   the exact offending coordinates).
4. Final check at the service's real quality flag: `manim -qm
   demos/lineage_of_llms_demo.py LineageOfLLMsDemo` (720p30).
5. Watch the rendered mp4 for: the active beat clipped at the camera edge, the
   filmstrip overlapping the workspace, a jump-cut instead of a smooth camera
   move in `archive_to_slot()`, or the final `zoomout_reveal()` cropping a
   filmstrip slot. Illegible text *inside an archived slot* is expected (see
   `archive_to_slot()`'s docstring) — not a bug.

## Publishing a scene for real (applies to either format)

Everything above renders against the internal render service directly — that
service isn't reachable on its own from outside the Docker network, and
nothing sent to it that way is saved anywhere. **The only path that actually
publishes a persistent, embeddable video is the `render_manim_animation` MCP
tool**, exposed by `pepper-site-back` at:

```
https://api.pepper.dev.br/mcp
```

This is OAuth 2.1 with dynamic client registration (Better Auth's `mcp`
plugin) — no API key to manage. Any MCP-capable client (Claude Desktop, this
assistant, etc.) connects to that URL, completes a normal OAuth login
(redirects through `pepper.dev.br/auth`), and gets a session-scoped token.
Logging in doesn't require an admin account, but every write the tool makes
is gated by `assertAdmin` server-side — so only the site's actual admin
account can use it to publish anything.

Calling the tool:

```json
{
  "name": "render_manim_animation",
  "arguments": {
    "name": "A short label for the scene library",
    "sceneCode": "<the full contents of the scene .py file — every copied header plus the Scene subclass, exactly what you'd hand to `manim render` locally>",
    "sceneClassName": "YourSceneName"
  }
}
```

`sceneCode` is not a snippet — it's the complete, self-contained file, same
convention as everywhere else in this repo (copy every helper header
verbatim, then the `class YourScene(...)` body underneath). Whatever you
verified locally with `manim -qm ...` is exactly what to paste in here.

What happens on the backend (`pepper-site-back/src/features/manim/
manim.controller.ts`): it renders the scene through the same internal
service documented above, stores the resulting mp4 as media, and returns a
permanent public URL —

```
https://api.pepper.dev.br/v1/public/media/<uuid>
```

— safe to embed directly in a blog post as `<video src="..." controls>`. The
scene itself is also saved to a re-editable "Manim scene library" (re-render
with edited code later without losing the history), unlike the front-end's
`/app/manim` **sandbox** page — that one only ever returns a browser-local
blob URL and saves nothing; it's for quick previews, not publishing.

This path was validated end-to-end by actually publishing
`demos/lineage_of_llms_demo.py` through it (not just rendering it locally) —
confirmed a real `https://api.pepper.dev.br/v1/public/media/...` URL
returning `200 video/mp4`.
