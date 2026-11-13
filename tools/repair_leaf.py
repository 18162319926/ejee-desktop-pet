"""修复头顶叶子：assets/leaf.png 的顶端被 base.png 的上边界切平了
（base.png 第 0 行上叶子还有 90px 宽，说明叶尖在原图之外），换成从
tools/src_4x.png（未裁切的 4 倍原图）重新抠出来的完整叶子。

做法：
  1. 从 src_4x.png 抠出叶子（HSV 饱和度 + 色相判据，含浅色叶尖）
  2. 用「旧叶子的逐行左右轮廓」和「源叶子的逐行轮廓」做最小二乘拟合，
     求出 缩放 s 与水平偏移 dx —— 保证新叶子和旧叶子在同一位置、同一
     大小，只是多出顶端那一截
  3. 以旧 asset 的像素尺度和宽度为基准重新生成 leaf.png / leaf_dry.png
  4. 打印新的 LEAF_GEO（设计坐标）

运行：python tools/repair_leaf.py            # 预览 + 打印 geo
      python tools/repair_leaf.py --write    # 写回 assets/
"""
import json
import os
import sys

import numpy as np
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "tools", "src_4x.png")
LEAF = os.path.join(ROOT, "assets", "leaf.png")
DRY = os.path.join(ROOT, "assets", "leaf_dry.png")
# 叶子在 src_4x.png 里的大致位置（角色头顶），留足余量
SRC_ROI = (2300, 930, 2900, 1500)


def spans(mask):
    """逐行左右轮廓：返回 [(row, left, right, width), ...]（只含有内容的行）"""
    out = []
    for i in range(mask.shape[0]):
        xs = np.nonzero(mask[i])[0]
        if len(xs):
            out.append((i, int(xs.min()), int(xs.max()), int(len(xs))))
    return out


def src_leaf_mask():
    im = Image.open(SRC).convert("RGBA")
    x0, y0, x1, y1 = SRC_ROI
    a = np.array(im.crop((x0, y0, x1, y1)))
    r, g, b, al = (a[..., i].astype(np.int16) for i in range(4))
    # 叶子是饱和绿色（叶尖偏浅但仍高饱和）；背景是低饱和的浅蓝。
    # 用 HSV 判据 + 绿色通道主导，避免叶尖浅色被漏掉。
    rgb = Image.fromarray(a[..., :3]).convert("HSV")
    hsv = np.array(rgb).astype(np.int16)
    sat, val = hsv[..., 1], hsv[..., 2]
    m = (al > 40) & (sat > 55) & (val > 60) & (g > b + 12) & (g >= r - 10)
    # 闭运算填掉渐变里的零星空洞（3x3 两次）
    for _ in range(2):
        p = np.pad(m, 1, constant_values=False)
        m = (p[:-2, 1:-1] & p[2:, 1:-1] & p[1:-1, :-2] & p[1:-1, 2:]
             & p[:-2, :-2] & p[:-2, 2:] & p[2:, :-2] & p[2:, 2:])
    ys, xs = np.nonzero(m)
    bx0, bx1, by0, by1 = xs.min(), xs.max(), ys.min(), ys.max()
    mask = m[by0:by1 + 1, bx0:bx1 + 1]
    rgba = a[by0:by1 + 1, bx0:bx1 + 1].copy()
    rgba[..., 3] = np.where(mask, rgba[..., 3], 0).astype(np.uint8)
    return Image.fromarray(rgba, "RGBA"), mask


def fit(old_spans, src_spans, s_lo=0.90, s_hi=1.12):
    """求 (s, dx)：把源叶子缩放到旧叶子坐标系里，逐行左右轮廓误差最小。

    对齐基准：旧叶子最下面一行 <-> 源叶子最下面一行（叶根不动），
    只往「上」长。"""
    o_last = old_spans[-1][0]
    s_last = src_spans[-1][0]
    s_arr = np.array([(r, l, rt) for r, l, rt, _w in src_spans], float)
    best = None
    for s in np.arange(s_lo, s_hi + 1e-9, 0.002):
        # 旧行 r 对应源行：s_last - (o_last - r) / s
        rs = s_last - (o_last - np.array([p[0] for p in old_spans], float)) / s
        if rs.min() < s_arr[0, 0] or rs.max() > s_arr[-1, 0]:
            continue
        # 只在旧叶子有内容的行上比较（跳过被切平的顶端那一行以外的部分）
        L = np.interp(rs, s_arr[:, 0], s_arr[:, 1]) * s
        R = np.interp(rs, s_arr[:, 0], s_arr[:, 2]) * s
        Lo = np.array([p[1] for p in old_spans], float)
        Ro = np.array([p[2] for p in old_spans], float)
        # 宽度误差给权重：宽度对不上 = 缩放不对
        w_err = np.abs((R - L) - (Ro - Lo))
        dx = float(np.median(Lo - L))
        c_err = np.abs(((L + R) / 2.0 + dx) - ((Lo + Ro) / 2.0))
        err = float(np.mean(w_err) + 0.5 * np.mean(c_err))
        key = (err, abs(s - 1.0))
        if best is None or key < best[0]:
            best = (key, float(s), dx, err)
    return best[1], best[2], best[3]


