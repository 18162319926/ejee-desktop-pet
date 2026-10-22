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
      叶子只枯萎转土黄（不耷拉），波浪嘴（不流口水），肚子每隔几秒轻轻抽一下
      （咕咕叫，不再画黄色同心圆波），每 10 秒头顶飘一朵较大的海市蜃楼
      （云里的牛奶吐司 + 热气）2 秒后啵地破灭，跟着叹一口气
      + 头顶面包幻想气泡（2s 后"啵"地破灭）；眼睛保持原形不压扁
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
    · 设计坐标 DW,DH = 400×472；s = width/DW；
      （画布顶部 PAD_T=72px 给饥饿状态的海市蜃楼云朵、底部 60px 给睡眠
       正圆泡泡；paintEvent 统一 translate(0,PAD_T)，角色位置不变）
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

from PySide6.QtCore import (Qt, QTimer, QPointF, QRectF, QElapsedTimer,
                            QPoint, Signal)
from PySide6.QtGui import (QPainter, QColor, QPen, QBrush, QPainterPath,
                           QFont, QPixmap, QIcon, QCursor, QImage,
                           QLinearGradient, QRadialGradient)
from PySide6.QtWidgets import (QApplication, QWidget, QSystemTrayIcon, QMenu,
                               QDialog, QLabel, QPushButton,
                               QVBoxLayout, QHBoxLayout,
                               QMessageBox, QFileDialog)

# P3-13：无状态纯绘制层（眼睛/嘴/海市蜃楼/睡眠泡泡/粒子画法）与
# 共享 clamp/色值搬到了 ejee_paint.py，这里 import 回来保持引用不变
# P3-13 第二刀：绘制层方法 + 绘制共享常量（几何/色板/字体/气泡主题）
# 都在 ejee_paint.py，这里 import 回来保持引用不变
# P3-13 第三刀：UI 层（菜单/对话框/独立特效窗）搬到 ejee_ui.py，
# 番茄钟时长配置随之过去；这里 import 回来保持引用不变
from ejee_ui import (SoftMenu, PomoDialog, BreadCursor, JuiceOverlay,
                     Crumb, _menu_icon, POMO_PRESETS,
                     POMO_MIN_DEF, POMO_MIN_LO, POMO_MIN_HI)

from ejee_paint import (EjeePaintMixin, clamp, EYE_DARK, OMEGA_COL,
                       DW, DH, PAD_T, DH_CHAR,
                       BAND_NEAR, BAND_FAR, RING_STEP, OMEGA_SW,
                       TAIL_RECT, LEAF_GEO,
                       BODY_TOP, CREAM, ACCENT, INK, CLOUD,
                       CONFETTI, HEARTS, STARS, JUICE,
                       FONT_ROUND, FONT_PUNCH,
                       BUBBLE_THEMES, STATE_BUBBLE_THEME)

APP_DIR = os.path.dirname(os.path.abspath(__file__))
if getattr(sys, "frozen", False):
    APP_DIR = os.path.dirname(sys.executable)      # exe 所在目录（可写）
SAVE_PATH = os.path.join(APP_DIR, "ejee_save.json")
PREVIEW_DIR = os.path.join(APP_DIR, "previews")   # --shot 预览图输出目录

# 存档结构版本号：未来字段迁移的锚点（读档时只记录不校验，兼容旧档）
SAVE_SCHEMA = 2

# 模块级「上次读档是否遇到坏档」标记：__init__ 里读完后转存到实例，
# 托盘初始化完成后弹一次气泡提示（避免每次启动都烦人）。
save_corrupted = False


def _to_int(v, dv):
    """存档字段容错读取：类型不对（脏数据/旧档）回落默认值，不炸启动。"""
    try:
        return int(v)
    except (TypeError, ValueError):
        return dv


def _to_float(v, dv):
    try:
        return float(v)
    except (TypeError, ValueError):
        return dv


