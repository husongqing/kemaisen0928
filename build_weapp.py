#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""构建科迈森在线培训学习平台 · 微信小程序交互原型 (weapp.html)
品牌规范：A 科技青环方案（#0A2540 + #00C9FF→#0066FF + #0098E8）
参考需求文档：科迈森在线培训学习平台 方案梳理 0928.docx
"""
import base64, os, io

ROOT = os.path.dirname(os.path.abspath(__file__))
BRAND = os.path.join(ROOT, '..', 'brand')
ASSETS = os.path.join(ROOT, 'assets')

def svg_uri(name):
    with open(os.path.join(BRAND, name), 'rb') as f:
        return 'data:image/svg+xml;base64,' + base64.b64encode(f.read()).decode()

LOGO_H   = svg_uri('logo-a-horizontal.svg')          # 白底深字（导航栏/页脚）
LOGO_REV = svg_uri('logo-a-horizontal-reverse.svg')  # 深底反白（个人中心头部）
LOGO_ICON = svg_uri('logo-icon-tile.svg')            # 渐变底反白图标

# ===== 真实封面图（来源：sudh.net 内容接口，已下载压缩到 assets/）=====
from PIL import Image
_jpg_cache = {}
def jpg_uri(name, w=700, q=76):
    """把 assets/<name> 压成 base64 data URI（宽度<=w），结果做缓存"""
    key = (name, w, q)
    if key in _jpg_cache:
        return _jpg_cache[key]
    im = Image.open(os.path.join(ASSETS, name)).convert('RGBA')
    bg = Image.new('RGB', im.size, (255, 255, 255))
    bg.paste(im, mask=im.split()[-1])
    im = bg
    if im.width > w:
        im = im.resize((w, round(im.height * w / im.width)), Image.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, 'JPEG', quality=q, optimize=True, progressive=True)
    uri = 'data:image/jpeg;base64,' + base64.b64encode(buf.getvalue()).decode()
    _jpg_cache[key] = uri
    return uri

COURSE_IMGS = [f'course-{i}.jpg' for i in range(1, 7)]   # 真实课程/术式封面
ACT_IMGS    = [f'act-{i}.jpg'    for i in range(1, 7)]   # 真实培训活动海报
NEWS_ALL    = [f'news-{i}.jpg'   for i in range(1, 7)]   # 真实资讯封面
# 资讯按栏目分配，配图更贴切：
#   学术资讯 = 学术大会/共识幻灯；器械知识 = 术式与器械；平台介绍 = 学术活动现场
NEWS_IMGS = {
    '学术资讯': ['news-1.jpg', 'news-4.jpg'],
    '器械知识': ['news-2.jpg', 'news-5.jpg'],
    '平台介绍': ['news-3.jpg'],
}

def img_cls(fname):
    """图片文件名 -> CSS 类名，例如 course-1.jpg -> im-course-1"""
    return 'im-' + os.path.splitext(fname)[0]

def _hash(key):
    return sum((i + 1) * ord(c) for i, c in enumerate(str(key)))

def _mix(key):
    """更强的散列，保证同一栏目内的多条内容能轮换到不同配图"""
    s = str(key)
    return _hash(s) + 7 * len(s) + ord(s[0])

def pick_img(lst, key):
    """按标题稳定地分配一张图（同一标题永远得到同一张）"""
    return lst[_hash(key) % len(lst)]

def pick_news_img(cat, key):
    """资讯封面按栏目取图，同一标题永远得到同一张"""
    lst = NEWS_IMGS.get(cat) or NEWS_ALL
    return lst[_mix(key) % len(lst)]

# 把真实图各生成一次 CSS 类（避免每张卡片重复内联 base64 导致文件膨胀）
# 用 !important 确保覆盖 .li .thumb / .poster / .article .img 等基类里的渐变占位 background
IMG_CSS = '\n'.join(
    f'.{img_cls(n)}{{background-image:url({jpg_uri(n)})!important}}'
    for n in COURSE_IMGS + ACT_IMGS + NEWS_ALL
)

CSS = r"""
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
:root{
  --navy:#061B3A; --navy2:#0A2540; --navy3:#143560;
  --cyan:#00C9FF; --cyan2:#0098E8; --cyanD:#0066FF;
  --t1:#0A2540; --t2:#4A5878; --t3:#8A96B0;
  --line:#E6EBF2; --line2:#EEF2F8; --bg:#F4F7FB; --w:#fff;
  --ok:#0EBD8E; --warn:#FFB547; --bad:#FF5A65;
  --gradTech:linear-gradient(135deg,#00C9FF 0%,#0066FF 100%);
  --gradMain:linear-gradient(135deg,#061B3A 0%,#0A2540 40%,#0066FF 100%);
  --sh:0 2px 10px rgba(10,37,64,.07); --sh2:0 8px 28px rgba(10,37,64,.12);
}
html{-webkit-font-smoothing:antialiased}
body{font-family:-apple-system,BlinkMacSystemFont,"PingFang SC","Helvetica Neue","Microsoft YaHei",sans-serif;
  font-size:14px;line-height:1.6;color:var(--t1);background:#cdd6e3;overflow-x:hidden;
  display:flex;flex-wrap:wrap;gap:34px;justify-content:center;padding:40px 24px;align-items:flex-start}
.stage{display:flex;flex-direction:column;align-items:center;gap:14px}
.stage .cap{font-size:13px;color:#5a6478;font-weight:600}
.stage .cap span{display:block;color:#8a96b0;font-weight:400;font-size:11px;margin-top:2px}

/* ===== 手机外框（微信小程序外观） ===== */
.phone{width:390px;height:844px;background:#000;border-radius:46px;padding:11px;position:relative;
  box-shadow:0 30px 70px rgba(10,37,64,.30),0 0 0 2px #1c2336;flex-shrink:0;overflow:hidden}
/* 注意：不要用 clip-path —— 它会让子层按绘制顺序拍平，z-index 失效（导致错误的页面盖在最上层）。
   离屏页面改用 visibility 隐藏，圆角由 .screen 的 overflow:hidden 负责 */
.phone .screen{position:absolute;inset:11px;border-radius:36px;overflow:hidden;background:var(--bg)}
.island{position:absolute;top:0;left:50%;transform:translateX(-50%);width:122px;height:34px;
  background:#000;border-radius:0 0 18px 18px;z-index:60}

/* ===== 系统状态栏 + 微信胶囊 ===== */
.sysbar{position:absolute;top:0;left:0;right:0;height:50px;z-index:55;display:flex;align-items:center;
  justify-content:space-between;padding:14px 26px 0;font-size:14px;font-weight:600;color:#0A2540;pointer-events:none}
.sysbar.dark{color:#fff}
.sysbar .sig{display:flex;align-items:center;gap:5px}
.sysbar .sig .bars{display:flex;gap:2px;align-items:flex-end;height:11px}
.sysbar .sig .bars i{width:3px;background:currentColor;border-radius:1px}
.sysbar .sig .bars i:nth-child(1){height:4px}.sysbar .sig .bars i:nth-child(2){height:6px}
.sysbar .sig .bars i:nth-child(3){height:8px}.sysbar .sig .bars i:nth-child(4){height:11px}
.sysbar .bat{width:24px;height:12px;border:1.5px solid currentColor;border-radius:3px;position:relative;padding:1.5px}
.sysbar .bat::after{content:'';position:absolute;right:-3px;top:3px;width:2px;height:4px;border-radius:0 1px 1px 0;background:currentColor}
.sysbar .bat i{display:block;height:100%;width:72%;background:currentColor;border-radius:1px}
/* 微信胶囊 */
.capsule{position:absolute;top:11px;right:22px;z-index:58;width:88px;height:31px;background:rgba(245,247,250,.82);
  border:1px solid rgba(10,37,64,.10);border-radius:16px;display:flex;align-items:center;justify-content:center;gap:14px;
  backdrop-filter:blur(6px)}
.capsule.dark{background:rgba(255,255,255,.18);border-color:rgba(255,255,255,.25)}
.capsule .dot{width:9px;height:9px;border-radius:50%;border:1.6px solid currentColor;color:#0A2540;position:relative}
.capsule.dark .dot{color:#fff}
.capsule .dot::after{content:'';position:absolute;inset:1.8px;border-radius:50%;background:currentColor}
.capsule .omit{display:flex;flex-direction:column;gap:3px}
.capsule .omit i{width:15px;height:2px;border-radius:1px;background:#0A2540;display:block}
.capsule.dark .omit i{background:#fff}

/* ===== 页面 =====
   状态机（三者互斥，避免层级打架）：
     .page.tab     —— 标记：这是一个 Tab 页，默认就位于屏幕内（不参与 push 位移）
     .page.under   —— 被 push 页压住的底层页（左移退后，始终低于顶层）
     .page.tab.cur —— 当前激活的 Tab 页（无 push 页时即为顶层）
     .page.show    —— 顶层页（push 进来的页 / 切 Tab 时的目标页）
   注意：.page.show 必须排在 .page.tab 之后，且 .under 的层级永远低于 .show */
.page{position:absolute;inset:0;background:var(--bg);display:flex;flex-direction:column;overflow:hidden;
  transform:translateX(100%);transition:transform .32s cubic-bezier(.4,.0,.2,1);
  z-index:5;visibility:hidden;pointer-events:none}
.page.tab{transform:none}
.page.under{transform:translateX(-22%);z-index:10;visibility:visible}
.page.show{transform:translateX(0);z-index:20;visibility:visible;pointer-events:auto}
.page.tab.cur{transform:none;z-index:15;visibility:visible;pointer-events:auto}
.body{flex:1;overflow-y:auto;-webkit-overflow-scrolling:touch;padding-bottom:8px}

/* 状态栏占位：电脑端（显示外壳）页面内容下移 50px，避免与系统状态栏重叠 */
.page{padding-top:50px}
.page#pg_splash,.page#pg_profile{padding-top:0}

/* 响应式：电脑端显示手机外壳；窄屏（手机）隐藏外壳，页面铺满全屏 */
@media (max-width:480px){
  html,body{height:100%}
  body{padding:0;display:block;overflow-x:hidden}
  .stage{display:block}
  .stage .cap{display:none}
  .phone{position:fixed;inset:0;border-radius:0;padding:0;box-shadow:none;background:transparent;flex-shrink:0}
  .phone .screen{position:absolute;inset:0;border-radius:0;background:var(--bg)}
  .island,.sysbar,.capsule{display:none}
  .page{padding-top:env(safe-area-inset-top,0px)}
  .page#pg_splash,.page#pg_profile{padding-top:env(safe-area-inset-top,0px)}
}

/* ===== 微信导航栏 ===== */
.navbar{height:44px;flex-shrink:0;display:flex;align-items:center;padding:0 12px;background:#fff;
  border-bottom:1px solid var(--line);position:relative;z-index:30}
.navbar.dark{background:var(--gradMain);border-bottom:none;color:#fff}
.navbar .back{width:30px;height:30px;display:flex;align-items:center;justify-content:center;margin-left:-6px;color:#0A2540}
.navbar.dark .back{color:#fff}
.navbar .tt{position:absolute;left:0;right:0;text-align:center;font-size:16px;font-weight:600;pointer-events:none}
.navbar .act{margin-left:auto;font-size:13px;color:var(--cyan2);font-weight:500;display:flex;align-items:center;gap:4px}
.navbar .more{width:30px;height:30px;margin-left:auto;display:flex;align-items:center;justify-content:center;color:#0A2540}
.navbar.dark .more{color:#fff}

/* ===== 底部 TabBar ===== */
.tabbar{height:58px;flex-shrink:0;background:#fff;border-top:1px solid var(--line);display:flex;z-index:30}
.tabbar .tb{flex:1;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:3px;
  font-size:10px;color:#9aa4ba;position:relative}
.tabbar .tb.on{color:var(--cyanD);font-weight:600}
.tabbar .tb svg{width:23px;height:23px}
.tabbar .tb .dot{position:absolute;top:8px;right:50%;margin-right:-18px;width:7px;height:7px;background:var(--bad);
  border-radius:50%;border:1.5px solid #fff}

/* ===== 通用组件 ===== */
.btn{height:46px;border:none;border-radius:24px;background:var(--gradTech);color:#fff;font-size:15px;
  font-weight:600;display:flex;align-items:center;justify-content:center;box-shadow:0 8px 20px rgba(0,102,255,.26);
  letter-spacing:.5px;cursor:pointer}
.btn:active{transform:scale(.98)}
.btn.ghost{background:#fff;color:var(--cyanD);border:1.5px solid rgba(0,102,255,.35);box-shadow:none}
.btn.disabled{background:#CBD5E4;box-shadow:none;color:#fff;cursor:not-allowed}
.btn.sm{height:32px;border-radius:16px;font-size:12.5px;padding:0 16px;display:inline-flex;width:auto}
.field{background:#fff;border-radius:14px;padding:4px 16px;margin:0 16px}
.field .row{display:flex;align-items:center;min-height:52px;border-bottom:1px solid var(--line2);position:relative}
.field .row:last-child{border-bottom:none}
.field .row label{width:84px;font-size:14px;color:var(--t2);flex-shrink:0}
.field .row input,.field .row textarea{border:none;outline:none;flex:1;font-size:14.5px;color:var(--t1);
  background:transparent;padding:6px 0;font-family:inherit;resize:none}
.field .row input::placeholder{color:#b6bfd0}
.field .row .arrow{color:#c2cad9;margin-left:6px}
.field .row .getcode{color:var(--cyanD);font-size:13px;font-weight:600;white-space:nowrap;background:none;border:none}
.field .row .getcode:disabled{color:#b6bfd0}
.chk{display:flex;align-items:center;gap:8px;margin:14px 16px;font-size:12.5px;color:var(--t3)}
.chk svg{width:18px;height:18px;flex-shrink:0}
.chk a{color:var(--cyan2)}

.badge{display:inline-flex;align-items:center;height:20px;padding:0 9px;border-radius:10px;font-size:11px;font-weight:600}
.b-live{background:var(--gradTech);color:#fff;box-shadow:0 3px 10px rgba(0,102,255,.3)}
.b-hot{background:rgba(255,90,101,.12);color:var(--bad)}
.b-cyan{background:rgba(0,152,232,.12);color:var(--cyan2)}
.b-navy{background:rgba(10,37,64,.08);color:var(--navy2)}
.b-ok{background:rgba(14,189,142,.12);color:var(--ok)}
.b-warn{background:rgba(255,181,71,.15);color:#E0962A}
.b-gray{background:var(--line2);color:var(--t3)}

.sec-h{display:flex;align-items:center;margin:18px 16px 10px}
.sec-h .t{font-size:16px;font-weight:700;color:var(--t1)}
.sec-h .t::before{content:'';display:inline-block;width:4px;height:15px;background:var(--gradTech);
  border-radius:2px;margin-right:8px;vertical-align:-2px}
.sec-h .more{margin-left:auto;font-size:12.5px;color:var(--t3);display:flex;align-items:center;gap:2px}

/* 卡片 */
.card{background:#fff;border-radius:16px;box-shadow:var(--sh);overflow:hidden}
.cv{position:relative;height:160px;background:var(--gradMain);overflow:hidden;display:flex;align-items:center;justify-content:center}
.cv::after{content:'';position:absolute;right:-30px;top:-30px;width:140px;height:140px;
  background:radial-gradient(circle,rgba(0,201,255,.45),transparent 70%);filter:blur(8px)}
.cv .play{width:52px;height:52px;border-radius:50%;background:rgba(255,255,255,.92);display:flex;align-items:center;justify-content:center;box-shadow:0 6px 18px rgba(0,0,0,.2);z-index:1}
.cv .play svg{width:22px;height:22px;color:var(--cyanD);margin-left:3px}
.cv .tag{position:absolute;left:10px;top:10px;z-index:2}
.cv .tag2{position:absolute;right:10px;top:10px;z-index:2}
.cv .src{position:absolute;left:10px;bottom:10px;z-index:2;color:#fff;font-size:11px;opacity:.85;display:flex;align-items:center;gap:4px}

/* 课程/活动/资讯列表项 */
.li{background:#fff;border-radius:14px;box-shadow:var(--sh);display:flex;gap:12px;padding:12px;margin:0 16px 12px}
.li .thumb{width:104px;height:74px;border-radius:11px;background:var(--gradMain);flex-shrink:0;position:relative;overflow:hidden;display:flex;align-items:center;justify-content:center}
.li .thumb::after{content:'';position:absolute;right:-14px;top:-14px;width:60px;height:60px;background:radial-gradient(circle,rgba(0,201,255,.4),transparent 70%);filter:blur(5px)}
.li .thumb .pi{width:26px;height:26px;color:rgba(255,255,255,.9);z-index:1}
.li .ct{flex:1;min-width:0;display:flex;flex-direction:column}
.li .ct .ti{font-size:14px;font-weight:600;color:var(--t1);line-height:1.35;overflow:hidden;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical}
.li .ct .me{font-size:11.5px;color:var(--t3);margin-top:3px;display:flex;align-items:center;gap:5px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.li .ct .bo{margin-top:auto;display:flex;align-items:center;gap:7px}
.li .ct .bo .pr{font-size:11px;color:var(--t3);display:flex;align-items:center;gap:3px}

/* ===== 真实封面图 ===== */
.li .thumb.cover{background-size:cover;background-position:center}
.li .thumb.cover::after{display:none}
.li .thumb.cover .pi{position:relative;z-index:1;width:30px;height:30px;border-radius:50%;
  background:rgba(10,37,64,.42);display:flex;align-items:center;justify-content:center;backdrop-filter:blur(2px)}
.li .thumb.cover .pi svg{width:13px;height:13px;color:#fff;margin-left:2px}
.cv.cover{background-size:cover;background-position:center}
.cv.cover::before{content:'';position:absolute;inset:0;z-index:1;
  background:linear-gradient(180deg,rgba(6,27,58,.05) 30%,rgba(6,27,58,.68) 100%)}
.cv.cover::after{display:none}
.cv.cover .play{z-index:2}
.banner.cover{background-size:cover;background-position:center}
.banner.cover::before{content:'';position:absolute;inset:0;z-index:0;
  background:linear-gradient(100deg,rgba(6,27,58,.96) 0%,rgba(6,45,105,.88) 58%,rgba(0,102,255,.74) 100%)}
.banner.cover::after{display:none}
.banner.cover>*{position:relative;z-index:1}
.player-area .poster.cover{background-size:cover;background-position:center}

/* 分类 Tab */
.tabs{display:flex;gap:6px;padding:10px 16px;overflow-x:auto;background:#fff;border-bottom:1px solid var(--line);scrollbar-width:none}
.tabs::-webkit-scrollbar{display:none}
.tabs .t{flex-shrink:0;height:32px;padding:0 15px;border-radius:16px;background:var(--line2);color:var(--t2);
  font-size:13px;display:flex;align-items:center;white-space:nowrap;font-weight:500}
.tabs .t.on{background:var(--gradTech);color:#fff;font-weight:600;box-shadow:0 4px 12px rgba(0,102,255,.22)}

/* 搜索框 */
.search{margin:12px 16px;height:38px;border-radius:19px;background:#fff;display:flex;align-items:center;
  padding:0 14px;color:var(--t3);font-size:13px;gap:7px;box-shadow:var(--sh)}

/* 功能入口 */
.entries{display:grid;grid-template-columns:repeat(4,1fr);gap:6px;margin:12px 16px}
.entries .e{background:#fff;border-radius:14px;padding:14px 4px;display:flex;flex-direction:column;align-items:center;gap:8px;
  box-shadow:var(--sh)}
.entries .e .ic{width:42px;height:42px;border-radius:13px;background:var(--gradMain);display:flex;align-items:center;justify-content:center;color:#fff}
.entries .e .ic svg{width:22px;height:22px}
.entries .e .lb{font-size:12px;color:var(--t1);font-weight:500}
.entries .e .sg{font-size:10px;color:var(--t3)}

/* Banner */
.banner{margin:12px 16px;height:140px;border-radius:16px;background:var(--gradMain);position:relative;overflow:hidden;padding:18px}
.banner::after{content:'';position:absolute;right:-26px;top:-26px;width:150px;height:150px;
  background:radial-gradient(circle,rgba(0,201,255,.5),transparent 70%);filter:blur(10px)}
.banner .t{color:#fff;font-size:18px;font-weight:700;position:relative}
.banner .d{color:rgba(255,255,255,.7);font-size:12px;margin-top:6px;position:relative;max-width:220px}
.banner .b{position:relative;margin-top:14px;display:inline-flex;height:30px;padding:0 16px;border-radius:15px;
  background:rgba(255,255,255,.95);color:var(--navy2);font-size:12.5px;font-weight:600;align-items:center}

/* 直播入口卡 */
.live{margin:12px 16px;border-radius:16px;overflow:hidden;position:relative;background:#0A2540;box-shadow:var(--sh2)}
.live.idle{background:#fff;border:1px solid var(--line)}
.live .hd{display:flex;align-items:center;gap:10px;padding:12px 14px;position:relative;z-index:1}
.live .hd .liveicon{width:46px;height:46px;border-radius:13px;background:var(--gradTech);display:flex;align-items:center;justify-content:center;color:#fff;flex-shrink:0}
.live .hd .liveicon svg{width:24px;height:24px}
.live .hd .nm{color:#fff;font-size:14.5px;font-weight:600;flex:1}
.live.idle .hd .nm{color:var(--t1)}
.live .hd .st{font-size:11px;color:#7FE4FF;font-weight:600;display:flex;align-items:center;gap:5px}
.live.idle .hd .st{color:var(--t3)}
.live .pulse{width:8px;height:8px;border-radius:50%;background:#7FE4FF;box-shadow:0 0 0 0 rgba(127,228,255,.7);animation:pulse 1.6s infinite}
@keyframes pulse{0%{box-shadow:0 0 0 0 rgba(127,228,255,.6)}70%{box-shadow:0 0 0 9px rgba(127,228,255,0)}100%{box-shadow:0 0 0 0 rgba(127,228,255,0)}}
.live .vd{position:relative;z-index:1;padding:0 14px 14px}
.live .vd .ti{color:rgba(255,255,255,.92);font-size:13px;font-weight:600}
.live.idle .vd .ti{color:var(--t1)}
.live .vd .su{color:rgba(255,255,255,.55);font-size:11.5px;margin-top:3px}
.live.idle .vd .su{color:var(--t3)}
.live .go{position:absolute;right:14px;bottom:14px;z-index:1;font-size:12px;color:#0A2540;background:var(--gradTech);
  color:#fff;padding:6px 13px;border-radius:14px;font-weight:600}
.live::after{content:'';position:absolute;left:-40px;bottom:-50px;width:200px;height:200px;
  background:radial-gradient(circle,rgba(0,201,255,.3),transparent 70%);filter:blur(4px)}

/* 列表菜单（个人中心） */
.menu{margin:12px 16px;background:#fff;border-radius:14px;box-shadow:var(--sh);overflow:hidden}
.menu .m{display:flex;align-items:center;gap:12px;padding:14px 14px;border-bottom:1px solid var(--line2);position:relative}
.menu .m:last-child{border-bottom:none}
.menu .m .ic{width:34px;height:34px;border-radius:10px;background:rgba(0,152,232,.1);display:flex;align-items:center;justify-content:center;color:var(--cyan2);flex-shrink:0}
.menu .m .ic svg{width:18px;height:18px}
.menu .m .lb{font-size:14px;color:var(--t1);font-weight:500}
.menu .m .rg{margin-left:auto;display:flex;align-items:center;gap:8px;color:var(--t3);font-size:13px}
.menu .m .rg svg{width:15px;height:15px;color:#c2cad9}
.menu .m .badge2{background:var(--bad);color:#fff;font-size:11px;font-weight:600;min-width:18px;height:18px;border-radius:9px;
  display:flex;align-items:center;justify-content:center;padding:0 5px}

/* 空状态 */
.empty{text-align:center;padding:60px 20px;color:var(--t3)}
.empty .ic{width:64px;height:64px;border-radius:20px;background:var(--line2);display:flex;align-items:center;justify-content:center;margin:0 auto 14px;color:#b6bfd0}
.empty .ic svg{width:30px;height:30px}
.empty .t{font-size:14px;color:var(--t2);font-weight:500}
.empty .d{font-size:12px;margin-top:5px}

/* ===== 弹窗 / Toast ===== */
.mask{position:absolute;inset:0;background:rgba(10,37,64,.5);z-index:90;display:none;align-items:center;justify-content:center;opacity:0;transition:opacity .25s}
.mask.show{display:flex;opacity:1}
.pop{width:300px;background:#fff;border-radius:20px;padding:26px 22px;text-align:center;transform:scale(.8);transition:transform .3s cubic-bezier(.2,1.2,.4,1)}
.mask.show .pop{transform:scale(1)}
.pop .pic{width:62px;height:62px;border-radius:50%;background:var(--gradTech);margin:0 auto 14px;display:flex;align-items:center;justify-content:center;color:#fff;box-shadow:0 8px 22px rgba(0,102,255,.3)}
.pop .pic svg{width:32px;height:32px}
.pop .pt{font-size:17px;font-weight:700}
.pop .pd{font-size:13px;color:var(--t2);margin-top:8px;line-height:1.6}
.pop .pbtn{margin-top:20px}
.toast{position:absolute;left:50%;top:46%;transform:translate(-50%,-50%) scale(.9);background:rgba(10,37,64,.92);
  color:#fff;font-size:13.5px;padding:11px 20px;border-radius:12px;z-index:95;opacity:0;transition:.22s;pointer-events:none;max-width:80%;text-align:center}
.toast.show{opacity:1;transform:translate(-50%,-50%) scale(1)}

/* 启动页 */
.pg_splash{background:var(--gradMain);align-items:center;justify-content:center}
.pg_splash .glow{position:absolute;top:14%;left:50%;transform:translateX(-50%);width:220px;height:220px;
  background:radial-gradient(circle,rgba(0,201,255,.4),transparent 70%);filter:blur(30px)}
.pg_splash .tile{width:96px;height:96px;border-radius:24px;box-shadow:0 16px 44px rgba(0,201,255,.45)}
.pg_splash .nm{color:#fff;font-size:24px;font-weight:700;letter-spacing:4px;margin-top:18px}
.pg_splash .su{color:rgba(255,255,255,.55);font-size:10px;letter-spacing:3px;margin-top:6px}
.pg_splash .bar{width:180px;height:4px;border-radius:2px;background:rgba(255,255,255,.18);margin-top:46px;overflow:hidden}
.pg_splash .bar i{display:block;height:100%;width:0;background:var(--gradTech);border-radius:2px;transition:width .2s}
.pg_splash .tips{color:rgba(255,255,255,.6);font-size:12px;margin-top:14px;height:18px}
.pg_splash .ft{position:absolute;bottom:34px;left:0;right:0;text-align:center;color:rgba(255,255,255,.4);font-size:10px;line-height:1.8}
.pg_splash .ft b{color:rgba(255,255,255,.7);font-weight:500}

/* 个人中心头部 */
.profile-hd{background:var(--gradMain);padding:8px 16px 22px;position:relative;overflow:hidden}
.profile-hd::after{content:'';position:absolute;right:-30px;top:-40px;width:150px;height:150px;background:radial-gradient(circle,rgba(0,201,255,.32),transparent 70%);filter:blur(14px)}
.profile-hd .logo{height:18px;position:relative}
.profile-hd .who{display:flex;align-items:center;gap:14px;margin-top:16px;position:relative}
.profile-hd .av{width:60px;height:60px;border-radius:50%;background:var(--gradTech);box-shadow:0 0 0 3px rgba(255,255,255,.22);display:flex;align-items:center;justify-content:center;color:#fff;font-size:24px;font-weight:700;flex-shrink:0}
.profile-hd .who .n{color:#fff;font-size:17px;font-weight:700}
.profile-hd .who .r{color:rgba(255,255,255,.65);font-size:12px;margin-top:4px;display:flex;align-items:center;gap:7px}
.profile-hd .who .r .st{background:rgba(255,255,255,.18);padding:2px 9px;border-radius:9px;font-size:11px;color:#fff}

/* 数据条 */
.statbar{display:flex;background:#fff;border-radius:14px;box-shadow:var(--sh);margin:-14px 16px 0;position:relative;z-index:2}
.statbar .s{flex:1;text-align:center;padding:13px 4px}
.statbar .s .v{font-size:18px;font-weight:700;color:var(--t1)}
.statbar .s .l{font-size:11px;color:var(--t3);margin-top:2px}
.statbar .s+.s{border-left:1px solid var(--line2)}

/* 视频播放页 */
.player-screen{background:#000}
.player-screen .navbar{background:rgba(0,0,0,.001);border-bottom:none;position:absolute;top:50px;left:0;right:0;z-index:40}
.player-screen .navbar .back,.player-screen .navbar .tt,.player-screen .navbar .more{color:#fff}
.player-area{flex:1;position:relative;background:#000;display:flex;align-items:center;justify-content:center}
.player-area .bigplay{width:64px;height:64px;border-radius:50%;background:rgba(255,255,255,.92);display:flex;align-items:center;justify-content:center;color:var(--cyanD)}
.player-area .bigplay svg{width:28px;height:28px;margin-left:3px}
.player-area .poster{position:absolute;inset:0;background:var(--gradMain)}
.player-ctrl{position:absolute;left:0;right:0;bottom:0;padding:18px;background:linear-gradient(transparent,rgba(0,0,0,.7));z-index:41}
.player-ctrl .ti{color:#fff;font-size:13.5px;font-weight:600;margin-bottom:10px}
.player-ctrl .progress{display:flex;align-items:center;gap:10px}
.player-ctrl .progress .bar{flex:1;height:4px;border-radius:2px;background:rgba(255,255,255,.3);position:relative;cursor:pointer}
.player-ctrl .progress .bar i{position:absolute;left:0;top:0;height:100%;width:34%;background:var(--gradTech);border-radius:2px}
.player-ctrl .progress .bar i::after{content:'';position:absolute;right:-5px;top:50%;transform:translateY(-50%);width:12px;height:12px;border-radius:50%;background:#fff;box-shadow:0 1px 4px rgba(0,0,0,.3)}
.player-ctrl .progress .tm{color:rgba(255,255,255,.85);font-size:11px;font-family:ui-monospace,Menlo,monospace}
.player-ctrl .tools{display:flex;align-items:center;gap:22px;margin-top:14px;color:#fff}
.player-ctrl .tools .ic{display:flex;flex-direction:column;align-items:center;gap:4px;font-size:10px;color:rgba(255,255,255,.75)}
.player-ctrl .tools .ic svg{width:22px;height:22px}
.player-ctrl .tools .ic.q{margin-left:auto;border:1px solid rgba(255,255,255,.4);border-radius:7px;padding:3px 9px;font-size:11px;flex-direction:row;gap:4px}

/* 文章正文 */
.article{padding:16px}
.article h1{font-size:20px;font-weight:700;line-height:1.4}
.article .meta{display:flex;align-items:center;gap:10px;color:var(--t3);font-size:12px;margin:12px 0 16px;flex-wrap:wrap}
.article .meta .au{display:flex;align-items:center;gap:6px}
.article .meta .au .a{width:22px;height:22px;border-radius:50%;background:var(--gradTech);color:#fff;font-size:11px;display:flex;align-items:center;justify-content:center}
.article p{font-size:14.5px;line-height:1.85;color:#3a4760;margin-bottom:14px}
.article .h2{font-size:16px;font-weight:700;margin:8px 0 12px;display:flex;align-items:center;gap:8px}
.article .h2::before{content:'';width:4px;height:15px;background:var(--gradTech);border-radius:2px}
.article .img{height:180px;border-radius:14px;background:var(--gradMain);margin:6px 0 16px;position:relative;overflow:hidden;display:flex;align-items:center;justify-content:center;color:rgba(255,255,255,.6);font-size:12px}
.article .img.cover{background-size:cover;background-position:center;color:transparent}
.article .img.cover::after{content:'';position:absolute;inset:0;background:linear-gradient(180deg,rgba(6,27,58,0) 55%,rgba(6,27,58,.35) 100%)}
.article .quote{background:rgba(0,152,232,.07);border-left:3px solid var(--cyan2);padding:12px 14px;border-radius:0 10px 10px 0;font-size:13.5px;color:var(--t2);margin-bottom:14px}

/* 报名表单提示 */
.notice{margin:14px 16px;background:rgba(0,152,232,.07);border-radius:12px;padding:12px 14px;display:flex;gap:10px;font-size:12.5px;color:var(--cyan2);line-height:1.6}
.notice svg{width:18px;height:18px;flex-shrink:0;margin-top:1px}

/* 视频号跳转提示 */
.wxjump{margin:14px 16px;background:#fff;border-radius:14px;box-shadow:var(--sh);padding:16px;display:flex;align-items:center;gap:13px}
.wxjump .ic{width:46px;height:46px;border-radius:12px;background:#07C160;display:flex;align-items:center;justify-content:center;color:#fff;flex-shrink:0}
.wxjump .ic svg{width:26px;height:26px}
.wxjump .tx{flex:1}
.wxjump .tx .t{font-size:14px;font-weight:600}
.wxjump .tx .d{font-size:12px;color:var(--t3);margin-top:2px}
"""

JS = r"""
const TABS = ['home','course','activity','news','profile'];
const TAB_LABEL = {home:'首页',course:'课程',activity:'培训',news:'资讯',profile:'我的'};
let stack = [];           // 导航栈（非 tab 页）
let curTab = 'home';
var userState = 'approved';  // approved | review
const $ = s => document.querySelector(s);

function pageEl(id){ return document.getElementById(id); }
function isTabId(id){ return TABS.includes(String(id).replace('pg_','')); }

/* 清空除 keep 之外所有页面的临时状态，保证任意时刻只有一个页面处于"可见"链路 */
function clearStates(keep){
  document.querySelectorAll('.page').forEach(p=>{
    if(p===keep) return;
    p.classList.remove('show','cur','under');
    p.style.transform=''; p.style.transition=''; p.style.visibility='';
  });
}

/* 切 Tab：当前页直接置顶，清空 push 栈 */
function switchTab(name){
  const el = pageEl('pg_'+name);
  if(!el) return;
  clearStates(el);
  el.classList.add('tab','cur','show');
  el.scrollTop = 0; const b = el.querySelector('.body'); if(b) b.scrollTop=0;
  stack = []; curTab = name;
  updateTabbar(); updateCapsule();
}

/* push 一个新页面（tab 页自动降级为切 Tab，避免与 Tab 状态冲突） */
function navigate(id){
  const el = pageEl(id);
  if(!el) return;
  if(isTabId(id)){ switchTab(id.replace('pg_','')); return; }

  const curId = stack.length ? stack[stack.length-1] : 'pg_'+curTab;
  const curEl = pageEl(curId);
  if(curEl === el) return;
  stack.push(id);

  // 除目标页与直接底层页外，其余页面一律清空（防止残留页面叠在一起）
  document.querySelectorAll('.page').forEach(p=>{
    if(p!==el && p!==curEl) p.classList.remove('show','cur','under');
  });
  if(curEl){ curEl.classList.remove('show','cur'); curEl.classList.add('under'); }

  el.classList.remove('under');
  el.style.transition='none';
  el.style.transform='translateX(100%)';
  el.style.visibility='visible';
  el.classList.add('show');
  void el.offsetWidth;                    // 强制重排，确保过渡起点生效
  el.style.transition='';
  el.style.transform='';                 // 交回 CSS：.page.show -> translateX(0)
  updateCapsule();
}

/* 返回上一层 */
function back(){
  const id = stack.pop();
  if(!id) return;
  const el = pageEl(id);
  const prev = stack.length ? stack[stack.length-1] : 'pg_'+curTab;
  const pe = pageEl(prev);
  if(pe){
    pe.classList.remove('under');
    pe.classList.add('show');
    if(isTabId(prev)) pe.classList.add('cur');
  }
  if(el){
    el.style.transform='translateX(100%)';
    setTimeout(()=>{
      el.classList.remove('show');
      el.style.transform=''; el.style.transition=''; el.style.visibility='';
    }, 340);
  }
  updateCapsule();
}
function updateTabbar(){
  document.querySelectorAll('.tabbar .tb').forEach(t=>{
    t.classList.toggle('on', t.dataset.tab===curTab);
  });
}
function updateCapsule(){
  const dark = document.querySelector('.page.show .navbar.dark, .page.show.pg_splash, .player-screen.show, .page.show .profile-hd');
  document.querySelectorAll('.capsule').forEach(c=>c.classList.toggle('dark', !!dark));
  document.querySelectorAll('.sysbar').forEach(s=>s.classList.toggle('dark', !!dark));
}
function toast(msg){
  const t = $('#toast'); t.textContent=msg; t.classList.add('show');
  clearTimeout(t._t); t._t=setTimeout(()=>t.classList.remove('show'),1700);
}
function openMask(id){ document.getElementById(id).classList.add('show'); }
function closeMask(id){ document.getElementById(id).classList.remove('show'); }

document.addEventListener('click', e=>{
  const T = e.target.closest('[data-go]');
  if(T){ const a=T.dataset.go.split(':');
    if(a[0]==='tab'){ switchTab(a[1]); }
    else if(a[0]==='nav'){ navigate('pg_'+a[1]); }
    else if(a[0]==='back'){ back(); }
    else if(a[0]==='mask'){ openMask(a[1]); }
    else if(a[0]==='closemask'){ closeMask(a[1]); }
    else if(a[0]==='toast'){ toast(T.dataset.msg||'已操作'); }
    else if(a[0]==='url'){ toast('即将跳转视频号直播（演示）'); }
    else if(a[0]==='review'){ if(userState!=='approved'){ openMask('m_review'); return;} navigate('pg_'+a[2]); }
    else if(a[0]==='review-home'){ userState='review'; switchTab('home'); toast('游客预览模式 · 仅可浏览公开内容'); }
    else if(a[0]==='success'){ closeMask('m_success'); back(); }
    return;
  }
  // 收藏切换
  const fav = e.target.closest('[data-fav]');
  if(fav){ fav.classList.toggle('on'); const on=fav.classList.contains('on');
    fav.querySelector('path') && (fav.querySelector('path').setAttribute('fill', on?'currentColor':''));
    toast(on?'已收藏':'已取消收藏'); return; }
  // tab 切换（分类）
  const tab = e.target.closest('.tabs .t');
  if(tab){ tab.parentElement.querySelectorAll('.t').forEach(x=>x.classList.remove('on')); tab.classList.add('on'); return; }
});

// 验证码倒计时
function startCode(btn){
  if(btn.disabled) return;
  let n=60; btn.disabled=true; btn.textContent=n+'s';
  const iv=setInterval(()=>{ n--; if(n<=0){ clearInterval(iv); btn.disabled=false; btn.textContent='获取验证码'; } else btn.textContent=n+'s'; },1000);
}
// 视频进度拖拽
function seekBar(bar,e){
  const r=bar.getBoundingClientRect(); const x=Math.max(0,Math.min(1,(e.clientX-r.left)/r.width));
  bar.querySelector('i').style.width=(x*100)+'%';
  const sec=Math.floor(x*1490); toast('已跳转 '+Math.floor(sec/60)+':'+String(sec%60).padStart(2,'0'));
}

// 启动页 loading
function splash(){
  const tips=['正在初始化安全学习环境…','同步课程与培训数据…','加载医生学习档案…'];
  let p=0,i=0; const bar=$('#sp_bar'), tp=$('#sp_tip');
  const iv=setInterval(()=>{
    p+=Math.random()*9+4; if(p>100)p=100; bar.style.width=p+'%';
    tp.textContent=tips[Math.min(2,Math.floor(p/34))];
    if(p>=100){ clearInterval(iv); setTimeout(()=>{ switchTab('home'); },500); }
  },230);
}
window.addEventListener('load',()=>{ updateTabbar(); splash(); });
"""

# ===================== helpers =====================
def svg(name, size=24, cls=''):
    return f'<svg class="{cls}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="{size}" height="{size}"><use href="#{name}"/></svg>'

ICONS = {
 'home':'<path d="M3 9l9-7 9 7v11a2 2 0 01-2 2H5a2 2 0 01-2-2z"/>',
 'play':'<polygon points="6 4 20 12 6 20 6 4"/>',
 'book':'<path d="M4 19.5A2.5 2.5 0 016.5 17H20V3H6.5A2.5 2.5 0 004 5.5z"/>',
 'cal':'<rect x="3" y="4" width="18" height="18" rx="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/>',
 'news':'<path d="M4 4h16v16H4z"/><line x1="8" y1="8" x2="16" y2="8"/><line x1="8" y1="12" x2="16" y2="12"/><line x1="8" y1="16" x2="13" y2="16"/>',
 'user':'<path d="M20 21v-2a4 4 0 00-4-4H8a4 4 0 00-4 4v2"/><circle cx="12" cy="7" r="4"/>',
 'search':'<circle cx="11" cy="11" r="7"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>',
 'back':'<path d="M15 18l-6-6 6-6"/>',
 'arrow':'<path d="M9 18l6-6-6-6"/>',
 'more':'<circle cx="5" cy="12" r="1.6"/><circle cx="12" cy="12" r="1.6"/><circle cx="19" cy="12" r="1.6"/>',
 'heart':'<path d="M20.84 4.61a5.5 5.5 0 00-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 00-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 000-7.78z"/>',
 'share':'<circle cx="18" cy="5" r="3"/><circle cx="6" cy="12" r="3"/><circle cx="18" cy="19" r="3"/><line x1="8.6" y1="13.5" x2="15.4" y2="17.5"/><line x1="15.4" y1="6.5" x2="8.6" y2="10.5"/>',
 'clock':'<circle cx="12" cy="12" r="9"/><polyline points="12 7 12 12 15 14"/>',
 'eye':'<path d="M1 12s4-7 11-7 11 7 11 7-4 7-11 7-11-7-11-7z"/><circle cx="12" cy="12" r="3"/>',
 'star':'<polygon points="12 2 15 9 22 9.3 17 14 18.5 21 12 17 5.5 21 7 14 2 9.3 9 9"/>',
 'pin':'<path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0118 0z"/><circle cx="12" cy="10" r="3"/>',
 'doc':'<path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/><polyline points="14 2 14 8 20 8"/>',
 'msg':'<path d="M21 15a2 2 0 01-2 2H7l-4 4V5a2 2 0 012-2h14a2 2 0 012 2z"/>',
 'set':'<circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 00.33 1.82l.06.06a2 2 0 11-2.83 2.83l-.06-.06a1.65 1.65 0 00-1.82-.33 1.65 1.65 0 00-1 1.51V21a2 2 0 01-4 0v-.09A1.65 1.65 0 009 19.4a1.65 1.65 0 00-1.82.33l-.06.06a2 2 0 11-2.83-2.83l.06-.06a1.65 1.65 0 00.33-1.82 1.65 1.65 0 00-1.51-1H3a2 2 0 010-4h.09A1.65 1.65 0 004.6 9a1.65 1.65 0 00-.33-1.82l-.06-.06a2 2 0 112.83-2.83l.06.06a1.65 1.65 0 001.82.33H9a1.65 1.65 0 001-1.51V3a2 2 0 014 0v.09a1.65 1.65 0 001 1.51 1.65 1.65 0 001.82-.33l.06-.06a2 2 0 112.83 2.83l-.06.06a1.65 1.65 0 00-.33 1.82V9a1.65 1.65 0 001.51 1H21a2 2 0 010 4h-.09a1.65 1.65 0 00-1.51 1z"/>',
 'tel':'<path d="M22 16.92v3a2 2 0 01-2.18 2 19.79 19.79 0 01-8.63-3.07 19.5 19.5 0 01-6-6 19.79 19.79 0 01-3.07-8.67A2 2 0 014.11 2h3a2 2 0 012 1.72c.13.96.36 1.9.7 2.81a2 2 0 01-.45 2.11L8.09 9.91a16 16 0 006 6l1.27-1.27a2 2 0 012.11-.45c.91.34 1.85.57 2.81.7A2 2 0 0122 16.92z"/>',
 'live':'<rect x="2" y="6" width="14" height="12" rx="2"/><polygon points="18 9 22 7 22 17 18 15"/>',
 'badge':'<rect x="3" y="5" width="18" height="14" rx="2"/><line x1="3" y1="10" x2="21" y2="10"/>',
 'cert':'<circle cx="12" cy="9" r="5"/><path d="M9 13.5L7 22l5-3 5 3-2-8.5"/>',
 'videocam':'<polygon points="23 7 16 12 23 17 23 7"/><rect x="1" y="5" width="15" height="14" rx="2"/>',
 'bell':'<path d="M18 8a6 6 0 00-12 0c0 7-3 9-3 9h18s-3-2-3-9"/><path d="M13.73 21a2 2 0 01-3.46 0"/>',
 'info':'<circle cx="12" cy="12" r="9"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/>',
 'check':'<polyline points="20 6 9 17 4 12"/>',
 'lock':'<rect x="3" y="11" width="18" height="11" rx="2"/><path d="M7 11V7a5 5 0 0110 0v4"/>',
 'wx':'<path d="M9 4C4.6 4 1 7 1 10.8c0 2.2 1.2 4.1 3 5.4L3.2 18l2.7-1.4c.9.25 1.8.4 2.8.4h.5a5.6 5.6 0 01-.2-1.5c0-3.3 3.1-6 7-6h.6C15.4 6 12.5 4 9 4z"/><path d="M23 14.5C23 11.5 20 9 16.5 9S10 11.5 10 14.5 13 20 16.5 20c.8 0 1.6-.13 2.3-.36L21 21l-.6-2.1c1.4-1 2.6-2.5 2.6-4.4z"/>',
 'edit':'<path d="M11 4H4a2 2 0 00-2 2v14a2 2 0 002 2h14a2 2 0 002-2v-7"/><path d="M18.5 2.5a2.12 2.12 0 013 3L12 15l-4 1 1-4z"/>',
 'plus':'<line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/>',
}

def ICON(name, size=24, cls=''):
    return f'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="{size}" height="{size}" class="{cls}">{ICONS[name]}</svg>'

def NB(title, back=True, dark=False, act=''):
    b = f'<button class="back" data-go="back">{ICON("back",24)}</button>' if back else '<span style="width:30px"></span>'
    ac = f'<div class="act">{act}</div>' if act else ''
    return f'<div class="navbar{" dark" if dark else ""}">{b}<div class="tt">{title}</div>{ac}</div>'

def TABBAR(active):
    def tb(name, icon, label, dot=False):
        return f'<div class="tb{" on" if name==active else ""}" data-tab="{name}" data-go="tab:{name}">{ICON(icon,23)}{label}{"<span class=\'dot\'></span>" if dot else ""}</div>'
    return ('<div class="tabbar">'
        + tb('home','home','首页')
        + tb('course','book','课程')
        + tb('activity','cal','培训')
        + tb('news','news','资讯')
        + tb('profile','user','我的',True)
        + '</div>')

def COURSE_CARD(d):
    img = img_cls(pick_img(COURSE_IMGS, d[0]))
    return (f'<div class="li" data-go="review:nav:course_detail" data-msg="进入课程详情">'
        f'<div class="thumb cover {img}"><span class="pi">{ICON("play",26)}</span></div>'
        f'<div class="ct"><div class="ti">{d[0]}</div>'
        f'<div class="me">{ICON("user",12)} {d[1]} · {d[2]}</div>'
        f'<div class="bo"><span class="pr">{ICON("eye",12)} {d[3]} 人在学</span>'
        f'<span class="badge b-cyan" style="margin-left:auto">{d[4]}</span></div></div></div>')

def ACT_CARD(d):
    st = d[4]
    bc = {'报名中':'b-live','即将开始':'b-warn','已满':'b-hot','已结束':'b-gray'}.get(st,'b-gray')
    img = img_cls(pick_img(ACT_IMGS, d[0]))
    return (f'<div class="li" data-go="review:nav:activity_detail" data-msg="进入活动详情">'
        f'<div class="thumb cover {img}"><span class="pi">{ICON("cal",26)}</span></div>'
        f'<div class="ct"><div class="ti">{d[0]}</div>'
        f'<div class="me">{ICON("clock",12)} {d[1]} · {d[2]}</div>'
        f'<div class="bo"><span class="pr">{ICON("user",12)} {d[3]} 人报名</span>'
        f'<span class="badge {bc}" style="margin-left:auto">{st}</span></div></div></div>')

def NEWS_CARD(d):
    f = pick_news_img(d[1], d[0])
    return (f'<div class="li" data-go="nav:article"><div class="thumb cover {img_cls(f)}"></div>'
        f'<div class="ct"><div class="ti">{d[0]}</div>'
        f'<div class="me" style="color:var(--t3)">{d[1]} · {ICON("clock",12)} {d[2]}</div>'
        f'<div class="bo"><span class="badge b-navy" style="font-size:10px">{d[1]}</span>'
        f'<span class="pr" style="margin-left:auto">{ICON("eye",12)} {d[3]}</span></div></div></div>')

S = {}
# ---------- 资讯中心 ----------
S['pg_news'] = NB('资讯中心', False) + f'''<div class="body" style="padding:0">
  <div class="tabs"><div class="t on">学术资讯</div><div class="t">平台介绍</div><div class="t">器械知识</div><div class="t">全部</div></div>
  {NEWS_CARD(('2026 妇科微创诊疗新进展专家共识','学术资讯','09-20','1.2万'))}
  {NEWS_CARD(('宫腔镜设备日常维护与故障排查','器械知识','09-18','8652'))}
  {NEWS_CARD(('科迈森培训基地获国家级继续教育资质','平台介绍','09-15','5321'))}
  {NEWS_CARD(('冷刀宫腔镜 vs 电切镜：适应证选择','学术资讯','09-12','9870'))}
  {NEWS_CARD(('能量器械安全使用白皮书（2026版）','器械知识','09-08','7433'))}
</div>''' + TABBAR('news')

# ---------- 文章详情 ----------
S['pg_article'] = NB('资讯详情', True) + f'''<div class="body" style="padding:0">
  <div class="article">
    <h1>宫腔镜设备日常维护与故障排查</h1>
    <div class="meta"><span class="au"><span class="a">技</span>技术工程师 · 王工</span><span>{ICON("clock",13)} 09-18</span><span>{ICON("eye",13)} 8652 阅读</span></div>
    <div class="img cover {img_cls('news-2.jpg')}"></div>
    <p>宫腔镜作为高精度微创器械，日常维护直接影响成像质量与使用寿命。本文梳理临床常见的维护要点与故障排查路径。</p>
    <div class="h2">一、日常清洁与灭菌</div>
    <p>术后应立即用酶洗液冲洗镜体通道，禁用含氯消毒剂长时间浸泡；光缆盘绕半径不小于 15cm，避免折损导光纤维。</p>
    <div class="quote">提示：镜体切忌超声清洗超过 3 分钟，以免接合部脱胶。</div>
    <div class="h2">二、常见故障排查</div>
    <p><b>成像发暗：</b>优先检查光源灯泡寿命与导光束端面清洁度；<b>图像模糊：</b>多为物镜污染或干涸体液残留，需专业返修。</p>
    <div class="img cover {img_cls('news-6.jpg')}"></div>
    <p>如自行处理无效，请通过「我的 — 联系我们」提交报修，平台将安排工程师上门。</p>
  </div>
  <div class="tabbar" style="height:58px"><div class="btn ghost sm" style="margin:0 10px 0 16px;flex:0 0 auto" data-fav="1">{ICON("heart",16)} 点赞</div><div class="btn ghost sm" style="margin:0 16px 0 0;flex:1" data-go="nav:msg">{ICON("share",16)} 分享给同事</div></div>
</div>'''

# ---------- 平台介绍 ----------
S['pg_about'] = NB('平台介绍', True) + f'''<div class="body" style="padding:0">
  <div class="banner cover {img_cls(pick_img(ACT_IMGS,'about_banner'))}" style="margin-top:12px"><div class="t">科迈森培训中心</div><div class="d">专注妇科微创器械的规范化培训与学术交流</div></div>
  <div class="sec-h"><div class="t">培训中心</div></div>
  <div class="card" style="margin:0 16px;padding:16px;font-size:13.5px;color:var(--t2);line-height:1.8">科迈森在线培训平台由 KMS Medical 搭建，依托厂家临床资源与三甲医院专家团队，为妇科微创医师提供从入门到进阶的系统化培训路径。</div>
  <div class="sec-h"><div class="t">专家团队</div></div>
  <div class="li" style="margin:0 16px 12px">{ICON("user",26)}<div class="ct"><div class="ti">王建国 主任医师</div><div class="me">北京协和医院 · 宫腔镜</div></div></div>
  <div class="li" style="margin:0 16px 12px">{ICON("user",26)}<div class="ct"><div class="ti">陈敏 教授</div><div class="me">四川大学华西 · 冷刀宫腔镜</div></div></div>
  <div class="sec-h"><div class="t">培训体系</div></div>
  <div class="entries" style="grid-template-columns:repeat(3,1fr)">
    <div class="e"><div class="ic">{ICON("play",20)}</div><div class="lb">在线课程</div></div>
    <div class="e"><div class="ic">{ICON("cal",20)}</div><div class="lb">线下研修</div></div>
    <div class="e"><div class="ic">{ICON("live",20)}</div><div class="lb">视频号直播</div></div>
  </div>
  <div style="height:8px"></div>
</div>'''

# ---------- 个人中心 ----------
S['pg_profile'] = f'''<div class="profile-hd" style="padding-top:56px">
  <img class="logo" src="{LOGO_REV}" alt="logo">
  <div class="who"><div class="av">李</div><div><div class="n">李慕白</div><div class="r"><span class="st">已通过</span>副主任医师 · 东莞市人民医院</div></div></div>
</div>
<div class="body" style="padding:0">
  <div class="statbar"><div class="s"><div class="v">42.6</div><div class="l">学习时长(h)</div></div><div class="s"><div class="v">12</div><div class="l">已学课程</div></div><div class="s"><div class="v">28</div><div class="l">我的收藏</div></div></div>
  <div class="menu">
    <div class="m" data-go="nav:mylearn"><div class="ic">{ICON("book",18)}</div><div class="lb">我的学习</div><div class="rg">12 门 <span class="badge2">3</span>{ICON("arrow",15)}</div></div>
    <div class="m" data-go="nav:mysignup"><div class="ic">{ICON("cal",18)}</div><div class="lb">我的报名</div><div class="rg">2 条{ICON("arrow",15)}</div></div>
    <div class="m" data-go="nav:myfav"><div class="ic">{ICON("star",18)}</div><div class="lb">我的收藏</div><div class="rg">28{ICON("arrow",15)}</div></div>
    <div class="m" data-go="nav:msg"><div class="ic">{ICON("bell",18)}</div><div class="lb">消息通知</div><div class="rg"><span class="badge2">5</span>{ICON("arrow",15)}</div></div>
    <div class="m" data-go="nav:contact"><div class="ic">{ICON("tel",18)}</div><div class="lb">联系我们</div><div class="rg">{ICON("arrow",15)}</div></div>
    <div class="m" data-go="nav:aboutus"><div class="ic">{ICON("info",18)}</div><div class="lb">关于我们</div><div class="rg">{ICON("arrow",15)}</div></div>
    <div class="m" data-go="toast" data-msg="设置（演示）"><div class="ic">{ICON("set",18)}</div><div class="lb">设置</div><div class="rg">{ICON("arrow",15)}</div></div>
    <div class="m" data-go="toast" data-msg="已退出登录（演示）"><div class="ic">{ICON("lock",18)}</div><div class="lb">退出登录</div><div class="rg">{ICON("arrow",15)}</div></div>
  </div>
  <div style="height:8px"></div>
</div>''' + TABBAR('profile')

# ---------- 个人资料 ----------
S['pg_profile_edit'] = NB('个人资料', True) + f'''<div class="body" style="padding:0">
  <div style="display:flex;flex-direction:column;align-items:center;padding:20px 0 8px">
    <div class="av" style="width:64px;height:64px;border-radius:50%;background:var(--gradTech);color:#fff;font-size:26px;font-weight:700;display:flex;align-items:center;justify-content:center;box-shadow:0 0 0 3px rgba(0,201,255,.18)">李</div>
    <div style="font-size:12.5px;color:var(--cyan2);margin-top:8px">点击更换头像</div>
  </div>
  <div class="field">
    <div class="row"><label>手机号</label><input value="138 0013 8000"><button class="getcode" onclick="startCode(this)">更换</button></div>
    <div class="row"><label>姓名</label><input value="李慕白"></div>
    <div class="row"><label>职称</label><input value="副主任医师"><span class="arrow">{ICON("arrow",16)}</span></div>
    <div class="row"><label>所在医院</label><input value="东莞市人民医院"></div>
    <div class="row"><label>所在科室</label><input value="妇科"><span class="arrow">{ICON("arrow",16)}</span></div>
    <div class="row"><label>专业方向</label><input value="宫腔镜微创"></div>
    <div class="row"><label>执业证号</label><input value="11032000012345"></div>
  </div>
  <div class="notice" style="margin-top:14px">{ICON("info",18)}执业证号、医院、科室等关键信息修改后，需重新提交审核。</div>
  <div style="margin:18px 16px"><div class="btn" data-go="toast" data-msg="资料已保存">保存</div></div>
</div>'''

# ---------- 我的学习 ----------
S['pg_mylearn'] = NB('我的学习', True) + f'''<div class="body" style="padding:0">
  <div class="card" style="margin:14px 16px;padding:14px">
    <div style="display:flex;justify-content:space-around;text-align:center">
      <div><div style="font-size:18px;font-weight:700;color:var(--t1)">42.6h</div><div style="font-size:11px;color:var(--t3);margin-top:2px">学习总时长</div></div>
      <div style="width:1px;background:var(--line2)"></div>
      <div><div style="font-size:18px;font-weight:700;color:var(--t1)">12</div><div style="font-size:11px;color:var(--t3);margin-top:2px">已学课程</div></div>
      <div style="width:1px;background:var(--line2)"></div>
      <div><div style="font-size:18px;font-weight:700;color:var(--t1)">9</div><div style="font-size:11px;color:var(--t3);margin-top:2px">已完成</div></div>
    </div>
  </div>
  <div class="sec-h"><div class="t">最近学习</div></div>
  {COURSE_CARD(('子宫纵隔切开术 · 4K 完整演示','王建国 主任医师','北京协和医院','1280','已学 62%'))}
  <div style="margin:-4px 16px 12px;height:4px;border-radius:2px;background:var(--line2)"><i style="display:block;height:100%;width:62%;background:var(--gradTech);border-radius:2px"></i></div>
  {COURSE_CARD(('KMS 电切镜系统标准操作','李慕白 副主任医师','东莞市人民医院','964','已学 28%'))}
  <div style="margin:-4px 16px 12px;height:4px;border-radius:2px;background:var(--line2)"><i style="display:block;height:100%;width:28%;background:var(--gradTech);border-radius:2px"></i></div>
  <div class="sec-h"><div class="t">收藏课程</div></div>
  {COURSE_CARD(('冷刀宫腔镜临床应用要点','陈敏 教授','四川大学华西','1577','宫腔镜'))}
</div>'''

# ---------- 我的报名 ----------
S['pg_mysignup'] = NB('我的报名', True) + f'''<div class="body" style="padding:0">
  <div class="li" style="margin-top:14px" data-go="nav:activity_detail">{ICON("cal",26)}<div class="ct"><div class="ti">宫腔镜四级手术高阶研修班</div><div class="me">报名时间 09-20 · 活动 10-18 东莞</div><div class="bo"><span class="badge b-ok" style="margin-left:0">已通过</span><span class="pr" style="margin-left:auto">平台已电话联系</span></div></div></div>
  <div class="li" data-go="nav:activity_detail">{ICON("cal",26)}<div class="ct"><div class="ti">妇科能量器械规范化培训班</div><div class="me">报名时间 09-12 · 活动 11-02 广州</div><div class="bo"><span class="badge b-cyan" style="margin-left:0">待审核</span><span class="pr" style="margin-left:auto">{ICON("bell",12)} 审核中</span></div></div></div>
  <div class="li" data-go="nav:activity_detail">{ICON("cal",26)}<div class="ct"><div class="ti">KMS 新品发布会 · 线上直播</div><div class="me">报名时间 09-25 · 活动 09-28 线上</div><div class="bo"><span class="badge b-warn" style="margin-left:0">已联系</span><span class="pr" style="margin-left:auto">会议链接已发送</span></div></div></div>
</div>'''

# ---------- 我的收藏 ----------
S['pg_myfav'] = NB('我的收藏', True) + f'''<div class="body" style="padding:0">
  <div class="tabs"><div class="t on">课程</div><div class="t">活动</div></div>
  {COURSE_CARD(('冷刀宫腔镜临床应用要点','陈敏 教授','四川大学华西','1577','宫腔镜'))}
  {COURSE_CARD(('KMS 电切镜系统标准操作','李慕白 副主任医师','东莞市人民医院','964','能量器械'))}
  {COURSE_CARD(('腹腔镜下子宫肌瘤剔除术','张伟 主任医师','中山一院','2103','腹腔镜'))}
  <div class="sec-h"><div class="t">收藏的活动</div></div>
  {ACT_CARD(('宫腔镜四级手术高阶研修班','10月18日 · 东莞','线下','86','报名中'))}
</div>'''

# ---------- 消息通知 ----------
S['pg_msg'] = NB('消息通知', True, '全部已读') + f'''<div class="body" style="padding:0">
  <div class="li" style="margin-top:14px;align-items:flex-start">{ICON("badge",24)}<div class="ct"><div class="ti" style="font-size:14px">报名审核通过<dot style="float:right;width:8px;height:8px;border-radius:50%;background:var(--bad);display:inline-block"></dot></div><div class="me">您报名的「宫腔镜四级手术高阶研修班」已通过，平台将电话联系您。</div><div class="bo"><span class="pr">09-20 14:30</span></div></div></div>
  <div class="li" style="align-items:flex-start">{ICON("cal",24)}<div class="ct"><div class="ti" style="font-size:14px">培训活动提醒</div><div class="me">「妇科能量器械规范化培训班」将于 11-02 在广州开班，报名即将截止。</div><div class="bo"><span class="pr">09-18 09:12</span></div></div></div>
  <div class="li" style="align-items:flex-start">{ICON("cert",24)}<div class="ct"><div class="ti" style="font-size:14px">证书发放通知</div><div class="me">您已完成「单孔腹腔镜实操工作坊」，证书已生成，可在我的学习查看。</div><div class="bo"><span class="pr">09-15 16:40</span></div></div></div>
  <div class="li" style="align-items:flex-start">{ICON("news",24)}<div class="ct"><div class="ti" style="font-size:14px">系统公告</div><div class="me">平台将于本周日 02:00-04:00 进行系统维护，期间暂不可访问。</div><div class="bo"><span class="pr">09-12 20:00</span></div></div></div>
</div>'''

# ---------- 联系我们 ----------
S['pg_contact'] = NB('联系我们', True) + f'''<div class="body" style="padding:0">
  <div class="wxjump" style="margin-top:14px"><div class="ic">{ICON("wx",26)}</div><div class="tx"><div class="t">学术顾问微信</div><div class="d">扫码或搜索 KMS_Academy 添加</div></div><div class="badge b-ok">已复制</div></div>
  <div class="card" style="margin:14px 16px;padding:6px 14px">
    <div class="m"><div class="ic">{ICON("tel",18)}</div><div class="lb">客服电话</div><div class="rg">400-888-0000 {ICON("arrow",15)}</div></div>
    <div class="m"><div class="ic">{ICON("msg",18)}</div><div class="lb">客服邮箱</div><div class="rg">service@kms-med.com {ICON("arrow",15)}</div></div>
    <div class="m"><div class="ic">{ICON("pin",18)}</div><div class="lb">办公地址</div><div class="rg">东莞市松山湖高新区 {ICON("arrow",15)}</div></div>
  </div>
  <div class="sec-h"><div class="t">意见反馈</div></div>
  <div class="field" style="margin:0 16px">
    <div class="row" style="align-items:flex-start"><label style="padding-top:14px">内容</label><textarea placeholder="请描述您遇到的问题或建议" rows="3"></textarea></div>
    <div class="row"><label>联系电话</label><input placeholder="选填，便于回访"></div>
  </div>
  <div style="margin:18px 16px"><div class="btn" data-go="toast" data-msg="反馈已提交，感谢您的建议">提交反馈</div></div>
</div>'''

# ---------- 关于我们 ----------
S['pg_aboutus'] = NB('关于我们', True) + f'''<div class="body" style="padding:0">
  <div style="text-align:center;padding:26px 0"><img src="{LOGO_ICON}" style="width:64px;height:64px;border-radius:18px;box-shadow:0 10px 28px rgba(0,201,255,.4)"><div style="font-size:15px;font-weight:700;margin-top:12px">科迈森在线培训平台</div><div style="font-size:11.5px;color:var(--t3);margin-top:4px">KMS Medical Technology</div></div>
  <div class="menu">
    <div class="m" data-go="toast" data-msg="当前版本 V2.0.3"><div class="ic">{ICON("info",18)}</div><div class="lb">版本号</div><div class="rg">V2.0.3 {ICON("arrow",15)}</div></div>
    <div class="m" data-go="toast" data-msg="用户协议（演示）"><div class="ic">{ICON("doc",18)}</div><div class="lb">用户协议</div><div class="rg">{ICON("arrow",15)}</div></div>
    <div class="m" data-go="toast" data-msg="隐私政策（演示）"><div class="ic">{ICON("lock",18)}</div><div class="lb">隐私政策</div><div class="rg">{ICON("arrow",15)}</div></div>
    <div class="m" data-go="toast" data-msg="© 2026 KMS Medical">{ICON("copyright",18) if 'copyright' in ICONS else ICON("info",18)}<div class="lb">版权信息</div><div class="rg">{ICON("arrow",15)}</div></div>
  </div>
  <div style="height:8px"></div>
</div>'''

# ---------- 忘记密码 ----------
S['pg_forgot'] = NB('忘记密码', True) + f'''<div class="body" style="padding:0">
  <div style="font-size:13px;color:var(--t2);padding:18px 16px 6px">通过原手机号验证身份后重置登录密码（8-20 位，字母+数字组合）。</div>
  <div class="field" style="margin-top:14px">
    <div class="row"><label>手机号</label><input placeholder="请输入注册手机号" value="138 0013 8000"></div>
    <div class="row"><label>验证码</label><input placeholder="请输入验证码"><button class="getcode" onclick="startCode(this)">获取验证码</button></div>
    <div class="row"><label>新密码</label><input placeholder="8-20 位，字母+数字" type="password"></div>
    <div class="row"><label>确认密码</label><input placeholder="再次输入新密码" type="password"></div>
  </div>
  <div style="margin:20px 16px"><div class="btn" data-go="toast" data-msg="密码已重置，请重新登录">重置密码</div></div>
</div>'''

# ---------- 启动页 ----------
S['pg_splash'] = f'''  <div class="glow"></div>
  <img class="tile" src="{LOGO_ICON}" alt="logo">
  <div class="nm">科迈森</div>
  <div class="su">KMS MEDICAL ACADEMY</div>
  <div class="bar"><i id="sp_bar"></i></div>
  <div class="tips" id="sp_tip"></div>
  <div class="ft">Powered by <b>KMS Medical Technology</b><br>© 2026 科迈森在线培训平台</div>'''

# ---------- 登录 ----------
S['pg_login'] = NB('登录', True) + f'''<div class="body" style="padding:0">
  <div style="text-align:center;padding:30px 0 18px"><img src="{LOGO_ICON}" style="width:70px;height:70px;border-radius:18px;box-shadow:0 10px 30px rgba(0,201,255,.4)"></div>
  <div style="text-align:center;font-size:20px;font-weight:700;color:var(--t1)">欢迎登录</div>
  <div style="text-align:center;font-size:12.5px;color:var(--t3);margin-top:6px">科迈森妇科微创器械在线培训平台</div>
  <div class="field" style="margin-top:24px">
    <div class="row"><label>手机号</label><input placeholder="请输入手机号" value="138 0013 8000"></div>
    <div class="row"><label>验证码</label><input placeholder="请输入验证码"><button class="getcode" onclick="startCode(this)">获取验证码</button></div>
  </div>
  <div style="margin:22px 16px"><div class="btn" data-go="toast" data-msg="登录成功">登录</div></div>
  <div style="margin:0 16px"><div class="btn ghost" data-go="toast" data-msg="微信一键登录（演示）">{ICON("wx",18)} 微信一键登录</div></div>
  <div style="text-align:center;margin-top:20px;font-size:13px;color:var(--t3)">还没有账号？<span style="color:var(--cyan2);font-weight:600" data-go="nav:reg1">立即注册</span></div>
  <div style="text-align:center;margin-top:10px;font-size:12.5px;color:var(--t3)"><span style="color:var(--cyan2)" data-go="nav:forgot">忘记密码</span> · <span style="color:var(--cyan2)" data-go="review:nav:course" data-msg="">体验未审核账号</span></div>
  <div class="chk" style="margin-top:18px;justify-content:center"><svg viewBox="0 0 24 24" fill="none" stroke="var(--cyan2)" stroke-width="2" width="16" height="16"><path d="M20 6L9 17l-5-5"/></svg>已阅读并同意<a>《用户协议》</a>与<a>《隐私政策》</a></div>
</div>'''

# ---------- 注册 步骤1 ----------
S['pg_reg1'] = NB('注册', True) + f'''<div class="body" style="padding:0">
  <div style="display:flex;gap:8px;padding:18px 16px">
    <div style="flex:1;text-align:center"><div style="width:28px;height:28px;border-radius:50%;background:var(--gradTech);color:#fff;margin:0 auto;display:flex;align-items:center;justify-content:center;font-weight:700;font-size:13px">1</div><div style="font-size:11.5px;color:var(--cyanD);font-weight:600;margin-top:6px">手机验证</div></div>
    <div style="flex:1;text-align:center;opacity:.5"><div style="width:28px;height:28px;border-radius:50%;background:var(--line2);color:var(--t3);margin:0 auto;display:flex;align-items:center;justify-content:center;font-weight:700;font-size:13px">2</div><div style="font-size:11.5px;color:var(--t3);margin-top:6px">医生信息</div></div>
    <div style="flex:1;text-align:center;opacity:.5"><div style="width:28px;height:28px;border-radius:50%;background:var(--line2);color:var(--t3);margin:0 auto;display:flex;align-items:center;justify-content:center;font-weight:700;font-size:13px">3</div><div style="font-size:11.5px;color:var(--t3);margin-top:6px">医院信息</div></div>
  </div>
  <div class="field">
    <div class="row"><label>手机号</label><input placeholder="请输入手机号" value="138 0013 8000"></div>
    <div class="row"><label>验证码</label><input placeholder="请输入验证码"><button class="getcode" onclick="startCode(this)">获取验证码</button></div>
  </div>
  <div class="chk"><svg viewBox="0 0 24 24" fill="none" stroke="var(--cyan2)" stroke-width="2" width="16" height="16"><path d="M20 6L9 17l-5-5"/></svg>已阅读并同意<a>《用户协议》</a>与<a>《隐私政策》</a></div>
  <div style="margin:18px 16px"><div class="btn" data-go="nav:reg2">下一步</div></div>
</div>'''

# ---------- 注册 步骤2 ----------
S['pg_reg2'] = NB('完善医生信息', True) + f'''<div class="body" style="padding:0">
  <div style="display:flex;gap:8px;padding:18px 16px">
    <div style="flex:1;text-align:center;opacity:.5"><div style="width:28px;height:28px;border-radius:50%;background:var(--line2);color:var(--t3);margin:0 auto;display:flex;align-items:center;justify-content:center;font-weight:700;font-size:13px">1</div><div style="font-size:11.5px;color:var(--t3);margin-top:6px">手机验证</div></div>
    <div style="flex:1;text-align:center"><div style="width:28px;height:28px;border-radius:50%;background:var(--gradTech);color:#fff;margin:0 auto;display:flex;align-items:center;justify-content:center;font-weight:700;font-size:13px">2</div><div style="font-size:11.5px;color:var(--cyanD);font-weight:600;margin-top:6px">医生信息</div></div>
    <div style="flex:1;text-align:center;opacity:.5"><div style="width:28px;height:28px;border-radius:50%;background:var(--line2);color:var(--t3);margin:0 auto;display:flex;align-items:center;justify-content:center;font-weight:700;font-size:13px">3</div><div style="font-size:11.5px;color:var(--t3);margin-top:6px">医院信息</div></div>
  </div>
  <div class="field">
    <div class="row"><label>姓名</label><input placeholder="请输入真实姓名" value="李慕白"></div>
    <div class="row"><label>职称</label><input placeholder="如 副主任医师" value="副主任医师"><span class="arrow">{ICON("arrow",16)}</span></div>
    <div class="row"><label>执业证号</label><input placeholder="医师资格证书编号" value="11032000012345"></div>
    <div class="row" style="align-items:flex-start;padding-top:12px"><label style="padding-top:2px">执业证</label>
      <div style="flex:1;display:flex;gap:8px;flex-wrap:wrap;padding:4px 0">
        <div style="width:54px;height:54px;border-radius:10px;background:var(--gradMain);display:flex;align-items:center;justify-content:center;color:#fff;font-size:11px;text-align:center;line-height:1.3">+<br>拍照</div>
        <div style="width:54px;height:54px;border-radius:10px;background:var(--line2);display:flex;align-items:center;justify-content:center;color:var(--t3);font-size:22px">+</div>
      </div></div>
    <div class="row"><label>所在医院</label><input placeholder="请输入医院全称" value="东莞市人民医院"></div>
    <div class="row"><label>所在科室</label><input placeholder="如 妇科" value="妇科"><span class="arrow">{ICON("arrow",16)}</span></div>
    <div class="row"><label>专业方向</label><input placeholder="如 宫腔镜" value="宫腔镜微创"></div>
  </div>
  <div style="margin:18px 16px"><div class="btn" data-go="nav:reg3">下一步</div></div>
</div>'''

# ---------- 注册 步骤3 ----------
S['pg_reg3'] = NB('医院信息', True) + f'''<div class="body" style="padding:0">
  <div style="display:flex;gap:8px;padding:18px 16px">
    <div style="flex:1;text-align:center;opacity:.5"><div style="width:28px;height:28px;border-radius:50%;background:var(--line2);color:var(--t3);margin:0 auto;display:flex;align-items:center;justify-content:center;font-weight:700;font-size:13px">1</div><div style="font-size:11.5px;color:var(--t3);margin-top:6px">手机验证</div></div>
    <div style="flex:1;text-align:center;opacity:.5"><div style="width:28px;height:28px;border-radius:50%;background:var(--line2);color:var(--t3);margin:0 auto;display:flex;align-items:center;justify-content:center;font-weight:700;font-size:13px">2</div><div style="font-size:11.5px;color:var(--t3);margin-top:6px">医生信息</div></div>
    <div style="flex:1;text-align:center"><div style="width:28px;height:28px;border-radius:50%;background:var(--gradTech);color:#fff;margin:0 auto;display:flex;align-items:center;justify-content:center;font-weight:700;font-size:13px">3</div><div style="font-size:11.5px;color:var(--cyanD);font-weight:600;margin-top:6px">医院信息</div></div>
  </div>
  <div class="field">
    <div class="row"><label>医院名称</label><input placeholder="自动带入可修改" value="东莞市人民医院"></div>
    <div class="row"><label>医院等级</label><input placeholder="如 三级甲等" value="三级甲等"><span class="arrow">{ICON("arrow",16)}</span></div>
    <div class="row"><label>医院地址</label><input placeholder="请输入详细地址" value="广东省东莞市万江区新谷涌万道路南3号"></div>
    <div class="row"><label>所在省市</label><input placeholder="省 / 市" value="广东省 / 东莞市"><span class="arrow">{ICON("arrow",16)}</span></div>
  </div>
  <div class="notice">{ICON("info",18)}提交后账号进入「待审核」状态，平台将在 1-2 个工作日内完成资质审核，审核通过后方可学习与报名。</div>
  <div style="margin:18px 16px"><div class="btn" data-go="nav:review">提交注册申请</div></div>
</div>'''

# ---------- 待审核提示页 ----------
S['pg_review'] = NB('提交成功', True) + f'''<div class="body" style="display:flex;flex-direction:column;align-items:center;justify-content:center;padding:0 30px;text-align:center">
  <div style="width:84px;height:84px;border-radius:50%;background:linear-gradient(135deg,#FFB547,#E0962A);display:flex;align-items:center;justify-content:center;color:#fff;box-shadow:0 12px 30px rgba(224,150,42,.35)">{ICON("clock",40)}</div>
  <div style="font-size:20px;font-weight:700;margin-top:20px;color:var(--t1)">资料审核中</div>
  <div style="font-size:13px;color:var(--t2);margin-top:10px;line-height:1.7">您的医生资质信息已提交，平台正在审核。<br>审核结果将通过<b style="color:var(--cyan2)">微信服务通知</b>告知您。<br>审核期间可先浏览平台公开资讯。</div>
  <div style="width:100%;margin-top:30px"><div class="btn" data-go="review-home" data-msg="">先去逛逛（游客预览）</div></div>
  <div style="width:100%;margin-top:12px"><div class="btn ghost" data-go="back">返回登录</div></div>
</div>'''

# ---------- 首页 ----------
S['pg_home'] = f'''<div class="navbar"><div style="display:flex;align-items:center;gap:8px"><img src="{LOGO_H}" style="height:20px"></div>
  <div class="act" style="gap:18px;color:var(--navy2);margin-left:auto">{ICON("search",21)}<span data-go="nav:msg">{ICON("bell",21)}</span></div></div>
<div class="body" style="padding:0">
  <div class="search" data-go="nav:course">{ICON("search",16)} 搜索课程、器械、专家</div>
  <div class="banner cover {img_cls(pick_img(COURSE_IMGS,'home_banner'))}"><div class="t">宫腔镜四级手术 高阶研修班</div><div class="d">10月18日 · 东莞 · 国家级继续教育学分</div><div class="b">立即报名 ›</div></div>
  <div class="live"><div class="hd"><div class="liveicon">{ICON("live",24)}</div><div class="nm">妇科微创直播课堂</div><div class="st"><span class="pulse"></span>直播中</div></div>
    <div class="vd"><div class="ti">能量器械安全使用规范（第3讲）</div><div class="su">主讲：王教授 · 宫腔镜培训中心</div></div>
    <div class="go" data-go="url">进入直播</div></div>
  <div class="entries">
    <div class="e" data-go="nav:course"><div class="ic">{ICON("book",22)}</div><div class="lb">课程学习</div><div class="sg">200+ 课程</div></div>
    <div class="e" data-go="nav:activity"><div class="ic">{ICON("cal",22)}</div><div class="lb">培训活动</div><div class="sg">线下+线上</div></div>
    <div class="e" data-go="nav:news"><div class="ic">{ICON("news",22)}</div><div class="lb">资讯中心</div><div class="sg">学术+器械</div></div>
    <div class="e" data-go="nav:about"><div class="ic">{ICON("info",22)}</div><div class="lb">平台介绍</div><div class="sg">了解我们</div></div>
  </div>
  <div class="sec-h"><div class="t">推荐课程</div><div class="more" data-go="nav:course">全部 ›</div></div>
  {COURSE_CARD(('子宫纵隔切开术 · 4K 完整演示','王建国 主任医师','北京协和医院','1280','宫腔镜'))}
  {COURSE_CARD(('KMS 电切镜系统标准操作','李慕白 副主任医师','东莞市人民医院','964','能量器械'))}
  <div class="sec-h"><div class="t">最新培训活动</div><div class="more" data-go="nav:activity">全部 ›</div></div>
  {ACT_CARD(('宫腔镜四级手术高阶研修班','10月18日 · 东莞','线下','86','报名中'))}
  {ACT_CARD(('妇科能量器械规范化培训班','11月02日 · 广州','线下','120','即将开始'))}
  <div class="sec-h"><div class="t">最新资讯</div><div class="more" data-go="nav:news">全部 ›</div></div>
  {NEWS_CARD(('2026 妇科微创诊疗新进展专家共识','学术资讯','09-20','1.2万'))}
  {NEWS_CARD(('宫腔镜设备日常维护与故障排查','器械知识','09-18','8652'))}
</div>''' + TABBAR('home')

# ---------- 课程中心 ----------
S['pg_course'] = NB('课程学习', False) + f'''<div class="body" style="padding:0">
  <div class="search" data-go="nav:course">{ICON("search",16)} 搜索课程、讲师、器械</div>
  <div class="tabs"><div class="t on">全部</div><div class="t">腹腔镜手术</div><div class="t">宫腔镜手术</div><div class="t">能量器械</div><div class="t">影像系统</div><div class="t">一次性耗材</div></div>
  {COURSE_CARD(('子宫纵隔切开术 · 4K 完整演示','王建国 主任医师','北京协和医院','1280','宫腔镜'))}
  {COURSE_CARD(('KMS 电切镜系统标准操作','李慕白 副主任医师','东莞市人民医院','964','能量器械'))}
  {COURSE_CARD(('腹腔镜下子宫肌瘤剔除术','张伟 主任医师','中山一院','2103','腹腔镜'))}
  {COURSE_CARD(('冷刀宫腔镜临床应用要点','陈敏 教授','四川大学华西','1577','宫腔镜'))}
  {COURSE_CARD(('超声刀能量平台原理与维护','刘强 副主任','广东省妇幼','842','影像系统'))}
</div>''' + TABBAR('course')

# ---------- 课程详情 ----------
S['pg_course_detail'] = NB('课程详情', True) + f'''<div class="body" style="padding:0">
  <div class="cv cover {img_cls(pick_img(COURSE_IMGS,'子宫纵隔切开术 · 4K 完整演示'))}"><div class="tag"><span class="badge b-cyan">宫腔镜</span></div><div class="tag2"><span class="badge b-live">{ICON("play",11)} 4K</span></div><div class="play">{ICON("play",22)}</div><div class="src">{ICON("eye",13)} 1280 人在学</div></div>
  <div class="card" style="margin:-14px 16px 0;position:relative;padding:16px">
    <div style="font-size:18px;font-weight:700">子宫纵隔切开术 · 4K 完整演示</div>
    <div style="display:flex;gap:10px;align-items:center;margin-top:10px;color:var(--t2);font-size:12.5px">{ICON("user",14)} 王建国 主任医师 · 北京协和医院</div>
    <div style="font-size:13px;color:var(--t2);line-height:1.7;margin-top:10px">系统讲解子宫纵隔的术前评估、TCRF 术式选择、能量器械参数设置与并发症预防，配套 4K 手术视频逐帧解析。</div>
  </div>
  <div class="tabs" style="margin-top:14px"><div class="t on">课程介绍</div><div class="t">学员评价</div></div>
  <div style="padding:14px 16px;color:var(--t2);font-size:13.5px;line-height:1.8">
    · 术前评估：超声 + 宫腔镜联合诊断要点<br>· 手术演示：单极电切环参数设定（60W 切割）<br>· 并发症：穿孔、水中毒的早期识别与处理<br>· 术后：雌激素预防再粘连方案
  </div>
  <div class="sec-h" style="margin-top:4px"><div class="t">相关课程</div></div>
  {COURSE_CARD(('冷刀宫腔镜临床应用要点','陈敏 教授','四川大学华西','1577','宫腔镜'))}
  {COURSE_CARD(('KMS 电切镜系统标准操作','李慕白 副主任医师','东莞市人民医院','964','能量器械'))}
</div>
<div class="tabbar" style="height:62px"><div data-fav="1" class="btn ghost sm" style="margin:0 10px 0 16px;flex:0 0 auto">{ICON("heart",16)} 收藏</div><div data-go="nav:msg" class="btn ghost sm" style="margin:0 10px 0 0;flex:0 0 auto">{ICON("share",16)} 分享</div><div class="btn" style="flex:1;margin:0 16px 0 0" data-go="review:nav:player" data-msg="">立即学习</div></div>'''

# ---------- 视频播放 ----------
S['pg_player'] = f'''  <div class="navbar"><button class="back" data-go="back">{ICON("back",24)}</button><div class="tt">子宫纵隔切开术</div><div class="more">{ICON("more",22)}</div></div>
  <div class="player-area"><div class="poster cover {img_cls(pick_img(COURSE_IMGS,'子宫纵隔切开术'))}"></div><div class="bigplay" data-go="toast" data-msg="播放/暂停（演示）">{ICON("play",28)}</div></div>
  <div class="player-ctrl">
    <div class="ti">子宫纵隔切开术 · 4K 完整演示</div>
    <div class="progress"><span class="tm">08:24</span><div class="bar" onclick="seekBar(this,event)"><i></i></div><span class="tm">24:50</span></div>
    <div class="tools">
      <div class="ic" data-go="toast" data-msg="已开启高清">{ICON("videocam",20)} 高清</div>
      <div class="ic" data-fav="1">{ICON("heart",20)} 收藏</div>
      <div class="ic" data-go="nav:msg">{ICON("share",20)} 分享</div>
      <div class="ic q" data-go="toast" data-msg="已切换全屏">⛶ 全屏</div>
    </div>
  </div>'''

# page wrapper metadata: extra classes / initial-show
PAGE_META = {
  'pg_splash': 'pg_splash show',
  'pg_player': 'player-screen',
  'pg_home': 'tab',
  'pg_course': 'tab',
  'pg_activity': 'tab',
  'pg_news': 'tab',
  'pg_profile': 'tab',
}

def wrap_page(o):
    meta = PAGE_META.get(o, '')
    cls = 'page ' + meta if meta else 'page'
    return f'<div id="{o}" class="{cls}">{S[o]}</div>'

# ---------- 培训活动 ----------
S['pg_activity'] = NB('培训活动', False) + f'''<div class="body" style="padding:0">
  <div class="tabs"><div class="t on">全部</div><div class="t">报名中</div><div class="t">未开始</div><div class="t">已结束</div></div>
  {ACT_CARD(('宫腔镜四级手术高阶研修班','10月18日 · 东莞','线下','86','报名中'))}
  {ACT_CARD(('妇科能量器械规范化培训班','11月02日 · 广州','线下','120','即将开始'))}
  {ACT_CARD(('单孔腹腔镜实操工作坊','09月05日 · 深圳','线下','60','已结束'))}
  {ACT_CARD(('KMS 新品发布会 · 线上直播','09月28日 · 线上','线上','310','报名中'))}
</div>''' + TABBAR('activity')

# ---------- 活动详情 ----------
S['pg_activity_detail'] = NB('活动详情', True) + f'''<div class="body" style="padding:0">
  <div class="cv cover {img_cls(pick_img(ACT_IMGS,'宫腔镜四级手术高阶研修班'))}"><div class="tag"><span class="badge b-live">报名中</span></div><div class="play">{ICON("cal",22)}</div><div class="src">{ICON("pin",13)} 东莞市人民医院 · 学术报告厅</div></div>
  <div class="card" style="margin:-14px 16px 0;position:relative;padding:16px">
    <div style="font-size:18px;font-weight:700">宫腔镜四级手术高阶研修班</div>
    <div style="display:flex;flex-wrap:wrap;gap:10px 18px;margin-top:10px;color:var(--t2);font-size:12.5px">
      {ICON("clock",14)} 2026-10-18 至 10-20<br>{ICON("pin",14)} 广东 · 东莞（线下）<br>{ICON("user",14)} 王建国 等 4 位专家<br>{ICON("badge",14)} 国家级继续教育学分</div>
    <div style="font-size:13px;color:var(--t2);line-height:1.7;margin-top:10px">面向妇科微创医师的进阶研修班，理论 + 动物实验 + 手术观摩三位一体，限额 100 人，报满即止。</div>
  </div>
  <div class="tabs" style="margin-top:14px"><div class="t on">活动介绍</div><div class="t">讲师团队</div><div class="t">报名须知</div></div>
  <div style="padding:14px 16px;color:var(--t2);font-size:13.5px;line-height:1.8">
    · 第一天：宫腔镜设备与能量平台原理<br>· 第二天：动物实验操作（分组带教）<br>· 第三天：手术直播观摩 + 病例讨论
  </div>
  <div class="sec-h" style="margin-top:4px"><div class="t">相关活动</div></div>
  {ACT_CARD(('妇科能量器械规范化培训班','11月02日 · 广州','线下','120','即将开始'))}
</div>
<div class="tabbar" style="height:62px"><div data-fav="1" class="btn ghost sm" style="margin:0 10px 0 16px;flex:0 0 auto">{ICON("heart",16)} 收藏</div><div data-go="nav:msg" class="btn ghost sm" style="margin:0 10px 0 0;flex:0 0 auto">{ICON("share",16)} 分享</div><div class="btn" style="flex:1;margin:0 16px 0 0" data-go="nav:signup" data-msg="">立即报名</div></div>'''

# ---------- 报名表单 ----------
S['pg_signup'] = NB('活动报名', True) + f'''<div class="body" style="padding:0">
  <div class="notice">{ICON("info",18)}本平台仅提供报名登记，不涉及线上付费。提交后由平台与您电话联系对接。</div>
  <div class="field">
    <div class="row"><label>姓名</label><input value="李慕白"></div>
    <div class="row"><label>手机号</label><input value="138 0013 8000"></div>
    <div class="row"><label>职称</label><input value="副主任医师"><span class="arrow">{ICON("arrow",16)}</span></div>
    <div class="row"><label>所在医院</label><input value="东莞市人民医院"></div>
    <div class="row"><label>科室</label><input value="妇科"><span class="arrow">{ICON("arrow",16)}</span></div>
    <div class="row" style="align-items:flex-start"><label style="padding-top:14px">备注</label><textarea placeholder="选填，最多200字（如特殊饮食、住宿需求）" rows="2"></textarea></div>
  </div>
  <div style="margin:20px 16px"><div class="btn" data-go="mask:m_success" data-msg="">确认报名</div></div>
</div>'''

ORDER = ['pg_splash','pg_login','pg_reg1','pg_reg2','pg_reg3','pg_review',
         'pg_home','pg_course','pg_course_detail','pg_player',
         'pg_activity','pg_activity_detail','pg_signup',
         'pg_news','pg_article','pg_about',
         'pg_profile','pg_profile_edit','pg_mylearn','pg_mysignup','pg_myfav',
         'pg_msg','pg_contact','pg_aboutus','pg_forgot']

# 公共 SVG 定义（图标 symbol）
DEFS = '<svg width="0" height="0" style="position:absolute"><defs>' + ''.join(
    f'<symbol id="{k}" viewBox="0 0 24 24">{v}</symbol>' for k,v in ICONS.items()) + '</defs></svg>'

def build():
    pages = '\n'.join(wrap_page(o) for o in ORDER)
    html = f"""<!DOCTYPE html><html lang="zh-CN"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>科迈森在线培训 · 小程序原型</title><style>{CSS}
{IMG_CSS}</style></head>
<body>{DEFS}
<div class="stage"><div class="cap">科迈森在线培训学习平台 · 微信小程序原型<span>品牌A 科技青环 · 页面可点击跳转 · 左下角页面导航</span></div>
<div class="phone">
  <div class="island"></div>
  <div class="screen">
    <div class="sysbar"><div class="sig"><span style="font-size:13px">9:41</span><span class="bars"><i></i><i></i><i></i><i></i></span><span style="font-size:11px">5G</span></div><div class="bat"><i></i></div></div>
    <div class="capsule"><span class="dot"></span><span class="omit"><i></i><i></i><i></i></span></div>
    {pages}
    <div class="mask" id="m_success"><div class="pop"><div class="pic">{ICON('check',32)}</div><div class="pt">报名提交成功</div><div class="pd">我们已收到您的报名信息，平台将在 1-2 个工作日内与您电话联系对接。<br>本平台不涉及线上付费。</div><div class="pbtn btn" data-go="success" style="margin:0">我知道了</div></div></div>
    <div class="mask" id="m_review"><div class="pop"><div class="pic" style="background:linear-gradient(135deg,#FFB547,#E0962A)">{ICON('lock',32)}</div><div class="pt">账号审核中</div><div class="pd">您的医生资质正在审核，审核通过后可观看课程视频与报名培训活动。<br>审核结果将通过微信服务通知告知。</div><div class="pbtn btn" data-go="closemask:m_review" style="margin:0">我知道了</div></div></div>
    <div class="toast" id="toast"></div>
  </div>
</div></div>
<script>{JS}</script>
</body></html>"""
    out = os.path.join(ROOT, 'weapp.html')
    with open(out, 'w', encoding='utf-8') as f:
        f.write(html)
    print('OK ->', out, len(html), 'bytes,', len(ORDER), 'screens')

if __name__ == '__main__':
    build()
