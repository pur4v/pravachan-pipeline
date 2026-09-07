#!/usr/bin/env python3
"""
Typeset a Gujarati pravachan transcript fragment as PDF and/or DOCX.

Input is an HTML fragment using a small, fixed vocabulary of elements:

    <h1>title</h1>
    <p class="sub">subtitle</p>
    <p class="note">(editorial note)</p>
    <h2>section heading</h2>
    <p>body paragraph</p>
    <p class="q"><b>પ્રશ્ন:</b> audience question</p>
    <div class="verse">gatha<br>second line</div>
    <div class="box"><p>enumerated list</p></div>
    <p class="end">॥ closing ॥</p>

Usage:
    python3 build_doc.py content.html --out Vyakhyan --format both \
            --size 19 --columns 2 --landscape
"""

import argparse
import re
import sys
from pathlib import Path

GUJ_SERIF = "Noto Serif Gujarati"
GUJ_SANS = "Noto Sans Gujarati"
BROWN_HEX = "7A2E00"
RULE_HEX = "D9A066"
VERSE_BG = "FAF4EC"
BOX_BG = "F6F2EE"
BOX_BORDER = "DDD0C0"

CSS = """
@page {{ size: A4 {orient}; margin: {mv}mm {mh}mm; }}
body {{ font-family: "{serif}", "{sans}", serif;
        font-size: {size}pt; line-height: {lh}; color: #1a1a1a;
        text-align: {align}; }}
h1 {{ font-family: "{sans}", sans-serif; font-size: {h1}pt; text-align: center;
      margin: 0 0 4px 0; color: #{brown}; line-height: 1.3; }}
.sub {{ text-align: center; font-size: {sub}pt; color: #666; margin: 0 0 6px 0; }}
.note {{ font-size: {note}pt; color: #555; text-align: center; margin: 0 0 10px 0; }}
.rule {{ border-bottom: 3px double #B8763E; margin: 8px 0 16px 0; }}
.cols {{ column-count: {cols}; column-gap: 9mm; column-rule: 1px solid #{boxbd}; }}
h2 {{ font-family: "{sans}", sans-serif; font-size: {h2}pt; color: #{brown};
      margin: 16px 0 7px 0; border-left: 4px solid #{rule}; padding-left: 8px;
      line-height: 1.35; break-after: avoid; }}
p {{ margin: 0 0 10px 0; }}
.q {{ margin: 0 0 8px 0; padding-left: 12px; color: #5a4636;
      font-style: italic; }}
.q b {{ font-style: normal; color: #{brown}; }}
.verse {{ background: #{versebg}; border-left: 3px solid #{rule}; padding: 8px 10px;
          margin: 0 0 11px 0; text-align: center; line-height: 1.6;
          font-size: {verse}pt; break-inside: avoid; }}
.box {{ background: #{boxbg}; border: 1px solid #{boxbd}; padding: 8px 11px;
        margin: 0 0 11px 0; break-inside: avoid; font-size: {box}pt; }}
.end {{ text-align: center; color: #{brown}; margin-top: 16px; font-size: {end}pt; }}
"""


def split_masthead(fragment: str):
    """Separate the leading h1/.sub/.note block from the body."""
    from bs4 import BeautifulSoup

    soup = BeautifulSoup(fragment, "html.parser")
    mast, body = [], []
    seen_body = False
    for el in soup.find_all(["h1", "h2", "p", "div"], recursive=False):
        cls = el.get("class", [])
        is_mast = el.name == "h1" or "sub" in cls or "note" in cls
        if is_mast and not seen_body:
            mast.append(el)
        else:
            seen_body = True
            body.append(el)
    return soup, mast, body


