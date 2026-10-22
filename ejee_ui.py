"""EJEE UI 层（P3-13 第三刀：菜单 / 对话框 / 独立特效窗迁出主文件）。

这里住着一批「不依赖桌宠状态机」的界面件：
  · _menu_icon / _paint_card / SoftMenu —— 奶油卡片菜单全家
  · PomoDialog + 番茄钟时长配置 —— 开始专注前的时长选择卡
  · BreadCursor / JuiceOverlay / Crumb —— 手里的面包 / 橘子汁全局层 /
    掉地上的面包渣，都是独立顶层小窗
行为与主文件版逐字一致；验收基准：--shot 14 张预览逐字节一致。
"""
import math
import random
import sys
import time

from PySide6.QtCore import Qt, QTimer, QPointF, QRectF, QPoint, Signal
from PySide6.QtGui import (QPainter, QColor, QPen, QBrush, QPainterPath,
                           QIcon, QPixmap, QLinearGradient)
from PySide6.QtWidgets import (QApplication, QWidget, QMenu, QDialog,
                               QLabel, QPushButton, QVBoxLayout, QHBoxLayout,
                               QComboBox)

from ejee_paint import clamp, DW, PAD_T

# ---- 番茄钟时长配置（与 PomoDialog 同住；ejee_pet 回导引用） ----
POMO_PRESETS = [15, 25, 45, 60, 90]   # 番茄钟时长预设（分钟）
POMO_MIN_DEF, POMO_MIN_LO, POMO_MIN_HI = 25, 1, 180

# 氛围飘浮物生成间隔（秒）：小叶子/星点偶尔横穿屏幕的桌面氛围
AMBIENT_EVERY = (55.0, 95.0)


_ICON_CACHE = {}

MENU_QSS = """
QMenu {
    background: transparent;
    border: 0px;
    padding: 15px 13px;
    font-family: "Microsoft YaHei UI", "Microsoft YaHei", sans-serif;
    font-size: 10pt;
    color: #5C3A22;
}
QMenu::item {
    padding: 7px 24px 7px 7px;
    margin: 1px 3px;
    border-radius: 9px;
    min-width: 92px;
}
QMenu::item:selected {
    background: #FFE7C5;
    color: #40260F;
}
QMenu::item:disabled {
    color: #C7AF98;
}
QMenu::separator {
    height: 1px;
    background: #F2DFC5;
    margin: 5px 12px;
}
QMenu::indicator {
    width: 0px;
    height: 0px;
}
"""


