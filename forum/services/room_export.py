"""Çalışma odası mesaj dökümü PDF export (Faz 4 — adli makam talebi).

Not: Export'u kim, ne zaman yaptığı forum/models.py RoomExportAuditLog'da
ayrıca kaydedilir (chain of custody); bu modül yalnızca PDF içeriğini üretir.
"""
import io
from xml.sax.saxutils import escape


def build_room_export_pdf(room, posts, exported_by) -> bytes:
    from django.utils import timezone
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import cm
    from reportlab.lib.enums import TA_CENTER
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from istatistik.services.pdf_fonts import register_fonts
    register_fonts()

    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4,
                             leftMargin=1.5 * cm, rightMargin=1.5 * cm,
                             topMargin=2 * cm, bottomMargin=2 * cm)

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('ExportTitle', parent=styles['Heading1'], fontSize=16,
                                  alignment=TA_CENTER, spaceAfter=10, fontName='DejaVuSans-Bold')
    meta_style = ParagraphStyle('ExportMeta', parent=styles['Normal'], fontSize=9,
                                 textColor=colors.HexColor('#4b5563'), fontName='DejaVuSans', spaceAfter=4)
    cell_style = ParagraphStyle('ExportCell', parent=styles['Normal'], fontSize=8.5,
                                 fontName='DejaVuSans', leading=11)
    header_style = ParagraphStyle('ExportCellHead', parent=styles['Normal'], fontSize=8.5,
                                   fontName='DejaVuSans-Bold', textColor=colors.white)

    now = timezone.now()
    story = [
        Paragraph('ÇALIŞMA ODASI MESAJ DÖKÜMÜ', title_style),
        Paragraph(f"<b>Oda:</b> {escape(room.title)} (slug: {escape(room.slug)})", meta_style),
        Paragraph(f"<b>Dışa aktaran:</b> {escape(exported_by.username)}", meta_style),
        Paragraph(f"<b>Dışa aktarma zamanı:</b> {now:%d.%m.%Y %H:%M}", meta_style),
        Paragraph(f"<b>Toplam mesaj sayısı:</b> {posts.count()}", meta_style),
        Spacer(1, 0.6 * cm),
    ]

    rows = [[
        Paragraph('Tarih / Saat', header_style),
        Paragraph('Yazar', header_style),
        Paragraph('Mesaj', header_style),
    ]]
    for post in posts:
        rows.append([
            Paragraph(f"{post.created_at:%d.%m.%Y %H:%M}", cell_style),
            Paragraph(escape(post.author.username), cell_style),
            Paragraph(escape(post.message or ''), cell_style),
        ])

    table = Table(rows, colWidths=[3 * cm, 3 * cm, 11 * cm], repeatRows=1)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f2937')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#d1d5db')),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('PADDING', (0, 0), (-1, -1), 5),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9fafb')]),
    ]))
    story.append(table)

    doc.build(story)
    return buf.getvalue()
