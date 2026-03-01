"""
PDF Rapor Oluşturucu (reportlab)
- Beyaz arka plan, DejaVu font (Türkçe karakter desteği)
- build_demo_pdf(figures):   3 grafik → demo PDF bytes
- build_full_pdf(figures):   10 grafik → tam rapor PDF bytes
"""
import io
import os
import logging
from datetime import date

logger = logging.getLogger(__name__)

# ── Renkler ──────────────────────────────────────────────────────
C_WHITE   = (1.0, 1.0, 1.0)
C_LIGHT   = (0.96, 0.97, 0.99)   # hafif mavi-gri header arka planı
C_NAVY    = (0.05, 0.07, 0.16)   # koyu başlık metni
C_ACCENT  = (0.0,  0.68, 0.83)   # #00ADCC — mavi vurgu
C_PURPLE  = (0.50, 0.42, 0.87)   # #7F6BDE
C_BORDER  = (0.80, 0.84, 0.92)   # çizgi/sınır
C_MUTED   = (0.45, 0.52, 0.62)   # alt metin
C_DARK    = (0.13, 0.15, 0.22)   # footer arka planı

# ── Font ─────────────────────────────────────────────────────────
_FONT_NORMAL = 'Helvetica'
_FONT_BOLD   = 'Helvetica-Bold'

def _register_turkish_fonts():
    """DejaVu Sans'ı kaydet → Türkçe karakter desteği."""
    global _FONT_NORMAL, _FONT_BOLD
    try:
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont

        candidates = [
            '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
            '/usr/share/fonts/dejavu/DejaVuSans.ttf',
            '/usr/share/fonts/truetype/DejaVuSans.ttf',
        ]
        bold_candidates = [
            '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',
            '/usr/share/fonts/dejavu/DejaVuSans-Bold.ttf',
            '/usr/share/fonts/truetype/DejaVuSans-Bold.ttf',
        ]
        # Projedeki fonts/ klasörü varsa öncelikli kullan
        base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        candidates.insert(0, os.path.join(base, 'fonts', 'DejaVuSans.ttf'))
        bold_candidates.insert(0, os.path.join(base, 'fonts', 'DejaVuSans-Bold.ttf'))

        for path in candidates:
            if os.path.exists(path):
                pdfmetrics.registerFont(TTFont('DejaVuSans', path))
                break
        for path in bold_candidates:
            if os.path.exists(path):
                pdfmetrics.registerFont(TTFont('DejaVuSans-Bold', path))
                break

        pdfmetrics.getFont('DejaVuSans')   # kayıt başarılıysa hata vermez
        _FONT_NORMAL = 'DejaVuSans'
        _FONT_BOLD   = 'DejaVuSans-Bold'
        logger.debug('DejaVu Sans kaydedildi — Türkçe desteği aktif')
    except Exception as e:
        logger.warning(f'DejaVu font kaydedilemedi, Helvetica kullanılıyor: {e}')

_register_turkish_fonts()


# ── Matplotlib → PNG (beyaz tema) ────────────────────────────────

def _fig_to_image_reader(fig):
    """
    matplotlib Figure'ı PDF için beyaz arka planlı PNG'ye çevirir.
    Figürü değiştirmez — geçici axes renk düzeltmesi yapılır.
    """
    from reportlab.lib.utils import ImageReader
    import matplotlib
    matplotlib.use('Agg')

    # Axes renklerini beyaz temaya geçici geç
    axes_list = fig.get_axes()
    old_state = []
    for ax in axes_list:
        old_state.append({
            'face':   ax.get_facecolor(),
            'xcolor': ax.xaxis.label.get_color(),
            'ycolor': ax.yaxis.label.get_color(),
            'tcolor': ax.title.get_color(),
            'xtick':  [t.get_color() for t in ax.get_xticklabels()],
            'ytick':  [t.get_color() for t in ax.get_yticklabels()],
        })
        ax.set_facecolor('#f8f9fc')
        ax.xaxis.label.set_color('#1a1a2e')
        ax.yaxis.label.set_color('#1a1a2e')
        ax.title.set_color('#1a1a2e')
        ax.tick_params(colors='#2d3748')
        for spine in ax.spines.values():
            spine.set_edgecolor('#cbd5e0')

    buf = io.BytesIO()
    fig.savefig(buf, format='png', dpi=150, bbox_inches='tight', facecolor='white')
    buf.seek(0)

    # Renkleri geri al
    for ax, state in zip(axes_list, old_state):
        ax.set_facecolor(state['face'])
        ax.xaxis.label.set_color(state['xcolor'])
        ax.yaxis.label.set_color(state['ycolor'])
        ax.title.set_color(state['tcolor'])

    return ImageReader(buf)


