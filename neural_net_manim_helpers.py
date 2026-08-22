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
