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
