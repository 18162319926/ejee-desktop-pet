#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""预览回归工具（P0-1）。

把「逐张肉眼比对预览图」变成一条命令：

    python tools/check_preview.py            # 比对 previews/ 与 _baseline/
    python tools/check_preview.py --run      # 先重跑 --shot 再比对
    python tools/check_preview.py --refresh  # 比对后把 previews/ 刷成新基线

设计要点：
  · 直接对两张图的 ARGB32 字节做比对（不靠外部 cmp / PIL），
    输出每张图的差异像素数与差异包围盒，方便定位"哪一块动了"。
  · 硬性断言渲染环境 DPR=1：DPR≠1 时预览尺寸会放大（如 1.5→600×708），
    那样刷出来的基线会让后续比对全部假 DIFF，直接报错退出。
  · 退出码：全部一致 -> 0；任一文件有差异/新增/缺失 -> 1（可进 CI）。

依赖：PySide6（与 ejee_pet.py 同一环境）。
"""
import os
import sys
import subprocess

APP_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PREVIEW_DIR = os.path.join(APP_DIR, "previews")
BASELINE_DIR = os.path.join(APP_DIR, "_baseline")
DW, DH = 400.0, 472.0

# 像素级差异阈值：单通道（含 alpha）绝对差超过它才算"动了"。
# 离屏渲染是确定性的，理论上要么完全一致、要么整块变动，留一点余量防抖动。
DIFF_THRESH = 12


def _load(path):
    from PySide6.QtGui import QImage
    im = QImage(path)
    if im.isNull():
        return None
    return im.convertToFormat(QImage.Format_ARGB32)


def _dpr(im):
    return im.width() / DW


def _compare_bytes(a, b):
    """返回 (diff_count, (x0,y0,x1,y1) or None)。a/b 为等长的 ARGB32 字节。"""
    if a == b:
        return 0, None
    na, nb = len(a), len(b)
    n = min(na, nb)
    x0 = y0 = 10 ** 9
    x1 = y1 = -1
    cnt = 0
    # 步进 4 字节（一个像素）
    i = 0
    while i < n:
        if a[i] != b[i] or a[i + 1] != b[i + 1] or a[i + 2] != b[i + 2] \
                or a[i + 3] != b[i + 3]:
            cnt += 1
            px = i // 4
            x = px % int(DW)
            y = px // int(DW)
            if x < x0:
                x0 = x
            if y < y0:
                y0 = y
            if x > x1:
                x1 = x
            if y > y1:
                y1 = y
        i += 4
    bbox = (x0, y0, x1, y1) if cnt else None
    return cnt, bbox


def run_shot():
    env = dict(os.environ)
    env["QT_QPA_PLATFORM"] = "offscreen"
    env["QT_QPA_FONTDIR"] = "C:/Windows/Fonts"
    print("[check_preview] 重跑 --shot 生成预览 …")
    cp = subprocess.run([sys.executable, os.path.join(APP_DIR, "ejee_pet.py"),
                         "--shot"], env=env, capture_output=True, text=True)
    if cp.returncode != 0:
        sys.stderr.write(cp.stdout + cp.stderr)
        sys.exit("preview generation failed (rc=%d)" % cp.returncode)
    print("  ->", cp.stdout.strip() or "(done)")


def main():
    do_run = "--run" in sys.argv
    do_refresh = "--refresh" in sys.argv

    if do_run:
        run_shot()

    if not os.path.isdir(PREVIEW_DIR):
        sys.exit("找不到 previews/ 目录，先跑一次 --shot")

    files = sorted(f for f in os.listdir(BASELINE_DIR)
                  if f.startswith("preview_") and f.endswith(".png"))
    if not files:
        sys.exit("基线目录 _baseline/ 为空，首次请加 --refresh 生成基线")

    print("文件            状态    差异像素   差异包围盒(x0,y0-x1,y1)")
    print("-" * 64)
    changed = []
    for f in files:
        pb = os.path.join(BASELINE_DIR, f)
        pp = os.path.join(PREVIEW_DIR, f)
        if not os.path.exists(pp):
            print("%-15s %-7s" % (f, "缺失!"))
            changed.append(f)
            continue
        ib = _load(pb)
        ip = _load(pp)
        if ib is None:
            print("%-15s %-7s" % (f, "基线坏"))
            changed.append(f)
            continue
        dpr = _dpr(ip)
        if abs(dpr - 1.0) > 0.01:
            sys.exit("渲染环境 DPR=%.2f ≠ 1（图像 %dx%d）。\n"
                     "请用 QT_QPA_PLATFORM=offscreen 且系统缩放设为 100%% "
                     "重新生成基线，否则后续比对会全部假 DIFF。"
                     % (dpr, ip.width(), ip.height()))
        ba = bytes(ib.constBits()[:ib.sizeInBytes()])
        bp = bytes(ip.constBits()[:ip.sizeInBytes()])
        cnt, bbox = _compare_bytes(ba, bp)
        if cnt == 0:
            print("%-15s %-7s" % (f, "一致"))
        else:
            bb = "%d,%d-%d,%d" % bbox if bbox else "-"
            print("%-15s %-7s %-9d %s" % (f, "DIFF", cnt, bb))
            changed.append(f)

    # previews/ 里多出来的（新文件，基线没有）
    extra = sorted(set(os.listdir(PREVIEW_DIR)) - set(files))
    extra = [e for e in extra if e.startswith("preview_") and e.endswith(".png")]
    for e in extra:
        print("%-15s %-7s" % (e, "新增!"))
        changed.append(e)

    print("-" * 64)
    if changed:
        print("有 %d 个文件与基线不一致：%s" % (len(changed), ", ".join(changed)))
        if do_refresh:
            import shutil
            for f in changed:
                src = os.path.join(PREVIEW_DIR, f)
                if os.path.exists(src):
                    shutil.copy2(src, os.path.join(BASELINE_DIR, f))
                    print("  [refresh] 已刷入基线：%s" % f)
            print("基线已更新，请目视确认新预览无误后再提交。")
        else:
            print("若要确认这是预期改动并刷新基线，重跑：")
            print("  python tools/check_preview.py --refresh")
        sys.exit(1)
    print("全部 %d 张预览与基线一致 ✓" % len(files))


if __name__ == "__main__":
    main()
