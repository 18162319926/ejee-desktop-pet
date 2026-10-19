"""从 base.png 里把头顶那片叶子拆出来，生成三份素材：

    assets/leaf.png       叶子本体（透明底，原色）
    assets/leaf_dry.png   同一片叶子调到枯黄色（与 leaf.png 按 ha 混合）
    assets/base_body.png  去掉叶子的底图（叶子覆盖处：头皮补橙色、天空留透明）

运行：  python tools/make_leaf_assets.py
输出还会打印 leaf_geo（设计坐标），供 ejee_pet.py 的 LEAF_GEO 使用。
"""
import json
import os
import sys

import numpy as np
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = os.path.join(ROOT, "assets", "base.png")
PAD = 2


def main():
    im = Image.open(BASE).convert("RGBA")
    a = np.array(im).astype(np.int16)
    r, g, b, al = a[..., 0], a[..., 1], a[..., 2], a[..., 3]

    # 叶子在头顶上方那一小块里是唯一的不透明物体：先用 ROI 框住（基图
    # 1548×1236 下叶子占 x 582..858 / y 0..258），再用「g > r」把橙色头皮
    # 排除掉。比单纯卡 g-r 阈值更不容易漏掉偏黄的叶尖。
    hsv_src = np.array(im.convert("RGB").convert("HSV")).astype(np.int16)
    hue, sat, val = hsv_src[..., 0], hsv_src[..., 1], hsv_src[..., 2]
    roi = np.zeros((im.height, im.width), bool)
    roi[0:290, 555:890] = True
    core = roi & (al > 26) & (g > r + 2) & (g > 55)
    ys, xs = np.nonzero(core)
    if len(xs) == 0:
        sys.exit("no green pixels found in base.png")

    def dilate(m, n):
        out = m.copy()
        for _ in range(n):
            p = np.pad(out, 1, mode="constant", constant_values=False)
            out = (p[:-2, 1:-1] | p[2:, 1:-1] | p[1:-1, :-2] | p[1:-1, 2:]
                   | p[:-2, :-2] | p[:-2, 2:] | p[2:, :-2] | p[2:, 2:])
        return out

    mask = dilate(core, 2)          # 覆盖抗锯齿过渡带
    ys, xs = np.nonzero(mask)
    x0, x1 = max(0, xs.min() - PAD), min(im.width, xs.max() + 1 + PAD)
    y0, y1 = max(0, ys.min() - PAD), min(im.height, ys.max() + 1 + PAD)
    w, h = x1 - x0, y1 - y0

    sub = a[y0:y1, x0:x1]
    sm = mask[y0:y1, x0:x1]

    # ---- leaf.png：mask 内保留原色（羽化一点，边缘不至于像剪贴画）----
    leaf = sub.copy()
    leaf[..., 3] = np.where(sm, sub[..., 3], 0).astype(np.int16)
    Image.fromarray(leaf.astype(np.uint8), "RGBA").save(
        os.path.join(ROOT, "assets", "leaf.png"))

    # ---- leaf_dry.png：色相绿→黄褐、略降饱和与明度 ----
    leaf_im = Image.fromarray(leaf.astype(np.uint8), "RGBA")
    hsv = np.array(leaf_im.convert("RGB").convert("HSV")).astype(np.float32)
    hh, ss, vv = hsv[..., 0], hsv[..., 1], hsv[..., 2]
    # PIL 的 H 是 0..255 环形：绿≈85，黄≈42，橙褐≈25
    hh = 85.0 + (hh - 85.0) * 0.18        # 先压缩到绿的附近，避免混色
    hh = np.where(ss > 8, 34.0, hh)       # 叶子整体转到土黄
    hh = hh + (vv / 255.0 - 0.5) * 8.0
    ss = np.clip(ss * 0.86, 0, 255)
    vv = np.clip(vv * 0.86, 0, 255)
    dry_rgb = np.stack([hh, ss, vv], -1).astype(np.uint8)
    dry = Image.fromarray(dry_rgb, "HSV").convert("RGB").convert("RGBA")
    dry.putalpha(leaf_im.split()[3])
    dry.save(os.path.join(ROOT, "assets", "leaf_dry.png"))

    # ---- base_body.png：把叶子“拿掉” ----
    # 只沿“核心叶子”向下找最近的皮肤像素；悬空部分下方几十像素内都没有
    # 橙色，就保持透明（否则会在头顶上方补出一块浅色补丁）。
    body = a.copy()
    out = body.copy()
    ys_, xs_ = np.nonzero(mask)
    for y, x in zip(ys_, xs_):
        yy = y + 1
        lim = min(im.height, y + 70)
        while yy < lim and (core[yy, x] or al[yy, x] < 180):
            yy += 1
        if yy < lim and al[yy, x] >= 180 and core[yy, x] is False:
            out[y, x] = body[yy, x]
        else:
            out[y, x, 3] = 0
    Image.fromarray(out.astype(np.uint8), "RGBA").save(
        os.path.join(ROOT, "assets", "base_body.png"))

    # ---- 旋转轴：叶子与头皮相接处的最低点 ----
    orange = (al > 200) & (~core)
    contact = core & dilate(orange, 1)
    cy_, cx_ = np.nonzero(contact)
    if len(cx_):
        ymax = cy_.max()
        sel = cx_[cy_ >= ymax - 3]
        ax, ay = float(np.median(sel)), float(ymax)
    else:
        ax, ay = float(x0 + w / 2), float(y1)

    # 换算到设计坐标：底图绘制在 x 49..341 / y 85..318
    s = 292.0 / 1548.0
    geo = {
        "x": round(49.0 + x0 * s, 2), "y": round(85.0 + y0 * s, 2),
        "w": round(w * s, 2), "h": round(h * s, 2),
        "ax": round(49.0 + ax * s, 2), "ay": round(85.0 + ay * s, 2),
        "src": [int(x0), int(y0), int(w), int(h)],
    }
    print("leaf_geo =", json.dumps(geo))
    print("leaf.png / leaf_dry.png / base_body.png 已写入 assets/")


if __name__ == "__main__":
    main()