def _menu_icon(kind, col="#BC7A42"):
    """生成 18×18 矢量小图标（2x 采样）。暖棕色描边，与桌宠配色统一。"""
    key = (kind, col)
    if key in _ICON_CACHE:
        return _ICON_CACHE[key]
    dpr = 2
    pm = QPixmap(18 * dpr, 18 * dpr)
    pm.fill(Qt.transparent)
    pm.setDevicePixelRatio(dpr)
    p = QPainter(pm)
    p.setRenderHint(QPainter.Antialiasing, True)
    c = QColor(col)
    p.setPen(QPen(c, 1.7, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
    p.setBrush(Qt.NoBrush)
    if kind == "bread":                      # 牛奶面包（圆顶 + 三道割痕）
        body = QPainterPath()
        body.moveTo(2.6, 9.6)
        body.cubicTo(2.6, 4.8, 5.5, 2.8, 9.0, 2.8)
        body.cubicTo(12.5, 2.8, 15.4, 4.8, 15.4, 9.6)
        body.cubicTo(15.4, 12.6, 15.2, 13.6, 13.6, 13.6)
        body.lineTo(4.4, 13.6)
        body.cubicTo(2.8, 13.6, 2.6, 12.6, 2.6, 9.6)
        body.closeSubpath()
        p.drawPath(body)
        p.setPen(QPen(c, 1.3, Qt.SolidLine, Qt.RoundCap))
        p.drawLine(QPointF(6.2, 6.3), QPointF(6.9, 9.4))
        p.drawLine(QPointF(9.0, 6.1), QPointF(9.7, 9.2))
        p.drawLine(QPointF(11.8, 6.3), QPointF(12.5, 9.4))
    elif kind == "clock":                    # 番茄钟
        p.drawEllipse(QPointF(9.0, 9.0), 6.3, 6.3)
        p.setPen(QPen(c, 1.5, Qt.SolidLine, Qt.RoundCap))
        p.drawLine(QPointF(9.0, 5.2), QPointF(9.0, 9.2))
        p.drawLine(QPointF(9.0, 9.2), QPointF(11.7, 10.6))
    elif kind == "ghost":                    # 穿透模式：虚线圈 + 中心点
        pen = QPen(c, 1.5, Qt.DashLine, Qt.RoundCap)
        pen.setDashPattern([1.6, 1.5])
        p.setPen(pen)
        p.drawEllipse(QPointF(9.0, 9.0), 6.2, 6.2)
        p.setPen(Qt.NoPen)
        p.setBrush(c)
        p.drawEllipse(QPointF(9.0, 9.0), 1.9, 1.9)
    elif kind == "size":                     # 尺寸：方框 + 斜箭头
        p.drawRoundedRect(QRectF(3.4, 3.4, 11.2, 11.2), 3.0, 3.0)
        p.setPen(QPen(c, 1.5, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        p.drawLine(QPointF(6.8, 11.2), QPointF(11.2, 6.8))
        p.drawLine(QPointF(11.2, 6.8), QPointF(11.2, 9.8))
        p.drawLine(QPointF(11.2, 6.8), QPointF(8.2, 6.8))
    elif kind == "quit":                     # 退出：门 + 出箭头
        path = QPainterPath()
        path.moveTo(10.4, 3.2)
        path.lineTo(4.6, 3.2)
        path.lineTo(4.6, 14.8)
        path.lineTo(10.4, 14.8)
        p.drawPath(path)
        p.setPen(QPen(c, 1.5, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        p.drawLine(QPointF(8.4, 9.0), QPointF(14.6, 9.0))
        p.drawLine(QPointF(12.4, 6.9), QPointF(14.6, 9.0))
        p.drawLine(QPointF(12.4, 11.1), QPointF(14.6, 9.0))
    elif kind == "eye":                      # 显示 / 隐藏
        path = QPainterPath()
        path.moveTo(2.6, 9.0)
        path.quadTo(9.0, 2.6, 15.4, 9.0)
        path.quadTo(9.0, 15.4, 2.6, 9.0)
        p.drawPath(path)
        p.setBrush(c)
        p.setPen(Qt.NoPen)
        p.drawEllipse(QPointF(9.0, 9.0), 2.1, 2.1)
    elif kind == "reset":                    # 重置大小：开口圆弧 + 箭头
        p.setPen(QPen(c, 1.7, Qt.SolidLine, Qt.RoundCap))
        p.drawArc(QRectF(3.6, 3.6, 10.8, 10.8), 50 * 16, 290 * 16)
        p.save()
        p.translate(9.0, 9.0)
        p.rotate(50.0)
        p.translate(0.0, -5.4)
        p.setPen(Qt.NoPen)
        p.setBrush(c)
        tri = QPainterPath()
        tri.moveTo(0.0, -2.9)
        tri.lineTo(-2.6, 1.4)
        tri.lineTo(2.6, 1.4)
        tri.closeSubpath()
        p.drawPath(tri)
        p.restore()
    elif kind == "mute":                     # 静默模式：小喇叭 + 斜杠
        sp = QPainterPath()
        sp.moveTo(3.2, 7.2)
        sp.lineTo(6.2, 7.2)
        sp.lineTo(9.6, 4.2)
        sp.lineTo(9.6, 13.8)
        sp.lineTo(6.2, 10.8)
        sp.lineTo(3.2, 10.8)
        sp.closeSubpath()
        p.drawPath(sp)
        p.setPen(QPen(c, 1.5, Qt.SolidLine, Qt.RoundCap))
        p.drawLine(QPointF(11.6, 5.8), QPointF(15.0, 12.2))
    elif kind == "slider":                   # 时长设置：双滑杆
        p.drawLine(QPointF(3.2, 6.3), QPointF(14.8, 6.3))
        p.drawLine(QPointF(3.2, 11.7), QPointF(14.8, 11.7))
        for (kx, ky) in ((11.3, 6.3), (6.7, 11.7)):
            p.setPen(QPen(c, 1.5))
            p.setBrush(QColor("#FFFDF8"))
            p.drawEllipse(QPointF(kx, ky), 2.3, 2.3)
    elif kind == "pencil":                   # 自定义
        p.save()
        p.translate(9.0, 9.0)
        p.rotate(-45.0)
        p.setPen(QPen(c, 1.6, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        p.setBrush(Qt.NoBrush)
        p.drawRoundedRect(QRectF(-2.6, -6.4, 5.2, 9.6), 1.8, 1.8)
        p.drawLine(QPointF(-2.6, 3.2), QPointF(0.0, 6.6))
        p.drawLine(QPointF(2.6, 3.2), QPointF(0.0, 6.6))
        p.restore()
    elif kind == "hand":                     # 投喂：手掌托着
        p.setPen(QPen(c, 2.0, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        palm = QPainterPath()
        palm.moveTo(4.2, 9.4)
        palm.cubicTo(4.2, 8.0, 5.2, 7.4, 6.2, 7.4)
        palm.lineTo(12.0, 7.4)
        palm.cubicTo(13.6, 7.4, 14.6, 8.4, 14.6, 10.2)
        palm.cubicTo(14.6, 13.2, 12.8, 15.0, 9.6, 15.0)
        palm.cubicTo(6.4, 15.0, 4.2, 13.0, 4.2, 10.6)
        palm.closeSubpath()
        p.drawPath(palm)
        p.drawLine(QPointF(6.6, 7.4), QPointF(6.6, 4.6))
        p.drawLine(QPointF(9.2, 7.2), QPointF(9.2, 3.8))
        p.drawLine(QPointF(11.8, 7.4), QPointF(11.8, 4.8))
    elif kind in ("radio_on", "radio_off"):  # 尺寸子菜单的单选标记
        if kind == "radio_on":
            p.setPen(QPen(QColor("#E1863A"), 1.3))
            p.setBrush(QColor("#F9A75C"))
            p.drawEllipse(QPointF(9.0, 9.0), 4.4, 4.4)
            p.setPen(Qt.NoPen)
            p.setBrush(QColor(255, 255, 255, 235))
            p.drawEllipse(QPointF(8.2, 8.2), 1.5, 1.5)
        else:
            p.setPen(QPen(QColor("#E2C6A2"), 1.4))
            p.setBrush(Qt.NoBrush)
            p.drawEllipse(QPointF(9.0, 9.0), 3.4, 3.4)
    p.end()
    icon = QIcon(pm)
    _ICON_CACHE[key] = icon
    return icon


def _paint_card(p, rect, shadow=9, radius=15):
    """奶油卡片：外圈自绘柔影 + 渐变本体 + 暖橙描边（菜单 / 弹窗共用）。"""
    card = rect.adjusted(shadow, shadow, -shadow, -shadow)
    p.setPen(Qt.NoPen)
    for i in range(shadow, 0, -1):
        k = 1.0 - i / float(shadow)
        p.setBrush(QColor(140, 90, 44, int(5 + 20 * k * k)))
        p.drawRoundedRect(card.adjusted(-i, -i, i, i).translated(0.0, 3.0),
                          radius + i, radius + i)
    g = QLinearGradient(card.topLeft(), card.bottomLeft())
    g.setColorAt(0.0, QColor(255, 253, 249, 252))
    g.setColorAt(1.0, QColor(255, 243, 227, 252))
    p.setBrush(QBrush(g))
    p.setPen(QPen(QColor(239, 208, 165, 240), 1.5))
    p.drawRoundedRect(card.adjusted(0.75, 0.75, -0.75, -0.75),
                      radius - 1.5, radius - 1.5)


class SoftMenu(QMenu):
    """奶油色圆角卡片菜单：外圈自绘柔影，卡片用线性渐变平涂，
    条目 / 分隔线 / 勾选圈全部交给 QSS。窗口需半透明 + 去原生阴影，
    否则圆角外会露出方形底。"""
    SHADOW = 9
    RADIUS = 15

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(self.windowFlags() | Qt.FramelessWindowHint
                            | Qt.NoDropShadowWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setStyleSheet(MENU_QSS)

    def paintEvent(self, e):
        sh, rad = self.SHADOW, self.RADIUS
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing, True)
        _paint_card(p, QRectF(self.rect()), sh, rad)
        p.end()
        super().paintEvent(e)      # 条目、分隔线由样式表绘制
        # 自绘开关（QSS 的 check 指示器会与图标抢位，故手绘一枚小胶囊）
        sw = [a for a in self.actions() if a.property("_switch")]
        if sw:
            p = QPainter(self)
            p.setRenderHint(QPainter.Antialiasing, True)
            for a in sw:
                r = self.actionGeometry(a)
                if r.isNull():
                    continue
                self._draw_switch(p, r, bool(a.property("_switchOn")))
            p.end()

    @staticmethod
    def _draw_switch(p, r, on):
        w, h = 25.0, 13.5
        x = r.right() - w - 6.0
        cy = r.center().y()
        body = QRectF(x, cy - h / 2.0, w, h)
        p.setPen(QPen(QColor("#E1863A") if on else QColor("#DEC4A4"), 1.2))
        p.setBrush(QColor("#F9A75C") if on else QColor("#FBF1E2"))
        p.drawRoundedRect(body, h / 2.0, h / 2.0)
        p.setPen(Qt.NoPen)
        p.setBrush(QColor(255, 255, 255))
        kx = x + w - h / 2.0 - 1.2 if on else x + h / 2.0 + 1.2
        p.drawEllipse(QPointF(kx, cy), h / 2.0 - 2.2, h / 2.0 - 2.2)


DIALOG_QSS = """
QDialog { background: transparent; }
QLabel#dlgTitle {
    color: #8A5B33;
    font-family: "Microsoft YaHei UI", "Microsoft YaHei";
    font-size: 10pt;
}
QLabel#dlgValue {
    color: #4A2C1E;
    font-family: "Microsoft YaHei UI", "Microsoft YaHei";
    font-size: 25pt;
    font-weight: 600;
}
QLabel#dlgUnit {
    color: #A2805F;
    font-family: "Microsoft YaHei UI", "Microsoft YaHei";
    font-size: 10pt;
    padding-bottom: 9px;
}
QLabel#dlgHint {
    color: #C2A385;
    font-family: "Microsoft YaHei UI", "Microsoft YaHei";
    font-size: 8pt;
}
QPushButton#step {
    background: #FFF6E8;
    border: 1px solid #EFD8B8;
    border-radius: 15px;
    color: #B4713C;
    font-size: 14pt;
    font-weight: 600;
}
QPushButton#step:hover { background: #FFE9CB; }
QPushButton#step:pressed { background: #FBD3A0; }
QPushButton#chip {
    background: #FFF6E8;
    border: 1px solid #EFD8B8;
    border-radius: 11px;
    color: #8A5B33;
    font-family: "Microsoft YaHei UI", "Microsoft YaHei";
    font-size: 9pt;
    padding: 3px 9px;
}
QPushButton#chip:hover { background: #FFE9CB; }
QPushButton#chip:checked {
    background: #F9A75C;
    border: 1px solid #E1863A;
    color: #FFFFFF;
}
QPushButton#primary {
    background: #F9A75C;
    border: none;
    border-radius: 13px;
    color: #FFFFFF;
    font-family: "Microsoft YaHei UI", "Microsoft YaHei";
    font-size: 10pt;
    padding: 7px 24px;
}
QPushButton#primary:hover { background: #FBAF6A; }
QPushButton#primary:pressed { background: #EE9448; }
QPushButton#plain {
    background: transparent;
    border: none;
    color: #9A7856;
    font-family: "Microsoft YaHei UI", "Microsoft YaHei";
    font-size: 10pt;
    padding: 7px 14px;
}
QPushButton#plain:hover { color: #6B4426; }
"""


class PomoDialog(QDialog):
    """开始番茄钟前的时长选择卡：与菜单同一套奶油卡片（无边框 + 自绘柔影），
    大号数字 + 加减步进 + 预设胶囊，可拖动窗口；确认即开始专注。"""
    SHADOW = 10
    RADIUS = 16

    def __init__(self, minutes, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint
                            | Qt.NoDropShadowWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setModal(True)
        self.setStyleSheet(DIALOG_QSS)
        self._val = int(clamp(int(minutes), POMO_MIN_LO, POMO_MIN_HI))
        self._drag = None
        self._build_ui()

    # ---- 界面 ----
    def _build_ui(self):
        sh = self.SHADOW
        lay = QVBoxLayout(self)
        lay.setContentsMargins(sh + 20, sh + 14, sh + 20, sh + 16)
        lay.setSpacing(9)

        title = QLabel("番茄钟")
        title.setObjectName("dlgTitle")
        title.setAlignment(Qt.AlignHCenter)
        lay.addWidget(title)

        # 步进行：[−] 25 分钟 [+]
        row = QHBoxLayout()
        row.setSpacing(14)
        row.setAlignment(Qt.AlignHCenter)
        b_minus = QPushButton("−")
        b_minus.setObjectName("step")
        b_minus.setFixedSize(30, 30)
        b_minus.setCursor(Qt.PointingHandCursor)
        b_minus.clicked.connect(lambda: self._bump(-5))
        b_plus = QPushButton("+")
        b_plus.setObjectName("step")
        b_plus.setFixedSize(30, 30)
        b_plus.setCursor(Qt.PointingHandCursor)
        b_plus.clicked.connect(lambda: self._bump(5))
        self.lbl_val = QLabel(str(self._val))
        self.lbl_val.setObjectName("dlgValue")
        unit = QLabel("分钟")
        unit.setObjectName("dlgUnit")
        row.addWidget(b_minus)
        row.addWidget(self.lbl_val)
        row.addWidget(unit, 0, Qt.AlignBottom)
        row.addWidget(b_plus)
        lay.addLayout(row)

        hint = QLabel("想专注多久就调多久（1 ~ 180 分钟）")
        hint.setObjectName("dlgHint")
        hint.setAlignment(Qt.AlignHCenter)
        lay.addWidget(hint)

        # 预设胶囊
        chips = QHBoxLayout()
        chips.setSpacing(6)
        chips.setAlignment(Qt.AlignHCenter)
        self._chips = []
        for v in POMO_PRESETS:
            b = QPushButton(str(v))
            b.setObjectName("chip")
            b.setCheckable(True)
            b.setCursor(Qt.PointingHandCursor)
            b.clicked.connect(lambda checked=False, mm=v: self._set_val(mm))
            chips.addWidget(b)
            self._chips.append((v, b))
        lay.addLayout(chips)

        # 按钮
        btns = QHBoxLayout()
        btns.setSpacing(6)
        btns.setAlignment(Qt.AlignHCenter)
        b_cancel = QPushButton("取消")
        b_cancel.setObjectName("plain")
        b_cancel.setCursor(Qt.PointingHandCursor)
        b_cancel.clicked.connect(self.reject)
        b_ok = QPushButton("开始")
        b_ok.setObjectName("primary")
        b_ok.setCursor(Qt.PointingHandCursor)
        b_ok.setDefault(True)
        b_ok.clicked.connect(self.accept)
        btns.addWidget(b_cancel)
        btns.addWidget(b_ok)
        lay.addLayout(btns)

        self._set_val(self._val)

    def _set_val(self, v):
        self._val = int(clamp(int(v), POMO_MIN_LO, POMO_MIN_HI))
        self.lbl_val.setText(str(self._val))
        for v0, b in self._chips:
            b.setChecked(v0 == self._val)

    def _bump(self, d):
        self._set_val(self._val + d)

    def minutes(self):
        return self._val

    # ---- 无边框窗口：拖动 + 卡片底 ----
    def paintEvent(self, e):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing, True)
        _paint_card(p, QRectF(self.rect()), self.SHADOW, self.RADIUS)
        p.end()

    def mousePressEvent(self, e):
        if e.button() == Qt.LeftButton:
            self._drag = (e.globalPosition().toPoint()
                          - self.frameGeometry().topLeft())
            e.accept()

    def mouseMoveEvent(self, e):
        if self._drag is not None and e.buttons() & Qt.LeftButton:
            self.move(e.globalPosition().toPoint() - self._drag)
            e.accept()

    def mouseReleaseEvent(self, e):
        self._drag = None


class BreadCursor(QWidget):
    """「手里的面包」：跟随鼠标的小窗户（无边框 / 置顶 / 点击穿透）。
      · 每 16ms 贴到光标右下方
      · 轮询左键，出现一次「按下 → 松开」就当作用户放下面包，
        emit dropped(全局坐标)，由桌宠判断有没有喂到嘴边
      · 因为窗口本身是穿透的、收不到鼠标事件，Windows 下用
        GetAsyncKeyState 读全局按键状态
    """
    dropped = Signal(QPoint)
    SZ = 64

    def __init__(self):
        super().__init__(None, Qt.FramelessWindowHint | Qt.Tool
                         | Qt.WindowStaysOnTopHint
                         | Qt.WindowTransparentForInput)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        self.setAttribute(Qt.WA_ShowWithoutActivating, True)
        self.resize(self.SZ, self.SZ)
        self._hot = False
        self._was_down = False
        self._arm_t = time.time() + 0.30    # 刚从菜单点起来那一下不算"放下"
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._poll)
        self._timer.start(16)

    def set_hot(self, v):
        if v != self._hot:
            self._hot = v
            self.update()

    @staticmethod
    def _down():
        if sys.platform == "win32":
            import ctypes
            return bool(ctypes.windll.user32.GetAsyncKeyState(0x01) & 0x8000)
        return bool(QApplication.mouseButtons() & Qt.LeftButton)

    def _poll(self):
        gp = QCursor.pos()
        self.move(gp - QPoint(self.SZ // 2 - 8, self.SZ // 2 + 4))
        down = self._down()
        if time.time() >= self._arm_t and self._was_down and not down:
            self.dropped.emit(gp)
        self._was_down = down

    def stop(self):
        self._timer.stop()
        self.hide()
        self.deleteLater()

    def paintEvent(self, e):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing, True)
        p.translate(self.width() / 2.0, self.height() / 2.0)
        sc = 1.14 if self._hot else 1.0
        p.scale(sc, sc)
        p.setPen(Qt.NoPen)                       # 落影
        p.setBrush(QColor(92, 58, 30, 58))
        p.drawEllipse(QPointF(1.0, 14.0), 15.0, 4.6)
        body = QPainterPath()                    # 面包体：圆顶 + 圆底
        body.moveTo(-16.5, 5.0)
        body.cubicTo(-19.5, -7.0, -12.0, -15.0, 0.0, -15.0)
        body.cubicTo(12.0, -15.0, 19.5, -7.0, 16.5, 5.0)
        body.quadTo(0.0, 12.5, -16.5, 5.0)
        p.setPen(QPen(QColor("#BE8146"), 2.2, Qt.SolidLine,
                      Qt.RoundCap, Qt.RoundJoin))
        p.setBrush(QColor(251, 227, 186))
        p.drawPath(body)
        p.setPen(QPen(QColor("#B4793E"), 1.9, Qt.SolidLine, Qt.RoundCap))
        for sx in (-8.5, -0.5, 7.5):             # 三道割痕
            cut = QPainterPath()
            cut.moveTo(sx, -8.5)
            cut.quadTo(sx + 1.8, -3.5, sx + 4.2, 0.6)
            p.drawPath(cut)
        p.setPen(QPen(QColor(255, 255, 255, 150), 2.0,
                      Qt.SolidLine, Qt.RoundCap))
        hl = QPainterPath()                      # 左上高光
        hl.moveTo(-10.5, -8.0)
        hl.quadTo(-7.5, -12.0, -2.0, -12.6)
        p.drawPath(hl)
        if self._hot:                            # 悬在嘴边：虚线光环
            pen = QPen(QColor(246, 176, 92, 220), 2.0, Qt.DashLine,
                       Qt.RoundCap)
            pen.setDashPattern([1.6, 1.4])
            p.setPen(pen)
            p.setBrush(Qt.NoBrush)
            p.drawEllipse(QPointF(0, 0), 22.0, 22.0)


class JuiceOverlay(QWidget):
    """橘子汁特效层：一块覆盖整块虚拟桌面的独立顶层透明窗，鼠标完全穿透。

    宠物自身窗口只有 400×340 设计坐标那么大，汁水画在窗口里必然被窗口
    矩形裁掉（朝尾巴那一侧一出界就没了）。这一层把汁滴换算成全局屏幕
    坐标来画，所以汁水可以飞出宠物窗口、360° 无边界溅射，也彻底去掉了
    原来"撞到框内沿就挂成水渍"的范围框。没有汁水时窗口自动隐藏。
    """

    def __init__(self, parent=None):
        super().__init__(parent, Qt.FramelessWindowHint
                         | Qt.WindowStaysOnTopHint | Qt.Tool
                         | Qt.WindowTransparentForInput)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        self.setAttribute(Qt.WA_ShowWithoutActivating, True)
        self._items = []
        # 氛围飘浮物（D2-11）：与汁滴共用这块全局透明窗，低透明度横穿屏幕。
        # _amb_next 惰性初始化——JuiceOverlay 在 EjeePet.__init__ 里创建，
        # 而且位置在呼吸/尾摆相位之前：构造期咬 random 会挪动 --shot 的
        # 种子流，让全部预览帧整体亚像素位移（P0-2 血泪教训的变体）
        self._amb = []
        self._amb_next = None
        self.hide()
        self._place()

    def _place(self):
        r = QRectF()
        for sc in QApplication.screens():
            r = r.united(QRectF(sc.geometry()))
        if r.isEmpty():
            pri = QApplication.primaryScreen()
            if pri is not None:
                r = QRectF(pri.geometry())
            else:
                r = QRectF(0, 0, 1920, 1080)
        self.setGeometry(int(r.left()), int(r.top()),
                         int(r.width()), int(r.height()))

    def ambient_step(self, dt, scr, t_now=None):
        """氛围飘浮物推进（宠物主循环每帧调用）：小叶子/星点从屏幕一侧
        缓慢飘到另一侧，低透明度，与角色无关的桌面氛围。
        不进粒子列表、不进视线系统、不与角色产生任何交互；
        scr 用宠物当前所在屏幕（多屏各飘各的）。"""
        if scr is None or dt <= 0:
            return
        now = t_now if t_now is not None else time.time()
        if self._amb_next is None:      # 首帧才定首片飘叶的时刻（不动构造期种子流）
            self._amb_next = now + random.uniform(18.0, 40.0)
        L, R, T = scr.left(), scr.right(), scr.top()
        H = scr.height()
        if now >= self._amb_next:
            self._amb_next = now + random.uniform(*AMBIENT_EVERY)
            from_left = random.random() < 0.5
            spd = random.uniform(20.0, 34.0)
            self._amb.append({
                "x": float(L - 30 if from_left else R + 30),
                "y": T + H * random.uniform(0.08, 0.62),
                "vx": spd if from_left else -spd,
                "ph": random.uniform(0.0, 6.28),
                "rot": random.uniform(0.0, 360.0),
                "vr": random.uniform(-40.0, 40.0),
                "kind": "leaf" if random.random() < 0.6 else "spark",
                "t0": now,
                "exit": float(R + 40 if from_left else L - 40),
            })
        alive = []
        for it in self._amb:
            it["x"] += it["vx"] * dt
            it["rot"] += it["vr"] * dt
            it["_y"] = it["y"] + math.sin(now * 1.3 + it["ph"]) * 9.0
            # 淡入 2.5s；飘近出口 2.5s 路程内淡出（按当前速度折算路程）
            it["_a"] = clamp(min((now - it["t0"]) / 2.5,
                                 abs(it["exit"] - it["x"])
                                 / max(60.0, abs(it["vx"]) * 2.5)), 0.0, 1.0)
            if (it["vx"] > 0 and it["x"] < it["exit"]) or \
                    (it["vx"] < 0 and it["x"] > it["exit"]):
                alive.append(it)
        self._amb = alive
        if self._amb and self.isVisible():
            self.update()

    def refresh(self, pet):
        """每帧把宠物身上的汁滴换算成全局坐标；没有汁滴也没有氛围
        飘浮物时自动隐藏。"""
        s = pet.width() / DW
        items = []
        for pt in pet.particles:
            if pt.kind != "juice":
                continue
            age = pet.t - pt.born
            if age < 0.0 or age >= pt.life:
                continue
            a = clamp(1.0 - age / pt.life, 0.0, 1.0)
            g = pet.mapToGlobal(QPoint(int(pt.x * s),
                                       int((pt.y + PAD_T) * s)))
            items.append((g.x(), g.y(), pt.size * s, a, age, pt.color))
        self._items = items
        if items or self._amb:
            if not self.isVisible():
                self._place()
                self.show()
            self.update()
        elif self.isVisible():
            self.hide()

    def _draw_ambient(self, p, ox, oy):
        """氛围飘浮物：秋橙小叶子（呼应角色的橘子叶）与淡金四角星点，
        旋转着慢飘，透明度封顶 0.26 —— 是背景，不是主角。"""
        for it in self._amb:
            p.save()
            p.translate(it["x"] - ox, it["_y"] - oy)
            p.rotate(it["rot"])
            p.setOpacity(0.26 * it.get("_a", 1.0))
            p.setPen(Qt.NoPen)
            if it["kind"] == "leaf":
                p.setBrush(QColor(232, 162, 89))
                leaf = QPainterPath()
                leaf.moveTo(0, -9)
                leaf.quadTo(7.5, -2, 0, 9)
                leaf.quadTo(-7.5, -2, 0, -9)
                p.drawPath(leaf)
                p.setPen(QPen(QColor(176, 108, 40, 160), 1.2,
                              Qt.SolidLine, Qt.RoundCap))
                p.drawLine(QPointF(0, -7), QPointF(0, 7))
            else:
                p.setBrush(QColor(246, 194, 78))
                st = QPainterPath()
                st.moveTo(0, -6)
                st.quadTo(1.2, -1.2, 6, 0)
                st.quadTo(1.2, 1.2, 0, 6)
                st.quadTo(-1.2, 1.2, -6, 0)
                st.quadTo(-1.2, -1.2, 0, -6)
                p.drawPath(st)
            p.restore()

    def paintEvent(self, e):
        if not self._items and not self._amb:
            return
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing, True)
        ox, oy = self.x(), self.y()
        self._draw_ambient(p, ox, oy)
        p.setPen(Qt.NoPen)
        for (gx, gy, sz, a, age, col) in self._items:
            c = QColor(col)
            c.setAlpha(int(255 * a))
            p.setBrush(c)
            stretch = 1.0 + min(0.5, age * 0.8)      # 坠落拉伸
            p.drawEllipse(QPointF(gx - ox, gy - oy),
                          sz * 0.62, sz * 0.62 * stretch)
        p.end()


class Crumb(QWidget):
    """掉在屏幕上的那一小块面包渣：一个 44×44 的透明小窗，画在松手点
    正下方（贴屏幕底部）——先弹跳两下落定，停留 CRUMB_HOLD 秒，再慢慢淡出。
    独立的顶层小窗（不是画在宠物窗口里），所以残渣落在宠物四周的屏幕
    任意位置都看得见；全程鼠标穿透，不挡任何操作。"""

    SZ = 44
    HOLD = 5.0            # 停留秒数
    FADE = 1.6            # 淡出秒数

    def __init__(self, gpos, screen_bottom):
        super().__init__(None, Qt.FramelessWindowHint | Qt.Tool
                         | Qt.WindowStaysOnTopHint
                         | Qt.WindowTransparentForInput)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        self.setAttribute(Qt.WA_ShowWithoutActivating, True)
        self.resize(self.SZ, self.SZ)
        self.t0 = time.time()
        self.alive = True
        # 落点：松手点正下方一点；顶到屏幕底部就贴着底部
        x = gpos.x() - self.SZ // 2
        y = gpos.y() + 26
        y = min(y, screen_bottom - self.SZ - 4)
        x = max(8, min(x, self._screen_right(gpos) - self.SZ - 8))
        self.move(int(x), int(y))
        self.gpos = QPoint(int(x + self.SZ / 2), int(y + self.SZ / 2))
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._timer.start(33)
        self.show()

    @staticmethod
    def _screen_right(gpos=None):
        """落点所在屏幕的右沿（副屏修正）：优先按掉落点找屏，
        找不到（如极小窗刚创建）再退回主屏。"""
        scr = QApplication.screenAt(gpos) if gpos is not None else None
        if scr is None:
            scr = QApplication.primaryScreen()
        return scr.availableGeometry().right() if scr else 1920

    def _tick(self):
        if time.time() - self.t0 > self.HOLD + self.FADE:
            self.alive = False
            self._timer.stop()
            self.hide()
            self.deleteLater()
            return
        self.update()

    def stop(self):
        self._timer.stop()
        self.hide()
        self.deleteLater()

    def paintEvent(self, e):
        age = time.time() - self.t0
        if age > self.HOLD:                       # 停留结束：慢慢淡出
            a = clamp(1.0 - (age - self.HOLD) / self.FADE, 0.0, 1.0)
        else:
            a = 1.0
        # 落地弹跳：前 0.42s 内两下递减的小跳
        if age < 0.42:
            k = clamp(age / 0.42, 0.0, 1.0)
            hop = math.sin(k * math.pi * 2.4) * (1.0 - k) * 7.0
            sq = 1.0 - abs(math.sin(k * math.pi * 2.4)) * 0.12
        else:
            hop = 0.0
            sq = 1.0
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing, True)
        p.setOpacity(a)
        cx, cy = self.SZ / 2.0, self.SZ / 2.0 + hop
        p.translate(cx, cy)
        p.scale(sq, 2.0 - sq)      # 挤压守恒：跳起时纵向拉长
        # 落影（贴地感）
        p.setPen(Qt.NoPen)
        p.setBrush(QColor(92, 58, 30, 56))
        p.drawEllipse(QPointF(1.0, 13.0 - hop * 0.7), 12.0, 3.4)
        # 残渣本体：一小块撕下来的面包边（不规则小片），极小
        p.setPen(QPen(QColor("#BE8146"), 1.6, Qt.SolidLine,
                      Qt.RoundCap, Qt.RoundJoin))
        p.setBrush(QColor(251, 227, 186))
        piece = QPainterPath()
        piece.moveTo(-11.0, 4.0)
        piece.lineTo(-8.0, -4.5)
        piece.lineTo(-1.0, -7.0)
        piece.lineTo(7.5, -3.0)
        piece.lineTo(10.5, 4.0)
        piece.quadTo(0.0, 8.5, -11.0, 4.0)
        p.drawPath(piece)
        # 撕口 + 一道割痕
        p.setPen(QPen(QColor("#B4793E"), 1.3, Qt.SolidLine, Qt.RoundCap))
        p.drawLine(QPointF(-3.5, -4.0), QPointF(1.5, 3.0))
        p.setPen(QPen(QColor(255, 255, 255, 130), 1.4,
                      Qt.SolidLine, Qt.RoundCap))
        hl = QPainterPath()
        hl.moveTo(-7.0, -3.0)
        hl.quadTo(-4.0, -5.6, -0.5, -5.4)
        p.drawPath(hl)


class BirthdayDialog(QDialog):
    """生日设置小对话框：月 / 日两个下拉（与 PomoDialog 同一套奶油卡片
    皮肤）。value 属性返回 "MM-DD"；选「不设」= 空串（清除生日）。
    不猜生日：用户不设置就不庆祝。
    kind="ejee"  设置 EJEE 自己的生日（当天它过生日）
    kind="owner" 设置主人的生日（当天它给主人庆祝）"""

    def __init__(self, current="", parent=None, kind="ejee"):
        super().__init__(parent)
        self.setWindowTitle("EJEE 的生日" if kind == "ejee" else "主人的生日")
        self.setModal(True)
        self.value = None
        self.setStyleSheet(DIALOG_QSS)
        lay = QVBoxLayout(self)
        if kind == "ejee":
            tip = QLabel("给 EJEE 定个生日吧～\n（选「不设」就不过生日）")
        else:
            tip = QLabel("告诉我你的生日吧～\n（选「不设」就不提醒你）")
        lay.addWidget(tip)
        row = QHBoxLayout()
        self._m = QComboBox()
        self._d = QComboBox()
        self._m.addItem("不设", None)
        for mth in range(1, 13):
            self._m.addItem("%d 月" % mth, mth)
        for dy in range(1, 32):
            self._d.addItem("%d 日" % dy, dy)
        if len(current) == 5:
            try:
                mm, dd = current.split("-")
                self._m.setCurrentIndex(int(mm))       # 索引 0 = 不设
                self._d.setCurrentIndex(int(dd) - 1)
            except ValueError:
                pass
        row.addWidget(self._m)
        row.addWidget(self._d)
        lay.addLayout(row)
        btns = QHBoxLayout()
        ok = QPushButton("记住啦")
        cancel = QPushButton("算了")
        ok.clicked.connect(self.accept)
        cancel.clicked.connect(self.reject)
        btns.addStretch(1)
        btns.addWidget(ok)
        btns.addWidget(cancel)
        lay.addLayout(btns)

    def accept(self):
        m = self._m.currentData()
        d = self._d.currentData()
        if m is None:
            self.value = ""              # 「不设」：清除生日
        else:
            self.value = "%02d-%02d" % (int(m), int(d))
        super().accept()
