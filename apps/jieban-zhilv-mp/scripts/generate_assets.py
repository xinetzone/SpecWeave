#!/usr/bin/env python3
"""生成结伴之旅小程序的图标与活动主图素材。

输出统一风格的线性图标（透明背景 PNG）与三张扁平插画风活动主图。
不使用 Emoji：所有图形均由几何基元绘制。
"""

import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

ROOT = Path(__file__).resolve().parent.parent
ICON_DIR = ROOT / "assets" / "icons"
COVER_DIR = ROOT / "assets" / "covers"

INK = (47, 58, 74, 255)
MUTED = (152, 162, 179, 255)
BRAND = (47, 107, 255, 255)
TAB_IDLE = (185, 192, 204, 255)

STROKE = 6.0
GRID = 64


def _canvas(size: int) -> tuple[Image.Image, ImageDraw.ImageDraw]:
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    return img, ImageDraw.Draw(img)


def _line(draw, points, color, width, closed=False):
    pts = list(points)
    if closed:
        pts = pts + [pts[0]]
    draw.line(pts, fill=color, width=int(width), joint="curve")
    radius = width / 2
    for x, y in pts:
        draw.ellipse([x - radius, y - radius, x + radius, y + radius], fill=color)


def _rrect(draw, box, radius, color, width):
    draw.rounded_rectangle(box, radius=radius, outline=color, width=int(width))


def _circle(draw, cx, cy, r, color, width):
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=color, width=int(width))


def _poly(draw, points, color):
    draw.polygon(points, fill=color)


def icon_calendar(draw, c):
    _rrect(draw, (10, 16, 54, 54), 6, c, STROKE)
    _line(draw, [(10, 28), (54, 28)], c, STROKE)
    _line(draw, [(21, 10), (21, 20)], c, STROKE)
    _line(draw, [(43, 10), (43, 20)], c, STROKE)
    for x in (22, 32, 42):
        for y in (36, 46):
            draw.ellipse([x - 2.4, y - 2.4, x + 2.4, y + 2.4], fill=c)


def icon_location(draw, c):
    _circle(draw, 32, 26, 12, c, STROKE)
    _line(draw, [(22, 35), (32, 56), (42, 35)], c, STROKE)


def icon_ticket(draw, c):
    _rrect(draw, (8, 16, 56, 48), 8, c, STROKE)
    _line(draw, [(40, 16), (40, 48)], c, STROKE - 1.2)


def icon_users(draw, c):
    _circle(draw, 26, 24, 9, c, STROKE)
    draw.arc([11, 34, 41, 60], start=180, end=360, fill=c, width=int(STROKE))
    _circle(draw, 44, 26, 7, c, STROKE - 1.4)
    draw.arc([32, 36, 58, 58], start=190, end=340, fill=c, width=int(STROKE - 1.4))


def icon_arrow(draw, c):
    _line(draw, [(16, 32), (48, 32)], c, STROKE)
    _line(draw, [(37, 21), (48, 32), (37, 43)], c, STROKE)


def icon_check(draw, c):
    _line(draw, [(15, 33), (27, 45), (49, 21)], c, STROKE)


def icon_clock(draw, c):
    _circle(draw, 32, 32, 21, c, STROKE)
    _line(draw, [(32, 32), (32, 20)], c, STROKE - 1)
    _line(draw, [(32, 32), (41, 37)], c, STROKE - 1)


def icon_shield(draw, c):
    _line(draw, [(32, 9), (52, 18), (52, 33), (32, 55), (12, 33), (12, 18)], c, STROKE, closed=True)
    _line(draw, [(23, 32), (29, 39), (42, 25)], c, STROKE - 1.4)


def icon_camera(draw, c):
    _rrect(draw, (8, 20, 56, 52), 7, c, STROKE)
    _line(draw, [(24, 20), (28, 13), (36, 13), (40, 20)], c, STROKE)
    _circle(draw, 32, 36, 10, c, STROKE - 1)