def load_save():
    """读存档。文件缺失 = 首次启动（静默用默认值）；
    文件存在但解析失败 = 档案损坏：把坏档改名 .bak 留底（旧备份被覆盖），
    回落默认值并置 save_corrupted 标记，托盘起来后提示一次。
    以前这里是 try/except 全吞——坏档会让 fed/pets/first_seen 静默清零。"""
    global save_corrupted
    d = {"schema": SAVE_SCHEMA, "size": 1.0, "last_seen": 0.0,
         "greet_day": "", "fed": 0, "pets": 0, "hunger": 80.0,
         "pomo_min": POMO_MIN_DEF, "first_seen": "", "silent": False,
         "x": None, "y": None}
    try:
        with open(SAVE_PATH, "r", encoding="utf-8") as f:
            d.update(json.load(f))
    except FileNotFoundError:
        pass
    except Exception:
        save_corrupted = True
        try:
            os.replace(SAVE_PATH, SAVE_PATH + ".bak")
        except OSError:
            pass
    return d


def res_path(name):
    """资源定位：PyInstaller onefile 下解包到 sys._MEIPASS（打包时置于根目录）；
    源码运行时优先取脚本同级的 assets/ 子目录，兼容旧的「资源与脚本同级」布局。"""
    base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    p = os.path.join(base, name)
    if os.path.exists(p):
        return p
    alt = os.path.join(base, "assets", name)
    return alt if os.path.exists(alt) else p


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


# ---- 饱食度非线性衰减：100→0 全程 3 小时，数值越低掉得越快 ----
# 速率 r(S) = r0 - c*S（S=100 时 r100，S=0 时 r0=4*r100），
# 由 ∫_0^100 dS/r(S) = HUNGER_FULL_SECONDS 解得 r100 = 100·ln4/(3·T)
HUNGER_FULL_SECONDS = 3 * 3600.0                       # 满 -> 空 的总时长
HUNGER_R100 = 100.0 * math.log(4.0) / (3.0 * HUNGER_FULL_SECONDS)
HUNGER_R0 = 4.0 * HUNGER_R100                          # 空肚时掉得最快
HUNGER_C = (HUNGER_R0 - HUNGER_R100) / 100.0

