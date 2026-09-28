"""
PDF Rapor Oluşturucu (reportlab)
- Beyaz arka plan, DejaVu font (Türkçe karakter desteği)
- build_demo_pdf(figures):  3 grafik → demo PDF bytes
- build_full_pdf(figures):  10 grafik → tam rapor PDF bytes
"""
import io
import os
from django.utils.translation import gettext
import logging
from datetime import date

logger = logging.getLogger(__name__)

# ── Renkler (RGB 0-1 ölçeği) ─────────────────────────────────────
C_WHITE  = (1.0,  1.0,  1.0)
C_LIGHT  = (0.96, 0.97, 0.99)   # hafif mavi-gri header arka planı
C_NAVY   = (0.07, 0.14, 0.31)   # koyu lacivert başlık
C_ACCENT = (0.31, 0.47, 0.66)   # Tableau mavi  #4E79A7
C_ORANGE = (0.95, 0.55, 0.17)   # Tableau turuncu #F28E2B
C_BORDER = (0.80, 0.84, 0.92)
C_MUTED  = (0.40, 0.50, 0.60)
C_DARK   = (0.07, 0.14, 0.31)

# ── Font ─────────────────────────────────────────────────────────
_FONT_NORMAL = 'Helvetica'
_FONT_BOLD   = 'Helvetica-Bold'


def _register_turkish_fonts():
    """DejaVu Sans'ı reportlab'e kaydet. Birincil kaynak: matplotlib bundle."""
    global _FONT_NORMAL, _FONT_BOLD
    try:
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont

        # matplotlib her zaman DejaVu fontlarını bundle eder — en güvenilir yol
        import matplotlib
        mpl_ttf = os.path.join(matplotlib.get_data_path(), 'fonts', 'ttf')
        regular_path = os.path.join(mpl_ttf, 'DejaVuSans.ttf')
        bold_path    = os.path.join(mpl_ttf, 'DejaVuSans-Bold.ttf')

        # Sistem fontları (yedek arama sırası)
        _sys_regular = [
            '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
            '/usr/share/fonts/dejavu/DejaVuSans.ttf',
            '/usr/share/fonts/truetype/DejaVuSans.ttf',
        ]
        _sys_bold = [
            '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',
            '/usr/share/fonts/dejavu/DejaVuSans-Bold.ttf',
            '/usr/share/fonts/truetype/DejaVuSans-Bold.ttf',
        ]

        if not os.path.exists(regular_path):
            regular_path = next((p for p in _sys_regular if os.path.exists(p)), None)
        if not os.path.exists(bold_path):
            bold_path = next((p for p in _sys_bold if os.path.exists(p)), None)

        if regular_path and os.path.exists(regular_path):
            pdfmetrics.registerFont(TTFont('DejaVuSans', regular_path))
            _FONT_NORMAL = 'DejaVuSans'
            logger.debug(f'DejaVuSans kaydedildi: {regular_path}')

        if bold_path and os.path.exists(bold_path):
            pdfmetrics.registerFont(TTFont('DejaVuSans-Bold', bold_path))
            _FONT_BOLD = 'DejaVuSans-Bold'
            logger.debug(f'DejaVuSans-Bold kaydedildi: {bold_path}')

        # Paragraph içindeki <b> etiketi aile eşlemesiyle kalın fonta geçer
        if _FONT_NORMAL == 'DejaVuSans':
            from reportlab.lib.fonts import addMapping
            addMapping('DejaVuSans', 0, 0, 'DejaVuSans')
            addMapping('DejaVuSans', 0, 1, 'DejaVuSans')
            addMapping('DejaVuSans', 1, 0, _FONT_BOLD)
            addMapping('DejaVuSans', 1, 1, _FONT_BOLD)

    except Exception as e:
        logger.warning(f'DejaVu font kaydedilemedi, Helvetica kullanılıyor: {e}')


_register_turkish_fonts()


# ── Matplotlib → PNG ─────────────────────────────────────────────

def _fig_to_image_reader(fig_or_bytes):
    """
    matplotlib Figure veya PNG bytes → reportlab ImageReader.
    Analyzer artık PNG bytes döndürüyor (Figure nesnesi değil).
    """
    from reportlab.lib.utils import ImageReader
    if isinstance(fig_or_bytes, (bytes, bytearray)):
        buf = io.BytesIO(fig_or_bytes)
    else:
        buf = io.BytesIO()
        fig_or_bytes.savefig(buf, format='png', dpi=120, bbox_inches='tight', facecolor='white')
    buf.seek(0)
    return ImageReader(buf)


