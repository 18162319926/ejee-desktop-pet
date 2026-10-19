# -*- coding: utf-8 -*-
"""
EJEE（伊吉）桌面宠物 —— 功能说明
================================================================
一只把静态设定图做成「会生气、会撒娇、会自己散步」的橘色小金鱼。
无边框 / 透明 / 置顶 / 不占任务栏；全部绘制在 paintEvent 里完成，
底图来自设定图抠图（4x 超分），只有眼睛与 ω 嘴是可动精灵。

零、角色设定
    EJEE（伊吉）来自韩国日山的湖水公园，MBTI 是 ISFP。
    爱好是在泡泡里睡觉 —— 入睡后会真的把自己裹进一颗透明泡泡里；
    魅力点是月亮形状的瞳孔（happy / surprised 时的月牙眼）；
    最爱牛奶吐司（喂食动画里的那一块）；
    口头禅是「吧嗒吧嗒」。
    EJEE 的一天很简单：睡觉、吃饭、和朋友玩、游泳
    —— 正好对应 睡眠 / 喂食 / 待机张望 / 散步游泳 这四套动作。

一、运行方式
    python ejee_pet.py            正常启动
    python ejee_pet.py --shot     离屏渲染各状态预览图（previews/preview_*.png）供校准

二、情绪与表情
   精灵 + 矢量叠加的混合方案，参数走弹簧（SPRING_K），状态间平滑过渡、无硬切。
   八个状态（优先级 mischief > dizzy > shy > happy > angry > surprised > sleep > idle）：
     idle       平静：呼吸起伏 + 眼球跟随鼠标（320px 死区）+ 待机微动作
     happy      开心：喂面包 / 摸头 / 庆祝 —— 眯眼月牙 + 张嘴笑 + 爱心星星
     angry      生气委屈：拖到屏幕边缘 —— 眼皮下垂 + 下弯弧眉 + 乌云蒸汽
     surprised  惊讶好奇：鼠标靠近 130px（7s 冷却）—— 瞪眼 + 后仰 + 感叹号
     mischief   恶作剧：抓尾巴 —— ＞＜坏笑眼 + 吐舌头 + 蓄力弹开 + 橘子汁喷射
     shy        傲娇躲避：连摸 5 下 —— 半眯眼别过头 + 直接闪现到屏幕另一侧
                （无身体形变、无小碎步）+ 傲娇台词 + 头顶小蒸汽 3 秒
     dizzy      晕车：按在屏幕边缘来回疯狂拉扯 —— 双眼蚊香圈（两眼反向自转）
                + 每 0.85s 真吐一串泡泡 + 「别晃啦，我要吐泡泡了」，持续 4.5s
     sleep      睡眠：5 分钟无交互 —— 闭眼弧 + 小圆嘴 + Zzz + 呼吸放缓，
                并钻进一颗有立体感的透明泡泡里（渐变泡泡壁 + 高光 + 聚光弧，
                周围缀几颗轻轻漂浮的小泡泡；设定：爱好在泡泡里睡觉），
                醒来时泡泡"啵"地破成一圈小泡泡
   两层「叠加式」表情图层，可与上面任意状态共存：
     · 饥饿层（饱食度 < 30，hungry_amt）：全身以脚底为支点压扁 15%（软趴），
      叶子向一侧耷拉转枯，波浪嘴 + 口水，每 3 秒咕咕叫，每 10 秒头顶飘一朵
      海市蜃楼（云里的牛奶吐司 + 热气）2 秒后啵地破灭，跟着叹一口气
       + 泪花 + 汗滴 + 肚子咕咕声波/音符 + 头顶面包幻想气泡（2s 后"啵"地破灭）
       + 身体下沉、尾巴无力、悬停时努力抬头；此期间不再触发惊讶/庆祝/散步
     · 睡眠层（sleep_amt）：闭眼弧与 ω 嘴 ⇄ 小圆嘴的交叉渐显
     · 可怜层（屏幕上有面包渣，_pity）：视线锁定残渣 + 表情复用 angry
       （倒 V 怒眉 + 生气撇嘴 + 人中小竖线；原委屈眼上眼穹顶已删除）

三、互动（左键落点分区：尾巴 > 头部 > 身体）
     · 摸头（头部）        开心 + 爱心 + 台词 + 摸头计数；
                           **4 秒内连摸第 5 下翻脸** → 傲娇躲避（见 shy 状态）
     · 喂面包（身体单击）  张嘴 → 面包飞入口 → 饱食度 +35 → 吃货台词；
                           饱食度 <99 永远吃得进去（65~99 喂完正好 100）
     · 拖拽投喂            菜单「拿起面包」后，面包跟着光标走（小面包窗口）；
                           拖到嘴边松手，面包**从松手那个点**飞进嘴吃掉；
                           落别处就掉地上 —— 留下一小块残渣（独立透明小窗
                           Crumb，停在落点下方、弹两下落定、留 5 秒再淡出），
                           EJEE 的视线会被它吸走，眼巴巴地盯着看
     · 吃饱再喂            饱食度 ≥99 再喂 → **摇头拒收**：脸左右甩三下
                           （_nod_offset）+ 肚皮鼓起来 + 「嗝～」+ 圆形泡泡框
                           台词，鼓肚持续 6 秒；这期间连点只小幅鼓一下，不刷屏
     · 抓尾巴（尾部）      恶作剧：蓄力压扁 → 猛地弹开 → 尾尖 360° 全方向
                           喷 28~38 滴橘子汁（速度 500~940 设计 px/s，受重力
                           走抛物线），由全屏特效层 JuiceOverlay 绘制——不受
                           宠物窗口边界限制，汁水可飞满整块屏幕；按生命期自然
                           淡出，不再撞内沿挂水渍；喷完沿屏幕边「略略略」溜走
                           130px 再回落
     · 拖拽                随速度倾斜 / 体积守恒拉伸，松手惯性滑行撞墙回弹；
                           拖到屏幕边缘会被激怒（波浪边气鼓框台词）；
                           2.6 秒内在边缘来回换 4 次方向 → 晕车（见 dizzy）
     · 双击                尺寸复位 1.0x（并撤销这次双击第一击挂起的喂食）
     · Shift + 滚轮        缩放 0.5x ~ 3.0x（以光标为锚点，弹簧缓动）
     · 右键                奶油卡片菜单（见「五」）
     · 悬停                唤醒睡眠；饥饿时会眼巴巴跟着鼠标抬头

四、陪伴功能
     · 多形态气泡          框型 + 皮肤随情绪切换（主题表 BUBBLE_THEMES，
                           解析见 _bubble_theme）：
                           cloud 奶油云泡泡（日常/摸头/喂食/问候/闲聊；
                                 手绘感圆角框，四边极轻起伏）
                           · burst 波浪边"气鼓"框（生气/被打扰）
                           · round 圆形泡泡框（打嗝/拒食，会轻轻呼吸）
                           · zzz 睡泡泡里的 Zzz（睡眠）
                           状态皮肤：傲娇粉+小爱心 · 果汁橙+挂汁滴 ·
                           晕车浅绿+整框摇摆 · 可怜蓝+挂泪滴
                           统一幼圆字体（生气用加粗硬体）+ 上亮下沉渐变
                           + 左上高光 + easeOutBack 弹性放大淡入/淡出
     · 台词库              lines.json（可自由扩写，缺失回落到 DEFAULT_LINES）；
                           时段分桶 morning/noon/afternoon/evening/night，
                           另有 feed/pet/angry/hungry/drag/zoom/double_click/
                           mischief/stuffed/stuffing/runaway/sleep_in/
                           shy/dizzy/no_more/crumb 等池
     · 记性                昼夜问候（跨天说早安/晚安）、久别重逢的第一句、
                           陪伴档案（右键 / 托盘菜单：陪伴天数/喂食/摸头/
                           当前饱食度）、喂食与摸头计数（存档累计）
     · 自言自语            30~60s 随机微表情（惊讶 / 庆祝），10% 概率顺带说一句
     · 饱食度              100→0 恰好 3 小时且越低掉得越快（解析解 _hunger_after）；
                           离线按同一公式补扣；<30 开始闹饿（4~7 分钟提醒一次）
     · 番茄钟              菜单唯一入口「开始番茄钟…」：点了先弹时长卡片
                           （15/25/45/60/90 预设胶囊 + ±5 步进，1~180 任意值），
                           确认即开始并记档；跑着再点一下取消。倒计时牌左侧的
                           进度圈随专注推进；最后一分钟牌子转暖红、秒数闪烁、
                           身体轻微发抖、眼睛瞪大（紧张又期待）；到点撒彩纸 + 提示音

五、菜单（窗口右键 / 穿透模式右键 / 托盘，共用同一套奶油卡片皮肤）
    窗口右键：拿起面包（拖到嘴边） · 陪伴档案 · 开始番茄钟…（点击选时长）
              · 穿透模式（胶囊开关）· 尺寸 ›（单选圆点）· 退出
    托盘菜单：另有 显示 / 隐藏、开机自动启动
    卡片外圈柔影、圆角、渐变奶油底、矢量小图标全部自绘；点「开始番茄钟…」
    弹出同皮肤的 PomoDialog 时长卡片（预设胶囊 + ±5 步进 + 取消/开始）。
    （「喂面包」已从菜单移除——喂食请直接点身体，或「拿起面包」拖到嘴边）

六、穿透模式
    OS 级点击穿透（WindowTransparentForInput）+ 半透明透视（淡至 0.30），
    右键由 WH_MOUSE_LL 全局钩子接管——此时窗口本身已收不到任何鼠标事件，
    该钩子同时接管 Shift+滚轮缩放（光标压在宠物身上 + 按住 Shift 滚轮），
    穿透状态下也能调整大小。

七、自由散步
    沿屏幕四周「边框带」环行（窗沿距屏幕边 26~150px）：预生成整圈密集航点，
    结构上不可能横穿屏幕中央；每段走 600~1400px 后到站张望、休息 25~50s；
    朝向按移动方向自动镜像（原图头朝左，向右走时整体水平翻转）。
    游动姿态：停着时只有呼吸，走起来叠加「一拱一拱」的浮沉（相位按走过的
    距离推进，尾巴摆得更欢），转弯时身体顺着转向倾斜；恶作剧后还会沿边
    迅速溜走一小段。

八、资源与存档（源码运行为脚本同级的 assets/ 目录；打包后与 exe 同目录）
    assets/base.png        底图（ω 洞与嘴角已修补干净）
    assets/eye_l/r.png     眼睛精灵（月牙已实心化：大白月牙 + 小黄弯月）
    assets/mouth.png       ω 嘴精灵（周围半透明残留已清理）
    assets/coords.json     眼睛定位；assets/lines.json 台词库；
                           assets/ejee_icon.png 托盘图标
    ejee_save.json  存档：size / last_seen / greet_day / fed / pets /
                    hunger / pomo_min / first_seen（首次启动日期，算陪伴
                    天数）/ x, y（窗口位置，重启后回到原处）
   （Crumb 残渣是运行期临时生成的透明小窗，不落盘、退出时统一 stop）

九、绘制约定（改代码前必读）
    · 设计坐标 DW,DH = 400×400；s = width/DW；
      （画布下方多出的 60px 只给睡眠正圆泡泡用，角色位置不变）
      底图锚点 translate(BCX,BCY) = (195,318)；
      CHAR_W = 292 ≠ DW —— 底图 1548px 只映射成 292 设计 px，
      角色实际占 x 49..341、y 85..318（换算一律用 self.s / self.bw / self.bh）
    · 情绪参数表 P 每个 key 一根弹簧（SPRING_K），paintEvent 只读 cur 快照
    · 所有动效由 _tick()（33ms ≈ 30fps）推进，粒子统一放 self.particles
    · ω 嘴是精灵 + 矢量混合：换嘴时 ω 按 (1-fade*4) 快出，避免新旧嘴形叠影
    · 尾巴是右侧竖长瓣：上半段 y<266 与身体融合、下半段可摆
      （TAIL_RECT 切成 4 条水平条带各自位移，顶带不动故不会裂缝）
    · 身体组内做 facing 镜像；气泡 / 倒计时牌 / 乌云画在组外，不受翻转影响
    · paintEvent 只做编排，具体分给 _draw_shadow / _apply_body_pose /
      _draw_body / _draw_eyes / _draw_mouth / _draw_fantasy / _draw_foreground，
      一帧共享量放在 _frame_ctx()（弹簧快照/视线/表情显形度），避免重复计算
    · 底图/尾巴/眼睛按当前缩放档缓存预缩放 pixmap（_cache_pm），
      避免每帧从 1548×1236 的原图重采样
    · --shot 预览模式会冻结视线并固定随机种子（PREVIEW_MODE），
      所以每次渲染完全一致，改代码前后可以逐像素比对

十、代码结构
    Spring / Particle          弹簧积分与粒子物理
    SoftMenu / PomoDialog      奶油卡片菜单、番茄钟时长选择弹窗（开始前选时长）
    BreadCursor                拖拽投喂的「手里的面包」（跟随光标的小窗口）
    Crumb                      掉在地上的面包渣小窗（独立顶层，鼠标穿透）
    EjeePet.paintEvent         绘制编排（阴影 → 身体组 → 组外前景）
    EjeePet._draw_*            分块绘制：body / eyes / mouth / fantasy / foreground
    EjeePet._tick              唯一的时间推进（情绪、物理、粒子、散步、番茄钟）
    EjeePet._decide_state      状态优先级仲裁
    EjeePet._click_zone        点击热区（尾巴胶囊 / 头部 / 身体）
    EjeePet.feed / _take_bread 喂食（含"吃撑"判定）与拖拽投喂
"""
import json
import math
import os
import random
import sys
import time
from PIL import Image, ImageChops, ImageDraw

from PySide6.QtCore import (Qt, QTimer, QPointF, QRectF, QElapsedTimer,
                            QPoint, Signal)
from PySide6.QtGui import (QPainter, QColor, QPen, QBrush, QPainterPath,
                           QFont, QPixmap, QIcon, QCursor, QImage,
                           QLinearGradient, QRadialGradient)
from PySide6.QtWidgets import (QApplication, QWidget, QSystemTrayIcon, QMenu,
                               QDialog, QLabel, QPushButton,
                               QVBoxLayout, QHBoxLayout)

APP_DIR = os.path.dirname(os.path.abspath(__file__))
if getattr(sys, "frozen", False):
    APP_DIR = os.path.dirname(sys.executable)      # exe 所在目录（可写）
SAVE_PATH = os.path.join(APP_DIR, "ejee_save.json")
PREVIEW_DIR = os.path.join(APP_DIR, "previews")   # --shot 预览图输出目录


def res_path(name):
    """资源定位：PyInstaller onefile 下解包到 sys._MEIPASS（打包时置于根目录）；
    源码运行时优先取脚本同级的 assets/ 子目录，兼容旧的「资源与脚本同级」布局。"""
    base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    p = os.path.join(base, name)
    if os.path.exists(p):
        return p
    alt = os.path.join(base, "assets", name)
    return alt if os.path.exists(alt) else p


def load_save():
    d = {"size": 1.0, "last_seen": 0.0, "greet_day": "", "fed": 0, "pets": 0,
         "hunger": 80.0, "pomo_min": POMO_MIN_DEF, "first_seen": "",
         "x": None, "y": None}
    try:
        with open(SAVE_PATH, "r", encoding="utf-8") as f:
            d.update(json.load(f))
    except Exception:
        pass
    return d


# 台词库：优先读外置 lines.json（可自定义），缺失时用内置默认
DEFAULT_LINES = {
    "morning": ["早上好呀！今天也一起加油。", "早安！记得吃早饭哦。",
                "新的一天，元气满满！",
                "吧嗒吧嗒——日山的湖水公园，今天也很热闹哦。",
                "早上好～我在泡泡里做了个梦，梦里有牛奶吐司。"],
    "noon": ["中午好，别忘了吃饭。", "午安～趴一会儿也不错。",
             "吧嗒吧嗒～午后的泡泡最舒服了。"],
    "afternoon": ["下午好，摸摸我更有干劲。", "无聊的话就看看天空吧。",
                  "下午茶时间到啦？",
                  "下午的阳光照进泡泡里，暖暖的。"],
    "evening": ["晚上好，今天辛苦啦。", "晚饭吃了嘛？",
                "夜晚的屏幕别开太亮哦。",
                "天黑啦，日山湖水公园的灯也一盏盏亮起来了。"],
    "night": ["夜深了，早点休息哦。", "这么晚还在忙呀？注意身体。",
              "星星都困了，你也快睡吧。",
              "吧嗒……吧嗒……我快要在泡泡里睡着啦……"],
    "pet": ["最喜欢摸头了！", "咕噜咕噜～", "好舒服呀～",
            "嘿嘿，被你摸到了。", "再摸一下也可以哦。",
            "吧嗒吧嗒～最喜欢你啦。"],
    "feed": ["牛奶吐司最好吃！", "谢谢投喂！", "唔，好幸福……", "还想再来一个！",
             "松松软软的牛奶吐司，是我的最爱！"],
    "angry": ["呜！尾巴不可以抓！", "生气了！哼！", "尾巴是我的宝贝！"],
    "hungry": ["肚子有点饿了……", "好想吃牛奶吐司呀……", "咕咕叫了，听到没？",
               "闻到吐司味了吗？我饿了。"],
    "pomo_start": ["开始专注！我陪着你。", "专心一会儿，冲鸭！"],
    "pomo_done": ["专注完成，休息一下吧！", "好棒！去喝口水休息下。"],
    "drag": ["哇啊啊——飞起来啦！", "你要带我去哪里？"],
    "zoom": ["变大啦！", "这个尺寸刚刚好！"],
    "double_click": ["砰！回到原样啦！", "还是这个大小最舒服。"],
    "mischief": ["嘿嘿，中计了吧！", "尝尝我的橘子汁攻击！"],
    "stuffed": ["吃不下了……嗝。", "肚子圆圆的，让我歇一会儿嘛。",
                "再吃就要变成橘子了……"],
    "stuffing": ["嗝——！吃撑了，先不吃了……", "唔，好饱，肚子鼓起来了。"],
    "runaway": ["略略略～抓不到我！", "溜了溜了～", "嘿嘿，先跑为敬！"],
    "sleep_in": ["我要钻进泡泡里睡个午觉……", "吧嗒……泡泡裹好啦，晚安……"],
    # 连续摸头 5 下 -> 傲娇躲避
    "shy": ["够、够啦！摸太多次了啦……",
            "哼，摸五下就想把我摸走呀？",
            "不要再摸了啦……我嗖地躲开哦！",
            "什、什么嘛！我的头又不是随便给人摸的！",
            "唔……好啦好啦，第五下了，就这样！",
            "躲到一边！你、你先冷静一下！",
            "再摸我就……我就躲起来了哦。"],
    # 在屏幕边缘被疯狂来回拉扯 -> 晕车
    "dizzy": ["吧嗒吧嗒……别晃啦，我要吐泡泡了！",
              "呜哇——停下来！我的泡泡转起来了……",
              "再晃……再晃真的要吐泡泡啦！",
              "晕、晕车了……你是故意的吧！",
              "眼睛都在转蚊香圈了……停一下嘛，我认输啦。",
              "脑袋里全是你晃来晃去的影子……"],
    # 吃饱了还喂 -> 摇头拒绝
    "no_more": ["摇头摇头——吃饱了，真的吃不下啦！",
                "唔唔，肚子已经圆得装不下了～",
                "不要再塞了啦，会变成橘子的！",
                "左摇右摇——不行不行，够饱够饱！"],
    # 面包掉地上、残渣被盯着看
    "crumb": ["呜……我的面包……",
              "就那么一小块……能不能捡起来嘛。",
              "掉地上了啦……好心疼。",
              "那个……掉地上的面包……还能吃吗……"],
}


def load_lines():
    try:
        with open(res_path("lines.json"), "r", encoding="utf-8") as f:
            d = json.load(f)
        DEFAULT_LINES.update(d)
    except Exception:
        pass
    return DEFAULT_LINES


def save_data(d):
    try:
        with open(SAVE_PATH, "w", encoding="utf-8") as f:
            json.dump(d, f)
    except Exception:
        pass


def clamp(v, lo, hi):
    return max(lo, min(hi, v))


