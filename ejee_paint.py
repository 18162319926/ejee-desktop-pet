"""EJEE 纯绘制层（P3-13：无状态绘制方法与绘制共享常量都住在这里）。

EjeePaintMixin 只做「给一块 QPainter，按当前帧参数画东西」：
不含状态机、输入、窗口逻辑。方法体从 ejee_pet.py 逐字搬运，
由 EjeePet(EjeePaintMixin, QWidget) 继承混入，行为零变化。
验收基准：--shot 14 张预览与基线逐字节一致（tools/check_preview.py --run）。

本模块同时是「绘制共享层」的单一出处：几何/色板/字体/气泡主题表 /
clamp 都在这里定义，ejee_pet 顶部 import 回去（E.DW 等引用不变）。
"""
import math
import sys

from PySide6.QtCore import Qt, QRectF, QPointF
from PySide6.QtGui import (QColor, QPen, QBrush, QPainterPath, QFont,
                           QLinearGradient, QRadialGradient)


# ---------------- 设计坐标系（400 x 472） ----------------
# 画布上下都留透明区，头顶那块（PAD_T）是给饥饿状态的海市蜃楼云朵用的——
# 它比角色高得多，原先 400 高只够塞下睡眠泡泡，云朵一大就贴边甚至被切。
# 角色本身仍占设计坐标 y 85..318（底图锚点 BCY 不动），整幅画面在
# paintEvent 里统一 translate(0, PAD_T) 下移，所以所有设计坐标一个都不用改。
# 上下两块透明区在落位/拖拽/缩放时按 _win_pad_b 的镜像量补偿，宠物不会悬空。
DW, DH = 400.0, 472.0
PAD_T = 72.0          # 顶部透明区：海市蜃楼云朵的舞台
DH_CHAR = 340.0       # 角色（含投影）实际用到的高度；DH-PAD_T-DH_CHAR 是
                      # 底部透明余量（给睡眠正圆泡泡）：落位时不计入可见高度
# 散步环带：窗口整体贴近屏幕四周边框（窗沿距边 BAND_NEAR..BAND_FAR px），
# 沿环带边走边不横穿屏幕中央、不挡中间内容
BAND_NEAR = 26.0        # 环带外沿：窗沿距屏幕边最近
BAND_FAR = 150.0        # 环带内沿：窗沿距屏幕边最远
RING_STEP = 46.0        # 环上路径点间距 px

# ------- 色板 -------
BODY_TOP = QColor("#F2A55B")
CREAM = QColor("#FBE8C4")
ACCENT = QColor("#F19A2E")
INK = QColor("#5C3A22")
CLOUD = QColor("#9AA7B5")
CONFETTI = ["#F6C24E", "#F0923C", "#8CCB57", "#FBE8C4", "#F6D14E", "#F3D9A6"]
HEARTS = ["#F27D93", "#F05A7E", "#F6A0B5"]
STARS = ["#F6D14E", "#FFE28A", "#FFC93C"]
JUICE = ["#FFA630", "#FFBE50", "#FF9628", "#FFD07A"]   # 橘子汁水滴

# ---- 气泡字体 ----
# 圆润体（幼圆优先，回退雅黑/黑体）：金鱼宝宝的形象就该配圆滚滚的字，
# 日常 / 摸头 / 喂食 / 傲娇 / 晕车 / 睡眠都用它
FONT_ROUND = ("YouYuan", "幼圆", "Microsoft YaHei UI",
              "Microsoft YaHei", "SimHei")
# 硬朗体（雅黑 / 黑体加粗）：只给生气用，读出"炸毛"的力道
FONT_PUNCH = ("Microsoft YaHei UI", "Microsoft YaHei", "SimHei")

# ---- 气泡主题表：每种情绪一套皮肤（边色 / 上下渐变 / 高光 / 挂饰 / 摇摆）----
# edge 边线色；top/bot 渐变填充的上亮下沉色；gloss 左上高光强度；
# deco 挂饰（heart 小爱心 / juice 挂汁滴 / tear 挂泪滴 / None）；
# wob 整框摇摆幅度（设计度）+ wob_sp 摇摆角速度（rad/s）：
# 晕车是坐船似的慢摇、生气是细颤、傲娇是微抖；
# font round 圆体 / punch 加粗硬体；size 字号（设计 px）
BUBBLE_THEMES = {
    # 奶油云泡泡：日常 / 问候 / 摸头 / 喂食 / 闲聊 / 番茄钟 / 缩放 / 双击
    "cloud": dict(edge="#E8A259", top="#FFFFFF", bot="#FFF1DA",
                  gloss=0.9, deco=None, wob=0.0, wob_sp=6.0,
                  font="round", size=12),
    # 傲娇（连摸 5 下）：粉色泡泡 + 两颗蹦跶小爱心，轻轻发抖
    "shy": dict(edge="#F0A3B8", top="#FFFFFF", bot="#FFE7EE",
                gloss=0.9, deco="heart", wob=0.9, wob_sp=6.0,
                font="round", size=12),
    # 恶作剧（喷橘子汁）：果汁橙泡泡 + 底缘挂一滴汁 + 旁边两颗飞溅小汁滴
    "mischief": dict(edge="#E8834A", top="#FFFFFF", bot="#FFE5C6",
                     gloss=0.9, deco="juice", wob=0.0, wob_sp=6.0,
                     font="round", size=12),
    # 晕车（边缘疯狂拉扯）：浅绿 + 整框大幅慢摇，像坐在颠簸的小船里
    "dizzy": dict(edge="#8FBF6A", top="#FFFFFF", bot="#F0F9E4",
                  gloss=0.7, deco=None, wob=3.2, wob_sp=11.0,
                  font="round", size=12),
    # 生气（拖到边缘 / 抓尾巴）：橙红爆炸框 + 加粗硬体 + 细颤
    "burst": dict(edge="#E2683A", top="#FFF3E8", bot="#FFDCBE",
                  gloss=0.0, deco=None, wob=0.7, wob_sp=23.0,
                  font="punch", size=12),
    # 可怜（面包掉地上）：浅蓝 + 底缘挂一滴将落未落的眼泪
    "crumb": dict(edge="#9BB8D8", top="#FFFFFF", bot="#E7F1FA",
                  gloss=0.8, deco="tear", wob=0.0, wob_sp=6.0,
                  font="round", size=12),
    # 吃饱（打嗝 / 拒食）：水蓝圆泡泡
    "round": dict(edge="#9FD4EC", top="#FFFFFF", bot="#E6F6FD",
                  gloss=0.0, deco=None, wob=0.0, wob_sp=6.0,
                  font="round", size=12),
    # 睡眠：Zzz 小泡泡（字大一点，配泡泡里的呼噜声）
    "zzz": dict(edge="#AFC6E4", top="#FFFFFF", bot="#EAF3FC",
                gloss=0.0, deco=None, wob=0.0, wob_sp=6.0,
                font="round", size=15),
}

# 状态 -> 气泡主题名（优先于 bubble_style，让每个状态有自己的皮肤）
STATE_BUBBLE_THEME = {
    "shy": "shy", "mischief": "mischief", "dizzy": "dizzy",
    "sleep": "zzz", "angry": "burst",
}

OMEGA_SW = 46.0                 # ω 嘴线宽（mouth.png 实测 base 像素，峰顶竖穿）

# 尾巴轻摆：剪切矩形（base 像素）。y>960 只有尾巴大圆与透明背景
# （大圆左缘 x≈1405-1420，前爪右缘 x<1345，矩形左界留 >40px 缓冲）
TAIL_RECT = (1350, 960, 1548, 1236)

# 头顶叶子（设计坐标，由 tools/make_leaf_assets.py 从 base.png 拆出）：
# (左上 x, 左上 y, 宽, 高, 轴心 x, 轴心 y)。轴心＝叶柄插入头皮处，
# 饥饿耷拉时绕它旋转，根部不动，接缝不会裂开。
LEAF_GEO = (158.97, 85.0, 51.87, 48.67, 178.59, 132.72)

# ---- 主文件回用的共享工具/色 ----

def clamp(v, lo, hi):
    return max(lo, min(hi, v))


EYE_DARK = QColor("#3A271E")
OMEGA_COL = "#A34B12"           # ω 嘴线条色（不透明最暗 15% 中位色）


