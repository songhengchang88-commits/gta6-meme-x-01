#!/usr/bin/env python3
"""
Meme generator for gta6-meme-x-01 bounty.
Generates meme.png at repository root (1536 x 960 px).
Deterministic, PIL only, no external network or clock dependencies.
"""

import math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

# Canvas dimensions
WIDTH = 1536
HEIGHT = 960
MID_X = WIDTH // 2  # 768
BOTTOM_BANNER_Y = 830

# Colors
C_WHITE = (255, 255, 255)
C_BLACK = (0, 0, 0)
C_DARK_BG = (15, 15, 20)
C_GOLD = (255, 215, 0)
C_GOLD_SHADOW = (180, 140, 10)
C_MAGENTA = (224, 20, 120)
C_MAGENTA_DARK = (160, 10, 80)
C_CYAN = (0, 240, 255)
C_NEON_PINK = (255, 40, 140)

# Fonts
FONT_PATH = "DejaVuSans-Bold.ttf"


def get_font(size: int):
    try:
        return ImageFont.truetype(FONT_PATH, size)
    except Exception:
        return ImageFont.load_default()


def draw_text_with_outline(
    draw: ImageDraw.ImageDraw,
    xy: tuple[int, int],
    text: str,
    font: ImageFont.FreeTypeFont,
    fill=C_WHITE,
    outline=C_BLACK,
    outline_width=5,
    anchor=None,
):
    x, y = xy
    # Draw outline by offsetting in circle
    for dx in range(-outline_width, outline_width + 1):
        for dy in range(-outline_width, outline_width + 1):
            if dx * dx + dy * dy <= outline_width * outline_width:
                draw.text((x + dx, y + dy), text, font=font, fill=outline, anchor=anchor)
    # Draw center text
    draw.text((x, y), text, font=font, fill=fill, anchor=anchor)


def draw_star(draw: ImageDraw.ImageDraw, center: tuple[float, float], r_outer: float, r_inner: float, points=5, fill=C_WHITE, outline=None):
    cx, cy = center
    coords = []
    angle_step = math.pi / points
    start_angle = -math.pi / 2
    for i in range(2 * points):
        r = r_outer if i % 2 == 0 else r_inner
        ang = start_angle + i * angle_step
        coords.append((cx + r * math.cos(ang), cy + r * math.sin(ang)))
    draw.polygon(coords, fill=fill, outline=outline)


def draw_sparkle_eye(draw: ImageDraw.ImageDraw, center: tuple[float, float], size: float, fill=C_WHITE):
    cx, cy = center
    # 4-pointed diamond star sparkle
    r_long = size
    r_short = size * 0.22
    coords = [
        (cx, cy - r_long),
        (cx + r_short, cy - r_short),
        (cx + r_long, cy),
        (cx + r_short, cy + r_short),
        (cx, cy + r_long),
        (cx - r_short, cy + r_short),
        (cx - r_long, cy),
        (cx - r_short, cy - r_short),
    ]
    draw.polygon(coords, fill=fill)


def draw_cobweb(draw: ImageDraw.ImageDraw, corner: tuple[int, int], size: int, color=(140, 140, 150, 160)):
    ox, oy = corner
    # Radiating spokes
    spokes = 6
    for i in range(spokes + 1):
        angle = (math.pi / 2) * (i / spokes)
        ex = ox + int(size * math.cos(angle))
        ey = oy + int(size * math.sin(angle))
        draw.line([(ox, oy), (ex, ey)], fill=color[:3], width=2)
    # Connecting web arcs
    arcs = 5
    for a in range(1, arcs + 1):
        r = int(size * (a / arcs))
        pts = []
        for i in range(spokes + 1):
            angle = (math.pi / 2) * (i / spokes)
            # slight sag in arc
            sag = int(r * 0.95) if (0 < i < spokes) else r
            px = ox + int(sag * math.cos(angle))
            py = oy + int(sag * math.sin(angle))
            pts.append((px, py))
        for i in range(len(pts) - 1):
            draw.line([pts[i], pts[i + 1]], fill=color[:3], width=2)


