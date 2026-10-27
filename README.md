# ielts-hotlist

一个 Claude Code skill：把**实时更新的七天热榜阅读题库**，自动整理成雅思阅读备考速查笔记。

## 能做什么

- **主题 + 逐段大意**：一篇文章读成「一句话主题 + 每段一句中文」，快速回忆讲了啥
- **考点词 + 同义替换**：提炼高频考点词，标出原文↔题目的同义替换（雅思阅读核心考点）
- **复盘速查表**：每道题考什么、定位在哪，一眼看清，对答案不用翻原文
- **可点击目录 + 导出 Word**：目录点击跳转，一键导出 Word 方便打印

## 一键安装

**Windows（PowerShell）**：

```powershell
New-Item -ItemType Directory -Force "$env:USERPROFILE\.claude\skills" | Out-Null
git clone https://github.com/Rios121/ielts-hotlist.git "$env:USERPROFILE\.claude\skills\ielts-hotlist"
```

**macOS / Linux**：

```bash
mkdir -p ~/.claude/skills
git clone https://github.com/Rios121/ielts-hotlist.git ~/.claude/skills/ielts-hotlist
```

装好后在 Claude Code 里运行 `/reload-skills`（或重启会话）。

## 使用

输入 `/ielts-hotlist`，或直接说「抓一下雅思阅读热榜」，Claude 会自动抓取最新七天热榜、整理成文档。

依赖：Python 3（转 Word 需 `pip install python-docx`）+ 联网 + Claude Code。

## 免责声明

本工具只提供代码与文档，**不含任何第三方版权内容**。数据由使用者从自己已获授权的平台即时获取，仅供个人学习。使用者需自行确认符合所在地法律及数据源的服务条款，责任自负。MIT 许可证仅覆盖本仓库代码与文档。
