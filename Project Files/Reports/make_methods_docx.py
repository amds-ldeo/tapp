#!/usr/bin/env python3
"""
Convert the methods-section Markdown into Word documents, for readers who don't use
Markdown. Two outputs from one parser:
  * ..._highlighted.docx — every <mark> span carries Word's native yellow highlight;
  * ....docx             — the same text with no highlighting, ready to paste into a paper.
The source is always the highlighted Markdown (itself generated from the clean file), so
all three stay in sync: edit the clean .md, run make_highlighted_methods.py, then this.
Handles only the constructs these files use: #/##/### headings, paragraphs, one
blockquote, one pipe table, "- " list items, --- rules, and inline **bold**, *italic*,
\\* escapes and <mark>.
"""
import os, re
from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_COLOR_INDEX
from docx.enum.section import WD_ORIENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, 'EPMA_Reference_Methods_Section_v77_highlighted.md')
OUTS = {True:  os.path.join(HERE, 'EPMA_Reference_Methods_Section_v77_highlighted.docx'),
        False: os.path.join(HERE, 'EPMA_Reference_Methods_Section_v77.docx')}
TOKEN = re.compile(r'(\\\*|\*\*|\*|</?mark>)')


def add_inline(par, text, highlight, size=None):
    bold = ital = mark = False
    parts = TOKEN.split(text)
    for k, tok in enumerate(parts):
        if not tok:
            continue
        if tok == '\\*':
            tok = '*'
        elif tok == '**':
            bold = not bold; continue
        elif tok == '*':
            # A lone * glued to a word with nothing after it (the "Zn*" footnote marker) is
            # literal; otherwise it opens or closes italics.
            prev = parts[k - 1][-1:] if k else ''
            nxt = next((q for q in parts[k + 1:] if q), '')[:1]
            if not ital and (prev.isalnum() or not nxt.isalpha()):
                pass
            else:
                ital = not ital; continue
        elif tok == '<mark>':
            mark = True; continue
        elif tok == '</mark>':
            mark = False; continue
        run = par.add_run(tok)
        run.bold, run.italic = bold, ital
        if size:
            run.font.size = Pt(size)
        if mark and highlight:
            run.font.highlight_color = WD_COLOR_INDEX.YELLOW


def shade(cell, hex_fill):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear'); shd.set(qn('w:color'), 'auto'); shd.set(qn('w:fill'), hex_fill)
    tcPr.append(shd)


def rule(doc):
    p = doc.add_paragraph()
    pPr = p._p.get_or_add_pPr()
    bdr = OxmlElement('w:pBdr'); b = OxmlElement('w:bottom')
    for k, v in (('val', 'single'), ('sz', '6'), ('space', '1'), ('color', 'A6A6A6')):
        b.set(qn('w:' + k), v)
    bdr.append(b); pPr.append(bdr)


def build(highlight):
    doc = Document()
    sec = doc.sections[0]
    sec.page_width, sec.page_height = Inches(8.5), Inches(11)
    for side in ('left_margin', 'right_margin', 'top_margin', 'bottom_margin'):
        setattr(sec, side, Inches(1))
    st = doc.styles['Normal']
    st.font.name = 'Calibri'; st.font.size = Pt(11)
    st.paragraph_format.space_after = Pt(6)
    st.paragraph_format.line_spacing = 1.15

    lines = open(SRC, encoding='utf-8').read().split('\n')
    i = 0
    while i < len(lines):
        line = lines[i]
        if not line.strip():
            i += 1; continue
        if line.startswith('> '):                      # the note box
            if 'Highlighting.' in line and not highlight:
                i += 1; continue
            p = doc.add_paragraph()
            p.paragraph_format.left_indent = Inches(0.3)
            add_inline(p, line[2:], highlight, size=9.5)
            for r in p.runs:
                r.font.color.rgb = RGBColor(0x40, 0x40, 0x40)
            i += 1; continue
        if line.strip() == '---':
            rule(doc); i += 1; continue
        m = re.match(r'(#+)\s+(.*)', line)
        if m:
            level = {1: 0, 2: 1, 3: 2}[len(m.group(1))]
            h = doc.add_heading(level=level)
            add_inline(h, m.group(2), highlight)
            i += 1; continue
        if line.startswith('|'):                       # pipe table
            block = []
            while i < len(lines) and lines[i].startswith('|'):
                block.append(lines[i]); i += 1
            rows = [[c.strip() for c in r.strip('|').split('|')] for r in block if not re.match(r'\|[-| ]+\|$', r)]
            t = doc.add_table(rows=len(rows), cols=len(rows[0]))
            t.style = 'Table Grid'
            t.autofit = False
            widths = [0.55, 0.45, 1.15, 0.4, 0.85, 0.85, 1.55, 0.7]   # sums to 6.5 in
            # Word and LibreOffice lay out from the grid, not from per-cell widths
            for gc, w in zip(t._tbl.tblGrid.findall(qn('w:gridCol')), widths):
                gc.set(qn('w:w'), str(int(w * 1440)))
            for ri, r in enumerate(rows):
                for ci, val in enumerate(r):
                    cell = t.cell(ri, ci)
                    cell.width = Inches(widths[ci])
                    cell.paragraphs[0].paragraph_format.space_after = Pt(0)
                    add_inline(cell.paragraphs[0], val, highlight, size=8)
                    if ri == 0:
                        for run in cell.paragraphs[0].runs:
                            run.bold = True
                        shade(cell, 'D9E1F2')
            doc.add_paragraph().paragraph_format.space_after = Pt(0)
            continue
        if line.startswith('- '):
            p = doc.add_paragraph(style='List Bullet')
            add_inline(p, line[2:], highlight)
            i += 1; continue
        # paragraph: join continuation lines (the footnote pair under Table 1 stays separate)
        p = doc.add_paragraph()
        add_inline(p, line, highlight, size=9 if line.startswith(('\\*', '†')) else None)
        i += 1
    doc.save(OUTS[highlight])
    return OUTS[highlight]


if __name__ == '__main__':
    for hl in (True, False):
        print('wrote', os.path.basename(build(hl)))