# ── Sayfa Bileşenleri ─────────────────────────────────────────────

def _draw_page_background(c, width, height):
    c.setFillColorRGB(*C_WHITE)
    c.rect(0, 0, width, height, fill=1, stroke=0)


def _draw_header(c, width, height, title, subtitle='', page_num=None, total_pages=None):
    HEADER_H = 62

    # Header şeridi
    c.setFillColorRGB(*C_LIGHT)
    c.rect(0, height - HEADER_H, width, HEADER_H, fill=1, stroke=0)

    # Alt accent çizgisi
    c.setStrokeColorRGB(*C_ACCENT)
    c.setLineWidth(3)
    c.line(0, height - HEADER_H, width, height - HEADER_H)

    # Sol accent bar
    c.setFillColorRGB(*C_ACCENT)
    c.rect(0, height - HEADER_H, 6, HEADER_H, fill=1, stroke=0)

    # Başlık metni
    c.setFillColorRGB(*C_NAVY)
    c.setFont(_FONT_BOLD, 14)
    c.drawString(22, height - 26, title)

    if subtitle:
        c.setFillColorRGB(*C_MUTED)
        c.setFont(_FONT_NORMAL, 9)
        c.drawString(22, height - 44, subtitle)

    # Sayfa no
    if page_num and total_pages:
        c.setFillColorRGB(*C_MUTED)
        c.setFont(_FONT_NORMAL, 8)
        c.drawRightString(width - 18, height - 28, gettext('Sayfa {page} / {total}').format(page=page_num, total=total_pages))

    # Marka (sağ)
    c.setFillColorRGB(*C_ACCENT)
    c.setFont(_FONT_BOLD, 10)
    c.drawRightString(width - 18, height - 48, 'ANALIZUS')


def _draw_footer(c, width):
    c.setStrokeColorRGB(*C_BORDER)
    c.setLineWidth(0.8)
    c.line(18, 30, width - 18, 30)

    c.setFillColorRGB(*C_MUTED)
    c.setFont(_FONT_NORMAL, 8)
    today = date.today().strftime('%d.%m.%Y')
    c.drawString(18, 14, f"Analizus — {gettext('Akademik Veri Üssü')}  |  analizus.com  |  {today}")
    c.drawRightString(width - 18, 14, gettext('Bu rapor otomatik olarak oluşturulmuştur.'))


def _fit_text(text: str, font_name: str, font_size: float, max_width: float) -> str:
    """Metni max_width point'e sığacak şekilde kırp, '…' ekle."""
    try:
        from reportlab.pdfbase.pdfmetrics import stringWidth as _sw
        if _sw(text, font_name, font_size) <= max_width:
            return text
        while text and _sw(text + '…', font_name, font_size) > max_width:
            text = text[:-1]
        return text + '…'
    except Exception:
        # stringWidth yoksa karaktere göre kaba kırp
        limit = max(1, int(max_width / (font_size * 0.58)))
        return text[:limit] + ('…' if len(text) > limit else '')