def main():
    write = "--write" in sys.argv
    old = Image.open(LEAF).convert("RGBA")
    oa = np.array(old)
    om = oa[..., 3] > 26
    osp = spans(om)
    print("旧叶子：%dx%d，行 %d..%d，首行宽 %d"
          % (old.width, old.height, osp[0][0], osp[-1][0], osp[0][3]))

    src, smask = src_leaf_mask()
    ssp = spans(smask)
    print("源叶子：%dx%d，行 %d..%d，首行宽 %d"
          % (src.width, src.height, ssp[0][0], ssp[-1][0], ssp[0][3]))

    s, dx, err = fit(osp, ssp)
    print("拟合：scale=%.4f dx=%.2f 残差=%.2f px" % (s, dx, err))

    sw, sh = int(round(src.width * s)), int(round(src.height * s))
    scaled = src.resize((sw, sh), Image.LANCZOS)

    # 旧叶子的「叶根」在 asset 里的 y = osp[-1][0]；源叶子缩放后的
    # 最后一行要落在这里
    o_bottom = osp[-1][0]
    s_bottom = sh - 1
    # 画布：宽度沿用旧 asset（设计 x 映射不变），高度 = 缩放后的源叶子，
    # 叶根（最后一行）落在画布最底行，整片叶子都在画布里，不会被裁
    new_w, new_h = old.width, sh
    canvas = Image.new("RGBA", (new_w, new_h), (0, 0, 0, 0))
    canvas.alpha_composite(scaled, (int(round(dx)), 0))
    grow = new_h - old.height
    print("叶子比旧素材高 %d px（多出来的就是被切掉的叶尖），新尺寸 %dx%d"
          % (grow, new_w, new_h))

    if write:
        canvas.save(LEAF)
        # 枯萎版：沿用 make_leaf_assets.py 的同一套 HSV 变换
        hsv = np.array(canvas.convert("RGB").convert("HSV")).astype(np.float32)
        hh, ss, vv = hsv[..., 0], hsv[..., 1], hsv[..., 2]
        hh = 85.0 + (hh - 85.0) * 0.18
        hh = np.where(ss > 8, 34.0, hh)
        hh = hh + (vv / 255.0 - 0.5) * 8.0
        ss = np.clip(ss * 0.86, 0, 255)
        vv = np.clip(vv * 0.86, 0, 255)
        dry_rgb = np.stack([hh, ss, vv], -1).astype(np.uint8)
        dry = Image.fromarray(dry_rgb, "HSV").convert("RGB").convert("RGBA")
        dry.putalpha(canvas.split()[3])
        dry.save(DRY)
        print("已写入 leaf.png / leaf_dry.png")

    # 设计坐标：底图绘制在 x 49..341 / y 85..318
    k = 292.0 / 1548.0
    # 设计 y：让新素材最后一行（叶根）落在旧素材的最后一行那个位置
    y0 = round(85.0 + (o_bottom - (new_h - 1)) * k, 2)
    geo = dict(x=158.97, y=y0, w=round(new_w * k, 2), h=round(new_h * k, 2))
    print("LEAF_GEO = (%.2f, %.2f, %.2f, %.2f, 178.59, 132.72)"
          % (geo["x"], geo["y"], geo["w"], geo["h"]))

    # 对照图：旧叶 / 新叶并排（放大 2 倍）
    comp = Image.new("RGBA", (new_w * 2 + 30, new_h + 20), (245, 245, 245, 255))
    comp.alpha_composite(old, (10, 10 + grow))
    comp.alpha_composite(canvas, (new_w + 20, 10))
    comp.resize((comp.width * 2, comp.height * 2), Image.NEAREST).save(
        os.path.join(ROOT, ".tmp", "leaf_rebuild.png"))
    print("对照图 .tmp/leaf_rebuild.png")


if __name__ == "__main__":
    main()