SIZES = [("小", 0.8), ("中", 1.0), ("大", 1.25), ("特大", 1.5)]
SIZE_MIN, SIZE_MAX = 0.5, 3.0   # Shift+滚轮缩放范围（底图原生 1548px，3x 仍不超采样）
# --shot 预览模式：冻结"跟随鼠标"的视线，让预览图每次渲染完全一致
# （否则光标位置会带动身体摇摆/眼睛方向，改一行代码前后的截图没法比对）
PREVIEW_MODE = False
# 预览模式里每一帧独立的随机种子：让各预览帧的随机流互不干扰
# （粒子位置/大小/颜色互不影响），改某一帧的粒子构成后其余帧逐字节不变。
PREVIEW_SEED_BASE = 900000
# 粒子硬上限：晕车吐泡泡 + 果汁 + 彩纸 + 爱心叠加时防止无界增长，
# 超限丢最旧的（正常玩法远达不到这个量）。
PARTICLE_MAX = 160
# 自适应帧率：有戏看（交互/粒子/气泡/走动/特效/番茄钟）30fps，
# 纯静止呼吸时降到 20fps，减少空转唤醒（呼吸幅度小，20fps 无感）。
TIMER_FAST_MS, TIMER_SLOW_MS = 33, 50
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
class EjeePet(EjeePaintMixin, QWidget):
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
        self._save_corrupted = save_corrupted    # 坏档提示（托盘起来后弹一次）
        self.size = clamp(float(data.get("size", 1.0)), SIZE_MIN, SIZE_MAX)
        self.resize(int(DW * self.size), int(DH * self.size))

        # ---- 记性（昼夜节律/陪伴统计）----
        self._meta = {"last_seen": _to_float(data.get("last_seen"), 0.0),
                      "greet_day": str(data.get("greet_day", "")),
                      "fed": _to_int(data.get("fed"), 0),
                      "pets": _to_int(data.get("pets"), 0),
                      "first_seen": str(data.get("first_seen") or ""),
                      "silent": bool(data.get("silent", False))}
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
        self._pomo_n = 0              # 本次运行完成的番茄钟个数（收尾台词递进）
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
        self._hungry_pending = None   # 饥饿提醒的两段式调度（先张望再开口）

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
        self.hungry_amt = Spring(0.0, 90, 12)  # 饥饿表情显形度 0..1（垂眼+波浪嘴+身体萎软）
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
        self.bubble_badges = None    # 陪伴档案徽章行（_show_stats 设置）
        self._tag_hidden = False     # 气泡压住饱食度牌时置 True（牌淡出让位）
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
        self.bubble_badges = None    # 新台词不带徽章（档案徽章只在档案气泡）
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
        认识多久、喂过几次、摸过几次、现在肚子什么状况。
        文案下方画一排小徽章（天数/喂食/摸头），给长期陪伴一点收集感。"""
        self._touch()                       # 睡着也能被点醒看档案
        days = self._companion_days()
        hug = self._meta.get("hunger", 0.0)
        mood = "有点饿了……" if hug < 30.0 else "肚子饱饱的！"
        txt = ("我已经陪你 %d 天啦～\n喂过我 %d 次，摸了我 %d 次。\n"
               "现在饱食度 %d%%，%s"
               % (days, self._meta.get("fed", 0), self._meta.get("pets", 0),
                  int(round(hug)), mood))
        self._say(txt, 6.0)
        # 徽章行：星星=天数 · 面包=喂食 · 爱心=摸头（绘制见 _draw_stat_badges）
        self.bubble_badges = [
            ("day", self._companion_days()),
            ("feed", _to_int(self._meta.get("fed"), 0)),
            ("pat", _to_int(self._meta.get("pets"), 0))]

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
        tip = self.mapToGlobal(QPoint(int(340 * s), int((300 + PAD_T) * s)))
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
        # ---- 尾巴轻摆素材：notail 底图 + 尾巴子图（Qt 原生加载，不再依赖
        #      PIL，P3-14 瘦身）。语义与原 PIL 版逐点对齐：
        #      clear 矩形 [bx0+10, by0, bx1, by1]（PIL rectangle 端点闭区间）
        #      内 alpha 清零 —— PIL 是 subtract 255 饱和，等价于擦除；
        #      区域外像素不动；尾巴子图 crop((bx0,by0,bx1,by1)) 右/下开区间。
        bx0, by0, bx1, by1 = TAIL_RECT
        body = QImage(res_path("base_body.png")).convertToFormat(
            QImage.Format_RGBA8888)
        notail = body.copy()
        clear_p = QPainter(notail)
        clear_p.setCompositionMode(QPainter.CompositionMode_Clear)
        clear_p.fillRect(bx0 + 10, by0, bx1 - (bx0 + 10) + 1,
                         by1 - by0 + 1, Qt.black)
        clear_p.end()
        self.base_pm = QPixmap.fromImage(notail)
        full = QImage(res_path("base.png")).convertToFormat(
            QImage.Format_RGBA8888)
        self.tail_pm = QPixmap.fromImage(full.copy(bx0, by0,
                                                   bx1 - bx0, by1 - by0))
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
                # 收尾仪式：台词按本次完成的番茄数递进 + 一次明确的跳起
                self._pomo_n += 1
                n = self._pomo_n
                if n <= 1:
                    cheer = "第一颗番茄收成啦！跳一个庆祝～"
                elif n <= 3:
                    cheer = "第 %d 颗番茄收成！去喝口水休息下。" % n
                else:
                    cheer = "连续 %d 颗番茄了，你也太厉害了吧！" % n
                self._celebrate_until = self.t + 2.0
                self._sq.kick(3.2)          # 跳起（比随机庆祝更猛的一下）
                self._say(cheer, 4.0)
                for i in range(18):
                    self.particles.append(Particle(
                        "confetti", self.BCX + random.uniform(-70, 70),
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

        # 待机闲聊：平静时每 4-8 分钟冒一句时段台词（穿透模式不打扰；
        # 番茄钟专注期与静默模式也闭嘴——免打扰）
        if (self.state == "idle" and not self._pass
                and self.phase == "idle"
                and self._pomo_end is None
                and not self._meta.get("silent")
                and self.t >= self._post_lock
                and self.bubble_until < self.t
                and self.t >= self._next_chatter):
            self._next_chatter = self.t + random.uniform(*IDLE_CHATTER_EVERY)
            self._say(self._line(self._bucket()), 3.0)

        # ---- 饱食度：非线性衰减（越低掉得越快，全程 3 小时），饿了提醒 ----
        self._meta["hunger"] = clamp(
            self._hunger_after(self._meta.get("hunger", 80.0), dt), 0.0, 100.0)
        # 饥饿提醒（两段式）：先扭头看一眼别处（复用张望微动作的视线调度），
        # 2.2s 后视线转回你身上再开口——比凭空弹气泡自然；
        # 专注期 / 静默模式下不打扰。
        if (self._meta["hunger"] < 30.0 and self.state == "idle"
                and not self._pass and self.phase == "idle"
                and self._pomo_end is None
                and not self._meta.get("silent")
                and self.bubble_until < self.t
                and self.t >= self._next_hungry):
            self._next_hungry = self.t + random.uniform(240, 420)
            self._look_dir = random.choice((-1.0, 1.0))
            self._look_until = self.t + 2.2
            self._hungry_pending = self.t + 2.2
        if (self._hungry_pending is not None
                and self.t >= self._hungry_pending):
            self._hungry_pending = None
            if (self._meta["hunger"] < 30.0 and self.state == "idle"
                    and self.phase == "idle" and self.bubble_until < self.t):
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
        # 饥饿表情图层：饱食度 <30 渐显（垂眼/虚弱波浪嘴/叶子枯萎）
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
                    # 碎屑从海市蜃楼所在处炸开（气泡画在身体组内、被饿软
                    # 的 sag 压过，位置按渲染结果折算到画布坐标：
                    # 云心 = BCY + (-300 × sag≈0.85) ≈ 63）
                    pt = Particle("bubble", self.BCX + 62
                                  + random.uniform(-20, 20),
                                  63 + random.uniform(-14, 18),
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
        # 番茄钟专注期 / 静默模式同样免打扰；
        # 10% 概率顺带自言自语一句（pet/hungry 池），没人理也鲜活
        if self.state == "idle" and self.phase == "idle" \
                and self.hungry_amt.v < 0.5 \
                and self._pomo_end is None \
                and not self._meta.get("silent") \
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

        # 肚子咕咕叫：每隔几秒一声——不再画黄色同心圆波（用户要求），
        # 只让肚皮轻轻抽一下（_sq 轻踢），读作“咕咕”的轻微颤动
        if (self.hungry_amt.v > 0.3 and self.state == "idle"
                and self.phase == "idle" and not self._pass):
            self._fx_timer2 -= dt
            if self._fx_timer2 <= 0:
                self._fx_timer2 = random.uniform(2.7, 3.7)
                self._sq.kick(0.6)      # 轻微肚皮抖动（峰值约 4%），表示咕咕叫

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
        # 硬上限：晕车吐泡泡 + 果汁 + 彩纸 + 爱心全叠在一起也不会无界增长，
        # 超限从头部丢最旧的（append 顺序即出生顺序）
        if len(self.particles) > PARTICLE_MAX:
            del self.particles[:len(self.particles) - PARTICLE_MAX]
        if self.floats:
            self.floats = [f for f in self.floats if self.t - f[3] < 1.2]
        # 自适应帧率：有戏看保持 30fps，纯静止呼吸降到 20fps（省空转唤醒）。
        # 预览/仿真不走 QTimer（scaffold 里 timer=None），跳过。
        if self.timer is not None:
            busy = bool(self.particles or self.floats or self.bubble_text
                        or self.bubble_badges
                        or self._glide or self._wander or self._flee
                        or self._dragging or self._bread is not None
                        or self._fantasy is not None or self._zooming
                        or self.state != "idle" or self.phase != "idle"
                        or self._pomo_end is not None
                        or self.t < self.mischief_until
                        or self.t < self._dizzy_until
                        or self.t < self._nod_until
                        or self.t < self._shy_until)
            want = TIMER_FAST_MS if busy else TIMER_SLOW_MS
            if self.timer.interval() != want:
                self.timer.setInterval(want)
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
        p.translate(0.0, PAD_T)   # 整体下移：给头顶的海市蜃楼云朵腾出舞台
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

    def _mouth_open(self):
        """happy 状态下的嘴开合：0=闭，1=全开（张嘴→吞入→闭嘴）。"""
        if self.state != "happy":
            return 0.0
        if self.phase == "bread":
            k = clamp((self.t - self.phase_t0) / 0.55, 0, 1)
            return math.sin(math.pi * min(1.0, k * 1.25))
        return 0.0

    # ---------- 特效绘制 ----------
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
                      int(self.pos().y() + (self.mouth_center[1] + PAD_T) * s))

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
                               clamp((gpos.y() - self.y()) / s - PAD_T,
                                     -30.0, DH + 30.0))
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
        不该把它算进"可见高度"，否则宠物会被顶起来悬空。顶部那块
        (PAD_T) 不用减——角色本来就在 PAD_T 下面，可见高度从窗口顶算起。"""
        return int(round((DH - PAD_T - DH_CHAR) * self.size))

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
                             (gp.y() - self.y()) / s_old - PAD_T, gp)

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

    # ---- 静默模式 / 陪伴档案的导出导入与重置（托盘菜单入口）----
    def _toggle_silent(self, on):
        """静默模式：不冒自发气泡（闲聊/饥饿提醒/微表情自言自语），
        用户主动互动的回应与番茄钟到点提醒不受影响。偏好随存档记。"""
        self._meta["silent"] = bool(on)
        self._save()
        if self._meta["silent"]:
            self._say("好～静默模式，我安静陪着你不说话。", 2.6)
        else:
            self._say("叽！静默模式关掉啦。", 2.2)
        # 同步托盘菜单开关（与 _toggle_pass 同一套对齐方式）
        if getattr(self, "tray_act_silent", None) is not None:
            self.tray_act_silent.setProperty("_switchOn", self._meta["silent"])
            if getattr(self, "_tray_menu", None) is not None:
                self._tray_menu.update()

    def _export_stats(self):
        """导出陪伴档案：把 meta（喂食/摸头/相识日/饱食度等）写成 JSON。"""
        path, _ = QFileDialog.getSaveFileName(
            self, "导出陪伴档案",
            os.path.join(os.path.expanduser("~"), "ejee_陪伴档案.json"),
            "JSON (*.json)")
        if not path:
            return
        d = {"schema": SAVE_SCHEMA}
        d.update(self._meta)
        d["exported"] = time.strftime("%Y-%m-%d %H:%M")
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(d, f, ensure_ascii=False, indent=1)
        except OSError:
            self._say("呜……档案没能写出去。", 2.6)
            return
        self._say("档案打包好啦，记得收好哦。", 2.8)

    def _import_stats(self):
        """导入陪伴档案：只认陪伴数据（喂食/摸头/相识日/饱食度/番茄钟时长），
        窗口位置与大小不跟档案走。字段逐个容错，坏档不炸。"""
        path, _ = QFileDialog.getOpenFileName(self, "导入陪伴档案", "",
                                              "JSON (*.json)")
        if not path:
            return
        try:
            with open(path, "r", encoding="utf-8") as f:
                d = json.load(f)
            if not isinstance(d, dict):
                raise ValueError("not a dict")
        except Exception:
            self._say("这个文件读不出来……是档案吗？", 2.6)
            return
        self._meta["fed"] = _to_int(d.get("fed"), self._meta.get("fed", 0))
        self._meta["pets"] = _to_int(d.get("pets"), self._meta.get("pets", 0))
        self._meta["hunger"] = clamp(
            _to_float(d.get("hunger"), 80.0), 0.0, 100.0)
        fs = str(d.get("first_seen") or "")
        if fs:
            self._meta["first_seen"] = fs
        pm = _to_int(d.get("pomo_min"), self._meta.get("pomo_min",
                                                       POMO_MIN_DEF))
        self._meta["pomo_min"] = clamp(pm, POMO_MIN_LO, POMO_MIN_HI)
        self._save()
        self._say("欢迎回来，这些日子我都记起来啦！", 3.2)

    def _reset_companion(self):
        """重置陪伴数据（带确认）：清空喂食/摸头/相识日，饱食度回满；
        窗口位置与大小保留。以前用户只能手删存档文件。"""
        ret = QMessageBox.question(
            self, "重置陪伴数据",
            "要清空喂食、摸头和相识日这些陪伴记录吗？\n"
            "（窗口位置与大小会保留，操作不可撤销）",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if ret != QMessageBox.Yes:
            return
        self._meta["fed"] = 0
        self._meta["pets"] = 0
        self._meta["hunger"] = 80.0
        self._meta["first_seen"] = time.strftime("%Y-%m-%d")
        self._meta["greet_day"] = ""
        self._save()
        self._say("记忆清空啦……我们、重新认识一下吧？", 3.6)

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
        act_silent = menu.addAction(_menu_icon("mute"), "静默模式")
        act_silent.setProperty("_switch", True)
        act_silent.setProperty("_switchOn", bool(self._meta.get("silent")))
        act_silent.triggered.connect(
            lambda checked=False: self._toggle_silent(
                not self._meta.get("silent")))
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
        act_silent = menu.addAction(_menu_icon("mute"), "静默模式")
        act_silent.setProperty("_switch", True)
        act_silent.setProperty("_switchOn", bool(self._meta.get("silent")))
        act_silent.triggered.connect(
            lambda checked=False: self._toggle_silent(
                not self._meta.get("silent")))
        self.tray_act_silent = act_silent   # _toggle_silent 里同步开关状态
        self._tray_menu = menu
        menu.addAction(_menu_icon("eye"), "显示 / 隐藏").triggered.connect(
            self._toggle_visible)
        act_reset = menu.addAction(_menu_icon("reset"), "重置大小 1.0x")
        act_reset.triggered.connect(lambda checked=False: self.set_size(1.0))
        menu.addSeparator()
        menu.addAction(_menu_icon("star"), "导出陪伴档案…").triggered.connect(
            self._export_stats)
        menu.addAction(_menu_icon("bread"), "导入陪伴档案…").triggered.connect(
            self._import_stats)
        menu.addAction(_menu_icon("reset"), "重置陪伴数据…").triggered.connect(
            self._reset_companion)
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
            if getattr(self, "tray_act_silent", None) is not None:
                self.tray_act_silent.setProperty(
                    "_switchOn", bool(self._meta.get("silent")))
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
        # 启动时发现坏档（load_save 已把坏档备份成 .bak）：提示一次
        if getattr(self, "_save_corrupted", False):
            self.tray.showMessage(
                "EJEE 存档已损坏",
                "坏档已备份为 ejee_save.json.bak，陪伴数据已重置。",
                QSystemTrayIcon.Warning, 6000)


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
    # 高分屏：缩放策略显式声明为 PassThrough（Qt6 默认值，写明防候选默认变
    # 化）——125%/150% 系统缩放下不把窗口圆整到整数倍，桌宠边缘不发虚。
    # 注意：预览基线仍必须在 DPR=1 环境生成（tools/check_preview.py 有硬断言）。
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
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
        random.seed(PREVIEW_SEED_BASE + 1)          # 后续帧各自独立随机流
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
        random.seed(PREVIEW_SEED_BASE + 2)
        snap("angry")
        pet.t = 2.6
        pet._last_t = 2.6
        pet._say("呜！尾巴不可以抓！", 3.0, "burst")
        pet.t = 2.95
        pet._last_t = 2.95
        pet.grab().save(os.path.join(PREVIEW_DIR, "preview_angry.png"))
        random.seed(PREVIEW_SEED_BASE + 3)
        snap("surprised")
        pet.t = 4.0
        pet._last_t = 4.0
        pet.grab().save(os.path.join(PREVIEW_DIR, "preview_surprised.png"))
        random.seed(PREVIEW_SEED_BASE + 4)
        snap("sleep")
        pet.t = 7.0
        pet._last_t = 7.0
        pet.particles.append(Particle("zzz", pet.BCX + 40,
                                      pet.head_top + 2, pet.t - 1.2))
        pet.particles.append(Particle("zzz", pet.BCX + 50,
                                      pet.head_top - 8, pet.t - 2.4))
        pet.grab().save(os.path.join(PREVIEW_DIR, "preview_sleep.png"))
        random.seed(PREVIEW_SEED_BASE + 5)
        snap("idle")
        pet.particles.clear()
        pet.t = 8.6
        pet._last_t = 8.6
        pet._say("咕噜咕噜～最喜欢被你摸头了！再用橘子尾巴给你比个心哦～", 3.0)
        pet.t = 8.95          # 气泡入场动画完成后截（age=0.35s，全显）
        pet.grab().save(os.path.join(PREVIEW_DIR, "preview_bubble.png"))
        random.seed(PREVIEW_SEED_BASE + 6)
        snap("idle")
        pet._meta["hunger"] = 12.0
        pet.hungry_amt.snap(1.0)
        pet.particles.clear()
        pet.t = 10.6
        pet._last_t = 10.6
        pet._fantasy = {"t0": pet.t - 0.9}    # 幻想气泡（展示期，放大版海市蜃楼）
        pet.grab().save(os.path.join(PREVIEW_DIR, "preview_hungry.png"))
        random.seed(PREVIEW_SEED_BASE + 7)
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
        random.seed(PREVIEW_SEED_BASE + 8)
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
        random.seed(PREVIEW_SEED_BASE + 9)
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
        random.seed(PREVIEW_SEED_BASE + 10)
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
        random.seed(PREVIEW_SEED_BASE + 11)
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
        random.seed(PREVIEW_SEED_BASE + 12)
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
