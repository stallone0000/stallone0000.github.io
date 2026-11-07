# Qilong Shi · Personal academic website

Live website: **https://stallone0000.github.io/**

The site has a concise homepage and a single [Full CV](https://stallone0000.github.io/cv.html) with education, teaching, honors, academic service, and publications. The design follows [Yinda Zhang's homepage](https://yindazhang.github.io/): fixed dark navigation, Arial typography, a white page and restrained blue links. HTML/CSS is independently implemented without Bootstrap or jQuery.

## 编辑与生成

- `data/profile.json`：本人选择公开的简介、教育、教学、荣誉、服务与 Highlights；`bio_links` 配置简介中的导师及合作老师主页链接，荣誉条目的可选 `url` 与 `note` 配置公告链接和简短备注。
- `data/publications.json`：论文题名、作者顺序、共同一作标记、venue、来源记录、站内 `pdf` 路径与补充资源。
- `data/presentation.json`：首页研究主题与论文简称；首页论文链接跳到 `cv.html#论文ID`。
- `data/visitors.json`：RevolverMaps2 地球开关、本站公开 site key、尺寸、主题与标记颜色。
- `assets/papers/`：可直接打开的论文 PDF，命名为 `年份-venue-论文ID.pdf`。
- `docs/papers.json`：每份 PDF 的来源、页数、字节数与 SHA256；作者提供文件不记录私人本地路径。
- `templates/base.html`、`assets/style.css`、`scripts/build.py`：模板、样式与 Python 标准库生成器。

```sh
python3 scripts/build.py
python3 -m http.server 8765
```

生成 `index.html`、`cv.html`、`404.html`，以及旧 `publications.html` 的兼容跳转页。将源文件、PDF 与生成页面一起提交并推送到 `main`，GitHub Pages 发布仓库根目录。无需 Node.js、数据库或运行时服务。

## 页面与链接规则

- 导航只有 Home 和 Full CV；旧 Publications 地址会保留查询参数和论文锚点，跳转至同一份完整简历。
- 首页每个论文链接进入 Full CV 的对应论文位置；Full CV 的蓝色论文题名直接打开站内 PDF。没有 PDF 的题名保持普通文字，不链接到其他文章或错误版本。
- 首页按研究领域与 venue 分为 LLMs、AI-based Measurement（SIGMETRICS）、Data Mining（ICDE、KDD、TKDE）、Network Measurement（ToN、WWW）；Data Mining 同时展示 PSSketch。首页是手动维护的研究主题概览，Full CV 的 Selected／More 则保留作者身份筛选规则。
- 论文下方只显示可用的 `[Code]`、`[Demo]`、`[Model]` 等补充资源，不再显示 `[Paper]`、`[PDF]`。
- Full CV 保留 `Publications & Preprints`、Highlights、Selected Publications、More Publications。Selected 分为 LLMs 与 Network Measurement，每组按年份倒序；其余论文在 More 中按年份倒序。
- 一作／共同一作且 `classifications` 含 CCF-A 或 THU-A 的论文自动精选；SCF 按本人明确要求以 `selected_override` 纳入，当前 11 Selected / 9 More。该例外不改变作者身份。
- `*` 表示 equal contribution，署名第一也保留星号。TKDE 2026 前两位、NeuFSD 前三位为共一；本人姓名加粗并加下划线。
- venue 格式统一为 `ACL'26`、`TKDE'26`、`SIGMETRICS'27`；Oral、Main Conference、Accepted 保留在数据中，不在列表显示。

## 内容依据

论文元数据依据本人确认及原论文；正式论文、录用状态和预印本分别记录。SCF 的新作者顺序由本人确认，并与作者提供的最新版相符；NeuFSD 的 SIGMETRICS 2027 录用信息由本人确认。新上传的两份原稿保持字节不变，仅统一文件名。

Full CV 的荣誉仅显示本人选择的国奖、Siebel 和华为奖学金，其他已确认奖项保留在源数据中。研究合作、模型链接与论文署名按原记录保留。网站只维护本人选择公开的资料，不上传私人简历文件。

照片来自本人指定的 `IMG_5491.JPG`，显示在 Full CV，CSS 在固定画框内按 125% 放大人物。中文姓名保持括号、常规字重与较小字号。

## 访客地球

地球位于首页右上方，桌面端在简介文字右边界与页面右边缘之间居中，两侧留白相等；地球独立定位，不撑高简介。联系方式紧接分割线，小屏时地球位于简介和联系方式之间。使用本人提供的 [RevolverMaps2](https://revolvermaps2.com/) 嵌入代码：240px、blue 主题、`ffb23f` 橙色标记。小屏自动缩放，打印时隐藏。官方脚本异步加载，自动插入独立的延迟加载 iframe，不阻塞正文和导航。

在 `data/visitors.json` 中设置 `enabled`，或更换 `site_key`、尺寸、主题与颜色，运行生成器后部署。site key 是公开的嵌入标识；账号密码、登录 cookie 和邮箱验证链接不写入仓库。

启用后从接入时开始统计首页访问；计数和地点数据由 RevolverMaps2 提供，本站不生成模拟访客。完整简历直达访问不另装计数器。脚本依据供应商 [embed.js](https://revolvermaps2.com/embed.js)，部署时核对球体、统计接口和真实记录。

插件在小于等于260px时隐藏自身累计计数，因此 `assets/visitors.js` 在地球下方补充 `Total visitors`，读取同一站点公开 `api/feed.php` 的 `total` 字段；不把 `live` 或 `views` 当作累计访客数，也不额外发送统计 hit。可见页面每30秒刷新，切回页面时刷新；加载失败保留上一次真实值，首次未加载时显示破折号。

## 备份与恢复

- 私有备选档案库：**https://github.com/stallone0000/academic-website-templates**，保存七种参考风格；Tianxing Chen 为未来内容更丰富时的优先备选。
- 改版前的完整备份：[2026-09-30 旧版](https://github.com/stallone0000/stallone0000.github.io/releases/tag/ben-style-2026-09-30)。恢复说明见 [docs/RESTORE.md](docs/RESTORE.md)。
- 恢复旧风格时须保留现行公开资料范围和最新论文数据，避免用过时履历覆盖当前版本。

素材与论文图来源见 [docs/ASSETS.md](docs/ASSETS.md)。正文使用系统 Arial/Helvetica，旧 Lato 字体及许可保留在 `assets/fonts/`。导航栏和浏览器标签页使用同一份 [OpenMoji](https://openmoji.org/) 龙图标（U+1F409），采用 [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/) 许可，导航图标为42px，并向下偏移2px。首页姓名、清华校标、北大校标为三个独立元素，桌面端等间距排列，整组约占简介文字列的2/3宽；较窄桌面保留至少16px间隔，平板和手机使用整列宽度。校标等高48px，窄屏为36px，必要时姓名单独一行、两校标分列左右。启用访客地球时会请求 RevolverMaps2 及其脚本依赖。
