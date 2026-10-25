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

    # Önce projeye dahil edilmiş font klasörüne bak (Render dahil her ortamda çalışır)
    _here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    bundled_dir = os.path.join(_here, 'fonts')
    regular = os.path.join(bundled_dir, 'DejaVuSans.ttf')
    bold = os.path.join(bundled_dir, 'DejaVuSans-Bold.ttf')

    if not os.path.exists(regular):
        # Sistem fontlarına fallback
        for candidate in [
            '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
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


def append_ai_comment(story, result: dict, style, bg_hex: str, box_color):
    """Varsa result['ai_comment']'i APA kutusunun hemen altına, aynı görsel
    dille (ince üst çizgi, ayrı kutu/ikon/uyarı metni yok) ekler — ekrandaki
    tasarımla tutarlı (bkz. analiz_console.css .ax-ai-comment-box)."""
    comment = result.get('ai_comment')
    if not comment:
        return
    from reportlab.lib import colors
    from reportlab.lib.units import cm
    from reportlab.platypus import Spacer, Table, TableStyle, Paragraph

    line_color = colors.HexColor(box_color) if isinstance(box_color, str) else box_color
    story.append(Spacer(1, 0.25 * cm))
    tbl = Table([[Paragraph(comment, style)]], colWidths=[16 * cm])
    tbl.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor(bg_hex)),
        ('LINEABOVE', (0, 0), (-1, 0), 1, line_color),
        ('PADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(tbl)
