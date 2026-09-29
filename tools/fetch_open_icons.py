#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把 game-icons.net（CC BY 3.0，宽松署名许可）的开源图标固化进 OreUI 的 Emoji 目录，
替换原先的 Mojang 版权基岩版字形（U+E000..U+E10C）。

为什么是 game-icons.net：
  - Kenney 全站没有「MC 物品」类图标（Game Icons 实测仅 3 个码点能匹配，RPG Icons 在站点 404）。
  - game-icons.net 是专门的图标库，sword/shield/potion/heart/coin/apple/chest/工作台类图标基本齐全，
    能覆盖绝大多数 MC 语义码点；仅 pickaxe/shovel/hoe/minecart 4 个无对应，会留空（McTextBlock 有缺失保护，不崩）。
  - 许可：CC BY 3.0（**非 copyleft**，可商用、可打进 MIT 包），但**必须随包附署名**。

源（本机有网时准备）：
  git clone --depth 1 https://github.com/game-icons/icons.git <source>
  源是 SVG；本脚本用 ImageMagick `magick` 转成白色线条 PNG（currentColor->#fff，透明底），
  以适配 OreUI 的深色背景。

用法：
  python3 tools/fetch_open_icons.py /tmp/game-icons-src
  python3 tools/fetch_open_icons.py /tmp/game-icons-src --dry-run   # 只看计划/缺失，不转不写
  python3 tools/fetch_open_icons.py /tmp/game-icons-src --map my_map.json   # 精确覆盖
  ~/dotnet11x64/dotnet build src/OreUI/OreUI.csproj -c Debug        # 验证嵌入
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import argparse
from datetime import datetime
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
EMOJI_DIR = REPO / "src" / "OreUI" / "Assets" / "Emoji"
MAGICK = shutil.which("magick") or "/opt/homebrew/bin/magick"
DEFAULT_SIZE = 128

# 码点(小写 eXXXX，对应基岩版 PUA 特殊字符区 U+E000..U+E10C；e1000+ 为扩展 PUA，技术合法)
# -> game-icons 的 SVG 基名（精确优先，取 rglob 第一个命中）。
# 语义取自基岩版定义；game-icons 命名见 https://game-icons.net
DEFAULT_MAP = {
    # —— 演示 / 标签栏强依赖 ——
    "e10c": ["ball-heart"],            # 生命/爱心（game-icons 无裸 heart，用 ball-heart）
    "e102": ["coins"],                 # 金币
    "e107": ["allied-star"],           # 实心星（成就/经验）
    "e106": ["allied-star"],           # 空心星（同图）
    "e109": ["broadsword"],            # 木剑 -> 阔剑
    "e108": ["pickaxe"],               # 木镐（game-icons 无 pickaxe -> 缺失留空）
    "e100": ["shiny-apple"],           # 食物/苹果
    "e101": ["chest-armor"],           # 盔甲（胸甲）
    "e10a": ["crafting"],              # 工作台
    "e10b": ["furnace"],               # 熔炉
    # —— 常用补充 ——
    "e000": ["book-cover"],            # 书
    "e001": ["book-aura"],             # 附魔书
    "e1000": ["compass"],              # 指南针
    "e1001": ["alarm-clock"],          # 钟
    "e1002": ["treasure-map"],         # 地图
    "e1003": ["chest"],                # 箱子
    "e1004": ["bed"],                  # 床
    "e1005": ["anvil"],                # 铁砧
    "e1006": ["wooden-sign"],          # 牌子
    "e1007": ["all-seeing-eye"],       # 末影之眼
    "e1008": ["round-potion"],         # 药水
    "e1009": ["broadsword"],           # 剑（通用）
    "e100a": ["battle-axe"],           # 斧
    "e100b": ["shovel"],               # 铲（game-icons 无 -> 缺失留空）
    "e100c": ["hoe"],                  # 锄（game-icons 无 -> 缺失留空）
    "e100d": ["bow-arrow"],            # 弓
    "e100e": ["shield"],               # 盾
    "e100f": ["fishing-hook"],         # 钓竿
    "e1010": ["torch"],                # 火把
    "e1011": ["wooden-door"],          # 门
    "e1012": ["beach-bucket"],         # 桶
    "e1013": ["minecart"],             # 矿车（game-icons 无 -> 缺失留空）
    "e1014": ["boat-horizon"],         # 船
    "e1015": ["bat-wing"],             # 鞘翅
    "e1016": ["trident"],              # 三叉戟
    "e1017": ["crossbow"],             # 弩
    "e1018": ["snowflake-1"],          # 雪球/雪花
    "e1019": ["oyster-pearl"],         # 末影珍珠
    "e101a": ["flint-spark"],          # 打火石
    "e101b": ["shears"],               # 剪刀
    "e101c": ["saddle"],               # 鞍
}

# 演示/标签栏强依赖的码点（缺失会明显影响展示，打印时高亮）
KEY_CODEPOINTS = {"e10c", "e102", "e107", "e109", "e108", "e100", "e101", "e10a", "e10b"}


def parse_args():
    ap = argparse.ArgumentParser(description="固化 game-icons.net (CC BY 3.0) 开源图标到 OreUI Emoji 目录")
    ap.add_argument("source", help="game-icons 仓库根目录（含 icons/<author>/<name>.svg）")
    ap.add_argument("--map", help="可选 JSON：{码点: svg基名或[基名,...]} 精确覆盖")
    ap.add_argument("--size", type=int, default=DEFAULT_SIZE, help="输出 PNG 边长（默认 128）")
    ap.add_argument("--dry-run", action="store_true", help="只打印计划与缺失，不转换/不写")
    return ap.parse_args()


