# 旧版恢复

## 已验证的完整旧版

- **风格**：Ben Mildenhall / Jon Barron，含生活照、四个 Highlights、带图论文列表。
- **保存日期**：2026-09-30，Yinda 风格改版前的实际线上版本。
- **标签**：`ben-style-2026-09-30`
- **提交**：`db0a223e03480421c5357d5a46228872acc24a0d`
- **[GitHub 备份与 ZIP 下载](https://github.com/stallone0000/stallone0000.github.io/releases/tag/ben-style-2026-09-30)**
- **[备用分支](https://github.com/stallone0000/stallone0000.github.io/tree/archive/ben-style-2026-09-30)**

完整包含源代码、生成页面、19 篇论文数据、本人照片、论文图、小丑图标和许可证。GitHub 上的 ZIP 已与本地该提交的所有跟踪文件逐字节核对。无需在电脑另存一份副本。早期 `v1-ben-style` 比本备份旧，不要误用。

## 快速恢复并上线

在此仓库 `main` 分支、无未提交改动且与 GitHub 同步时运行：

```sh
python3 scripts/restore_site.py --apply --push
```

脚本先把恢复前版本另存为 GitHub 标签，再恢复旧版全部文件，核对 Git tree 完全一致，创建新的恢复提交并推送，随后 GitHub Pages 自动部署。不使用 force push，不改写历史。只查看计划可省略 `--apply --push`。

这是**完整快照恢复**，也会还原到保存时的论文和个人信息。若将来只想换回旧布局并保留新增论文，应先保留当前 `data/` 和新增资产，再把旧版 `templates/base.html`、`assets/style.css`、`scripts/build.py` 移植回来并重新生成；不要直接做完整快照恢复。

## 不依赖恢复脚本的备用方法

若当前版本已不含上述脚本，在干净且已同步的 `main` 上执行下面的操作。先用一个新的唯一标签保存当前版本并推送，再执行恢复：

```sh
git fetch origin --tags
git tag -a before-restore-YYYYMMDD-HHMMSS -m 'Save current site before restoration'
git push origin refs/tags/before-restore-YYYYMMDD-HHMMSS
git restore --source=ben-style-2026-09-30 --staged --worktree -- .
git commit -m 'Restore Ben-style website from 2026-09-30 backup'
git push origin main
```

恢复后应检查 GitHub Pages 最新构建成功，并确认线上 HTML 与恢复提交一致。

2026-10-01 已在隔离的临时仓库完成实际恢复演练：自动备份新版本、生成并推送恢复提交、核对旧版 Git tree 完全相同，并重新构建旧版且无文件差异。临时仓库已清理。
