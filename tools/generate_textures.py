#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CodeHub-OreUI 纹理生成器 (faithful rebuild)
按 Minecraft Bedrock Edition 官方 OreUI 设计系统精确重建 9-slice 像素纹理。

设计依据（中文 Minecraft Wiki `.mcbutton-oreui` 真实 CSS，2026-09 查实）：
  - 真实 OreUI 按钮 = 纯色填充 + 底部 2px 暗带 + 左上 1px 白色高光 + 右下 1px 白色高光
    （对应 CSS: box-shadow: inset 0 -2px <暗带>,
                            inset 1px 1px rgba(255,255,255,.3),
                            inset -1px -3px rgba(255,255,255,.2)）
  - 没有整圈描边，没有整块垂直渐变（旧生成器这两点都错了，是"看起来不像"的根因）。

精确配色（来自 wiki）：
  primary     bg #3C8527 / dark #1D4C14 / 高光白 0.3,0.2
  destructive bg #C93635 / dark #AD1C1C / 高光白 0.3,0.2
  realms      bg #7444E5 / dark #4A1BAC / 高光彩 #A264F2,#8D4BEC
  tab         bg #48494B / dark #313234 / 高光白 0.3,0.2
  disabled    bg #D0D1D4 / dark #B1B2B5 / 外框 #8C8D90（无高光）
  secondary   bg #D9D9D9 / dark #B5B5B5 / 高光白 0.5,0.4（浅灰按钮，强高光更显立体）

