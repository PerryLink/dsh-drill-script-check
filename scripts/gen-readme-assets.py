#!/usr/bin/env python3
"""README visuals for dsh-drill-script-check, derived from the shipped pipeline.

Everything here is read off the repository, not off a generic checker template:

  `rules/drill-script-check.yaml`  eight rules DR-001…DR-008, each with a
                                   `check.kind` and a `basis.kind` that caps its
                                   severity (`derived-from-principle` <= warn,
                                   `institutional-configuration` <= info).
  `src/model.ts`                   the column aliases (stepNo, phase, script,
                                   commander, resource, durationMin, level,
                                   checkpoint) and the header fields the rules
                                   read (drillName, organizer,
                                   totalDurationMin).
  `src/shared/rows.ts`             what each `kind` reads: presenceAny takes two
                                   fields, conditionalPresence reads a trigger
                                   then a required field, sum adds a row column
                                   and compares it with a header field.
  `src/view.ts`                    the report: `summary`, `issues[]` with
                                   `locator.{row,column}`, `found`, `expected`,
                                   `fix`, plus `skipped[]` and a disclaimer.

Two figures:

  hero 1440x576 (Pillow: zh/en x light/dark, four WebP files)
      Left column: kicker / wordmark / two value lines / two-line subtitle /
      one meta line / footer. Right side: one drill sheet — a header strip
      (drill name, organizer, planned total) over three step rows — whose third
      row leaves `phase` and `script` blank. The two blank cells are ringed and
      a leader drops to the finding card the engine emits for that row
      (`DR-001` / `warn` / row 3 / phase / found / expected / fix). The sheet's
      duration rail — 6 + 5 + 4 = 15 — is the arithmetic DR-005 checks against
      the header's planned total.

  flow 1100x660 (hand-written SVG, light/dark — shared by all five READMEs)
      Grammar: a RULE x FIELD CAPABILITY MATRIX, not a node chain. Eight rule
      columns (id, `check.kind`, one sample-run state) cross eleven field rows:
      the eight step fields plus the three header fields, separated by a
      "HEADER · stated once per material" band. A filled dot means the rule
      reads that field on every row; a ring marks DR-004's trigger field
      (`script`); the sigma / equals pair marks DR-005's row sum against the
      header total. Two source cards (material, rule pack) converge on
      `drill_script_check` above the matrix; three report exits (`issues[]`,
      `skipped[]`, `summary`) sit beneath it. Everything is command-surface
      token or a short English note, so the same pair serves five languages.

All text is measured before it is drawn; a label that would overflow aborts the
run instead of shipping clipped text.

Run once:  python scripts/gen-readme-assets.py
Requires:  Pillow, Windows fonts msyh.ttc / msyhbd.ttc / consola.ttf.
"""
from __future__ import annotations

import os
from html import escape

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "docs", "assets")
NAME = "dsh-drill-script-check"

FONT_FILES = {
    "cjk": r"C:\Windows\Fonts\msyh.ttc",
    "cjk_bold": r"C:\Windows\Fonts\msyhbd.ttc",
    "mono": r"C:\Windows\Fonts\consola.ttf",
    "mono_bold": r"C:\Windows\Fonts\consolab.ttf",
}
for _kind, _path in FONT_FILES.items():
    if not os.path.exists(_path):
        raise SystemExit(f"FATAL: font missing: {_path}")
os.makedirs(OUT, exist_ok=True)

SKIN = {
    "light": dict(
        bg_from="#f9f6fd", bg_to="#e4eaf8",
        card="#ffffff", band="#f7f4fc", edge="#e7e2f0",
        text="#141419", sub="#4d5261", faint="#8f94a4",
        accent="#4B67B4", accent_soft="#ece7f9",
        grid="#e8e4f1",
        amber="#b45309", amber_bg="#fdf3e9", amber_soft="#f6e2cc",
        ok="#15803d", ok_bg="#eaf6ee",
        skip="#8f94a4", skip_bg="#eeecf3",
        shadow=(43, 32, 74), shadow_alpha=16, glow=30,
    ),
    "dark": dict(
        bg_from="#131a2a", bg_to="#0c1016",
        card="#1b2231", band="#202839", edge="#2e374b",
        text="#f0f3f9", sub="#a8b1c4", faint="#737b8d",
        accent="#8496f5", accent_soft="#242d42",
        grid="#262f42",
        amber="#d9a441", amber_bg="#2a2216", amber_soft="#3a2f1c",
        ok="#3fb950", ok_bg="#16281c",
        skip="#737b8d", skip_bg="#222a3a",
        shadow=(0, 0, 0), shadow_alpha=90, glow=48,
    ),
}

# --------------------------------------------------------------------------- #
# small drawing kit
# --------------------------------------------------------------------------- #


def font(size: int, kind: str = "cjk") -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(FONT_FILES[kind], size)


def hx(color: str) -> tuple[int, int, int]:
    color = color.lstrip("#")
    return tuple(int(color[i:i + 2], 16) for i in (0, 2, 4))