# ── Sayfa Bileşenleri ─────────────────────────────────────────────

def _draw_page_background(c, width, height):
    c.setFillColorRGB(*C_WHITE)
    c.rect(0, 0, width, height, fill=1, stroke=0)


def _draw_header(c, width, height, title, subtitle='', page_num=None, total_pages=None):
    from reportlab.lib.units import cm

    # Arka plan şeridi
    c.setFillColorRGB(*C_LIGHT)
    c.rect(0, height - 65, width, 65, fill=1, stroke=0)

    # Alt sınır çizgisi (accent)
    c.setStrokeColorRGB(*C_ACCENT)
    c.setLineWidth(3)
    c.line(0, height - 65, width, height - 65)

    # Sol accent blok
    c.setFillColorRGB(*C_ACCENT)
    c.rect(0, height - 65, 5, 65, fill=1, stroke=0)

    # Başlık
    c.setFillColorRGB(*C_NAVY)
    c.setFont(_FONT_BOLD, 15)
    c.drawString(22, height - 30, title)

    if subtitle:
        c.setFillColorRGB(*C_MUTED)
        c.setFont(_FONT_NORMAL, 9)
        c.drawString(22, height - 48, subtitle)

    # Sayfa no (sağ üst)
    if page_num and total_pages:
        c.setFillColorRGB(*C_MUTED)
        c.setFont(_FONT_NORMAL, 8)
        c.drawRightString(width - 18, height - 32, f'Sayfa {page_num} / {total_pages}')

    # Logo (sağ)
    c.setFillColorRGB(*C_ACCENT)
    c.setFont(_FONT_BOLD, 11)
    c.drawRightString(width - 18, height - 52, 'ANALIZUS')


def _draw_footer(c, width):
    # Üst sınır çizgisi
    c.setStrokeColorRGB(*C_BORDER)
    c.setLineWidth(0.8)
    c.line(18, 32, width - 18, 32)

    c.setFillColorRGB(*C_MUTED)
    c.setFont(_FONT_NORMAL, 8)
    c.drawString(18, 16, f'Analizus — Akademik Veri Ustu  |  analizus.com  |  {date.today().strftime("%d.%m.%Y")}')
    c.drawRightString(width - 18, 16, 'Bu rapor otomatik olarak olusturulmustur.')


