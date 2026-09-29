import sys, pymupdf
SRC = "/root/.claude/uploads/f558412f-db81-59ea-9cb2-47460ef0a5d6/560055b0-LESKAART_TOPBAL_NIEUW_-_printklaar.pdf"
OUT = sys.argv[1]
SAMPLE = len(sys.argv) > 2

doc = pymupdf.open(SRC)

def field(page, name, rect, size=11, align=0, maxlen=0, multiline=False, value=""):
    w = pymupdf.Widget()
    w.field_type = pymupdf.PDF_WIDGET_TYPE_TEXT
    w.field_name = name
    w.rect = pymupdf.Rect(rect)
    w.text_font = "Helv"
    w.text_fontsize = size
    w.text_color = (0, 0, 0)
    w.border_width = 0
    w.fill_color = None
    w.text_format = pymupdf.TEXT_ALIGN_LEFT if align == 0 else pymupdf.TEXT_ALIGN_CENTER
    w.field_flags = pymupdf.PDF_TX_FIELD_IS_MULTILINE if multiline else 0
    if maxlen:
        w.text_maxlen = maxlen
    if value:
        w.field_value = value
    a = page.add_widget(w)
    if align:
        doc.xref_set_key(a.xref, "Q", "1")
        for ww in page.widgets():
            if ww.xref == a.xref:
                ww.update()

# ---- page 1 header ----
p = doc[0]
# remove "Postcode & woonplaats:" so the postcode line sits under the address
p.add_redact_annot(pymupdf.Rect(246, 128.5, 367, 137.5), fill=(1, 1, 1))
p.apply_redactions(images=pymupdf.PDF_REDACT_IMAGE_NONE,
                   graphics=pymupdf.PDF_REDACT_LINE_ART_NONE)

X = 282  # shared left edge: address and postcode start at exactly this x
R = 564
rows = [97.6, 111.9, 125.5, 139.5, 153.7, 167.4, 185.8]
S_ = lambda v: v if SAMPLE else ""
field(p, "Naam", (X, rows[0], R, rows[1]), value=S_("Jan Jansen"))
field(p, "Adres", (X, rows[1] + 1.2, R, rows[2] - 1), size=0,
      value=S_("Aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa,15 Rotterdam"))
field(p, "Postcode", (X, rows[2], R, rows[3]), value=S_("1234AB"))
field(p, "Geboortedatum", (329, rows[3], 430, rows[4]), value=S_("01-01-2005"))
field(p, "Mobiel", (473, rows[4 - 1], R, rows[4]), value=S_("06-12345678"))
field(p, "Datum aanvang", (329, rows[4], R, rows[5]), value=S_("29-09-2026"))
field(p, "Schakel automaat", (343, rows[5], R, rows[6] - 4), value=S_("Schakel"))

# ---- lesson tables: two mark columns + Opmerkingen ----
def tables(page, prefix):
    thin = [g["rect"] for g in page.get_drawings() if g["rect"].height < 800]
    verts = [r for r in thin if r.width < 1.2 and r.height > 5 and 290 < r.x0 < 500]
    xs = sorted({round(r.x0) for r in verts})
    # cluster to the three inner column lines
    cl = []
    for x in xs:
        if not cl or x - cl[-1][-1] > 4: cl.append([x])
        else: cl[-1].append(x)
    cols = [min(c) for c in cl]
    assert len(cols) == 3, cols
    mid = [r for r in verts if abs(r.x0 - cols[1]) < 4]
    n = 0
    for r in sorted(mid, key=lambda r: r.y0):
        n += 1
        y0, y1 = r.y0 + 0.8, r.y1 - 0.2
        field(page, f"{prefix} rij {n} a", (cols[0] + 1.5, y0, cols[1] - 0.5, y1), size=10, align=1, maxlen=2,
              value=S_("Y" if n % 3 == 0 else ""))
        field(page, f"{prefix} rij {n} b", (cols[1] + 1.5, y0, cols[2] - 0.5, y1), size=10, align=1, maxlen=2,
              value=S_("X" if n % 4 == 0 else ""))
        field(page, f"{prefix} rij {n} opmerking", (cols[2] + 3, y0, 565, y1), size=9,
              multiline=(y1 - y0) > 20, value=S_("Goed gedaan" if n == 2 else ""))
    return n

tables(doc[0], "Blad1")
tables(doc[1], "Blad2")

# ---- page 2 boxes ----
q = doc[1]
field(q, "Naam leerling", (196, 71.5, 521, 93.5), size=14, value=S_("Jan Jansen"))
field(q, "Opleider machtiging", (202, 487.8, 322, 504.6), size=11)
field(q, "Theoriecertificaat", (435, 487.8, 521, 504.6), size=11)
labels = [("Producten", 505.8, 523.4, 140), ("Plaats B-T", 524.5, 542.2, 140),
          ("Plaats B ex", 543.2, 560.2, 149), ("Plaats B-H ex", 561.2, 578.9, 163),
          ("Plaats B-NO ex", 580.0, 596.9, 168), ("Plaats B-FA ex", 598.0, 615.6, 168)]
for name, y0, y1, x0 in labels:
    field(q, name, (x0, y0, 521, y1), size=11)

doc.save(OUT, garbage=3, deflate=True)
print("ok", OUT)