def backup_existing(dry: bool) -> None:
    if not EMOJI_DIR.exists():
        EMOJI_DIR.mkdir(parents=True, exist_ok=True)
        return
    existing = [f for f in EMOJI_DIR.glob("*.png") if f.name.startswith("e")]
    if not existing:
        return
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    bak = Path(f"/tmp/oreui_emoji_backup_{ts}")
    if dry:
        print(f"[dry-run] 将备份 {len(existing)} 张旧(Mojang)图到 {bak}")
        return
    bak.mkdir(parents=True, exist_ok=True)
    for f in existing:
        shutil.move(str(f), str(bak / f.name))
    print(f"已备份 {len(existing)} 张旧(Mojang)图到 {bak}")


def resolve_svg(source: Path, base: str):
    hits = [h for h in source.rglob(f"{base}.svg") if h.is_file()]
    return hits[0] if hits else None


def convert_svg(src: Path, dst: Path, size: int) -> bool:
    try:
        txt = src.read_text(encoding="utf-8")
    except Exception as e:
        print(f"  [!] 读 SVG 失败 {src.name}: {e}")
        return False
    # game-icons 用 currentColor，ImageMagick 默认渲染成透明 -> 先替换为白色线条
    txt = txt.replace("currentColor", "#ffffff")
    tmp = dst.with_suffix(".svg.tmp")
    tmp.write_text(txt, encoding="utf-8")
    r = subprocess.run(
        [MAGICK, str(tmp), "-background", "none", "-resize", f"{size}x{size}", str(dst)],
        capture_output=True, text=True,
    )
    tmp.unlink(missing_ok=True)
    if r.returncode != 0 or not dst.exists():
        print(f"  [!] magick 转换失败 {src.name}: {r.stderr.strip()[:200]}")
        return False
    return True


def copy_upstream_license(source: Path, dry: bool) -> None:
    """CC BY 3.0 要求再分发时附带上游 LICENSE 与署名。"""
    hits = [h for h in source.glob("license*") if h.is_file()] or \
           [h for h in source.glob("LICENSE*") if h.is_file()]
    if not hits:
        print("  [警告] 源仓库根未找到 license* 文件，请手动核实许可并按需放入 Emoji/LICENSE_game-icons.txt")
        return
    dst = EMOJI_DIR / "LICENSE_game-icons.txt"
    if dry:
        print(f"[dry-run] 将拷贝上游 LICENSE -> {dst} （{hits[0].name}）")
        return
    shutil.copy(str(hits[0]), str(dst))
    print(f"已拷贝上游 LICENSE -> {dst}")


LICENSE_TEMPLATE = """# Emoji 图标许可说明

本目录下的字形图标用于替换 Mojang 版权的基岩版 PUA 字形（U+E000..U+E10C）。

- 图标来源：game-icons.net（https://game-icons.net）
- 仓库：https://github.com/game-icons/icons
- 许可：**CC BY 3.0**（Creative Commons Attribution 3.0 Unported，见同目录 LICENSE_game-icons.txt）
- 作者：game-icons.net 各图标作者（lorc、delapouite、sbed、Skoll 等，详见仓库 README.md）

⚠ 署名义务（必须随包保留本说明与 LICENSE_game-icons.txt）：
  CC BY 3.0 **不是** copyleft，可商用、可打进 MIT 包；但必须**署名**原作者与 game-icons.net，
  且若修改了图标，修改版须以相同许可（CC BY 3.0）提供。
  仅本地使用也建议保留署名，以示对原作者的尊重。

缺失码点（game-icons 无对应图标，McTextBlock 加载时留空不崩）：
  pickaxe(木镐 e108) / shovel(铲 e100b) / hoe(锄 e100c) / minecart(矿车 e1013)。
"""


def main() -> None:
    args = parse_args()
    src = Path(args.source).expanduser().resolve()
    if not src.exists():
        print(f"错误：源目录不存在 {src}", file=sys.stderr)
        sys.exit(1)
    EMOJI_DIR.mkdir(parents=True, exist_ok=True)

    mapping = DEFAULT_MAP
    if args.map:
        with open(args.map, encoding="utf-8") as f:
            custom = json.load(f)
        mapping = {k.lower(): v for k, v in custom.items()}

    backup_existing(args.dry_run)
    copy_upstream_license(src, args.dry_run)

    ok, miss = [], []
    for cp, cands in sorted(mapping.items()):
        cands = [cands] if isinstance(cands, str) else list(cands)
        hit = None
        for base in cands:
            hit = resolve_svg(src, base)
            if hit:
                break
        dst = EMOJI_DIR / f"{cp.lower()}.png"
        star = " [关键]" if cp in KEY_CODEPOINTS else ""
        if hit is None:
            miss.append(cp)
            print(f"  [缺] {cp}{star}: 未匹配到源图（game-icons 无对应）")
            continue
        if args.dry_run:
            print(f"  [计划] {cp}{star} <- {hit}")
            ok.append(cp)
            continue
        if convert_svg(hit, dst, args.size):
            ok.append(cp)
            print(f"  [✓] {cp}{star} <- {hit.name}")
        else:
            miss.append(cp)
            print(f"  [✗] {cp}{star}: 转换失败")

    note = EMOJI_DIR / "EMOJI_LICENSE_NOTE.md"
    note.write_text(LICENSE_TEMPLATE, encoding="utf-8")

    print(f"\n完成：成功 {len(ok)} 张，缺失 {len(miss)} 张")
    if miss:
        print("缺失码点（McTextBlock 留空不崩）：", ", ".join(miss))
        key_miss = [m for m in miss if m in KEY_CODEPOINTS]
        if key_miss:
            print("⚠ 关键码点缺失（影响标签栏展示）：", ", ".join(key_miss))
    print(f"许可署名模板已写到：{note}")


if __name__ == "__main__":
    main()