def icon_close(draw, c):
    _line(draw, [(19, 19), (45, 45)], c, STROKE)
    _line(draw, [(45, 19), (19, 45)], c, STROKE)


def icon_minus(draw, c):
    _line(draw, [(17, 32), (47, 32)], c, STROKE)


def icon_plus(draw, c):
    _line(draw, [(17, 32), (47, 32)], c, STROKE)
    _line(draw, [(32, 17), (32, 47)], c, STROKE)


def icon_pencil(draw, c):
    _line(draw, [(16, 48), (16, 44), (42, 18), (48, 24), (22, 50), (16, 48)], c, STROKE - 1.0, closed=True)
    _line(draw, [(38, 22), (44, 28)], c, STROKE - 2.0)


def icon_image(draw, c):
    _rrect(draw, (9, 14, 55, 50), 6, c, STROKE)
    _circle(draw, 22, 26, 5, c, STROKE - 2)
    _poly(draw, [(13, 46), (28, 30), (38, 40), (45, 33), (52, 46)], c)


def icon_home(draw, c):
    _line(draw, [(12, 30), (32, 13), (52, 30)], c, STROKE)
    _line(draw, [(19, 27), (19, 51), (45, 51), (45, 27)], c, STROKE)


def icon_list(draw, c):
    _rrect(draw, (13, 11, 51, 53), 6, c, STROKE)
    for y in (22, 32, 42):
        draw.ellipse([19 - 2, y - 2, 19 + 2, y + 2], fill=c)
        _line(draw, [(27, y), (44, y)], c, STROKE - 1.6)


def icon_compass(draw, c):
    _circle(draw, 32, 32, 21, c, STROKE)
    _poly(draw, [(40, 24), (35, 35), (24, 40), (29, 29)], c)


ICONS = {
    "ic-calendar": icon_calendar,
    "ic-location": icon_location,
    "ic-ticket": icon_ticket,
    "ic-users": icon_users,
    "ic-arrow": icon_arrow,
    "ic-check": icon_check,
    "ic-clock": icon_clock,
    "ic-shield": icon_shield,
    "ic-camera": icon_camera,
    "ic-close": icon_close,
    "ic-minus": icon_minus,
    "ic-plus": icon_plus,
    "ic-pencil": icon_pencil,
    "ic-image": icon_image,
    "ic-home": icon_home,
    "ic-list": icon_list,
    "ic-compass": icon_compass,
}


def write_icon(name: str, painter, color, size: int) -> None:
    img, draw = _canvas(size)
    painter(draw, color)
    img.save(ICON_DIR / f"{name}.png")


def build_icons() -> None:
    for name, painter in ICONS.items():
        write_icon(name, painter, INK, GRID)
    for name, painter in (("ic-location", icon_location), ("ic-users", icon_users)):
        write_icon(f"{name}-muted", painter, MUTED, GRID)
    write_icon("tab-home", icon_home, TAB_IDLE, 81)
    write_icon("tab-home-active", icon_home, BRAND, 81)
    write_icon("tab-list", icon_list, TAB_IDLE, 81)
    write_icon("tab-list-active", icon_list, BRAND, 81)
    write_icon("tab-publish", icon_pencil, TAB_IDLE, 81)
    write_icon("tab-publish-active", icon_pencil, BRAND, 81)
    write_icon("tab-mine", icon_users, TAB_IDLE, 81)
    write_icon("tab-mine-active", icon_users, BRAND, 81)


def _vertical_gradient(size, top, bottom):
    w, h = size
    img = Image.new("RGB", (1, h))
    px = img.load()
    for y in range(h):
        t = y / max(h - 1, 1)
        px[0, y] = tuple(int(top[i] + (bottom[i] - top[i]) * t) for i in range(3))
    return img.resize((w, h), Image.BICUBIC)


