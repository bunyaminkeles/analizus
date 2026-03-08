"""
TR Dizin Makale Analizi PDF Rapor Oluşturucu.
tezanaliz pdf_builder.py ile aynı altyapı, "Makale Analizi" markası.
"""
import io
import os
import logging
from datetime import date

logger = logging.getLogger(__name__)

C_WHITE  = (1.0,  1.0,  1.0)
C_LIGHT  = (0.96, 0.97, 0.99)
C_NAVY   = (0.07, 0.14, 0.31)
C_ACCENT = (0.31, 0.47, 0.66)
C_BORDER = (0.80, 0.84, 0.92)
C_MUTED  = (0.40, 0.50, 0.60)

_FONT_NORMAL = 'Helvetica'
_FONT_BOLD   = 'Helvetica-Bold'


def _register_turkish_fonts():
    global _FONT_NORMAL, _FONT_BOLD
    try:
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
        import matplotlib
        mpl_ttf = os.path.join(matplotlib.get_data_path(), 'fonts', 'ttf')
        regular_path = os.path.join(mpl_ttf, 'DejaVuSans.ttf')
        bold_path    = os.path.join(mpl_ttf, 'DejaVuSans-Bold.ttf')

        _sys_regular = [
            '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
            '/usr/share/fonts/dejavu/DejaVuSans.ttf',
        ]
        _sys_bold = [
            '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',
            '/usr/share/fonts/dejavu/DejaVuSans-Bold.ttf',
        ]
        if not os.path.exists(regular_path):
            regular_path = next((p for p in _sys_regular if os.path.exists(p)), None)
        if not os.path.exists(bold_path):
            bold_path = next((p for p in _sys_bold if os.path.exists(p)), None)

        if regular_path and os.path.exists(regular_path):
            pdfmetrics.registerFont(TTFont('DejaVuSans', regular_path))
            _FONT_NORMAL = 'DejaVuSans'
        if bold_path and os.path.exists(bold_path):
            pdfmetrics.registerFont(TTFont('DejaVuSans-Bold', bold_path))
            _FONT_BOLD = 'DejaVuSans-Bold'
    except Exception as e:
        logger.warning(f'DejaVu font kaydedilemedi: {e}')


_register_turkish_fonts()


def _fig_to_image_reader(fig):
    from reportlab.lib.utils import ImageReader
    buf = io.BytesIO()
    fig.savefig(buf, format='png', dpi=150, bbox_inches='tight', facecolor='white')
    buf.seek(0)
    return ImageReader(buf)


def _draw_page_background(c, width, height):
    c.setFillColorRGB(*C_WHITE)
    c.rect(0, 0, width, height, fill=1, stroke=0)


def _draw_header(c, width, height, title, page_num=None, total_pages=None):
    HEADER_H = 58
    c.setFillColorRGB(*C_LIGHT)
    c.rect(0, height - HEADER_H, width, HEADER_H, fill=1, stroke=0)
    c.setStrokeColorRGB(*C_ACCENT)
    c.setLineWidth(3)
    c.line(0, height - HEADER_H, width, height - HEADER_H)
    c.setFillColorRGB(*C_ACCENT)
    c.rect(0, height - HEADER_H, 6, HEADER_H, fill=1, stroke=0)

    c.setFillColorRGB(*C_NAVY)
    c.setFont(_FONT_BOLD, 13)
    c.drawString(22, height - 24, title)

    c.setFillColorRGB(*C_MUTED)
    c.setFont(_FONT_NORMAL, 8)
    c.drawString(22, height - 42, 'TR Dizin Makale Analizi — Analizus')

    if page_num and total_pages:
        c.setFillColorRGB(*C_MUTED)
        c.setFont(_FONT_NORMAL, 8)
        c.drawRightString(width - 18, height - 24, f'Sayfa {page_num} / {total_pages}')

    c.setFillColorRGB(*C_ACCENT)
    c.setFont(_FONT_BOLD, 9)
    c.drawRightString(width - 18, height - 42, 'ANALIZUS')


def _draw_footer(c, width):
    c.setStrokeColorRGB(*C_BORDER)
    c.setLineWidth(0.8)
    c.line(18, 30, width - 18, 30)
    c.setFillColorRGB(*C_MUTED)
    c.setFont(_FONT_NORMAL, 8)
    today = date.today().strftime('%d.%m.%Y')
    c.drawString(18, 14, f'Analizus — Akademik Veri Üssü  |  analizus.com  |  {today}')
    c.drawRightString(width - 18, 14, 'Bu rapor otomatik olarak oluşturulmuştur.')


