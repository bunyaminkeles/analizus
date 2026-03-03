"""
PDF Rapor Oluşturucu (reportlab)
- Beyaz arka plan, DejaVu font (Türkçe karakter desteği)
- build_demo_pdf(figures):  3 grafik → demo PDF bytes
- build_full_pdf(figures):  10 grafik → tam rapor PDF bytes
"""
import io
import os
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

    except Exception as e:
        logger.warning(f'DejaVu font kaydedilemedi, Helvetica kullanılıyor: {e}')


_register_turkish_fonts()


# ── Matplotlib → PNG ─────────────────────────────────────────────

def _fig_to_image_reader(fig):
    """
    matplotlib Figure → reportlab ImageReader.
    Analyzer beyaz tema kullandığından ek dönüşüm gerekmez.
    """
    from reportlab.lib.utils import ImageReader
    buf = io.BytesIO()
    fig.savefig(buf, format='png', dpi=150, bbox_inches='tight', facecolor='white')
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
        c.drawRightString(width - 18, height - 28, f'Sayfa {page_num} / {total_pages}')

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
    c.drawString(18, 14, f'Analizus — Akademik Veri Üssü  |  analizus.com  |  {today}')
    c.drawRightString(width - 18, 14, 'Bu rapor otomatik olarak oluşturulmuştur.')


def _draw_cover(c, width, height, is_demo: bool, total_records: int, filename: str):
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
    c.drawCentredString(width / 2, height - 84, 'Akademik Veri Üssü  —  analizus.com')

    # Rapor başlığı
    c.setFillColorRGB(1.0, 1.0, 1.0)
    c.setFont(_FONT_BOLD, 22)
    c.drawCentredString(width / 2, height - 128, 'Bibliometrik Analiz Raporu')

    # Rapor türü etiketi
    label      = 'DEMO RAPOR  (3 Analiz)' if is_demo else 'TAM RAPOR  (10 Analiz)'
    lbl_color  = C_ORANGE if is_demo else C_ACCENT
    c.setFillColorRGB(*lbl_color)
    c.setFont(_FONT_BOLD, 13)
    c.drawCentredString(width / 2, height - 160, label)

    # ── Bilgi kartı ──
    card_w = 330
    card_h = 128
    card_x = width / 2 - card_w / 2
    card_y = height / 2 - card_h / 2 - 20

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
        c.drawString(card_x + 140, row_y, str(val)[:44])
        row_y -= 24

    _kv('Toplam Kayıt:',  f'{total_records:,}')
    _kv('Dosya:',          filename[:42])
    _kv('Rapor Tarihi:',   date.today().strftime('%d.%m.%Y'))
    _kv('Hazırlayan:',     'Analizus Otomatik Analiz')

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
        c.drawCentredString(width / 2, note_y + 27, 'Demo: 3 analiz içermektedir.')
        c.setFont(_FONT_NORMAL, 8)
        c.setFillColorRGB(*C_MUTED)
        c.drawCentredString(width / 2, note_y + 12,
                            'Tam rapor (10 analiz) için sipariş oluşturunuz → analizus.com')

    _draw_footer(c, width)


def _draw_figure_page(c, width, height, fig, analysis_title: str, page_num: int, total_pages: int):
    _draw_page_background(c, width, height)
    _draw_header(c, width, height,
                 title=analysis_title,
                 subtitle='Bibliometrik Analiz Raporu — Analizus',
                 page_num=page_num, total_pages=total_pages)
    _draw_footer(c, width)

    img_reader = _fig_to_image_reader(fig)

    # Kullanılabilir alan
    from reportlab.lib.units import cm
    margin       = 0.8 * cm
    content_top  = height - 62 - margin
    content_bot  = 35 + margin
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


# ── Public API ───────────────────────────────────────────────────

def build_demo_pdf(figures: list, total_records: int = 0, filename: str = '') -> bytes:
    """figures: [(title, Figure), ...]  — ilk 3 tanesi kullanılır"""
    A4, cm, canvas_mod, _ = _get_reportlab()
    width, height = A4

    buf = io.BytesIO()
    c = canvas_mod.Canvas(buf, pagesize=A4)

    demo_figs   = figures[:3]
    total_pages = 1 + len(demo_figs)

    _draw_cover(c, width, height, is_demo=True,
                total_records=total_records, filename=filename)
    c.showPage()

    for i, (title, fig) in enumerate(demo_figs, start=1):
        try:
            _draw_figure_page(c, width, height, fig, title,
                              page_num=i + 1, total_pages=total_pages)
        except Exception as e:
            logger.warning(f'PDF grafik sayfası [{title}]: {e}')
        c.showPage()

    c.save()
    buf.seek(0)
    return buf.read()


def build_full_pdf(figures: list, total_records: int = 0, filename: str = '') -> bytes:
    """figures: [(title, Figure), ...]  — tümü kullanılır"""
    A4, cm, canvas_mod, _ = _get_reportlab()
    width, height = A4

    buf = io.BytesIO()
    c = canvas_mod.Canvas(buf, pagesize=A4)

    total_pages = 1 + len(figures)

    _draw_cover(c, width, height, is_demo=False,
                total_records=total_records, filename=filename)
    c.showPage()

    for i, (title, fig) in enumerate(figures, start=1):
        try:
            _draw_figure_page(c, width, height, fig, title,
                              page_num=i + 1, total_pages=total_pages)
        except Exception as e:
            logger.warning(f'PDF grafik sayfası [{title}]: {e}')
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
