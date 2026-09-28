# 科迈森在线培训学习平台 · 微信小程序原型

A high-fidelity WeChat Mini Program UI prototype for **科迈森 (KMS Medical)** online training platform, built as a single-file HTML deliverable.

品牌规范：**A 方案 · 科技青环**（深海军蓝 `#061B3A` + 科技青 `#00C9FF → #0066FF`）
参考需求：科迈森在线培训学习平台 方案梳理 0928.docx

## 直接打开

直接用浏览器打开 `weapp.html` 即可：

- **电脑端**：显示 390×844 手机外壳 + 全部 25 个页面，可逐屏交互
- **手机端**：自动铺满屏幕，隐藏外壳（响应式断点 480px）

## 包含页面（25 屏）

启动页 / 登录 / 注册 / 忘记密码 / 首页 / 课程中心 / 课程详情 / 播放页 / 培训活动 / 活动详情 / 活动报名 / 资讯 / 资讯详情 / 个人中心 / 我的课程 / 证书 / 收藏 / 消息 / 平台介绍 / 任务中心 / 等等…

## 重新构建

```bash
python3 build_weapp.py     # 重新生成 weapp.html
```

构建脚本会从 `assets/` 读取 18 张真实图（从 sudh.net 内容接口抓取），把它们编码成 base64 内联进 HTML，输出一个完全自包含的单文件。

## 资源素材

`assets/` 目录下：

- `course-1..6.jpg` — 课程卡片缩略图（6 张真实手术/讲座帧）
- `act-1..6.jpg` — 培训活动海报（6 张 4:3 真实海报）
- `news-1..6.jpg` — 资讯栏目封面（6 张真实幻灯/学术截图）

如需替换素材，直接覆盖同名文件，重新跑 `build_weapp.py` 即可。

## 技术栈

- 单文件 HTML + 内联 `<style>` / `<script>`
- 无任何外部依赖
- 所有图片 base64 内联 → 离线可用、无 CDN 依赖
- Playwright 验证：响应式外壳、真实封面渲染、24 条主流程（推送开关 0 报错）

## 文件清单

| 文件 | 说明 |
|---|---|
| `weapp.html` | 主交付物（单文件，约 1.2 MB） |
| `build_weapp.py` | 构建脚本（Python 3 + Pillow） |
| `assets/` | 原始图片素材（18 张 JPEG） |