def _draw_cover(c, width, height, total_records: int, query_summary: str):
    _draw_page_background(c, width, height)

    c.setFillColorRGB(*C_NAVY)
    c.rect(0, height - 180, width, 180, fill=1, stroke=0)
    c.setStrokeColorRGB(*C_ACCENT)
    c.setLineWidth(4)
    c.line(0, height - 180, width, height - 180)

    c.setFillColorRGB(*C_ACCENT)
    c.setFont(_FONT_BOLD, 26)
    c.drawCentredString(width / 2, height - 58, 'ANALIZUS')

    c.setFillColorRGB(0.75, 0.87, 1.0)
    c.setFont(_FONT_NORMAL, 9)
    c.drawCentredString(width / 2, height - 78, 'Akademik Veri Üssü  —  analizus.com')

    c.setFillColorRGB(1.0, 1.0, 1.0)
    c.setFont(_FONT_BOLD, 20)
    c.drawCentredString(width / 2, height - 118, 'TR Dizin Makale Analizi Raporu')

    c.setFillColorRGB(*C_ACCENT)
    c.setFont(_FONT_NORMAL, 11)
    c.drawCentredString(width / 2, height - 150, 'TR Dizin Verisi')

    card_w = 350
    card_h = 110
    card_x = width / 2 - card_w / 2
    card_y = height / 2 - card_h / 2

    c.setFillColorRGB(0.86, 0.89, 0.94)
    c.roundRect(card_x + 4, card_y - 4, card_w, card_h, 10, fill=1, stroke=0)
    c.setFillColorRGB(*C_WHITE)
    c.roundRect(card_x, card_y, card_w, card_h, 10, fill=1, stroke=0)
    c.setStrokeColorRGB(*C_BORDER)
    c.setLineWidth(1)
    c.roundRect(card_x, card_y, card_w, card_h, 10, fill=0, stroke=1)
    c.setFillColorRGB(*C_ACCENT)
    c.roundRect(card_x, card_y, 7, card_h, 4, fill=1, stroke=0)

    row_y = card_y + card_h - 26

    def _kv(key, val):
        nonlocal row_y
        c.setFillColorRGB(*C_MUTED)
        c.setFont(_FONT_NORMAL, 9)
        c.drawString(card_x + 22, row_y, key)
        c.setFillColorRGB(*C_NAVY)
        c.setFont(_FONT_BOLD, 10)
        c.drawString(card_x + 150, row_y, str(val)[:48])
        row_y -= 26

    _kv('Toplam Makale:', f'{total_records:,}')
    _kv('Sorgu:', (query_summary or 'Genel Tarama')[:48])
    _kv('Rapor Tarihi:', date.today().strftime('%d.%m.%Y'))
    _kv('Hazırlayan:', 'Analizus Otomatik Analiz')

    _draw_footer(c, width)


def _draw_figure_page(c, width, height, fig, analysis_title: str, page_num: int, total_pages: int):
    _draw_page_background(c, width, height)
    _draw_header(c, width, height, title=analysis_title, page_num=page_num, total_pages=total_pages)
    _draw_footer(c, width)

    img_reader = _fig_to_image_reader(fig)

    from reportlab.lib.units import cm
    margin       = 0.8 * cm
    content_top  = height - 58 - margin
    content_bot  = 35 + margin
    content_w    = width - 2 * margin
    content_h    = content_top - content_bot

    iw, ih = img_reader.getSize()
    ratio  = min(content_w / iw, content_h / ih)
    draw_w = iw * ratio
    draw_h = ih * ratio
    x = margin + (content_w - draw_w) / 2
    y = content_bot + (content_h - draw_h) / 2

    c.setFillColorRGB(0.87, 0.89, 0.93)
    c.roundRect(x + 4, y - 4, draw_w, draw_h, 8, fill=1, stroke=0)
    c.drawImage(img_reader, x, y, width=draw_w, height=draw_h, preserveAspectRatio=True)
    c.setStrokeColorRGB(*C_BORDER)
    c.setLineWidth(0.5)
    c.roundRect(x, y, draw_w, draw_h, 8, fill=0, stroke=1)


def build_pdf(figures: list, total_records: int = 0, query_summary: str = '') -> bytes:
    """
    figures: [(title, Figure), ...]
    Kapak + sayfa sayfa PDF.
    """
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas as canvas_mod

    width, height = A4
    buf = io.BytesIO()
    c = canvas_mod.Canvas(buf, pagesize=A4)

    total_pages = 1 + len(figures)

    _draw_cover(c, width, height, total_records=total_records, query_summary=query_summary)
    c.showPage()

    for i, (title, fig) in enumerate(figures, start=1):
        try:
            _draw_figure_page(c, width, height, fig, title,
                              page_num=i + 1, total_pages=total_pages)
        except Exception as e:
            logger.warning(f'[makaleanaliz pdf] Grafik sayfası hatası [{title}]: {e}')
        c.showPage()

    c.save()
    buf.seek(0)
    return buf.read()