def build_pdf(fragment, out, size, cols, landscape):
    from weasyprint import HTML

    align = "left" if cols > 1 else "justify"
    css = CSS.format(
        orient="landscape" if landscape else "portrait",
        mv=13 if landscape else 14, mh=14 if landscape else 13,
        serif=GUJ_SERIF, sans=GUJ_SANS, size=size, lh=1.62, align=align,
        h1=round(size * 1.6), sub=round(size * 0.85), note=round(size * 0.72),
        h2=round(size * 1.06), verse=round(size * 0.9), box=round(size * 0.95),
        end=round(size * 0.95), cols=cols,
        brown=BROWN_HEX, rule=RULE_HEX, versebg=VERSE_BG,
        boxbg=BOX_BG, boxbd=BOX_BORDER,
    )
    _, mast, body = split_masthead(fragment)
    html = (
        "<!DOCTYPE html><html lang='gu'><head><meta charset='utf-8'>"
        f"<style>{css}</style></head><body>"
        + "".join(str(e) for e in mast)
        + "<div class='rule'></div>"
        + f"<div class='cols'>{''.join(str(e) for e in body)}</div>"
        + "</body></html>"
    )
    HTML(string=html).write_pdf(f"{out}.pdf")
    return f"{out}.pdf"


def build_docx(fragment, out, size, cols, landscape):
    from docx import Document
    from docx.enum.section import WD_ORIENT, WD_SECTION
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.oxml import OxmlElement
    from docx.oxml.ns import qn
    from docx.shared import Cm, Pt, RGBColor

    brown = RGBColor(0x7A, 0x2E, 0x00)
    grey = RGBColor(0x66, 0x66, 0x66)

    def font(run, pt, bold=False, italic=False, color=None):
        run.font.size = Pt(pt)
        run.bold = bold
        run.italic = italic
        if color is not None:
            run.font.color.rgb = color
        rpr = run._element.get_or_add_rPr()
        rf = rpr.find(qn("w:rFonts"))
        if rf is None:
            rf = OxmlElement("w:rFonts")
            rpr.insert(0, rf)
        for a in ("w:ascii", "w:hAnsi", "w:cs"):
            rf.set(qn(a), GUJ_SERIF)

    def shade(par, fill):
        sh = OxmlElement("w:shd")
        sh.set(qn("w:val"), "clear")
        sh.set(qn("w:fill"), fill)
        par._p.get_or_add_pPr().append(sh)

    def bar(par, color):
        bd = OxmlElement("w:pBdr")
        lb = OxmlElement("w:left")
        lb.set(qn("w:val"), "single")
        lb.set(qn("w:sz"), "18")
        lb.set(qn("w:space"), "6")
        lb.set(qn("w:color"), color)
        bd.append(lb)
        par._p.get_or_add_pPr().append(bd)

    def inline(par, node, pt, italic=False):
        for child in node.children:
            nm = getattr(child, "name", None)
            if nm == "br":
                par.add_run().add_break()
            elif nm in ("b", "strong"):
                font(par.add_run(child.get_text()), pt, bold=True, italic=italic)
            elif nm in ("i", "em"):
                font(par.add_run(child.get_text()), pt, italic=True)
            elif nm == "span":
                font(par.add_run(child.get_text()), pt - 2, italic=True, color=grey)
            else:
                txt = child if isinstance(child, str) else child.get_text()
                if txt:
                    font(par.add_run(txt), pt, italic=italic)

    doc = Document()
    sec = doc.sections[0]
    if landscape:
        sec.orientation = WD_ORIENT.LANDSCAPE
        sec.page_width, sec.page_height = Cm(29.7), Cm(21.0)
    sec.top_margin = sec.bottom_margin = Cm(1.4)
    sec.left_margin = sec.right_margin = Cm(1.5)

    _, mast, body = split_masthead(fragment)

    for el in mast:
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        if el.name == "h1":
            font(p.add_run(el.get_text(strip=True)), round(size * 1.6), True, color=brown)
        elif "sub" in el.get("class", []):
            font(p.add_run(el.get_text(strip=True)), round(size * 0.85), color=grey)
        else:
            font(p.add_run(el.get_text(strip=True)), round(size * 0.72),
                 color=RGBColor(0x55, 0x55, 0x55))

    rule = doc.add_paragraph()
    bd = OxmlElement("w:pBdr")
    bt = OxmlElement("w:bottom")
    bt.set(qn("w:val"), "double")
    bt.set(qn("w:sz"), "12")
    bt.set(qn("w:space"), "1")
    bt.set(qn("w:color"), "B8763E")
    bd.append(bt)
    rule._p.get_or_add_pPr().append(bd)

    if cols > 1:
        bsec = doc.add_section(WD_SECTION.CONTINUOUS)
        if landscape:
            bsec.orientation = WD_ORIENT.LANDSCAPE
            bsec.page_width, bsec.page_height = Cm(29.7), Cm(21.0)
        bsec.top_margin = bsec.bottom_margin = Cm(1.4)
        bsec.left_margin = bsec.right_margin = Cm(1.5)
        c = bsec._sectPr.xpath("./w:cols")[0]
        c.set(qn("w:num"), str(cols))
        c.set(qn("w:space"), "480")
        c.set(qn("w:sep"), "1")

    for el in body:
        cls = el.get("class", [])
        if el.name == "h2":
            p = doc.add_paragraph()
            p.paragraph_format.space_before = Pt(12)
            p.paragraph_format.space_after = Pt(5)
            p.paragraph_format.keep_with_next = True
            bar(p, RULE_HEX)
            font(p.add_run(el.get_text(strip=True)), round(size * 1.06), True, color=brown)
        elif "verse" in cls:
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            shade(p, VERSE_BG)
            bar(p, RULE_HEX)
            p.paragraph_format.keep_together = True
            p.paragraph_format.space_after = Pt(10)
            inline(p, el, round(size * 0.9))
        elif "box" in cls:
            p = doc.add_paragraph()
            shade(p, BOX_BG)
            bar(p, BOX_BORDER)
            p.paragraph_format.keep_together = True
            p.paragraph_format.space_after = Pt(10)
            inline(p, el.find("p") or el, round(size * 0.95))
        elif "end" in cls:
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.space_before = Pt(14)
            font(p.add_run(el.get_text(strip=True)), round(size * 0.95), color=brown)
        else:
            p = doc.add_paragraph()
            p.paragraph_format.space_after = Pt(8)
            p.paragraph_format.line_spacing = 1.15
            if "q" in cls:
                p.paragraph_format.left_indent = Cm(0.4)
                inline(p, el, size, italic=True)
            else:
                inline(p, el, size)

    doc.save(f"{out}.docx")
    return f"{out}.docx"


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("content", help="HTML fragment file")
    ap.add_argument("--out", required=True, help="output base name, no extension")
    ap.add_argument("--format", choices=["pdf", "docx", "both"], default="both")
    ap.add_argument("--size", type=int, default=18, help="body point size")
    ap.add_argument("--columns", type=int, default=2, choices=[1, 2, 3])
    ap.add_argument("--portrait", action="store_true",
                    help="A4 vertical; default is landscape")
    args = ap.parse_args()
    landscape = not args.portrait

    fragment = Path(args.content).read_text(encoding="utf-8")
    # tolerate a full HTML document as input
    m = re.search(r"<body[^>]*>(.*)</body>", fragment, re.S | re.I)
    if m:
        fragment = m.group(1)
    # unwrap any .cols / .masthead wrapper divs so a full styled page can be reused
    from bs4 import BeautifulSoup
    _s = BeautifulSoup(fragment, "html.parser")
    for d in _s.find_all("div", class_=["cols", "masthead"]):
        d.unwrap()
    for r in _s.find_all("div", class_="rule"):
        r.decompose()
    fragment = str(_s).strip()

    made = []
    if args.format in ("pdf", "both"):
        made.append(build_pdf(fragment, args.out, args.size, args.columns, landscape))
    if args.format in ("docx", "both"):
        made.append(build_docx(fragment, args.out, args.size, args.columns, landscape))

    for f in made:
        print(f"wrote {f}")


if __name__ == "__main__":
    try:
        main()
    except ImportError as e:
        sys.exit(f"missing dependency: {e}\nrun scripts/setup.sh first")