def cover_dawn(w=750, h=420):
    img = _vertical_gradient((w, h), (28, 38, 68), (240, 158, 96)).convert("RGBA")
    d = ImageDraw.Draw(img)
    d.ellipse([w * 0.62, h * 0.18, w * 0.62 + 92, h * 0.18 + 92], fill=(255, 214, 150, 255))
    glow = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ImageDraw.Draw(glow).ellipse(
        [w * 0.62 - 46, h * 0.18 - 46, w * 0.62 + 138, h * 0.18 + 138],
        fill=(255, 196, 120, 150),
    )
    img = Image.alpha_composite(img, glow.filter(ImageFilter.GaussianBlur(34)))
    d = ImageDraw.Draw(img)
    _poly(d, [(0, 300), (140, 196), (250, 268), (360, 178), (520, 286), (640, 226), (750, 292), (750, 420), (0, 420)], (44, 58, 96, 255))
    _poly(d, [(0, 344), (180, 268), (330, 330), (500, 262), (750, 336), (750, 420), (0, 420)], (26, 36, 62, 255))
    return img


def cover_night(w=750, h=420):
    img = _vertical_gradient((w, h), (24, 26, 58), (74, 46, 92)).convert("RGBA")
    glow = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    for x in range(70, w, 96):
        gd.ellipse([x - 40, 46 - 40, x + 40, 46 + 40], fill=(255, 196, 118, 170))
    img = Image.alpha_composite(img, glow.filter(ImageFilter.GaussianBlur(26)))
    d = ImageDraw.Draw(img)
    for x in range(70, w, 96):
        d.ellipse([x - 17, 46 - 17, x + 17, 46 + 17], fill=(255, 214, 140, 255))
        d.line([(x, 46 + 17), (x, 46 + 58)], fill=(255, 214, 140, 200), width=3)
    for i, x in enumerate((30, 250, 470, 690)):
        top = 150 + (i % 2) * 26
        _poly(d, [(x, top), (x + 96, top), (x + 48, top - 30)], (214, 92, 82, 255))
        _poly(d, [(x, top), (x + 96, top), (x + 96, top + 62), (x, top + 62)], (58, 44, 70, 255))
        d.ellipse([x + 36, top + 20, x + 60, top + 44], fill=(255, 206, 128, 220))
    _poly(d, [(0, 330), (w, 330), (w, 420), (0, 420)], (30, 26, 52, 255))
    return img


def cover_island(w=750, h=420):
    img = _vertical_gradient((w, h), (128, 206, 226), (232, 244, 248)).convert("RGBA")
    d = ImageDraw.Draw(img)
    d.ellipse([w * 0.74, 54, w * 0.74 + 78, 54 + 78], fill=(255, 238, 190, 255))
    _poly(d, [(0, 232), (150, 196), (300, 238), (470, 190), (620, 234), (750, 204), (750, 300), (0, 300)], (86, 176, 196, 255))
    _poly(d, [(0, 262), (200, 238), (420, 268), (620, 236), (750, 258), (750, 420), (0, 420)], (42, 140, 168, 255))
    _poly(d, [(0, 336), (180, 306), (400, 330), (600, 300), (750, 322), (750, 420), (0, 420)], (242, 232, 206, 255))
    d.rectangle([104, 176, 112, 300], fill=(74, 58, 44, 255))
    for ang, rad in ((-58, 92), (-122, 92), (-90, 108)):
        ex = 108 + rad * math.cos(math.radians(ang))
        ey = 196 + rad * math.sin(math.radians(ang))
        d.ellipse([ex - 44, ey - 26, ex + 44, ey + 26], fill=(58, 142, 96, 255))
    return img


def cover_default(w=750, h=420):
    """中性兜底主图：活动 slug 未命中时不误用其它活动的画面。"""
    img = _vertical_gradient((w, h), (108, 124, 152), (176, 190, 214)).convert("RGBA")
    d = ImageDraw.Draw(img)
    _poly(d, [(0, 300), (150, 236), (280, 288), (420, 220), (560, 292), (700, 244), (750, 276),
              (750, 420), (0, 420)], (92, 106, 134, 255))
    _poly(d, [(0, 348), (200, 306), (420, 336), (620, 302), (750, 330), (750, 420), (0, 420)],
          (74, 88, 114, 255))
    d.ellipse([w * 0.5 - 40, 56, w * 0.5 + 40, 136], fill=(236, 240, 246, 235))
    return img