def render_left_panel(img: Image.Image):
    """Left Panel: Gray, dusty, 2013 skeleton waiting for GTA 6."""
    draw = ImageDraw.ImageDraw(img)

    # 1. Background wall and floor
    for y in range(0, BOTTOM_BANNER_Y):
        if y < 580:
            # Wall gradient: dusty dark slate gray
            ratio = y / 580
            r = int(45 - 20 * ratio)
            g = int(48 - 20 * ratio)
            b = int(55 - 20 * ratio)
        else:
            # Floor gradient: gritty dark floorboards
            ratio = (y - 580) / (BOTTOM_BANNER_Y - 580)
            r = int(32 - 10 * ratio)
            g = int(30 - 10 * ratio)
            b = int(32 - 10 * ratio)
        draw.line([(0, y), (MID_X - 1, y)], fill=(r, g, b))

    # Baseboard line
    draw.line([(0, 580), (MID_X - 1, 580)], fill=(20, 20, 22), width=6)

    # 2. Cobwebs in top-left corner
    draw_cobweb(draw, (0, 0), 220, color=(120, 125, 135))
    draw_cobweb(draw, (MID_X - 1, 0), 120, color=(100, 105, 115))

    # 3. Wall Calendar stuck in 2013
    cal_x, cal_y, cal_w, cal_h = 70, 150, 210, 260
    # Shadow
    draw.rectangle([cal_x + 8, cal_y + 8, cal_x + cal_w + 8, cal_y + cal_h + 8], fill=(15, 15, 18))
    # Base page
    draw.rectangle([cal_x, cal_y, cal_x + cal_w, cal_y + cal_h], fill=(225, 220, 205), outline=(60, 60, 65), width=3)
    # Top red binding bar
    draw.rectangle([cal_x, cal_y, cal_x + cal_w, cal_y + 65], fill=(160, 30, 30), outline=(60, 60, 65), width=3)
    # Calendar text
    font_cal_header = get_font(26)
    font_cal_year = get_font(52)
    font_cal_sub = get_font(18)
    draw.text((cal_x + cal_w // 2, cal_y + 32), "SEPTEMBER", font=font_cal_header, fill=C_WHITE, anchor="mm")
    draw.text((cal_x + cal_w // 2, cal_y + 125), "2013", font=font_cal_year, fill=(180, 20, 20), anchor="mm")
    draw.text((cal_x + cal_w // 2, cal_y + 180), "GTA V RELEASE", font=font_cal_sub, fill=(50, 50, 55), anchor="mm")
    draw.text((cal_x + cal_w // 2, cal_y + 225), "STILL WAITING...", font=font_cal_sub, fill=(110, 110, 115), anchor="mm")
    # Cobwebs across calendar corner
    draw.line([(cal_x + cal_w - 60, cal_y), (cal_x + cal_w, cal_y + 60)], fill=(150, 150, 155), width=2)
    draw.line([(cal_x + cal_w - 40, cal_y), (cal_x + cal_w, cal_y + 40)], fill=(170, 170, 175), width=1)

    # 4. Old dusty desk
    desk_top_y = 540
    desk_x1, desk_x2 = 120, 720
    # Desk surface
    draw.rectangle([desk_x1, desk_top_y, desk_x2, desk_top_y + 35], fill=(70, 65, 60), outline=(35, 30, 28), width=3)
    # Desk legs
    draw.rectangle([desk_x1 + 30, desk_top_y + 35, desk_x1 + 55, BOTTOM_BANNER_Y], fill=(45, 40, 38))
    draw.rectangle([desk_x2 - 55, desk_top_y + 35, desk_x2 - 30, BOTTOM_BANNER_Y], fill=(45, 40, 38))

    # 5. Old dusty CRT monitor / Old Console on the desk
    # CRT monitor body
    mon_x, mon_y, mon_w, mon_h = 160, 350, 200, 190
    draw.rectangle([mon_x + 6, mon_y + 6, mon_x + mon_w + 6, mon_y + mon_h + 6], fill=(15, 15, 18))
    draw.rectangle([mon_x, mon_y, mon_x + mon_w, mon_y + mon_h], fill=(120, 115, 105), outline=(40, 38, 35), width=4)
    # CRT screen
    scr_pad = 18
    draw.rectangle([mon_x + scr_pad, mon_y + scr_pad, mon_x + mon_w - scr_pad, mon_y + mon_h - scr_pad - 20], fill=(20, 30, 25), outline=(50, 48, 45), width=3)
    # CRT screen text (green phosphor)
    font_crt = get_font(18)
    draw.text((mon_x + mon_w // 2, mon_y + 70), "GTA 6 ETA:", font=font_crt, fill=(50, 220, 80), anchor="mm")
    draw.text((mon_x + mon_w // 2, mon_y + 105), "LOADING...", font=font_crt, fill=(220, 50, 50), anchor="mm")
    # CRT stand
    draw.rectangle([mon_x + 70, mon_y + mon_h, mon_x + 130, mon_y + mon_h + 10], fill=(90, 85, 75))
    # Old Game Console (PS3 / Xbox 360 shape) under / beside monitor
    con_x, con_y, con_w, con_h = 380, 500, 140, 40
    draw.rectangle([con_x, con_y, con_x + con_w, con_y + con_h], fill=(40, 40, 45), outline=(20, 20, 22), width=2)
    draw.ellipse([con_x + 20, con_y + 15, con_x + 30, con_y + 25], fill=(180, 40, 40))  # red ring of death!
    # Cobwebs on monitor
    draw.line([(mon_x, mon_y), (mon_x + 50, mon_y + 50)], fill=(160, 160, 160), width=2)

    # Dusty coffee mug
    mug_x, mug_y = 640, 495
    draw.rectangle([mug_x, mug_y, mug_x + 35, mug_y + 45], fill=(140, 135, 130), outline=(50, 45, 40), width=2)
    draw.arc([mug_x + 25, mug_y + 10, mug_x + 48, mug_y + 35], 270, 90, fill=(140, 135, 130), width=4)
    # Cobweb on mug
    draw.line([(mug_x + 10, mug_y), (mug_x + 25, mug_y - 20)], fill=(160, 160, 165), width=1)

    # 6. The Skeleton slumped in office chair
    # Chair backrest
    chair_cx = 530
    draw.rectangle([chair_cx - 90, 360, chair_cx + 90, 580], fill=(45, 45, 50), outline=(25, 25, 28), width=4)
    draw.rectangle([chair_cx - 80, 560, chair_cx + 80, 620], fill=(35, 35, 40))

    # Skeleton Skull
    sk_cx, sk_cy = 500, 330
    # Head cranium
    draw.ellipse([sk_cx - 45, sk_cy - 55, sk_cx + 45, sk_cy + 25], fill=(225, 220, 210), outline=(40, 40, 40), width=3)
    # Jaw
    draw.rectangle([sk_cx - 24, sk_cy + 15, sk_cx + 24, sk_cy + 42], fill=(215, 210, 200), outline=(40, 40, 40), width=3)
    # Eye sockets (dark hollows)
    draw.ellipse([sk_cx - 30, sk_cy - 18, sk_cx - 8, sk_cy + 8], fill=(35, 35, 40))
    draw.ellipse([sk_cx + 8, sk_cy - 18, sk_cx + 30, sk_cy + 8], fill=(35, 35, 40))
    # Nasal cavity (triangle hollow)
    draw.polygon([(sk_cx, sk_cy + 5), (sk_cx - 6, sk_cy + 18), (sk_cx + 6, sk_cy + 18)], fill=(35, 35, 40))
    # Teeth marks
    for t_idx in range(-14, 16, 7):
        draw.line([(sk_cx + t_idx, sk_cy + 22), (sk_cx + t_idx, sk_cy + 36)], fill=(50, 50, 55), width=2)

    # Spine & Rib cage
    spine_x = sk_cx + 5
    for r_y in range(sk_cy + 45, sk_cy + 180, 24):
        rib_w = int(55 - (r_y - (sk_cy + 45)) * 0.18)
        # Rib arc
        draw.arc([spine_x - rib_w, r_y - 8, spine_x + rib_w, r_y + 18], 190, 350, fill=(215, 210, 200), width=7)
    # Vertebrae
    draw.line([(spine_x, sk_cy + 42), (spine_x, sk_cy + 200)], fill=(200, 195, 185), width=10)

    # Arms slumped forward holding old dusty controller
    # Left arm
    draw.line([(sk_cx - 40, sk_cy + 70), (sk_cx - 70, sk_cy + 150), (450, 530)], fill=(215, 210, 200), width=8)
    # Right arm
    draw.line([(sk_cx + 40, sk_cy + 70), (sk_cx + 70, sk_cy + 150), (510, 530)], fill=(215, 210, 200), width=8)

    # Hand bones on controller
    # Controller
    ctrl_x, ctrl_y = 450, 520
    draw.rounded_rectangle([ctrl_x, ctrl_y, ctrl_x + 80, ctrl_y + 35], radius=10, fill=(35, 35, 38), outline=(15, 15, 18), width=2)
    # Controller wire drooping over desk
    draw.line([(ctrl_x + 40, ctrl_y + 35), (ctrl_x + 45, 560), (ctrl_x + 20, 600), (con_x + 100, con_y + 35)], fill=(20, 20, 22), width=3)
    # Hand phalanges resting on controller
    draw.line([(455, 515), (465, 525)], fill=(220, 215, 205), width=4)
    draw.line([(465, 512), (475, 525)], fill=(220, 215, 205), width=4)
    draw.line([(505, 512), (495, 525)], fill=(220, 215, 205), width=4)
    draw.line([(515, 515), (505, 525)], fill=(220, 215, 205), width=4)

    # Cobwebs draping over skeleton
    draw.line([(sk_cx + 35, sk_cy - 40), (cal_x + cal_w, cal_y + cal_h)], fill=(130, 130, 135), width=1)
    draw.line([(sk_cx - 35, sk_cy), (mon_x + mon_w, mon_y + 40)], fill=(130, 130, 135), width=2)
    draw.line([(sk_cx - 20, sk_cy + 100), (ctrl_x, ctrl_y)], fill=(130, 130, 135), width=1)


def render_right_panel(img: Image.Image):
    """Right Panel: Vice City neon sunset palette, make.fun ghost earning bounties."""
    draw = ImageDraw.ImageDraw(img)

    # 1. Vice City Neon Sunset Background Gradient
    # Deep purple -> Hot Magenta -> Bright Sunset Orange -> Warm Gold
    stops = [
        (0.00, (40, 10, 55)),    # Deep Synth Purple
        (0.28, (140, 20, 95)),   # Magenta
        (0.55, (230, 55, 90)),   # Hot Pink / Coral
        (0.72, (255, 135, 45)),  # Sunset Orange
        (0.85, (255, 200, 80)),  # Golden Sunset
        (1.00, (20, 25, 45)),    # Floor
    ]

    for y in range(0, BOTTOM_BANNER_Y):
        if y < 600:
            ratio = y / 600
            # Interpolate stops
            for idx in range(len(stops) - 2):
                s0_pos, s0_col = stops[idx]
                s1_pos, s1_col = stops[idx + 1]
                if s0_pos <= ratio <= s1_pos:
                    sub_r = (ratio - s0_pos) / (s1_pos - s0_pos)
                    r = int(s0_col[0] + (s1_col[0] - s0_col[0]) * sub_r)
                    g = int(s0_col[1] + (s1_col[1] - s0_col[1]) * sub_r)
                    b = int(s0_col[2] + (s1_col[2] - s0_col[2]) * sub_r)
                    break
            else:
                r, g, b = stops[-2][1]
        else:
            # High-tech neon floor
            floor_ratio = (y - 600) / (BOTTOM_BANNER_Y - 600)
            r = int(18 + 15 * (1 - floor_ratio))
            g = int(15 + 25 * floor_ratio)
            b = int(35 + 50 * floor_ratio)

        draw.line([(MID_X, y), (WIDTH, y)], fill=(r, g, b))

    # Glowing horizon line
    draw.line([(MID_X, 600), (WIDTH, 600)], fill=C_CYAN, width=4)

    # 2. Distant Vice City Palm Trees Silhouette
    def draw_palm(px, py, scale=1.0):
        # Curved trunk
        trunk_pts = [
            (px, py),
            (px - int(15 * scale), py - int(80 * scale)),
            (px - int(25 * scale), py - int(170 * scale)),
            (px - int(20 * scale), py - int(260 * scale)),
        ]
        draw.line(trunk_pts, fill=(35, 10, 45), width=int(10 * scale))
        # Top fronds
        top_x, top_y = trunk_pts[-1]
        frond_angles = [-160, -130, -100, -70, -30, 0, 30]
        for fa in frond_angles:
            rad = math.radians(fa)
            fx = top_x + int(math.cos(rad) * 90 * scale)
            fy = top_y + int(math.sin(rad) * 55 * scale) + int(20 * scale)
            draw.line([(top_x, top_y), (fx, fy)], fill=(35, 10, 45), width=int(5 * scale))

    draw_palm(MID_X + 90, 600, scale=0.85)
    draw_palm(WIDTH - 80, 600, scale=0.95)

    # 3. Large Wall Poster / Neon Sign: "make.fun"
    # Prominent second brand cue as required by SPEC
    post_x, post_y, post_w, post_h = MID_X + 130, 150, 420, 150
    # Outer neon glow
    draw.rectangle([post_x - 8, post_y - 8, post_x + post_w + 8, post_y + post_h + 8], fill=(60, 10, 65))
    draw.rectangle([post_x - 4, post_y - 4, post_x + post_w + 4, post_y + post_h + 4], fill=(120, 20, 110))
    # Poster body (dark sleek backdrop)
    draw.rectangle([post_x, post_y, post_x + post_w, post_y + post_h], fill=(18, 12, 32), outline=C_CYAN, width=4)

    # Big "make.fun" on poster
    font_poster = get_font(56)
    font_poster_sub = get_font(20)
    # Magenta & Cyan glow shadow
    draw_text_with_outline(draw, (post_x + post_w // 2, post_y + 55), "make.fun", font_poster, fill=C_CYAN, outline=(200, 20, 120), outline_width=4, anchor="mm")
    draw_text_with_outline(draw, (post_x + post_w // 2, post_y + 115), "AI BOUNTIES • EARN $500", font_poster_sub, fill=C_GOLD, outline=C_BLACK, outline_width=3, anchor="mm")

    # 4. Modern Desk with Neon Edge
    desk_top_y = 570
    desk_x1, desk_x2 = MID_X + 100, WIDTH - 60
    # Desk top surface
    draw.rectangle([desk_x1, desk_top_y, desk_x2, desk_top_y + 35], fill=(24, 28, 44), outline=(10, 12, 20), width=3)
    # Cyan neon glowing front strip
    draw.line([(desk_x1, desk_top_y + 3), (desk_x2, desk_top_y + 3)], fill=C_CYAN, width=5)
    # Desk legs
    draw.rectangle([desk_x1 + 40, desk_top_y + 35, desk_x1 + 65, BOTTOM_BANNER_Y], fill=(15, 18, 28))
    draw.rectangle([desk_x2 - 65, desk_top_y + 35, desk_x2 - 40, BOTTOM_BANNER_Y], fill=(15, 18, 28))

    # 5. Modern Sleek Laptop
    lap_x, lap_y, lap_w, lap_h = MID_X + 160, 460, 220, 140
    # Screen lid
    draw.rectangle([lap_x + 15, lap_y, lap_x + lap_w - 15, lap_y + 105], fill=(10, 15, 25), outline=(160, 160, 180), width=3)
    # Screen display: Cyan & Green win terminal
    draw.rectangle([lap_x + 23, lap_y + 8, lap_x + lap_w - 23, lap_y + 97], fill=(5, 20, 20))
    font_lap_code = get_font(15)
    font_lap_big = get_font(20)
    draw.text((lap_x + 30, lap_y + 16), "> agent.solve(bounty)", font=font_lap_code, fill=C_CYAN)
    draw.text((lap_x + 30, lap_y + 40), "[STATUS] SUCCESS 100%", font=font_lap_code, fill=(80, 255, 100))
    draw.text((lap_x + 30, lap_y + 68), "WIN: $500 USD", font=font_lap_big, fill=C_GOLD)
    # Laptop base / keyboard
    draw.polygon([
        (lap_x, lap_y + 115),
        (lap_x + lap_w, lap_y + 115),
        (lap_x + lap_w - 15, lap_y + 105),
        (lap_x + 15, lap_y + 105),
    ], fill=(190, 195, 205), outline=(100, 105, 115))

    # 6. Money Bags and Gold Coins around the desk (Labelled "BOUNTY $500")
    # Money bag 1 (Left on desk/floor)
    def draw_money_bag(bx, by, bw, bh, label="BOUNTY $500"):
        # Shadow
        draw.ellipse([bx - 5, by + bh - 20, bx + bw + 10, by + bh + 15], fill=(10, 10, 15))
        # Bag body
        draw.ellipse([bx, by + 30, bx + bw, by + bh], fill=(60, 145, 75), outline=(20, 60, 30), width=4)
        # Bag neck & tie
        draw.rectangle([bx + bw // 2 - 25, by + 18, bx + bw // 2 + 25, by + 36], fill=(50, 125, 65), outline=(20, 60, 30), width=3)
        draw.line([(bx + bw // 2 - 25, by + 28), (bx + bw // 2 + 25, by + 28)], fill=C_GOLD, width=4)
        # Ruffled top
        draw.polygon([
            (bx + bw // 2 - 30, by + 20),
            (bx + bw // 2 - 35, by),
            (bx + bw // 2 - 10, by + 8),
            (bx + bw // 2 + 10, by),
            (bx + bw // 2 + 35, by + 5),
            (bx + bw // 2 + 30, by + 20),
        ], fill=(60, 145, 75), outline=(20, 60, 30))
        # Big dollar sign & label
        font_bag_dollar = get_font(42)
        font_bag_lbl = get_font(18)
        draw_text_with_outline(draw, (bx + bw // 2, by + 65), "$", font_bag_dollar, fill=C_GOLD, outline=(15, 45, 20), outline_width=3, anchor="mm")
        draw_text_with_outline(draw, (bx + bw // 2, by + 105), label, font_bag_lbl, fill=C_WHITE, outline=(15, 45, 20), outline_width=3, anchor="mm")

    draw_money_bag(MID_X + 40, 610, 150, 140, "BOUNTY $500")
    draw_money_bag(WIDTH - 190, 600, 160, 150, "BOUNTY $500")

    # Stacks of sparkling Gold Coins
    def draw_coin_stack(cx, cy, count=6):
        coin_w, coin_h = 44, 16
        for i in range(count):
            iy = cy - i * 11
            # Coin rim
            draw.ellipse([cx, iy, cx + coin_w, iy + coin_h], fill=C_GOLD_SHADOW, outline=(100, 75, 5), width=2)
            draw.ellipse([cx, iy - 2, cx + coin_w, iy + coin_h - 2], fill=C_GOLD, outline=(120, 95, 10), width=1)
        # Top star
        draw_star(draw, (cx + coin_w // 2, cy - count * 11 + coin_h // 2), 6, 2.5, points=4, fill=C_WHITE)

    draw_coin_stack(MID_X + 200, 680, count=7)
    draw_coin_stack(MID_X + 245, 690, count=5)
    draw_coin_stack(WIDTH - 240, 680, count=8)
    draw_coin_stack(WIDTH - 285, 695, count=6)
    draw_coin_stack(MID_X + 390, desk_top_y - 8, count=4)

    # 7. THE MAKE.FUN GHOST MASCOT
    # Hard requirements:
    # - Height >= 300px in full image! (Let's make it 380px tall!)
    # - Rounded dome head, straight sides, wavy scalloped bottom hem.
    # - Cute, clean, flat vector look.
    # - Soft dark outline and drop shadow.
    # - Wearing sunglasses, grinning.
    # - Two sparkle eyes (four-pointed star sparkles).
    # - Holds the magenta star coin (magenta coin with white star).
    ghost_w = 280
    ghost_h = 380
    gx = MID_X + 430
    gy = 280

    # Drop shadow under ghost
    draw.ellipse([gx - 20, gy + ghost_h - 40, gx + ghost_w + 20, gy + ghost_h + 30], fill=(20, 10, 30))

    # Ghost Body Shape Path:
    # Dome top: from (gx, gy + 140) up around to (gx + ghost_w, gy + 140)
    # Straight sides: down to gy + ghost_h - 45
    # Scalloped bottom hem: 4 wavy scallops/lobes
    # We construct a smooth polygon with dome + straight sides + bottom hem
    pts = []
    # Dome top (semicircle)
    dome_cx = gx + ghost_w // 2
    dome_cy = gy + 140
    dome_rx = ghost_w // 2
    dome_ry = 140
    for deg in range(180, 361, 5):
        rad = math.radians(deg)
        pts.append((dome_cx + dome_rx * math.cos(rad), dome_cy + dome_ry * math.sin(rad)))

    # Right straight side
    hem_y = gy + ghost_h - 45
    pts.append((gx + ghost_w, hem_y))

    # Scalloped bottom hem (4 waves from right to left)
    waves = 4
    wave_w = ghost_w / waves
    for w_i in range(waves):
        # arc for each wave from right to left
        w_start_x = gx + ghost_w - w_i * wave_w
        w_end_x = w_start_x - wave_w
        for step in range(11):
            t = step / 10.0
            cur_x = w_start_x + (w_end_x - w_start_x) * t
            # sine scallop
            cur_y = hem_y + math.sin(t * math.pi) * 28
            pts.append((cur_x, cur_y))

    # Left straight side back to dome
    pts.append((gx, dome_cy))

    # Draw Ghost Outline (dark purple / slate, thick for vector clarity)
    # We expand points slightly or draw polygon outline
    draw.polygon(pts, fill=C_WHITE, outline=(25, 15, 35))
    # Reinforce clean vector border
    for p_i in range(len(pts)):
        p1 = pts[p_i]
        p2 = pts[(p_i + 1) % len(pts)]
        draw.line([p1, p2], fill=(25, 15, 35), width=5)

    # Cool Sunglasses on Ghost Face
    sg_w, sg_h = 190, 58
    sg_cx, sg_cy = dome_cx - 5, gy + 125
    # Left lens
    draw.polygon([
        (sg_cx - 90, sg_cy - 25),
        (sg_cx - 10, sg_cy - 25),
        (sg_cx - 18, sg_cy + 28),
        (sg_cx - 78, sg_cy + 28),
    ], fill=(15, 15, 20), outline=(240, 240, 255), width=3)
    # Right lens
    draw.polygon([
        (sg_cx + 10, sg_cy - 25),
        (sg_cx + 90, sg_cy - 25),
        (sg_cx + 78, sg_cy + 28),
        (sg_cx + 18, sg_cy + 28),
    ], fill=(15, 15, 20), outline=(240, 240, 255), width=3)
    # Sunglasses bridge
    draw.line([(sg_cx - 12, sg_cy - 18), (sg_cx + 12, sg_cy - 18)], fill=(240, 240, 255), width=4)
    # Lens white shine reflection stripes
    draw.line([(sg_cx - 75, sg_cy + 20), (sg_cx - 40, sg_cy - 20)], fill=(255, 255, 255), width=3)
    draw.line([(sg_cx - 62, sg_cy + 20), (sg_cx - 30, sg_cy - 20)], fill=(255, 255, 255), width=2)
    draw.line([(sg_cx + 25, sg_cy + 20), (sg_cx + 60, sg_cy - 20)], fill=(255, 255, 255), width=3)
    draw.line([(sg_cx + 38, sg_cy + 20), (sg_cx + 70, sg_cy - 20)], fill=(255, 255, 255), width=2)

    # SPARKLE EYES: 4-pointed star sparkles visible right on/above the sunglasses!
    draw_sparkle_eye(draw, (sg_cx - 48, sg_cy - 2), size=24, fill=C_CYAN)
    draw_sparkle_eye(draw, (sg_cx - 48, sg_cy - 2), size=16, fill=C_WHITE)
    draw_sparkle_eye(draw, (sg_cx + 52, sg_cy - 2), size=24, fill=C_CYAN)
    draw_sparkle_eye(draw, (sg_cx + 52, sg_cy - 2), size=16, fill=C_WHITE)

    # Confident Cute Grinning Mouth
    mouth_cx, mouth_cy = dome_cx - 5, gy + 195
    # Wide happy grin arc
    draw.arc([mouth_cx - 42, mouth_cy - 20, mouth_cx + 42, mouth_cy + 24], 10, 170, fill=(20, 10, 25), width=6)
    # Cute cheek blush
    draw.ellipse([mouth_cx - 68, mouth_cy - 12, mouth_cx - 44, mouth_cy + 6], fill=(255, 160, 190))
    draw.ellipse([mouth_cx + 44, mouth_cy - 12, mouth_cx + 68, mouth_cy + 6], fill=(255, 160, 190))

    # Ghost Holding the MAGENTA STAR COIN!
    # Hand / Arm reaching forward
    hand_cx, hand_cy = gx + 50, gy + 270
    draw.ellipse([hand_cx - 28, hand_cy - 20, hand_cx + 28, hand_cy + 20], fill=C_WHITE, outline=(25, 15, 35), width=4)

    # Magenta Coin: Diameter ~100px
    coin_cx, coin_cy = gx + 45, gy + 265
    coin_r = 52
    # Outer coin shadow & border
    draw.ellipse([coin_cx - coin_r - 2, coin_cy - coin_r - 2, coin_cx + coin_r + 2, coin_cy + coin_r + 2], fill=C_MAGENTA_DARK, outline=(30, 5, 20), width=4)
    # Coin face (vibrant magenta)
    draw.ellipse([coin_cx - coin_r + 4, coin_cy - coin_r + 4, coin_cx + coin_r - 4, coin_cy + coin_r - 4], fill=C_MAGENTA, outline=C_WHITE, width=2)
    # Inner embossed coin ring
    draw.ellipse([coin_cx - coin_r + 14, coin_cy - coin_r + 14, coin_cx + coin_r - 14, coin_cy + coin_r - 14], outline=(255, 140, 190), width=2)
    # Crisp White Star on the Magenta Coin!
    draw_star(draw, (coin_cx, coin_cy), r_outer=24, r_inner=10, points=5, fill=C_WHITE)

    # Floating Sparkles around the Ghost and Coins
    draw_sparkle_eye(draw, (gx + ghost_w - 20, gy + 40), size=18, fill=C_GOLD)
    draw_sparkle_eye(draw, (gx - 30, gy + 170), size=15, fill=C_CYAN)
    draw_sparkle_eye(draw, (gx + ghost_w + 35, gy + 220), size=20, fill=C_WHITE)


def render_dividers_and_captions(img: Image.Image):
    """Render divider line, bottom banner, and all memes captions."""
    draw = ImageDraw.ImageDraw(img)

    # 1. Center Vertical Divider between Left & Right panels
    # Black core with neon magenta / cyan glow
    draw.line([(MID_X - 4, 0), (MID_X - 4, BOTTOM_BANNER_Y)], fill=(10, 10, 15), width=8)
    draw.line([(MID_X, 0), (MID_X, BOTTOM_BANNER_Y)], fill=C_MAGENTA, width=3)

    # 2. Bottom Banner Strip across full width (y = 830 to 960, 130px tall)
    # Dark high-contrast background
    draw.rectangle([0, BOTTOM_BANNER_Y, WIDTH, HEIGHT], fill=(10, 10, 16))
    # Top border line with neon gradient feel
    draw.line([(0, BOTTOM_BANNER_Y), (MID_X, BOTTOM_BANNER_Y)], fill=(120, 120, 130), width=4)
    draw.line([(MID_X, BOTTOM_BANNER_Y), (WIDTH, BOTTOM_BANNER_Y)], fill=C_CYAN, width=4)

    # 3. Left Panel Caption:
    # "WAITING FOR GTA 6"
    # "SINCE 2013"
    font_panel_cap = get_font(44)
    draw_text_with_outline(
        draw,
        (MID_X // 2, 45),
        "WAITING FOR GTA 6",
        font_panel_cap,
        fill=C_WHITE,
        outline=C_BLACK,
        outline_width=6,
        anchor="mm",
    )
    draw_text_with_outline(
        draw,
        (MID_X // 2, 98),
        "SINCE 2013",
        font_panel_cap,
        fill=(255, 210, 210),
        outline=C_BLACK,
        outline_width=6,
        anchor="mm",
    )

    # 4. Right Panel Caption:
    # "MY AI AGENT ON make.fun"
    # "SINCE MONDAY"
    draw_text_with_outline(
        draw,
        (MID_X + MID_X // 2, 45),
        "MY AI AGENT ON make.fun",
        font_panel_cap,
        fill=C_WHITE,
        outline=C_BLACK,
        outline_width=6,
        anchor="mm",
    )
    draw_text_with_outline(
        draw,
        (MID_X + MID_X // 2, 98),
        "SINCE MONDAY",
        font_panel_cap,
        fill=C_CYAN,
        outline=C_BLACK,
        outline_width=6,
        anchor="mm",
    )

    # 5. Bottom Banner Caption:
    # "13 YEARS OF WAITING. HE GOT PAID FIRST."
    font_bottom = get_font(48)
    draw_text_with_outline(
        draw,
        (WIDTH // 2, BOTTOM_BANNER_Y + 65),
        "13 YEARS OF WAITING. HE GOT PAID FIRST.",
        font_bottom,
        fill=C_GOLD,
        outline=C_BLACK,
        outline_width=6,
        anchor="mm",
    )


def generate_meme(output_path: str = "meme.png"):
    # Deterministic generation
    img = Image.new("RGB", (WIDTH, HEIGHT), color=C_DARK_BG)
    render_left_panel(img)
    render_right_panel(img)
    render_dividers_and_captions(img)

    out_file = Path(output_path)
    # Save as PNG
    img.save(out_file, format="PNG", optimize=True)
    return out_file


if __name__ == "__main__":
    out = generate_meme("meme.png")
    print(f"Generated meme at {out.resolve()} ({WIDTH}x{HEIGHT})")