def gradient(w: int, h: int, top: str, bottom: str) -> Image.Image:
    base = Image.new("RGB", (w, h))
    draw = ImageDraw.Draw(base)
    a, b = hx(top), hx(bottom)
    for y in range(h):
        t = 0.10 * (y / h) + 0.90 * (y / h) ** 1.25
        draw.line([(0, y), (w, y)],
                  fill=tuple(int(p + (q - p) * t) for p, q in zip(a, b)))
    return base


def glow(img: Image.Image, cx: int, cy: int, r: int, color: str,
         alpha: int) -> Image.Image:
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    rgb = hx(color)
    for i in range(10, 0, -1):
        rr = r * i / 10
        d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr],
                  fill=rgb + (int(alpha * (1 - i / 11)),))
    return Image.alpha_composite(img.convert("RGBA"),
                                 layer.filter(ImageFilter.GaussianBlur(30))
                                 ).convert("RGB")


def shadows(img: Image.Image, boxes: list[tuple[tuple[int, int, int, int], int]],
            s: dict) -> Image.Image:
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer)
    for (x0, y0, x1, y1), radius in boxes:
        for i in range(12, 0, -2):
            alpha = int(s["shadow_alpha"] * (1 - i / 13) ** 1.5)
            if alpha <= 0:
                continue
            ld.rounded_rectangle(
                [x0 - i * 0.35, y0 + i * 0.5, x1 + i * 0.35, y1 + i * 0.9],
                radius=radius + i * 0.4,
                fill=s["shadow"] + (alpha,))
    return Image.alpha_composite(
        img.convert("RGBA"), layer.filter(ImageFilter.GaussianBlur(16))
    ).convert("RGB")


_MEASURE = ImageDraw.Draw(Image.new("RGB", (8, 8)))


def measure(text: str, size: int, kind: str) -> float:
    return _MEASURE.textlength(text, font=font(size, kind))


def require_w(text: str, size: int, kind: str, max_w: float, what: str) -> None:
    got = measure(text, size, kind)
    if got > max_w + 0.5:
        raise SystemExit(f"FATAL: {what} overflows: {text!r} needs "
                         f"{got:.1f}px > {max_w:.0f}px")


def fit(text: str, kind: str, max_w: float, start: int, minimum: int) -> int:
    size = start
    while size >= minimum:
        if measure(text, size, kind) <= max_w:
            return size
        size -= 1
    raise SystemExit(f"FATAL: text does not fit {max_w}px at >= {minimum}px: "
                     f"{text!r}")


def fit_lines(lines: list[str], kind: str, max_w: float, start: int,
              minimum: int) -> int:
    return min(fit(t, kind, max_w, start, minimum) for t in lines)


def pill(img: Image.Image, xy: tuple[int, int], text: str, s: dict,
         size: int = 16, fg: str | None = None, bg: str | None = None,
         kind: str = "cjk_bold", pad: int = 16) -> int:
    d = ImageDraw.Draw(img)
    f = font(size, kind)
    w = d.textlength(text, font=f)
    x, y = xy
    h = size + 19
    d.rounded_rectangle([x, y, x + w + pad * 2, y + h], radius=h / 2,
                        fill=hx(bg or s["accent_soft"]))
    d.text((x + pad, y + h / 2), text, font=f, fill=hx(fg or s["accent"]),
           anchor="lm")
    return int(x + w + pad * 2)


def dashed_rrect(d: ImageDraw.ImageDraw, box: tuple[float, float, float, float],
                 color: str, radius: int = 8, width: int = 2,
                 dash: int = 7, gap: int = 5) -> None:
    x0, y0, x1, y1 = box
    xa, xb = x0 + radius, x1 - radius
    for x in range(int(xa), int(xb), dash + gap):
        x_end = min(x + dash, xb)
        d.line([(x, y0), (x_end, y0)], fill=hx(color), width=width)
        d.line([(x, y1), (x_end, y1)], fill=hx(color), width=width)
    ya, yb = y0 + radius, y1 - radius
    for y in range(int(ya), int(yb), dash + gap):
        y_end = min(y + dash, yb)
        d.line([(x0, y), (x0, y_end)], fill=hx(color), width=width)
        d.line([(x1, y), (x1, y_end)], fill=hx(color), width=width)
    d.arc([x0, y0, x0 + 2 * radius, y0 + 2 * radius], 180, 270,
          fill=hx(color), width=width)
    d.arc([x1 - 2 * radius, y0, x1, y0 + 2 * radius], 270, 360,
          fill=hx(color), width=width)
    d.arc([x0, y1 - 2 * radius, x0 + 2 * radius, y1], 90, 180,
          fill=hx(color), width=width)
    d.arc([x1 - 2 * radius, y1 - 2 * radius, x1, y1], 0, 90,
          fill=hx(color), width=width)


