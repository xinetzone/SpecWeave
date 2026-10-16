# -*- coding: utf-8 -*-
"""R2 N1 修复：清除 facts 勘误段控制字符并还原被 PowerShell 转义吞掉的字符。"""
import pathlib

D = pathlib.Path(r"projects/awesome-okf-xs/doc/bundles/jishu/systems/kylin-wayland-compositor/references")

# 1) facts-effect-plugin.md：用完整正确段替换损坏的三行（含两个控制字符）
p = D / "facts-effect-plugin.md"
text = p.read_text(encoding="utf-8")
broken = (
    "- **勘 F-R4-024/025（option_value/option_type 口径）**：include/kywc/plugin.h:46-51 的 kywc_plugin_option_value 实际联合成员为 \n"
    "um（int）、str（char *）、\n"
)
# 直接按行切除损坏段（从标题行到 F-R4-031 行之前），用正确文本重建
lines = text.splitlines(keepends=True)
start = next(i for i, l in enumerate(lines) if l.startswith("- **勘 F-R4-024/025"))
end = next(i for i, l in enumerate(lines) if l.startswith("- **勘 F-R4-031"))
fixed_line = (
    "- **勘 F-R4-024/025（option_value/option_type 口径）**：include/kywc/plugin.h:46-51 的 "
    "`kywc_plugin_option_value` 实际联合成员为 `num`（int）、`str`（char *）、`realnum`（double）、"
    "`boolean`（bool），非早期采集所记的 i/f/ptr 口径；`enum kywc_plugin_option_type`（:53-59）实际取值为 "
    "null/boolean/double/int/string。examples/simple_plugin.c:21-27 可互证。concepts/11 与 examples/01 已按源码书写。\n"
)
lines[start:end] = [fixed_line]
text = "".join(lines)

# 2) facts-graphics.md：还原 `enum scene_role`（ESC 吞掉反引号 e）
p2 = D / "facts-graphics.md"
t2 = p2.read_text(encoding="utf-8")
t2 = t2.replace(
    "include/scene/scene.h:126-157 的 \x1bnum scene_role 共 25 个枚举器",
    "include/scene/scene.h:126-157 的 `enum scene_role` 共 25 个枚举器",
)

# 写回（无 BOM）并验证
for pp, tt in [(p, text), (p2, t2)]:
    assert "\x08" not in tt and "\x1b" not in tt, pp
    pp.write_text(tt, encoding="utf-8", newline="")
    bad = [b for b in pp.read_bytes() if b < 0x20 and b not in (9, 10, 13)]
    print(pp.name, "control chars after fix:", bad)

# 全束复扫
bundle = D.parent
bad_all = []
for f in bundle.rglob("*.md"):
    for i, b in enumerate(f.read_bytes()):
        if b < 0x20 and b not in (9, 10, 13):
            bad_all.append((f.relative_to(bundle), i, hex(b)))
print("bundle control chars:", bad_all if bad_all else "NONE")