def _draw_cover(c, width, height, is_demo: bool, total_records: int, filename: str, n_analyses: int = 0):
    _draw_page_background(c, width, height)

    # ── Üst başlık bandı ──
    c.setFillColorRGB(*C_NAVY)
    c.rect(0, height - 190, width, 190, fill=1, stroke=0)

    # Accent çizgi (bandın altı)
    c.setStrokeColorRGB(*C_ACCENT)
    c.setLineWidth(4)
    c.line(0, height - 190, width, height - 190)

    # Marka
    c.setFillColorRGB(*C_ACCENT)
    c.setFont(_FONT_BOLD, 28)
    c.drawCentredString(width / 2, height - 62, 'ANALIZUS')

    c.setFillColorRGB(0.75, 0.87, 1.0)
    c.setFont(_FONT_NORMAL, 10)
    c.drawCentredString(width / 2, height - 84, gettext('Akademik Veri Üssü  —  analizus.com'))

    # Rapor başlığı
    c.setFillColorRGB(1.0, 1.0, 1.0)
    c.setFont(_FONT_BOLD, 22)
    c.drawCentredString(width / 2, height - 128, gettext('Bibliometrik Analiz Raporu'))

    # Rapor türü etiketi
    # Sayı gerçek grafik sayısından (eskiden tam raporda sabit '10' yazıyordu, rapor 15 analiz içeriyordu)
    label      = (gettext('DEMO RAPOR  ({n} Analiz)') if is_demo else gettext('TAM RAPOR  ({n} Analiz)')).format(n=n_analyses)
    lbl_color  = C_ORANGE if is_demo else C_ACCENT
    c.setFillColorRGB(*lbl_color)
    c.setFont(_FONT_BOLD, 13)
    c.drawCentredString(width / 2, height - 160, label)

    # ── Bilgi kartı ──
    card_w = 440                          # genişletildi: değer kolonu için yeterli alan
    card_h = 128
    card_x = width / 2 - card_w / 2
    card_y = height / 2 - card_h / 2 - 20

    KEY_W   = 120                         # anahtar sütun genişliği
    VAL_X   = card_x + KEY_W + 22        # değer başlangıç X
    VAL_MAX = card_w - KEY_W - 22 - 12   # değere ayrılan maksimum genişlik (12pt sağ pay)

    # Gölge
    c.setFillColorRGB(0.86, 0.89, 0.94)
    c.roundRect(card_x + 5, card_y - 5, card_w, card_h, 10, fill=1, stroke=0)

    # Kart arka planı
    c.setFillColorRGB(*C_WHITE)
    c.roundRect(card_x, card_y, card_w, card_h, 10, fill=1, stroke=0)

    # Kart çerçevesi
    c.setStrokeColorRGB(*C_BORDER)
    c.setLineWidth(1)
    c.roundRect(card_x, card_y, card_w, card_h, 10, fill=0, stroke=1)

    # Sol accent bar
    c.setFillColorRGB(*C_ACCENT)
    c.roundRect(card_x, card_y, 7, card_h, 4, fill=1, stroke=0)

    # Kart içerikleri
    row_y = card_y + card_h - 28

    def _kv(key, val):
        nonlocal row_y
        c.setFillColorRGB(*C_MUTED)
        c.setFont(_FONT_NORMAL, 9)
        c.drawString(card_x + 22, row_y, key)
        c.setFillColorRGB(*C_NAVY)
        c.setFont(_FONT_BOLD, 10)
        val_str = _fit_text(str(val), _FONT_BOLD, 10, VAL_MAX)
        c.drawString(VAL_X, row_y, val_str)
        row_y -= 24

    _kv(gettext('Toplam Kayıt:'),  f'{total_records:,}')
    _kv(gettext('Dosya:'),          filename)
    _kv(gettext('Rapor Tarihi:'),   date.today().strftime('%d.%m.%Y'))
    _kv(gettext('Hazırlayan:'),     gettext('Analizus Otomatik Analiz'))

    # ── Demo uyarı kutusu ──
    if is_demo:
        note_y = card_y - 58
        note_h = 42
        c.setFillColorRGB(1.0, 0.97, 0.91)
        c.roundRect(card_x, note_y, card_w, note_h, 7, fill=1, stroke=0)
        c.setStrokeColorRGB(*C_ORANGE)
        c.setLineWidth(1.2)
        c.roundRect(card_x, note_y, card_w, note_h, 7, fill=0, stroke=1)
        c.setFillColorRGB(0.60, 0.35, 0.05)
        c.setFont(_FONT_BOLD, 9)
        c.drawCentredString(width / 2, note_y + 27, gettext('Demo: {n} analiz içermektedir.').format(n=n_analyses))
        c.setFont(_FONT_NORMAL, 8)
        c.setFillColorRGB(*C_MUTED)
        c.drawCentredString(width / 2, note_y + 12,
                            gettext('Tam rapor için sipariş oluşturunuz → analizus.com'))

    _draw_footer(c, width)


