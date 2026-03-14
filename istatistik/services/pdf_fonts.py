"""ReportLab için Türkçe karakter destekli font kaydı."""
_registered = False


def register_fonts():
    """DejaVu TTF fontlarını ReportLab'a kaydet (bir kez çalışır)."""
    global _registered
    if _registered:
        return
    import os
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont

    font_dir = '/usr/share/fonts/truetype/dejavu'
    regular = os.path.join(font_dir, 'DejaVuSans.ttf')
    bold = os.path.join(font_dir, 'DejaVuSans-Bold.ttf')

    if os.path.exists(regular):
        pdfmetrics.registerFont(TTFont('DejaVuSans', regular))
    if os.path.exists(bold):
        pdfmetrics.registerFont(TTFont('DejaVuSans-Bold', bold))
    if os.path.exists(regular) and os.path.exists(bold):
        pdfmetrics.registerFontFamily('DejaVuSans',
                                      normal='DejaVuSans',
                                      bold='DejaVuSans-Bold')
    _registered = True
