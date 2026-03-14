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
    from reportlab.lib.fonts import addMapping

    font_dir = '/usr/share/fonts/truetype/dejavu'
    regular = os.path.join(font_dir, 'DejaVuSans.ttf')
    bold = os.path.join(font_dir, 'DejaVuSans-Bold.ttf')

    if not os.path.exists(regular):
        # Render veya farklı sistemde farklı path dene
        for candidate in [
            '/usr/share/fonts/dejavu/DejaVuSans.ttf',
            '/usr/share/fonts/TTF/DejaVuSans.ttf',
        ]:
            if os.path.exists(candidate):
                regular = candidate
                bold = candidate.replace('DejaVuSans.ttf', 'DejaVuSans-Bold.ttf')
                break

    if os.path.exists(regular):
        pdfmetrics.registerFont(TTFont('DejaVuSans', regular))
        # addMapping: Paragraph parser'ın kullandığı family lookup
        addMapping('DejaVuSans', 0, 0, 'DejaVuSans')   # normal
        addMapping('DejaVuSans', 0, 1, 'DejaVuSans')   # italic → normal
        if os.path.exists(bold):
            pdfmetrics.registerFont(TTFont('DejaVuSans-Bold', bold))
            addMapping('DejaVuSans', 1, 0, 'DejaVuSans-Bold')   # bold
            addMapping('DejaVuSans', 1, 1, 'DejaVuSans-Bold')   # bold italic

    _registered = True