def _draw_figure_page(c, width, height, fig, analysis_title: str, page_num: int, total_pages: int,
                      warning: str = ''):
    _draw_page_background(c, width, height)
    _draw_header(c, width, height,
                 title=analysis_title,
                 subtitle=gettext('Bibliometrik Analiz Raporu — Analizus'),
                 page_num=page_num, total_pages=total_pages)
    _draw_footer(c, width)

    img_reader = _fig_to_image_reader(fig)

    # Kullanılabilir alan
    from reportlab.lib.units import cm
    margin       = 0.8 * cm
    content_top  = height - 62 - margin
    content_bot  = 35 + margin

    # Veri kesintisi uyarısı: footer'ın üstünde turuncu kutu, grafik alanı o kadar daralır
    if warning:
        box = _box(warning, width - 2 * margin, C_ORANGE, (1.0, 0.97, 0.91), font_size=8.5)
        _, box_h = box.wrap(width - 2 * margin, height)
        box.drawOn(c, margin, content_bot)
        content_bot += box_h + 8
    content_w    = width - 2 * margin
    content_h    = content_top - content_bot

    iw, ih = img_reader.getSize()
    ratio  = min(content_w / iw, content_h / ih)
    draw_w = iw * ratio
    draw_h = ih * ratio
    x = margin + (content_w - draw_w) / 2
    y = content_bot + (content_h - draw_h) / 2

    # Hafif gölge
    c.setFillColorRGB(0.87, 0.89, 0.93)
    c.roundRect(x + 4, y - 4, draw_w, draw_h, 8, fill=1, stroke=0)

    # Grafik
    c.drawImage(img_reader, x, y, width=draw_w, height=draw_h,
                preserveAspectRatio=True)

    # İnce çerçeve
    c.setStrokeColorRGB(*C_BORDER)
    c.setLineWidth(0.5)
    c.roundRect(x, y, draw_w, draw_h, 8, fill=0, stroke=1)


# ── Veri, Yöntem ve Kısıtlar bölümü (report_notes çıktısı) ───────

def _rgb(rgb):
    from reportlab.lib import colors
    return colors.Color(*rgb)


def _styles():
    from reportlab.lib.styles import ParagraphStyle
    body = ParagraphStyle('ax_body', fontName=_FONT_NORMAL, fontSize=9, leading=12.5, textColor=_rgb(C_DARK))
    return {
        'body':   body,
        'head':   ParagraphStyle('ax_head', parent=body, fontName=_FONT_BOLD, fontSize=11.5, leading=15,
                                 textColor=_rgb(C_NAVY)),
        'bullet': ParagraphStyle('ax_bullet', parent=body, leftIndent=12, bulletIndent=2),
        'muted':  ParagraphStyle('ax_muted', parent=body, fontSize=8, leading=11, textColor=_rgb(C_MUTED)),
    }


def _box(html: str, box_w: float, border_rgb, fill_rgb, font_size: float = 9):
    """Tek hücreli renkli kutu (Table) — html: escape edilmiş Paragraph metni."""
    from reportlab.platypus import Paragraph, Table, TableStyle
    from reportlab.lib.styles import ParagraphStyle
    st = ParagraphStyle('ax_box', fontName=_FONT_NORMAL, fontSize=font_size, leading=font_size * 1.35,
                        textColor=_rgb(C_DARK))
    t = Table([[Paragraph(html, st)]], colWidths=[box_w])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), _rgb(fill_rgb)),
        ('BOX', (0, 0), (-1, -1), 1, _rgb(border_rgb)),
        ('LEFTPADDING', (0, 0), (-1, -1), 8), ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 5), ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    return t


def _data_table(header: list, rows: list, col_widths: list, bold_last: bool = False):
    from reportlab.platypus import Table, TableStyle
    t = Table([header] + rows, colWidths=col_widths, hAlign='LEFT')
    style = [
        ('FONTNAME', (0, 0), (-1, -1), _FONT_NORMAL), ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('FONTNAME', (0, 0), (-1, 0), _FONT_BOLD), ('BACKGROUND', (0, 0), (-1, 0), _rgb(C_LIGHT)),
        ('TEXTCOLOR', (0, 0), (-1, -1), _rgb(C_DARK)), ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
        ('LINEBELOW', (0, 0), (-1, -1), 0.4, _rgb(C_BORDER)),
        ('TOPPADDING', (0, 0), (-1, -1), 3), ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]
    if bold_last:
        style.append(('FONTNAME', (0, -1), (-1, -1), _FONT_BOLD))
    t.setStyle(TableStyle(style))
    return t


