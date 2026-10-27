#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把 reading_data.json 转成 LLM 总结的中间输入：WD/input/batch_01..06.md（每批 10 篇）。"""
import argparse, json, os, re


def split_paras(t):
    t = re.sub(r'\(([A-I])\)', r'\1', t)
    pattern = re.compile(r'(?:^|(?<=[.!?]))\s*([A-I])\s+(?=[A-Z])')
    matches = list(pattern.finditer(t))
    paras = []
    for idx, m in enumerate(matches):
        end = matches[idx + 1].start() if idx + 1 < len(matches) else len(t)
        paras.append((m.group(1), t[m.end():end].strip()))
    return paras


def trim(s, n=400):
    s = (s or '').strip()
    return s if len(s) <= n else s[:n] + ' …'


TYPE_LABEL = {
    'fill-in-the-blank': '填空',
    'single-choice': '单选/判断',
    'multiple-choice': '多选',
    'matching': '匹配',
    'map': '段落/图标注',
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--workdir", default=".", help="工作目录（含 reading_data.json）")
    args = ap.parse_args()
    wd = args.workdir
    data_path = os.path.join(wd, "reading_data.json")
    d = json.load(open(data_path, encoding="utf-8"))
    out_dir = os.path.join(wd, "input")
    os.makedirs(out_dir, exist_ok=True)

    batches = []
    for slot in ['Part 1', 'Part 2', 'Part 3']:
        recs = [r for r in d['records'] if r['slot'] == slot and not r.get('_failed')]
        for i in range(0, len(recs), 10):
            batches.append((slot, recs[i:i + 10]))

    for bi, (slot, chunk) in enumerate(batches, 1):
        lines = []
        for r in chunk:
            lines.append('\n\n' + '=' * 60)
            lines.append(f"【{slot} #{r['rank']}】 {r['title']}"
                         + (f"（{r['titleZh']}）" if r.get('titleZh') else ''))
            if r.get('subtitle'):
                lines.append('副标题: ' + trim(r['subtitle'], 200))
            paras = split_paras(r['article'])
            if len(paras) < 3:
                paras = [('?', r['article'])]
            lines.append(f'--- 正文（{len(paras)} 段）---')
            for letter, content in paras:
                lines.append(f'[{letter}] {trim(content, 600)}')
            lines.append('--- 题目与解析 ---')
            for q in r['questions']:
                lines.append('')
                tlabel = TYPE_LABEL.get(q['type'], q['type'])
                lines.append(f"Q{q['qNumber']} [{tlabel}] "
                             + trim(q['question'] or q.get('groupDesc') or '', 150))
                if q.get('options'):
                    lines.append('  选项: ' + ' | '.join(
                        f"{o['num']}. {trim(o['text'], 40)}" for o in q['options']))
                for a in q['analyses']:
                    lab = a['label'] or '解析'
                    lines.append(f'  [{lab}] {trim(a["content"], 400)}')
        fn = os.path.join(out_dir, f'batch_{bi:02d}.md')
        with open(fn, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
        print(f'{slot} -> {fn} ({os.path.getsize(fn) // 1024} KB)')


if __name__ == "__main__":
    main()