# ---------------- 设计坐标系（400 x 400） ----------------
# 高度 400 而不是 340：角色仍占 y 85..318（底图锚点 BCY 不动），
# 多出来的下方 82px 是留给睡眠状态那颗正圆泡泡的——圆心 (195,201)、
# 半径 188，泡泡下沿 y≈389，只有这样才不会被 widget 边框切平。
# 窗口多出的透明区在落位/拖拽时按 _default_pos 的 pad 补偿，宠物不会悬空。
DW, DH = 400.0, 400.0
DH_CHAR = 340.0     # 角色（含投影）实际用到的画布高度，DH-DH_CHAR 只是给
                    # 睡眠正圆泡泡的透明余量：落位/回位/缩放时不算可见高度
# 散步环带：窗口整体贴近屏幕四周边框（窗沿距边 BAND_NEAR..BAND_FAR px），
# 沿环带边走边不横穿屏幕中央、不挡中间内容
BAND_NEAR = 26.0        # 环带外沿：窗沿距屏幕边最近
BAND_FAR = 150.0        # 环带内沿：窗沿距屏幕边最远
RING_STEP = 46.0        # 环上路径点间距 px

# ------- 色板 -------
BODY_TOP = QColor("#F2A55B")
CREAM = QColor("#FBE8C4")
EYE_DARK = QColor("#3A271E")
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

# ---- 饱食度非线性衰减：100→0 全程 3 小时，数值越低掉得越快 ----
# 速率 r(S) = r0 - c*S（S=100 时 r100，S=0 时 r0=4*r100），
# 由 ∫_0^100 dS/r(S) = HUNGER_FULL_SECONDS 解得 r100 = 100·ln4/(3·T)
HUNGER_FULL_SECONDS = 3 * 3600.0                       # 满 -> 空 的总时长
HUNGER_R100 = 100.0 * math.log(4.0) / (3.0 * HUNGER_FULL_SECONDS)
HUNGER_R0 = 4.0 * HUNGER_R100                          # 空肚时掉得最快
HUNGER_C = (HUNGER_R0 - HUNGER_R100) / 100.0

SIZES = [("小", 0.8), ("中", 1.0), ("大", 1.25), ("特大", 1.5)]
SIZE_MIN, SIZE_MAX = 0.5, 3.0   # Shift+滚轮缩放范围（底图原生 1548px，3x 仍不超采样）
POMO_PRESETS = [15, 25, 45, 60, 90]   # 番茄钟时长预设（分钟）
POMO_MIN_DEF, POMO_MIN_LO, POMO_MIN_HI = 25, 1, 180
# --shot 预览模式：冻结"跟随鼠标"的视线，让预览图每次渲染完全一致
# （否则光标位置会带动身体摇摆/眼睛方向，改一行代码前后的截图没法比对）
PREVIEW_MODE = False
OMEGA_SW = 46.0                 # ω 嘴线宽（mouth.png 实测 base 像素，峰顶竖穿）
OMEGA_COL = "#A34B12"           # ω 嘴线条色（不透明最暗 15% 中位色）
SLEEP_AFTER = 300.0             # 无交互多少秒进入睡眠
# 用户操作引发的状态（恶作剧/晕车/傲娇/睡眠）结束后，先老实回 idle 坐
# 这么久，期间不冒出任何自发状态（随机惊讶/庆祝/散步/闲聊/睡眠都按住），
# 避免一个反应还没看完就紧跟着蹦下一个。
POST_IDLE_SECS = 5.0
USER_STATES = ("mischief", "dizzy", "shy", "sleep")
# 待机自发行为的间隔（比早期版本整体放慢，让"静态待机"更安静）
IDLE_EXPR_EVERY = (30.0, 60.0)      # 随机微表情（惊讶/庆祝）
IDLE_WALK_EVERY = (60.0, 110.0)     # 屏幕边框散步
IDLE_CHATTER_EVERY = (240.0, 480.0)  # 自言自语一句

# 尾巴轻摆：剪切矩形（base 像素）。y>960 只有尾巴大圆与透明背景
# （大圆左缘 x≈1405-1420，前爪右缘 x<1345，矩形左界留 >40px 缓冲）
TAIL_RECT = (1350, 960, 1548, 1236)

# 头顶叶子（设计坐标，由 tools/make_leaf_assets.py 从 base.png 拆出）：
# (左上 x, 左上 y, 宽, 高, 轴心 x, 轴心 y)。轴心＝叶柄插入头皮处，
# 饥饿耷拉时绕它旋转，根部不动，接缝不会裂开。
LEAF_GEO = (158.97, 85.0, 51.87, 48.67, 178.59, 132.72)

# ------- 情绪状态参数表（目标值，状态间做指数平滑） -------
# eye_sx/sy 眼睛缩放; eye_dy 眼睛下移; eye_rot 眼睛外角下垂旋转;
# bounce 弹跳幅度; shake 颤抖幅度; sway_amp/period 摇摆; bob 浮动;
# puff 脸颊鼓包(仅驱动怒容眉眼渐显); cloud 乌云; excl 感叹号
P = {
    "idle":      dict(eye_sx=1.0, eye_sy=1.0, eye_dy=0.0, eye_rot=0.0,
                      bounce=0.0, shake=0.0, sway_amp=1.2, sway_per=3.6,
                      bob=2.5, puff=0.0, cloud=0.0, excl=0.0),
    "happy":     dict(eye_sx=1.0, eye_sy=0.45, eye_dy=-2.0, eye_rot=0.0,
                      bounce=9.0, shake=0.0, sway_amp=0.8, sway_per=2.2,
                      bob=1.0, puff=0.0, cloud=0.0, excl=0.0),
    "angry":     dict(eye_sx=1.0, eye_sy=1.0, eye_dy=1.0, eye_rot=0.0,
                      bounce=0.0, shake=1.6, sway_amp=0.3, sway_per=3.6,
                      bob=0.8, puff=1.0, cloud=1.0, excl=0.0),
    "surprised": dict(eye_sx=1.18, eye_sy=1.18, eye_dy=-1.0, eye_rot=0.0,
                      bounce=0.0, shake=0.0, sway_amp=0.4, sway_per=3.6,
                      bob=1.2, puff=0.0, cloud=0.0, excl=1.0),
    # 睡眠：闭眼 + 呼吸起伏加大 + 极慢摇摆（优先级最低，5 分钟无交互进入）
    "sleep":     dict(eye_sx=1.0, eye_sy=0.06, eye_dy=3.0, eye_rot=0.0,
                      bounce=0.0, shake=0.0, sway_amp=0.5, sway_per=7.5,
                      bob=5.5, puff=0.0, cloud=0.0, excl=0.0),
    # 恶作剧：抓尾巴触发（最高优先级），坏笑眼+吐舌头由矢量叠加另画
    "mischief":  dict(eye_sx=1.02, eye_sy=0.74, eye_dy=-1.0, eye_rot=0.0,
                      bounce=0.0, shake=0.0, sway_amp=0.7, sway_per=2.4,
                      bob=2.2, puff=0.0, cloud=0.0, excl=0.0),
    # 傲娇躲避（连摸 5 下）：半眯眼别过头 + 直接闪现到屏幕另一侧（无身体形变）
    "shy":       dict(eye_sx=0.98, eye_sy=0.62, eye_dy=1.6, eye_rot=0.0,
                      bounce=0.0, shake=0.0, sway_amp=0.2, sway_per=2.6,
                      bob=1.4, puff=0.0, cloud=0.0, excl=0.0),
    # 晕车（边缘疯狂拉扯）：蚊香圈眼由 _draw_eyes 叠画，这里只管轻微摇晃
    "dizzy":     dict(eye_sx=1.0, eye_sy=1.0, eye_dy=0.0, eye_rot=0.0,
                      bounce=0.0, shake=0.0, sway_amp=0.6, sway_per=4.4,
                      bob=3.0, puff=0.0, cloud=0.0, excl=0.0),
}

# 各参数的弹簧刚度/阻尼（ζ = d/(2√k)：<1 欠阻尼回弹，越小越 Q 弹）
SPRING_K = {
    "eye_sx": (210, 15), "eye_sy": (210, 15), "eye_dy": (170, 13),
    "eye_rot": (120, 12),
    "bounce": (260, 15),
    "shake": (300, 22),
    "sway_amp": (80, 12), "sway_per": (60, 14),
    "bob": (80, 11),
    "puff": (110, 9),        # 腮帮鼓起带弹性
    "cloud": (90, 10),
    "excl": (140, 8.5),      # 感叹号弹跳入场
}


class Spring:
    """欠阻尼弹簧：value 以速度逼近 target，自带惯性、回弹与 Overshoot。
    半隐式欧拉积分，子步进保证数值稳定。"""
    __slots__ = ("v", "vel", "k", "d")

    def __init__(self, value, k=150.0, d=16.0):
        self.v = float(value)
        self.vel = 0.0
        self.k = k              # 刚度
        self.d = d              # 阻尼（d/(2*sqrt(k)) < 1 时欠阻尼回弹）

    def snap(self, value):
        self.v = float(value)
        self.vel = 0.0

    def kick(self, dv):
        self.vel += dv

    def step(self, target, dt):
        n = max(1, int(dt / 0.008))
        h = dt / n
        for _ in range(n):
            acc = (target - self.v) * self.k - self.vel * self.d
            self.vel += acc * h
            self.v += self.vel * h


class Particle:
    """confetti 彩纸 / heart 爱心 / star 星星 / steam 蒸汽 / bubble 泡泡"""
    __slots__ = ("kind", "x", "y", "vx", "vy", "rot", "vr", "color",
                 "size", "born", "life")

    def __init__(self, kind, x, y, t):
        self.kind = kind
        self.x, self.y = x, y
        self.born = t
        if kind == "confetti":
            ang = random.uniform(-math.pi * 0.92, -math.pi * 0.08)
            sp = random.uniform(150, 330)
            self.vx, self.vy = sp * math.cos(ang), sp * math.sin(ang)
            self.rot = random.uniform(0, 360)
            self.vr = random.uniform(-360, 360)
            self.color = QColor(random.choice(CONFETTI))
            self.size = random.uniform(4, 8)
            self.life = random.uniform(1.6, 2.4)
        elif kind == "heart":
            self.vx = random.uniform(-22, 22)
            self.vy = random.uniform(-95, -60)
            self.rot = random.uniform(-16, 16)
            self.vr = 0.0
            self.color = QColor(random.choice(HEARTS))
            self.size = random.uniform(7, 12)
            self.life = random.uniform(1.4, 2.0)
        elif kind == "star":
            ang = random.uniform(-math.pi * 0.85, -math.pi * 0.15)
            sp = random.uniform(110, 240)
            self.vx, self.vy = sp * math.cos(ang), sp * math.sin(ang)
            self.rot = random.uniform(0, 90)
            self.vr = random.uniform(-240, 240)
            self.color = QColor(random.choice(STARS))
            self.size = random.uniform(5, 9)
            self.life = random.uniform(0.9, 1.4)
        elif kind == "juice":
            # 橘子汁水滴：从尾巴橘子瓣向上喷洒后受重力坠落
            self.vx = random.uniform(-150, 60)
            self.vy = random.uniform(-310, -130)
            self.rot = random.uniform(-14, 14)
            self.vr = 0.0
            self.color = QColor(random.choice(JUICE))
            self.size = random.uniform(3.0, 6.0)
            self.life = random.uniform(0.7, 1.1)
        elif kind == "crumb_dust":
            # 面包碎屑：极小的面包色颗粒，弹一下就落在地上不动了
            self.vx = random.uniform(-28, 28)
            self.vy = random.uniform(-64, -20)
            self.rot = random.uniform(-30, 30)
            self.vr = 0.0
            self.color = QColor(random.choice((238, 186, 120, 214, 160, 96)))
            self.size = random.uniform(1.4, 2.6)
            self.life = random.uniform(0.5, 0.9)
        elif kind == "zzz":
            # 睡眠 Z 字：慢速右上漂 + 轻微摆动（绘制时按 age 加 wobble）
            self.vx = random.uniform(6, 14)
            self.vy = random.uniform(-26, -18)
            self.rot = random.uniform(0, 6.28)   # 用作摆动相位
            self.vr = 0.0
            self.color = QColor(150, 170, 200)
            self.size = random.uniform(9, 14)
            self.life = random.uniform(2.4, 3.2)
        elif kind == "sweat":
            # 饥饿汗滴：从太阳穴缓缓滑落，轻微外斜
            self.vx = random.uniform(-5, 5)
            self.vy = random.uniform(16, 30)
            self.rot = random.uniform(-0.22, 0.22)   # 用作倾斜角（弧度）
            self.vr = 0.0
            self.color = QColor(158, 205, 235)
            self.size = random.uniform(4.4, 6.4)
            self.life = random.uniform(1.0, 1.4)
        elif kind in ("rumble", "note"):
            # 肚子咕咕叫：从肚皮冒出的声波纹/音符，缓慢上浮
            self.vx = random.uniform(-3, 3)
            self.vy = random.uniform(-14, -9)
            self.rot = random.uniform(0, 6.28)   # 用作摆动相位
            self.vr = 0.0
            self.color = QColor(172, 190, 214)
            self.size = random.uniform(0.9, 1.1)  # 缩放系数
            self.life = random.uniform(1.5, 1.9)
        else:  # steam
            self.vx = random.uniform(-8, 8)
            self.vy = random.uniform(-46, -30)
            self.rot = 0.0
            self.vr = 0.0
            self.color = QColor(200, 208, 218)
            self.size = random.uniform(5, 9)
            self.life = random.uniform(1.3, 1.9)
        # 泡泡：缓慢上浮 + 横向摆动（绘制时按 age 加 wobble）
        if kind == "bubble":
            self.vx = random.uniform(-6, 6)
            self.vy = random.uniform(-34, -22)
            self.rot = random.uniform(0, 360)   # 用作摆动相位
            self.vr = 0.0
            self.color = QColor(214, 234, 248)
            self.size = random.uniform(4, 8)
            self.life = random.uniform(2.2, 3.2)


# ============================================================
# 右键菜单：暖奶油手绘风卡片（自绘柔影 + 圆角 + QSS 条目 + 矢量小图标）
# ============================================================
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

    def refresh(self, pet):
        """每帧把宠物身上的汁滴换算成全局坐标；没有汁滴就自动隐藏。"""
        s = pet.width() / DW
        items = []
        for pt in pet.particles:
            if pt.kind != "juice":
                continue
            age = pet.t - pt.born
            if age < 0.0 or age >= pt.life:
                continue
            a = clamp(1.0 - age / pt.life, 0.0, 1.0)
            g = pet.mapToGlobal(QPoint(int(pt.x * s), int(pt.y * s)))
            items.append((g.x(), g.y(), pt.size * s, a, age, pt.color))
        self._items = items
        if items:
            if not self.isVisible():
                self._place()
                self.show()
            self.update()
        elif self.isVisible():
            self.hide()

    def paintEvent(self, e):
        if not self._items:
            return
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing, True)
        ox, oy = self.x(), self.y()
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