def _notes_groups(notes: dict, avail_w: float) -> list:
    """Bölümün içeriği: sayfa bölünmesinde birlikte kalması gereken flowable grupları."""
    from xml.sax.saxutils import escape
    from django.conf import settings
    from django.urls import reverse
    from django.utils.formats import number_format
    from django.utils.translation import pgettext
    from reportlab.platypus import Paragraph

    st = _styles()
    num = lambda n: number_format(n, force_grouping=True)
    groups = [[Paragraph(escape(gettext(
        'Bu bölüm, analizlerin hangi veriyle ve hangi kurallarla üretildiğini ve sonuçları yorumlarken '
        'dikkate alınması gereken kısıtları özetler.')), st['body'])]]

    for w in notes.get('source_warnings') or []:
        groups.append([_box('<b>%s</b> %s' % (escape(gettext('Önemli:')), escape(w)),
                            avail_w, C_ORANGE, (1.0, 0.97, 0.91))])

    def section(title, first):
        groups.append([Paragraph(escape(title), st['head']), first])

    def bullets(title, texts):
        paras = [Paragraph(t, st['bullet'], bulletText='•') for t in texts]
        section(title, paras[0])
        groups.extend([p] for p in paras[1:])

    flow = notes.get('flow') or []
    section(gettext('Veri Akışı'), _data_table(
        [pgettext('bibliometri tablo', 'Adım'), pgettext('bibliometri tablo', 'Kayıt')],
        [[label, num(n)] for label, n in flow], [avail_w * 0.7, avail_w * 0.3], bold_last=True))

    coverage = notes.get('coverage') or []
    section(gettext('Alan Doluluğu'), Paragraph(escape(gettext(
        'Her analiz yalnız ilgili bilgisi dolu olan kayıtları kullanır.')), st['muted']))
    groups.append([_data_table(
        [pgettext('bibliometri tablo', 'Alan'), pgettext('bibliometri tablo', 'Kayıt'),
         pgettext('bibliometri tablo', 'Oran')],
        [[label, num(n), gettext('%{value}').format(value=number_format(pct, 1))] for label, n, pct, _ in coverage],
        [avail_w * 0.5, avail_w * 0.25, avail_w * 0.25])])

    bullets(gettext('Uygulanan Kurallar ve Eşikler'), [escape(r) for r in notes.get('rules') or []])
    if notes.get('skipped'):
        bullets(gettext('Üretilemeyen Analizler'),
                ['<b>%s</b>: %s' % (escape(t), escape(r)) for t, r in notes['skipped']])
    bullets(gettext('Bilinen Kısıtlar'), [escape(x) for x in notes.get('limitations') or []])

    url = getattr(settings, 'SITE_URL', 'https://analizus.com') + reverse('proje_talebi') + '?source=bibliometrics'
    groups.append([_box('%s<br/><link href="%s" color="#4E79A7">%s</link>' % (
        escape(gettext('Bu rapordaki analizler otomatik olarak üretilmiştir ve örnek niteliğindedir. Veri '
                       'temizliği, yazar ve kurum adlarının birleştirilmesi, birden fazla veri kaynağının '
                       'birlikte kullanılması ve bulguların yorumlanmasını içeren kapsamlı bir bibliometrik '
                       'çalışma için uzmanlarımızla görüşebilirsiniz:')),
        escape(url), escape(url)), avail_w, C_ACCENT, C_LIGHT)])
    return groups


def _paginate(groups: list, avail_w: float, avail_h: float, gap: float = 7) -> list:
    """Grupları sayfalara böler: [[(flowable, yükseklik), ...], ...] — grup sayfalar arasında bölünmez."""
    pages = [[]]
    remaining = avail_h
    for group in groups:
        sized = [(f, f.wrap(avail_w, avail_h)[1]) for f in group]
        need = sum(h for _, h in sized) + gap * len(sized)
        if need > remaining and pages[-1]:
            pages.append([])
            remaining = avail_h
        pages[-1].extend(sized)
        remaining -= need
    return pages


def _draw_notes_page(c, width, height, items: list, page_num: int, total_pages: int, margin: float,
                     gap: float = 7):
    _draw_page_background(c, width, height)
    _draw_header(c, width, height, title=gettext('Veri, Yöntem ve Kısıtlar'),
                 subtitle=gettext('Bibliometrik Analiz Raporu — Analizus'),
                 page_num=page_num, total_pages=total_pages)
    _draw_footer(c, width)
    y = height - 62 - margin
    for f, h in items:
        y -= h
        f.drawOn(c, margin, y)
        y -= gap