class EjeePaintMixin:
    """无状态纯绘制方法集（由 EjeePet 混入；self 即完整的 EjeePet 实例，
    可以自由访问其状态属性与辅助方法，但自身不持有任何状态）。"""


    def _draw_eyes(self, p, f):
        """眼睛：精灵变形 + 表情眼（眯眼弧 ∩ / 睡眠闭眼 ︶ / 泪花 /
        ＞＜ 坏笑 / 怒容眉与眼周阴影）。坐标均为身体组内的相对设计坐标。"""
        t, c, gaze, ha = f["t"], f["c"], f["gaze"], f["ha"]
        sa, ma, blink = f["sa"], f["ma"], f["blink"]
        nrv = clamp(self._pomo_nrv.v, 0.0, 1.0)   # 番茄钟最后一分钟：眼睛瞪大一点
        dz = clamp(self._dizzy_amt.v, 0.0, 1.0)   # 晕车显形度
        # 腮红（生气/委屈时随 puff 渐显）：双眼下方偏外侧两团暖红。
        # 用多层同心椭圆叠出柔边 —— QRadialGradient 是正圆，映射到扁椭圆
        # 时会在边缘留下硬边，实色多层的台阶在这么大尺度上看不出来。
        bk = clamp(c["puff"], 0.0, 1.0) * (1.0 - 0.85 * ha)
        if bk > 0.03:
            p.save()
            p.setOpacity(bk)
            p.setPen(Qt.NoPen)
            for key, sgn in (("eye_l", -1), ("eye_r", 1)):
                ex, ey, ew, eh = self.eye_pos[key]
                ex -= self.BCX
                ey -= self.BCY
                bx = ex + sgn * ew * 0.22      # 眼睛下方、略偏外侧（眼外角下）
                by = ey + eh * 0.54
                rx, ry = ew * 0.29, eh * 0.17
                for i, al in enumerate((11, 12, 14, 16, 18, 21, 24, 27)):
                    k = 1.0 - 0.095 * i        # 外圈大而淡，内圈小而浓
                    p.setBrush(QColor(226, 84, 88, al))
                    p.drawEllipse(QPointF(bx, by), rx * k, ry * k)
            p.restore()
        # 眼睛精灵：缩放（月牙/放大）、下垂、旋转、眨眼、视线；
        # 官方五表情：happy 双眯眼弧 ∩∩、surprised 左眼眨眼
        for key, pm, rot_dir, wk in (
                ("eye_l", self.eye_l_pm, -1, clamp(self.wink_l.v, 0.0, 1.0)),
                ("eye_r", self.eye_r_pm, 1, clamp(self.wink_r.v, 0.0, 1.0))):
            ex, ey, ew, eh = self.eye_pos[key]
            ex -= self.BCX
            ey -= self.BCY
            if wk < 0.995:
                epm = self._cache_pm(key, pm, self._dev_px(ew))
                p.save()
                # 晕车时精灵整个淡出，脸上只留眩晕蚊香（见
                # _draw_dizzy_eyes）——精灵 + 瞳孔蚊香叠一起会变成
                # "黑圈套白蚊香"的风镜，两层结构反而最不自然
                p.setOpacity((1.0 - wk) * (1.0 - sa) * (1.0 - ma)
                             * (1.0 - dz))
                p.translate(ex + gaze[0] * self.facing * 3.5 * (1.0 + 0.9 * ha),
                            ey + c["eye_dy"] + gaze[1] * 2.5 * (1.0 + 0.9 * ha)
                            + ha * 2.2)
                p.rotate(rot_dir * c["eye_rot"])
                # 眼睛保持原形：饥饿/叹气都不压扁（用户要求）
                p.scale(c["eye_sx"] * (1.0 + 0.05 * nrv),
                        c["eye_sy"] * max(0.05, blink)
                        * (1.0 + 0.04 * nrv))
                p.drawPixmap(QRectF(-ew / 2, -eh / 2, ew, eh), epm,
                             QRectF(0, 0, epm.width(), epm.height()))
                p.restore()
            if wk > 0.005:
                # 眯眼弧 ∩（开心闭眼 / 坏笑眨眼）
                p.save()
                p.setOpacity(wk)
                p.setPen(QPen(QColor("#4A2C1E"), 5.0, Qt.SolidLine,
                              Qt.RoundCap))
                p.setBrush(Qt.NoBrush)
                aw, ah = ew * 0.30, eh * 0.24
                p.drawArc(QRectF(ex - aw, ey + c["eye_dy"] - ah - 2,
                                 2 * aw, 2 * ah), 0, 180 * 16)
                p.restore()
        # 睡眠闭眼：柔和下弯弧 ︶（放松眼睑，与 happy ∩ 同笔画风格），
        # 随 sleep_amt 渐显盖过压扁的精灵，入睡过渡像眼睛缓缓合上
        if sa > 0.005:
            p.save()
            p.setOpacity(sa)
            p.setPen(QPen(QColor("#4A2C1E"), 5.0, Qt.SolidLine, Qt.RoundCap))
            p.setBrush(Qt.NoBrush)
            for key in ("eye_l", "eye_r"):
                ex, ey, ew, eh = self.eye_pos[key]
                ex -= self.BCX
                ey -= self.BCY
                aw, ah = ew * 0.28, eh * 0.13
                p.drawArc(QRectF(ex - aw, ey + c["eye_dy"] - ah,
                                 2 * aw, 2 * ah), 180 * 16, 180 * 16)
            p.restore()
        # （原「可怜泪花」已删除：泪珠读作委屈/快哭，和“饿瘪了”的语义打架。
        #   饥饿层现在只留：原形眼睛、波浪嘴（不流口水）、枯萎叶子、海市蜃楼）
        # 恶作剧坏笑眼：＞＜ 折线（双眼向中间挤成 V 形，精灵同步淡出）
        if ma > 0.02 and sa < 0.5:
            p.save()
            p.setOpacity(ma)
            p.setPen(QPen(QColor("#4A2C1E"), 5.0, Qt.SolidLine,
                          Qt.RoundCap, Qt.RoundJoin))
            p.setBrush(Qt.NoBrush)
            for key, o in (("eye_l", 1), ("eye_r", -1)):
                ex, ey, ew, eh = self.eye_pos[key]
                ex -= self.BCX
                ey -= self.BCY
                cxx, cyy = ex, ey + c["eye_dy"] - 1.0
                aw, ah = ew * 0.21, eh * 0.17
                ch = QPainterPath()
                ch.moveTo(cxx - o * aw, cyy - ah)
                ch.lineTo(cxx + o * aw * 0.75, cyy)
                ch.lineTo(cxx - o * aw, cyy + ah)
                p.drawPath(ch)
            p.restore()
        # 晕车蚊香圈眼：瞳孔里转起一团蚊香，两眼反向转 = 经典晕眩符号
        if dz > 0.02:
            self._draw_dizzy_eyes(p, c, gaze, dz)
        # （原"委屈眼上眼穹顶"已删除；现在可怜层改成直接复用 angry 这一套
        #   眉眼：puff 弹簧被 _pity 顶起，所以面包掉地上时画的就是怒容眉。）
        # 怒容眉眼（官方表情 4，随 puff 弹簧渐显）：眼周淡阴影 + 脸红 +
        # 半眯怒视眼（上眼睑盖住瞳孔上半 + 粗眼线）+ 眉心折角压眉。
        # 素材月牙是"笑眼"符号，直接配怒眉会各说各话——用半透明上眼睑
        # 把它压成"怒视下压眼"，剩下的下半弧恰好就是压着的怒眼形状。
        if c["puff"] > 0.03:
            pf = clamp(c["puff"], 0.0, 1.0)
            p.save()
            p.setOpacity(pf)
            # （原"脸颊外侧两团径向渐变脸红"已上移到 _draw_eyes 开头，
            #   改成眼睛下方的多层椭圆腮红：单层径向渐变在扁椭圆上有硬边）
            for key, sgn in (("eye_l", -1), ("eye_r", 1)):
                ex, ey, ew, eh = self.eye_pos[key]
                ex -= self.BCX
                ey -= self.BCY
                # 怒眉微颤：气到眉毛发抖（左右眼错开相位）
                quiv = math.sin(self.t * 17.0 + (0.0 if sgn < 0 else 1.7)) * 0.4
                cx = ex + gaze[0] * self.facing * 3.5
                cy = ey + c["eye_dy"] + gaze[1] * 2.5 + quiv
                # 怒眉：不画描边线，改成一笔填充的眉形——眉尾细、眉腰略粗、
                # 眉头收尖，沿横向带一点自然的拱度（像手绘一笔带过的眉毛，
                # 与底图柔和的渐变/高光融得住；等宽曲线会像贴上去的黑线条）
                p.setPen(Qt.NoPen)
                p.setBrush(QColor(EYE_DARK))
                p.drawPath(self._brow_path(cx, cy, ew, eh, sgn))
            p.restore()

    def _draw_dizzy_eyes(self, p, c, gaze, dz):
        """晕车蚊香圈眼：不画任何眼睛底图，只在原眼位上一对深棕蚊香。

        弯路记一笔：先试过"精灵保留 + 瞳孔上画米白蚊香"，也试过"白圆饼 +
        深棕蚊香"——前者是深色大眼圈里再套一圈白螺旋，远看像戴了风镜；
        后者干脆把角色眼睛换成图标。最后确定**底图全撤**：底图眼洞本来就是
        修补成皮肤的，撤掉后是干净的橙色脸颊，一对蚊香直接落在脸上，才是最
        经典的晕眩画法。
        尺寸取 0.46 眼宽（≈ 原眼径），太小会显得脸空、像随手涂的圈；线色用
        比眼珠深棕浅一档的 (86,58,42)，比纯黑柔和、又不至于淡成花纹。
        两眼反向旋转，一笔螺旋外圈起笔、向内收细。
        """
        p.save()
        p.setOpacity(dz)
        col = QColor(86, 58, 42)
        for key, spin in (("eye_l", 1.0), ("eye_r", -1.0)):
            ex, ey, ew, eh = self.eye_pos[key]
            ex -= self.BCX
            ey -= self.BCY
            cx = ex + gaze[0] * self.facing * 3.5 * 0.3
            cy = ey + c["eye_dy"]
            base_a = self.t * 2.1 * spin
            rad0, rad1 = ew * 0.46, ew * 0.034
            N = 52
            pts = []
            for k in range(N + 1):
                u = k / N
                aa = base_a + u * 2.4 * math.tau
                rad = rad0 + (rad1 - rad0) * u
                pts.append(QPointF(cx + math.cos(aa) * rad,
                                   cy + math.sin(aa) * rad * 0.96))
            path = QPainterPath()
            path.moveTo(pts[0])
            for i in range(1, N):
                path.quadTo(pts[i],
                            QPointF((pts[i].x() + pts[i + 1].x()) * 0.5,
                                    (pts[i].y() + pts[i + 1].y()) * 0.5))
            path.lineTo(pts[N])
            p.setPen(QPen(col, max(2.0, ew * 0.052), Qt.SolidLine,
                          Qt.RoundCap, Qt.RoundJoin))
            p.setBrush(Qt.NoBrush)
            p.drawPath(path)
        p.restore()

    @staticmethod
    def _brow_path(cx, cy, ew, eh, sgn):
        """生气眉：一笔填充出来的锥形眉（眉尾细 -> 眉腰最粗 -> 眉头收尖），
        脊线带一点拱度。等宽描边线会像"贴上去的黑条"，填充笔触更像
        画在脸上的眉毛，也和底图的柔和渐变融得住。
        sgn = -1 左眼（外侧在左）/ +1 右眼。"""
        N = 14
        tops, bots = [], []
        for i in range(N + 1):
            u = i / N
            x = cx + sgn * ew * (0.28 - 0.58 * u)
            y = cy + eh * (-0.545 + 0.170 * u + 0.014 * math.sin(math.pi * u))
            # 脊线切向（沿 u 增大方向）-> 法向（指向上方）
            v = min(1.0, u + 0.01)
            x2 = cx + sgn * ew * (0.28 - 0.58 * v)
            y2 = cy + eh * (-0.545 + 0.170 * v
                            + 0.014 * math.sin(math.pi * v))
            tx, ty = x2 - x, y2 - y
            ln = math.hypot(tx, ty) or 1.0
            nx, ny = ty / ln, -tx / ln
            half = eh * 0.026 * math.sin(math.pi * u) ** 0.7
            tops.append(QPointF(x + nx * half, y + ny * half))
            bots.append(QPointF(x - nx * half, y - ny * half))
        path = QPainterPath()
        path.moveTo(tops[0])
        for pt in tops[1:]:
            path.lineTo(pt)
        for pt in reversed(bots):
            path.lineTo(pt)
        path.closeSubpath()
        return path

    def _draw_mouth(self, p, f):
        """嘴：ω 精灵 + 各表情嘴（张嘴笑 / 吐舌 / 生气撇嘴 + 人中 / 睡眠圆嘴 /
        饥饿波浪嘴（不流口水）/ 恶作剧坏笑 + 舌头）。"""
        bw, bh, s2 = f["bw"], f["bh"], f["s2"]
        sa, ma, ha = f["sa"], f["ma"], f["ha"]
        # 可怜层（面包掉地上）：表情与 angry 一致，这里把生气撇嘴也画出来
        pty = clamp(self._pity.v, 0.0, 1.0)
        # 哈欠显形度：睡前犯困铺垫（张嘴渐大 -> 眼皮合上 -> 闭嘴时叹气收尾）
        ysp = getattr(self, "_yawn_amt", None)
        ya = clamp(ysp.v, 0.0, 1.0) if ysp is not None else 0.0
        # 嘴：ω 嘴恒显（官方设定），表情嘴从 ω 下缘展开——ω 下轮廓
        # 充当上唇，先画表情嘴再画 ω 精灵，重叠处 ω 笔画保持在最上层
        mr = self.coords["mouth"]
        mcx = -bw / 2 + (mr["x"] + mr["w"] / 2) * s2
        mcy = -bh + (mr["y"] + mr["h"] / 2) * s2
        op = self._mouth_open()
        alt = clamp(self.mouth_alt.v, 0.0, 1.0)
        mw, mh = mr["w"] * s2, mr["h"] * s2
        wbot = mcy + mh * 0.5                      # ω 下缘（设计坐标）
        if alt > 0.005:
            p.setOpacity(alt)
            if self.state == "happy" and op > 0.02:
                # 官方张嘴笑：居中圆袋腔。双层填充=一条连续外描边
                # （外层描边色 + 内层腔色内缩半笔宽），上缘藏 ω 下、
                # 绝不超出 ω；粉舌只填充
                dep = (mh * 1.15) * op + 5
                outer, inner, yb = self._omega_cavity(mcx, mcy, mw, mh,
                                                      s2, dep, span=0.32)
                p.setPen(Qt.NoPen)
                p.setBrush(QBrush(QColor(OMEGA_COL)))
                p.drawPath(outer)
                g = QLinearGradient(mcx, wbot, mcx, yb)
                g.setColorAt(0.0, QColor("#92501B"))
                g.setColorAt(1.0, QColor("#B56A38"))
                p.setBrush(QBrush(g))
                p.drawPath(inner)
                p.save()
                p.setClipPath(inner)
                p.setPen(Qt.NoPen)
                gt = QLinearGradient(mcx, yb - dep * 0.60, mcx, yb + dep * 0.30)
                gt.setColorAt(0.0, QColor("#E6899A"))
                gt.setColorAt(1.0, QColor("#D4717C"))
                p.setBrush(QBrush(gt))
                p.drawEllipse(QPointF(mcx, yb - dep * 0.02),
                              mw * 0.277, dep * 0.58)
                p.restore()
            elif self.state == "surprised":
                # 调皮吐舌（官方表情 5）：小一号圆袋腔（双层=一条外描边），
                # 舌头从腔底探出（只填充），上方留浅色口腔
                dep = mh * 0.80
                outer, inner, yb = self._omega_cavity(mcx, mcy, mw, mh,
                                                      s2, dep, span=0.28)
                p.setPen(Qt.NoPen)
                p.setBrush(QBrush(QColor(OMEGA_COL)))
                p.drawPath(outer)
                g2 = QLinearGradient(mcx, wbot, mcx, yb)
                g2.setColorAt(0.0, QColor("#92501B"))
                g2.setColorAt(1.0, QColor("#B56A38"))
                p.setBrush(QBrush(g2))
                p.drawPath(inner)
                p.save()
                p.setClipPath(inner)
                p.setPen(Qt.NoPen)
                gt2 = QLinearGradient(mcx, yb - dep * 0.55, mcx, yb + dep * 0.30)
                gt2.setColorAt(0.0, QColor("#E6899A"))
                gt2.setColorAt(1.0, QColor("#D4717C"))
                p.setBrush(QBrush(gt2))
                p.drawEllipse(QPointF(mcx, yb - dep * 0.03),
                              mw * 0.215, dep * 0.54)
                p.restore()
            elif self.state == "angry" or pty > 0.02:
                # 生气嘴：一条弧形撇嘴（两侧弧线朝下、弧度远小于 W 的双碗），
                # 正中再拉一根人中竖线，顶端插进鼻子下缘 —— 与平静状态的 ω
                # 一样是"中间朝上连到鼻子"的走向。整条嘴矢量绘制，同色同粗
                # 完全一体；ω 精灵同步淡出，整条嘴微垂 + 气到发颤。
                # （可怜层走同一分支：用户要求掉面包时的表情与 angry 一致）
                dy_m = 2.2 * alt + math.sin(self.t * 19.0) * 0.45  # 微垂+气到嘴抖
                # 线宽与平静状态（ω 素材）及其他表情嘴线（4.6）保持一致；
                # OMEGA_SW 是竖穿峰顶的高估值（8.7），直接用会粗一圈
                sw = 4.6
                hx = mw * 0.26            # 嘴角半宽
                y_apex = wbot - mh * 0.29 + dy_m   # 撇嘴中央（最高处）
                y_cor = wbot - mh * 0.04 + dy_m    # 嘴角（最低处）
                # 人中竖线顶端：ω 素材里那根"朝上连鼻子"的竖线正好顶到
                # 素材上沿往下 0.23mh（= 鼻子下缘）。这里取同一个位置，且
                # 不叠加 dy_m —— 嘴垂坠/发颤时上端仍咬住鼻子，不会脱开。
                y_top = mcy - mh * 0.23
                tail = mh * 0.07                   # 嘴角向外的下垂小尾巴
                pen = QPen(QBrush(QColor(OMEGA_COL)), sw, Qt.SolidLine,
                           Qt.RoundCap, Qt.RoundJoin)
                p.setPen(pen)
                p.setBrush(Qt.NoBrush)
                path = QPainterPath()
                path.moveTo(mcx - hx - 1.0, y_cor + tail)     # 左嘴角底
                path.lineTo(mcx - hx, y_cor)
                # 一条完整的弧（抛物线）：左嘴角 -> 正中最高的点 -> 右嘴角，
                # 中间是圆滑的顶，不是两段拼接的平顶
                path.quadTo(QPointF(mcx, 2.0 * y_apex - y_cor),
                            QPointF(mcx + hx, y_cor))
                path.lineTo(mcx + hx + 1.0, y_cor + tail)     # 右嘴角底
                p.drawPath(path)
                # 人中竖线：比嘴线略细（像一道人中，不做成一根粗棍）
                p.setPen(QPen(QBrush(QColor(OMEGA_COL)), sw * 0.74,
                              Qt.SolidLine, Qt.RoundCap))
                p.drawLine(QPointF(mcx, y_apex + 0.6),
                           QPointF(mcx, y_top))
                p.setPen(Qt.NoPen)
            p.setOpacity(1.0)
        # ω 嘴绘制：happy 张嘴笑 / surprised 吐舌时 ω 充当"上唇"必须保留；
        # 其余情况凡是替换嘴形在场（生气、睡眠、饥饿、恶作剧）都让 ω
        # "先走"——4 倍速快出（约 0.05s 内退净），避免换嘴过渡时新旧嘴形长时间重叠成残影；
        # alt 的淡出也连续跟随（不在 angry→idle 的状态切换瞬间跳回全显）
        fade_alt = 0.0 if self.state in ("happy", "surprised") else alt
        fade = max(fade_alt, sa, ha, ma, ya)
        if fade > 0.005:
            p.setOpacity(clamp(1.0 - fade * 4.0, 0.0, 1.0))
        else:
            p.setOpacity(1.0)
        p.drawPixmap(QRectF(mcx - mw / 2, mcy - mh / 2, mw, mh),
                     self.mouth_pm,
                     QRectF(0, 0, self.mouth_pm.width(),
                            self.mouth_pm.height()))
        if sa > 0.005:
            # 睡眠小圆嘴：ω 中心偏下一枚小椭圆，同 ω 描边色同笔画宽
            p.setOpacity(sa)
            p.setPen(QPen(QBrush(QColor(OMEGA_COL)), 4.6, Qt.SolidLine,
                          Qt.RoundCap))
            p.setBrush(Qt.NoBrush)
            p.drawEllipse(QPointF(mcx, mcy + mh * 0.06),
                          mw * 0.13, mh * 0.30)
            p.setOpacity(1.0)
        if ya > 0.02:
            # 打哈欠：嘴张成竖椭圆（比睡眠圆嘴大得多），幅度跟包络走；
            # ω 已按 ya 淡出。闭上那刻的叹气由 _tick 触发（身体一沉 +
            # 眼睛半闭），"啊——呼"一气呵成
            p.setOpacity(ya)
            p.setPen(QPen(QBrush(QColor(OMEGA_COL)), 4.6, Qt.SolidLine,
                          Qt.RoundCap))
            p.setBrush(Qt.NoBrush)
            p.drawEllipse(QPointF(mcx, mcy + mh * 0.10),
                          mw * (0.10 + 0.10 * ya),
                          mh * (0.16 + 0.62 * ya))
            p.setOpacity(1.0)
        if ha > 0.005 and sa < 0.5 and alt < 0.5 and ma < 0.3:
            # 饥饿波浪嘴：一条上下起伏的小波浪（4 段），比小圆洞更像
            # "饿得没力气、嘴都撑不住了"。ω 已按 ha 淡出，整条嘴自绘。
            p.setOpacity(ha)
            w = mw * 0.68
            y0 = mcy + mh * 0.13 + f["sigh"] * mh * 0.10
            amp = mh * 0.105
            seg = 4
            path = QPainterPath()
            path.moveTo(mcx - w / 2, y0 - amp * 0.35)
            # 段间用二次曲线交替上下，端点略收（波浪的“两端翘、中间塌”）
            for i in range(seg):
                x1 = mcx - w / 2 + w * (i + 0.5) / seg
                x2 = mcx - w / 2 + w * (i + 1.0) / seg
                dy = amp if i % 2 == 0 else -amp
                path.quadTo(QPointF(x1, y0 + dy), QPointF(x2, y0))
            p.setPen(QPen(QBrush(QColor(OMEGA_COL)), 4.6, Qt.SolidLine,
                          Qt.RoundCap, Qt.RoundJoin))
            p.setBrush(Qt.NoBrush)
            p.drawPath(path)
        # （原「脸颊凹陷深棕渐变」和「脸颊暗带」两版都删掉了：在橙色圆脸上
        #   无论怎么调都读成脏斑/竖纹。饿瘪改用几何做——见 _apply_body_pose
        #   里的 sag：以脚底为支点压扁 + 全身微微内收，轮廓自己就瘪了。）
        if ma > 0.02 and sa < 0.5 and alt < 0.5:
            # 恶作剧吐舌头：单边翘起的坏笑弧 + 探出来的粉舌头
            p.setOpacity(ma)
            # 舌头先画：竖向胶囊只描「侧壁 + 圆底」，顶部敞开不描边——
            # 让随后画上的嘴线描边盖住舌根，看不出接缝（闭合全包会像贴了颗胶囊）
            tcx = mcx + mw * 0.05
            ty0 = mcy + mh * 0.05          # 舌顶探进嘴线描边带内，左右壁都不露头
            tw0 = mw * 0.26
            th0 = mh * 0.68
            rect_t = QRectF(tcx - tw0 / 2, ty0 + th0 - tw0, tw0, tw0)
            # 填充：闭合路径（含顶边），保证舌根颜色连续伸到嘴线后方
            tf = QPainterPath()
            tf.moveTo(tcx - tw0 / 2, ty0)
            tf.lineTo(tcx - tw0 / 2, ty0 + th0 - tw0 / 2)
            tf.arcTo(rect_t, 180, 180)      # 逆时针过屏幕底部 = 圆底
            tf.lineTo(tcx + tw0 / 2, ty0)
            tf.closeSubpath()
            p.setPen(Qt.NoPen)
            p.setBrush(QColor(232, 137, 154))
            p.drawPath(tf)
            # 描边：只描侧壁 + 圆底；方帽 + 起点缩进，防止笔帽探出嘴线
            ts = QPainterPath()
            ts.moveTo(tcx - tw0 / 2, ty0 + 0.4)
            ts.lineTo(tcx - tw0 / 2, ty0 + th0 - tw0 / 2)
            ts.arcTo(rect_t, 180, 180)
            ts.lineTo(tcx + tw0 / 2, ty0 + 0.4)
            p.setPen(QPen(QColor("#C9737F"), 2.0, Qt.SolidLine,
                          Qt.SquareCap, Qt.RoundJoin))
            p.setBrush(Qt.NoBrush)
            p.drawPath(ts)
            # 舌面中缝
            p.setPen(QPen(QColor("#B25F6C"), 1.4, Qt.SolidLine, Qt.RoundCap))
            p.drawLine(QPointF(tcx, ty0 + th0 * 0.25),
                       QPointF(tcx, ty0 + th0 * 0.76))
            # 坏笑弧最后画：4.6px 描边压在舌根上，舌头就像从嘴里伸出来的
            p.setPen(QPen(QBrush(QColor(OMEGA_COL)), 4.6, Qt.SolidLine,
                          Qt.RoundCap, Qt.RoundJoin))
            p.setBrush(Qt.NoBrush)
            grin = QPainterPath()
            grin.moveTo(mcx - mw * 0.25, mcy + mh * 0.04)
            grin.quadTo(mcx - mw * 0.04, mcy + mh * 0.20,
                        mcx + mw * 0.21, mcy - mh * 0.06)
            p.drawPath(grin)
            p.setOpacity(1.0)

    def _draw_fantasy(self, p, f):
        """头顶幻想气泡：云朵里画着牛奶面包，2 秒后"啵"地破灭。

        尺寸（2026-10-19 用户两轮反馈）：
          · 吐司与眼睛同量级（65.5 × 70.9 设计 px）——这轮改成**直接按最终
            尺寸作画**，不再套 p.scale(3,3)：放大后的粗描边读起来像塑料，
            按最终尺寸画才能加烤边渐变、烤痕、气孔、黄油融化这些让它
            "像真面包"的细节；
          · 云朵跟着放大到 1.45 倍（141 × 139），为此把画布顶部让出
            PAD_T=72px 的透明区（见 DW/DH/PAD_T），云顶不再被 widget 切；
          · 锚点是身体组局部 (64,-300)：整团浮在头顶右上方，压不到叶子。
        """
        t = f["t"]
        # 幻想气泡：头顶云朵里画着牛奶面包，2 秒后"啵"地破灭
        if self._fantasy is not None:
            fage = t - self._fantasy["t0"]
            FIN, HOLD, POP = 0.3, 2.0, 0.3
            if fage < FIN:
                fa = fage / FIN
                fsc = 0.7 + 0.3 * fa
            elif fage < FIN + HOLD:
                fa = 1.0
                fsc = 1.0 + 0.015 * math.sin(t * 2.2)   # 轻微呼吸
            else:
                k3 = clamp((fage - FIN - HOLD) / POP, 0.0, 1.0)
                fa = 1.0 - k3
                fsc = 1.0 + 0.22 * k3
            if fa > 0.01:
                p.save()
                p.setOpacity(fa * 0.96)
                p.translate(64, -300 + 1.2 * math.sin(t * 1.7))  # 轻飘
                p.scale(fsc, fsc)
                # ---- 云朵：整体放大 1.45 倍（用户："云朵也要放大"）----
                # "啵"的扩散环画不出来（环几乎全躲在云后面），破灭感交给
                # 「云猛放大 + 急速淡出」和 _tick 里喷出的 4 颗 bubble 碎屑。
                p.save()
                p.scale(1.45, 1.45)
                # 云朵轮廓恒定不变（只整体缩放），缓存为实例属性——
                # 7 次 QPainterPath.united() 每帧重算纯属浪费。
                # 用 getattr 惰性构建：仿真的 scaffold 宠物不走 __init__。
                cloud = getattr(self, "_cloud_path", None)
                if cloud is None:
                    cloud = QPainterPath()
                    cloud.addEllipse(QPointF(0, 2), 40, 30)
                    for (bx, by, br) in ((-22, -26, 16), (2, -32, 18),
                                         (22, -24, 15), (-36, 4, 12),
                                         (38, 1, 11), (-22, 28, 14),
                                         (24, 27, 12)):
                        bump = QPainterPath()
                        bump.addEllipse(QPointF(bx, by), br, br)
                        cloud = cloud.united(bump)
                    self._cloud_path = cloud
                # 投影：右下轻偏移的一层柔影，做出一点空气感
                p.setPen(Qt.NoPen)
                p.setBrush(QColor(140, 95, 50, 30))
                p.save()
                p.translate(2.6, 3.6)
                p.drawPath(cloud)
                p.restore()
                # 云体：上缘暖白、下缘偏冷白，读成有厚度的云
                cg = QLinearGradient(0.0, -52.0, 0.0, 46.0)
                cg.setColorAt(0.0, QColor(255, 251, 242, 248))
                cg.setColorAt(0.55, QColor(252, 250, 246, 246))
                cg.setColorAt(1.0, QColor(236, 240, 246, 244))
                p.setPen(QPen(QColor("#E8A259"), 2.4, Qt.SolidLine,
                              Qt.RoundCap, Qt.RoundJoin))
                p.setBrush(cg)
                p.drawPath(cloud)
                # 云内受光/背光：顶部一道淡白高光、底部一层冷蓝阴影
                p.save()
                p.setClipPath(cloud)
                p.setPen(Qt.NoPen)
                p.setBrush(QColor(255, 255, 255, 120))
                p.drawEllipse(QPointF(-14, -34), 24, 13)
                p.setBrush(QColor(198, 214, 234, 90))
                p.drawEllipse(QPointF(20, 30), 30, 15)
                p.restore()
                p.restore()
                # 意念泡小尾：两枚渐小的圆，从云底斜垂向头顶
                for (tx_, ty_, tr_) in ((8.0, 52.0, 5.5), (3.0, 66.0, 3.8)):
                    p.setPen(QPen(QColor("#E8A259"), 2.4))
                    p.setBrush(QColor(255, 251, 243, 244))
                    p.drawEllipse(QPointF(tx_, ty_), tr_, tr_)
                # ================= 牛奶吐司（按最终尺寸作画） =================
                # 用户："面包图标要更真实"。真实感来自四层：
                #   ① 烤边壳（比面包心大 4.4px，焦黄竖向渐变 + 深棕收边）
                #   ② 面包心（奶白纵向渐变，边缘一圈内阴影）
                #   ③ 表面细节（软边烤痕斑 + 气孔孔洞 + 左上受光）
                #   ④ 一块正在融化的黄油（带高光和往下淌的一道）
                TW, TH = 35.0, 26.0        # 半宽 / 半高
                TCY = -2.0                # 吐司中心相对云心的纵向偏移

                def toast_path(inset):
                    """吐司轮廓；inset>0 时整体向内收（烤边壳/面包心共用）。
                    顶部是牛奶吐司标志性的两个圆鼓肩 + 中间一道浅凹。"""
                    a, b = TW - inset, TH - inset * 0.92
                    pth = QPainterPath()
                    pth.moveTo(-a + 7.0, TCY + b)
                    pth.lineTo(a - 7.0, TCY + b)               # 底边平直
                    pth.quadTo(a, TCY + b, a, TCY + b - 7.0)  # 右下圆角
                    pth.lineTo(a, TCY - 3.0)                  # 右侧
                    # 右肩：一段四分之一圆鼓包下来收到顶中
                    pth.cubicTo(a, TCY - b + 1.6, a * 0.54, TCY - b,
                                2.0, TCY - b + 1.0)
                    pth.quadTo(0.0, TCY - b + 2.2,           # 顶中浅凹
                               -2.0, TCY - b + 1.0)
                    pth.cubicTo(-a * 0.54, TCY - b, -a, TCY - b + 1.6,
                                -a, TCY - 3.0)                # 左肩
                    pth.lineTo(-a, TCY + b - 7.0)
                    pth.quadTo(-a, TCY + b, -a + 7.0, TCY + b)
                    pth.closeSubpath()
                    return pth

                sil = getattr(self, "_toast_sil", None)
                if sil is None:             # 吐司轮廓同样恒定：缓存（见上）
                    sil = toast_path(0.0)       # 烤边壳轮廓
                    self._toast_sil = sil
                    self._toast_mid = toast_path(4.4)   # 面包心轮廓
                mid = self._toast_mid

                # ① 烤边壳：焦黄渐变（上浅下深）
                crg = QLinearGradient(0.0, TCY - TH, 0.0, TCY + TH)
                crg.setColorAt(0.0, QColor("#DCA25C"))
                crg.setColorAt(0.55, QColor("#C4833F"))
                crg.setColorAt(1.0, QColor("#A96C2E"))
                p.setPen(QPen(QColor("#8A5A2B"), 1.8, Qt.SolidLine,
                              Qt.RoundCap, Qt.RoundJoin))
                p.setBrush(crg)
                p.drawPath(sil)

                # ② 面包心：奶白纵向渐变
                p.setPen(Qt.NoPen)
                pgb = QLinearGradient(0.0, TCY - TH, 0.0, TCY + TH)
                pgb.setColorAt(0.0, QColor(251, 235, 201))
                pgb.setColorAt(1.0, QColor(235, 207, 156))
                p.setBrush(pgb)
                p.drawPath(mid)

                # ③ 表面细节：烤痕斑 + 气孔 + 边缘内阴影 + 左上受光
                p.save()
                p.setClipPath(mid)
                for (mx, my, mr, ma) in ((-16.0, -11.0, 9.5, 46),
                                         (13.0, -14.0, 7.5, 38),
                                         (2.0, 5.0, 10.5, 30),
                                         (-7.0, -17.0, 6.0, 34)):
                    rg = QRadialGradient(QPointF(mx, TCY + my), mr)
                    rg.setColorAt(0.0, QColor(198, 143, 78, ma))
                    rg.setColorAt(1.0, QColor(198, 143, 78, 0))
                    p.setPen(Qt.NoPen)
                    p.setBrush(rg)
                    p.drawEllipse(QPointF(mx, TCY + my), mr, mr)
                # 气孔：几个小洞
                p.setPen(Qt.NoPen)
                p.setBrush(QColor(206, 170, 116, 130))
                for (hx, hy, hr) in ((-20.0, 8.0, 1.8), (-7.0, -6.0, 1.4),
                                     (9.0, 12.0, 1.6), (19.0, -2.0, 1.3),
                                     (0.0, 16.0, 1.5)):
                    p.drawEllipse(QPointF(hx, TCY + hy), hr, hr)
                # 边缘内阴影：沿面包心轮廓描一道半透明棕
                p.setBrush(Qt.NoBrush)
                p.setPen(QPen(QColor(146, 98, 46, 95), 3.0, Qt.SolidLine,
                              Qt.RoundCap, Qt.RoundJoin))
                p.drawPath(mid)
                # 左上受光：径向渐变的软斑（实色椭圆会留硬边）
                sheen = QRadialGradient(QPointF(-16, TCY - 14), 26)
                sheen.setColorAt(0.0, QColor(255, 255, 255, 96))
                sheen.setColorAt(1.0, QColor(255, 255, 255, 0))
                p.setPen(Qt.NoPen)
                p.setBrush(sheen)
                p.drawEllipse(QPointF(-16, TCY - 14), 26, 18)
                p.restore()

                # ④ 黄油：方块微微陷进面包，右下淌下一道融化的黄油
                bx, by = -11.0, TCY - 13.0
                bw2, bh2 = 22.0, 15.0
                btb = QLinearGradient(bx, by, bx, by + bh2)
                btb.setColorAt(0.0, QColor(255, 233, 166))
                btb.setColorAt(1.0, QColor(224, 172, 66))
                p.setPen(QPen(QColor("#C9973A"), 1.4, Qt.SolidLine,
                              Qt.RoundCap, Qt.RoundJoin))
                p.setBrush(btb)
                p.drawRoundedRect(QRectF(bx, by, bw2, bh2), 3.0, 3.0)
                p.setPen(Qt.NoPen)
                p.setBrush(QColor(255, 250, 214, 175))
                p.drawRoundedRect(QRectF(bx + 2.6, by + 2.0, bw2 * 0.50, 3.4),
                                  1.6, 1.6)
                drip = QPainterPath()
                drip.moveTo(bx + bw2 * 0.64, by + bh2 - 1.2)
                drip.cubicTo(bx + bw2 * 0.74, by + bh2 + 4.6,
                             bx + bw2 * 0.55, by + bh2 + 7.4,
                             bx + bw2 * 0.63, by + bh2 + 10.6)
                p.setPen(QPen(QColor("#EFC65E"), 3.0, Qt.SolidLine,
                              Qt.RoundCap))
                p.setBrush(Qt.NoBrush)
                p.drawPath(drip)
                # 热气：三缕细汽从吐司顶端往上冒、穿出云层（白色画在白云上
                # 等于没有，所以用带一点暖灰的雾色，并且在云外也能看到）。
                # 云顶在 -52×1.45 ≈ -75，汽得拉到 -108 才穿出云顶冒到外面
                p.setBrush(Qt.NoBrush)
                for k in range(3):
                    ph = t * 1.9 + k * 1.7
                    hx = -15.0 + 15.0 * k
                    a_ = int(118 + 74 * math.sin(ph * 1.3))
                    if a_ <= 6:
                        continue
                    p.setPen(QPen(QColor(180, 160, 140, a_), 2.8,
                                  Qt.SolidLine, Qt.RoundCap))
                    yy = TCY - TH - 2.0 - 1.8 * math.sin(ph * 0.7)
                    st = QPainterPath()
                    st.moveTo(hx, yy)
                    st.cubicTo(hx - 5.2, yy - 9.0, hx + 5.6, yy - 17.0,
                               hx - 1.4, yy - 26.0)
                    st.cubicTo(hx - 5.6, yy - 32.0, hx + 3.0, yy - 36.0,
                               hx + 1.4, yy - 41.0)
                    p.drawPath(st)
                # 闪光：吐司右上肩外一颗四角星（在云里最显眼），明暗闪烁
                tw_ = 0.55 + 0.45 * math.sin(t * 4.6)
                p.setPen(QPen(QColor(255, 198, 92, int(245 * tw_)), 3.4,
                              Qt.SolidLine, Qt.RoundCap))
                p.drawLine(QPointF(46.0 - 6.0 * tw_, -34.0),
                           QPointF(46.0 + 6.0 * tw_, -34.0))
                p.drawLine(QPointF(46.0, -34.0 - 6.0 * tw_),
                           QPointF(46.0, -34.0 + 6.0 * tw_))
                # 左下一颗小星，做出双星
                p.setPen(QPen(QColor(255, 214, 130, int(215 * tw_)), 2.4,
                              Qt.SolidLine, Qt.RoundCap))
                p.drawLine(QPointF(-46.0 - 3.6 * tw_, 20.0),
                           QPointF(-46.0 + 3.6 * tw_, 20.0))
                p.drawLine(QPointF(-46.0, 20.0 - 3.6 * tw_),
                           QPointF(-46.0, 20.0 + 3.6 * tw_))
                p.restore()

    def _draw_sleep_bubble(self, p, f):
        """设定彩蛋「在泡泡里睡觉」：入睡后把自己裹进一颗透明泡泡，
        随呼吸轻轻鼓动，醒来（sleep_amt 回落）时泡泡跟着淡掉。
        立体感按真实肥皂泡的构成来堆：
          ① 泡内极淡水色（上淡下浓）——只有一点点"水感"，不挡表情
          ② 菲涅尔边：三圈同心描边，越贴边越厚越亮（球感全在这里）
          ③ 薄膜彩虹：下侧内缘三段低透明度的洋红/青/橘，模拟干涉色
          ④ 底部穿透光带（宽柔 + 细锐两条）
          ⑤ 左上主高光（渐变软斑）+ 小亮点
          ⑥ 13 颗大小不一的卫星小泡，各有自己的漂移相位，攀壁或浮在泡里
        画在身体组内，所以会一起呼吸/翻转。"""
        sa = clamp(self.sleep_amt.v, 0.0, 1.0)
        if sa < 0.05:
            return
        t, bh = f["t"], f["bh"]
        wob = 1.0 + 0.022 * math.sin(t * 2.1)          # 轻轻鼓动
        # ---- 正圆泡泡：半径取"刚好把角色整个裹住" ----
        # 角色实际轮廓到圆心 (195,201) 最远 174px（左下鱼鳍），取 rc=180 时
        # 四周还各留 6~10px 空气；再加呼吸鼓动 wob(±2.2%) 也不出画布：
        # 左沿 8px、下沿 10px，泡泡整颗正圆、不再被 widget 边框切掉。
        # 画布上下都留了透明区（见 DW, DH, PAD_T），圆心落在角色中轴 y≈201。
        cxc, cyc = 0.0, -bh * 0.50
        rc = 180.0 * wob

        def ring(k):
            """半径 k*rc 的同心圆（描边用）。"""
            r_ = rc * k
            return QRectF(cxc - r_, cyc - r_, 2.0 * r_, 2.0 * r_)

        def arc_band(a0, a1, rad, wmax, steps=30):
            """沿半径 rad 的一段"两头渐细"的弧带（角度按数学正向，y 向上）。
            等宽 RoundCap 描边两头是钝的，放大后像贴了一条胶布；
            用「锥形闭合路径」填充才像泡泡上真正的一道反光。"""
            outer, inner = [], []
            for i in range(steps + 1):
                u = i / steps
                a = math.radians(a0 + (a1 - a0) * u)
                w = wmax * math.sin(math.pi * u) ** 0.85
                ca, sn = math.cos(a), math.sin(a)
                outer.append(QPointF(cxc + (rad + w) * ca,
                                     cyc - (rad + w) * sn))
                inner.append(QPointF(cxc + (rad - w) * ca,
                                     cyc - (rad - w) * sn))
            path = QPainterPath()
            path.moveTo(outer[0])
            for pt in outer[1:]:
                path.lineTo(pt)
            for pt in reversed(inner):
                path.lineTo(pt)
            path.closeSubpath()
            return path

        p.save()
        p.setOpacity(sa)
        p.setPen(Qt.NoPen)
        p.setBrush(Qt.NoBrush)
        # ---- ① 泡内水色：径向渐变中心压到左上角外，越靠右下越"厚" ----
        #      光源侧的膜几乎透明（白），背光侧积成冷蓝，球感来自这层渐变
        g = QRadialGradient(cxc - rc * 0.42, cyc - rc * 0.48, rc * 1.62)
        g.setColorAt(0.00, QColor(255, 255, 255, 0))
        g.setColorAt(0.34, QColor(250, 252, 255, 10))
        g.setColorAt(0.62, QColor(226, 242, 252, 15))
        g.setColorAt(0.84, QColor(186, 220, 242, 30))
        g.setColorAt(0.94, QColor(148, 198, 230, 46))
        g.setColorAt(1.00, QColor(118, 178, 218, 62))
        p.setBrush(g)
        p.drawEllipse(QPointF(cxc, cyc), rc, rc)
        p.setBrush(Qt.NoBrush)
        # 右下内缘再补一圈宽而淡的冷影：膜越贴近轮廓越厚
        p.setPen(QPen(QColor(140, 190, 228, 26), 14.0, Qt.SolidLine,
                      Qt.RoundCap))
        p.drawArc(ring(0.965), 262 * 16, 128 * 16)
        # ---- ② 菲涅尔边：三圈同心描边，薄膜在边缘视线穿过的厚度最大 ----
        for k, w, col in ((0.997, 10.0, QColor(212, 237, 250, 22)),
                          (0.993, 4.4, QColor(240, 251, 255, 52))):
            p.setPen(QPen(col, w))
            p.drawEllipse(ring(k))
        # 最外那道细线分冷暖两段：左上受光近白、右下折射偏蓝
        p.setPen(QPen(QColor(255, 255, 255, 152), 1.5, Qt.SolidLine,
                      Qt.RoundCap))
        p.drawArc(ring(0.988), 26 * 16, 208 * 16)
        p.setPen(QPen(QColor(126, 174, 212, 132), 1.5, Qt.SolidLine,
                      Qt.RoundCap))
        p.drawArc(ring(0.988), 234 * 16, 152 * 16)
        # ---- ③ 薄膜彩虹：只在侧下缘，三段低透明度干涉色 ----
        for a0, span, col, w in ((198, 66, QColor(198, 162, 238, 46), 3.4),
                                 (246, 34, QColor(250, 206, 168, 34), 3.0),
                                 (300, 46, QColor(146, 224, 206, 42), 3.4)):
            p.setPen(QPen(col, w, Qt.SolidLine, Qt.RoundCap))
            p.drawArc(ring(0.972), a0 * 16, span * 16)
        # ---- ④ 底部穿透光带：宽而柔的一条 + 贴着膜的细锐线 ----
        p.setPen(Qt.NoPen)
        p.setBrush(QColor(255, 255, 255, 34))
        p.drawPath(arc_band(208, 292, rc * 0.955, rc * 0.030))
        p.setPen(QPen(QColor(255, 255, 255, 112), 2.2, Qt.SolidLine,
                      Qt.RoundCap))
        p.drawArc(ring(0.982), 216 * 16, 60 * 16)
        # ---- ⑤ 左上主高光：贴着球面的一道弧形反光，两头渐细 ----
        p.setPen(Qt.NoPen)
        p.setBrush(QColor(255, 255, 255, 52))
        p.drawPath(arc_band(96, 154, rc * 0.944, rc * 0.038))
        p.setBrush(QColor(255, 255, 255, 138))
        p.drawPath(arc_band(103, 147, rc * 0.954, rc * 0.021))
        p.setBrush(QColor(255, 255, 255, 214))
        p.drawPath(arc_band(110, 140, rc * 0.961, rc * 0.007))
        # 反光里那粒柔和的镜面点（软心，不描硬边）
        dgx, dgy = cxc - rc * 0.426, cyc - rc * 0.631
        dg = QRadialGradient(dgx, dgy, rc * 0.030)
        dg.setColorAt(0.00, QColor(255, 255, 255, 235))
        dg.setColorAt(0.34, QColor(255, 255, 255, 110))
        dg.setColorAt(1.00, QColor(255, 255, 255, 0))
        p.setBrush(dg)
        p.drawEllipse(QPointF(dgx, dgy), rc * 0.030, rc * 0.030)
        # ---- 右侧短反光弧（对面墙的一次反射） ----
        p.setPen(QPen(QColor(255, 255, 255, 54), 2.6, Qt.SolidLine,
                      Qt.RoundCap))
        p.setBrush(Qt.NoBrush)
        p.drawArc(ring(0.986), 336 * 16, 40 * 16)
        # ---- ⑥ 卫星小泡：极坐标 (角度, 距圆心的 rc 倍, 半径px, 相位, 速度) ----
        #      分布在泡壁附近与泡内，尺寸 2.8~13 三档拉开，各自漂移
        for ang, dist, r, ph, sp in (
                (152, 0.78, 11.2, 0.0, 1.5), (120, 0.90, 6.2, 1.7, 2.0),
                (96, 0.66, 4.2, 3.1, 1.3), (70, 0.86, 8.6, 4.4, 1.8),
                (38, 0.70, 3.6, 5.6, 2.3), (12, 0.90, 6.8, 0.8, 1.6),
                (-16, 0.60, 3.2, 2.4, 2.1), (-48, 0.82, 13.0, 3.7, 1.4),
                (-84, 0.90, 5.4, 5.0, 2.4), (-118, 0.74, 8.0, 1.2, 1.7),
                (-158, 0.86, 4.6, 4.0, 2.2), (-128, 0.46, 2.8, 2.9, 2.6),
                (170, 0.52, 3.4, 5.9, 1.9)):
            a_ = math.radians(ang)
            bx = cxc + rc * (dist * math.cos(a_)
                             + 0.014 * math.sin(t * sp + ph))
            by = cyc + rc * (dist * math.sin(a_)
                             + 0.024 * math.sin(t * sp * 0.72 + ph * 1.7))
            rr = r * (0.92 + 0.08 * math.sin(t * 1.9 + ph))
            srect = QRectF(bx - rr, by - rr, 2.0 * rr, 2.0 * rr)
            # 泡体：中心近透明、贴壁转冷蓝——浅色背景上也读得出是个球
            sg = QRadialGradient(bx - rr * 0.26, by - rr * 0.28, rr * 1.10)
            sg.setColorAt(0.00, QColor(255, 255, 255, 24))
            sg.setColorAt(0.55, QColor(214, 238, 251, 20))
            sg.setColorAt(0.86, QColor(158, 203, 232, 66))
            sg.setColorAt(1.00, QColor(120, 172, 212, 104))
            p.setPen(Qt.NoPen)
            p.setBrush(sg)
            p.drawEllipse(QPointF(bx, by), rr, rr)
            # 膜边：左上白（受光）+ 右下冷蓝（折射），两段拼成一整圈
            p.setBrush(Qt.NoBrush)
            lw = 0.85 + rr * 0.045
            p.setPen(QPen(QColor(255, 255, 255, 205), lw))
            p.drawArc(srect, 96 * 16, 168 * 16)
            p.setPen(QPen(QColor(126, 172, 210, 165), lw))
            p.drawArc(srect, 276 * 16, 168 * 16)
            # 左上高光点
            p.setPen(Qt.NoPen)
            p.setBrush(QColor(255, 255, 255, 218))
            p.drawEllipse(QPointF(bx - rr * 0.34, by - rr * 0.36),
                          rr * 0.28, rr * 0.28)
            if rr >= 5.0:              # 大泡才看得出第二点与底部反光
                p.setBrush(QColor(255, 255, 255, 110))
                p.drawEllipse(QPointF(bx + rr * 0.30, by + rr * 0.32),
                              rr * 0.13, rr * 0.13)
                p.setPen(QPen(QColor(255, 255, 255, 96), 1.1,
                              Qt.SolidLine, Qt.RoundCap))
                p.setBrush(Qt.NoBrush)
                p.drawArc(QRectF(bx - rr * 0.80, by - rr * 0.80,
                                 rr * 1.60, rr * 1.60), 208 * 16, 60 * 16)
        p.restore()

    def _draw_particles(self, p):
        # PREVIEW_MODE 由主模块在启动时重绑定（main() 的 global /
        # 仿真的 E.PREVIEW_MODE），必须在调用时读「定义 EjeePet 的
        # 模块」的现值——脚本直跑时该模块是 __main__，被导入时是
        # ejee_pet，两种情况都取到正确值。
        preview_mode = getattr(sys.modules[type(self).__module__],
                               "PREVIEW_MODE", False)
        for pt in self.particles:
            # 实时运行时橘子汁由 JuiceOverlay 在全局坐标绘制（能飞出窗口、
            # 无范围框），这里跳过，免得再画一份被窗口矩形裁掉的残影。
            # 预览图（--shot）仍走本地绘制，方便截图展示。
            if pt.kind == "juice" and not preview_mode:
                continue
            age = self.t - pt.born
            a = clamp(1.0 - age / pt.life, 0, 1)
            p.save()
            p.translate(pt.x, pt.y)
            p.rotate(pt.rot)
            col = QColor(pt.color)
            col.setAlpha(int(255 * a))
            p.setBrush(col)
            if pt.kind == "confetti":
                p.drawRect(QRectF(-pt.size / 2, -pt.size / 4,
                                  pt.size, pt.size / 2))
            elif pt.kind == "bubble":
                age = self.t - pt.born
                wob = math.sin(age * 5.0 + pt.rot) * 2.5
                r = pt.size * (1.0 + age * 0.06)
                p.setPen(QPen(QColor(232, 245, 252, int(210 * a)), 1.4))
                p.setBrush(QColor(214, 234, 248, int(44 * a)))
                p.drawEllipse(QPointF(wob, 0), r, r)
                p.setPen(Qt.NoPen)
                p.setBrush(QColor(255, 255, 255, int(185 * a)))
                p.drawEllipse(QPointF(wob - r * 0.35, -r * 0.38),
                              r * 0.24, r * 0.24)
            elif pt.kind == "zzz":
                # 矢量 Z 字（上横-斜-下横），越飘越大 + 左右轻摆
                sz = pt.size * (1.0 + age * 0.30)
                wob = math.sin(age * 3.2 + pt.rot) * 2.4
                hw = sz * 0.60
                p.setPen(QPen(QColor(165, 188, 214, int(185 * a)), 2.2,
                              Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
                p.setBrush(Qt.NoBrush)
                p.drawLine(QPointF(wob - hw, -sz * 0.55),
                           QPointF(wob + hw, -sz * 0.55))
                p.drawLine(QPointF(wob + hw, -sz * 0.55),
                           QPointF(wob - hw, sz * 0.55))
                p.drawLine(QPointF(wob - hw, sz * 0.55),
                           QPointF(wob + hw, sz * 0.55))
                p.setPen(Qt.NoPen)
            elif pt.kind == "heart":
                sz = pt.size
                path = QPainterPath()
                path.moveTo(0, sz * 0.35)
                path.cubicTo(-sz, -sz * 0.25, -sz * 0.4, -sz * 0.8, 0, -sz * 0.25)
                path.cubicTo(sz * 0.4, -sz * 0.8, sz, -sz * 0.25, 0, sz * 0.35)
                p.drawPath(path)
            elif pt.kind == "juice":
                # 汁水滴：竖长小椭圆，随 age 略拉长（坠落拉伸）
                stretch = 1.0 + min(0.5, age * 0.8)
                p.drawEllipse(QPointF(0, 0),
                              pt.size * 0.62, pt.size * 0.62 * stretch)
            elif pt.kind == "crumb_dust":
                # 面包碎屑：极小的一粒，落地前略微拉长
                st2 = 1.0 + min(0.4, age * 0.7)
                p.drawEllipse(QPointF(0, 0), pt.size, pt.size * st2)
            elif pt.kind == "stain":
                # 橘子汁水渍：扁圆主体 + 两枚卫星小点，2 秒淡出
                rs = pt.size * 1.7
                p.setPen(Qt.NoPen)
                p.setBrush(QColor(255, 168, 58, int(140 * a)))
                p.drawEllipse(QPointF(0, 0), rs * 1.3, rs * 0.72)
                p.setBrush(QColor(255, 190, 92, int(115 * a)))
                p.drawEllipse(QPointF(rs * 1.15, -rs * 0.45), rs * 0.34, rs * 0.26)
                p.drawEllipse(QPointF(-rs * 1.2, rs * 0.34), rs * 0.26, rs * 0.2)
                p.setBrush(Qt.NoBrush)
            elif pt.kind == "star":
                sz = pt.size
                path = QPainterPath()
                path.moveTo(0, -sz)
                for i in range(1, 10):
                    ang = -math.pi / 2 + i * math.pi / 5
                    rad = sz if i % 2 == 0 else sz * 0.42
                    path.lineTo(rad * math.cos(ang), rad * math.sin(ang))
                path.closeSubpath()
                p.drawPath(path)
            else:  # steam
                gr = 1.0 + age * 0.9
                col.setAlpha(int(150 * a))
                p.setBrush(col)
                p.drawEllipse(QPointF(0, 0), pt.size * gr, pt.size * gr)
            p.restore()

    def _draw_shadow(self, p, pose):
        """动态投影（画在身体组之下）：随离地高度（弹跳/浮动/拖拽）变大、
        变淡、下移；落地挤压（_sq>0）时变宽变实。与 _sq 弹簧同帧读取，
        所以和身体的形变天然同步。"""
        bob, bounce = pose["bob"], pose["bounce"]
        lift = clamp((-bounce - max(0.0, -bob)) / 14.0, 0.0, 1.6)
        if self._dragging:
            lift = max(lift, 0.6)
        sq_g = clamp(self._sq.v, -0.22, 0.22)
        gr = 46.0 * (1.0 + 0.16 * lift + 0.10 * sq_g)
        ga = int(clamp(76.0 - 34.0 * lift + 26.0 * sq_g, 22.0, 96.0))
        gdy = 11.0 + 8.0 * lift
        p.setBrush(QColor(70, 40, 18, ga))
        p.drawEllipse(QPointF(self.BCX, self.BCY + gdy), gr, gr * 0.24)

    def _apply_body_pose(self, p, pose, f):
        """把身体组的平移 / 旋转 / 挤压拉伸 / 朝向镜像写进 painter。"""
        p.translate(self.BCX + pose["shake_x"],
                    self.BCY + pose["bob"] + pose["bounce"] + pose["shake_y"]
                    + f["ha"] * (3.4 - 2.4 * self._hover_amt.v)
                    + pose["sigh"] * 2.6)
        p.rotate(pose["sway"] + pose["lean"] + self._tilt.v
                 + self._turn.v * self.facing)   # 转弯倾斜（乘 facing 抵消镜像）
        # 挤压拉伸（Squash & Stretch）：squash 弹簧 + 拖拽速度拉伸，
        # 体积守恒（sx 增大部分由 sy 减小补偿）
        dst = clamp(abs(self._dvx) / 3200.0, 0.0, 0.16)
        sq = clamp(self._sq.v, -0.22, 0.22)
        br = pose["breathe"]
        st = clamp(self._stuffed.v, 0.0, 1.0)     # 吃撑：肚子横向鼓起来
        # 傲娇躲避：不再做身体形变（改为直接闪现到别处），保持原比例
        shyk = 1.0
        # 饿软了：以脚底（BCY，身体组原点）为支点纵向压扁，头顶往下塌
        # ~34px，整只像一滩橘子水贴在地上；同时全身微微内收——轮廓自己
        # 就瘪下去，比画阴影靠谱（暗斑在橙色圆脸上只会像脏）。叹气再补一点。
        sag = 1.0 - 0.150 * f["ha"] - 0.055 * pose["sigh"]
        p.scale((1.0 + 0.008 * br + sq + dst) * (1.0 + 0.055 * st) * shyk
                * (1.0 - 0.028 * f["ha"] + 0.012 * pose["sigh"]),
                (1.0 + 0.015 * br - sq - dst * 0.7) * (1.0 + 0.012 * st) * sag)
        # 朝向镜像：以身体竖直中轴翻转（眼/嘴/眉/尾巴全体自动跟随，
        # 气泡/倒计时牌/粒子在组外不受影响）
        if self.facing == -1:
            p.scale(-1.0, 1.0)

    def _draw_body(self, p, f):
        """底图（尾巴区域留空，随后用形变条带补上）+ 尾巴轻摆。"""
        bw, bh = f["bw"], f["bh"]
        # 底图：缩略图走缓存，避免每帧从 1548×1236 的原图重采样。
        # 目标矩形按缓存图的实际像素反算，保证 1:1 贴图
        bpm = self._cache_pm("base", self.base_pm, self._dev_px(bw))
        k = self._design_per_px()
        p.drawPixmap(QRectF(-bpm.width() * k / 2.0, -bh,
                            bpm.width() * k, bpm.height() * k), bpm,
                     QRectF(0, 0, bpm.width(), bpm.height()))

        # ---- 头顶叶子：单独一层，平时直立；饿了只枯萎、不耷拉（见 _draw_leaf）----
        self._draw_leaf(p, f)

        # ---- 尾巴轻摆：4 条水平条带，位移顶部 0（与融合区无缝衔接）
        #      -> 底部最大；幅度受慢波调制产生不规律感，随情绪微调 ----
        ta = self._tail_amp()
        # 恶作剧：尾巴尖甩向鼠标一侧（sw 横向）+ 向上翘起（lift 竖向）
        sw = 15.0 * self._mis_tail.v * self._mis_dir
        lift = max(0.0, self._mis_tail.v) * 13.0
        if ta > 0.1 or abs(sw) > 0.6:
            tx0, ty0, tx1, ty1 = self.tail_geo
            fx = -bw / 2 + tx0 * self.s
            fy = -bh + ty0 * self.s
            tw = (tx1 - tx0) * self.s
            th = (ty1 - ty0) * self.s
            tpm = self._cache_pm("tail", self.tail_pm, self._dev_px(tw))
            pw, ph = float(tpm.width()), float(tpm.height())
            p.save()
            p.setClipRect(QRectF(fx - 4.0, fy - 4.0, tw + 8.0, th + 8.0))
            n = 4
            for i in range(n):
                w = (i / (n - 1)) ** 1.2
                dx = ta * w * math.sin(self._tail_ph + i * 0.55) + sw * w
                dy = -lift * w
                p.drawPixmap(
                    QRectF(fx + dx, fy + th * i / n + dy, tw, th / n),
                    tpm,
                    QRectF(0.0, ph * i / n, pw, ph / n))
            p.restore()

    def _draw_leaf(self, p, f):
        """头顶那片叶子：只枯萎，不耷拉。

        平时（ha=0）就是原素材的直立姿态；越饿只做两件事：沿叶脉方向
        缩短一点点（萎软），颜色从嫩绿叠到土黄（leaf.png 与 leaf_dry.png
        按 ha 叠加），读作“蔫了/枯萎”。不再绕叶柄旋转倒向一侧。"""
        ha = f["ha"]
        lx, ly, lw, lh, ax, ay = LEAF_GEO
        rect = QRectF(lx - self.BCX, ly - self.BCY, lw, lh)
        axr, ayr = ax - self.BCX, ay - self.BCY
        # 不旋转（用户：不要耷拉，只枯萎）；以叶柄根部为支点纵向缩短
        p.save()
        p.setOpacity(1.0 - 0.18 * ha)
        p.translate(axr, ayr)
        p.scale(1.0, 1.0 - 0.07 * ha)        # 萎软：沿叶脉方向缩短
        p.translate(-axr, -ayr)
        lp = self._cache_pm("leaf", self.leaf_pm, self._dev_px(lw))
        p.drawPixmap(rect, lp, QRectF(lp.rect()))
        if ha > 0.02:                        # 枯色叠层：嫩绿 -> 土黄
            dp = self._cache_pm("leaf_dry", self.leaf_dry_pm, self._dev_px(lw))
            p.setOpacity(ha * 0.92)
            p.drawPixmap(rect, dp, QRectF(dp.rect()))
        p.restore()

    def _draw_foreground(self, p, f):
        """组外特效（不受身体翻转/位移影响）：面包、乌云、感叹号、
        飘字、粒子、对话气泡、倒计时牌与饱食度牌。"""
        t, c = f["t"], f["c"]
        self._draw_bread(p)
        if c["cloud"] > 0.03:
            self._draw_cloud(p, c["cloud"])
        if c["excl"] > 0.03:
            self._draw_excl(p, c["excl"], t)
        self._draw_floats(p)
        self._draw_particles(p)
        self._draw_bubble(p)
        self._draw_pomo_tag(p)
        self._draw_hunger_tag(p)

    def _draw_hunger_tag(self, p):
        """饱食度牌：左上侧小深棕牌（面包图标 + 进度条 + 数值）。
        >50 橙 / 30-50 黄 / <30 红，随饥饿程度变色。
        气泡压到牌（_draw_bubble 置 _tag_hidden）时优先台词：
        牌在气泡出生后 0.25s 内淡到 0，气泡收了再回来。"""
        hg = self._meta.get("hunger", 80.0)
        alpha = 1.0
        if getattr(self, "_tag_hidden", False):
            alpha = 1.0 - clamp((self.t - self.bubble_t0) / 0.25, 0.0, 1.0)
            if alpha <= 0.01:
                return
        p.save()
        p.setOpacity(alpha)
        p.setPen(Qt.NoPen)
        p.setBrush(QColor(58, 39, 30, 228))
        p.drawRoundedRect(QRectF(6, 16, 96, 32), 10, 10)
        # 小面包图标
        p.setBrush(QColor(238, 186, 120))
        p.drawEllipse(QPointF(19, 33), 8.0, 6.2)
        p.setBrush(QColor(214, 160, 96))
        p.drawEllipse(QPointF(19, 30), 4.2, 2.2)
        # 进度条
        bx, bw_, bh_ = 32, 44, 8
        p.setBrush(QColor(30, 20, 14, 200))
        p.drawRoundedRect(QRectF(bx, 28, bw_, bh_), 4, 4)
        frac = clamp(hg / 100.0, 0.0, 1.0)
        if hg > 50:
            col = QColor(248, 166, 60)
        elif hg > 30:
            col = QColor(246, 210, 80)
        else:
            col = QColor(240, 100, 80)
        p.setBrush(col)
        if frac > 0.02:
            p.drawRoundedRect(QRectF(bx, 28, max(6.0, bw_ * frac), bh_), 4, 4)
        # 数值
        f = QFont()
        f.setPixelSize(13)
        f.setBold(True)
        p.setFont(f)
        p.setPen(QPen(QColor(252, 250, 244)))
        p.drawText(QRectF(bx + bw_ + 2, 16, 24, 32), Qt.AlignCenter,
                   str(int(hg)))
        p.restore()

    def _draw_pomo_tag(self, p):
        """番茄钟倒计时牌：悬在桌宠右上角的小牌子。
        左侧是进度圈（小番茄外圈按已完成比例顺时针填满），最后一分钟
        牌底渐变成暖红、秒数开始闪，配合桌宠的紧张表情。"""
        if self._pomo_end is None:
            return
        rem = max(0.0, self._pomo_end - self.t)
        total = max(60.0, float(self._pomo_total))
        frac = clamp(1.0 - rem / total, 0.0, 1.0)
        nrv = clamp(self._pomo_nrv.v, 0.0, 1.0)
        box = QRectF(DW - 108, 13 + clamp(self._tag_dy.v, 0.0, 46.0), 102, 34)
        cx, cy = box.left() + 16.0, box.center().y()
        p.save()
        p.setPen(Qt.NoPen)
        # 牌底：深棕 → 暖红（最后一分钟）
        c0, c1 = QColor(58, 39, 30, 228), QColor(158, 56, 38, 238)
        p.setBrush(QColor(int(c0.red() + (c1.red() - c0.red()) * nrv),
                          int(c0.green() + (c1.green() - c0.green()) * nrv),
                          int(c0.blue() + (c1.blue() - c0.blue()) * nrv),
                          int(c0.alpha() + (c1.alpha() - c0.alpha()) * nrv)))
        p.drawRoundedRect(box, 11, 11)
        # 进度圈：底环 + 已完成弧（从 12 点顺时针走）
        p.setBrush(Qt.NoBrush)
        p.setPen(QPen(QColor(255, 255, 255, 52), 2.4))
        p.drawEllipse(QPointF(cx, cy), 9.6, 9.6)
        if frac > 0.003:
            p.setPen(QPen(QColor(255, 206, 142) if nrv > 0.5
                          else QColor(246, 176, 92), 2.6, Qt.SolidLine,
                          Qt.RoundCap))
            p.drawArc(QRectF(cx - 9.6, cy - 9.6, 19.2, 19.2),
                      90 * 16, int(-360 * 16 * frac))
        # 小番茄
        p.setPen(Qt.NoPen)
        p.setBrush(QColor(240, 90, 62) if nrv < 0.5 else QColor(255, 122, 96))
        p.drawEllipse(QPointF(cx, cy), 5.4, 5.4)
        p.setBrush(QColor(120, 200, 110))
        p.drawEllipse(QPointF(cx, cy - 5.6), 2.2, 1.5)
        # 剩余时间：最后 10 秒开始闪
        f = QFont()
        f.setPixelSize(17)
        f.setBold(True)
        p.setFont(f)
        blink = 1.0 if rem > 10.0 else 0.55 + 0.45 * abs(math.sin(self.t * 6.0))
        p.setPen(QPen(QColor(252, 250, 244, int(255 * blink))))
        mm, ss = int(rem // 60), int(rem % 60)
        p.drawText(QRectF(box.left() + 28, box.top(), 70, box.height()),
                   Qt.AlignCenter, f"{mm:02d}:{ss:02d}")
        p.restore()

    def _omega_cavity(self, mcx, mcy, mw, mh, s2, dep, span=0.30):
        """居中圆袋形张口腔（官方张嘴表情）。返回 (outer, inner, yb)：
        outer —— 描边色外层袋：上缘沿 ω 下轮廓折线（tuck 2.0 藏精灵笔画
                下），左右锚点内收使其从 ω 端头正下方垂下——折线本身取自
                ω 下缘，几何上不可能超出 ω 轮廓；
        inner —— 腔色内层袋：相对外层整体内缩半笔宽，两层之间形成一条
                等宽连续描边带。全路径填充、无 stroke、无端点 cap——
                只有一条外描边，内部无任何线条；
        yb —— 内层袋底（渐变与舌头的基准）。"""
        half_b = mw * span / s2        # omega_bot 的 dx 是 base 像素
        pts = [(mcx + dx * s2, mcy + dy * s2 - 2.0)
               for dx, dy in self.omega_bot if abs(dx) <= half_b]
        half_sw = OMEGA_SW * s2 * 0.5

        def _trim(seq, inset):
            lo, hi = seq[0][0] + inset, seq[-1][0] - inset
            i = next(k for k, pt in enumerate(seq) if pt[0] >= lo)
            j = max(k for k, pt in enumerate(seq) if pt[0] <= hi)
            return seq[i:j + 1]

        cor_o = _trim(pts, half_sw * 0.6)
        cor_i = _trim(cor_o, half_sw)
        xo0, yo0 = cor_o[0]
        xo1, yo1 = cor_o[-1]
        xi0, yi0 = cor_i[0]
        xi1, yi1 = cor_i[-1]
        ymid = mcy + max(dy for dx, dy in self.omega_bot
                         if abs(dx) <= half_b * 0.5) * s2
        yb = ymid + dep                    # 外层袋底
        ybi = yb - half_sw                 # 内层袋底（描边带半宽）
        outer = QPainterPath()
        outer.moveTo(xo0, yo0)
        for pt in cor_o[1:]:
            outer.lineTo(pt[0], pt[1])
        # 侧壁先竖直下沉再弯向中心（控制点不越锚点外侧），C2 压底成宽圆底
        outer.cubicTo(QPointF(xo1 + 0.5, yo1 + dep * 0.60),
                      QPointF(mcx + mw * 0.18, yb - dep * 0.06),
                      QPointF(mcx, yb))
        outer.cubicTo(QPointF(mcx - mw * 0.18, yb - dep * 0.06),
                      QPointF(xo0 - 0.5, yo0 + dep * 0.60),
                      QPointF(xo0, yo0))
        inner = QPainterPath()
        inner.moveTo(xi0, yi0)
        for pt in cor_i[1:]:
            inner.lineTo(pt[0], pt[1])
        inner.cubicTo(QPointF(xi1 + 0.5, yi1 + dep * 0.55),
                      QPointF(mcx + mw * 0.155, ybi - dep * 0.06),
                      QPointF(mcx, ybi))
        inner.cubicTo(QPointF(mcx - mw * 0.155, ybi - dep * 0.06),
                      QPointF(xi0 - 0.5, yi0 + dep * 0.55),
                      QPointF(xi0, yi0))
        return outer, inner, ybi

    def _teardrop(self, p, cx, cy, w, h):
        """泪滴：尖顶圆底。"""
        path = QPainterPath()
        path.moveTo(cx, cy - h * 0.55)
        path.cubicTo(cx + w * 0.55, cy - h * 0.05,
                     cx + w * 0.50, cy + h * 0.30, cx, cy + h * 0.5)
        path.cubicTo(cx - w * 0.50, cy + h * 0.30,
                     cx - w * 0.55, cy - h * 0.05, cx, cy - h * 0.55)
        p.drawPath(path)

    def _draw_bread(self, p):
        """飞入口中的面包：走一条二次贝塞尔，起点是「这次面包从哪来」——
        拖拽投喂 = 松手处的设计坐标（从那儿飞进嘴）；单击喂食用默认的
        身前位置。末段随进度缩小，钻进口腔。"""
        if self.phase != "bread":
            return
        d = self.t - self.phase_t0
        k = clamp(d / 0.55, 0, 1)
        fade = clamp((1.0 - k) / 0.28, 0.0, 1.0)   # 末段缩小进嘴
        if fade <= 0.02:
            return
        mcx, mcy = self.mouth_center
        ex, ey = mcx + 2, mcy + 13                    # 覆盖 ω 下开口
        if self._feed_from is not None:
            sx, sy0 = self._feed_from                # 拖拽：从松手点飞来
        else:
            sx, sy0 = 358.0, 322.0
        # 控制点：从起点向上/向外挑一道弧，飞进来才有"被送过去"的感觉
        mx = (sx + ex) / 2.0
        my = min(sy0, ey) - 26.0
        u = 1 - k
        x = u * u * sx + 2 * u * k * mx + k * k * ex
        y = u * u * sy0 + 2 * u * k * my + k * k * ey
        p.save()
        p.translate(x, y)
        p.rotate(-16 * math.sin(math.pi * k) * (1 if sx > ex else -1))
        p.scale((0.55 + 0.45 * k) * fade, (0.55 + 0.45 * k) * fade)
        p.setBrush(QColor("#E2A75F"))
        p.drawRoundedRect(QRectF(-24, -14, 48, 28), 13, 13)
        p.setBrush(QColor("#F2CF94"))
        p.drawRoundedRect(QRectF(-24, -14, 48, 18), 12, 12)
        p.setBrush(QColor(255, 255, 255, 130))
        p.drawEllipse(QPointF(-8, -5), 6, 3)
        p.restore()

    def _draw_cloud(self, p, intensity):
        """生气头顶的小乌云 + 雨丝，随 intensity 弹入。"""
        cx, cy = self.BCX - 72, self.head_top - 2
        s = clamp(intensity, 0, 1)
        p.save()
        p.translate(cx, cy)
        p.scale(0.5 + 0.5 * s, 0.5 + 0.5 * s)
        col = QColor(CLOUD)
        col.setAlpha(int(215 * s))
        p.setBrush(col)
        p.drawEllipse(QPointF(-16, 0), 17, 12)
        p.drawEllipse(QPointF(2, -7), 14, 11)
        p.drawEllipse(QPointF(16, 2), 12, 9)
        p.setPen(QPen(QColor(120, 140, 160, int(180 * s)), 2,
                      Qt.SolidLine, Qt.RoundCap))
        for i, dx in enumerate((-14, 0, 13)):
            off = (self.t * 60 + i * 8) % 18
            p.drawLine(QPointF(dx, 12 + off), QPointF(dx, 16 + off))
        p.setPen(Qt.NoPen)
        p.restore()

    def _draw_excl(self, p, intensity, t):
        """惊讶头顶的感叹号，弹跳入场。"""
        s = clamp(intensity, 0, 1)
        pop = 1.0 + 0.25 * math.sin(min(1.0, (t - self.state_t0) * 6) * math.pi)
        cx, cy = self.BCX + 62, self.head_top - 6
        p.save()
        p.translate(cx, cy - 10 * (1 - s))
        p.scale(s * pop, s * pop)
        p.setBrush(ACCENT)
        p.drawRoundedRect(QRectF(-4, -26, 8, 20), 4, 4)
        p.drawEllipse(QPointF(0, 1), 4.2, 4.2)
        p.restore()

    def _bubble_theme(self):
        """本条气泡的皮肤：状态优先（傲娇粉 / 果汁橙 / 晕车浅绿 / 生气橙红…），
        再按 bubble_style 回落。屏幕上有面包渣且没有更激烈的状态时，换成
        可怜蓝（配一滴将落未落的眼泪）。"""
        if self._crumbs and self.state in ("idle", "happy"):
            return BUBBLE_THEMES["crumb"]
        name = STATE_BUBBLE_THEME.get(self.state) or self.bubble_style
        return BUBBLE_THEMES.get(name, BUBBLE_THEMES["cloud"])

    @staticmethod
    def _bubble_font(th):
        """主题对应的字体：圆润体（幼圆）默认，生气用加粗硬体。"""
        f = QFont()
        f.setFamilies(list(FONT_PUNCH if th["font"] == "punch"
                           else FONT_ROUND))
        f.setPixelSize(th["size"])
        f.setBold(th["font"] == "punch")
        return f

    @staticmethod
    def _heart_path(cx, cy, r):
        """小爱心路径（r≈半宽）。"""
        path = QPainterPath()
        path.moveTo(cx, cy + r * 0.85)
        path.cubicTo(cx - r * 1.55, cy + r * 0.05,
                     cx - r * 0.72, cy - r * 1.05, cx, cy - r * 0.32)
        path.cubicTo(cx + r * 0.72, cy - r * 1.05,
                     cx + r * 1.55, cy + r * 0.05, cx, cy + r * 0.85)
        path.closeSubpath()
        return path

    def _bubble_deco(self, p, deco, bx, y_b, w, h):
        """气泡挂饰：傲娇爱心 / 恶作剧汁滴 / 可怜泪滴。"""

        def _drop(cx_, cy_, r_, edge, fill):
            """一滴将落未落的水珠（尖顶圆底）。"""
            path = QPainterPath()
            path.moveTo(cx_, cy_ + r_ * 1.55)
            path.quadTo(cx_ - r_ * 1.02, cy_ + r_ * 0.28, cx_, cy_ - r_ * 0.72)
            path.quadTo(cx_ + r_ * 1.02, cy_ + r_ * 0.28, cx_, cy_ + r_ * 1.55)
            path.closeSubpath()
            p.setPen(QPen(edge, 1.4))
            p.setBrush(fill)
            p.drawPath(path)
            p.setPen(Qt.NoPen)
            p.setBrush(QColor(255, 255, 255, 150))
            p.drawEllipse(QPointF(cx_ - r_ * 0.26, cy_ + r_ * 0.10),
                          r_ * 0.20, r_ * 0.14)

        if deco == "heart":      # 傲娇：右上两颗蹦跶的小爱心
            heart = QColor("#F27D9B")
            heart.setAlpha(235)
            for fx, fy, r_, ph in ((0.86, 0.0, 4.6, 0.0),
                                   (0.97, 0.14, 3.4, 1.7)):
                cx_ = bx + w * fx
                cy_ = (y_b - h * 0.72 + fy * 8
                       + math.sin(self.t * 4.0 + ph) * 1.8)
                p.setPen(Qt.NoPen)
                p.setBrush(heart)
                p.drawPath(self._heart_path(cx_, cy_, r_))
        elif deco == "juice":    # 恶作剧：底缘挂一滴汁 + 右上两颗飞溅小汁滴
            drip = QColor("#FBD9A8")
            drip.setAlpha(240)
            _drop(bx + w * 0.5 - 14, y_b - 2 + math.sin(self.t * 2.4 + 1.0)
                  * 1.4, 4.4, QColor("#E8834A"), drip)
            splash = QColor("#F7B36A")
            splash.setAlpha(235)
            for fx, fy, r_, ph in ((0.88, 0.02, 2.6, 0.6),
                                   (0.97, 0.18, 2.0, 2.4)):
                cx_ = (bx + w * fx + math.sin(self.t * 3.1 + ph) * 1.2)
                cy_ = (y_b - h + h * fy - 4
                       + math.cos(self.t * 2.6 + ph) * 1.6)
                p.setPen(Qt.NoPen)
                p.setBrush(splash)
                p.drawEllipse(QPointF(cx_, cy_), r_, r_ * 1.15)
        elif deco == "tear":     # 可怜：底缘挂一滴眼泪（轻轻晃）
            tear = QColor("#C6E0F4")
            tear.setAlpha(240)
            _drop(bx + w * 0.5 + 16, y_b - 2 + math.sin(self.t * 3.0) * 1.6,
                  4.0, QColor("#7FA6CC"), tear)

    def _draw_floats(self, p):
        """飘字（吃撑时的「嗝～」等）：暖棕加粗 + 白描边，
        压在橙色身体上也看得清。字体与气泡同一套圆润体，形象统一。"""
        f = QFont()
        f.setFamilies(list(FONT_ROUND))
        f.setPixelSize(21)
        f.setBold(True)
        p.setFont(f)
        for (txt, x, y, born) in self.floats:
            d = self.t - born
            a = clamp(1.0 - d / 1.2, 0, 1)
            path = QPainterPath()
            path.addText(QPointF(x, y - 26 * d), f, txt)
            p.setPen(QPen(QColor(255, 252, 245, int(215 * a)), 4.5,
                          Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
            p.setBrush(Qt.NoBrush)
            p.drawPath(path)                    # 先描白边
            p.setPen(Qt.NoPen)
            p.setBrush(QColor(146, 74, 28, int(255 * a)))
            p.drawPath(path)                    # 再填暖棕
        p.setPen(Qt.NoPen)

    @staticmethod
    def _wavy_edge(path, ax, ay, bx_, by_, n, amp, phase=0.0):
        """沿 a->b 画 n 段圆滑波浪（每段中点沿外法向偏移 amp）。

        用于生气框：平滑起伏的边比一圈三角尖刺自然得多（尖刺像太阳，
        和 Q 版画风不搭）。amp 正为正向外鼓、负为向内凹，相邻段交替。
        """
        dx, dy = bx_ - ax, by_ - ay
        ln = math.hypot(dx, dy) or 1.0
        nx, ny = dy / ln, -dx / ln       # 顺时针遍历时的外法向
        for i in range(n):
            t1 = (i + 1) / n
            tm = (i + 0.5) / n
            m = amp * math.sin(math.pi * (i + 0.5) + phase)
            path.quadTo(QPointF(ax + dx * tm + nx * m,
                                ay + dy * tm + ny * m),
                        QPointF(ax + dx * t1, ay + dy * t1))

    def _bubble_blob_path(self, bx, y_b, w, h, r=15.0):
        """手绘感的对话泡：圆角矩形，四条边带极轻的起伏（上边微鼓、
        右边略饱、下边微垂）。不再是"圆角方块 + 顶缘三颗固定小圆凸"
        那种机械拼装，像随手勾出来的一朵气泡。"""
        x0, y0 = bx, y_b - h
        x1, y1 = bx + w, y_b
        mx, my = (x0 + x1) / 2.0, (y0 + y1) / 2.0
        path = QPainterPath()
        path.moveTo(x0 + r, y0)
        path.quadTo(mx, y0 - 2.8, x1 - r, y0)              # 上边轻上鼓
        path.quadTo(x1, y0, x1, y0 + r)                    # 右上圆角
        path.quadTo(x1 + 2.0, my, x1, y1 - r)              # 右边略饱
        path.quadTo(x1, y1, x1 - r, y1)                    # 右下圆角
        path.quadTo(mx, y1 + 1.5, x0 + r, y1)              # 下边微垂
        path.quadTo(x0, y1, x0, y1 - r)                    # 左下圆角
        path.quadTo(x0 - 1.8, my, x0, y0 + r)              # 左边略饱
        path.quadTo(x0, y0, x0 + r, y0)                    # 左上圆角
        path.closeSubpath()
        return path

    def _bubble_cloud_path(self, bx, y_b, w, h):
        """云朵框：手绘感主体 + 指向头顶的小弯尾。"""
        return self._bubble_blob_path(bx, y_b, w, h)

    def _bubble_burst_path(self, bx, y_b, w, h):
        """生气框：边线起伏的"气鼓起来"的气泡。四边平滑波浪 + 圆角，
        不再用一圈锐利三角尖刺（像太阳，太硬）。"""
        x0, y0 = bx, y_b - h
        x1, y1 = bx + w, y_b
        r = 12.0
        amp = 3.2
        path = QPainterPath()
        path.moveTo(x0 + r, y0)
        self._wavy_edge(path, x0 + r, y0, x1 - r, y0, 4, amp, 0.0)
        path.quadTo(x1, y0, x1, y0 + r)
        self._wavy_edge(path, x1, y0 + r, x1, y1 - r, 3, amp, 1.1)
        path.quadTo(x1, y1, x1 - r, y1)
        self._wavy_edge(path, x1 - r, y1, x0 + r, y1, 4, amp, 0.7)
        path.quadTo(x0, y1, x0, y1 - r)
        self._wavy_edge(path, x0, y1 - r, x0, y0 + r, 3, amp, 1.9)
        path.quadTo(x0, y0, x0 + r, y0)
        path.closeSubpath()
        return path

    def _bubble_round_path(self, bx, y_b, w, h):
        """圆形泡泡框：主体是一个大圆（外加两枚小气泡点缀），没有尖尾巴。"""
        r = max(h / 2.0 + 8.0, w / 2.0 + 8.0)
        cx = bx + w / 2.0
        cy = y_b - h / 2.0
        path = QPainterPath()
        path.addEllipse(QPointF(cx, cy), r, r)
        # 两枚缀在边上小气泡，像刚吐出来的
        for ang, rr in ((math.pi * 0.86, 5.4), (math.pi * 0.14, 3.8)):
            path.addEllipse(QPointF(cx + math.cos(ang) * r * 1.02,
                                    cy + math.sin(ang) * r * 1.02), rr, rr)
        return path

    # ---- 打字机气泡参数：14 字/秒，前 0.12s 停顿；≤6 字短句整句弹出 ----
    TYPE_CPS = 14.0
    TYPE_DELAY = 0.12
    TYPE_MIN = 6

    def _bubble_shown_text(self):
        """打字机当前应显示的文本前缀：台词逐字冒出，像"在说话"而不是
        "贴出一张纸"。预览模式返回全量（回归需与显示时机无关的确定性），
        短句不吃打字机（"咕噜咕噜～"这类一口气说完更自然）。"""
        txt = self.bubble_text
        if not txt or len(txt) <= self.TYPE_MIN:
            return txt
        if getattr(sys.modules[type(self).__module__], "PREVIEW_MODE", False):
            return txt
        n = int((self.t - self.bubble_t0 - self.TYPE_DELAY) * self.TYPE_CPS)
        if n >= len(txt):
            return txt
        return txt[:max(0, n)]

    def _draw_bubble(self, p):
        """对话气泡：框型 + 皮肤随情绪切换（主题表见 BUBBLE_THEMES）。
          cloud 奶油云泡泡（日常） / burst 带刺爆炸（生气） / round 圆泡泡（打嗝）
          / zzz  睡泡泡里的 Zzz（睡眠）
        另有状态皮肤：傲娇粉+爱心 · 果汁橙+汁滴 · 晕车浅绿+摇摆 · 可怜蓝+泪滴。
        统一：幼圆字体（生气用加粗硬体）、上亮下沉渐变、左上高光、
        easeOutBack 弹性放大淡入 + 淡出，文字自适应换行。"""
        if not self.bubble_text or self.t > self.bubble_until:
            self._tag_hidden = False      # 没气泡：饱食度牌照常显示
            return
        style = self.bubble_style
        th = self._bubble_theme()
        f = self._bubble_font(th)

        # ---- 睡眠：三只 Z 坐在小泡泡里向右上方飘开（像真的在打呼）----
        if style == "zzz":
            age = self.t - self.bubble_t0
            IN, OUT = 0.30, 0.5
            k = clamp(age / IN, 0.0, 1.0)
            sc = 0.7 + 0.3 * k
            a = k
            left = self.bubble_until - self.t
            if left < OUT:
                a *= max(0.0, left / OUT)
            if a <= 0.01:
                return
            p.save()
            p.setOpacity(a)
            base_x = self.BCX + 34
            base_y = self.head_top + 6
            for i, (dxx, dyy, sc2, al) in enumerate(((0, 0, 1.00, 1.00),
                                                     (11, -9, 0.76, 0.82),
                                                     (20, -17, 0.58, 0.60))):
                cx_, cy_ = base_x + dxx, base_y + dyy
                p.save()
                p.translate(cx_, cy_)
                p.rotate(-8)
                p.scale(sc * sc2, sc * sc2)
                p.translate(-cx_, -cy_)
                p.setOpacity(a * al)
                # 小睡泡泡：半透明水色圆 + 细边 + 左上亮点，Z 坐在里面
                r_ = 11.5
                p.setPen(QPen(QColor(th["edge"]), 1.6))
                p.setBrush(QColor(232, 243, 252, 205))
                p.drawEllipse(QPointF(cx_, cy_ - 1.5), r_, r_)
                p.setPen(Qt.NoPen)
                p.setBrush(QColor(255, 255, 255, 170))
                p.drawEllipse(QPointF(cx_ - r_ * 0.34, cy_ - 1.5 - r_ * 0.42),
                              r_ * 0.20, r_ * 0.14)
                zz = QPainterPath()
                zz.addText(QPointF(cx_, cy_ + 4.8), f, "z")
                p.setPen(QPen(QColor(255, 255, 255, 200), 3.2, Qt.SolidLine,
                              Qt.RoundCap, Qt.RoundJoin))
                p.setBrush(Qt.NoBrush)
                p.drawPath(zz)
                p.setPen(Qt.NoPen)
                p.setBrush(QColor(112, 142, 186, int(235 * al)))
                p.drawPath(zz)
                p.restore()
            p.restore()
            return

        age = self.t - self.bubble_t0
        IN, OUT = 0.30, 0.35            # 入场/退场动画时长
        k = clamp(age / IN, 0.0, 1.0)
        # easeOutBack：带轻微过冲的弹出曲线
        e = 1.0 + 2.70 * (k - 1.0) ** 3 + 1.70 * (k - 1.0) ** 2
        sc = 0.62 + 0.38 * e
        a = k
        left = self.bubble_until - self.t
        if left < OUT:
            a *= max(0.0, left / OUT)
        if a <= 0.01:
            return

        # 文字自适应：超宽自动换行（中文逐字断行）
        p.setFont(f)
        fm = p.fontMetrics()
        trect = fm.boundingRect(0, 0, 200, 500,
                                Qt.TextWordWrap, self.bubble_text)
        w = max(96.0, trect.width() + 44.0)
        h = max(38.0, trect.height() + 26.0)
        if style == "round":
            # 圆形泡泡：正文改为竖排不换行的窄条（泡泡框本身就窄）
            w = max(72.0, min(w, 150.0))
        # 陪伴档案徽章行：气泡底部多留一行高度（绘制在文字下方）
        badges = getattr(self, "bubble_badges", None)
        if badges:
            h += 26.0
        y_b = 64.0                                   # 气泡底边（尾巴根）
        bx = clamp(self.BCX - w / 2.0, 10.0, DW - 10.0 - w)
        # 饱食度牌 (6,16,96,32) 与气泡的水平投影相交时整块让位——
        # 台词优先（牌在 _draw_hunger_tag 里按气泡出生后 0.25s 淡出）
        self._tag_hidden = bool(
            bx < 102.0 and bx + w > 6.0
            and (y_b - h - 8.0) < 48.0 and (y_b + 15.0) > 16.0)

        # 框型（配色全部来自主题）
        if style == "burst":
            shape = self._bubble_burst_path(bx, y_b, w, h)
            tail_anchor = True              # 爆炸框也带一根指向头顶的小尾
        elif style == "round":
            shape = self._bubble_round_path(bx, y_b, w, h)
            tail_anchor = False             # 圆泡泡没有尖尾，整体飘在头顶
        else:
            shape = self._bubble_cloud_path(bx, y_b, w, h)
            tail_anchor = True
        if tail_anchor:
            tail = QPainterPath()
            tail.moveTo(bx + w / 2 - 11, y_b - 2)
            tail.quadTo(self.BCX - 3, y_b + 3, self.BCX, y_b + 15)
            tail.quadTo(self.BCX + 3, y_b + 3, bx + w / 2 + 11, y_b - 2)
            tail.closeSubpath()
            shape = shape.united(tail)

        p.save()
        p.setOpacity(a)
        # 以尾巴尖为锚点缩放：气泡像从头顶"啵"地冒出来
        ax, ay = (self.BCX, y_b + 15) if tail_anchor \
            else (bx + w / 2.0, y_b - h / 2.0)
        p.translate(ax, ay)
        # 摇摆 / 颤抖：整框随情绪轻晃（晕车坐船慢摇、生气细颤、傲娇微抖）
        if th["wob"] > 0.01:
            p.rotate(math.sin(self.t * th["wob_sp"]) * th["wob"])
        if style == "round":
            # 圆泡泡轻轻呼吸（像饱饱的肚子一起一伏）
            mo = 0.035 * math.sin(self.t * 5.2)
            p.scale(1.0 + mo, 1.0 - mo)
        p.scale(sc, sc)
        p.translate(-ax, -ay)
        if style == "burst":
            # 生气框：外圈一层极淡的暖光（只做体积感，不抢戏）
            p.setPen(QPen(QColor(240, 170, 120, 55), 5.0, Qt.SolidLine,
                          Qt.RoundCap, Qt.RoundJoin))
            p.setBrush(Qt.NoBrush)
            p.drawPath(shape)
        # 上亮下沉的渐变填充（像有光从上面打下来）
        grad = QLinearGradient(0.0, y_b - h - 8.0, 0.0, y_b + 4.0)
        c_top, c_bot = QColor(th["top"]), QColor(th["bot"])
        grad.setColorAt(0.0, c_top)
        grad.setColorAt(1.0, c_bot)
        p.setPen(QPen(QColor(th["edge"]), 1.8, Qt.SolidLine,
                      Qt.RoundCap, Qt.RoundJoin))
        p.setBrush(QBrush(grad))
        p.drawPath(shape)
        # 左上柔光（径向渐变，边缘完全透明——实色椭圆会留下硬边，
        # 看着像贴在气泡上的一块白斑）
        if th["gloss"] > 0.05 and style != "burst":
            p.setPen(Qt.NoPen)
            gg = QRadialGradient(QPointF(bx + w * 0.30, y_b - h * 0.68),
                                 max(w * 0.26, h * 0.75))
            gg.setColorAt(0.0, QColor(255, 255, 255, int(82 * th["gloss"])))
            gg.setColorAt(0.55, QColor(255, 255, 255, int(34 * th["gloss"])))
            gg.setColorAt(1.0, QColor(255, 255, 255, 0))
            p.setBrush(QBrush(gg))
            p.drawEllipse(QRectF(bx + w * 0.10, y_b - h * 0.94,
                                 w * 0.44, h * 0.64))
        # 挂饰（爱心 / 汁滴 / 泪滴）
        if th["deco"]:
            self._bubble_deco(p, th["deco"], bx, y_b, w, h)
        if style == "round":
            # 泡泡框：左上高光弧 + 右下反光（小一点，像真的肥皂泡）
            r_ = max(h / 2.0 + 8.0, w / 2.0 + 8.0)
            ccx, ccy = bx + w / 2.0, y_b - h / 2.0
            rr_ = QRectF(ccx - r_, ccy - r_, 2 * r_, 2 * r_)
            p.setBrush(Qt.NoBrush)
            p.setPen(QPen(QColor(255, 255, 255, 190), 2.4, Qt.SolidLine,
                          Qt.RoundCap))
            p.drawArc(rr_, 116 * 16, 44 * 16)
            p.setPen(QPen(QColor(255, 255, 255, 120), 1.8, Qt.SolidLine,
                          Qt.RoundCap))
            p.drawArc(rr_, 296 * 16, 22 * 16)
        p.setFont(f)
        p.setPen(QPen(INK))
        area = QRectF(bx + 15, y_b - h, w - 30, h - 26.0 if badges else h)
        shown = self._bubble_shown_text()
        if badges:
            # 有徽章行：文字占上部，徽章画在底部那一条里
            if shown == self.bubble_text:
                p.drawText(area, Qt.AlignHCenter | Qt.AlignVCenter
                           | Qt.TextWordWrap, self.bubble_text)
            else:
                self._draw_typing(p, fm, area, shown)
            self._draw_stat_badges(p, bx, y_b, w, badges)
        elif shown == self.bubble_text:
            p.drawText(area, Qt.AlignHCenter | Qt.AlignVCenter
                       | Qt.TextWordWrap, self.bubble_text)
        else:
            self._draw_typing(p, fm, area, shown)
        p.restore()

    def _draw_typing(self, p, fm, area, shown):
        """打字机进行中的文字版面：按全量文本的中排位置定位（同宽下
        前缀换行稳定），逐字向下补；说完一帧自动接回全量中排版式，
        中间无跳变。前 0.12s 停顿期 shown 为空串，自然留白。"""
        full_r = fm.boundingRect(0, 0, int(area.width()), 500,
                                 Qt.TextWordWrap, self.bubble_text)
        if not shown:
            return
        part_r = fm.boundingRect(0, 0, int(area.width()), 500,
                                 Qt.TextWordWrap, shown)
        top = area.top() + (area.height() - full_r.height()) / 2.0
        p.drawText(QRectF(area.left(), top, area.width(),
                          part_r.height() + 4.0),
                   Qt.AlignHCenter | Qt.AlignTop | Qt.TextWordWrap, shown)

    def _draw_stat_badges(self, p, bx, y_b, w, badges):
        """陪伴档案徽章行：星星=陪伴天数 · 面包=喂食次数 · 爱心=摸头次数。
        画在气泡底部留出的那一行里（_draw_bubble 已把 h 加高 26px）。"""
        n = len(badges)
        if n == 0:
            return
        seg = w / n
        cy = y_b - 13.0
        f = QFont()
        f.setPixelSize(12)
        f.setBold(True)
        p.setFont(f)
        for i, (kind, val) in enumerate(badges):
            cx = bx + seg * (i + 0.5)
            if kind == "day":                # 小星星（奶油黄）
                p.setPen(Qt.NoPen)
                p.setBrush(QColor("#F6C24E"))
                star = QPainterPath()
                for k in range(10):
                    rr = 6.2 if k % 2 == 0 else 2.8
                    ang = -math.pi / 2.0 + k * math.pi / 5.0
                    pt = QPointF(cx - 8.0 + math.cos(ang) * rr,
                                 cy + math.sin(ang) * rr)
                    if k == 0:
                        star.moveTo(pt)
                    else:
                        star.lineTo(pt)
                star.closeSubpath()
                p.drawPath(star)
            elif kind == "feed":             # 小面包（同饱食度牌的画法）
                p.setPen(Qt.NoPen)
                p.setBrush(QColor(238, 186, 120))
                p.drawEllipse(QPointF(cx - 8.0, cy), 6.2, 4.8)
                p.setBrush(QColor(214, 160, 96))
                p.drawEllipse(QPointF(cx - 8.0, cy - 2.2), 3.2, 1.7)
            else:                            # 小爱心
                p.setPen(Qt.NoPen)
                p.setBrush(QColor(HEARTS[0]))
                p.drawPath(self._heart_path(cx - 8.0, cy, 6.0))
            p.setPen(QPen(INK))
            p.drawText(QRectF(cx + 1.0, cy - 9.0, seg - 10.0, 18.0),
                       Qt.AlignLeft | Qt.AlignVCenter, str(val))