class EjeePet(QWidget):
    # ---------- 布局常量（设计坐标） ----------
    CHAR_W = 292.0
    BCX, BCY = 195.0, 318.0          # 底图底部中心锚点

    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint |
                            Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setMouseTracking(True)      # 悬停唤醒睡眠（mouseMoveEvent）

        data = load_save()
        self.size = clamp(float(data.get("size", 1.0)), SIZE_MIN, SIZE_MAX)
        self.resize(int(DW * self.size), int(DH * self.size))

        # ---- 记性（昼夜节律/陪伴统计）----
        self._meta = {"last_seen": float(data.get("last_seen") or 0.0),
                      "greet_day": str(data.get("greet_day", "")),
                      "fed": int(data.get("fed", 0)),
                      "pets": int(data.get("pets", 0)),
                      "first_seen": str(data.get("first_seen") or "")}
        if not self._meta["first_seen"]:
            # 首次启动（或旧存档迁移）：把今天记为相识日，立刻落盘
            self._meta["first_seen"] = time.strftime("%Y-%m-%d")
            self._save()
        try:
            self._restore_pos = (int(data["x"]), int(data["y"]))
        except (KeyError, TypeError, ValueError):
            self._restore_pos = None      # 没有（或非法）历史位置 -> 默认位
        self._save_t = 0.0            # 周期性存档节流
        self._lines = load_lines()
        self._next_chatter = random.uniform(*IDLE_CHATTER_EVERY)   # 首次闲聊 1.5-3 分钟后
        self._pomo_end = None         # 番茄钟结束时刻（self.t 基准）
        self._pomo_txt_t = 0.0        # 托盘倒计时文案节流
        self._pomo_total = 25 * 60.0  # 本段番茄钟总时长（进度环用）
        self._pomo_nrv = Spring(0.0, 90, 12)   # 最后一分钟的紧张度 0..1
        self._sleeping_prev = False           # 上一帧是否在睡（醒来泡泡破掉）
        self._tag_dy = Spring(0.0, 110, 13)    # 有气泡时倒计时牌下移避让
        try:
            self._meta["pomo_min"] = int(clamp(
                int(data.get("pomo_min", POMO_MIN_DEF)), POMO_MIN_LO, POMO_MIN_HI))
        except (TypeError, ValueError):
            self._meta["pomo_min"] = POMO_MIN_DEF

        # ---- 自由走动（第二档⑤）：idle 沿屏幕底边散步 ----
        self.facing = 1               # 朝向：1 向右 / -1 向左（绘制镜像）
        self._wander = None           # {"tx": 目标窗口左上x, "until": 到站停留截止}
        self._next_walk = random.uniform(*IDLE_WALK_EVERY)   # 首次散步时刻
        self._walk_speed = 88.0       # 移动速度 px/s
        self._ring_phase = random.uniform(0.0, math.tau)  # 环带深度正弦相位

        # ---- 轻量饱食度（第二档⑥）：无惩罚，饿了会提醒 ----
        self._meta["hunger"] = self._load_hunger(data)
        self._next_hungry = random.uniform(60, 120)

        # ---- Shift+滚轮 缩放（弹簧缓动 + 光标锚点）----
        self.target_size = self.size
        self._size_spring = Spring(self.size, 90, 12)   # ζ≈1 临界阻尼，无过冲
        self._zoom_anchor = None    # 冻结锚点 (设计x, 设计y, 全局光标QPoint)
        self._zooming = False
        # ---- 双击重置：单击喂食延迟派发，双击时撤单 ----
        self._feed_pending = False
        self._feed_deadline = 0.0       # 排队中的喂食最晚等到这一刻（不丢点击）
        self._dbl_until = 0.0
        self._bread = None            # 手里的面包（BreadCursor，拖拽投喂）
        self._stuffed_until = 0.0     # 吃撑了：这段时间内肚皮鼓着、拒绝再吃
        self._stuffed = Spring(0.0, 90, 12)   # 鼓肚显形度 0..1
        self._feed_from = None           # 拖拽投喂时面包的起飞点（设计坐标）
        self._crumbs = []                # 掉在地上的面包渣（Crumb 小窗列表）
        self._pity = Spring(0.0, 70, 12)     # 可怜眼神显形度（盯着残渣时）
        # ---- 傲娇躲避（连摸 5 下）----
        self._pat_n = 0                     # 摸头连击数（4 秒窗口）
        self._pat_last = -99.0
        self._shy_until = 0.0               # 傲娇躲避结束时刻
        self._shy_dir = (1.0, 0.0)          # 躲开方向（单位向量）
        self._shy_amt = Spring(0.0, 130, 11)  # 缩身显形度 0..1
        # ---- 晕车（边缘被疯狂拉扯）----
        self._dizzy_until = 0.0
        self._dizzy_amt = Spring(0.0, 100, 13)  # 晕车显形度 0..1
        self._dizzy_fx = 0.0             # 晕车吐泡泡的独立计时器
        self._shake_log = []                # 边缘往返记录 [(时刻, 方向)]
        # ---- 摇头拒绝（吃饱还喂）----
        self._nod_until = 0.0               # 摇头结束时刻
        self._nod_dur = 1.15                # 一次摇头持续时长
        self._nod_n = 0                     # 已摇头次数（决定幅度）

        self.clock = QElapsedTimer()
        self.clock.start()
        self.t = 0.0
        self._last_t = 0.0

        # 橘子汁特效层（全局坐标绘制，可飞出宠物窗口；无汁滴时自动隐藏）
        self._juice_fx = JuiceOverlay(self)

        # ---- 情绪状态机 ----
        self.state = "idle"
        self.state_t0 = 0.0
        self.spr = {key: Spring(P["idle"][key], *SPRING_K[key])
                    for key in P["idle"]}
        self.cur = dict(P["idle"])            # 当前参数快照（弹簧值）
        # 挤压拉伸 / 拖拽倾斜 / 惯性滑行 / 微动作
        self._sq = Spring(0.0, 230, 9)        # squash&stretch（Q 弹）
        self._tilt = Spring(0.0, 120, 14)     # 拖拽方向倾斜
        self.mouth_alt = Spring(0.0, 110, 13)  # 替代嘴形显形度 0..1（0=ω 原嘴）
        self.sleep_amt = Spring(0.0, 110, 13)  # 睡眠表情显形度 0..1（闭眼弧+小圆嘴）
        self.hungry_amt = Spring(0.0, 90, 12)  # 饥饿表情显形度 0..1（垂眼+波浪嘴+汗）
        self.mischief_amt = Spring(0.0, 120, 13)  # 恶作剧表情显形度 0..1
        self.mischief_until = 0.0     # 恶作剧结束时刻（最高优先级状态）
        self._mis_tail = Spring(0.0, 90, 11)  # 尾巴甩动量（触发 snap(1) 自然衰减）
        self._flee = None                     # 恶作剧后的逃跑（{dx,dy,left}）
        self._fled = False
        # 游泳姿态：散步时身体一拱一拱地浮沉、转弯时略微倾斜
        self._swim = Spring(0.0, 70, 12)      # 游泳强度 0..1（起走/停下平滑过渡）
        self._swim_ph = 0.0                   # 浮沉相位（按走过的距离推进）
        self._turn = Spring(0.0, 130, 13)     # 转弯倾斜角（度）
        self._turn_t = 0.0                    # 倾斜目标，指数衰减回 0
        self._heading = None                  # 上一帧的移动方向（弧度）
        self._mis_puff = 0.0          # 蓄力后"猛地弹开"的时刻
        self._mis_dir = 1.0           # 尾巴甩向（+1 右 / -1 左）
        self._hover = False          # 鼠标是否悬停在身上
        self._hover_amt = Spring(0.0, 70, 12)  # 悬停抬头量（饿了看到鼠标努力抬头）
        self._breathe_ph = random.uniform(0.0, 6.28)   # 呼吸相位累积器（可变速）
        self._tail_ph = random.uniform(0.0, 6.28)      # 尾摆相位累积器（可变速）
        self._rumble_i = 0           # 咕咕叫轮次（波浪/音符交替）
        self._fantasy = None         # 幻想气泡 {"t0": 开始时刻}
        self._next_fantasy = random.uniform(5.0, 8.0)
        # 叹气：每次海市蜃楼破灭后来一下（身体一沉 + 眼睛半闭）
        self._sigh_t0 = -99.0
        self._sigh_dur = 1.25
        self.wink_l = Spring(0.0, 110, 13)     # 左眼眯眼弧（happy/surprised 眨眼）
        self.wink_r = Spring(0.0, 110, 13)     # 右眼眯眼弧（happy 双眼闭）
        # 视线平滑：raw 视线（鼠标/残渣/张望）每帧重算、可能突变，
        # 这里用弹簧缓动，避免掉面包渣等瞬间眼睛"啪"地甩过去 / 身体猛摆
        self._gvx = Spring(0.0, 130, 17)
        self._gvy = Spring(0.0, 130, 17)
        self._dvx = 0.0                       # 拖拽水平速度 px/s
        self._dvy = 0.0
        self._last_move_t = 0.0
        self._glide = None                    # 松手惯性滑行 [vx, vy]
        self._next_micro = random.uniform(6, 14)
        self._look_until = 0.0
        self._look_dir = 0.0
        self.angry_until = -1.0
        self.surprised_until = -1.0
        self.surprised_cd = 0.0
        self._celebrate_until = -1.0         # 待机随机庆祝微表情截止时刻
        self._post_lock = 0.0                # 用户状态结束后强制 idle 的截止时刻
        self._next_expr = random.uniform(*IDLE_EXPR_EVERY)  # 下一次随机微表情
        self.last_interact = 0.0             # 最近一次交互（睡眠判定）
        self._wake2 = False                  # 伸懒腰两段进度
        self._fx_timer = 0.0
        self._fx_timer2 = 3.2         # 咕咕叫计时（每 3 秒出头一声）

        # 眨眼
        self.next_blink = self._rand_blink_delay()
        self.blink_t0 = None
        self.blink_pending2 = False

        # 互动（happy 子相位）：idle -> bread（张嘴→吞入→闭嘴）
        self.phase = "idle"
        self.phase_t0 = 0.0

        self.bubble_text = ""
        self.bubble_until = 0.0
        self.bubble_t0 = 0.0         # 本条气泡出生时刻（驱动入场/退场动画）
        self.bubble_style = "cloud"  # 框型：cloud/burst/round/zzz
        self._next_drag_line = 0.0   # 拖拽台词冷却
        self._next_zoom_line = 0.0   # 缩放台词冷却
        self._zoom_from = 1.0        # 本次缩放手势起始尺寸
        self.particles = []
        self.floats = []

        # 拖拽
        self._press_pos = None
        self._dragging = False

        self.timer = QTimer(self)
        self.timer.timeout.connect(self._tick)
        self.timer.start(33)

        self._pass = False                   # 穿透模式开关
        self._mouse_hook = None              # 穿透模式全局鼠标钩子句柄（右键+滚轮）
        self._hook_proc = None               # 钩子回调引用（防 GC）
        self._opac = Spring(1.0, 90, 12)     # 穿透模式透明度弹簧
        self._load_assets()
        self._init_tray()
        # 开屏问候：等窗口显示后再冒气泡（1.2s 延迟）
        QTimer.singleShot(1200, self._maybe_greet)

    @staticmethod
    def _hunger_after(s0, dt):
        """饱食度非线性衰减：速率随数值降低线性加快（0 时是 100 时的
        4 倍），100→0 全程恰好 HUNGER_FULL_SECONDS（3 小时）；
        dt 大（离线补扣）也精确。dS/dt = -(r0 - c·S) 的解析解。"""
        s0 = clamp(s0, 0.0, 100.0)
        return (HUNGER_R0 - (HUNGER_R0 - HUNGER_C * s0)
                * math.exp(HUNGER_C * dt)) / HUNGER_C

    def _load_hunger(self, data):
        """饱食度 0-100，离线按同一非线性模型补扣。"""
        h = float(data.get("hunger", 80.0))
        last = float(data.get("last_seen") or 0.0)
        if last > 0:
            h = self._hunger_after(h, time.time() - last)
        return clamp(h, 0.0, 100.0)

    # ================= 陪伴：问候 / 闲聊 / 番茄钟 =================
    @staticmethod
    def _bucket():
        h = time.localtime().tm_hour
        if 5 <= h < 11:
            return "morning"
        if 11 <= h < 14:
            return "noon"
        if 14 <= h < 18:
            return "afternoon"
        if 18 <= h < 23:
            return "evening"
        return "night"

    def _line(self, key):
        pool = self._lines.get(key) or DEFAULT_LINES.get(key) or [""]
        return random.choice(pool)

    def _say(self, text, dur=3.0, style="cloud"):
        """统一气泡入口：记录出生时刻，供入场弹跳/淡入与到点淡出动画用。

        style 决定气泡的框型（皮肤由 _bubble_theme 按当前状态再细化）：
          cloud  默认云朵框（日常 / 摸头 / 喂食 / 闲聊）
          burst  波浪边的"气鼓"框（生气、被打扰）
          round  圆形泡泡框（打嗝、吃饱满足）
          zzz    睡泡泡里的 Zzz（睡眠：三只小泡泡各坐一个 Z）
        """
        self.bubble_text = text
        self.bubble_t0 = self.t
        self.bubble_until = self.t + dur
        self.bubble_style = style
        # 短促的情绪台词更贴合的框型自动改写（只改框不改词）
        if style == "cloud":
            if self.state == "angry":
                self.bubble_style = "burst"
            elif self.state == "sleep":
                self.bubble_style = "zzz"

    def _maybe_greet(self):
        """每天首次见面打一声招呼；隔了很久才回来有专属问候。"""
        today = time.strftime("%Y-%m-%d")
        if self._meta.get("greet_day") == today:
            return
        self._meta["greet_day"] = today
        self._save()
        gap = time.time() - self._meta.get("last_seen", 0.0)
        text = self._line(self._bucket())
        if gap > 10 * 3600 and self._meta.get("last_seen", 0) > 0:
            text = "你终于回来了！" + text
        self._say(text, 3.6)

    def _companion_days(self):
        """陪伴天数：从 first_seen（相识日）到今天，最少算 1 天。"""
        fs = self._meta.get("first_seen", "")
        try:
            d0 = time.strptime(fs, "%Y-%m-%d")
        except ValueError:
            return 1
        days = (time.time() - time.mktime(d0)) / 86400.0
        return max(1, int(days) + 1)

    def _show_stats(self):
        """陪伴档案（托盘菜单）：EJEE 用自己的话汇报这些日子的陪伴——
        认识多久、喂过几次、摸过几次、现在肚子什么状况。"""
        self._touch()                       # 睡着也能被点醒看档案
        days = self._companion_days()
        hug = self._meta.get("hunger", 0.0)
        mood = "有点饿了……" if hug < 30.0 else "肚子饱饱的！"
        txt = ("我已经陪你 %d 天啦～\n喂过我 %d 次，摸了我 %d 次。\n"
               "现在饱食度 %d%%，%s"
               % (days, self._meta.get("fed", 0), self._meta.get("pets", 0),
                  int(round(hug)), mood))
        self._say(txt, 6.0)

    def _pat(self):
        """摸头：眯眼开心 + 爱心 + 台词。**连续摸 5 下会被摸烦**——
        进入「傲娇躲避」3 秒：半眯眼别过头、直接闪现到屏幕另一侧（不做身体
        形变、不挪小碎步）、说傲娇台词 + 头顶小蒸汽。"""
        self._touch()
        # ---- 连击计数：4 秒内累计到 5 次就翻脸 ----
        if self.t - self._pat_last < 4.0:
            self._pat_n += 1
        else:
            self._pat_n = 1
        self._pat_last = self.t
        if self._pat_n >= 5:
            self._pat_n = 0
            self._start_shy()
            return
        self._celebrate_until = self.t + 0.9
        self._sq.kick(-0.8)
        self._say(self._line("pet"), 2.4)
        for i in range(2):
            self.particles.append(Particle(
                "heart", self.BCX + random.uniform(-42, 42),
                self.head_top + random.uniform(-2, 14), self.t))
        self._meta["pets"] = self._meta.get("pets", 0) + 1

    def _start_shy(self):
        """傲娇躲避：被连摸 5 下，直接闪现到屏幕另一侧（不做身体形变 /
        小碎步），甩出傲娇台词 + 头顶小蒸汽，3 秒后回 idle。"""
        self._touch()
        self._shy_until = self.t + 3.0
        self._wander = None                  # 别一边躲一边散步
        self._next_walk = self.t + random.uniform(*IDLE_WALK_EVERY)
        # 直接闪现：从当前位置反射到屏幕对侧（环带内），落点带随机扰动
        g = self._scr_rect()
        w, h = self.width(), self.height()
        ocx = self.x() + w / 2.0
        if ocx < g.center().x():
            nx = g.right() - w - BAND_NEAR
        else:
            nx = g.left() + BAND_NEAR
        nx = clamp(nx + random.uniform(-50, 50), g.left() + BAND_NEAR,
                   g.right() - w - BAND_NEAR)
        ny = clamp(self.y() + random.uniform(-90, 90), g.top() + BAND_NEAR,
                   g.bottom() - h - BAND_NEAR)
        self._teleport_flash(ocx, self.y() + h / 2.0, nx + w / 2.0, ny + h / 2.0)
        self._sq.kick(-1.6)
        self._say(self._line("shy"), 2.6)
        # 头顶冒两颗害羞的小蒸汽（不是爱心了，是"别摸啦"的意思）
        for i in range(4):
            self.particles.append(Particle(
                "steam", self.BCX + random.uniform(-46, 46),
                self.head_top + random.uniform(0, 12),
                self.t - i * 0.07))
        # 背对原来的光标所在侧
        m = QCursor.pos()
        dx = (nx + w / 2.0) - m.x()
        self.facing = 1 if dx < 0 else -1

    def _teleport_flash(self, ox, oy, nx, ny):
        """闪现：瞬间从旧位置挪到新位置；在落点甩一小撮蒸汽做"啪"的弹出感。"""
        self.move(int(nx - (self.width() / 2.0)), int(ny - (self.height() / 2.0)))

    def _start_dizzy(self):
        """晕车：被按在屏幕边缘来回疯狂摇晃 —— 蚊香圈眼 + 喊"要吐泡泡了"。
        持续 4.5 秒；期间不再重复触发（等用户松手）。"""
        self._dizzy_until = self.t + 4.5
        self._sq.kick(-1.0)
        self._say(self._line("dizzy"), 3.4, "burst")
        # 先憋一串小泡泡（"我要吐泡泡了"的预告）
        for i in range(5):
            pt = Particle("bubble", self.mouth_center[0]
                          + random.uniform(-24, 24),
                          self.mouth_center[1] - 12, self.t - i * 0.10)
            pt.vx = random.uniform(-20, 20)
            pt.vy = random.uniform(-52, -30)
            self.particles.append(pt)
        # 头顶转圈的星星（晕眩的通用符号）
        for i in range(3):
            pt = Particle("star", self.BCX + random.uniform(-34, 34),
                          self.head_top + random.uniform(-4, 10),
                          self.t - i * 0.09)
            pt.vx = random.uniform(-30, 30)
            pt.vy = random.uniform(-30, -12)

    def _start_flee(self):
        """恶作剧后逃跑：顺着当前贴着的那条屏幕边溜 130px，不横穿屏幕。"""
        g = self._scr_rect()
        w, h = self.width(), self.height()
        cx, cy = self.x() + w / 2.0, self.y() + h / 2.0
        d_l, d_r = cx - g.left(), g.right() - cx
        d_t, d_b = cy - g.top(), g.bottom() - cy
        if min(d_l, d_r) < min(d_t, d_b):        # 贴左右边 -> 竖直溜
            dx, dy = 0.0, (1.0 if d_b >= d_t else -1.0)
        else:                                    # 贴上下边 -> 水平溜
            dx, dy = (1.0 if d_r >= d_l else -1.0), 0.0
        self._wander = None
        self._next_walk = self.t + random.uniform(*IDLE_WALK_EVERY)
        self._flee = {"dx": dx, "dy": dy, "left": 130.0}
        self._sq.kick(-1.4)                      # 起跑先蹲一下
        self._say(self._line("runaway"), 2.0)

    def _mischief(self):
        """抓尾巴 -> 恶作剧：坏笑吐舌 + 蓄力收缩再猛弹开 + 橘子汁朝鼠标喷。
        最高优先级状态，持续 1.5 秒后自然回落 idle。"""
        self._touch()
        self.mischief_until = self.t + 1.5
        self._fled = False                   # 还没溜
        self._flee = None
        self._sq.kick(-2.0)                  # 蓄力收缩
        self._mis_puff = self.t + 0.12       # 0.12s 后猛地弹开（见 _tick）
        self._mis_tail.snap(1.0)             # 尾巴甩动初值，弹簧自然衰减
        self._say(self._line("mischief"), 2.2)
        # 尾巴甩动方向：朝鼠标那一侧甩（纯装饰；汁水本身向四周全方向溅射）
        s = self.width() / DW
        tip = self.mapToGlobal(QPoint(int(340 * s), int(300 * s)))
        m = QCursor.pos()
        ddx, ddy = m.x() - tip.x(), m.y() - tip.y()
        self._mis_dir = 1.0 if ddx >= 0 else -1.0
        # 尾瓣尖（设计绝对坐标；朝左时视觉尾巴在另一侧，按 facing 镜像）
        jx = self.BCX + 145
        jy = self.BCY - 18
        if self.facing == -1:
            jx = 2 * self.BCX - jx
        # 橘子汁向四周溅射（360° 全方向大放送），范围更大更密。
        # 用「等距打底 + 抖动」保证整圈无大空隙（覆盖 >320°），
        # 而不是纯随机（纯随机偶发会留 >40° 空档）。
        n = random.randint(32, 42)
        span = math.tau / n
        for i in range(n):
            ang = span * i + random.uniform(-span * 0.5, span * 0.5)
            sp = random.uniform(500.0, 940.0)          # 设计 px/s（受重力 820 走抛物线）
            pt = Particle("juice", jx + random.uniform(-6.0, 6.0),
                          jy + random.uniform(-6.0, 6.0), self.t)
            pt.vx, pt.vy = sp * math.cos(ang), sp * math.sin(ang)
            pt.size *= random.uniform(1.4, 2.2)
            pt.life *= random.uniform(1.5, 2.1)
            self.particles.append(pt)

    def _pomo_text(self, txt):
        """托盘不可用时静默跳过倒计时文案。"""
        act = getattr(self, "tray_act_pomo", None)
        if act is not None:
            act.setText(txt)

    def _scr_rect(self):
        """宠物当前所在屏幕的可用区域（避开任务栏；多屏取所在屏）。"""
        scr = QApplication.screenAt(self.frameGeometry().center())
        if scr is None:
            scr = QApplication.primaryScreen()
        return scr.availableGeometry()

    def _ring_pts(self):
        """生成一环散步路径点（窗口左上角坐标）：沿屏幕四周边框带走一圈，
        点距约 RING_STEP；深度（窗沿距屏幕边）按环周长正弦缓摆于
        [BAND_NEAR, BAND_FAR-8]，路径圆润自然，且整体不进屏幕中央。"""
        g = self._scr_rect()
        # 底部那块透明余量不算：散步时宠物脚底才真的贴着屏幕边走
        w, h = self.width(), self.height() - self._win_pad_b()
        L, T, R, B = g.left(), g.top(), g.right(), g.bottom()
        x0, y0 = L + BAND_NEAR, T + BAND_NEAR
        x1, y1 = R - w - BAND_NEAR, B - h - BAND_NEAR
        if x1 < x0:                       # 窄屏兜底：水平居中成竖线
            x0 = x1 = (L + R - w) / 2.0
        if y1 < y0:                       # 矮屏兜底：垂直居中成横线
            y0 = y1 = (T + B - h) / 2.0
        per = 2.0 * ((x1 - x0) + (y1 - y0))
        if per < 120.0:                   # 屏比窗还小：无可走环
            return []
        lo, hi = BAND_NEAR, BAND_FAR - 8.0
        mid, amp = (lo + hi) / 2.0, (hi - lo) / 2.0

        def depth(s):                     # 每圈摆动两次，缓入缓出
            return mid + amp * math.sin(s / per * math.tau * 2.0
                                        + self._ring_phase)

        pts, s = [], 0.0
        n = max(2, int((x1 - x0) / RING_STEP) + 2)      # 顶边 左→右
        for i in range(n):
            f = i / (n - 1)
            pts.append((x0 + (x1 - x0) * f, T + depth(s)))
            s += RING_STEP
        n = max(2, int((y1 - y0) / RING_STEP) + 2)      # 右边 上→下
        for i in range(1, n):
            f = i / (n - 1)
            pts.append((R - w - depth(s), y0 + (y1 - y0) * f))
            s += RING_STEP
        n = max(2, int((x1 - x0) / RING_STEP) + 2)      # 底边 右→左
        for i in range(1, n):
            f = i / (n - 1)
            pts.append((x1 - (x1 - x0) * f, B - h - depth(s)))
            s += RING_STEP
        n = max(2, int((y1 - y0) / RING_STEP) + 2)      # 左边 下→上
        for i in range(1, n - 1):
            f = i / (n - 1)
            pts.append((L + depth(s), y1 - (y1 - y0) * f))
            s += RING_STEP
        return pts

    def _band_clamp(self, x, y):
        """散步位置约束：窗口完整留在屏幕内（边距 ≥12px）；若深入中央
        死区且刚浅越界（拖拽后的过渡不管，交给寻路自行走回环上）。"""
        g = self._scr_rect()
        w, h = self.width(), self.height()
        m = 12.0
        if x < g.left() + m:
            x = g.left() + m
        elif x > g.right() - w - m:
            x = g.right() - w - m
        if y < g.top() + m:
            y = g.top() + m
        elif y > g.bottom() - h - m:
            y = g.bottom() - h - m
        # 中央死区（窗沿四边都深入 >BAND_FAR）：浅越界贴回环带内沿
        if (x >= g.left() + BAND_FAR and x <= g.right() - w - BAND_FAR
                and y >= g.top() + BAND_FAR
                and y <= g.bottom() - h - BAND_FAR):
            dl = x - (g.left() + BAND_FAR - 1)
            dr = (g.right() - w - BAND_FAR + 1) - x
            dt = y - (g.top() + BAND_FAR - 1)
            db = (g.bottom() - h - BAND_FAR + 1) - y
            mn = min(dl, dr, dt, db)
            if mn <= 6.0:
                if mn == dl:
                    x = g.left() + BAND_FAR - 1
                elif mn == dr:
                    x = g.right() - w - BAND_FAR + 1
                elif mn == dt:
                    y = g.top() + BAND_FAR - 1
                else:
                    y = g.bottom() - h - BAND_FAR + 1
        return x, y

    def _wander_start(self):
        """开始一段环带散步：路径点取全环，从离当前位置最近的点起，
        随机方向，走 600-1400px 后收工张望、休息 25-50s。"""
        self._ring_phase = random.uniform(0.0, math.tau)
        pts = self._ring_pts()
        if not pts:
            self._next_walk = self.t + random.uniform(*IDLE_WALK_EVERY)
            return
        bx, by = self.x(), self.y()
        i = min(range(len(pts)),
                key=lambda k: (pts[k][0] - bx) ** 2 + (pts[k][1] - by) ** 2)
        self._wander = {"pts": pts, "i": i, "dir": random.choice((-1, 1)),
                        "left": random.uniform(600, 1400),
                        "key": (self.width(), self.height()), "it": self.t}

    def _pomo_min(self):
        """当前设置的番茄钟时长（分钟）。"""
        try:
            return int(clamp(int(self._meta.get("pomo_min", POMO_MIN_DEF)),
                             POMO_MIN_LO, POMO_MIN_HI))
        except (TypeError, ValueError):
            return POMO_MIN_DEF

    def _pomo_label(self):
        """菜单里的番茄钟文案：没开始 = 开始番茄钟…；跑着 = 停止（剩 mm:ss）。"""
        if self._pomo_end is None:
            return "开始番茄钟…"
        left = max(0, int(self._pomo_end - self.t))
        return "停止番茄钟（剩 %d:%02d）" % (left // 60, left % 60)

    def _pomo_toggle(self):
        """番茄钟开关（菜单唯一入口）：跑着 → 取消；没开始 → 先问时长再开始。"""
        if self._pomo_end is not None:
            self._pomo_end = None
            self._say("好，番茄钟取消啦。", 2.0)
            self._pomo_text("番茄钟 %d 分钟" % self._pomo_min())
            return
        self._ask_pomo_min()

    def _ask_pomo_min(self):
        """弹出奶油卡片对话框选时长（预设胶囊 + ±5 步进，1~180 任意值）；
        确认即开始这一段番茄钟，并把时长记进存档当默认。"""
        dlg = PomoDialog(self._pomo_min(), self)
        dlg.adjustSize()
        scr = self._scr_rect()
        x = self.x() + (self.width() - dlg.width()) // 2
        y = self.y() - dlg.height() - 6
        if y < scr.top() + 8:                      # 头顶放不下就放到下方
            y = self.y() + self.height() - self._win_pad_b() - 20
        x = int(clamp(x, scr.left() + 8, scr.right() - dlg.width() - 8))
        y = int(clamp(y, scr.top() + 8, scr.bottom() - dlg.height() - 8))
        dlg.move(x, y)
        if dlg.exec():
            self._pomo_start(dlg.minutes())

    def _pomo_start(self, mins):
        """以指定时长开始一段番茄钟（时长记档，下次默认还是它）。"""
        mins = int(clamp(int(mins), POMO_MIN_LO, POMO_MIN_HI))
        self._meta["pomo_min"] = mins
        self._save()
        self._pomo_end = self.t + mins * 60.0
        self._pomo_total = mins * 60.0
        self._pomo_txt_t = self.t
        self._say(self._line("pomo_start"), 3.0)
        self._sq.kick(1.6)
        self._pomo_text("停止番茄钟（剩 %d 分）" % mins)

    def closeEvent(self, e):
        self._close_bread()
        for c in self._crumbs:           # 收掉地上残留的面包渣小窗
            c.stop()
        self._crumbs = []
        self._meta["last_seen"] = time.time()
        self._save()
        super().closeEvent(e)

    # ================= 资源 =================
    @staticmethod
    def _pm_from_pil(im):
        """PIL Image -> QPixmap（RGBA 直转，无落盘）。"""
        im = im.convert("RGBA")
        data = im.tobytes("raw", "RGBA")
        qimg = QImage(data, im.width, im.height,
                      im.width * 4, QImage.Format_RGBA8888)
        return QPixmap.fromImage(qimg.copy())

    # ---------- 缩放缓存（性能） ----------
    def _dev_px(self, design_len):
        """设计长度 -> 设备像素：paintEvent 的 painter scale × 屏幕 DPR。"""
        dpr = self.devicePixelRatioF() or 1.0
        return design_len * (self.width() / DW) * dpr

    def _cache_pm(self, key, pm, wdev):
        """按设备像素宽预缩放并缓存（取整到整像素）。
        底图 1548×1236 直接 drawPixmap 到几百像素时，Qt 每帧都要做一次
        大面积平滑重采样；缓存后静止状态就是 1:1 贴图，只有缩放动画期间
        才随尺寸变化重建。返回的 pixmap 直接用整图作源绘制即可。"""
        wq = max(4, int(round(wdev)))
        hq = max(4, int(round(wq * pm.height() / float(pm.width()))))
        ck = (key, wq, hq)
        hit = self._pm_cache.get(ck)
        if hit is None:
            if len(self._pm_cache) > 16:     # 连续缩放时别把缓存撑爆
                self._pm_cache.clear()
            hit = pm.scaled(wq, hq, Qt.IgnoreAspectRatio,
                            Qt.SmoothTransformation)
            self._pm_cache[ck] = hit
        return hit

    def _design_per_px(self):
        """1 设备像素 = 多少设计单位（缓存回贴时用，保证 1:1 不二次重采样）。"""
        dpr = self.devicePixelRatioF() or 1.0
        return DW / (self.width() * dpr)

    def _load_assets(self):
        # 缩放缓存：底图 1548×1236（4x 超分）每帧实时重采样代价很高，
        # 这里按"当前缩放档"缓存一份已缩好的 pixmap（见 _cache_pm）
        self._pm_cache = {}
        # ---- 尾巴轻摆素材：notail 底图 + 尾巴子图（PIL 启动时一次生成）。
        #      剪切矩形取尾巴大圆 y>960 的下部（该区域无身体像素，
        #      左缘距矩形左界有 >40px 透明缓冲，前爪右缘 <1345 不受影响）
        img = Image.open(res_path("base.png")).convert("RGBA")
        bx0, by0, bx1, by1 = TAIL_RECT
        # 叶子单独成层：底图用“去叶版”，叶子自己按饥饿程度绕根部旋转。
        # （去叶版由 tools/make_leaf_assets.py 生成并随 assets 打包）
        img_body = Image.open(res_path("base_body.png")).convert("RGBA")
        clear = Image.new("L", img.size, 0)
        ImageDraw.Draw(clear).rectangle([bx0 + 10, by0, bx1, by1], fill=255)
        notail = img_body.copy()
        notail.putalpha(ImageChops.subtract(img_body.getchannel("A"), clear))
        self.base_pm = self._pm_from_pil(notail)
        self.tail_pm = self._pm_from_pil(img.crop((bx0, by0, bx1, by1)))
        self.tail_geo = (bx0, by0, bx1, by1)
        self.leaf_pm = QPixmap(res_path("leaf.png"))
        self.leaf_dry_pm = QPixmap(res_path("leaf_dry.png"))
        self.eye_l_pm = QPixmap(res_path("eye_l.png"))
        self.eye_r_pm = QPixmap(res_path("eye_r.png"))
        self.mouth_pm = QPixmap(res_path("mouth.png"))
        with open(res_path("coords.json"), "r", encoding="utf-8") as f:
            self.coords = json.load(f)
        self.s = self.CHAR_W / self.base_pm.width()
        self.bw = self.base_pm.width() * self.s
        self.bh = self.base_pm.height() * self.s
        # 预计算 ω 精灵下轮廓（素材像素坐标，相对嘴盒中心，每 4px 一档），
        # 张嘴腔体上缘沿它连线，实现与 ω 连成一体
        img = self.mouth_pm.toImage().convertToFormat(QImage.Format_ARGB32)
        self.omega_bot = []
        for px in range(0, img.width(), 2):
            bot = -1
            for py in range(img.height() - 1, -1, -1):
                if (img.pixel(px, py) >> 24) & 0xFF > 40:
                    bot = py
                    break
            if bot >= 0:
                self.omega_bot.append(
                    (px - img.width() / 2.0, bot - img.height() / 2.0))
        mc = self.coords["mouth"]
        self.mouth_center = (
            self.BCX - self.bw / 2 + (mc["x"] + mc["w"] / 2) * self.s,
            self.BCY - self.bh + (mc["y"] + mc["h"] / 2) * self.s)
        ec = self.coords["eye_l"]
        er = self.coords["eye_r"]
        self.eye_pos = {
            "eye_l": (self.BCX - self.bw / 2 + (ec["x"] + ec["w"] / 2) * self.s,
                      self.BCY - self.bh + (ec["y"] + ec["h"] / 2) * self.s,
                      ec["w"] * self.s, ec["h"] * self.s),
            "eye_r": (self.BCX - self.bw / 2 + (er["x"] + er["w"] / 2) * self.s,
                      self.BCY - self.bh + (er["y"] + er["h"] / 2) * self.s,
                      er["w"] * self.s, er["h"] * self.s),
        }
        self.head_top = self.BCY - self.bh           # 头顶（含叶）设计 y

    # ================= 状态机 =================
    def _set_state(self, name):
        if self.state == name:
            return
        # 从用户操作引发的状态退出来的那一刻，先锁一段 idle：
        # 这段里不再冒出任何自发状态（见 _decide_state 的 _post_lock）。
        if self.state in USER_STATES:
            self._post_lock = self.t + POST_IDLE_SECS
        self.state = name
        self.state_t0 = self.t

    def _decide_state(self):
        """优先级：mischief(恶作剧) > dizzy(晕车) > shy(傲娇躲避) > happy(互动)
        > angry > surprised > sleep > idle"""
        if self.t < self.mischief_until:      # 恶作剧最高优先，中断一切
            self._set_state("mischief")
            return
        if self.t < self._dizzy_until:        # 晕车：被晃到晕，只想躲清静
            self._set_state("dizzy")
            return
        if self.t < self._shy_until:          # 傲娇躲避：连摸 5 下，翻脸躲开
            self._set_state("shy")
            return
        if self.phase != "idle":
            self._set_state("happy")
            return
        # 用户操作引发的状态刚结束：强制回 idle 坐一会儿（POST_IDLE_SECS），
        # 期间不冒自发状态。喂食/抚摸等直接互动（上面 phase 分支）不受影响。
        if self.t < self._post_lock:
            self._set_state("idle")
            return
        if self.t < self.angry_until:
            self._set_state("angry")
            return
        # 随机庆祝微表情：happy 眯眼 + 小跳 + 彩纸（短促，1.3s）
        if self.t < self._celebrate_until:
            self._set_state("happy")
            return
        # 鼠标靠近 -> 惊讶（冷却 7s，仅平静时触发；饿了不会有精神惊讶）
        if (self.t >= self.surprised_cd and self.state == "idle"
                and self.hungry_amt.v < 0.5):
            m = QCursor.pos()
            c = self.mapToGlobal(QPoint(int(self.width() / 2),
                                        int(self.height() / 2)))
            dist = math.hypot(m.x() - c.x(), m.y() - c.y())
            if dist < 130 * self.size:
                self.surprised_until = self.t + 1.5
                self.surprised_cd = self.t + 7.0
                self._set_state("surprised")
                return
        if self.t < self.surprised_until:
            self._set_state("surprised")
            return
        # 深度空闲（优先级最低）：SLEEP_AFTER 秒无交互 -> 睡眠；
        # 深夜（23-5 点）困意提前，90 秒就犯困。钻进泡泡前嘟囔一句（设定：
        # EJEE 的爱好是在泡泡里睡觉）
        hour = time.localtime().tm_hour
        thresh = 90.0 if (hour >= 23 or hour < 5) else SLEEP_AFTER
        if self.phase == "idle" \
                and self.t - self.last_interact > thresh:
            if self.state != "sleep" and self.bubble_until < self.t \
                    and not self._pass:
                self._say(self._line("sleep_in"), 2.6, "zzz")
            self._set_state("sleep")
            return
        self._set_state("idle")

    # ================= 主循环 =================
    def _tick(self):
        dt = clamp(self.t - self._last_t, 0.001, 0.2)
        self._last_t = self.t
        self.t = self.clock.elapsed() / 1000.0

        # 眨眼（平静时才眨）
        if self.blink_t0 is None and self.t >= self.next_blink \
                and self.state == "idle":
            self.blink_t0 = self.t
            self.blink_pending2 = random.random() < 0.25
            if not self.blink_pending2:
                self.next_blink = self.t + self._rand_blink_delay()

        # happy 子相位推进：面包吃进去（张嘴→吞入→闭嘴），随后满足收尾
        if self.phase == "bread" and self.t - self.phase_t0 >= 0.55:
            self._end_interact()
            self._say(self._line("feed"), 2.8)

        # 番茄钟：到点庆祝 + 提示音；托盘文案 15s 节流刷新倒计时
        if self._pomo_end is not None:
            rem = self._pomo_end - self.t
            if rem <= 0:
                self._pomo_end = None
                self._pomo_text("番茄钟 %d 分钟" % self._pomo_min())
                self._celebrate_until = self.t + 1.5
                self._sq.kick(2.4)
                self._say(self._line("pomo_done"), 4.0)
                for i in range(12):
                    self.particles.append(Particle(
                        "confetti", self.BCX + random.uniform(-60, 60),
                        self.head_top + random.uniform(-4, 20), self.t))
                self._ding()
            elif self.t - self._pomo_txt_t > 15:
                self._pomo_txt_t = self.t
                self._pomo_text(
                    f"停止番茄钟（剩 {max(1, int(rem / 60) + 1)} 分）")

        # 番茄钟：最后一分钟转为"紧张期待"（牌子转红 + 轻抖 + 瞪眼）
        left = (self._pomo_end - self.t) if self._pomo_end is not None else 999.0
        self._pomo_nrv.step(1.0 if 0.0 < left <= 60.0 else 0.0, dt)
        # 气泡会占到右上角：倒计时牌此时往下让一让，避免压字
        self._tag_dy.step(
            40.0 if (self.bubble_text and self.t < self.bubble_until) else 0.0,
            dt)
        # 吃撑：肚子鼓起 / 消下去
        self._stuffed.step(1.0 if self.t < self._stuffed_until else 0.0, dt)
        # 拖拽投喂：面包悬在嘴边时放大 + 虚线光环，给个"可以放了"的提示
        if self._bread is not None:
            mg = self._mouth_global()
            gp = QCursor.pos()
            self._bread.set_hot(
                math.hypot(gp.x() - mg.x(), gp.y() - mg.y()) <= 48 * self.size)

        # ---- 自由走动：沿屏幕四周边框带环行（不横穿中央），走够收工张望 ----
        if self._wander is not None:
            w = self._wander
            if (self._dragging or self._pass or self.state == "sleep"
                    or self.hungry_amt.v > 0.6
                    or self.t < self.mischief_until):
                self._wander = None
                self._next_walk = self.t + random.uniform(*IDLE_WALK_EVERY)
            else:
                key = (self.width(), self.height())
                if key != w["key"] or self.t - w["it"] > 15.0:
                    # 窗口尺寸变了 / 疑似卡住（改分辨率等）：重算环带就近续走
                    w["pts"] = self._ring_pts()
                    w["key"] = key
                    bx, by = self.x(), self.y()
                    w["i"] = min(range(len(w["pts"])),
                                 key=lambda k: (w["pts"][k][0] - bx) ** 2
                                 + (w["pts"][k][1] - by) ** 2)
                    w["it"] = self.t
                tx, ty = w["pts"][w["i"]]
                dx = tx - self.x()
                dy = ty - self.y()
                dist = math.hypot(dx, dy)
                if dist > 3:
                    step = min(self._walk_speed * dt, dist)
                    w["left"] -= step
                    # 段落水平分量占优才转身（竖直爬行保持原朝向，不抖）
                    if abs(dx) > 0.35 * dist:
                        self.facing = -1 if dx > 0 else 1
                    nx, ny = self._band_clamp(self.x() + dx / dist * step,
                                              self.y() + dy / dist * step)
                    self.move(int(nx), int(ny))
                    # 游泳姿态：相位按走过的距离推进（一拱一拱），
                    # 方向变化率转成身体倾斜（转弯像开车压弯）
                    self._swim_ph += (step / 180.0) * math.tau
                    hd = math.atan2(dy, dx)
                    if self._heading is not None:
                        dph = math.atan2(math.sin(hd - self._heading),
                                         math.cos(hd - self._heading))
                        if abs(dph) > 0.03:      # 忽略逐帧抖动
                            self._turn_t = clamp(dph * 42.0, -8.0, 8.0)
                    self._heading = hd
                else:
                    self._heading = None
                    w["i"] = (w["i"] + w["dir"]) % len(w["pts"])
                    w["it"] = self.t
                    if w["left"] <= 0:           # 走够了：收工张望休息
                        self._look_until = self.t + 1.6
                        self._look_dir = random.choice((-1.0, 1.0))
                        self._wander = None
                        self._next_walk = self.t + random.uniform(*IDLE_WALK_EVERY)
        elif (self.state == "idle" and self.phase == "idle"
                and not self._dragging and not self._pass
                and self.hungry_amt.v < 0.6
                and self.t >= self._post_lock
                and self.t >= self._next_walk):
            self._next_walk = self.t + 1e9     # 散步中不再触发
            self._wander_start()

        # 游泳姿态弹簧：走起来才浮沉，停下就交还给呼吸；倾斜目标衰减回 0
        self._swim.step(1.0 if self._wander is not None else 0.0, dt)
        self._turn_t *= math.exp(-5.5 * dt)
        self._turn.step(self._turn_t, dt)

        # 恶作剧收尾：喷完汁立刻沿屏幕边溜走一小段（"略略略"），再回落
        if (self.mischief_until > 0.0 and self.t >= self.mischief_until
                and not self._fled):
            self._fled = True
            self._start_flee()
        if self._flee is not None:
            fl = self._flee
            if self._dragging or self._pass:
                self._flee = None
            else:
                step = min(520.0 * dt, fl["left"])
                fl["left"] -= step
                nx, ny = self._band_clamp(self.x() + fl["dx"] * step,
                                          self.y() + fl["dy"] * step)
                self.move(int(nx), int(ny))
                if fl["dx"] != 0.0:
                    self.facing = -1 if fl["dx"] > 0 else 1
                self._turn_t = clamp(9.0 * fl["dx"] + 9.0 * fl["dy"], -9.0, 9.0)
                self._swim_ph += (step / 180.0) * math.tau
                if fl["left"] <= 0.5:
                    self._flee = None
                    self._sq.kick(1.5)

        # 傲娇躲避：重定位已在 _start_shy 里"直接闪现"完成，这里不再做
        # 持续小碎步 / 缩身（用户要求不做形变，闪现即可）。
        self._shy_amt.step(0.0, dt)

        # 待机闲聊：平静时每 4-8 分钟冒一句时段台词（穿透模式不打扰）
        if (self.state == "idle" and not self._pass
                and self.phase == "idle"
                and self.t >= self._post_lock
                and self.bubble_until < self.t
                and self.t >= self._next_chatter):
            self._next_chatter = self.t + random.uniform(*IDLE_CHATTER_EVERY)
            self._say(self._line(self._bucket()), 3.0)

        # ---- 饱食度：非线性衰减（越低掉得越快，全程 3 小时），饿了提醒 ----
        self._meta["hunger"] = clamp(
            self._hunger_after(self._meta.get("hunger", 80.0), dt), 0.0, 100.0)
        if (self._meta["hunger"] < 30.0 and self.state == "idle"
                and not self._pass and self.phase == "idle"
                and self.bubble_until < self.t
                and self.t >= self._next_hungry):
            self._next_hungry = self.t + random.uniform(240, 420)
            txt = self._line("hungry")
            if self._meta["hunger"] < 10.0:
                txt = "真的好饿……" + txt
            self._say(txt, 3.0)
            self._sq.kick(-0.6)

        # 周期存档：last_seen 每 60s 刷新（昼夜问候与回来时长判定用）
        if time.time() - self._save_t > 60.0:
            self._save_t = time.time()
            self._save()

        # wake 相位：伸懒腰两段（0.38s 拉长回弹 -> 0.72s 收尾回 idle）
        if self.phase == "wake":
            if not self._wake2 and self.t - self.phase_t0 >= 0.38:
                self._wake2 = True
                self._sq.kick(2.6)
            if self.t - self.phase_t0 >= 0.72:
                self._end_interact()

        # 状态与参数推进（弹簧动力学：惯性 + 回弹 + Overshoot）
        self._decide_state()
        tgt = P[self.state]
        for key, s in self.spr.items():
            s.step(tgt[key], dt)
            self.cur[key] = s.v
        # 可怜层（面包掉在地上）：表情按用户要求与 angry 完全一致
        # （倒 V 怒眉 + 生气撇嘴 + 人中小竖线）。用 _pity 显形度把 angry
        # 的眉眼通道（puff）顶起来，叠加在 idle 之上；嘴形见下面 alt_tgt。
        pty = clamp(self._pity.v, 0.0, 1.0)
        if pty > 0.01:
            self.cur["puff"] = max(self.cur["puff"], pty)
        # 拖拽倾斜弹簧（朝移动方向压）+ 拖拽速度衰减
        self._tilt.step(clamp(self._dvx / 50.0, -7.0, 7.0)
                        if self._dragging else 0.0, dt)
        self._sq.step(0.0, dt)
        # 嘴形交叉渐变：替代嘴形（happy 开合/圆嘴/瘪嘴）显形度弹簧，
        # happy 进食期间保持显形（咀嚼开合到闭的瞬间不闪回 ω 嘴）
        op_now = self._mouth_open()
        # 嘴形目标：surprised/angry/happy进食 之外，可怜层（pty）也要顶到
        # 全显，让掉面包时的嘴形与 angry 一致（生气撇嘴 + 人中）。
        alt_tgt = max(1.0 if self.state in ("surprised", "angry") \
                      or (self.state == "happy"
                          and (op_now > 0.05 or self.phase == "bread"))
                      else 0.0, pty)
        self.mouth_alt.step(alt_tgt, dt)
        # 官方五表情眼形：happy 双眯眼弧 / surprised 左眼眨眼
        self.wink_l.step(1.0 if self.state in ("happy", "surprised") else 0.0, dt)
        self.wink_r.step(1.0 if self.state == "happy" else 0.0, dt)
        # 睡眠表情（闭眼弧 + 小圆嘴）交叉渐显
        self.sleep_amt.step(1.0 if self.state == "sleep" else 0.0, dt)
        # 醒来时泡泡"啵"地破掉：一圈小泡泡 + 飘字
        if self._sleeping_prev and self.state != "sleep" \
                and self.sleep_amt.v > 0.35:
            for i in range(5):
                ang = -2.4 + i * 0.55
                pt = Particle(
                    "bubble", self.BCX + math.cos(ang) * 70,
                    self.BCY - self.bh * 0.45 + math.sin(ang) * 50,
                    self.t - i * 0.03)
                pt.vx = math.cos(ang) * 30      # 破泡：向外轻轻溅开
                pt.vy = -16.0 - 12.0 * random.random()
                self.particles.append(pt)
            self.floats.append(("啵～", self.BCX + 52, self.head_top - 4,
                                self.t))
        self._sleeping_prev = self.state == "sleep"
        # 饥饿表情图层：饱食度 <30 渐显（垂眼/虚弱波浪嘴/汗滴）
        self.hungry_amt.step(
            1.0 if self._meta.get("hunger", 100.0) < 30.0 else 0.0, dt)
        # 恶作剧：表情显形弹簧（1.5s 内 1→0 自动回落）+ 尾巴甩动衰减 + 蓄力弹开
        self.mischief_amt.step(1.0 if self.t < self.mischief_until else 0.0, dt)
        self._mis_tail.step(0.0, dt)
        if self._mis_puff and self.t >= self._mis_puff:
            self._mis_puff = 0.0
            self._sq.kick(2.8)
        ha_ = clamp(self.hungry_amt.v, 0.0, 1.0)
        self._hover_amt.step(1.0 if self._hover else 0.0, dt)
        # 可怜眼神：屏幕上还有面包渣就盯着它看（淡入），渣没了就收回去
        self._pity.step(1.0 if self._crumbs else 0.0, dt)
        # 视线缓动：把 raw 视线目标缓动进来，消除突变（面包渣出现等瞬间）
        tgx, tgy, _ = self._gaze_target()
        self._gvx.step(tgx, dt)
        self._gvy.step(tgy, dt)
        # 晕车：显形弹簧；期间每隔一拍真的吐一串泡泡（说到做到）
        dzy = self.t < self._dizzy_until
        self._dizzy_amt.step(1.0 if dzy else 0.0, dt)
        if dzy and not self._dragging and self._dizzy_fx <= 0.0:
            self._dizzy_fx = 0.85
            for i in range(3):
                pt = Particle("bubble", self.mouth_center[0]
                              + random.uniform(-20, 20),
                              self.mouth_center[1] - 10, self.t - i * 0.07)
                pt.vx = random.uniform(-34, 34)
                pt.vy = random.uniform(-70, -40)
                self.particles.append(pt)
            self._sq.kick(0.9)
            self.floats.append(("呕…", self.mouth_center[0] + 10,
                                self.mouth_center[1] - 32, self.t))
        # 呼吸/尾摆相位累积器：饥饿时呼吸变慢变浅、尾巴几乎不摆（可变速无跳变）
        self._breathe_ph += dt * 2 * math.pi / max(
            0.5, self.cur["sway_per"] * (1.0 + 0.30 * ha_))
        self._tail_ph += dt * 2 * math.pi / (
            1.9 * (1.0 + 0.45 * ha_) * (1.0 - 0.35 * clamp(self._swim.v, 0.0, 1.0)))
        # 海市蜃楼（牛奶吐司）：饿了每 10 秒头顶飘出一朵极小的云，2 秒后啵地破灭
        if (ha_ > 0.5 and self.state == "idle" and self.phase == "idle"
                and not self._pass and self.t >= self._next_fantasy):
            self._next_fantasy = self.t + random.uniform(9.4, 10.6)
            self._fantasy = {"t0": self.t}
        if self._fantasy is not None:
            if self._dragging or self.state == "sleep":
                self._fantasy = None          # 被拖走/睡着：幻想被打断
            elif self.t - self._fantasy["t0"] > 2.3:
                self._fantasy = None          # 破灭：啵 + 一缕气 + 轻轻叹一口
                self._sigh_t0 = self.t
                for i in range(4):            # 破掉的泡皮碎屑
                    pt = Particle("bubble", self.BCX + 58
                                  + random.uniform(-14, 14),
                                  self.head_top + random.uniform(6, 22),
                                  self.t - i * 0.03)
                    pt.vx = random.uniform(-46, 46)
                    pt.vy = random.uniform(-56, -20)
                    self.particles.append(pt)
                self.floats.append(("呼…", self.mouth_center[0] + 26,
                                    self.mouth_center[1] + 6, self.t))
        self._dvx *= math.exp(-10 * dt)
        self._dvy *= math.exp(-10 * dt)

        # 松手惯性滑行（带撞墙反弹）
        if self._glide is not None:
            gx_, gy_ = self._glide
            self.move(self.pos() + QPoint(int(gx_ * dt), int(gy_ * dt)))
            dec = math.exp(-3.2 * dt)
            gx_, gy_ = gx_ * dec, gy_ * dec
            g = self.frameGeometry()
            scr = self._scr_rect()
            hit = False
            if g.left() <= scr.left() + 4 and gx_ < 0:
                gx_ = -gx_ * 0.45; hit = True
            if g.right() >= scr.right() - 4 and gx_ > 0:
                gx_ = -gx_ * 0.45; hit = True
            if g.top() <= scr.top() + 4 and gy_ < 0:
                gy_ = -gy_ * 0.45; hit = True
            if g.bottom() >= scr.bottom() - 4 and gy_ > 0:
                gy_ = -gy_ * 0.45; hit = True
            if hit:
                self._sq.kick(2.6)
                self.angry_until = self.t + 2.0
            self._glide = [gx_, gy_]
            if math.hypot(gx_, gy_) < 40:
                self._glide = None

        # Shift+滚轮缩放：弹簧推进（缓动），落定后一次性存档
        self._size_spring.step(self.target_size, dt)
        # 穿透模式透明度：淡出至 0.30（透视身后内容），恢复 1.0
        self._opac.step(0.30 if self._pass else 1.0, dt)
        self.setWindowOpacity(clamp(self._opac.v, 0.05, 1.0))
        if abs(self._size_spring.v - self.size) > 0.0004 or \
                abs(self._size_spring.vel) > 0.02:
            self._zooming = True
            self._apply_size(self._size_spring.v)
        elif self._zooming:
            self._zooming = False
            self._zoom_anchor = None
            self._save()
            # 缩放手势收尾：尺寸确实变了才说一句（带冷却）
            if (abs(self.size - self._zoom_from) > 0.04
                    and self.t >= self._next_zoom_line):
                self._next_zoom_line = self.t + 15.0
                self._say(self._line("zoom"), 2.4)

        # 待机微动作调度（吐泡泡 / 左右张望 / 双连眨）
        if self.state == "idle" and self.phase == "idle" \
                and self.t >= self._next_micro:
            r = random.random()
            if r < 0.45:
                mx, my = self.mouth_center
                for i in range(random.randint(3, 5)):
                    self.particles.append(Particle(
                        "bubble", mx + random.uniform(-8, 8),
                        my - 12 - random.uniform(0, 10), self.t))
            elif r < 0.8:
                self._look_dir = random.choice((-1.0, 1.0))
                self._look_until = self.t + 2.2
            else:
                self.blink_t0 = self.t
                self.blink_pending2 = True
            self._next_micro = self.t + random.uniform(9, 22)

        # 随机微表情调度（30~60s 一次，短促惊讶或庆祝，1.3s 后回 idle）；
        # 饥饿时保持可怜的虚弱态，不再间歇切换表情；
        # 用户操作引发的状态刚结束（_post_lock 内）也先按住不冒；
        # 10% 概率顺带自言自语一句（pet/hungry 池），没人理也鲜活
        if self.state == "idle" and self.phase == "idle" \
                and self.hungry_amt.v < 0.5 \
                and self.t >= self._post_lock \
                and self.t >= self._next_expr:
            if random.random() < 0.5:
                self.surprised_until = self.t + 1.3
            else:
                self._celebrate_until = self.t + 1.3
                self._sq.kick(2.2)          # 庆祝小跳（挤压形变）
                for i in range(10):
                    self.particles.append(Particle(
                        "confetti",
                        self.BCX + random.uniform(-55, 55),
                        self.head_top + random.uniform(-4, 20), self.t))
            self._next_expr = self.t + random.uniform(*IDLE_EXPR_EVERY)
            if (random.random() < 0.10 and not self._pass
                    and self.bubble_until < self.t):
                self._say(self._line("pet" if random.random() < 0.55
                                     else "hungry"), 2.8)

        # happy 期间持续冒爱心/星星
        if self.state == "happy":
            self._fx_timer -= dt
            if self._fx_timer <= 0:
                self._fx_timer = 0.28
                hx = self.BCX + random.uniform(-60, 60)
                hy = self.head_top + random.uniform(-6, 26)
                kind = "heart" if random.random() < 0.6 else "star"
                self.particles.append(Particle(kind, hx, hy, self.t))
        # angry 冒蒸汽（气到冒烟：节奏更急、上浮更冲）
        if self.state == "angry":
            self._fx_timer -= dt
            if self._fx_timer <= 0:
                self._fx_timer = 0.18
                sx = self.BCX + random.uniform(-70, 70)
                pt = Particle("steam", sx, self.head_top + 8, self.t)
                pt.vy = random.uniform(-74, -54)
                self.particles.append(pt)
        # sleep 冒 Zzz（头顶右上慢飘，避开叶子）
        if self.state == "sleep":
            self._fx_timer -= dt
            if self._fx_timer <= 0:
                self._fx_timer = random.uniform(1.1, 1.9)
                self.particles.append(Particle(
                    "zzz", self.BCX + random.uniform(30, 56),
                    self.head_top + random.uniform(-2, 10), self.t))

        # 饥饿汗滴：饿肚子时头侧冒汗（弱弱的感觉），与 zzz/蒸汽共用计时器
        if (self.hungry_amt.v > 0.6 and self.state == "idle"
                and self.phase == "idle" and not self._pass):
            self._fx_timer -= dt
            if self._fx_timer <= 0:
                self._fx_timer = random.uniform(2.6, 4.0)
                self.particles.append(Particle(
                    "sweat", self.BCX + random.choice((-1, 1))
                    * random.uniform(56, 76),
                    self.BCY - 132 + random.uniform(-8, 8), self.t))

        # 肚子咕咕叫：每 3 秒出头一声——波纹和音符交替，从肚皮冒出来；
        # 同时肚子抽一下（_sq 轻踢），静态图上是形变、exe 里能看出"叫"了
        if (self.hungry_amt.v > 0.3 and self.state == "idle"
                and self.phase == "idle" and not self._pass):
            self._fx_timer2 -= dt
            if self._fx_timer2 <= 0:
                self._fx_timer2 = random.uniform(2.7, 3.7)
                self._rumble_i += 1
                kind = "note" if self._rumble_i % 2 else "rumble"
                self.particles.append(Particle(
                    kind, self.BCX + random.uniform(-11, 11),
                    self.BCY - 40 + random.uniform(-4, 4), self.t))
                self._sq.kick(1.2)      # 位移峰值约 8%，读作肚子抽一下

        # 粒子物理
        alive = []
        for pt in self.particles:
            if self.t - pt.born >= pt.life:
                continue
            if pt.kind in ("confetti", "star"):
                pt.vy += 380 * dt
            elif pt.kind == "juice":
                pt.vy += 820 * dt         # 汁水重，坠得快
            elif pt.kind == "heart":
                pt.vy -= 14 * dt          # 越飘越轻
            elif pt.kind == "crumb_dust":
                pt.vy += 520 * dt         # 碎屑：落得快，弹一下就贴地
            pt.x += pt.vx * dt
            pt.y += pt.vy * dt
            pt.rot += pt.vr * dt
            # 橘子汁不再有范围框：旧实现会在汁滴碰到设计框内沿时把它
            # 钉在边缘并变成"水渍"（那圈水渍就是用户看到的方框，而且
            # 朝尾巴那一侧的汁水一撞边就停住，看起来像只往后喷）。
            # 现在汁水自由飞行、按 life 自然淡出，并由 JuiceOverlay
            # 在全局坐标里绘制，能飞出宠物自己的小窗口，360° 无边界。
            alive.append(pt)
        self.particles = alive
        if self.floats:
            self.floats = [f for f in self.floats if self.t - f[3] < 1.2]
        self.update()

    def _rand_blink_delay(self):
        return random.uniform(2.0, 6.0)

    def _blink_scale(self):
        if self.blink_t0 is None:
            return 1.0
        d = self.t - self.blink_t0
        DUR = 0.16
        if d >= DUR:
            self.blink_t0 = None
            if self.blink_pending2:
                self.blink_pending2 = False
                self.next_blink = self.t + 0.12
            return 1.0
        return 1.0 - 0.96 * math.sin(math.pi * d / DUR)

    def _tail_amp(self):
        """尾巴摆幅（设计 px）：慢波调制 + 情绪系数，产生不规律轻摆。
        饥饿时幅度大幅减弱（有气无力地晃一下）。"""
        base = {"happy": 2.0, "sleep": 0.7, "angry": 0.5,
                "mischief": 2.6}.get(self.state, 1.5)
        ha = clamp(self.hungry_amt.v, 0.0, 1.0)
        swim = clamp(self._swim.v, 0.0, 1.0)      # 游起来尾巴摆得更欢
        return (base * (1.0 - 0.62 * ha) * (1.0 + 0.55 * swim)
                * (1.0 + 0.35 * math.sin(self.t * 0.37)))

    def _gaze_target(self):
        """(gx, gy, tilt)：raw 视线朝向量（可能逐帧突变），远处衰减到 0。
        优先级：残渣 > 鼠标 > 张望微动作。掉在地上的面包渣存在时，
        会可怜巴巴地盯着它看（这是"喂不到"的情绪落点）。
        注意：返回值由 _gaze() 经弹簧缓动后对外使用，避免突变。"""
        if PREVIEW_MODE:            # 预览图可复现：视线固定
            return 0.30, -0.12, 0.60
        # 待机张望微动作：先看一边再看另一边
        if self.t < self._look_until:
            left = self._look_until - self.t
            d = self._look_dir if left > 1.1 else -self._look_dir
            return d * 0.9, -0.15, d * 2.0
        gx = gy = 0.0
        if QApplication.instance() is not None:
            # 掉地上的面包渣：视线被它吸走（不看鼠标了，盯着残渣）
            cm = self._crumb_gaze()
            if cm is not None:
                m = cm.gpos
                pity = clamp(1.0 - (time.time() - cm.t0 - Crumb.HOLD)
                             / 0.8, 0.0, 1.0) if time.time() - cm.t0 > \
                    Crumb.HOLD else 1.0
            else:
                m = QCursor.pos()
                pity = 0.0
            c = self.mapToGlobal(QPoint(int(self.width() / 2),
                                        int(self.height() * 0.45)))
            dx = (m.x() - c.x()) / max(1, self.width())
            dy = (m.y() - c.y()) / max(1, self.height())
            dist = math.hypot(m.x() - c.x(), m.y() - c.y())
            # 饥饿时视线范围拉远（眼巴巴盯着远处的"大面包"）；
            # 看残渣时不衰减（近处的东西就是要死死盯着）
            if pity >= 1.0:
                factor = 1.0
            else:
                span = 280.0 + 320.0 * clamp(self.hungry_amt.v, 0.0, 1.0)
                factor = clamp(1.0 - (dist - 320.0) / span, 0.0, 1.0)
            if pity >= 1.0 and dist > 30:
                gx = clamp(dx * 3.4, -1.0, 1.0)
                gy = clamp(dy * 3.4, -1.0, 1.0)
            else:
                gx = clamp(dx * 2.2, -1.0, 1.0) * factor
                gy = clamp(dy * 2.2, -1.0, 1.0) * factor
        return gx, gy, gx * 2.0

    def _gaze(self):
        """对外的平滑视线：返回弹簧缓动后的 (gx, gy, tilt)。
        原始目标由 _gaze_target() 每帧算出（可能突变，例如面包渣出现的
        一瞬间眼睛要"啪"地甩去看残渣），这里用 _gvx/_gvy 弹簧缓动，
        让眼睛 / 身体转向都是连续过渡，不再有"出错几帧"的突跳。
        预览图直接出目标值，避免离屏短帧里的缓动滞后。"""
        if PREVIEW_MODE:
            tgx, tgy, _ = self._gaze_target()
            return tgx, tgy, tgx * 2.0
        return self._gvx.v, self._gvy.v, self._gvx.v * 2.0

    # ================= 绘制 =================
    # ================= 绘制：一帧的上下文与身体 =================
    def _frame_ctx(self):
        """一帧里各绘制模块共用的量（只算一次，避免重复取弹簧/光标）。"""
        return {
            "t": self.t,
            "c": self.cur,
            "gaze": self._gaze(),
            "ha": clamp(self.hungry_amt.v, 0.0, 1.0),     # 饥饿表情显形度
            "sa": clamp(self.sleep_amt.v, 0.0, 1.0),      # 睡眠表情显形度
            "ma": clamp(self.mischief_amt.v, 0.0, 1.0),   # 恶作剧表情显形度
            "pity": clamp(self._pity.v, 0.0, 1.0),        # 残渣显形度（表情复用 angry：怒眉+撇嘴）
            "alt": clamp(self.mouth_alt.v, 0.0, 1.0),     # 替代嘴形显形度
            "blink": self._blink_scale(),
            "sigh": self._sigh_amt(),                    # 叹气包络 0..1
            "bw": self.bw, "bh": self.bh, "s2": self.s,
        }

    def _sigh_amt(self):
        """叹气包络 0..1：海市蜃楼破灭后轻轻塌一下再回来（约 1.25s）。"""
        a = (self.t - self._sigh_t0) / self._sigh_dur
        if a <= 0.0 or a >= 1.0:
            return 0.0
        return math.sin(math.pi * a) ** 0.72

    def _pose(self, f):
        """身体姿态：呼吸 / 摇摆 / 弹跳 / 颤抖 / 后仰（饥饿时起伏减半）。"""
        t, c, gaze, ha = f["t"], f["c"], f["gaze"], f["ha"]
        breathe = math.sin(self._breathe_ph)
        sway = (c["sway_amp"] * (1.0 - 0.4 * ha)
                * math.sin(self._breathe_ph) + gaze[2] * 0.6)
        bob = -c["bob"] * (1.0 - 0.5 * ha) * math.sin(self._breathe_ph)
        bounce = 0.0
        if c["bounce"] > 0.1:
            # 衰减弹跳：以 0.62s 为周期，随时间衰减
            ph = (t - self.state_t0) % 0.62
            decay = clamp(1.2 - (t - self.state_t0) * 0.12, 0.45, 1.0)
            bounce = -abs(math.sin(math.pi * ph / 0.62)) * c["bounce"] * decay
        shake_x = shake_y = 0.0
        if c["shake"] > 0.05:
            shake_x = c["shake"] * math.sin(t * 42.0)
            shake_y = c["shake"] * 0.6 * math.sin(t * 47.0 + 1.0)
        lean = -3.0 * c["excl"] if self.state == "surprised" else 0.0
        # 番茄钟最后一分钟：轻微发抖（紧张又期待）
        nrv = clamp(self._pomo_nrv.v, 0.0, 1.0)
        if nrv > 0.02:
            shake_x += 0.9 * nrv * math.sin(t * 36.0)
            shake_y += 0.5 * nrv * math.sin(t * 43.0 + 0.7)
        # 游泳：身体一拱一拱地向上顶（sin² 的柔和驼峰，比 |sin| 少些棱角），
        # 强度由 _swim 弹簧淡入淡出，停下时自然回到纯呼吸
        swim = clamp(self._swim.v, 0.0, 1.0)
        bob -= 3.8 * swim * math.sin(self._swim_ph) ** 2
        # 叹气：胸口一塌，整个身子往下坠一点（配合 _apply_body_pose 的压缩）
        sigh = f["sigh"]
        bob += 2.4 * sigh
        return {"breathe": breathe, "sway": sway, "bob": bob, "bounce": bounce,
                "shake_x": shake_x, "shake_y": shake_y, "lean": lean,
                "swim": swim, "sigh": sigh}

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

        # ---- 头顶叶子：单独一层，平时直立，饿了向一侧耷拉（见 _draw_leaf）----
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
        """头顶那片叶子：绕叶柄根部旋转。

        平时（ha=0）就是原素材的姿态；越饿越向右倒（最高 56°，叶尖从
        右上倒向右侧、微微压到头顶上），同时纵向缩一点、颜色从嫩绿转到
        土黄（leaf.png 与 leaf_dry.png 按 ha 叠加），读作“蔫了/枯萎”。"""
        ha = f["ha"]
        lx, ly, lw, lh, ax, ay = LEAF_GEO
        rect = QRectF(lx - self.BCX, ly - self.BCY, lw, lh)
        axr, ayr = ax - self.BCX, ay - self.BCY
        # 旋转轴在叶柄插入头皮的那一点，叶子绕它转，根部不裂缝；
        # 再叠一点很慢的晃动，像挂不住了却还在勉强撑着
        ang = ha * (66.0 + 2.6 * math.sin(self.t * 1.35))
        p.save()
        p.setOpacity(1.0 - 0.18 * ha)
        p.translate(axr, ayr)
        p.rotate(ang)
        p.scale(1.0, 1.0 - 0.07 * ha)        # 萎软：沿叶脉方向缩短
        p.translate(-axr, -ayr)
        lp = self._cache_pm("leaf", self.leaf_pm, self._dev_px(lw))
        p.drawPixmap(rect, lp, QRectF(lp.rect()))
        if ha > 0.02:                        # 枯色叠层：嫩绿 -> 土黄
            dp = self._cache_pm("leaf_dry", self.leaf_dry_pm, self._dev_px(lw))
            p.setOpacity(ha * 0.92)
            p.drawPixmap(rect, dp, QRectF(dp.rect()))
        p.restore()

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
                p.scale(c["eye_sx"] * (1.0 + 0.06 * ha) * (1.0 + 0.05 * nrv),
                        c["eye_sy"] * (1.0 - 0.10 * ha) * max(0.05, blink)
                        * (1.0 + 0.04 * nrv) * (1.0 - 0.30 * f["sigh"]))
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
        #   饥饿层现在只留：压扁的眼睛、波浪嘴、嘴角口水。）
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
        饥饿波浪嘴 + 口水 / 恶作剧坏笑 + 舌头）。"""
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
            # 口水：透明浅蓝小水滴挂在右嘴角，随时间轻微拉长（摇摇欲坠）
            p.setOpacity(ha * 0.80)
            p.setPen(Qt.NoPen)
            p.setBrush(QColor(176, 216, 244, 222))
            dh = mh * (0.22 + 0.05 * math.sin(self.t * 1.9))
            self._teardrop(p, mcx + w * 0.46, y0 + amp * 0.35 + dh * 0.42,
                           mw * 0.062, dh)
            p.setOpacity(1.0)
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
        """头顶幻想气泡：云朵里画着牛奶面包，2 秒后\"啵\"地破灭。"""
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
                p.translate(58, -294 + 1.2 * math.sin(t * 1.7))  # 轻飘
                # "极小"：整体再收 0.78；海市蜃楼本来就该是若有若无的一小团
                p.scale(fsc * 0.78, fsc * 0.78)
                # （"啵"的扩散环画不出来：云瓣半径 18.6、环只能到 22，几乎
                #   整圈都躲在云后面。破灭感交给「云猛放大 + 急速淡出」和
                #   _tick 里喷出的 4 颗 bubble 碎屑。）
                # 云朵：底圆 + 六瓣圆并集，一条干净轮廓（与对话气泡同画风）
                cloud = QPainterPath()
                cloud.addEllipse(QPointF(0, 0), 19, 14)
                for (bx, by, br) in ((-15, -4, 8.5), (-6, -12, 9.5),
                                     (5, -11, 9.0), (14, -3, 7.5),
                                     (-14, 5, 7.0), (13, 5, 6.5)):
                    bump = QPainterPath()
                    bump.addEllipse(QPointF(bx, by), br, br)
                    cloud = cloud.united(bump)
                # 投影：右下轻偏移的一层柔影，做出一点空气感
                p.setPen(Qt.NoPen)
                p.setBrush(QColor(140, 95, 50, 30))
                p.save()
                p.translate(1.8, 2.6)
                p.drawPath(cloud)
                p.restore()
                p.setPen(QPen(QColor("#E8A259"), 1.8, Qt.SolidLine,
                              Qt.RoundCap, Qt.RoundJoin))
                p.setBrush(QColor(255, 252, 245, 246))
                p.drawPath(cloud)
                # 意念泡小尾：两枚渐小的圆，斜垂向头顶
                for (tx_, ty_, tr_) in ((6.5, 18.5, 4.4), (1.5, 26, 2.9)):
                    p.setPen(QPen(QColor("#E8A259"), 1.9))
                    p.setBrush(QColor(255, 251, 243, 244))
                    p.drawEllipse(QPointF(tx_, ty_), tr_, tr_)
                # 牛奶吐司：方形面包片（顶部两瓣圆肩）+ 焦黄烤边 + 一块黄油
                p.setPen(QPen(QColor("#C08A4E"), 1.8, Qt.SolidLine,
                              Qt.RoundCap, Qt.RoundJoin))
                p.setBrush(QColor(253, 235, 198))
                tx = 10.4
                toast = QPainterPath()
                toast.moveTo(-tx, 6.2)
                toast.quadTo(-tx, 7.6, -tx + 1.6, 7.6)
                toast.lineTo(tx - 1.6, 7.6)
                toast.quadTo(tx, 7.6, tx, 6.2)
                toast.lineTo(tx, -1.4)
                toast.cubicTo(tx, -5.6, tx * 0.52, -7.6, 0, -7.6)
                toast.cubicTo(-tx * 0.52, -7.6, -tx, -5.6, -tx, -1.4)
                toast.closeSubpath()
                p.drawPath(toast)
                # 烤皮：沿吐司肩线压一条偏厚的焦黄边
                p.setPen(QPen(QColor("#DFA968"), 2.4, Qt.SolidLine,
                              Qt.RoundCap))
                crust = QPainterPath()
                crust.moveTo(-tx + 1.2, -1.8)
                crust.cubicTo(-tx + 0.8, -5.0, -tx * 0.5, -6.4, 0, -6.4)
                crust.cubicTo(tx * 0.5, -6.4, tx - 0.8, -5.0, tx - 1.2, -1.8)
                p.drawPath(crust)
                # 黄油：中间一小块 + 一道窄高光
                p.setPen(Qt.NoPen)
                p.setBrush(QColor(247, 205, 114))
                p.drawRoundedRect(QRectF(-4.2, -3.9, 8.4, 5.0), 1.3, 1.3)
                p.setBrush(QColor(255, 235, 176, 190))
                p.drawRoundedRect(QRectF(-3.4, -3.4, 4.6, 1.4), 0.6, 0.6)
                # 热气：三缕细汽从吐司顶端往上冒、穿出云层（白色画在白云上
                # 等于没有，所以用带一点暖灰的雾色，并且在云外也能看到）
                p.setBrush(Qt.NoBrush)
                for k in range(3):
                    ph = t * 1.9 + k * 1.7
                    hx = -5.6 + 5.6 * k
                    a_ = int(96 + 58 * math.sin(ph * 1.3))
                    if a_ <= 6:
                        continue
                    p.setPen(QPen(QColor(202, 184, 164, a_), 1.8,
                                  Qt.SolidLine, Qt.RoundCap))
                    yy = -7.2 - 1.0 * math.sin(ph * 0.7)
                    st = QPainterPath()
                    st.moveTo(hx, yy)
                    st.cubicTo(hx - 2.4, yy - 2.8, hx + 2.6, yy - 5.0,
                               hx - 0.5, yy - 7.4)
                    st.cubicTo(hx - 2.2, yy - 9.0, hx + 1.2, yy - 9.6,
                               hx + 0.6, yy - 10.4)
                    p.drawPath(st)
                # 闪光：吐司右上角的小四角星，明暗闪烁
                tw_ = 0.55 + 0.45 * math.sin(t * 4.6)
                p.setPen(QPen(QColor(255, 218, 140, int(225 * tw_)), 1.6,
                              Qt.SolidLine, Qt.RoundCap))
                p.drawLine(QPointF(9.0 - 2.6 * tw_, -10.5),
                           QPointF(9.0 + 2.6 * tw_, -10.5))
                p.drawLine(QPointF(9.0, -10.5 - 2.6 * tw_),
                           QPointF(9.0, -10.5 + 2.6 * tw_))
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
        # 画布已加高到 400（见 DW, DH），圆心落在角色中轴 y≈201。
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

    def paintEvent(self, ev):
        """绘制编排：只负责坐标系与绘制顺序，具体每一块交给对应的 _draw_*。
            ┌ 地面投影（身体组之外，跟着离地高度变化）
            └ 身体组（平移/旋转/挤压/朝向镜像之后）
                底图 → 尾巴条带 → 眼睛 → 嘴 → 头顶幻想气泡
            ┌ 组外前景（不受身体变换影响：面包/乌云/粒子/气泡/状态牌）"""
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing, True)
        p.setRenderHint(QPainter.TextAntialiasing, True)
        p.setRenderHint(QPainter.SmoothPixmapTransform, True)
        p.scale(self.width() / DW, self.width() / DW)   # 设计坐标 -> 窗口坐标
        p.setPen(Qt.NoPen)

        f = self._frame_ctx()        # 本帧共享量（弹簧快照/视线/表情显形度）
        pose = self._pose(f)         # 呼吸 / 摇摆 / 弹跳 / 颤抖
        self._draw_shadow(p, pose)

        p.save()
        self._apply_body_pose(p, pose, f)   # 平移 / 旋转 / 挤压 / 镜像
        self._draw_body(p, f)               # 底图 + 尾巴条带
        # 摇头（吃饱后还塞面包）：眼/嘴/眉整体左右甩，头顶幻想泡不跟
        nod = self._nod_offset()
        if nod != 0.0:
            p.save()
            p.translate(nod, 0.0)
            p.rotate(nod * 0.10)
        self._draw_eyes(p, f)
        self._draw_mouth(p, f)
        if nod != 0.0:
            p.restore()
        self._draw_fantasy(p, f)            # 头顶面包幻想泡
        self._draw_sleep_bubble(p, f)       # 设定：在泡泡里睡觉
        p.restore()

        self._draw_foreground(p, f)         # 组外特效与状态牌

        # 橘子汁特效层：把汁滴换算到全局屏幕坐标后交给独立的透明窗绘制，
        # 这样汁水能飞出宠物自己的小窗口，360° 无边界溅射（无汁滴则隐藏）。
        jf = getattr(self, "_juice_fx", None)
        if jf is not None and not PREVIEW_MODE:
            jf.refresh(self)

    def _nod_offset(self):
        """摇头位移（设计 px）：吃饱还喂时，脸左右甩三下（幅度指数衰减）。
        返回 0 = 不摇头（绝大多数帧）。"""
        if self.t >= self._nod_until:
            return 0.0
        d = self._nod_until - self.t          # 还剩多久
        el = self._nod_dur - d                # 已经摇了多久
        amp = (8.5 + 1.6 * self._nod_n) * math.exp(-0.55 * el)
        return amp * math.sin(el / 0.42 * math.tau)

    def _draw_hunger_tag(self, p):
        """饱食度牌：左上侧小深棕牌（面包图标 + 进度条 + 数值）。
        >50 橙 / 30-50 黄 / <30 红，随饥饿程度变色。"""
        hg = self._meta.get("hunger", 80.0)
        p.save()
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

    def _mouth_open(self):
        """happy 状态下的嘴开合：0=闭，1=全开（张嘴→吞入→闭嘴）。"""
        if self.state != "happy":
            return 0.0
        if self.phase == "bread":
            k = clamp((self.t - self.phase_t0) / 0.55, 0, 1)
            return math.sin(math.pi * min(1.0, k * 1.25))
        return 0.0

    # ---------- 特效绘制 ----------
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

    def _draw_particles(self, p):
        for pt in self.particles:
            # 实时运行时橘子汁由 JuiceOverlay 在全局坐标绘制（能飞出窗口、
            # 无范围框），这里跳过，免得再画一份被窗口矩形裁掉的残影。
            # 预览图（--shot）仍走本地绘制，方便截图展示。
            if pt.kind == "juice" and not PREVIEW_MODE:
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
            elif pt.kind == "sweat":
                # 汗滴：尖顶圆底（复用泪滴形），缓缓下滑渐隐
                r = pt.size * (0.85 + 0.3 * min(1.0, age))
                p.rotate(math.degrees(pt.rot))
                p.setPen(Qt.NoPen)
                p.setBrush(QColor(158, 205, 235, int(205 * a)))
                self._teardrop(p, 0, 0, r * 1.6, r * 2.0)
                p.setBrush(QColor(255, 255, 255, int(150 * a)))
                p.drawEllipse(QPointF(-r * 0.12, r * 0.05), r * 0.15, r * 0.2)
                p.setBrush(Qt.NoBrush)
            elif pt.kind == "rumble":
                # 咕咕叫声波：两道波浪纹 + 小圆点，从肚皮冒出上浮
                k2 = min(1.0, age / 0.35)
                sc2 = (0.6 + 0.4 * k2) * pt.size
                wob = math.sin(age * 6.0 + pt.rot) * 1.6
                p.translate(wob, 0)
                p.scale(sc2, sc2)
                p.setPen(QPen(QColor(255, 248, 236, int(215 * a)), 2.4,
                              Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
                p.setBrush(Qt.NoBrush)
                for row, half in ((0.0, 1.0), (7.5, -1.0)):
                    wv = QPainterPath()
                    wv.moveTo(-11, row)
                    wv.quadTo(-5.5, row - 4.5 * half, 0, row)
                    wv.quadTo(5.5, row + 4.5 * half, 11, row)
                    p.drawPath(wv)
                p.setPen(Qt.NoPen)
                p.setBrush(QColor(255, 248, 236, int(180 * a)))
                p.drawEllipse(QPointF(15.5, -7.5), 1.9, 1.9)
                p.drawEllipse(QPointF(-15.5, -9.5), 1.5, 1.5)
                p.setBrush(Qt.NoBrush)
            elif pt.kind == "note":
                # 音符 ♪：符头 + 符干 + 小旗，从肚皮飘出表示肚子在唱歌
                k2 = min(1.0, age / 0.3)
                sc2 = (0.6 + 0.4 * k2) * pt.size
                wob = math.sin(age * 5.0 + pt.rot) * 1.5
                p.translate(wob, 0)
                p.rotate(-12)
                p.scale(sc2, sc2)
                col = QColor(255, 248, 236, int(222 * a))
                p.setPen(Qt.NoPen)
                p.setBrush(col)
                p.drawEllipse(QPointF(-3.2, 6.5), 4.0, 3.1)        # 符头
                p.setPen(QPen(col, 2.2, Qt.SolidLine, Qt.RoundCap))
                p.drawLine(QPointF(0.6, 6.0), QPointF(0.6, -8.5))  # 符干
                p.setPen(Qt.NoPen)
                flag = QPainterPath()
                flag.moveTo(0.6, -8.5)
                flag.quadTo(8.0, -6.0, 5.2, 1.0)
                flag.quadTo(6.4, -4.5, 0.6, -3.5)
                p.drawPath(flag)                                   # 小旗
                p.setBrush(Qt.NoBrush)
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

    def _draw_bubble(self, p):
        """对话气泡：框型 + 皮肤随情绪切换（主题表见 BUBBLE_THEMES）。
          cloud 奶油云泡泡（日常） / burst 带刺爆炸（生气） / round 圆泡泡（打嗝）
          / zzz  睡泡泡里的 Zzz（睡眠）
        另有状态皮肤：傲娇粉+爱心 · 果汁橙+汁滴 · 晕车浅绿+摇摆 · 可怜蓝+泪滴。
        统一：幼圆字体（生气用加粗硬体）、上亮下沉渐变、左上高光、
        easeOutBack 弹性放大淡入 + 淡出，文字自适应换行。"""
        if not self.bubble_text or self.t > self.bubble_until:
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
        y_b = 64.0                                   # 气泡底边（尾巴根）
        bx = clamp(self.BCX - w / 2.0, 10.0, DW - 10.0 - w)

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
        p.drawText(QRectF(bx + 15, y_b - h, w - 30, h),
                   Qt.AlignHCenter | Qt.AlignVCenter | Qt.TextWordWrap,
                   self.bubble_text)
        p.restore()

    # ================= 互动 =================
    def _touch(self):
        """任何交互的统一入口：更新 last_interact；睡眠中则触发
        伸懒腰唤醒动画（先压扁 -> 0.38s 后拉长回弹）。"""
        if self.state == "sleep" and self.phase == "idle":
            self.phase = "wake"
            self.phase_t0 = self.t
            self._wake2 = False
            self._sq.kick(-2.0)
        self.last_interact = self.t

    def feed(self):
        """喂一口面包（+35 饱食度）。

        规则（2026-10-18 修正，此前"满 100 还能继续吃、要靠 12 秒连塞
        三口才吃撑"根本摸不到，用户实际看不到"饱到吃不了"）：
        · 饱食度 < 99：一定吃得进去，+35，超出 100 的部分丢弃——
          65~99 喂完正好停在 100（所以喂食是能达到 100 的）；
        · 饱食度 >= 99（吃饱）：**摇头拒收**——脸左右甩三下 + 肚皮
          当场鼓起来 + 打个嗝「嗝～」（圆形泡泡框台词），鼓肚持续 6 秒；
          这期间再点只会小幅鼓一下，不刷屏。于是"饱到吃不了"在喂满
          后的下一口立刻可见。
        """
        if self.phase != "idle":
            return
        before = self._meta.get("hunger", 80.0)
        if before >= 99.0:                       # 吃饱了：摇头拒收（吃撑状态）
            first = self.t >= self._stuffed_until  # 鼓肚消了再来：算新的一次
            self._stuffed_until = self.t + 6.0
            self._stuffed.snap(1.0)              # 肚皮立刻圆起来
            self._sq.kick(1.3 if first else 0.5)
            # 摇头拒绝：脸左右甩三下，幅度随"已经拒了几次"略微加大
            self._nod_until = self.t + self._nod_dur
            self._nod_n = 0 if first else min(6, self._nod_n + 1)
            if first:                            # 台词只在刚吃撑时播，避免刷屏
                self._say(self._line("no_more"), 3.0, "round")
            self.floats.append(("不～要～", self.mouth_center[0] + 34,
                                self.mouth_center[1] - 52, self.t))
            self.floats.append(("嗝～", self.mouth_center[0] - 26,
                                self.mouth_center[1] - 34, self.t))
            for i in range(3):                   # 打嗝小雾泡
                self.particles.append(Particle(
                    "steam", self.mouth_center[0] + random.uniform(-12, 12),
                    self.mouth_center[1] - 14, self.t - i * 0.1))
            return
        self.phase = "bread"
        self.phase_t0 = self.t
        self._sq.kick(-2.2)          # 张嘴前的期待拉伸
        self._set_state("happy")
        self._meta["fed"] = self._meta.get("fed", 0) + 1
        # +35 溢出 100 的部分丢弃（65~99 也能喂，吃完就是 100）
        self._meta["hunger"] = clamp(before + 35.0, 0.0, 100.0)

    # ---------- 拖拽投喂（面包跟随鼠标，松在嘴边才吃） ----------
    def _mouth_global(self):
        """嘴在世界坐标里的位置（缩放/移动后每帧算）。"""
        s = self.width() / DW
        return QPoint(int(self.pos().x() + self.mouth_center[0] * s),
                      int(self.pos().y() + self.mouth_center[1] * s))

    def _close_bread(self):
        if self._bread is not None:
            b, self._bread = self._bread, None
            b.stop()

    def _drop_crumb(self, gpos):
        """在松手点下方留一小块面包渣，并让它在视线里待着（5 秒后淡出）。"""
        scr = self._scr_rect()
        cm = Crumb(gpos, scr.bottom())
        self._crumbs = [c for c in self._crumbs if c.alive][:4]
        self._crumbs.append(cm)
        # 溅起几粒面包屑，落在地上
        for i in range(4):
            pt = Particle("crumb_dust", cm.gpos.x() - self.x(),
                          cm.gpos.y() - self.y() + random.uniform(-4, 4),
                          self.t)
            pt.vx = random.uniform(-26, 26)
            pt.vy = random.uniform(-58, -22)
            self.particles.append(pt)
        # 过一会儿小声心疼一句（别抢了"掉地上了"那句的位置）
        if self.bubble_until < self.t + 0.9:
            QTimer.singleShot(1400, self._crumb_line)

    def _crumb_line(self):
        """残渣落地 1.4 秒后的一句心疼话（要等前一句台词说完）。"""
        if self._crumbs and self.t >= self.bubble_until:
            self._say(self._line("crumb"), 2.8)

    def _crumb_gaze(self):
        """有没有正在"可惜"的残渣：EJEE 的视线会先落在它身上。"""
        self._crumbs = [c for c in self._crumbs
                        if c.alive and time.time() - c.t0 <= Crumb.HOLD + 0.4]
        return self._crumbs[-1] if self._crumbs else None

    def _take_bread(self):
        """拿起面包：之后面包跟着光标走，拖到嘴边松手才会吃掉。"""
        if self._bread is not None:
            return
        self._bread = BreadCursor()
        self._bread.dropped.connect(self._drop_bread)
        self._bread.show()
        self._say("给～把面包拖到我嘴边放下来。", 3.2)

    @staticmethod
    def _ding():
        """番茄钟到点提示音：优先播放 Windows 柔和的系统「Asterisk」
        （异步、不打断手头的事），失败/非 Windows 再退回 Qt 蜂鸣。"""
        try:
            if sys.platform == "win32":
                import winsound
                winsound.PlaySound("SystemAsterisk",
                                   winsound.SND_ALIAS | winsound.SND_ASYNC)
                return
        except Exception:
            pass
        QApplication.beep()

    def _drop_bread(self, gpos):
        """松手：落在嘴边就张嘴吃掉（吃饱了会被拒收），否则面包掉地上
        ——留一小块残渣在落点下方，EJEE 会可怜巴巴地盯着看一会儿。"""
        self._close_bread()
        mg = self._mouth_global()
        if math.hypot(gpos.x() - mg.x(), gpos.y() - mg.y()) <= 48 * self.size:
            # 起飞点 = 松手的屏幕坐标换算回设计坐标（面包从被放开的地方
            # 飞进嘴，而不是从身前的固定位置凭空出现）
            s = self.width() / DW
            self._feed_from = (clamp((gpos.x() - self.x()) / s, -30.0, DW + 30.0),
                               clamp((gpos.y() - self.y()) / s, -30.0, DH + 30.0))
            self.phase = "idle"              # 喂食相位优先，免得这一口被吞
            self.feed()
            if self.phase == "bread":        # 真吃到了才喊"啊呜"（拒收时不喊）
                self._say("啊呜——！", 1.6)
            else:
                self._feed_from = None       # 被拒收：没有面包飞行动画
        else:
            self._sq.kick(-0.6)
            self._say("啊……面包掉地上了。", 2.2)
            self._drop_crumb(gpos)

    def _end_interact(self):
        self.phase = "idle"
        self.bubble_text = ""
        self._feed_from = None       # 拖拽投喂的起飞点用完即弃

    def _save(self):
        d = {"size": round(self.size, 2)}
        d.update(self._meta)
        d["x"] = int(self.x())
        d["y"] = int(self.y())
        d["last_seen"] = time.time()
        save_data(d)

    # ---------- 启动落位：记住上次离开的位置 ----------
    def _restore_position(self):
        """启动落位：优先回到上次离开的位置（窗口中心仍在某块屏幕的
        可用区内，多屏/拔掉副屏都不会把宠物放到看不见的地方），
        否则回主屏右下角默认位。"""
        r = getattr(self, "_restore_pos", None)
        if r is not None:
            c = QPoint(r[0] + self.width() // 2, r[1] + self.height() // 2)
            scr = QApplication.screenAt(c)
            if scr is not None:
                ag = scr.availableGeometry()
                nx = clamp(r[0], ag.left(),
                           max(ag.left(), ag.right() - self.width()))
                # 底部透明区允许溢出屏幕：宠物脚底仍能贴住任务栏
                ny = clamp(r[1], ag.top(),
                           max(ag.top(), ag.bottom() - self.height()
                               + self._win_pad_b()))
                self.move(int(nx), int(ny))
                return
        self._default_pos()

    def _win_pad_b(self):
        """画布下方那块只给睡眠正圆泡泡的透明区（px）。落位/回位/缩放时
        不该把它算进"可见高度"，否则宠物会被顶起来悬空。"""
        return int(round((DH - DH_CHAR) * self.size))

    def _default_pos(self):
        scr = QApplication.primaryScreen()
        ag = scr.availableGeometry() if scr else QRectF(0, 0, 1920, 1080)
        self.move(int(ag.right() - self.width() - 40),
                  int(ag.bottom() - self.height() + self._win_pad_b() - 60))

    # ---------- 开机自动启动（HKCU\...\Run，仅 Windows）----------
    @staticmethod
    def _autostart_cmd():
        """自启动命令行：打包后是 exe 本身；源码运行则是 解释器 + 脚本。"""
        if getattr(sys, "frozen", False):
            return '"%s"' % sys.executable
        return '"%s" "%s"' % (sys.executable, os.path.abspath(__file__))

    def _get_autostart(self):
        if sys.platform != "win32":
            return False
        try:
            import winreg
            with winreg.OpenKey(
                    winreg.HKEY_CURRENT_USER,
                    r"Software\Microsoft\Windows\CurrentVersion\Run",
                    0, winreg.KEY_READ) as k:
                winreg.QueryValueEx(k, "EJEE")
                return True
        except Exception:
            return False

    def _set_autostart(self, on):
        if sys.platform != "win32":
            return
        import winreg
        with winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Run",
                0, winreg.KEY_SET_VALUE) as k:
            if on:
                winreg.SetValueEx(k, "EJEE", 0, winreg.REG_SZ,
                                  self._autostart_cmd())
            else:
                try:
                    winreg.DeleteValue(k, "EJEE")
                except FileNotFoundError:
                    pass

    def _toggle_autostart(self, on):
        self._set_autostart(on)
        if getattr(self, "tray_act_boot", None) is not None:
            self.tray_act_boot.setProperty("_switchOn", on)
            if getattr(self, "_tray_menu", None) is not None:
                self._tray_menu.update()
    def set_size(self, sz):
        # 统一走弹簧：右键菜单预设也享受缓动；存档在落定时由 _tick 完成
        self.target_size = clamp(sz, SIZE_MIN, SIZE_MAX)
        self._zoom_anchor = None

    def _apply_size(self, sz):
        """按弹簧当前值缩放窗口，并以冻结的光标锚点（或窗口中心）补偿位移。
        热区=整个窗口矩形，resize 后自动跟随；情绪逻辑用 self.size 自动适配。"""
        new = clamp(sz, SIZE_MIN, SIZE_MAX)
        # 锚点校验：光标已明显移开则退化为窗口中心缩放（只缩不挪）
        if self._zoom_anchor is not None:
            da_x, da_y, gp = self._zoom_anchor
            cur = QCursor.pos()
            if abs(cur.x() - gp.x()) > 80 or abs(cur.y() - gp.y()) > 80:
                self._zoom_anchor = None
        if self._zoom_anchor is not None:
            ax, ay = da_x, da_y
            anchor = gp
        else:
            ax, ay = DW / 2.0, DH / 2.0
            anchor = self.geometry().center()
        new_s = new                       # s = width/DW = size
        nx = round(anchor.x() - ax * new_s)
        ny = round(anchor.y() - ay * new_s)
        self.resize(int(round(DW * new)), int(round(DH * new)))
        # 屏幕钳制：缩放后窗口完整留在可用区内（小屏放不下时退到贴顶）
        scr = self._scr_rect()
        nx = clamp(nx, scr.left(), max(scr.left(), scr.right() - self.width()))
        pad_b = (DH - DH_CHAR) * new    # 底部透明区不计入可见高度
        ny = clamp(ny, scr.top(),
                   max(scr.top(), scr.bottom() - self.height() + pad_b))
        if (nx, ny) != (self.x(), self.y()):
            self.move(nx, ny)
        self.size = new

    # ================= 鼠标 =================
    def mousePressEvent(self, e):
        self._touch()
        if e.button() == Qt.LeftButton:
            self._press_pos = e.globalPosition().toPoint()
            self._dragging = False

    def enterEvent(self, e):
        self._hover = True            # 悬停：饿了会努力抬头看鼠标
        super().enterEvent(e)

    def leaveEvent(self, e):
        self._hover = False           # 移开：又无力地趴下去
        super().leaveEvent(e)

    def _zoom_steps(self, delta, gp):
        """Shift+滚轮缩放核心：窗口内 wheelEvent 与穿透模式全局钩子共用。
        delta = 滚轮步进（120 的整数倍，正负=放大/缩小）；
        gp = 光标全局坐标（冻结锚点，缩放全程光标指向的设计坐标钉在原地）。"""
        self._touch()
        if self._dragging or delta == 0:
            return
        old = self.target_size
        if not self._zooming:                # 手势起点：记起始尺寸供台词用
            self._zoom_from = self.size
        self.target_size = clamp(old * (1.0015 ** delta), SIZE_MIN, SIZE_MAX)
        # 边界反馈：顶到上限继续放大 -> 压扁（被"顶住"）；缩到下限继续缩小 -> 拉伸
        # _sq 是叠加形变（clamp ±0.22、目标恒 0），与情绪动画共用不冲突
        if delta > 0 and self.target_size >= SIZE_MAX - 1e-9 \
                and old >= SIZE_MAX - 1e-9:
            self._sq.kick(1.4)
        elif delta < 0 and self.target_size <= SIZE_MIN + 1e-9 \
                and old <= SIZE_MIN + 1e-9:
            self._sq.kick(-1.4)
        # 冻结光标锚点：缩放全程光标指向的设计坐标钉在原地
        s_old = self.width() / DW
        self._zoom_anchor = ((gp.x() - self.x()) / s_old,
                             (gp.y() - self.y()) / s_old, gp)

    def wheelEvent(self, e):
        # Shift+滚轮缩放：仅悬停在本窗口上时触发，无 Shift 不响应（防误触）
        if self._dragging or not (e.modifiers() & Qt.ShiftModifier):
            e.ignore()
            return
        delta = e.angleDelta().y() or e.angleDelta().x()
        if delta == 0:
            e.ignore()
            return
        self._zoom_steps(delta, e.globalPosition().toPoint())
        e.accept()

    def mouseDoubleClickEvent(self, e):
        # 双击：重置 1.0x（撤销这次双击第一击挂起的喂食）
        if e.button() == Qt.LeftButton:
            self._touch()
            self._feed_pending = False
            self._dbl_until = time.time() + 0.35
            self._zoom_anchor = None          # 复位以窗口中心为锚
            self._zoom_from = 1.0             # 复位视为无缩放，避免触发缩放台词
            self.target_size = 1.0
            self._sq.kick(1.6)                # 轻弹一下作为"复位"反馈
            self._say(self._line("double_click"), 2.2)
            e.accept()

    def _do_feed(self):
        # 单击喂食延迟派发：双击重置到达时撤单，避免双击误触发两次喂食；
        # 赶上面包等其他相位时稍等重试——连点不再被悄悄吞掉（以前点快了
        # 有一半点击没有任何反应，用户会以为"喂不进去/到不了 100"）
        if not self._feed_pending:
            return
        if self.phase != "idle" and self.t < self._feed_deadline:
            QTimer.singleShot(90, self._do_feed)
            return
        self._feed_pending = False
        self.feed()

    def mouseMoveEvent(self, e):
        self._touch()          # 悬停唤醒睡眠（需 mouseTracking）
        self._hover = True     # 移动中：眼巴巴跟着鼠标看
        if self._press_pos is None:
            return
        gp = e.globalPosition().toPoint()
        d = gp - self._press_pos
        now = time.time()
        dtm = max(0.008, now - self._last_move_t)
        if self._dragging:
            # 移动速度（px/s）：供挤压拉伸与倾斜使用
            self._dvx = clamp((gp.x() - self._press_pos.x()) / dtm, -3000, 3000)
            self._dvy = clamp((gp.y() - self._press_pos.y()) / dtm, -3000, 3000)
        self._last_move_t = now
        if d.manhattanLength() > 6:
            if not self._dragging:           # 拖拽起步：喊一声（带冷却）
                self._dragging = True
                if self.t >= self._next_drag_line:
                    self._next_drag_line = self.t + 18.0
                    self._say(self._line("drag"), 2.4)
            self.move(self.pos() + d)
            self._press_pos = gp
            # 拖到屏幕边缘 -> 生气 + 撞击挤压
            g = self.frameGeometry()
            scr = self._scr_rect()
            if (g.left() <= scr.left() + 8 or g.right() >= scr.right() - 8
                    or g.top() <= scr.top() + 8
                    or g.bottom() >= scr.bottom() - 8):
                was_angry = self.t < self.angry_until
                self.angry_until = self.t + 2.5
                self._sq.kick(2.6)
                if not was_angry:      # 刚撞上边：骂一句（带刺爆炸框）
                    self._say(self._line("angry"), 2.0, "burst")
                # ---- 疯狂来回拉扯 -> 晕车（比"撞边生气"更严重）----
                self._edge_shake(d.x())

    def _edge_shake(self, dx):
        """边缘拉扯检测：贴着屏幕边时记录「这一下往哪边拽」，2.6 秒内
        方向反了 3 次（= 用户在疯狂来回拉扯）就触发晕车。
        独立成方法便于仿真覆盖；dx 为本帧的水平拖拽量。"""
        if abs(dx) < 2.0:
            return                            # 几乎没动，不算一次拉扯
        sdir = 1 if dx > 0 else -1
        self._shake_log = [r for r in self._shake_log
                           if self.t - r[0] < 2.6]
        if self._shake_log and self._shake_log[-1][1] != sdir:
            self._shake_log.append((self.t, sdir))
            if len(self._shake_log) >= 4:     # 2.6 秒内 4 次方向变更
                self._shake_log.clear()
                self._start_dizzy()
        elif not self._shake_log:
            self._shake_log.append((self.t, sdir))

    def _click_zone(self, e):
        """点击落点分区（视觉设计坐标）：tail 尾巴 / head 头部（含眼区上方）
        / body 身体。eye_pos 是设计坐标；朝左时 x 轴镜像。"""
        scale = self.width() / DW
        dx = e.position().x() / scale
        if self.facing == -1:
            dx = 2.0 * self.BCX - dx      # 绕身体中轴镜像（非窗口中线）
        dy = e.position().y() / scale
        # 尾巴判定优先：橘子尾巴是右侧竖长瓣（实测设计 x≈300..347、
        # y≈172..318，上半段与身体融合、下半段可摆），用"到竖线段距离"
        # 的胶囊判定覆盖整条尾巴，比椭圆更贴合这个竖长形状
        cy_ = clamp(dy, 190.0, 310.0)
        if math.hypot(dx - 323.0, dy - cy_) <= 30.0:
            return "tail"
        eye_y = min(self.eye_pos["eye_l"][1], self.eye_pos["eye_r"][1])
        if dy < eye_y:
            return "head"
        return "body"

    def mouseReleaseEvent(self, e):
        if e.button() == Qt.LeftButton and self._press_pos is not None:
            if not self._dragging:
                # 分区交互：摸头 / 抓尾巴 / 喂食（延迟派发给双击留撤单窗口）
                # 手里拿着面包时，这一下点击留给"放下面包"
                if self._bread is None and time.time() >= self._dbl_until:
                    zone = self._click_zone(e)
                    if zone == "tail":
                        self._mischief()
                    elif zone == "head":
                        self._pat()
                    else:
                        self._feed_pending = True
                        self._feed_deadline = self.t + 2.0
                        QTimer.singleShot(280, self._do_feed)
            else:
                v = math.hypot(self._dvx, self._dvy)
                if v > 80:                   # 松手惯性甩动
                    self._glide = [self._dvx * 0.85, self._dvy * 0.85]
                self._sq.kick(clamp(self._dvx / 900.0, -2.0, 2.0))
            self._press_pos = None
            self._dragging = False

    def _build_menu(self):
        """构建共享右键菜单（窗口右键 / 穿透模式全局右键钩子共用）。
        每次弹出重建，状态（穿透勾选、当前尺寸）自然是最新的。"""
        menu = SoftMenu(self)
        act_take = menu.addAction(_menu_icon("hand"), "拿起面包（拖到嘴边）")
        act_take.triggered.connect(self._take_bread)
        menu.addAction(_menu_icon("heart"), "陪伴档案").triggered.connect(
            self._show_stats)
        act_pomo = menu.addAction(_menu_icon("clock"), self._pomo_label())
        act_pomo.triggered.connect(self._pomo_toggle)
        menu.addSeparator()
        act_pass = menu.addAction(_menu_icon("ghost"), "穿透模式")
        act_pass.setProperty("_switch", True)
        act_pass.setProperty("_switchOn", self._pass)
        act_pass.triggered.connect(
            lambda checked=False: self._toggle_pass(not self._pass))
        size_menu = SoftMenu(menu)
        size_menu.setTitle("尺寸")
        size_menu.setIcon(_menu_icon("size"))
        for label, sz in SIZES:
            on = abs(sz - self.size) < 0.01
            act = size_menu.addAction(
                _menu_icon("radio_on" if on else "radio_off"), label)
            act.triggered.connect(lambda checked=False, s=sz: self.set_size(s))
        menu.addMenu(size_menu)
        menu.addSeparator()
        act_quit = menu.addAction(_menu_icon("quit"), "退出")
        return menu, act_quit

    def _popup_menu(self, gpos):
        menu, act_quit = self._build_menu()
        chosen = menu.exec(gpos)
        if chosen is act_quit:
            QApplication.quit()

    def contextMenuEvent(self, e):
        self._touch()
        self._popup_menu(e.globalPos())

    def _toggle_pass(self, on):
        """穿透模式 = OS 级点击穿透 + 半透明透视 + 全局右键钩子。
        穿透必须走 Qt 官方通道 WindowTransparentForInput——QWindowsWindow
        会把它翻译成 WS_EX_TRANSPARENT 并在每次重算窗口样式时保留；
        直接 SetWindowLongW 会被 Qt 的样式缓存覆盖掉而失效。
        该 flag 会触发原生窗口重建，需重新 show()。
        透明度由 _opac 弹簧驱动（_tick），淡出至 0.30 露出身后内容。
        穿透下窗口收不到任何鼠标事件，右键由 WH_MOUSE_LL 全局钩子
        拦截（光标在窗口矩形内时吞掉并弹共享菜单）；恢复也可走托盘。"""
        self._pass = bool(on)
        self.setAttribute(Qt.WA_TransparentForMouseEvents, self._pass)
        self.setWindowFlag(Qt.WindowTransparentForInput, self._pass)
        self.show()          # setWindowFlag 会隐藏窗口，恢复原位重显
        if self._pass:
            self._install_mouse_hook()
        else:
            self._uninstall_mouse_hook()
        # 同步托盘菜单开关（共享右键菜单每次弹出按 _pass 重建，
        # 托盘菜单是常驻的，triggered 后在此对齐并重绘）
        if getattr(self, "tray_act_pass", None) is not None:
            self.tray_act_pass.setProperty("_switchOn", self._pass)
            if getattr(self, "_tray_menu", None) is not None:
                self._tray_menu.update()

    # ---- 穿透模式的全局右键钩子 ----
    def _install_mouse_hook(self):
        if self._mouse_hook or sys.platform != "win32":
            return
        import ctypes
        from ctypes import wintypes
        user32 = ctypes.windll.user32
        kernel32 = ctypes.windll.kernel32

        class POINT(ctypes.Structure):
            _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]

        class MSLLHOOKSTRUCT(ctypes.Structure):
            _fields_ = [("pt", POINT),
                        ("mouseData", wintypes.DWORD),
                        ("flags", wintypes.DWORD),
                        ("time", wintypes.DWORD),
                        ("dwExtraInfo", ctypes.POINTER(wintypes.ULONG))]

        WM_RBUTTONDOWN = 0x0204
        WM_MOUSEWHEEL = 0x020A
        VK_SHIFT = 0x10
        WH_MOUSE_LL = 14

        def proc(n_code, w_param, l_param):
            if n_code >= 0 and w_param == WM_RBUTTONDOWN:
                info = ctypes.cast(l_param,
                                   ctypes.POINTER(MSLLHOOKSTRUCT)).contents
                g = self.frameGeometry()
                if (g.left() <= info.pt.x <= g.right()
                        and g.top() <= info.pt.y <= g.bottom()):
                    # 钩子回调内不做 UI，投递到主事件循环；吞掉该右键
                    QTimer.singleShot(0, self._pass_context_menu)
                    return 1
            elif n_code >= 0 and w_param == WM_MOUSEWHEEL:
                # 穿透下窗口收不到滚轮：Shift + 光标压在宠物身上 -> 缩放
                # （与窗口内 wheelEvent 同一规则；无 Shift 一律放行不吞）
                if user32.GetKeyState(VK_SHIFT) & 0x8000:
                    info = ctypes.cast(
                        l_param, ctypes.POINTER(MSLLHOOKSTRUCT)).contents
                    g = self.frameGeometry()
                    if (g.left() <= info.pt.x <= g.right()
                            and g.top() <= info.pt.y <= g.bottom()):
                        d = (info.mouseData >> 16) & 0xFFFF
                        if d >= 0x8000:            # 有符号 16 位
                            d -= 0x10000
                        px, py = info.pt.x, info.pt.y
                        QTimer.singleShot(
                            0, lambda: self._zoom_steps(
                                d / 120.0, QPoint(px, py)))
                        return 1
            return user32.CallNextHookEx(None, n_code, w_param, l_param)

        self._hook_proc = ctypes.WINFUNCTYPE(
            ctypes.c_int, ctypes.c_int, wintypes.WPARAM,
            wintypes.LPARAM)(proc)          # 持引用防 GC
        self._mouse_hook = user32.SetWindowsHookExW(
            WH_MOUSE_LL, self._hook_proc,
            kernel32.GetModuleHandleW(None), 0)

    def _uninstall_mouse_hook(self):
        if self._mouse_hook:
            ctypes.windll.user32.UnhookWindowsHookEx(self._mouse_hook)
            self._mouse_hook = None
            self._hook_proc = None

    def _pass_context_menu(self):
        """穿透模式下右键宠物弹出的菜单（全局钩子触发）。"""
        if self._pass:
            self._popup_menu(QCursor.pos())

    def _toggle_visible(self):
        if self.isVisible():
            self.hide()
        else:
            self.show()

    def _on_tray_activated(self, reason):
        # 左键单击托盘图标：恢复显示（穿透/隐藏后的兜底出口）
        if reason == QSystemTrayIcon.Trigger:
            self.show()

    # ================= 托盘 =================
    def _init_tray(self):
        if not QSystemTrayIcon.isSystemTrayAvailable():
            return
        icon_path = res_path("ejee_icon.png")
        if os.path.exists(icon_path):
            self.tray = QSystemTrayIcon(QIcon(icon_path), self)
        else:
            pm = QPixmap(64, 64)
            pm.fill(Qt.transparent)
            p = QPainter(pm)
            p.setRenderHint(QPainter.Antialiasing, True)
            p.setBrush(BODY_TOP)
            p.drawEllipse(6, 12, 52, 40)
            p.setBrush(CREAM)
            p.drawEllipse(16, 34, 32, 16)
            p.setBrush(EYE_DARK)
            p.drawEllipse(18, 24, 9, 11)
            p.drawEllipse(37, 24, 9, 11)
            p.end()
            self.tray = QSystemTrayIcon(QIcon(pm), self)
        menu = SoftMenu()          # 与右键菜单同一套奶油卡片皮肤
        menu.addAction(_menu_icon("hand"), "拿起面包（拖到嘴边）").triggered.connect(
            self._take_bread)
        menu.addAction(_menu_icon("heart"), "陪伴档案").triggered.connect(
            self._show_stats)
        self.tray_act_pomo = menu.addAction(_menu_icon("clock"),
                                            "开始番茄钟…")
        self.tray_act_pomo.triggered.connect(self._pomo_toggle)
        menu.addSeparator()
        act_pass = menu.addAction(_menu_icon("ghost"), "穿透模式")
        act_pass.setProperty("_switch", True)
        act_pass.setProperty("_switchOn", self._pass)
        act_pass.triggered.connect(
            lambda checked=False: self._toggle_pass(not self._pass))
        self.tray_act_pass = act_pass   # _toggle_pass 里同步开关状态
        self._tray_menu = menu
        menu.addAction(_menu_icon("eye"), "显示 / 隐藏").triggered.connect(
            self._toggle_visible)
        act_reset = menu.addAction(_menu_icon("reset"), "重置大小 1.0x")
        act_reset.triggered.connect(lambda checked=False: self.set_size(1.0))
        menu.addSeparator()
        act_boot = menu.addAction(_menu_icon("star"), "开机自动启动")
        act_boot.setProperty("_switch", True)
        act_boot.setProperty("_switchOn", self._get_autostart())
        act_boot.triggered.connect(
            lambda checked=False: self._toggle_autostart(
                not self._get_autostart()))
        self.tray_act_boot = act_boot
        menu.addSeparator()
        size_menu = SoftMenu(menu)
        size_menu.setTitle("尺寸")
        size_menu.setIcon(_menu_icon("size"))
        self._tray_size_acts = []
        for label, sz in SIZES:
            act = size_menu.addAction(_menu_icon("radio_off"), label)
            act.triggered.connect(lambda checked=False, s=sz: self.set_size(s))
            self._tray_size_acts.append((sz, act))
        menu.addMenu(size_menu)
        menu.addSeparator()
        menu.addAction(_menu_icon("quit"), "退出").triggered.connect(
            QApplication.quit)

        def _sync():
            """托盘菜单常驻，弹出前刷新开关状态与番茄钟剩余时间。"""
            for sz, act in self._tray_size_acts:
                on = abs(sz - self.size) < 0.01
                act.setIcon(_menu_icon("radio_on" if on else "radio_off"))
            if self.tray_act_pass is not None:
                self.tray_act_pass.setProperty("_switchOn", self._pass)
            if getattr(self, "tray_act_boot", None) is not None:
                self.tray_act_boot.setProperty("_switchOn",
                                               self._get_autostart())
            self.tray_act_pomo.setText(self._pomo_label())

        menu.aboutToShow.connect(_sync)
        self.tray.setContextMenu(menu)
        self.tray.activated.connect(self._on_tray_activated)
        self.tray.setToolTip("EJEE 伊吉 · ISFP · 来自日山湖水公园\n"
                             "爱好：在泡泡里睡觉｜最爱：牛奶吐司｜吧嗒吧嗒～")
        self.tray.show()


class _PreviewCrumb:
    """预览专用的假面包渣：本身不绘制，只让 _bubble_theme 的气球解析
    走到「可怜蓝」皮肤（有残渣 + 平静状态）。"""
    t0 = 0.0


def main():
    global PREVIEW_MODE
    shot = "--shot" in sys.argv
    PREVIEW_MODE = shot            # 预览模式冻结视线，保证渲染可复现
    if shot:
        os.makedirs(PREVIEW_DIR, exist_ok=True)
        random.seed(20261017)      # 相位/微动作初值也固定，截图才能逐像素比对
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    pet = EjeePet()
    if shot:
        pet._meta["hunger"] = 80.0     # 预览用固定饱食度（不吃存档里的实时值）
        def snap(state):
            """预览用：切到目标状态并直接快照弹簧参数（运行时的弹簧
            过渡无法在无事件循环的截图模式下推进）。"""
            pet.phase = "idle"
            pet.bubble_text = ""
            pet.floats = []          # 飘字不会自动过期（截图模式下没有 _tick）
            pet._set_state(state)
            for key, s in pet.spr.items():
                s.snap(P[state][key])
            pet.cur = dict(P[state])
            pet.mouth_alt.snap(1.0 if state in ("surprised", "angry") else 0.0)
            pet.wink_l.snap(1.0 if state in ("happy", "surprised") else 0.0)
            pet.wink_r.snap(1.0 if state == "happy" else 0.0)
            pet.sleep_amt.snap(1.0 if state == "sleep" else 0.0)
            pet.mischief_amt.snap(1.0 if state == "mischief" else 0.0)
            pet.hungry_amt.snap(1.0 if pet._meta["hunger"] < 30.0 else 0.0)
            pet._shy_amt.snap(1.0 if state == "shy" else 0.0)
            pet._dizzy_amt.snap(1.0 if state == "dizzy" else 0.0)

        pet.t = 0.4
        pet._last_t = 0.4
        pet.grab().save(os.path.join(PREVIEW_DIR, "preview_idle.png"))
        # happy：面包飞入中段（大张嘴吐舌，ω 精灵已隐藏）
        pet.feed()
        pet._set_state("happy")
        for key, s in pet.spr.items():
            s.snap(P["happy"][key])
        pet.cur = dict(P["happy"])
        pet.mouth_alt.snap(1.0)       # 进食期替代嘴形全显
        pet.wink_l.snap(1.0)          # 开心闭眼
        pet.wink_r.snap(1.0)
        pet.t = 1.1
        pet._last_t = 1.1
        pet.phase_t0 = pet.t - 0.33   # 面包飞行至约 60% 处，嘴大张
        pet.grab().save(os.path.join(PREVIEW_DIR, "preview_happy.png"))
        snap("angry")
        pet.t = 2.6
        pet._last_t = 2.6
        pet._say("呜！尾巴不可以抓！", 3.0, "burst")
        pet.t = 2.95
        pet._last_t = 2.95
        pet.grab().save(os.path.join(PREVIEW_DIR, "preview_angry.png"))
        snap("surprised")
        pet.t = 4.0
        pet._last_t = 4.0
        pet.grab().save(os.path.join(PREVIEW_DIR, "preview_surprised.png"))
        snap("sleep")
        pet.t = 7.0
        pet._last_t = 7.0
        pet.particles.append(Particle("zzz", pet.BCX + 40,
                                      pet.head_top + 2, pet.t - 1.2))
        pet.particles.append(Particle("zzz", pet.BCX + 50,
                                      pet.head_top - 8, pet.t - 2.4))
        pet.grab().save(os.path.join(PREVIEW_DIR, "preview_sleep.png"))
        snap("idle")
        pet.particles.clear()
        pet.t = 8.6
        pet._last_t = 8.6
        pet._say("咕噜咕噜～最喜欢被你摸头了！再用橘子尾巴给你比个心哦～", 3.0)
        pet.t = 8.95          # 气泡入场动画完成后截（age=0.35s，全显）
        pet.grab().save(os.path.join(PREVIEW_DIR, "preview_bubble.png"))
        snap("idle")
        pet._meta["hunger"] = 12.0
        pet.hungry_amt.snap(1.0)
        pet.particles.clear()
        pet.t = 10.6
        pet._last_t = 10.6
        pet._fantasy = {"t0": pet.t - 0.9}    # 幻想气泡（展示期）
        pet.particles.append(Particle("sweat", pet.BCX - 64,
                                      pet.BCY - 130, pet.t - 0.5))
        pet.particles.append(Particle("sweat", pet.BCX + 70,
                                      pet.BCY - 124, pet.t - 0.2))
        pet.particles.append(Particle("note", pet.BCX + 34,
                                      pet.BCY - 40, pet.t - 0.6))
        pet.grab().save(os.path.join(PREVIEW_DIR, "preview_hungry.png"))
        snap("mischief")
        pet.hungry_amt.snap(0.0)      # 恶作剧预览回到正常体型（不然还是软趴的）
        pet._meta["hunger"] = 80.0
        pet.mischief_amt.snap(1.0)
        pet._mis_tail.snap(0.85)
        pet._mis_dir = 1.0
        pet.particles.clear()
        pet.t = 12.6
        pet._last_t = 12.6
        # 橘子汁 360° 全方向溅射（反映新行为：向四周大范围喷溅）
        jox, joy = pet.BCX + 145, pet.BCY - 18      # 尾尖喷汁点
        for k in range(9):
            ang = math.tau * k / 9.0
            sp = 560.0
            jp = Particle("juice", jox, joy, pet.t - 0.18)
            jp.vx, jp.vy = sp * math.cos(ang), sp * math.sin(ang) - 110.0
            jp.size *= 1.9
            jp.life *= 1.9
            pet.particles.append(jp)
        pet._say("嘿嘿，中计了吧！尝尝我的橘子汁攻击！", 3.0)
        pet.t = 12.95
        pet._last_t = 12.95
        pet.grab().save(os.path.join(PREVIEW_DIR, "preview_mischief.png"))
        pet.bubble_text = ""
        # 吃撑了：吃饱（>=99）后再喂一口 -> 拒收：鼓肚 + 打嗝
        pet._meta["hunger"] = 100.0
        snap("idle")
        pet.particles.clear()
        pet.floats.clear()
        pet.t = 17.0
        pet._last_t = 17.0
        pet.feed()                       # 真走拒收分支：鼓肚 + 摇头 + 嗝～
        pet._say("唔唔，肚子已经圆得装不下了～", 3.0, "round")
        pet.t = 17.11                # 摇到约 1/4 周期（脸甩到最侧）
        pet.grab().save(os.path.join(PREVIEW_DIR, "preview_stuffed.png"))
        pet._stuffed.snap(0.0)
        pet._nod_until = 0.0
        pet.bubble_text = ""
        # 番茄钟：进度环 + 最后一分钟"紧张期待"
        pet._meta["hunger"] = 80.0              # 先回到吃饱状态（上一张是饿的）
        snap("idle")
        pet.particles.clear()
        pet._fantasy = None
        pet.t = 15.0
        pet._last_t = 15.0
        pet._pomo_total = 25 * 60.0
        pet._pomo_end = pet.t + 42.0          # 剩 42 秒 -> 最后一分钟
        pet._pomo_nrv.snap(1.0)
        pet.grab().save(os.path.join(PREVIEW_DIR, "preview_pomo.png"))
        # 傲娇躲避：连摸 5 下 -> 直接闪现到别处（无身体形变）+ 别过头 + 傲娇台词（粉色爱心泡）
        snap("shy")
        pet._pomo_end = None           # 关掉番茄钟牌，别挡住气泡
        pet._shy_amt.snap(1.0)
        pet._shy_until = 1e9
        pet.particles.clear()
        pet.floats.clear()
        pet.t = 20.0
        pet._last_t = 20.0
        pet._say("够、够啦！摸太多次了啦……", 3.0)
        pet.t = 20.35
        pet.grab().save(os.path.join(PREVIEW_DIR, "preview_shy.png"))
        # 晕车：蚊香圈眼 + 「要吐泡泡了」（浅绿摇摆泡）
        snap("dizzy")
        pet._dizzy_amt.snap(1.0)
        pet._dizzy_until = 1e9
        pet._shy_amt.snap(0.0)
        pet.particles.clear()
        pet.t = 24.0
        pet._last_t = 24.0
        pet._say("吧嗒吧嗒……别晃啦，我要吐泡泡了！", 3.0)
        for i, (dx, dy) in enumerate(((18, -6), (34, -22), (4, -38))):
            bp = Particle("bubble", pet.mouth_center[0] + dx,
                          pet.mouth_center[1] - 14 + dy, pet.t - i * 0.12)
            bp.vx, bp.vy = 12.0 * i - 8, -26 - 8 * i
            pet.particles.append(bp)
        pet.t = 24.35
        pet.grab().save(os.path.join(PREVIEW_DIR, "preview_dizzy.png"))
        # 可怜层：盯着掉在地上的面包渣（表情复用 angry：怒眉 + 撇嘴；
        # 气泡换可怜蓝皮肤 + 底缘挂一滴泪——放一枚假残渣让主题解析走到 crumb）
        snap("idle")
        pet._dizzy_amt.snap(0.0)
        pet._dizzy_until = 0.0
        pet._pity.snap(1.0)
        pet.cur["puff"] = 1.0          # 预览：直接顶起怒容眉
        pet.mouth_alt.snap(1.0)        # 预览：直接顶起生气撇嘴
        pet._crumbs = [_PreviewCrumb()]
        pet.particles.clear()
        pet.t = 28.0
        pet._last_t = 28.0
        pet._say("呜……我的面包……", 3.0)
        pet.t = 28.35
        pet.grab().save(os.path.join(PREVIEW_DIR, "preview_pity.png"))
        pet._pity.snap(0.0)
        pet._crumbs = []
        print("previews saved")
        return
    pet._restore_position()      # 回到上次离开的位置（无效则主屏右下角）
    pet.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
