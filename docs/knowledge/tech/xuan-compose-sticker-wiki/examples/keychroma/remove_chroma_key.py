# SPDX-License-Identifier: GPL-2.0-only
"""均匀色幕（chroma-key）去底 —— 贴纸稿 → 透明底 PNG（教学示例）。

对应 travel-memory-card-duo 技能的第二步产物：贴纸先生成在**均匀纯色幕布**上
（普通场景用 #00ff00 绿幕，绿植丰盛场景用 #ff00ff 品红幕），再由本脚本抠除。

用法（容器内，/work/out 已由 compose 绑定到宿主 ./out）：

    python remove_chroma_key.py /work/out/stickers-chroma.png /work/out/stickers.png \
        --auto-key border --soft-matte --despill --edge-contract 1

退出码：成功且四角 alpha=0 时为 0；校验失败为 2（会原样透传为
``xuan-compose run`` 的退出码，便于在脚本/CI 中判定）。
"""

import argparse
import os
import sys

import numpy as np
from PIL import Image


def parse_color(text: str) -> np.ndarray:
    text = text.strip().lstrip("#")
    if len(text) != 6:
        raise ValueError(f"色幕颜色需为 #RRGGBB，收到: {text!r}")
    return np.array([int(text[i : i + 2], 16) for i in (0, 2, 4)], dtype=np.float32)


def sample_border_key(rgb: np.ndarray, mode: str) -> np.ndarray:
    """从边框采样色幕颜色（中位数，抗压缩噪点）。"""
    if mode == "corners":
        h, w, _ = rgb.shape
        k = max(2, min(h, w) // 100)
        patches = [
            rgb[:k, :k], rgb[:k, w - k :], rgb[h - k :, :k], rgb[h - k :, w - k :]
        ]
        border = np.concatenate([p.reshape(-1, 3) for p in patches], axis=0)
    else:  # border：上下左右各取 2 像素的整圈边框
        frame = np.concatenate(
            [
                rgb[:2].reshape(-1, 3),
                rgb[-2:].reshape(-1, 3),
                rgb[:, :2].reshape(-1, 3),
                rgb[:, -2:].reshape(-1, 3),
            ],
            axis=0,
        )
        border = frame
    return np.median(border, axis=0).astype(np.float32)


def erode_alpha(alpha: np.ndarray, iterations: int) -> np.ndarray:
    """对 alpha 做 3x3 最小值滤波（形态学腐蚀），吃掉边缘色幕光晕。"""
    if iterations <= 0:
        return alpha
    a = alpha
    for _ in range(iterations):
        padded = np.pad(a, 1, mode="edge")
        acc = padded[1:-1, 1:-1].copy()
        for dy, dx in ((-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)):
            acc = np.minimum(acc, padded[1 + dy : 1 + dy + a.shape[0], 1 + dx : 1 + dx + a.shape[1]])
        a = acc
    return a


def despill(rgb: np.ndarray, key: np.ndarray, alpha: np.ndarray, bias: float) -> np.ndarray:
    """去除半透明边缘上的色幕溢色（绿幕压绿、品红幕压红蓝）。"""
    out = rgb.copy()
    key_ch = [i for i, v in enumerate(key) if v >= 128]          # 色幕主通道
    keep_ch = [i for i, v in enumerate(key) if v < 128]          # 非色幕通道
    if not key_ch or not keep_ch:
        return out
    fringe = alpha < 255                                          # 只处理边缘过渡带
    keep_max = out[:, :, keep_ch].max(axis=2)
    for c in key_ch:
        out[:, :, c] = np.where(
            fringe, np.minimum(out[:, :, c], keep_max + bias), out[:, :, c]
        )
    return out


def remove_chroma(args: argparse.Namespace) -> tuple[np.ndarray, dict]:
    img = Image.open(args.input).convert("RGBA")
    arr = np.asarray(img).astype(np.float32)
    rgb, alpha_in = arr[:, :, :3], arr[:, :, 3]

    if args.auto_key == "none":
        key = parse_color(args.key)
    else:
        key = sample_border_key(rgb, args.auto_key)

    # RMS 色差（0..255），对压缩造成的幕布轻微不均更稳
    dist = np.sqrt(((rgb - key) ** 2).mean(axis=2))

    t, o = args.transparent_threshold, args.opaque_threshold
    if args.soft_matte:
        alpha = np.clip((dist - t) / max(o - t, 1e-6), 0.0, 1.0) * 255.0
    else:
        alpha = np.where(dist <= t, 0.0, 255.0)

    # 原图若自带 alpha，取交集，避免把已透明像素重新做实
    alpha = np.minimum(alpha, alpha_in)
    alpha = erode_alpha(alpha, args.edge_contract)

    rgb = despill(rgb, key, alpha, args.despill_bias) if args.despill else rgb

    rgba = np.dstack([np.clip(rgb, 0, 255), alpha]).astype(np.uint8)
    stats = {
        "key": "#%02x%02x%02x" % tuple(int(v) for v in key),
        "transparent_pct": round(float((alpha == 0).mean()) * 100, 1),
        "opaque_pct": round(float((alpha == 255).mean()) * 100, 1),
        "corners_alpha": [
            int(rgba[0, 0, 3]), int(rgba[0, -1, 3]), int(rgba[-1, 0, 3]), int(rgba[-1, -1, 3])
        ],
    }
    return rgba, stats


def main() -> int:
    ap = argparse.ArgumentParser(description="色幕去底 → 透明 PNG")
    ap.add_argument("input")
    ap.add_argument("output")
    ap.add_argument("--key", default=os.environ.get("CHROMA_KEY", "#00ff00"), help="显式色幕色 #RRGGBB")
    ap.add_argument("--auto-key", choices=["border", "corners", "none"], default="border")
    ap.add_argument("--transparent-threshold", type=float, default=12.0)
    ap.add_argument("--opaque-threshold", type=float, default=60.0)
    ap.add_argument("--soft-matte", action="store_true")
    ap.add_argument("--despill", action="store_true")
    ap.add_argument("--despill-bias", type=float, default=8.0)
    ap.add_argument("--edge-contract", type=int, default=0)
    args = ap.parse_args()

    rgba, stats = remove_chroma(args)
    Image.fromarray(rgba, "RGBA").save(args.output, format="PNG")

    print("[keychroma] 色幕 =", stats["key"])
    print(f"[keychroma] 全透明 {stats['transparent_pct']}% / 全不透明 {stats['opaque_pct']}%")
    print("[keychroma] 四角 alpha =", stats["corners_alpha"])

    corners_ok = all(v == 0 for v in stats["corners_alpha"])
    if not corners_ok:
        print("[keychroma] 校验失败：四角未全透明，请加大 --transparent-threshold 或检查幕布均匀度", file=sys.stderr)
        return 2
    print(f"[keychroma] OK → {args.output}（RGBA 透明底 PNG）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
