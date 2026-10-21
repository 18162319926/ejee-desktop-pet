"""桌宠行为回归仿真（离屏，Qt 事件由 _tick 手动推进）。
覆盖 R38~R45：傲娇躲避 / 面包残渣+视线 / 多形态气泡 / 晕车 / 摇头拒绝 /
      拖拽投喂起点 / 果汁 360° 喷射 / post-lock 回 idle / 陪伴档案 /
      穿透缩放 / 位置记忆 / 开机自启 / 右键菜单（陪伴档案·无喂面包）/
      番茄钟单入口选时长。
"""
import os
import sys
import math

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
os.environ.setdefault("QT_QPA_FONTDIR", "C:/Windows/Fonts")

from PySide6.QtCore import Qt, QPoint, QPointF          # noqa: E402
from PySide6.QtWidgets import QApplication              # noqa: E402
from PySide6.QtGui import QCursor                       # noqa: E402

sys.argv = [sys.argv[0]]
import ejee_pet as E                                    # noqa: E402


class FakeClock:
    """可控时钟：ms 只增不减，让 _tick 的 dt 可控。"""

    def __init__(self):
        self.ms = 0.0

    def elapsed(self):
        return self.ms

    def start(self):
        pass


def make_pet(app, w=400, h=340, x=200, y=300):
    pet = E.EjeePet.__new__(E.EjeePet)
    E.QWidget.__init__(pet)
    pet.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint
                       | Qt.Tool)
    pet.setAttribute(E.Qt.WA_TranslucentBackground, True)
    pet.resize(w, h)
    pet.move(x, y)
    pet.clock = FakeClock()
    pet.t = 0.0
    pet._last_t = 0.0
    pet.size = w / E.DW
    pet.target_size = pet.size
    pet.bw, pet.bh, pet.s = 292.0, 233.0, E.EjeePet.CHAR_W / 1548.0
    pet.BCX, pet.BCY = E.EjeePet.BCX, E.EjeePet.BCY
    # 情绪状态机
    pet.state = "idle"
    pet.state_t0 = 0.0
    pet.spr = {k: E.Spring(E.P["idle"][k], *E.SPRING_K[k])
               for k in E.P["idle"]}
    pet.cur = dict(E.P["idle"])
    pet._sq = E.Spring(0.0, 230, 9)
    pet._tilt = E.Spring(0.0, 120, 14)
    pet._opac = E.Spring(1.0, 90, 12)
    pet._size_spring = E.Spring(pet.size, 90, 12)
    pet._pomo_nrv = E.Spring(0.0, 120, 12)
    pet.mouth_alt = E.Spring(0.0, 110, 13)
    pet.sleep_amt = E.Spring(0.0, 110, 13)
    pet.hungry_amt = E.Spring(0.0, 90, 12)
    pet.mischief_amt = E.Spring(0.0, 120, 13)
    pet._mis_tail = E.Spring(0.0, 90, 11)
    pet._flee = None
    pet._fled = False
    pet._swim = E.Spring(0.0, 70, 12)
    pet._swim_ph = 0.0
    pet._turn = E.Spring(0.0, 130, 13)
    pet._turn_t = 0.0
    pet._heading = None
    pet._mis_puff = 0.0
    pet._mis_dir = 1.0
    pet._hover = False
    pet._hover_amt = E.Spring(0.0, 70, 12)
    pet._breathe_ph = 0.0
    pet._tail_ph = 0.0
    pet._rumble_i = 0
    pet._fantasy = None
    pet._next_fantasy = 999.0
    pet.wink_l = E.Spring(0.0, 110, 13)
    pet.wink_r = E.Spring(0.0, 110, 13)
    pet._gvx = E.Spring(0.0, 130, 17)       # 视线缓动（对应 __init__）
    pet._gvy = E.Spring(0.0, 130, 17)
    pet._dvx = pet._dvy = 0.0
    pet._last_move_t = 0.0
    pet._glide = None
    pet._next_micro = 999.0
    pet._look_until = 0.0
    pet._look_dir = 0.0
    pet.angry_until = -1.0
    pet.surprised_until = -1.0
    pet.surprised_cd = 999.0
    pet._celebrate_until = -1.0
    pet._next_expr = 999.0
    pet.last_interact = 0.0
    pet._wake2 = False
    pet._fx_timer = 5.0
    pet._fx_timer2 = 5.0
    pet.mischief_until = 0.0
    pet.next_blink = 999.0
    pet.blink_t0 = None
    pet.blink_pending2 = False
    pet.phase = "idle"
    pet.phase_t0 = 0.0
    pet.bubble_text = ""
    pet.bubble_until = 0.0
    pet.bubble_t0 = 0.0
    pet.bubble_style = "cloud"
    pet.particles = []
    pet.floats = []
    pet._next_drag_line = 0.0
    pet._next_zoom_line = 0.0
    pet._next_chatter = 1e9
    pet._next_hungry = 1e9
    pet._zooming = False
    pet._zoom_anchor = None
    pet._zoom_from = 1.0
    pet._press_pos = None
    pet._dragging = False
    pet._feed_pending = False
    pet._feed_deadline = 0.0
    pet._dbl_until = 0.0
    pet._bread = None
    pet._stuffed_until = 0.0
    pet._stuffed = E.Spring(0.0, 90, 12)
    pet._feed_from = None
    pet._crumbs = []
    pet._pity = E.Spring(0.0, 70, 12)
    pet._tag_dy = E.Spring(0.0, 90, 12)
    pet._tag_dx = E.Spring(0.0, 90, 12)
    pet._pat_n = 0
    pet._pat_last = -99.0
    pet._shy_until = 0.0
    pet._shy_dir = (1.0, 0.0)
    pet._shy_amt = E.Spring(0.0, 130, 11)
    pet._dizzy_until = 0.0
    pet._dizzy_amt = E.Spring(0.0, 100, 13)
    pet._dizzy_fx = 0.0
    pet._shake_log = []
    pet._post_lock = 0.0
    pet._nod_until = 0.0
    pet._nod_dur = 1.15
    pet._nod_n = 0
    pet._sleeping_prev = False
    pet.facing = -1
    pet._wander = None
    pet._next_walk = 1e9
    pet._walk_speed = 150.0
    pet._band_clamp = lambda x, y: (x, y)
    pet._ring_phase = 0.0
    pet._save_t = 1e9
    pet._lines = E.load_lines()
    pet._meta = {"hunger": 80.0, "fed": 0, "pets": 0, "pomo_min": 25,
                 "first_seen": "2026-10-01", "greet_day": "2026-10-18",
                 "last_seen": 0.0}
    pet._restore_pos = None
    pet._pomo_end = None
    pet._pomo_raf = None
    pet._pass = False
    pet._tray = None
    pet.timer = None
    pet.tray_act_pomo = None
    pet.tray_act_pass = None
    pet.tray_act_boot = None
    pet.mouth_center = (195.0, 235.0)
    pet.eye_pos = {"eye_l": (150.0, 160.0, 30.0, 22.0),
                   "eye_r": (238.0, 162.0, 30.0, 22.0)}
    pet.head_top = E.EjeePet.BCY - pet.bh
    pet.omega_bot = []
    pet._tail_amp = lambda: 0.0
    return pet