def _draw_cover(c, width, height, is_demo: bool, total_records: int, filename: str):
    from reportlab.lib.units import cm

    _draw_page_background(c, width, height)

    # Üst büyük başlık alanı
    c.setFillColorRGB(*C_NAVY)
    c.rect(0, height - 180, width, 180, fill=1, stroke=0)

    # Logo
    c.setFillColorRGB(*C_ACCENT)
    c.setFont(_FONT_BOLD, 26)
    c.drawCentredString(width / 2, height - 65, 'ANALIZUS')

    c.setFillColorRGB(0.7, 0.85, 1.0)
    c.setFont(_FONT_NORMAL, 10)
    c.drawCentredString(width / 2, height - 85, 'Akademik Veri Ustu  —  analizus.com')

    # Rapor türü
    c.setFillColorRGB(1, 1, 1)
    c.setFont(_FONT_BOLD, 22)
    c.drawCentredString(width / 2, height - 125, 'Bibliometrik Analiz Raporu')

    label = 'DEMO RAPOR (3 Analiz)' if is_demo else 'TAM RAPOR (10 Analiz)'
    label_color = C_PURPLE if is_demo else C_ACCENT
    c.setFillColorRGB(*label_color)
    c.setFont(_FONT_BOLD, 13)
    c.drawCentredString(width / 2, height - 152, label)

    # ── Bilgi kutusu ──
    box_y = height / 2 - 30
    box_h = 120
    box_x = width / 2 - 160

    # Gölge
    c.setFillColorRGB(0.88, 0.90, 0.95)
    c.roundRect(box_x + 4, box_y - 4, 320, box_h, 10, fill=1, stroke=0)

    # Kart
    c.setFillColorRGB(*C_WHITE)
    c.roundRect(box_x, box_y, 320, box_h, 10, fill=1, stroke=0)
    c.setStrokeColorRGB(*C_BORDER)
    c.setLineWidth(1)
    c.roundRect(box_x, box_y, 320, box_h, 10, fill=0, stroke=1)

    # Sol accent bar
    c.setFillColorRGB(*C_ACCENT)
    c.roundRect(box_x, box_y, 6, box_h, 3, fill=1, stroke=0)

    # İçerik
    row_y = box_y + box_h - 30
    def _kv(key, val):
        nonlocal row_y
        c.setFillColorRGB(*C_MUTED)
        c.setFont(_FONT_NORMAL, 9)
        c.drawString(box_x + 22, row_y, key)
        c.setFillColorRGB(*C_NAVY)
        c.setFont(_FONT_BOLD, 10)
        c.drawString(box_x + 130, row_y, str(val)[:45])
        row_y -= 22

    _kv('Toplam Kayit:', f'{total_records:,}')
    _kv('Dosya:', filename[:42])
    _kv('Rapor Tarihi:', date.today().strftime('%d.%m.%Y'))
    _kv('Hazırlayan:', 'Analizus Otomatik Analiz')

    if is_demo:
        note_y = box_y - 50
        c.setFillColorRGB(*C_LIGHT)
        c.roundRect(box_x, note_y, 320, 38, 6, fill=1, stroke=0)
        c.setStrokeColorRGB(*C_PURPLE)
        c.setLineWidth(1)
        c.roundRect(box_x, note_y, 320, 38, 6, fill=0, stroke=1)
        c.setFillColorRGB(*C_PURPLE)
        c.setFont(_FONT_BOLD, 9)
        c.drawCentredString(width / 2, note_y + 24, 'Demo: 3 analiz icermektedir.')
        c.setFont(_FONT_NORMAL, 8)
        c.setFillColorRGB(*C_MUTED)
        c.drawCentredString(width / 2, note_y + 10, 'Tam rapor (10 analiz) icin siparis olusturunuz → analizus.com')

    _draw_footer(c, width)


def _draw_figure_page(c, width, height, fig, analysis_title: str, page_num: int, total_pages: int):
    from reportlab.lib.units import cm

    _draw_page_background(c, width, height)
    _draw_header(c, width, height,
                 title=analysis_title,
                 subtitle='Bibliometrik Analiz Raporu — Analizus',
                 page_num=page_num, total_pages=total_pages)
    _draw_footer(c, width)

    img_reader = _fig_to_image_reader(fig)

    # Grafik alanı: header (65) ve footer (40) arasındaki boşluk
    margin = 1.0 * cm
    content_top    = height - 65 - margin
    content_bottom = 40 + margin
    content_width  = width - 2 * margin
    content_height = content_top - content_bottom

    iw, ih = img_reader.getSize()
    ratio  = min(content_width / iw, content_height / ih)
    draw_w = iw * ratio
    draw_h = ih * ratio
    x = margin + (content_width - draw_w) / 2
    y = content_bottom + (content_height - draw_h) / 2

    # Gölge
    c.setFillColorRGB(0.88, 0.90, 0.95)
    c.roundRect(x + 3, y - 3, draw_w, draw_h, 6, fill=1, stroke=0)

    # Grafik
    c.drawImage(img_reader, x, y, width=draw_w, height=draw_h,
                preserveAspectRatio=True)

    # İnce çerçeve
    c.setStrokeColorRGB(*C_BORDER)
    c.setLineWidth(0.5)
    c.roundRect(x, y, draw_w, draw_h, 6, fill=0, stroke=1)


# ── Public API ───────────────────────────────────────────────────

def build_demo_pdf(figures: list, total_records: int = 0, filename: str = '') -> bytes:
    """figures: [(title, Figure), ...]  ilk 3 tanesi kullanılır"""
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
    """figures: [(title, Figure), ...]  tümü kullanılır"""
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
