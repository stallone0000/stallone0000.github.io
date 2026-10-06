# Qilong Shi · Personal academic website

Live website: **https://stallone0000.github.io/**

English academic homepage, full publications page and printable CV. The current design follows [Yinda Zhang's homepage](https://yindazhang.github.io/): a fixed dark navigation bar, Arial typography, a wide white page, restrained blue links and research-topic publication lists. The HTML/CSS is independently implemented; it does not copy personal content or load Bootstrap/jQuery.

**改版前完整备份：[2026-09-30 旧版](https://github.com/stallone0000/stallone0000.github.io/releases/tag/ben-style-2026-09-30)。快速恢复方法见 [docs/RESTORE.md](docs/RESTORE.md)。**

## 编辑内容

- `data/profile.json`：简介、联系方式、教育、实习、教学、奖项、服务和精选项目。
- `data/publications.json`：完整论文列表、作者顺序、共同一作、正式链接和缩略图。
- `data/presentation.json`：新风格首页的研究主题短句和论文简称。
- `assets/images/`：经过压缩的本人照片与本人论文图；图源全部保留，当前文字风格首页不加载论文图。
- `templates/base.html`、`assets/style.css`：公共页面结构和样式。
- `scripts/build.py`：仅依赖 Python 3 标准库，生成可直接发布的 HTML。

更新数据后运行：

```sh
python3 scripts/build.py
python3 -m http.server 8765
```

打开 http://localhost:8765 。将修改后的数据与生成的页面一起 commit / push 到 `main`，GitHub Pages 自动发布仓库根目录。无需 Node.js、API 密钥、数据库或运行时服务。

## 更换模板

私人备选档案库：**https://github.com/stallone0000/academic-website-templates**

其中保存 Keunhong Park、Yuki Asano、Matthew Tancik、Ben Mildenhall、Saining Xie、Maithra Raghu 和 Tianxing Chen 的参考快照、来源与许可说明。Tianxing 是未来经历更丰富时的优先备选。

更换时保留 `data/`、本人照片和论文素材，按目标布局改造模板层，再生成网站。各参考站框架不同，档案不是一键主题切换器；没有明确复用许可的源码仅作私有参考，独立实现对应布局。开始换版前先为当前版本打 tag，便于恢复。

## 数据口径

资料整理于 2026-09-24。教育、服务和已列论文依据个人简历及公开论文记录；360 实习起止为本人确认的 2025.08–2026.08。AI 相关研究与该实习关联，但不改写各论文的正式署名。

- 论文链接指向 DOI、ACL Anthology 或 arXiv 原记录。
- `*` 标注原文确认的 equal contribution；本人姓名加粗并加下划线。
- Selected Publications 根据一作／共同一作身份及 `classifications` 中的 CCF-A 或 THU-A 自动生成并统计篇数，包含已发表及已录用论文；分为 Network Measurement 与 LLMs，每类按年份倒序。完整论文页仍按此规则分为 10 篇 Selected 和 9 篇 More。首页是独立的主题精选：原 10 篇加本人指定的 SCF（NeurIPS 2026）和 Edge-Optimized Voice Control（BigData 2025），共 12 篇，分为 LLMs 与 Network Measurement；Network Measurement 聚合为 Learning-based measurement、Flow dynamics and persistence、Frequency, heavy hitters, and quantiles 三条，每条内部按年份倒序。Highlights 在 Publications 页保留。More Publications 和 CV 均按年份倒序。
- 论文 venue 显示统一为简称加两位年份，如 `SIGMETRICS'27`、`NeurIPS'26`、`TKDE'26`、`ToN'23`。首页、Highlights、完整论文列表和网页 CV 共用格式；Oral、Main Conference、Accepted 保留在源数据中，但不在页面显示。
- 预印本的 venue 简写为 arXiv。ScienceArena 数据记录为 EMNLP 2026 Main Conference，前三位作者共一，依据本人确认与 arXiv 页面／论文脚注。TRS 数据记录为 ACL 2026 (Oral)，保留原始 Anthology 链接。
- Beyond Parameter Arithmetic 的 NeurIPS 2026 录用由本人于2026-09-25确认，数据记录为 NeurIPS 2026 Accepted，页面显示为 `NeurIPS'26`；保留 arXiv 论文链接。根据现有作者顺序，本人非一作/共一，仍列入 More Publications。
- NeuFSD 的最终九人作者名单及 ACM SIGMETRICS 2027 录用信息由本人提供的 Scholar 条目确认，按 THU-A 归入 Selected；未添加尚无可靠链接的 DOI 或公开 PDF。
- 奖项仅列可确认名称，未使用存在口径差异的排名描述。
- 2026 年清华大学国家奖学金及全校 Top 1% 由本人于 2026-10-06 确认，列在网页 CV 的 Selected Honors 首位。
- 本人确认入选2026年IETF菁才计划，按“Selected Participant”列入荣誉。个人验收报告明确身份为“IETF 125 New Participants 资助计划参与者”，报名材料明确时间为2026年3月，故附注 New Participants。项目全称与资助性质见[中国互联网协会官方通知](https://www.isc.org.cn/article/27269689823457280.html)，本人姓名与清华单位可见[IETF 125官方参会记录](https://datatracker.ietf.org/doc/bluesheets-125-newparticipant-202603150130/00/)。Elite Talent Program 为英文表述，保留菁才计划中文名以便对应；未公开原始个人材料。
- BitMatcher获2024年广东省计算机学会优秀论文一等奖，本人已确认；荣誉列表和论文备注均有标注。组织英文名采用[学会官网](https://www.gdcomf.com/gyxh/xhjj)的 Computer Academy of Guangdong，论文奖另有[共同作者公开资料](https://www.wenjunli.com/newstudent/ForNewStudent.pdf)支持。
- `cv.html` 是根据当前数据生成的公开版 CV；不上传原始私人简历文件。
- 照片使用本人指定的 `IMG_5491.JPG`，进行尺寸/编码优化并移除元数据；当前放在 CV 页，CSS 在固定画框内按 125% 放大人物。
- 新版桌面 Arial 简介、联系方式、论文列表与论文附注统一 17.85px，分节标题 24px，姓名 30px；容器 750/970/1170px，导航高 50px，对应 Yinda 参考页。中文姓名保留括号、常规字重并缩为 22px。移动端正文保留 16px 以方便阅读。
- 主页仅含简介、联系方式和主题精选论文，底部以分隔线结束；教育、实习、教学、荣誉、审稿服务保留在 CV，审稿只公开 venue、年份及角色。

素材来源见 [docs/ASSETS.md](docs/ASSETS.md)。网站没有第三方统计脚本、Cookie 横幅或外部字体请求。当前使用系统 Arial/Helvetica 字体；旧版 Lato 字体与许可仍保留在 `assets/fonts/`。

标签页小丑图标由 [OpenMoji](https://openmoji.org/) 设计，采用 [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/) 许可，图形未经修改。