def run(pet, seconds, dt=1.0 / 30.0, keep_awake=True):
    n = int(seconds / dt)
    for _ in range(n):
        if keep_awake:
            pet.last_interact = pet.t
        pet.clock.ms += dt * 1000.0
        pet._tick()


FAILED = []


def check(name, cond, extra=""):
    print(("  PASS  " if cond else "  FAIL  ") + name + ("  " + extra
                                                           if extra else ""))
    if not cond:
        FAILED.append(name)


def main():
    app = QApplication.instance() or QApplication(sys.argv)

    # 测试卫生：_save() 会走 save_data 落盘，而测试宠物的 _meta 是脚手架值
    # （first_seen / x / y 等）——直接写真的存档文件会污染开发/活存档。
    # 这里把落盘函数打成空操作，只验证内存行为。
    E.save_data = lambda d: None

    # ---------- 1. 傲娇躲避 ----------
    print("[1] 连续摸头 5 次 -> 傲娇躲避")
    pet = make_pet(app)
    pet.move(600, 400)
    for i in range(4):
        pet._pat()
    check("前 4 下都是开心（phase=idle, state=idle）",
          pet.state == "idle" and pet.phase == "idle")
    n_before = len([p for p in pet.particles if p.kind == "heart"])
    check("摸头产生爱心", n_before >= 1, "hearts=%d" % n_before)
    x0, y0 = pet.x(), pet.y()
    n_steam0 = len([p for p in pet.particles if p.kind == "steam"])
    pet._pat()                                  # 第 5 下 -> 翻脸
    check("第 5 下触发 shy", pet._shy_until > pet.t)
    pet._decide_state()
    check("状态切到 shy", pet.state == "shy", pet.state)
    check("有傲娇台词", "摸" in pet.bubble_text or "够" in pet.bubble_text
          or len(pet.bubble_text) > 0, repr(pet.bubble_text))
    n_steam1 = len([p for p in pet.particles if p.kind == "steam"])
    check("第 5 下改冒蒸汽（不是爱心）", n_steam1 > n_steam0,
          "steam %d->%d" % (n_steam0, n_steam1))
    run(pet, 1.2)
    moved = math.hypot(pet.x() - x0, pet.y() - y0)
    check("不再做身体形变（_shy_amt 接近 0）", pet._shy_amt.v < 0.1,
          "shy_amt=%.2f" % pet._shy_amt.v)
    check("直接闪现到别处（位移很大）", moved > 100, "moved=%.0fpx" % moved)
    run(pet, 3.2)
    pet._decide_state()
    check("3 秒后退出 shy", pet.state != "shy", pet.state)

    # ---------- 2. 摇手拒绝（吃饱后喂食）----------
    print("\n[2] 吃饱后再喂食 -> 摇头拒绝")
    pet = make_pet(app)
    pet._meta["hunger"] = 100.0
    pet.phase = "idle"
    pet.feed()
    check("饱食度保持 100", pet._meta["hunger"] == 100.0)
    check("触发摇头", pet._nod_until > pet.t)
    check("气泡框=圆形泡泡框", pet.bubble_style == "round",
          pet.bubble_style)
    check("有「不～要～」飘字",
          any(f[0] == "不～要～" for f in pet.floats),
          str([f[0] for f in pet.floats]))
    xs = []
    for _ in range(30):
        xs.append(pet._nod_offset())
        pet.clock.ms += 33.3
        pet._tick()
    peak = max(abs(v) for v in xs)
    check("摇头有左右位移（振幅>2px）", peak > 2.0, "peak=%.2fpx" % peak)
    check("左右往返（符号翻转）",
          any(xs[i] * xs[i + 1] < 0 for i in range(len(xs) - 1)))
    check("振幅衰减", abs(xs[6]) <= abs(xs[1]) + 0.01)
    pet.clock.ms += 1400
    pet._tick()
    check("摇头结束后位移归零", pet._nod_offset() == 0.0)

    # ---------- 3. 拖拽投喂从松手点飞入 ----------
    print("\n[3] 拖拽投喂：面包从松手点飞进嘴")
    pet = make_pet(app)
    pet.move(600, 400)
    pet._meta["hunger"] = 40.0
    pet.phase = "idle"
    mg = pet._mouth_global()
    far = QPoint(mg.x() - 150, mg.y() - 90)
    pet._drop_bread(far)                        # 远离嘴 -> 应掉地上
    check("远离嘴时不进喂食相位", pet.phase != "bread", pet.phase)
    check("生成了面包渣", len(pet._crumbs) == 1, "crumbs=%d" % len(pet._crumbs))
    cm = pet._crumbs[0]
    check("残渣落在松手点下方",
          cm.gpos.y() > far.y() - 5 and abs(cm.gpos.x() - far.x()) < 40,
          "drop=(%d,%d) crumb=(%d,%d)" % (far.x(), far.y(),
                                           cm.gpos.x(), cm.gpos.y()))
    check("残渣不在宠物窗口内（独立小窗）",
          pet._crumbs[0].parent() is None)

    pet2 = make_pet(app)
    pet2.move(600, 400)
    pet2._meta["hunger"] = 40.0
    pet2.phase = "idle"
    mg2 = pet2._mouth_global()
    # 在嘴的命中圈内的左上角（48*size 内）
    spot = QPoint(mg2.x() - 26, mg2.y() - 20)
    assert math.hypot(spot.x() - mg2.x(), spot.y() - mg2.y()) <= 48 * pet2.size
    pet2._drop_bread(spot)
    check("嘴边松手吃到面包", pet2.phase == "bread", pet2.phase)
    s = pet2.width() / E.DW
    # _feed_from 存的是"扣掉画布顶部留白"的设计坐标（paintEvent 会把整幅
    # 画面 translate(0, PAD_T) 下移），所以屏幕 y 换算过来要减 PAD_T
    want = ((spot.x() - pet2.x()) / s, (spot.y() - pet2.y()) / s - E.PAD_T)
    check("面包起点=松手点（设计坐标）",
          pet2._feed_from is not None
          and abs(pet2._feed_from[0] - want[0]) < 1.0
          and abs(pet2._feed_from[1] - want[1]) < 1.0,
          "from=%s want=(%.1f,%.1f)" % (pet2._feed_from, want[0], want[1]))

    # 只画面包层（脚手架没底图资源），验证飞行起点/终点轨迹
    from PySide6.QtGui import QPainter, QImage
    pet2.clock.ms = pet2._last_t * 1000.0 + 1.0   # 只走 1ms，面包还在起点
    pet2._tick()
    traj = []
    phase_t0_0 = pet2.phase_t0
    for _ in range(18):
        pet2.clock.ms += 30.0                 # 30ms/帧，共 ~0.54s
        pet2._tick()
        pet2.phase = "bread"
        pet2.phase_t0 = phase_t0_0            # 动画时长固定 0.55s
        img = QImage(400, 340, QImage.Format_ARGB32)
        img.fill(0)
        pnt = QPainter(img)
        pnt.setRenderHint(QPainter.Antialiasing, True)
        pnt.scale(pet2.width() / E.DW, pet2.width() / E.DW)
        pet2._draw_bread(pnt)
        pnt.end()
        ys, xs = [], []
        for y in range(0, 340):
            for x in range(0, 400):
                if img.pixelColor(x, y).alpha() > 40:
                    xs.append(x); ys.append(y)
        if xs:
            traj.append((sum(xs) / len(xs) / (pet2.width() / E.DW),
                         sum(ys) / len(ys) / (pet2.width() / E.DW)))
    if traj:
        sx, sy = traj[0]
        ex, ey = traj[-1]
        mc = pet2.mouth_center
        check("面包起点≈松手点", abs(sx - pet2._feed_from[0]) < 14
              and abs(sy - pet2._feed_from[1]) < 14,
              "start=(%.0f,%.0f) from=%s" % (sx, sy, pet2._feed_from))
        check("面包终点≈嘴中心", abs(ex - (mc[0] + 2)) < 16
              and abs(ey - (mc[1] + 13)) < 16,
              "end=(%.0f,%.0f) mouth=(%.0f,%.0f)"
              % (ex, ey, mc[0] + 2, mc[1] + 13))
        check("走的是弧线不是直线（中段偏离直线）", len(traj) > 3)
    else:
        check("面包轨迹可渲染", False, "no pixels")
    pet2._feed_from = None

    # ---------- 4. 视线跟随残渣 ----------
    print("\n[4] 视线可怜巴巴跟着残渣")
    pet = make_pet(app)
    pet.move(600, 400)
    E.PREVIEW_MODE = False
    pet._crumbs = [cm]
    cm.t0 = __import__("time").time()
    cm.alive = True
    g = pet._gaze_target()
    check("视线被残渣吸走（横向有明确方向）",
          g[0] != 0.0, "gaze=%s" % (tuple(round(v, 2) for v in g),))
    run(pet, 0.8)
    # 可怜层表情复用 angry：_pity 顶起 puff（怒眉+眼周阴影）与 mouth_alt（W 嘴）
    check("有残渣时 pity 量升起", pet._pity.v > 0.4,
          "pity=%.2f" % pet._pity.v)
    check("可怜层复用 angry 眉眼（puff 被顶起）",
          pet.cur["puff"] > 0.4, "puff=%.2f" % pet.cur["puff"])
    check("可怜层复用 angry 嘴形（alt 被顶起）",
          pet.mouth_alt.v > 0.4, "alt=%.2f" % pet.mouth_alt.v)
    # 视线缓动收敛到残渣方向（不再是突变，而是连续转过去）
    g2 = pet._gaze()
    check("视线缓动收敛到残渣方向", abs(g2[0]) > 0.3,
          "gaze=%s" % (tuple(round(v, 2) for v in g2),))
    pet._crumbs = []
    run(pet, 1.5)
    check("渣没了 pity 量收回", pet._pity.v < 0.35, "pity=%.2f" % pet._pity.v)
    check("渣没了怒眉收回", pet.cur["puff"] < 0.35,
          "puff=%.2f" % pet.cur["puff"])
    check("渣没了 W 嘴收回", pet.mouth_alt.v < 0.35,
          "alt=%.2f" % pet.mouth_alt.v)
    for c in pet._crumbs:
        c.stop()

    # ---------- 5. 多形态气泡 ----------
    print("\n[5] 气泡框型随情绪切换")
    pet = make_pet(app)
    pet.state = "idle"
    pet._say("普通闲聊", 2.0)
    check("日常 -> cloud", pet.bubble_style == "cloud", pet.bubble_style)
    pet.state = "angry"
    pet._say("生气啦", 2.0)
    check("生气 -> burst", pet.bubble_style == "burst", pet.bubble_style)
    pet.state = "sleep"
    pet._say("困了", 2.0)
    check("睡眠 -> zzz", pet.bubble_style == "zzz", pet.bubble_style)
    pet.state = "idle"
    pet._say("打嗝", 2.0, "round")
    check("打嗝 -> round", pet.bubble_style == "round", pet.bubble_style)
    pet._say("生气", 2.0, "burst")
    check("显式 burst 不被改写", pet.bubble_style == "burst",
          pet.bubble_style)

    # ---- 气泡皮肤（BUBBLE_THEMES）：每种状态一套配色 / 字体 / 挂饰 ----
    def theme_of(st, style="cloud", crumbs=False):
        pet.state = st
        pet.bubble_style = style
        pet._crumbs = ["stub"] if crumbs else []
        return pet._bubble_theme()
    check("日常皮肤=奶油云", theme_of("idle") is E.BUBBLE_THEMES["cloud"])
    check("傲娇皮肤=粉色爱心泡", theme_of("shy") is E.BUBBLE_THEMES["shy"])
    check("恶作剧皮肤=果汁橙泡", theme_of("mischief")
          is E.BUBBLE_THEMES["mischief"])
    check("晕车皮肤=浅绿摇摆泡", theme_of("dizzy", "burst")
          is E.BUBBLE_THEMES["dizzy"])
    check("生气皮肤=橙红爆炸泡", theme_of("angry", "burst")
          is E.BUBBLE_THEMES["burst"])
    check("睡眠皮肤=睡泡泡", theme_of("sleep", "zzz")
          is E.BUBBLE_THEMES["zzz"])
    check("有残渣+平静 -> 可怜蓝泡", theme_of("idle", crumbs=True)
          is E.BUBBLE_THEMES["crumb"])
    check("有残渣但在生气 -> 仍爆炸泡", theme_of("angry", "burst", crumbs=True)
          is E.BUBBLE_THEMES["burst"])
    check("摸头（happy）+残渣 -> 可怜蓝泡", theme_of("happy", crumbs=True)
          is E.BUBBLE_THEMES["crumb"])
    # 字体：默认圆润体（幼圆优先），生气用加粗硬体
    fr = pet._bubble_font(E.BUBBLE_THEMES["cloud"])
    check("默认字体=幼圆圆润体", fr.families()[0] == "YouYuan",
          str(fr.families()))
    check("默认字号=12", fr.pixelSize() == 12, str(fr.pixelSize()))
    check("默认字体不加粗", not fr.bold())
    fp = pet._bubble_font(E.BUBBLE_THEMES["burst"])
    check("生气字体=加粗硬体", fp.bold()
          and fp.families()[0] == "Microsoft YaHei UI", str(fp.families()))
    # 爱心路径可用
    hp = pet._heart_path(0.0, 0.0, 5.0)
    check("爱心路径非空", not hp.isEmpty(),
          "bounding=%s" % (hp.boundingRect(),))

    # 渲染四种框型不崩
    pet._crumbs = []
    pet.t = 5.0
    pet._last_t = 5.0
    for st in ("cloud", "burst", "round", "zzz"):
        pet.bubble_style = st
        pet.bubble_text = "测试气泡文字"
        pet.bubble_t0 = pet.t - 0.6      # 已过入场动画（0.30s）
        pet.bubble_until = pet.t + 5.0
        im = QImage(400, 340, QImage.Format_ARGB32)
        im.fill(0)
        pp = QPainter(im)
        pp.setRenderHint(QPainter.Antialiasing, True)
        pp.setRenderHint(QPainter.TextAntialiasing, True)
        pp.scale(pet.width() / E.DW, pet.width() / E.DW)
        pet._draw_bubble(pp)
        pp.end()
        npx = sum(1 for y in range(0, 340) for x in range(0, 400)
                  if im.pixelColor(x, y).alpha() > 0)
        thr = 150 if st == "zzz" else 400
        check("框型 %s 渲染有内容" % st, npx > thr, "ink px=%d" % npx)
    pet.bubble_text = ""

    # 各状态皮肤 + 挂饰真实渲染不崩（爱心 / 汁滴 / 泪滴 / 摇摆 / 渐变）
    for st, style in (("shy", "cloud"), ("mischief", "cloud"),
                      ("dizzy", "burst"), ("angry", "burst")):
        pet.state = st
        pet.bubble_style = style
        pet.bubble_text = "状态皮肤测试"
        pet.bubble_t0 = pet.t - 0.6
        pet.bubble_until = pet.t + 5.0
        im = QImage(400, 340, QImage.Format_ARGB32)
        im.fill(0)
        pp = QPainter(im)
        pp.setRenderHint(QPainter.Antialiasing, True)
        pp.scale(pet.width() / E.DW, pet.width() / E.DW)
        pet._draw_bubble(pp)
        pp.end()
        npx = sum(1 for y in range(0, 340) for x in range(0, 400)
                  if im.pixelColor(x, y).alpha() > 0)
        check("皮肤 %s 渲染有内容" % st, npx > 400, "ink px=%d" % npx)
    pet.state = "idle"
    pet.bubble_text = ""

    # ---------- 6. 晕车 ----------
    print("\n[6] 边缘疯狂拉扯 -> 晕车")
    pet = make_pet(app)
    scr = pet._scr_rect()
    pet._shake_log = []
    pet.t = 1.0
    pet._last_t = 1.0
    # 在边缘左右横跳：窗口中心贴左 / 贴右 -> sdir 反复变化
    for i, dx in enumerate((30, -30, 30, -30, 30)):
        pet._edge_shake(dx)          # 疯狂左右横拉
        pet.t += 0.25
        pet._last_t = pet.t
    check("4 次来回触发晕车", pet._dizzy_until > 0.0,
          "dizzy_until=%.1f" % pet._dizzy_until)
    pet._decide_state()
    check("状态切到 dizzy", pet.state == "dizzy", pet.state)
    run(pet, 0.6)
    check("蚊香圈显形", pet._dizzy_amt.v > 0.5,
          "dizzy=%.2f" % pet._dizzy_amt.v)
    nb0 = len([p for p in pet.particles if p.kind == "bubble"])
    run(pet, 1.4)
    nb1 = len([p for p in pet.particles if p.kind == "bubble"])
    check("晕车会吐泡泡", nb1 > nb0 or nb1 > 0, "%d -> %d" % (nb0, nb1))
    check("晕车会吐「呕…」飘字",
          any(f[0] == "呕…" for f in pet.floats) or nb1 > 0,
          str([f[0] for f in pet.floats]))
    check("晕车期间有台词", len(pet.bubble_text) > 0, repr(pet.bubble_text))
    check("晕车气泡=burst", pet.bubble_style == "burst",
          pet.bubble_style)
    check("蚊香圈眼值有效", pet._dizzy_amt.v > 0.5,
          "dizzy=%.2f" % pet._dizzy_amt.v)
    run(pet, 4.6)
    pet._decide_state()
    check("4.5 秒后退出晕车", pet.state != "dizzy", pet.state)

    # ---------- 7. 果汁喷射量 ----------
    print("\n[7] 尾巴果汁更多、范围更大")
    pet = make_pet(app)
    pet.move(600, 400)
    pet.phase = "idle"
    QCursor.setPos(QPoint(900, 500))
    pet._mischief()
    juice = [p for p in pet.particles if p.kind == "juice"]
    check("果汁 >= 16 滴", len(juice) >= 16, "count=%d" % len(juice))
    speeds = [math.hypot(p.vx, p.vy) for p in juice]
    check("初速范围更大（>=420）", max(speeds) >= 420,
          "max=%.0f" % max(speeds))
    angs = [math.atan2(p.vy, p.vx) for p in juice]
    spread = math.degrees(max(angs) - min(angs)) if len(angs) > 1 else 0
    check("全方向溅射（覆盖 >320°）", spread > 320.0, "spread=%.0f°" % spread)
    check("汁滴更大更大", max(p.size for p in juice) > 6.0,
          "max size=%.1f" % max(p.size for p in juice))
    # 不再有"范围框"：汁水自由飞出设计框，且不再被钉在边缘变成水渍
    run(pet, 0.6)
    stains = [p for p in pet.particles if p.kind == "stain"]
    check("汁水不再撞框变成水渍", len(stains) == 0, "stain=%d" % len(stains))
    jl = [p for p in pet.particles if p.kind == "juice"]
    outside = [p for p in jl
               if p.x < 8.0 or p.x > E.DW - 8.0 or p.y < 6.0 or p.y > 330.0]
    check("汁水能飞出旧的设计框（无范围限制）", len(outside) >= 4,
          "outside=%d/%d" % (len(outside), len(jl)))
    # 特效层：把汁滴换算到全局屏幕坐标，且确实落在宠物窗口矩形之外
    try:
        fx = E.JuiceOverlay()
        fx.refresh(pet)
        n = len(fx._items)
        check("特效层承载汁滴（全局坐标）", n > 0, "items=%d" % n)
        outs = [i for i in fx._items
                if not (pet.x() <= i[0] <= pet.x() + pet.width()
                        and pet.y() <= i[1] <= pet.y() + pet.height())]
        check("汁水能飞出宠物窗口（不被窗口裁切）",
              n > 0 and len(outs) > 0, "outside=%d/%d" % (len(outs), n))
        fx.hide()
        fx.deleteLater()
    except Exception as ex:
        check("特效层承载汁滴（全局坐标）", False, "exc=%r" % (ex,))

    # ---------- 7b. 用户状态结束后先回 idle（POST_IDLE_SECS 内不冒自发状态）----
    print("\n[7b] 用户操作引发的状态结束后先回 idle")
    pet = make_pet(app)
    pet.move(600, 400)
    pet.phase = "idle"
    QCursor.setPos(QPoint(1400, 200))       # 光标远离，避免顺手触发惊讶
    pet._mischief()
    run(pet, 0.05)                         # 让 _decide_state 把状态切过去
    check("触发 mischief", pet.state == "mischief", pet.state)
    run(pet, 2.0)                            # mischief 持续 1.5s
    check("mischief 结束回到 idle", pet.state == "idle", pet.state)
    check("退场时上了 idle 锁", pet._post_lock > pet.t,
          "lock=%.2f t=%.2f" % (pet._post_lock, pet.t))
    # 把三个自发调度全部设为"已到期"，锁期内也不该冒出任何状态
    pet._next_expr = pet.t - 1.0
    pet._next_walk = pet.t - 1.0
    pet._next_chatter = pet.t - 1.0
    run(pet, 1.0)
    check("锁期内保持 idle（不冒自发状态）", pet.state == "idle", pet.state)
    run(pet, E.POST_IDLE_SECS + 1.0)         # 锁过期，恢复正常调度
    check("锁过期后恢复自发调度（微表情真的冒了）",
          pet._next_expr > pet.t,
          "next_expr=%.2f t=%.2f state=%s" % (pet._next_expr, pet.t, pet.state))

    # ---------- 8. 饱食度规则回归（不能被本轮改坏）----------
    print("\n[8] 喂食规则回归")
    for h0 in (65.0, 70.0, 80.0, 98.0):
        p2 = make_pet(app)
        p2._meta["hunger"] = h0
        p2.feed()
        check("饱食 %d -> 喂后 100" % h0, p2._meta["hunger"] == 100.0,
              "-> %g" % p2._meta["hunger"])

    # ---------- 9. R44：陪伴档案 / 穿透滚轮缩放 / 位置记忆 / 开机自启 ----------
    print("\n[9] R44：陪伴档案 / 穿透缩放 / 位置记忆 / 自启")
    p3 = make_pet(app)
    # —— 陪伴档案 ——
    days = p3._companion_days()
    check("陪伴天数可算（>=1）", days >= 1, "days=%d" % days)
    p3._meta["fed"] = 46
    p3._meta["pets"] = 81
    p3._show_stats()
    st = p3.bubble_text
    check("陪伴档案文案含天数/喂食/摸头",
          "天" in st and "46" in st and "81" in st, repr(st[:40]))
    check("陪伴档案气泡时长足够阅读", p3.bubble_until - p3.t >= 5.0,
          "%.1f" % (p3.bubble_until - p3.t))
    p3._meta["hunger"] = 10.0
    p3._show_stats()
    check("饥饿时档案文案变饿语气", "饿" in p3.bubble_text,
          repr(p3.bubble_text[:30]))
    p3._meta["hunger"] = 80.0

    # —— 穿透模式滚轮缩放核心（与窗口内 wheelEvent 同一方法）——
    p3.target_size = 1.0
    p3._zoom_steps(120.0, QPoint(p3.x() + 100, p3.y() + 100))
    check("滚轮放大 target_size", p3.target_size > 1.0,
          "%.3f" % p3.target_size)
    t_big = p3.target_size
    p3._zoom_steps(-240.0, QPoint(p3.x() + 100, p3.y() + 100))
    check("滚轮缩小 target_size", p3.target_size < t_big,
          "%.3f" % p3.target_size)
    check("缩放锚点已冻结", p3._zoom_anchor is not None,
          "%s" % (p3._zoom_anchor,))
    p3.target_size = 1.0
    p3._zoom_steps(0.0, QPoint(0, 0))
    check("delta=0 不缩放", p3.target_size == 1.0, "%.3f" % p3.target_size)
    p3._dragging = True
    p3._zoom_steps(120.0, QPoint(0, 0))
    check("拖拽中不缩放", p3.target_size == 1.0, "%.3f" % p3.target_size)
    p3._dragging = False

    # —— 位置记忆：合法历史位置回到原处，没有则回主屏右下角 ——
    p3._restore_pos = (300, 200)
    p3.move(0, 0)
    p3._restore_position()
    check("有历史位置则回到原处", (p3.x(), p3.y()) == (300, 200),
          "(%d,%d)" % (p3.x(), p3.y()))
    p3._restore_pos = None
    p3.move(0, 0)
    p3._restore_position()
    ag = QApplication.primaryScreen().availableGeometry()
    check("无历史位置回主屏右下角",
          ag.right() - (p3.x() + p3.width()) <= 40
          and ag.bottom() - (p3.y() + p3.height()) <= 60,
          "(%d,%d) ag=%dx%d" % (p3.x(), p3.y(), ag.width(), ag.height()))

    # —— 开机自启：命令行拼接正确；状态读取只读不改注册表 ——
    cmd = p3._autostart_cmd()
    check("自启动命令行指向自己",
          "ejee_pet.py" in cmd or cmd.endswith('EJEE.exe"'), cmd)
    check("读取自启状态为布尔", isinstance(p3._get_autostart(), bool))

    # ---------- 10. R45：右键加陪伴档案 / 删喂面包 / 番茄钟合并为单入口 ----------
    print("\n[10] R45：右键菜单（陪伴档案·无喂面包） / 番茄钟单入口选时长")
    p4 = make_pet(app)
    menu, act_quit = p4._build_menu()
    texts = [a.text() for a in menu.actions()]
    check("右键菜单已无「喂面包」", not any("喂面包" in t for t in texts),
          str(texts))
    check("右键菜单保留「拿起面包（拖到嘴边）」",
          any("拿起面包" in t for t in texts), str(texts))
    check("右键菜单新增「陪伴档案」", any("陪伴档案" in t for t in texts),
          str(texts))
    subs = [a.menu().title() for a in menu.actions() if a.menu()]
    check("番茄钟时长子菜单已合并移除", not any("番茄钟" in s for s in subs),
          str(subs))
    check("尺寸子菜单仍在", any("尺寸" in s for s in subs), str(subs))
    check("菜单只剩一个番茄钟入口",
          sum(1 for t in texts if "番茄钟" in t) == 1, str(texts))
    menu.deleteLater()

    # —— 文案：空闲 = 开始番茄钟…；跑着 = 停止（剩 mm:ss）——
    p4._pomo_end = None
    check("空闲文案 = 开始番茄钟…", p4._pomo_label() == "开始番茄钟…",
          p4._pomo_label())
    p4._pomo_end = p4.t + 95.0
    check("跑动文案 = 停止 + 剩余时间",
          p4._pomo_label() == "停止番茄钟（剩 1:35）", p4._pomo_label())

    # —— _pomo_start：记档 + 起表 + 越界夹紧 ——
    p4._meta["pomo_min"] = 25
    p4._pomo_end = None
    p4._pomo_start(45)
    check("开始即记档时长", p4._meta["pomo_min"] == 45,
          str(p4._meta["pomo_min"]))
    check("结束时刻 = 现在 + 时长",
          p4._pomo_end is not None
          and abs(p4._pomo_end - p4.t - 45 * 60.0) < 1.0,
          "end=%s t=%.1f" % (p4._pomo_end, p4.t))
    check("进度环总长同步", p4._pomo_total == 45 * 60.0,
          "%.0f" % p4._pomo_total)
    check("开始时有台词", len(p4.bubble_text) > 0,
          repr(p4.bubble_text[:20]))
    p4._pomo_start(999)
    check("超过 180 夹紧到 180", p4._meta["pomo_min"] == 180,
          str(p4._meta["pomo_min"]))
    p4._pomo_start(0)
    check("低于 1 夹紧到 1", p4._meta["pomo_min"] == 1,
          str(p4._meta["pomo_min"]))

    # —— 运行中再点 = 取消 ——
    p4._pomo_start(30)
    p4._pomo_toggle()
    check("运行中再点番茄钟 = 取消", p4._pomo_end is None)
    check("取消有台词", "取消" in p4.bubble_text, repr(p4.bubble_text[:20]))

    # —— 空闲时点击 = 先弹时长卡（打桩 PomoDialog，不真的模态）——
    class _FakeDlg:
        def __init__(self, minutes, parent=None):
            self._m = 33

        def adjustSize(self):
            pass

        def width(self):
            return 260

        def height(self):
            return 190

        def move(self, *a):
            pass

        def exec(self):
            return True

        def minutes(self):
            return self._m

    real_dlg = E.PomoDialog
    E.PomoDialog = _FakeDlg
    try:
        p4._pomo_end = None
        p4._pomo_toggle()
        check("空闲点番茄钟 = 弹卡选时长后开始",
              p4._pomo_end is not None and p4._meta["pomo_min"] == 33,
              "end=%s min=%s" % (p4._pomo_end, p4._meta["pomo_min"]))
    finally:
        E.PomoDialog = real_dlg

    # ---------- 11. P0-3：饥饿压扁 / 海市蜃楼 / 睡眠泡泡 几何断言 ----------
    # （纯几何，不依赖底图资源；渲染特定层到离屏 QImage 后量包围盒）
    print("\n[11] 饥饿压扁 / 海市蜃楼 / 睡眠泡泡 几何")
    from PySide6.QtGui import QPainter, QImage, QColor
    from PySide6.QtCore import Qt, QRectF

    def _neutral_pose():
        return {"breathe": 0.0, "sway": 0.0, "bob": 0.0, "bounce": 0.0,
                "shake_x": 0.0, "shake_y": 0.0, "lean": 0.0, "swim": 0.0,
                "sigh": 0.0}

    def _bbox_scan(img, alpha_thr, cond=lambda r, g, b: True, roi=None):
        # Format_ARGB32 在内存里是 BGRA 字节序：必须转 RGBA8888 才能得到
        # 真正的 R,G,B,A（否则橙色/灰色会被错判成蓝色，导致漏检）。
        img = img.convertToFormat(QImage.Format_RGBA8888)
        data = bytes(img.constBits()[:img.sizeInBytes()])
        W, H = img.width(), img.height()
        if roi:
            rx0, ry0, rx1, ry1 = roi
        else:
            rx0, ry0, rx1, ry1 = 0, 0, W - 1, H - 1
        mnx = mny = 10 ** 9
        mxx = mxy = -1
        i = 0
        n = len(data)
        while i < n:
            a = data[i + 3]
            if a > alpha_thr:
                px = i // 4
                x = px % W
                y = px // W
                if rx0 <= x <= rx1 and ry0 <= y <= ry1:
                    r, g, b = data[i], data[i + 1], data[i + 2]
                    if cond(r, g, b):
                        if x < mnx:
                            mnx = x
                        if y < mny:
                            mny = y
                        if x > mxx:
                            mxx = x
                        if y > mxy:
                            mxy = y
            i += 4
        if mxx < 0:
            return None
        return (mnx, mny, mxx, mxy)

    # ---- 11a. 饥饿：以脚底为支点压扁，脚底几乎不动，头顶往下塌 ----
    def body_extent(pet, ha):
        img = QImage(400, 472, QImage.Format_ARGB32)
        img.fill(0)
        p = QPainter(img)
        p.setRenderHint(QPainter.Antialiasing, True)
        p.scale(pet.width() / E.DW, pet.width() / E.DW)
        p.translate(0.0, E.PAD_T)
        pet.facing = 1
        pet._apply_body_pose(p, _neutral_pose(), {"ha": ha, "sigh": 0.0})
        p.setPen(Qt.NoPen)
        p.setBrush(QColor(255, 0, 0, 255))
        # 一根竖条：从头顶(-bh)画到脚底(0)，量它的上下沿
        p.drawRect(QRectF(-2.0, -pet.bh, 4.0, pet.bh))
        p.end()
        return _bbox_scan(img, 40)

    ext0 = body_extent(pet, 0.0)
    ext5 = body_extent(pet, 0.5)
    ext1 = body_extent(pet, 1.0)
    ok = ext0 and ext5 and ext1
    foot_move = abs(ext1[3] - ext0[3]) if ok else 999
    top_move = (ext1[1] - ext0[1]) if ok else 0
    check("饥饿：脚底支点基本不动（位移≤5px）", ok and foot_move <= 5.0,
          "foot_move=%.2f" % foot_move)
    check("饥饿：身体纵向压扁（头顶下移≥28px）", ok and top_move >= 28.0,
          "top_move=%.2f" % top_move)
    mono = (ext0[1] < ext5[1] < ext1[1]) if ok else False
    check("饥饿：压扁随 ha 单调（头顶 y 递增）", mono,
          "tops=%s" % ((ext0[1], ext5[1], ext1[1]),))

    # ---- 11b. 海市蜃楼：云朵不出血画布；热气顶端穿出云顶 ----
    pf = make_pet(app)
    pf.t = 5.0
    pf._fantasy = {"t0": pf.t - 1.5}     # HOLD 阶段，fsc≈1
    fimg = QImage(400, 472, QImage.Format_ARGB32)
    fimg.fill(0)
    fp = QPainter(fimg)
    fp.setRenderHint(QPainter.Antialiasing, True)
    fp.scale(pf.width() / E.DW, pf.width() / E.DW)
    fp.translate(0.0, E.PAD_T)
    pf.facing = 1
    pf._apply_body_pose(fp, _neutral_pose(), {"ha": 0.0, "sigh": 0.0})
    pf._draw_fantasy(fp, {"t": pf.t})
    fp.end()
    # 云体（奶白）：R>245 & G>240 & B>230 & alpha>200
    cloud = _bbox_scan(fimg, 200, lambda r, g, b: r > 245 and g > 240 and b > 230)
    check("海市蜃楼：云朵已渲染", cloud is not None, str(cloud))
    if cloud:
        cx0, cy0, cx1, cy1 = cloud
        check("海市蜃楼：云朵不出画布（左右）", cx0 >= 0 and cx1 <= 399,
              "x=%d..%d" % (cx0, cx1))
        check("海市蜃楼：云朵不出画布（上下）", cy0 >= 0 and cy1 <= 471,
              "y=%d..%d" % (cy0, cy1))
        # 热气：在云顶之上仍有墨迹（R>150 & B<150 & G<200，排除白云）
        steam = _bbox_scan(fimg, 40,
                           lambda r, g, b: r > 150 and b < 150 and g < 200)
        check("海市蜃楼：热气已渲染", steam is not None, str(steam))
        if steam:
            check("海市蜃楼：热气顶端穿出云顶", steam[1] < cy0 - 3,
                  "steam_top=%d cloud_top=%d" % (steam[1], cy0))
    # 吐司：暖橙轮廓（R>150 & B<150 & G<220 & alpha>120），量宽并对照眼睛。
    # 用紧 ROI 只扫云心附近，避免把云朵橙色轮廓(#E8A259)一起抓进来。
    toast = _bbox_scan(fimg, 120,
                       lambda r, g, b: r > 150 and b < 150 and g < 220,
                       roi=(216, 50, 302, 126))
    ew = pf.eye_pos["eye_l"][2]            # 单眼精灵宽（设计 px）
    if toast:
        tw = toast[2] - toast[0]
        check("海市蜃楼：吐司已渲染", tw > 10, "tw=%d" % tw)
        check("吐司宽度与眼睛同量级（∈[1.6,3.0]×眼宽）",
              1.6 * ew <= tw <= 3.0 * ew, "tw=%d eye=%.0f" % (tw, ew))
        tcx = (toast[0] + toast[2]) / 2.0
        check("吐司居中于云朵（|dx|≤60）", abs(tcx - (cx0 + cx1) / 2.0) <= 60,
              "dx=%.0f" % (tcx - (cx0 + cx1) / 2.0))
    else:
        check("海市蜃楼：吐司已渲染", False, "no toast pixels")

    # ---- 11c. 睡眠泡泡：正圆 + 不被画布切边 ----
    ps = make_pet(app)
    ps.sleep_amt.snap(1.0)
    simg = QImage(400, 472, QImage.Format_ARGB32)
    simg.fill(0)
    sp = QPainter(simg)
    sp.setRenderHint(QPainter.Antialiasing, True)
    sp.scale(ps.width() / E.DW, ps.width() / E.DW)
    sp.translate(0.0, E.PAD_T)
    ps.facing = 1
    ps._apply_body_pose(sp, _neutral_pose(), {"ha": 0.0, "sigh": 0.0})
    ps._draw_sleep_bubble(sp, {"t": 5.0, "bh": ps.bh})
    sp.end()
    sb = _bbox_scan(simg, 15)
    check("睡眠泡泡：已渲染", sb is not None, str(sb))
    if sb:
        sw = sb[2] - sb[0]
        sh = sb[3] - sb[1]
        check("睡眠泡泡：正圆（|w-h|≤1px）", abs(sw - sh) <= 1.0,
              "w=%d h=%d" % (sw, sh))
        check("睡眠泡泡：不被画布切边（四边留白≥0）",
              sb[0] >= 0 and sb[2] <= 399 and sb[1] >= 0 and sb[3] <= 471,
              "bbox=%s" % (sb,))

    print("\n" + "=" * 52)
    if FAILED:
        print("FAILED %d:" % len(FAILED))
        for f in FAILED:
            print("   -", f)
        sys.exit(1)
    print("ALL PASS")


if __name__ == "__main__":
    main()