# --------------------------------------------------------------------------- #
# hero content
# --------------------------------------------------------------------------- #

HERO = {
    "zh": dict(
        kicker="DEEPSEEK HARNESS 插件 · 演练脚本核对 · 只读",
        value=["把一份应急演练脚本", "读成一张差异清单"],
        sub=["读表头与每个环节一行，核对脚本自身的齐备与算术；",
             "差异指着行号与栏目——不下合规结论、不认定责任。"],
        meta="drill_script_check · DR-001…DR-008 · issues + skipped",
        foot="Apache-2.0 · 纯本地表格运算 · 不联网 · 不调用模型",
        sheet_title="演练脚本",
        sheet_tag="只读",
        sum="Σ 6+5+4 = 15 = 总时长",
        head=[("演练名称", "某某装置泄漏事故演练"),
              ("组织单位", "某某公司应急管理部"),
              ("计划总时长", "15 min")],
        cols=[("序号", 46), ("演练阶段", 104), ("脚本内容", 162),
              ("指挥人", 84), ("计划时长", 70), ("关键节点", 158)],
        rows=[["1", "预警与信息报告", "值班员发现泄漏并报告", "张指挥", "6", "接报确认"],
              ["2", "现场处置", "关阀断源、疏散人员", "李指挥", "5", "泄漏受控"],
              ["3", "", "", "王指挥", "4", "复位确认"]],
        card_rule="DR-001",
        card_sev="warn",
        card_loc="row 3 · phase",
        card_rows=[("found", "第 3 行 phase、script 都为空"),
                   ("expected", "phase、script 至少应填写一项"),
                   ("fix", "补填演练阶段与脚本内容；本条只核对是否填写，不判断处置是否正确")],
    ),
    "en": dict(
        kicker="DEEPSEEK HARNESS PLUGIN · DRILL-SCRIPT CHECKER · READ-ONLY",
        value=["Turn one drill script", "into a difference list"],
        sub=["Header plus one row per step: completeness and arithmetic.",
             "Every finding names a row and a column, never a verdict."],
        meta="drill_script_check · DR-001…DR-008 · issues + skipped",
        foot="Apache-2.0 · local table arithmetic · no network · no model call",
        sheet_title="Drill script",
        sheet_tag="read-only",
        sum="Σ 6+5+4 = 15 = planned",
        head=[("Drill", "Leak-response drill"),
              ("Organiser", "Some Co. emergency dept."),
              ("Planned total", "15 min")],
        cols=[("Step", 46), ("Phase", 104), ("Script", 162),
              ("Commander", 84), ("Min", 70), ("Checkpoint", 158)],
        rows=[["1", "Warning", "Operator reports the leak", "Zhang", "6", "Handover"],
              ["2", "On-scene", "Isolate, evacuate", "Li", "5", "Contained"],
              ["3", "", "", "Wang", "4", "Reset done"]],
        card_rule="DR-001",
        card_sev="warn",
        card_loc="row 3 · phase",
        card_rows=[("found", "row 3: phase and script are both empty"),
                   ("expected", "at least one of phase, script must be filled"),
                   ("fix", "fill in the phase and the script; presence only, not a judgement")],
    ),
}

# hero geometry, in final pixels
HERO_W, HERO_H = 1440, 576
LEFT_X, LEFT_W = 60, 620
SHEET = (712, 56, 1384, 344)
CARD = (712, 372, 1384, 536)


