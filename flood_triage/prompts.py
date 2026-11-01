"""Prompts for Muse Spark Open. Levels follow STURM-FloodDepth (water height relative to vehicle parts)."""

# v0 definitions (my own wording, used for the zero-shot run)
LEVELS_V0 = {
    0: "no water, or only wet ground; water below the bottom of the tyres",
    1: "water up to roughly half the tyre height",
    2: "water up to the top of the tyre / bottom of the door",
    3: "water above the door bottom, up to the bottom of the windows (body submerged)",
    4: "water at or above the window line",
}
# Official definitions from the STURM-FloodDepth paper (Notarangelo et al., 2025), following Wan et al. (2024)
LEVELS = {
    0: "not flooded (dry or only wet road surface)",
    1: "water below half of the tyre height, below the chassis",
    2: "water between half and the whole tyre height, between the chassis and the front marker lights / trunk",
    3: "water between the top of the tyre and the side window, between the front marker lights and the windscreen",
    4: "water above the bottom of the side window, or above the front/rear windscreen",
}
LEVEL_NAMES = {0: "Not flooded", 1: "Below half tyre", 2: "Half to full tyre", 3: "Tyre to window", 4: "Window or above"}

_DEFS_V0 = "; ".join(f"{k} = {v}" for k, v in LEVELS_V0.items())
_DEFS = "; ".join(f"{k} = {v}" for k, v in LEVELS.items())

ZERO_SHOT = (
    "This is a cropped street photo of a vehicle during urban flooding. Classify the floodwater level "
    f"against the vehicle: {_DEFS_V0}. If the waterline or vehicle is not visible enough, answer X. "
    "Reply only as: LEVEL=<0-4 or X>; EVIDENCE=<which vehicle part the waterline touches, max 12 words>"
)

STRUCTURED = (
    "You are auditing a citizen flood report. The photo is a crop around one vehicle in a flooded street.\n"
    "Work in this order:\n"
    "1. Identify the vehicle type and which of its parts are visible (tyres, wheel arch, door bottom, door, window).\n"
    "2. Locate the waterline: the boundary where water meets the vehicle body or wheels. Reflections, wet "
    "paint and puddles on the road are not a waterline.\n"
    "3. Name the highest vehicle part the water reaches.\n"
    f"4. Map it to a level: {_DEFS}.\n"
    "If no vehicle or no waterline can be seen (blur, darkness, occlusion, too small), answer X instead of guessing. A clearly visible vehicle with no water on it is level 0, not X.\n"
    "Final answer on the last line only, exactly:\n"
    "LEVEL=<0-4 or X>; CONFIDENCE=<high|medium|low>; PART=<part the waterline touches>; "
    "EVIDENCE=<what you see, max 15 words>"
)

FEWSHOT_INTRO = (
    "Reference examples from a labelled training set follow, one per level. Use them to calibrate where each "
    "level begins. Then classify the final photo."
)