def cover_city(w=750, h=420):
    """城市漫步：城市天际线与街道的扁平插画。"""
    img = _vertical_gradient((w, h), (236, 198, 168), (248, 232, 214)).convert("RGBA")
    d = ImageDraw.Draw(img)
    d.ellipse([w * 0.7, 62, w * 0.7 + 84, 62 + 84], fill=(255, 236, 198, 255))
    # 远景楼群
    _poly(d, [(0, 250), (90, 168), (176, 250), (176, 420), (0, 420)], (150, 160, 186, 255))
    _poly(d, [(176, 262), (268, 186), (360, 262), (360, 420), (176, 420)], (166, 174, 198, 255))
    _poly(d, [(360, 240), (470, 152), (580, 240), (580, 420), (360, 420)], (138, 148, 176, 255))
    _poly(d, [(580, 268), (672, 200), (750, 268), (750, 420), (580, 420)], (162, 172, 196, 255))
    # 街道
    _poly(d, [(0, 344), (750, 320), (750, 420), (0, 420)], (86, 96, 122, 255))
    _poly(d, [(0, 372), (750, 350), (750, 420), (0, 420)], (72, 82, 106, 255))
    # 窗格点缀
    for x in (30, 66, 118, 210, 250, 400, 448, 620, 664, 706):
        for y in (196, 232):
            d.rectangle([x, y, x + 14, y + 20], fill=(246, 226, 186, 190))
    return img


def cover_read(w=750, h=420):
    """共读共学：书页与桌面光影的扁平插画。"""
    img = _vertical_gradient((w, h), (226, 232, 240), (246, 248, 252)).convert("RGBA")
    d = ImageDraw.Draw(img)
    # 桌面
    _poly(d, [(0, 316), (750, 316), (750, 420), (0, 420)], (198, 206, 220, 255))
    # 展开的书
    _poly(d, [(375, 196), (150, 232), (150, 348), (375, 320)], (255, 255, 255, 255))
    _poly(d, [(375, 196), (600, 232), (600, 348), (375, 320)], (240, 243, 249, 255))
    _line(d, [(375, 196), (375, 320)], (176, 186, 204, 255), 3.0)
    # 书页文字线
    for i, y in enumerate((238, 262, 286)):
        _line(d, [(186, y + i * 2), (338, y + 10)], (196, 204, 218, 255), 4.0)
        _line(d, [(412, y + 10), (564, y + i * 2)], (206, 214, 226, 255), 4.0)
    # 光晕
    glow = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ImageDraw.Draw(glow).ellipse([w * 0.28, 40, w * 0.28 + 260, 300], fill=(255, 226, 168, 120))
    img = Image.alpha_composite(img, glow.filter(ImageFilter.GaussianBlur(40)))
    return img


def build_covers() -> None:
    cover_dawn().save(COVER_DIR / "dawn-trek.png")
    cover_night().save(COVER_DIR / "night-market.png")
    cover_island().save(COVER_DIR / "island-week.png")
    cover_city().save(COVER_DIR / "city-walk.png")
    cover_read().save(COVER_DIR / "co-reading.png")
    cover_default().save(COVER_DIR / "default.png")


def main() -> None:
    ICON_DIR.mkdir(parents=True, exist_ok=True)
    COVER_DIR.mkdir(parents=True, exist_ok=True)
    build_icons()
    build_covers()
    icons = sorted(p.name for p in ICON_DIR.glob("*.png"))
    covers = sorted(p.name for p in COVER_DIR.glob("*.png"))
    print(f"icons: {len(icons)} -> {icons}")
    print(f"covers: {len(covers)} -> {covers}")


if __name__ == "__main__":
    main()
