---
name: ielts-hotlist
description: Fetch an IELTS reading hot-list (Part 1/2/3, 20 passages each) from an IELTS computer-based test platform's API and generate a study-reference doc (Markdown + Word) with per-passage theme, paragraph summaries, key vocabulary, and per-question answers (with short Chinese stems for choice/判断题). Use when the user asks to 抓取/整理/生成 雅思阅读热榜、阅读备考速查、阅读真题答案、热榜文档、备考材料 等.
---

# 雅思阅读热榜备考速查生成器

从一个雅思机考平台的阅读热榜（Part 1 / Part 2 / Part 3 各 20 篇，共 60 篇）生成一份备考速查文档：每篇含**主题 / 段落大意 / 考点词（同义替换 + 高频生词）/ 逐题答案速查**，选择题与判断题附简短中文题干。

## 版权与合规（重要，先读）

- 本 skill **只提供「方法 + 工具」**，仓库内**不含任何第三方版权内容**——真题文章、题目、答案、解析等一概不打包、不分发、不内置。
- 数据由**使用者本人**，从**自己安装、并已合法获得使用授权**的 App 中即时获取，仅供个人学习之用。
- 使用者应自行确认其使用方式符合**所在地法律**及**数据源提供方的服务条款（Terms of Service）与版权规定**。未经授权抓取、复制或再分发第三方内容可能构成侵权，责任由使用者自负。
- 本工具作者仅提供代码与文档，对使用者如何使用、以及由此产生的任何后果**不承担责任**。
- MIT 许可证仅适用于本仓库的代码与文档，**不延伸至任何第三方内容**。

## 兼容性（安装位置无关）

数据走的是该平台的后端 API，**与 App 装在哪个盘、哪个目录无关**。唯一需要「探测本地」的情况是：若 API 加了鉴权（返回 401/403），脚本会自动降级，扫描 `%APPDATA%` 下所有 Electron 应用的 `Local Storage` 提取 `token` 重试——自动兼容不同的 App 目录名，无需手动配置。

## 工作流（按顺序执行）

设工作目录 `WD`（默认当前目录，脚本会自动建 `WD/input`、`WD/summaries` 等子目录）。

1. **抓取**：`python ${CLAUDE_SKILL_DIR}/scripts/fetch_hotlist.py --workdir WD`
   产出 `WD/reading_data.json`（60 篇正文 + 题目 + 答案解析）。默认使用内置数据源，无需配置。

2. **生成总结中间输入**：`python ${CLAUDE_SKILL_DIR}/scripts/build_input.py --workdir WD`
   产出 `WD/input/batch_01.md` ~ `batch_06.md`（每批 10 篇）。

3. **LLM 总结**（核心，由 Claude 完成）：派 6 个子代理，每个读一个 `batch_XX.md`，按下方「Agent 总结 prompt 模板」生成总结；把每个子代理返回的 markdown 原样写入 `WD/summaries/batch_XX.md`（文件名与输入对应）。

4. **合并**：`python ${CLAUDE_SKILL_DIR}/scripts/merge_to_md.py --workdir WD`
   产出最终 `WD/阅读7天热榜_备考速查_<当天日期>.md`（含**可点击跳转的超链接目录**）。

5. **（可选）转 Word**：`python ${CLAUDE_SKILL_DIR}/scripts/md2docx.py --md <md文件> --out <docx文件>`

## Agent 总结 prompt 模板

第 3 步对每个批次（`batch_XX.md`，对应 Part N 的某 10 篇）派一个子代理，prompt 如下（把 `<文件绝对路径>`、`<Part 号>`、`<排名范围>` 替换为实际值）：

> 读文件 `<文件绝对路径>`（UTF-8）。里面有 10 篇雅思阅读真题（Part `<Part 号>`，排名 `<排名范围>`），每篇含：英文正文（按 [A][B][C]… 分段）、题目（题干+选项）和中文答案解析（解析含"题目理解 + 定位 + 答案"，以及英文定位原文）。
>
> 为每篇生成一份备考总结。**硬要求：① 考点词/生词要丰富（每篇约 10 个）；② 选择题和判断题必须在答案速查里给出简短中文题干。**
>
> 对每一篇严格按下面格式输出（markdown）：
>
> ### [P`<Part 号>` #N] 英文标题（中文标题）
> **主题**：一句话说明文章讲什么
> **题型**：填空 x · 单选/判断 x · 多选 x · 匹配 x · 段落定位 x（只列不为 0 的项）
> **段落大意**：A→…；B→…；C→…（每段一句中文概括，段落多时可合并相近段）
> **考点词**：
> - 同义替换：A↔B · C↔D · E↔F · …（6-7 组，原文词↔题目同义表达）
> - 高频生词：word（中文释义）· word（中文释义）· …（5-6 个正文重要学术词/低频词，附简短中文释义）
> **答案速查**：
> | 题号 | 题型 | 答案 | 题干/考点 |
> | --- | --- | --- | --- |
>
> 答案速查逐题规则（务必遵守）：
> - **判断题**（选项是 TRUE/FALSE/NOT GIVEN 或 YES/NO/NOT GIVEN）：答案填 TRUE/FALSE/NOT GIVEN（或 YES/NO/NOT GIVEN），"题干/考点"列写**简短中文题干**（忠实翻译题目那句话）。
> - **单选题**（选项是 A/B/C/D 具体内容）："题干/考点"列写**简短中文题干**，答案填 A/B/C。
> - **多选题**："题干/考点"列写**简短中文题干**，答案填多个字母如「A C E」。
> - **填空题**：答案填答案词，"题干/考点"写定位/同义替换。
> - **匹配题**：答案写配对（如 1→A (France)），"题干/考点"写配对依据。
> - **段落/图标注**：答案填段落字母，"题干/考点"写题目大意。
> - 中文题干务必简短（一句话）、忠实原意、不扩写；答案一律从「解析」提取，解析未明确的写「（未明确）」不要猜。
>
> 输出就是这 10 篇的完整 markdown，从第 1 篇到第 10 篇，不要遗漏任何一篇、任何一题。不要写任何额外说明，直接输出 markdown。

批次与 Part/排名对应：batch_01=Part1 #1-10，batch_02=Part1 #11-20，batch_03=Part2 #1-10，batch_04=Part2 #11-20，batch_05=Part3 #1-10，batch_06=Part3 #11-20。

## 脚本

- `scripts/fetch_hotlist.py` — 抓取热榜 + 正文 + 答案（`--base` 可选，含 token 降级探测）
- `scripts/build_input.py` — 生成 LLM 总结的中间输入（batch 文件）
- `scripts/merge_to_md.py` — 合并 batch 成最终 markdown（含超链接目录）
- `scripts/md2docx.py` — markdown → Word（含答案速查表格）

## 备注

- 判断/单选/多选的"中文题干"是子代理对英文题干的忠实翻译；答案仍取自官方解析，不改动。
- 若某篇正文缺段（部分文章段落不全），子代理会依据解析里引用的原文段还原段落大意与答案，属正常。
- 所有脚本幂等、无副作用，可重复运行覆盖旧文件。
