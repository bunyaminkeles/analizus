"""Kurumsal eğitim katılım belgesi PDF üretimi.

Not: Bu bir akredite sertifika değildir — yalnızca katılım kaydıdır.
Bu ibare belge üzerinde zorunlu olarak yer alır (bkz. analizus_egitim_prompt.md §Faz 7).
"""
import io


def build_certificate_pdf(training_request) -> bytes:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import cm
    from reportlab.lib.enums import TA_CENTER
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from istatistik.services.pdf_fonts import register_fonts
    register_fonts()

    from .. import training_catalog

    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4,
                             leftMargin=2.5 * cm, rightMargin=2.5 * cm,
                             topMargin=3 * cm, bottomMargin=3 * cm)

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('CertTitle', parent=styles['Heading1'], fontSize=20,
                                  alignment=TA_CENTER, spaceAfter=18, fontName='DejaVuSans-Bold')
    subtitle_style = ParagraphStyle('CertSubtitle', parent=styles['Normal'], fontSize=11,
                                     alignment=TA_CENTER, textColor=colors.grey, spaceAfter=24,
                                     fontName='DejaVuSans')
    name_style = ParagraphStyle('CertName', parent=styles['Heading1'], fontSize=18,
                                 alignment=TA_CENTER, spaceAfter=6, fontName='DejaVuSans-Bold')
    course_style = ParagraphStyle('CertCourse', parent=styles['Heading2'], fontSize=14,
                                   alignment=TA_CENTER, spaceAfter=18, fontName='DejaVuSans')
    normal_center = ParagraphStyle('NormalCenter', parent=styles['Normal'], fontSize=10,
                                    alignment=TA_CENTER, fontName='DejaVuSans')
    disclaimer_style = ParagraphStyle('Disclaimer', parent=styles['Normal'], fontSize=9,
                                       alignment=TA_CENTER, textColor=colors.HexColor('#6b7280'),
                                       fontName='DejaVuSans')

    topic_item = training_catalog.get_item_by_slug(training_request.topic) if training_request.topic else None
    course_title = training_request.other_topic or (topic_item['title'] if topic_item else 'Kurumsal Eğitim Programı')

    story = [
        Spacer(1, 1 * cm),
        Paragraph('KATILIM BELGESİ', title_style),
        Paragraph('ANALIZUS EĞİTİM HİZMETLERİ', subtitle_style),
        Spacer(1, 1 * cm),
        Paragraph(training_request.name, name_style),
        Paragraph(training_request.organization or '', course_style) if training_request.organization else Spacer(1, 0),
        Spacer(1, 0.4 * cm),
        Paragraph('aşağıdaki eğitim programına katılmıştır:', normal_center),
        Spacer(1, 0.3 * cm),
        Paragraph(course_title, course_style),
        Spacer(1, 0.3 * cm),
        Paragraph(f"Tarih: {training_request.created_at.strftime('%d.%m.%Y')}", normal_center),
        Spacer(1, 2 * cm),
    ]

    disclaimer_tbl = Table([[Paragraph(
        'Bu belge katılım kaydıdır, akredite sertifika değildir.',
        disclaimer_style,
    )]], colWidths=[16 * cm])
    disclaimer_tbl.setStyle(TableStyle([
        ('BOX', (0, 0), (-1, -1), 0.75, colors.HexColor('#d1d5db')),
        ('PADDING', (0, 0), (-1, -1), 10),
    ]))
    story.append(disclaimer_tbl)

    doc.build(story)
    return buf.getvalue()
