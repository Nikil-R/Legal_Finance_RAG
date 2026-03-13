"""
PDF generation utility for query results.
"""

import io
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle

def generate_query_report(query: str, answer: str, sources: list[dict] = None) -> io.BytesIO:
    """Generates a PDF report for a query result."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=12,
        textColor=colors.HexColor("#1e3a8a")
    )
    
    content = []
    
    # Header
    content.append(Paragraph("LegalFinance AI Research Report", title_style))
    content.append(Paragraph(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
    content.append(Spacer(1, 12))
    
    # Query
    content.append(Paragraph("<b>Question:</b>", styles['Heading3']))
    content.append(Paragraph(query, styles['Normal']))
    content.append(Spacer(1, 12))
    
    # Answer
    content.append(Paragraph("<b>Analysis:</b>", styles['Heading3']))
    # Clean up markdown-ish things for reportlab (very basic)
    answer_clean = answer.replace("**", "<b>").replace("__", "<i>").replace("\n", "<br/>")
    content.append(Paragraph(answer_clean, styles['Normal']))
    content.append(Spacer(1, 18))
    
    # Sources
    if sources:
        content.append(Paragraph("<b>Sources & Citations:</b>", styles['Heading3']))
        for i, src in enumerate(sources, 1):
            source_text = f"{i}. {src.get('source', 'Unknown')} ({src.get('domain', 'N/A')})"
            content.append(Paragraph(source_text, styles['Normal']))
            if src.get('excerpt'):
                excerpt = src['excerpt'][:200] + "..." if len(src['excerpt']) > 200 else src['excerpt']
                content.append(Paragraph(f"<i>Excerpt: {excerpt}</i>", styles['Italic']))
            content.append(Spacer(1, 6))
            
    # Footer
    content.append(Spacer(1, 24))
    content.append(Paragraph("<hr/>", styles['Normal']))
    content.append(Paragraph("<b>Disclaimer:</b> This information is for educational purposes only and should not be considered as professional legal, tax, or financial advice. Please consult qualified professionals for advice specific to your situation.", styles['Small']))
    
    doc.build(content)
    buffer.seek(0)
    return buffer
