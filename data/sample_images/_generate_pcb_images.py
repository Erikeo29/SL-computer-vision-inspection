"""
Generate 6 realistic synthetic PCB inspection images using PIL and numpy.
This script is meant to be run once, then deleted.
"""

from __future__ import annotations

import random
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

RNG = np.random.default_rng(42)
random.seed(42)

W, H = 800, 600

# Realistic colours
PCB_GREEN_DARK = (26, 92, 26)
PCB_GREEN_MID = (35, 120, 35)
PCB_GREEN_LIGHT = (45, 140, 45)
COPPER = (184, 115, 51)
COPPER_LIGHT = (205, 145, 80)
SOLDER_SILVER = (192, 192, 192)
SOLDER_DARK = (140, 140, 140)
IC_BLACK = (30, 30, 35)
SILKSCREEN_WHITE = (230, 230, 225)
GOLD = (212, 175, 55)
GOLD_DARK = (170, 130, 30)
FLEX_TAN = (210, 165, 90)
FLEX_ORANGE = (220, 150, 60)
SUBSTRATE_WHITE = (240, 238, 232)


def add_gaussian_noise(
    img: Image.Image, mean: float = 0.0, sigma: float = 8.0
) -> Image.Image:
    """Add Gaussian noise to make images look realistic."""
    arr = np.array(img, dtype=np.float64)
    noise = RNG.normal(mean, sigma, arr.shape)
    arr = np.clip(arr + noise, 0, 255).astype(np.uint8)
    return Image.fromarray(arr)


def add_pcb_texture(img: Image.Image, intensity: float = 0.35) -> Image.Image:
    """Add a subtle fiberglass weave texture typical of FR4 PCB substrates."""
    arr = np.array(img, dtype=np.float64)
    h, w = arr.shape[:2]
    # Horizontal and vertical weave pattern
    x = np.arange(w)
    y = np.arange(h)
    xx, yy = np.meshgrid(x, y)
    pattern_h = np.sin(xx * 2 * np.pi / 6.0) * intensity * 8
    pattern_v = np.sin(yy * 2 * np.pi / 6.0) * intensity * 8
    texture = pattern_h + pattern_v
    # Add fine-grain randomness
    texture += RNG.normal(0, 2.0, (h, w))
    for c in range(3):
        arr[:, :, c] = np.clip(arr[:, :, c] + texture, 0, 255)
    return Image.fromarray(arr.astype(np.uint8))


def make_green_pcb_base() -> Image.Image:
    """Create a base green PCB image with slight colour variation."""
    arr = np.zeros((H, W, 3), dtype=np.uint8)
    for y in range(H):
        t = y / H
        r = int(PCB_GREEN_DARK[0] * (1 - t) + PCB_GREEN_MID[0] * t)
        g = int(PCB_GREEN_DARK[1] * (1 - t) + PCB_GREEN_MID[1] * t)
        b = int(PCB_GREEN_DARK[2] * (1 - t) + PCB_GREEN_MID[2] * t)
        arr[y, :] = (r, g, b)
    # Per-pixel slight variation
    arr = arr.astype(np.float64) + RNG.normal(0, 3, arr.shape)
    arr = np.clip(arr, 0, 255).astype(np.uint8)
    img = Image.fromarray(arr)
    img = add_pcb_texture(img)
    return img


def draw_copper_trace(
    draw: ImageDraw.ImageDraw,
    x0: int, y0: int, x1: int, y1: int,
    width: int = 2,
    colour: tuple = COPPER,
) -> None:
    """Draw a copper trace between two points."""
    draw.line([(x0, y0), (x1, y1)], fill=colour, width=width)