输出：src/OreUI/Assets/Textures/  （保持全部 162 个文件名不变，XAML 引用无需改动）
用法：python3 tools/generate_textures.py
"""
import os
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "src", "OreUI", "Assets", "Textures")
os.makedirs(OUT, exist_ok=True)

SLICE = 4  # 9 宫格切片边宽（与 Button/Tab/Field 的 4px 网格一致）


def blend(px, x, y, color, alpha):
    """把 color 以 alpha(0..1) 叠加到像素 (x,y) 上。"""
    r, g, b = color
    cur = px[x, y]
    a = alpha
    nr = int(round(cur[0] * (1 - a) + r * a))
    ng = int(round(cur[1] * (1 - a) + g * a))
    nb = int(round(cur[2] * (1 - a) + b * a))
    na = max(cur[3], int(round(255 * a)))
    px[x, y] = (nr, ng, nb, na)


def fill(img, color):
    px = img.load()
    for y in range(img.size[1]):
        for x in range(img.size[0]):
            px[x, y] = (color[0], color[1], color[2], 255)
    return img


def make_ore_button(bg, dark, hi_tl=(255, 255, 255, 0.3), hi_br=(255, 255, 255, 0.2)):
    """16x16 OreUI 按钮（默认态）。

    结构（与 wiki CSS 逐像素对应）：
      1) 纯色填充 bg
      2) 右下高光（inset -1px -3px）：右 1px 列 + 底部 3px 行
      3) 左上高光（inset 1px 1px）：左 1px 列 + 顶部 1px 行
      4) 底部 2px 暗带（inset 0 -2px）：最后绘制，覆盖底部，形成真实下沿斜面
    无整圈描边、无渐变。
    """
    img = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
    px = img.load()
    fill(img, bg)

    # 2) 右下高光（先画，会被暗带压住底部 2 行）
    r2, g2, b2, a2 = hi_br
    for x in range(16):
        blend(px, x, 13, (r2, g2, b2), a2)      # 底部第 13 行（底部 3px 之一）
    for y in range(16):
        blend(px, 15, y, (r2, g2, b2), a2)       # 右 1px 列

    # 3) 左上高光
    r1, g1, b1, a1 = hi_tl
    for x in range(16):
        blend(px, x, 0, (r1, g1, b1), a1)        # 顶部 1px 行
    for y in range(16):
        blend(px, 0, y, (r1, g1, b1), a1)        # 左 1px 列

    # 4) 底部 2px 暗带（最后，覆盖一切）
    for x in range(16):
        for y in range(14, 16):
            px[x, y] = (dark[0], dark[1], dark[2], 255)
    return img


def make_disabled(bg, dark, border):
    """16x16 禁用按钮：浅灰填充 + 1px 外框 + 底部 2px 暗带（无高光，wiki 规范）。"""
    img = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
    px = img.load()
    fill(img, bg)
    for x in range(16):
        px[x, 0] = border
        px[x, 15] = border
    for y in range(16):
        px[0, y] = border
        px[15, y] = border
    for x in range(16):               # 底部 2px 暗带压住外框
        px[x, 14] = dark
        px[x, 15] = dark
    return img


def make_field():
    """16x16 输入框：深色凹陷，1px 黑外框（focus 绿框由 XAML 叠加）。9-slice。"""
    img = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
    px = img.load()
    fill(img, (0x1E, 0x1E, 0x1E))
    blk = (0, 0, 0, 255)
    for x in range(16):
        px[x, 0] = blk
        px[x, 15] = blk
    for y in range(16):
        px[0, y] = blk
        px[15, y] = blk
    return img


def make_panel(color):
    """16x16 面板：纯色平铺（直接 Fill 拉伸用，平色避免拉伸出粗边）。9-slice（9 块同色，安全）。"""
    return Image.new("RGBA", (16, 16), (color[0], color[1], color[2], 255))


def make_slot():
    """18x18 物品槽：深底 + 1px 灰框 + 外黑。9-slice。"""
    img = Image.new("RGBA", (18, 18), (0, 0, 0, 0))
    px = img.load()
    fill(img, (0x1A, 0x1A, 0x1A))
    edge = (0x4A, 0x4A, 0x4A, 255)
    for x in range(18):
        px[x, 1] = edge
        px[x, 16] = edge
    for y in range(18):
        px[1, y] = edge
        px[16, y] = edge
    blk = (0, 0, 0, 200)
    for x in range(18):
        px[x, 0] = blk
        px[x, 17] = blk
    for y in range(18):
        px[0, y] = blk
        px[17, y] = blk
    return img


def make_toggle(on):
    """27x14 开关轨道：绿/灰，顶部 1px 高光 + 底部 2px 暗带（外框由 XAML 加）。直接 Fill。"""
    w, h = 27, 14
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    px = img.load()
    if on:
        bg, dark = (0x3C, 0x85, 0x27), (0x1D, 0x4C, 0x14)
    else:
        bg, dark = (0x5A, 0x5A, 0x5A), (0x3A, 0x3A, 0x3A)
    fill(img, bg)
    for x in range(w):
        blend(px, x, 0, (255, 255, 255), 0.25)   # 顶部高光
    for x in range(w):
        for y in range(h - 2, h):
            px[x, y] = (dark[0], dark[1], dark[2], 255)  # 底部暗带
    return img


def make_thumb():
    """16x16 滑块/开关拇指：白方块，圆角透明，顶高光 + 底暗。直接 Fill（toggle 12px / slider 16px 复用）。"""
    img = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
    px = img.load()
    body = (0xE8, 0xE8, 0xE8)
    for y in range(16):
        for x in range(16):
            px[x, y] = (body[0], body[1], body[2], 255)
    for cx, cy in [(0, 0), (15, 0), (0, 15), (15, 15)]:
        px[cx, cy] = (0, 0, 0, 0)               # 四角透明（圆角感）
    for x in range(16):
        blend(px, x, 0, (255, 255, 255), 0.6)
        blend(px, x, 1, (255, 255, 255), 0.3)
    for x in range(16):
        px[x, 15] = (0xB5, 0xB5, 0xB5, 255)     # 底部暗
    return img


def make_bar(color):
    """8x6 滑块轨道/进度：纯色。直接 Fill。"""
    return Image.new("RGBA", (8, 6), (color[0], color[1], color[2], 255))


def nine_slice(img, base):
    """把图片切成 9-slice（SLICE 像素边界）：_tl/_t/_tr/_l/_c/_r/_bl/_b/_br。"""
    s = SLICE
    w, h = img.size
    pieces = {
        "tl": (0, 0, s, s), "t": (s, 0, w - s, s), "tr": (w - s, 0, w, s),
        "l": (0, s, s, h - s), "c": (s, s, w - s, h - s), "r": (w - s, s, w, h - s),
        "bl": (0, h - s, s, h), "b": (s, h - s, w - s, h), "br": (w - s, h - s, w, h),
    }
    for name, box in pieces.items():
        img.crop(box).save(os.path.join(OUT, f"{base}_{name}.png"))


def emit(img, base, slice_it=True):
    img.save(os.path.join(OUT, f"{base}.png"))
    if slice_it:
        nine_slice(img, base)


def main():
    # ---- 按钮变体（默认态；hover/pressed 由 Avalonia 覆盖层处理）----
    buttons = {
        # 名称         bg           暗带          左上高光           右下高光
        "primary":   dict(bg=(0x3C, 0x85, 0x27), dark=(0x1D, 0x4C, 0x14),
                          hi_tl=(255, 255, 255, 0.3), hi_br=(255, 255, 255, 0.2)),
        "secondary": dict(bg=(0xD9, 0xD9, 0xD9), dark=(0xB5, 0xB5, 0xB5),
                          hi_tl=(255, 255, 255, 0.5), hi_br=(255, 255, 255, 0.4)),
        "contrast":  dict(bg=(0xE0, 0xA8, 0x00), dark=(0xA8, 0x7A, 0x00),
                          hi_tl=(255, 255, 255, 0.3), hi_br=(255, 255, 255, 0.2)),
        "danger":    dict(bg=(0xC9, 0x36, 0x35), dark=(0xAD, 0x1C, 0x1C),
                          hi_tl=(255, 255, 255, 0.3), hi_br=(255, 255, 255, 0.2)),
        "realm":     dict(bg=(0x74, 0x44, 0xE5), dark=(0x4A, 0x1B, 0xAC),
                          hi_tl=(0xA2, 0x64, 0xF2, 1.0), hi_br=(0x8D, 0x4B, 0xEC, 1.0)),
    }
    for name, kw in buttons.items():
        emit(make_ore_button(**kw), f"btn_{name}")

    # disabled（专用结构：外框 + 暗带，无高光）
    emit(make_disabled((0xD0, 0xD1, 0xD4), (0xB1, 0xB2, 0xB5), (0x8C, 0x8D, 0x90)), "btn_disabled")

    # transparent：全透明 16x16（9-slice 同样全透明，XAML 引用 btn_transparent_*）
    emit(Image.new("RGBA", (16, 16), (0, 0, 0, 0)), "btn_transparent")

    # ---- 面板 / 输入框（平色，直接 Fill 拉伸安全）----
    emit(make_panel((0x1C, 0x1C, 0x1C)), "panel")
    emit(make_panel((0x24, 0x24, 0x24)), "panel_raised")
    emit(make_field(), "field")

    # ---- 开关 / 滑块（直接 Fill）----
    emit(make_toggle(False), "toggle_off", slice_it=False)
    emit(make_toggle(True), "toggle_on", slice_it=False)
    emit(make_thumb(), "thumb", slice_it=False)
    emit(make_bar((0x33, 0x33, 0x33)), "track", slice_it=False)
    emit(make_bar((0x3C, 0x85, 0x27)), "progress", slice_it=False)

    # ---- 标签页（默认态结构）----
    emit(make_ore_button((0x48, 0x49, 0x4B), (0x31, 0x32, 0x34),
                         (255, 255, 255, 0.3), (255, 255, 255, 0.2)), "tab_normal")
    emit(make_ore_button((0x3C, 0x85, 0x27), (0x1D, 0x4C, 0x14),
                         (255, 255, 255, 0.3), (255, 255, 255, 0.2)), "tab_selected")

    # ---- 物品槽 ----
    emit(make_slot(), "slot")

    count = len([f for f in os.listdir(OUT) if f.endswith(".png")])
    print(f"generated {count} textures -> {OUT}")


if __name__ == "__main__":
    main()
