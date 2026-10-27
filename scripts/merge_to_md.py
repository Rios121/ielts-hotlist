#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""合并 summaries/batch_XX.md 成最终 markdown，目录做成可点击跳转的锚点链接。

锚点规则：<a id="p{part}-{rank}"></a> 放在每篇标题前，目录里 [标题](#p{part}-{rank}) 跳转。
"""
import argparse, json, os, re, datetime

PART_OF_SLOT = {'Part 1': 1, 'Part 2': 2, 'Part 3': 3}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--workdir", default=".", help="工作目录（含 reading_data.json 与 summaries/）")
    args = ap.parse_args()
    wd = args.workdir
    data = json.load(open(os.path.join(wd, "reading_data.json"), encoding="utf-8"))
    sum_dir = os.path.join(wd, "summaries")

    today = datetime.date.today().strftime("%Y-%m-%d")
    out_path = os.path.join(wd, f"阅读7天热榜_备考速查_{today}.md")

    # 头部 + 超链接目录
    header = []
    header.append("# 雅思阅读 · 7 天热榜备考速查")
    header.append("")
    header.append(f"> 数据来源：雅思机考平台「一周高频榜单」阅读榜 · 生成日期 {today}")
    header.append("> 覆盖 Part 1 / Part 2 / Part 3 各 20 篇（共 60 篇），目录点击可跳转。")
    header.append("> 用法：刷题前看「主题」预判话题；做完题用「答案速查」核对；「考点词」积累同义替换（雅思阅读核心考点）。")
    header.append("")
    header.append("## 目录")
    header.append("")
    for slot in ['Part 1', 'Part 2', 'Part 3']:
        pn = PART_OF_SLOT[slot]
        header.append(f"### {slot}")
        recs = [r for r in data['records'] if r['slot'] == slot and not r.get('_failed')]
        for r in recs:
            rank = r['rank']
            zh = r.get('titleZh') or ''
            anchor = f"p{pn}-{rank}"
            label = f"P{pn} #{rank} {r['title']}" + (f"（{zh}）" if zh else "")
            header.append(f"- [{label}](#{anchor})")
        header.append("")
    header.append("---")
    header.append("")

    # 拼接正文（每篇标题前插锚点）
    title_re = re.compile(r'^###\s+\[P(\d)\s+#(\d+)\]')

    def insert_anchors(text):
        out_lines = []
        for line in text.splitlines():
            m = title_re.match(line.strip())
            if m:
                pn, rank = int(m.group(1)), int(m.group(2))
                out_lines.append(f'<a id="p{pn}-{rank}"></a>')
            out_lines.append(line)
        return "\n".join(out_lines)

    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(header))
        for slot, (a, b) in zip(['Part 1', 'Part 2', 'Part 3'],
                                [('01', '02'), ('03', '04'), ('05', '06')]):
            f.write(f"# {slot}\n\n")
            for bn in (a, b):
                fn = os.path.join(sum_dir, f"batch_{bn}.md")
                if not os.path.exists(fn):
                    print(f"[merge] 缺少 {fn}，跳过")
                    continue
                text = open(fn, encoding="utf-8").read().rstrip()
                f.write(insert_anchors(text) + "\n\n")

    print(f"[merge] 已生成 {out_path} ({os.path.getsize(out_path) // 1024} KB)")


if __name__ == "__main__":
    main()