def draw_solder_pad(
    draw: ImageDraw.ImageDraw, cx: int, cy: int, r: int = 8
) -> None:
    """Draw a circular solder pad."""
    # Annular ring (copper)
    draw.ellipse([cx - r - 2, cy - r - 2, cx + r + 2, cy + r + 2], fill=COPPER)
    # Solder fill
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=SOLDER_SILVER)
    # Highlight
    draw.ellipse(
        [cx - r // 2, cy - r // 2, cx + r // 4, cy + r // 4],
        fill=(210, 210, 215),
    )


def draw_ic_chip(
    draw: ImageDraw.ImageDraw, x: int, y: int, w: int, h: int, pin_side: str = "both"
) -> None:
    """Draw an IC chip (black rectangle) with small pins on sides."""
    # Body
    draw.rectangle([x, y, x + w, y + h], fill=IC_BLACK, outline=(50, 50, 55))
    # Orientation dot
    draw.ellipse([x + 4, y + 4, x + 8, y + 8], fill=(80, 80, 85))
    # Pins
    pin_spacing = max(6, h // 8) if h > 30 else 8
    pin_len = 5
    pin_w = 2
    if pin_side in ("both", "left"):
        py = y + 5
        while py + pin_w < y + h - 3:
            draw.rectangle(
                [x - pin_len, py, x, py + pin_w], fill=SOLDER_SILVER
            )
            py += pin_spacing
    if pin_side in ("both", "right"):
        py = y + 5
        while py + pin_w < y + h - 3:
            draw.rectangle(
                [x + w, py, x + w + pin_len, py + pin_w], fill=SOLDER_SILVER
            )
            py += pin_spacing


def draw_grid_traces(
    draw: ImageDraw.ImageDraw,
    x0: int, y0: int, x1: int, y1: int,
    spacing: int = 40, width: int = 2,
) -> None:
    """Draw a grid of copper traces in a region."""
    for x in range(x0, x1, spacing):
        draw_copper_trace(draw, x, y0, x, y1, width)
    for y in range(y0, y1, spacing):
        draw_copper_trace(draw, x0, y, x1, y, width)


def get_font(size: int = 12) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    """Get a font, fallback to default."""
    try:
        return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", size)
    except (OSError, IOError):
        try:
            return ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf", size)
        except (OSError, IOError):
            return ImageFont.load_default()


# ---------------------------------------------------------------------------
# Image 1: pcb_solder_defects.png
# ---------------------------------------------------------------------------

def generate_pcb_solder_defects() -> Image.Image:
    img = make_green_pcb_base()
    draw = ImageDraw.Draw(img)

    # Copper trace grid
    draw_grid_traces(draw, 30, 30, W - 30, H - 30, spacing=45, width=2)

    # Additional diagonal traces for realism
    for i in range(8):
        x0 = random.randint(50, W - 200)
        y0 = random.randint(50, H - 200)
        draw_copper_trace(draw, x0, y0, x0 + random.randint(80, 200), y0, 2, COPPER_LIGHT)

    # Solder pads - normal
    pad_positions = []
    for row in range(4):
        for col in range(8):
            cx = 80 + col * 85
            cy = 100 + row * 120
            cx += random.randint(-5, 5)
            cy += random.randint(-5, 5)
            pad_positions.append((cx, cy))
            draw_solder_pad(draw, cx, cy, r=10)

    # Solder voids (dark spots inside some solder pads)
    void_indices = [3, 11, 19]
    for idx in void_indices:
        cx, cy = pad_positions[idx]
        # Redraw pad then add void
        draw.ellipse([cx - 10, cy - 10, cx + 10, cy + 10], fill=SOLDER_SILVER)
        # Dark void
        vx = cx + random.randint(-3, 3)
        vy = cy + random.randint(-3, 3)
        vr = random.randint(3, 5)
        draw.ellipse([vx - vr, vy - vr, vx + vr, vy + vr], fill=(40, 35, 30))
        # Smaller secondary void nearby
        draw.ellipse([vx + 2, vy + 2, vx + 5, vy + 5], fill=(55, 45, 35))

    # IC chips
    draw_ic_chip(draw, 150, 200, 70, 45)
    draw_ic_chip(draw, 400, 350, 90, 55)
    draw_ic_chip(draw, 600, 130, 60, 40)

    # Silkscreen labels
    font = get_font(10)
    draw.text((155, 190), "U1", fill=SILKSCREEN_WHITE, font=font)
    draw.text((405, 340), "U2", fill=SILKSCREEN_WHITE, font=font)
    draw.text((605, 120), "U3", fill=SILKSCREEN_WHITE, font=font)

    img = add_gaussian_noise(img, sigma=6)
    return img


# ---------------------------------------------------------------------------
# Image 2: pcb_missing_component.png
# ---------------------------------------------------------------------------

def generate_pcb_missing_component() -> Image.Image:
    img = make_green_pcb_base()
    draw = ImageDraw.Draw(img)
    font = get_font(9)
    font_big = get_font(11)

    # Copper traces
    draw_grid_traces(draw, 20, 20, W - 20, H - 20, spacing=50, width=1)

    # Component footprints - resistors / caps style
    components = []
    for row in range(5):
        for col in range(6):
            x = 60 + col * 120
            y = 50 + row * 105
            cw, ch = 40 + random.randint(-5, 10), 18 + random.randint(-2, 5)
            components.append((x, y, cw, ch))

    missing_indices = {4, 13, 22}

    for i, (x, y, cw, ch) in enumerate(components):
        # Silkscreen outline
        draw.rectangle([x - 1, y - 1, x + cw + 1, y + ch + 1], outline=SILKSCREEN_WHITE, width=1)
        # Pads at each end
        pad_w = 8
        draw.rectangle([x - pad_w, y, x, y + ch], fill=SOLDER_SILVER)
        draw.rectangle([x + cw, y, x + cw + pad_w, y + ch], fill=SOLDER_SILVER)

        label = f"R{i + 1}" if i % 3 != 0 else f"C{i + 1}"
        draw.text((x + 2, y - 12), label, fill=SILKSCREEN_WHITE, font=font)

        if i in missing_indices:
            # Empty footprint - show solder paste (slightly shiny) but no component
            paste_col = (200, 195, 185)
            draw.rectangle([x - pad_w + 1, y + 1, x - 1, y + ch - 1], fill=paste_col)
            draw.rectangle([x + cw + 1, y + 1, x + cw + pad_w - 1, y + ch - 1], fill=paste_col)
        else:
            # Filled component - dark body
            body_col = IC_BLACK if i % 4 == 0 else (60, 55, 50)
            draw.rectangle([x + 1, y + 1, x + cw - 1, y + ch - 1], fill=body_col)
            # Marking on component
            if cw > 35:
                tiny_font = get_font(7)
                draw.text((x + 4, y + 3), "103", fill=(180, 180, 180), font=tiny_font)

    # Board text
    draw.text((W - 180, H - 30), "REV 2.1  PCB-042", fill=SILKSCREEN_WHITE, font=font_big)

    # A larger IC
    draw_ic_chip(draw, 500, 400, 100, 60)
    draw.text((505, 390), "U5", fill=SILKSCREEN_WHITE, font=font)

    img = add_gaussian_noise(img, sigma=7)
    return img


# ---------------------------------------------------------------------------
# Image 3: connector_bent_pins.png
# ---------------------------------------------------------------------------

def generate_connector_bent_pins() -> Image.Image:
    # Dark background - microscope view
    arr = np.full((H, W, 3), 25, dtype=np.uint8)
    # Slight vignette
    yy, xx = np.ogrid[:H, :W]
    dist = np.sqrt((xx - W / 2) ** 2 + (yy - H / 2) ** 2)
    vignette = 1.0 - 0.3 * (dist / (np.sqrt((W / 2) ** 2 + (H / 2) ** 2)))
    for c in range(3):
        arr[:, :, c] = np.clip(arr[:, :, c] * vignette, 0, 255).astype(np.uint8)

    img = Image.fromarray(arr)
    draw = ImageDraw.Draw(img)

    # Connector housing
    housing_x, housing_y = 100, 150
    housing_w, housing_h = 600, 120
    draw.rectangle(
        [housing_x, housing_y, housing_x + housing_w, housing_y + housing_h],
        fill=(55, 50, 45), outline=(70, 65, 60), width=2,
    )
    # Housing label area
    draw.rectangle(
        [housing_x + 10, housing_y + 10, housing_x + housing_w - 10, housing_y + 30],
        fill=(65, 60, 55),
    )

    # Pins
    num_pins = 24
    pin_spacing = housing_w // (num_pins + 1)
    pin_top = housing_y + housing_h
    pin_length = 200
    pin_width = 6

    bent_pins = {5, 12, 19}  # 0-indexed

    for i in range(num_pins):
        px = housing_x + (i + 1) * pin_spacing
        pin_colour = GOLD if i % 2 == 0 else (195, 185, 160)

        if i in bent_pins:
            # Bent pin - draw as two segments at an angle
            bend_y = pin_top + pin_length // 3 + random.randint(-10, 10)
            bend_offset = random.choice([-18, -12, 15, 20])
            # Upper straight part
            draw.rectangle(
                [px - pin_width // 2, pin_top, px + pin_width // 2, bend_y],
                fill=pin_colour,
            )
            # Bent lower part
            end_x = px + bend_offset
            end_y = pin_top + pin_length
            draw.line(
                [(px, bend_y), (end_x, end_y)],
                fill=pin_colour, width=pin_width,
            )
            # Highlight the bend point with a slight bright spot
            draw.ellipse(
                [px - 3, bend_y - 3, px + 3, bend_y + 3],
                fill=(min(pin_colour[0] + 40, 255), min(pin_colour[1] + 40, 255), min(pin_colour[2] + 20, 255)),
            )
        else:
            # Straight pin
            draw.rectangle(
                [px - pin_width // 2, pin_top, px + pin_width // 2, pin_top + pin_length],
                fill=pin_colour,
            )
            # Subtle highlight on straight pins
            draw.line(
                [(px - 1, pin_top), (px - 1, pin_top + pin_length)],
                fill=(min(pin_colour[0] + 30, 255), min(pin_colour[1] + 30, 255), min(pin_colour[2] + 20, 255)),
                width=1,
            )

    # Reflection on connector housing
    draw.rectangle(
        [housing_x + 5, housing_y + housing_h - 15, housing_x + housing_w - 5, housing_y + housing_h - 5],
        fill=(75, 70, 65),
    )

    # Pin row label at bottom
    font = get_font(10)
    draw.text((housing_x + 10, pin_top + pin_length + 15), "Pin row A - 24 pos.", fill=(120, 120, 115), font=font)

    img = add_gaussian_noise(img, sigma=10)
    return img


# ---------------------------------------------------------------------------
# Image 4: pcb_contamination.png
# ---------------------------------------------------------------------------

def generate_pcb_contamination() -> Image.Image:
    img = make_green_pcb_base()
    draw = ImageDraw.Draw(img)

    # Traces and pads
    draw_grid_traces(draw, 40, 40, W - 40, H - 40, spacing=55, width=2)
    for _ in range(12):
        cx = random.randint(80, W - 80)
        cy = random.randint(80, H - 80)
        draw_solder_pad(draw, cx, cy, r=7)

    # A couple of small ICs
    draw_ic_chip(draw, 100, 100, 60, 40)
    draw_ic_chip(draw, 500, 300, 80, 50)
    draw_ic_chip(draw, 300, 450, 55, 35)

    # Horizontal bus traces
    for y_pos in [180, 380, 520]:
        draw_copper_trace(draw, 30, y_pos, W - 30, y_pos, 3, COPPER)

    # Convert to array for contamination blobs
    arr = np.array(img, dtype=np.float64)

    # Brownish / yellowish contamination spots
    contam_spots = [
        (200, 250, 45, 30),
        (450, 180, 55, 40),
        (600, 400, 35, 50),
        (150, 450, 40, 35),
        (700, 150, 30, 25),
    ]
    for cx, cy, rx, ry in contam_spots:
        yy, xx = np.ogrid[:H, :W]
        mask = ((xx - cx) ** 2 / (rx ** 2 + 1)) + ((yy - cy) ** 2 / (ry ** 2 + 1))
        # Irregular shape via noise
        noise_mask = RNG.normal(0, 0.3, (H, W))
        blob = (mask + noise_mask) < 1.0
        # Brownish-yellow colour
        brown = np.array([160, 130, 50], dtype=np.float64)
        alpha = 0.55
        for c in range(3):
            arr[:, :, c] = np.where(blob, arr[:, :, c] * (1 - alpha) + brown[c] * alpha, arr[:, :, c])

    # White flux residue spots
    flux_spots = [
        (350, 320, 20, 15),
        (550, 500, 25, 18),
        (250, 150, 15, 12),
    ]
    for cx, cy, rx, ry in flux_spots:
        yy, xx = np.ogrid[:H, :W]
        mask = ((xx - cx) ** 2 / (rx ** 2 + 1)) + ((yy - cy) ** 2 / (ry ** 2 + 1))
        noise_mask = RNG.normal(0, 0.25, (H, W))
        blob = (mask + noise_mask) < 1.0
        white = np.array([225, 220, 210], dtype=np.float64)
        alpha = 0.6
        for c in range(3):
            arr[:, :, c] = np.where(blob, arr[:, :, c] * (1 - alpha) + white[c] * alpha, arr[:, :, c])

    img = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))
    img = add_gaussian_noise(img, sigma=7)
    return img


# ---------------------------------------------------------------------------
# Image 5: biosensor_assembly.png
# ---------------------------------------------------------------------------

def generate_biosensor_assembly() -> Image.Image:
    # White / light substrate
    arr = np.full((H, W, 3), 0, dtype=np.uint8)
    base = np.array(SUBSTRATE_WHITE, dtype=np.float64)
    for c in range(3):
        arr[:, :, c] = int(base[c])
    # Subtle texture
    arr = arr.astype(np.float64) + RNG.normal(0, 3, arr.shape)
    arr = np.clip(arr, 0, 255).astype(np.uint8)
    img = Image.fromarray(arr)
    draw = ImageDraw.Draw(img)

    # Interdigitated electrode area
    ide_x, ide_y = 150, 120
    ide_w, ide_h = 500, 300

    # Background pad area (gold tint)
    draw.rectangle([ide_x - 10, ide_y - 10, ide_x + ide_w + 10, ide_y + ide_h + 10],
                    fill=(248, 242, 225), outline=(200, 180, 120), width=1)

    # Draw interdigitated fingers
    finger_width = 4
    finger_spacing = 12
    finger_length_a = ide_h - 40  # from top
    finger_length_b = ide_h - 40  # from bottom

    num_fingers = ide_w // finger_spacing
    for i in range(num_fingers):
        fx = ide_x + 20 + i * finger_spacing
        if fx + finger_width > ide_x + ide_w - 20:
            break
        if i % 2 == 0:
            # Finger from top bus
            draw.rectangle(
                [fx, ide_y + 15, fx + finger_width, ide_y + 15 + finger_length_a],
                fill=GOLD,
            )
        else:
            # Finger from bottom bus
            draw.rectangle(
                [fx, ide_y + ide_h - 15 - finger_length_b, fx + finger_width, ide_y + ide_h - 15],
                fill=GOLD_DARK,
            )

    # Top bus bar
    draw.rectangle([ide_x + 15, ide_y + 8, ide_x + ide_w - 15, ide_y + 18], fill=GOLD)
    # Bottom bus bar
    draw.rectangle([ide_x + 15, ide_y + ide_h - 18, ide_x + ide_w - 15, ide_y + ide_h - 8], fill=GOLD_DARK)

    # Connection pads
    draw.rectangle([ide_x - 30, ide_y + 2, ide_x + 15, ide_y + 25], fill=GOLD, outline=GOLD_DARK)
    draw.rectangle([ide_x - 30, ide_y + ide_h - 25, ide_x + 15, ide_y + ide_h - 2], fill=GOLD_DARK, outline=GOLD)

    # Reference electrode (silver rectangle)
    ref_x, ref_y = 680, 180
    ref_w, ref_h = 70, 200
    draw.rectangle([ref_x, ref_y, ref_x + ref_w, ref_y + ref_h],
                    fill=SOLDER_SILVER, outline=SOLDER_DARK, width=2)
    font = get_font(9)
    draw.text((ref_x + 8, ref_y + ref_h // 2 - 5), "REF", fill=(80, 80, 80), font=font)

    # Scratch across one electrode area
    scratch_points = []
    sx = ide_x + 80
    sy = ide_y + 60
    for step in range(60):
        sx += random.randint(4, 8)
        sy += random.randint(-3, 4)
        scratch_points.append((sx, sy))
    if len(scratch_points) > 2:
        draw.line(scratch_points, fill=(SUBSTRATE_WHITE[0] - 10, SUBSTRATE_WHITE[1] - 15, SUBSTRATE_WHITE[2] - 10), width=2)
        # Parallel highlight line for scratch depth illusion
        draw.line(
            [(p[0], p[1] + 2) for p in scratch_points],
            fill=(200, 195, 185), width=1,
        )

    # Labels
    font_label = get_font(11)
    draw.text((ide_x + ide_w // 2 - 40, ide_y + ide_h + 20), "IDE sensor area", fill=(100, 100, 100), font=font_label)
    draw.text((ref_x - 5, ref_y + ref_h + 10), "Ag/AgCl", fill=(100, 100, 100), font=font)

    img = add_gaussian_noise(img, sigma=5)
    return img


# ---------------------------------------------------------------------------
# Image 6: microconnector_overview.png
# ---------------------------------------------------------------------------

def generate_microconnector_overview() -> Image.Image:
    # Tan/orange flex PCB substrate
    arr = np.zeros((H, W, 3), dtype=np.uint8)
    for y in range(H):
        t = y / H
        r = int(FLEX_TAN[0] * (1 - t * 0.15))
        g = int(FLEX_TAN[1] * (1 - t * 0.15))
        b = int(FLEX_TAN[2] * (1 - t * 0.15))
        arr[y, :] = (r, g, b)
    # Add subtle polyimide texture
    texture = RNG.normal(0, 4, (H, W))
    for c in range(3):
        arr[:, :, c] = np.clip(arr[:, :, c].astype(np.float64) + texture, 0, 255).astype(np.uint8)

    img = Image.fromarray(arr)
    draw = ImageDraw.Draw(img)

    # Fine pitch parallel traces
    num_traces = 35
    trace_width = 3
    trace_spacing = (W - 200) // num_traces
    trace_start_y = 80
    trace_end_y = H - 100

    misaligned_trace = 17  # This trace will be slightly wider/offset

    for i in range(num_traces):
        tx = 100 + i * trace_spacing
        tw = trace_width
        colour = COPPER

        if i == misaligned_trace:
            # Dimensional deviation - wider and slightly offset
            tw = trace_width + 3
            tx += 2
            colour = (190, 125, 60)  # Slightly different shade

        draw.rectangle([tx, trace_start_y, tx + tw, trace_end_y], fill=colour)

        # Subtle edge highlight
        draw.line([(tx, trace_start_y), (tx, trace_end_y)], fill=COPPER_LIGHT, width=1)

    # Connector pads at the bottom end - row of gold rectangles
    pad_y = trace_end_y + 10
    pad_h = 40
    pad_w = trace_spacing - 4
    for i in range(num_traces):
        px = 100 + i * trace_spacing
        if i == misaligned_trace:
            px += 2
        draw.rectangle(
            [px - 1, pad_y, px + pad_w + 1, pad_y + pad_h],
            fill=GOLD, outline=GOLD_DARK, width=1,
        )
        # Solder on pad
        draw.rectangle(
            [px + 1, pad_y + 2, px + pad_w - 1, pad_y + pad_h - 8],
            fill=(SOLDER_SILVER[0], SOLDER_SILVER[1] - 10, SOLDER_SILVER[2] - 5),
        )

    # Stiffener bar at top
    draw.rectangle([80, trace_start_y - 30, W - 80, trace_start_y - 5],
                    fill=(120, 100, 60), outline=(90, 75, 45), width=2)

    # Alignment marks
    for mark_x in [90, W - 90]:
        draw.ellipse([mark_x - 8, 40, mark_x + 8, 56], outline=COPPER, width=2)
        draw.line([(mark_x, 40), (mark_x, 56)], fill=COPPER, width=1)
        draw.line([(mark_x - 8, 48), (mark_x + 8, 48)], fill=COPPER, width=1)

    # Coverlay edge (darker band along sides)
    draw.rectangle([0, 0, 60, H], fill=(180, 140, 70))
    draw.rectangle([W - 60, 0, W, H], fill=(180, 140, 70))

    # Label
    font = get_font(10)
    draw.text((W // 2 - 60, H - 30), "FPC-24  Rev.B", fill=(100, 75, 40), font=font)

    img = add_gaussian_noise(img, sigma=6)
    return img


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    out_dir = Path(__file__).parent
    out_dir.mkdir(parents=True, exist_ok=True)

    generators = {
        "pcb_solder_defects.png": generate_pcb_solder_defects,
        "pcb_missing_component.png": generate_pcb_missing_component,
        "connector_bent_pins.png": generate_connector_bent_pins,
        "pcb_contamination.png": generate_pcb_contamination,
        "biosensor_assembly.png": generate_biosensor_assembly,
        "microconnector_overview.png": generate_microconnector_overview,
    }

    for name, gen_func in generators.items():
        print(f"Generating {name} ...")
        img = gen_func()
        assert img.size == (W, H), f"Expected {W}x{H}, got {img.size}"
        path = out_dir / name
        img.save(str(path), "PNG")
        print(f"  -> saved {path}  ({path.stat().st_size / 1024:.1f} KB)")

    print("\nDone - all 6 images generated.")


if __name__ == "__main__":
    main()