def hero(lang: str, skin: str) -> Image.Image:
    s = SKIN[skin]
    h = HERO[lang]
    img = gradient(HERO_W, HERO_H, s["bg_from"], s["bg_to"])
    img = glow(img, 1180, 80, 430, s["accent"], s["glow"])
    img = glow(img, 140, 566, 330, s["accent"], max(8, s["glow"] // 3))
    img = shadows(img, [(SHEET, 22), (CARD, 18)], s)
    d = ImageDraw.Draw(img)

    # ---- left column -------------------------------------------------------
    pill(img, (LEFT_X, 50), h["kicker"], s, size=16)
    d = ImageDraw.Draw(img)

    title_size = fit(NAME, "mono_bold", LEFT_W, 54, 48)
    require_w(NAME, title_size, "mono_bold", LEFT_W, "hero title")
    d.text((LEFT_X - 2, 152), NAME, font=font(title_size, "mono_bold"),
           fill=hx(s["text"]), anchor="ls")

    value_size = fit_lines(h["value"], "cjk_bold", LEFT_W, 46, 38)
    for i, line in enumerate(h["value"]):
        require_w(line, value_size, "cjk_bold", LEFT_W, "hero value line")
        d.text((LEFT_X, 232 + i * 58), line,
               font=font(value_size, "cjk_bold"), fill=hx(s["text"]),
               anchor="ls")

    sub_size = fit_lines(h["sub"], "cjk", LEFT_W, 22, 18)
    for i, line in enumerate(h["sub"]):
        require_w(line, sub_size, "cjk", LEFT_W, "hero subtitle")
        d.text((LEFT_X, 344 + i * 30), line, font=font(sub_size, "cjk"),
               fill=hx(s["sub"]), anchor="ls")

    require_w(h["meta"], 19, "mono", LEFT_W, "hero meta")
    d.text((LEFT_X - 1, 428), h["meta"], font=font(19, "mono"),
           fill=hx(s["faint"]), anchor="ls")

    d.line([LEFT_X, 470, LEFT_X + LEFT_W - 14, 470], fill=hx(s["grid"]),
           width=2)
    require_w(h["foot"], 16, "cjk", LEFT_W, "hero footer")
    d.text((LEFT_X, 496), h["foot"], font=font(16, "cjk"), fill=hx(s["faint"]),
           anchor="ls")

    # ---- sheet -------------------------------------------------------------
    x0, y0, x1, y1 = SHEET
    d.rounded_rectangle(SHEET, radius=22, fill=hx(s["card"]),
                        outline=hx(s["edge"]), width=2)

    pad = 24
    left = x0 + pad
    right = x1 - pad
    d.text((left, y0 + 32), h["sheet_title"], font=font(16, "cjk_bold"),
           fill=hx(s["text"]), anchor="ls")
    title_w = measure(h["sheet_title"], 16, "cjk_bold")
    d.text((left + title_w + 6, y0 + 32), "· " + h["sheet_tag"],
           font=font(11.5, "cjk"), fill=hx(s["faint"]), anchor="ls")
    sum_size = fit(h["sum"], "cjk", 260, 12, 11)
    require_w(h["sum"], sum_size, "cjk", 260, "hero sum")
    sum_w = measure(h["sum"], sum_size, "cjk")
    d.rounded_rectangle([right - sum_w - 24, y0 + 14, right, y0 + 38],
                        radius=12, fill=hx(s["ok_bg"]))
    d.text((right - 12, y0 + 26), h["sum"], font=font(sum_size, "cjk"),
           fill=hx(s["ok"]), anchor="rm")
    d.line([left, y0 + 46, right, y0 + 46], fill=hx(s["grid"]), width=2)

    # header strip
    head_top, head_h = y0 + 56, 50
    d.rounded_rectangle([left, head_top, right, head_top + head_h],
                        radius=12, fill=hx(s["band"]))
    head_x = [left + 16, left + 300, right - 130]
    for (label, value), hx_pos in zip(h["head"], head_x):
        d.text((hx_pos, head_top + 18), label, font=font(10.5, "cjk"),
               fill=hx(s["faint"]), anchor="ls")
        d.text((hx_pos, head_top + 40), value, font=font(13, "cjk_bold"),
               fill=hx(s["text"]), anchor="ls")
    require_w(h["head"][0][1], 13, "cjk_bold", 264, "hero drill name")
    require_w(h["head"][1][1], 13, "cjk_bold", 182, "hero organizer")
    require_w(h["head"][2][1], 13, "cjk_bold", 120, "hero total")

    # table
    table_top = head_top + head_h + 20
    head_row = 26
    row_h = 42
    col_x = [left]
    for _label, width in h["cols"]:
        col_x.append(col_x[-1] + width)
    for i, (label, _width) in enumerate(h["cols"]):
        d.text((col_x[i] + (0 if i == 0 else 6), table_top + 19), label,
               font=font(11.5, "cjk_bold"), fill=hx(s["sub"]), anchor="ls")
    d.line([left, table_top + head_row, right, table_top + head_row],
           fill=hx(s["grid"]), width=2)

    ring_row = len(h["rows"]) - 1
    ring_y = table_top + head_row + ring_row * row_h
    d.rounded_rectangle([col_x[1] + 1, ring_y + 5, col_x[3] - 1,
                         ring_y + row_h - 5], radius=9,
                        fill=hx(s["amber_bg"]))

    for r, row in enumerate(h["rows"]):
        ry = table_top + head_row + r * row_h
        if r:
            d.line([left, ry, right, ry], fill=hx(s["grid"]), width=2)
        for c, value in enumerate(row):
            if value == "":
                cell = (col_x[c] + 7, ry + 8, col_x[c + 1] - 7, ry + row_h - 8)
                dashed_rrect(d, cell, s["amber_soft"], radius=8, width=2,
                             dash=8, gap=5)
                d.text(((cell[0] + cell[2]) / 2, (cell[1] + cell[3]) / 2 - 1),
                       "—", font=font(13, "cjk"), fill=hx(s["amber"]),
                       anchor="mm")
            else:
                size = 12.5
                fit_width = (col_x[c + 1] - col_x[c] - 16)
                if measure(value, size, "cjk") > fit_width:
                    size = fit(value, "cjk", fit_width, 12, 10)
                weight = "cjk_bold" if c == 0 else "cjk"
                d.text((col_x[c] + (2 if c == 0 else 6), ry + 27), value,
                       font=font(size, weight), fill=hx(s["text"]),
                       anchor="ls")

    # ring around the two blank cells of the last row
    ring = (col_x[1] - 2, ring_y + 3, col_x[3] - 1, ring_y + row_h - 3)
    d.rounded_rectangle(ring, radius=11, outline=hx(s["amber"]), width=3)

    # leader down to the finding card
    leader_x = (ring[0] + ring[2]) / 2
    dash_y = ring[3] + 6
    while dash_y < CARD[1] - 4:
        d.line([leader_x, dash_y, leader_x, min(dash_y + 6, CARD[1] - 4)],
               fill=hx(s["amber"]), width=3)
        dash_y += 12
    d.ellipse([leader_x - 4, ring[3] - 1, leader_x + 4, ring[3] + 7],
              fill=hx(s["amber"]))

    # ---- finding card ------------------------------------------------------
    cx0, cy0, cx1, cy1 = CARD
    d.rounded_rectangle(CARD, radius=18, fill=hx(s["card"]),
                        outline=hx(s["amber"]), width=2)
    d.rounded_rectangle([cx0 + 16, cy0 + 34, cx0 + 22, cy1 - 34], radius=3,
                        fill=hx(s["amber"]))

    inner = cx0 + 40
    end = pill(img, (inner, cy0 + 20), h["card_rule"], s, size=12,
               kind="mono_bold", pad=10)
    d = ImageDraw.Draw(img)
    pill(img, (end + 8, cy0 + 20), h["card_sev"], s, size=12, kind="mono_bold",
         fg=s["amber"], bg=s["amber_bg"], pad=10)
    d = ImageDraw.Draw(img)
    d.text((cx1 - 22, cy0 + 37), h["card_loc"], font=font(12, "mono"),
           fill=hx(s["faint"]), anchor="rs")

    for i, (label, value) in enumerate(h["card_rows"]):
        ly = cy0 + 74 + i * 30
        d.text((inner, ly), label, font=font(10.5, "mono"),
               fill=hx(s["accent"]), anchor="ls")
        require_w(value, 12.5, "cjk", cx1 - (inner + 92) - 20, "hero card line")
        d.text((inner + 92, ly), value, font=font(12.5, "cjk"),
               fill=hx(s["text"]), anchor="ls")

    return img


# --------------------------------------------------------------------------- #
# flow SVG: rule x field capability matrix
# --------------------------------------------------------------------------- #

FONT_SANS = ("'Microsoft YaHei','Segoe UI',ui-sans-serif,system-ui,"
             "sans-serif")
FONT_MONO = "ui-monospace,Consolas,'Courier New',monospace"

FLOW_W, FLOW_H = 1100, 660

# (id, check.kind, kind line 2, state) — straight from the rule pack
FLOW_RULES = [
    ("DR-001", "presenceAny", "", "finding"),
    ("DR-002", "presence", "", "clean"),
    ("DR-003", "enum", "", "skipped"),
    ("DR-004", "conditional", "Presence", "clean"),
    ("DR-005", "sum", "", "clean"),
    ("DR-006", "presence", "", "clean"),
    ("DR-007", "unique", "", "clean"),
    ("DR-008", "headerPresence", "", "clean"),
]
RULE_W = [96, 98, 100, 108, 96, 96, 100, 106]
RULE_X = [260 + sum(RULE_W[:i]) for i in range(len(RULE_W))]
assert sum(RULE_W) == 800 and RULE_X[-1] + RULE_W[-1] == 1060

FIELD_ROWS = ["stepNo", "phase", "script", "commander", "resource",
              "durationMin", "level", "checkpoint"]
HEADER_ROWS = ["drillName", "organizer", "totalDurationMin"]

# rule number -> {field: marker}, marker is dot / ring / sum / total
MARKS = {
    (1, "phase"): "dot", (1, "script"): "dot",
    (2, "commander"): "dot",
    (3, "level"): "dot",
    (4, "script"): "ring", (4, "resource"): "dot",
    (5, "durationMin"): "sum", (5, "totalDurationMin"): "total",
    (6, "checkpoint"): "dot",
    (7, "stepNo"): "dot",
    (8, "drillName"): "dot", (8, "organizer"): "dot",
}

STATE_COLOR = {"finding": "amber", "skipped": "skip", "clean": "ok"}


class Svg:
    """Tiny string builder for one hand-written SVG document."""

    def __init__(self) -> None:
        self.parts: list[str] = []

    def add(self, chunk: str) -> None:
        self.parts.append(chunk)

    def rect(self, x: float, y: float, w: float, h: float, fill: str,
             r: float = 0, stroke: str | None = None, sw: float = 1) -> None:
        self.add(f'<rect x="{x:g}" y="{y:g}" width="{w:g}" height="{h:g}" '
                 f'rx="{r:g}" fill="{fill}"'
                 + (f' stroke="{stroke}" stroke-width="{sw:g}"' if stroke else "")
                 + "/>")

    def line(self, x1: float, y1: float, x2: float, y2: float, stroke: str,
             sw: float = 1) -> None:
        self.add(f'<line x1="{x1:g}" y1="{y1:g}" x2="{x2:g}" y2="{y2:g}" '
                 f'stroke="{stroke}" stroke-width="{sw:g}"/>')

    def circle(self, cx: float, cy: float, r: float, fill: str | None = None,
               stroke: str | None = None, sw: float = 1) -> None:
        self.add(f'<circle cx="{cx:g}" cy="{cy:g}" r="{r:g}" '
                 f'fill="{fill or "none"}"'
                 + (f' stroke="{stroke}" stroke-width="{sw:g}"' if stroke else "")
                 + "/>")

    def path(self, d: str, stroke: str, sw: float = 1) -> None:
        self.add(f'<path d="{d}" fill="none" stroke="{stroke}" '
                 f'stroke-width="{sw:g}" stroke-linecap="round" '
                 f'stroke-linejoin="round"/>')

    def text(self, x: float, y: float, s: str, size: float, fill: str,
             family: str = "sans", weight: str = "400",
             anchor: str = "start", spacing: float | None = None) -> None:
        extra = f' letter-spacing="{spacing:g}"' if spacing is not None else ""
        face = FONT_MONO if family == "mono" else FONT_SANS
        self.add(f'<text x="{x:g}" y="{y:g}" fill="{fill}" '
                 f'font-family="{face}" font-size="{size:g}" '
                 f'font-weight="{weight}" text-anchor="{anchor}"{extra}>'
                 f'{escape(s)}</text>')

    def guard(self, s: str, size: float, family: str, max_w: float,
              what: str) -> None:
        kind = "mono" if family == "mono" else "cjk"
        got = measure(s, int(round(size)), kind) * 1.06  # browser slack
        if got > max_w + 0.5:
            raise SystemExit(f"FATAL: svg {what} overflows: {s!r} needs "
                             f"{got:.1f}px > {max_w:.0f}px")


def arrow(svg: Svg, x1: float, y1: float, x2: float, y2: float, color: str,
          sw: float = 1.6) -> None:
    svg.line(x1, y1, x2, y2, color, sw)
    if y1 == y2:
        sign = 1 if x2 > x1 else -1
        svg.path(f"M{x2 - 6 * sign:g} {y2 - 5:g}L{x2:g} {y2:g}"
                 f"L{x2 - 6 * sign:g} {y2 + 5:g}", color, sw)
    else:
        svg.path(f"M{x2 - 5:g} {y2 - 6:g}L{x2:g} {y2:g}L{x2 + 5:g} {y2 - 6:g}",
                 color, sw)


def flow_svg(skin: str) -> str:
    s = SKIN[skin]
    svg = Svg()
    svg.add(f'<svg xmlns="http://www.w3.org/2000/svg" width="{FLOW_W}" '
            f'height="{FLOW_H}" viewBox="0 0 {FLOW_W} {FLOW_H}" role="img" '
            f'aria-labelledby="t d">')
    svg.add('<title id="t">dsh-drill-script-check — rule x field matrix</title>')
    svg.add(
        '<desc id="d">Eight rules (DR-001 to DR-008) as columns and eleven '
        'material fields as rows; a dot marks a field a rule reads, a ring the '
        'trigger field of DR-004, sigma and equals the row sum DR-005 compares '
        'with the header total. Material and rule pack converge on '
        'drill_script_check above the matrix; issues, skipped and summary are '
        'the report exits below it.</desc>')
    svg.add("<defs>")
    svg.add(f'<linearGradient id="bg" x1="0" y1="0" x2="0" y2="1">'
            f'<stop offset="0" stop-color="{s["bg_from"]}"/>'
            f'<stop offset="1" stop-color="{s["bg_to"]}"/></linearGradient>')
    svg.add("</defs>")
    svg.add(f'<rect width="{FLOW_W}" height="{FLOW_H}" rx="20" fill="url(#bg)"/>')
    svg.add(f'<rect x="0.5" y="0.5" width="{FLOW_W - 1}" height="{FLOW_H - 1}" '
            f'rx="20" fill="none" stroke="{s["edge"]}"/>')

    # ---- title -------------------------------------------------------------
    svg.text(40, 44, "STRUCTURE · RULE × FIELD", 11, s["accent"],
             family="mono", weight="700", spacing=1.6)
    svg.text(40, 76, "Each rule reads only the fields it declares", 20,
             s["text"], weight="700")
    svg.guard("Each rule reads only the fields it declares", 20, "sans", 640,
              "title")
    svg.text(40, 99, "drill_script_check · material JSON / YAML (rows[] + "
             "header) × rules/*.yaml (8 rules, 2026.1)", 11.5, s["sub"],
             family="mono")
    svg.guard("drill_script_check · material JSON / YAML (rows[] + header) × "
              "rules/*.yaml (8 rules, 2026.1)", 11.5, "mono", 720, "subtitle")

    # ---- two sources converge on the engine --------------------------------
    src_y, src_h = 110, 56
    svg.rect(40, src_y, 276, src_h, s["card"], 12, s["edge"], 1.2)
    svg.text(56, src_y + 22, "MATERIAL · JSON / YAML", 12.5, s["text"],
             family="mono", weight="700")
    svg.text(56, src_y + 42, "aliases folded · rows[] + header", 11, s["faint"],
             family="mono")

    svg.rect(400, 104, 300, 64, s["card"], 14, s["accent"], 1.6)
    svg.text(550, 134, "drill_script_check", 15, s["accent"], family="mono",
             weight="700", anchor="middle")
    svg.text(550, 154, "parseTable → canonical rows → runTableCheck", 11,
             s["sub"], family="mono", anchor="middle")
    svg.guard("parseTable → canonical rows → runTableCheck", 11, "mono", 292,
              "engine sub")

    svg.rect(784, src_y, 276, src_h, s["card"], 12, s["edge"], 1.2)
    svg.text(800, src_y + 22, "RULE PACK · rules/*.yaml", 12.5, s["text"],
             family="mono", weight="700")
    svg.text(800, src_y + 42, "8 rules · version 2026.1", 11, s["faint"],
             family="mono")

    arrow(svg, 316, 138, 398, 138, s["faint"])
    arrow(svg, 784, 138, 702, 138, s["faint"])
    arrow(svg, 550, 168, 550, 176, s["faint"])

    # ---- matrix header -----------------------------------------------------
    head_y, head_h = 180, 60
    svg.rect(40, head_y, 1020, head_h, s["band"], 12)
    svg.text(56, head_y + 24, "field \\ rule", 11, s["faint"], family="mono")
    svg.text(56, head_y + 42, "8 step + 3 header fields", 11,
             s["faint"], family="mono")
    svg.guard("8 step + 3 header fields", 11, "mono", 196, "axis note")

    for i, (rid, kind, kind2, state) in enumerate(FLOW_RULES):
        cx = RULE_X[i] + RULE_W[i] / 2
        svg.circle(cx - 34, head_y + 20, 3.8, s[STATE_COLOR[state]])
        svg.text(cx, head_y + 25, rid, 13.5, s["text"], family="mono",
                 weight="700", anchor="middle")
        svg.guard(rid, 13.5, "mono", RULE_W[i] - 20, f"{rid} id")
        svg.text(cx, head_y + 45, kind, 11, s["faint"], family="mono",
                 anchor="middle")
        svg.guard(kind, 11, "mono", RULE_W[i] - 14, f"{rid} kind")
        if kind2:
            svg.text(cx, head_y + 56, kind2, 11, s["faint"], family="mono",
                     anchor="middle")
            svg.guard(kind2, 11, "mono", RULE_W[i] - 14, f"{rid} kind2")

    # ---- matrix body -------------------------------------------------------
    body_y, row_h = 240, 22
    band_y = body_y + row_h * len(FIELD_ROWS)
    band_h = 18
    hdr_y = band_y + band_h
    body_bottom = hdr_y + row_h * len(HEADER_ROWS)
    assert body_bottom == 500

    for i in range(len(FIELD_ROWS) + 1):
        svg.line(40, body_y + row_h * i, 1060, body_y + row_h * i,
                 s["grid"], 1)
    for i in range(len(HEADER_ROWS)):
        svg.line(40, hdr_y + row_h * i, 1060, hdr_y + row_h * i, s["grid"], 1)
    svg.line(40, body_bottom, 1060, body_bottom, s["grid"], 1)
    for x in RULE_X:
        svg.line(x, head_y + head_h, x, body_bottom, s["grid"], 1)
    svg.line(260, head_y + head_h, 260, body_bottom, s["grid"], 1)

    # header band separating step fields from the material's header
    svg.rect(40, band_y, 1020, band_h, s["band"], 0)
    svg.text(56, band_y + 13, "HEADER · stated once per material", 11,
             s["faint"], family="mono")
    svg.guard("HEADER · stated once per material", 11, "mono", 240,
              "header band")

    rows = [(FIELD_ROWS, body_y), (HEADER_ROWS, hdr_y)]
    for names, y0 in rows:
        for r, field_name in enumerate(names):
            cy = y0 + row_h * r + row_h / 2
            svg.text(56, cy + 4.5, field_name, 13, s["text"], family="mono")
            svg.guard(field_name, 13, "mono", 186, f"field {field_name}")
            for i, rule in enumerate(FLOW_RULES):
                cx = RULE_X[i] + RULE_W[i] / 2
                marker = MARKS.get((i + 1, field_name))
                if marker == "dot":
                    svg.circle(cx, cy, 5.2, s["accent"])
                elif marker == "ring":
                    svg.circle(cx, cy, 5.4, s["card"], s["accent"], 2.2)
                elif marker == "sum":
                    svg.text(cx, cy + 4.5, "Σ", 13, s["accent"], family="mono",
                             weight="700", anchor="middle")
                elif marker == "total":
                    svg.text(cx, cy + 4.5, "=", 13, s["accent"], family="mono",
                             weight="700", anchor="middle")
                else:
                    svg.circle(cx, cy, 2.2, s["grid"])

    # ---- legend ------------------------------------------------------------
    ly = body_bottom + 21
    svg.circle(46, ly - 3.5, 5.2, s["accent"])
    svg.text(58, ly, "read on every row", 11, s["sub"])
    svg.circle(196, ly - 3.5, 5.4, s["card"], s["accent"], 2.2)
    svg.text(208, ly, "trigger field", 11, s["sub"])
    svg.text(300, ly, "Σ", 13, s["accent"], family="mono", weight="700")
    svg.text(314, ly, "row sum = header total", 11, s["sub"])
    svg.circle(474, ly - 3.5, 2.2, s["grid"])
    svg.text(484, ly, "never read", 11, s["sub"])
    svg.text(566, ly, "·", 13, s["faint"])
    svg.text(580, ly, "state: one sample run —", 11, s["sub"])
    svg.circle(736, ly - 3.5, 3.8, s["amber"])
    svg.text(746, ly, "finding", 11, s["sub"])
    svg.circle(812, ly - 3.5, 3.8, s["skip"])
    svg.text(822, ly, "skipped", 11, s["sub"])
    svg.circle(892, ly - 3.5, 3.8, s["ok"])
    svg.text(902, ly, "ran clean", 11, s["sub"])

    ly2 = ly + 17
    caps = ("evidence kind caps severity — direct → any · "
            "derived-from-principle ≤ warn (7) · institutional-configuration "
            "≤ info (DR-003); no verbatim excerpt in this pack")
    svg.text(40, ly2, caps, 11, s["faint"], family="mono")
    svg.guard(caps, 11, "mono", 1020, "cap legend")

    # ---- report exits ------------------------------------------------------
    exits = [
        (40, 380, "issues[]", "1", "warn", "amber",
         "DR-001 · row 3 · phase",
         "found: phase — · script — → fix: fill either"),
        (400, 300, "skipped[]", "1", "not run", "skip",
         "DR-003 · values unset",
         "reported, never passed silently"),
        (720, 340, "summary", "8 rules", "0 error", "ok",
         "error 0 · warn 1 · info 0",
         "empty issues ≠ all clear"),
    ]
    exit_y, exit_h = 548, 78
    for x, w, title, count, tag, tag_color, l1, l2 in exits:
        svg.rect(x, exit_y, w, exit_h, s["card"], 14, s["edge"], 1.2)
        svg.text(x + 16, exit_y + 24, title, 13, s["text"], family="mono",
                 weight="700")
        svg.guard(title, 13, "mono", w - 130, f"{title} title")
        tw = measure(title, 13, "mono") * 1.06
        svg.text(x + 16 + tw + 8, exit_y + 24, count, 13, s["accent"],
                 family="mono", weight="700")
        tag_w = measure(tag, 11, "mono") * 1.06 + 16
        svg.rect(x + w - tag_w - 16, exit_y + 11, tag_w, 20,
                 s[tag_color + "_bg"], 10)
        svg.text(x + w - 16 - tag_w / 2, exit_y + 25, tag, 11, s[tag_color],
                 family="mono", anchor="middle")
        svg.text(x + 16, exit_y + 48, l1, 11.5, s["sub"], family="mono")
        svg.guard(l1, 11.5, "mono", w - 32, f"{title} line 1")
        svg.text(x + 16, exit_y + 66, l2, 11.5, s["faint"], family="mono")
        svg.guard(l2, 11.5, "mono", w - 32, f"{title} line 2")

    note = ("a finding is one cell — row × field — and the matrix shows "
            "reads, not verdicts")
    svg.text(40, 644, note, 11, s["faint"], family="mono")
    svg.guard(note, 11, "mono", 1020, "footnote")

    svg.add("</svg>")
    return "\n".join(svg.parts) + "\n"


# --------------------------------------------------------------------------- #
# main
# --------------------------------------------------------------------------- #


def main() -> None:
    written: list[str] = []
    for lang in ("zh", "en"):
        for skin in ("light", "dark"):
            img = hero(lang, skin)
            name = f"{NAME}-hero-{lang}-{skin}.webp"
            img.save(os.path.join(OUT, name), "WEBP", quality=92, method=6)
            written.append(name)
    for skin in ("light", "dark"):
        name = f"{NAME}-flow-v5-{skin}.svg"
        with open(os.path.join(OUT, name), "w", encoding="utf-8",
                  newline="\n") as fh:
            fh.write(flow_svg(skin))
        written.append(name)
    for name in written:
        size = os.path.getsize(os.path.join(OUT, name))
        print(f"wrote docs/assets/{name} ({size / 1024:.1f} kB)")


if __name__ == "__main__":
    main()