def _trend_warning(notes: dict, in_full_report: bool) -> str:
    """Veri eski yıllardan kesildiyse zaman serisi sayfalarına yazılacak kısa uyarı (escape edilmiş)."""
    from xml.sax.saxutils import escape
    year = (notes or {}).get('partial_year')
    if not year:
        return ''
    if in_full_report:
        text = gettext('Veri kesintisi: yalnız en yeni kayıtlar alındı; {year} yılı kısmen, daha eski yıllar '
                       'hiç kapsanmadı. Eski dönem eksik görünür. Ayrıntı raporun sonundaki "Veri, Yöntem ve '
                       'Kısıtlar" bölümündedir.')
    else:
        text = gettext('Veri kesintisi: yalnız en yeni kayıtlar alındı; {year} yılı kısmen, daha eski yıllar '
                       'hiç kapsanmadı. Eski dönem eksik görünür.')
    return escape(text.format(year=year))


# ── Public API ───────────────────────────────────────────────────

def build_demo_pdf(figures: list, total_records: int = 0, filename: str = '', notes: dict = None,
                   time_series: list = None) -> bytes:
    """figures: [(title, Figure), ...]  — ilk 3 tanesi kullanılır
    notes/time_series: verilirse veri kesildiğinde zaman serisi sayfalarına uyarı satırı (bölüm yok)"""
    A4, cm, canvas_mod, _ = _get_reportlab()
    width, height = A4

    buf = io.BytesIO()
    c = canvas_mod.Canvas(buf, pagesize=A4)

    demo_figs   = figures[:3]
    total_pages = 1 + len(demo_figs)
    warning     = _trend_warning(notes, in_full_report=False)
    series      = set(time_series or [])

    _draw_cover(c, width, height, is_demo=True,
                total_records=total_records, filename=filename, n_analyses=len(demo_figs))
    c.showPage()

    for i, (title, fig) in enumerate(demo_figs, start=1):
        try:
            _draw_figure_page(c, width, height, fig, title,
                              page_num=i + 1, total_pages=total_pages,
                              warning=warning if i - 1 in series else '')
        except Exception as e:
            logger.warning(f'PDF grafik sayfası [{title}]: {e}')
        c.showPage()

    c.save()
    buf.seek(0)
    return buf.read()


def build_full_pdf(figures: list, total_records: int = 0, filename: str = '', notes: dict = None,
                   time_series: list = None) -> bytes:
    """figures: [(title, Figure), ...]  — tümü kullanılır
    notes: report_notes.build_report_notes() çıktısı — raporun sonuna "Veri, Yöntem ve Kısıtlar" bölümü
    time_series: zaman serisi grafiklerinin figures içindeki sırası (veri kesintisi uyarısı için)"""
    A4, cm, canvas_mod, _ = _get_reportlab()
    width, height = A4

    buf = io.BytesIO()
    c = canvas_mod.Canvas(buf, pagesize=A4)

    margin     = 0.8 * cm
    note_pages = []
    if notes:
        avail_w = width - 2 * margin
        note_pages = _paginate(_notes_groups(notes, avail_w), avail_w, (height - 62 - margin) - (35 + margin))
    warning = _trend_warning(notes, in_full_report=True)
    series  = set(time_series or [])

    total_pages = 1 + len(figures) + len(note_pages)

    _draw_cover(c, width, height, is_demo=False,
                total_records=total_records, filename=filename, n_analyses=len(figures))
    c.showPage()

    for i, (title, fig) in enumerate(figures, start=1):
        try:
            _draw_figure_page(c, width, height, fig, title,
                              page_num=i + 1, total_pages=total_pages,
                              warning=warning if i - 1 in series else '')
        except Exception as e:
            logger.warning(f'PDF grafik sayfası [{title}]: {e}')
        c.showPage()

    for j, items in enumerate(note_pages, start=1 + len(figures) + 1):
        _draw_notes_page(c, width, height, items, page_num=j, total_pages=total_pages, margin=margin)
        c.showPage()

    c.save()
    buf.seek(0)
    return buf.read()


def _get_reportlab():
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import cm
    from reportlab.pdfgen import canvas
    from reportlab.lib.utils import ImageReader
    return A4, cm, canvas, ImageReader
