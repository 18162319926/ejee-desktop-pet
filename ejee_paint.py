"""EJEE 纯绘制层（P3-13 第一刀：无状态绘制方法迁出主文件）。

EjeePaintMixin 只做「给一块 QPainter，按当前帧参数画东西」：
不含状态机、输入、窗口逻辑。方法体从 ejee_pet.py 逐字搬运，
由 EjeePet(EjeePaintMixin, QWidget) 继承混入，行为零变化。
验收基准：--shot 14 张预览与基线逐字节一致（tools/check_preview.py --run）。
"""
import math
import sys

from PySide6.QtCore import Qt, QRectF, QPointF
from PySide6.QtGui import (QColor, QPen, QBrush, QPainterPath,
                           QLinearGradient, QRadialGradient)


# ---- 主文件回用的共享工具/色（单一出处，ejee_pet 顶部 import 回去） ----

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
        fade = max(fade_alt, sa, ha, ma)
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

