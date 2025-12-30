"""
Enhanced PDF Generator for HealthWatch AI Project Workflow
Converts PROJECT_WORKFLOW.md to professional PDF with proper formatting
"""

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle, Preformatted
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from datetime import datetime
import re

def create_enhanced_pdf(input_md_file, output_pdf_file):
    """
    Convert PROJECT_WORKFLOW.md to professional PDF
    """
    # Create PDF document
    doc = SimpleDocTemplate(
        output_pdf_file,
        pagesize=letter,
        rightMargin=50,
        leftMargin=50,
        topMargin=50,
        bottomMargin=30,
    )
    
    # Container for flowables
    elements = []
    
    # Define styles
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=28,
        textColor=colors.HexColor('#1a237e'),
        spaceAfter=20,
        spaceBefore=10,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    subtitle_style = ParagraphStyle(
        'Subtitle',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.HexColor('#3949ab'),
        spaceAfter=30,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    heading1_style = ParagraphStyle(
        'CustomHeading1',
        parent=styles['Heading1'],
        fontSize=16,
        textColor=colors.HexColor('#283593'),
        spaceAfter=10,
        spaceBefore=15,
        fontName='Helvetica-Bold',
        borderWidth=0,
        borderColor=colors.HexColor('#3949ab'),
        borderPadding=5,
        backColor=colors.HexColor('#e8eaf6')
    )
    
    heading2_style = ParagraphStyle(
        'CustomHeading2',
        parent=styles['Heading2'],
        fontSize=13,
        textColor=colors.HexColor('#3949ab'),
        spaceAfter=8,
        spaceBefore=10,
        fontName='Helvetica-Bold'
    )
    
    heading3_style = ParagraphStyle(
        'CustomHeading3',
        parent=styles['Heading3'],
        fontSize=11,
        textColor=colors.HexColor('#5c6bc0'),
        spaceAfter=6,
        spaceBefore=8,
        fontName='Helvetica-Bold'
    )
    
    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['BodyText'],
        fontSize=10,
        alignment=TA_LEFT,
        spaceAfter=6,
        leading=14
    )
    
    code_style = ParagraphStyle(
        'CodeBlock',
        parent=styles['Code'],
        fontSize=8,
        fontName='Courier',
        leftIndent=20,
        rightIndent=20,
        spaceAfter=10,
        spaceBefore=5,
        backColor=colors.HexColor('#f5f5f5'),
        borderColor=colors.HexColor('#bdbdbd'),
        borderWidth=1,
        borderPadding=8,
        leading=11
    )
    
    bullet_style = ParagraphStyle(
        'Bullet',
        parent=styles['BodyText'],
        fontSize=10,
        leftIndent=20,
        spaceAfter=4,
        bulletIndent=10,
        leading=13
    )
    
    # Read markdown file
    with open(input_md_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Add cover page
    elements.append(Spacer(1, 1.5*inch))
    elements.append(Paragraph("🏥 HealthWatch AI", title_style))
    elements.append(Spacer(1, 0.2*inch))
    elements.append(Paragraph("Complete Project Workflow", subtitle_style))
    elements.append(Spacer(1, 0.3*inch))
    elements.append(Paragraph("Digital Twin for Hospital Records", heading2_style))
    elements.append(Spacer(1, 0.8*inch))
    
    # Metadata table
    metadata = [
        ['Project Name:', 'HealthWatch AI - Digital Twin System'],
        ['Document Type:', 'Complete Project Workflow'],
        ['Version:', '1.0.0'],
        ['Date:', datetime.now().strftime('%B %d, %Y')],
        ['Status:', 'Production Ready']
    ]
    
    metadata_table = Table(metadata, colWidths=[1.5*inch, 4*inch])
    metadata_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e8eaf6')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#c5cae9'))
    ]))
    
    elements.append(metadata_table)
    elements.append(PageBreak())
    
    # Process markdown content
    lines = content.split('\n')
    in_code_block = False
    code_buffer = []
    code_language = ''
    
    i = 0
    while i < len(lines):
        line = lines[i]
        
        # Handle code blocks
        if line.strip().startswith('```'):
            if in_code_block:
                # End of code block
                if code_buffer:
                    code_text = '\n'.join(code_buffer)
                    # Use Preformatted for better code display
                    elements.append(Preformatted(code_text, code_style))
                    elements.append(Spacer(1, 0.1*inch))
                code_buffer = []
                in_code_block = False
                code_language = ''
            else:
                # Start of code block
                in_code_block = True
                code_language = line.strip()[3:].strip()
            i += 1
            continue
        
        if in_code_block:
            code_buffer.append(line)
            i += 1
            continue
        
        # Handle headings
        if line.startswith('# ') and not line.startswith('## '):
            text = line[2:].strip()
            # Remove emojis for cleaner look
            text = re.sub(r'[^\w\s\-&]', '', text)
            elements.append(Spacer(1, 0.15*inch))
            elements.append(Paragraph(text, heading1_style))
        elif line.startswith('## '):
            text = line[3:].strip()
            text = re.sub(r'[^\w\s\-&]', '', text)
            elements.append(Spacer(1, 0.12*inch))
            elements.append(Paragraph(text, heading2_style))
        elif line.startswith('### '):
            text = line[4:].strip()
            text = re.sub(r'[^\w\s\-&]', '', text)
            elements.append(Spacer(1, 0.08*inch))
            elements.append(Paragraph(text, heading3_style))
        elif line.startswith('#### '):
            text = line[5:].strip()
            text = re.sub(r'[^\w\s\-&]', '', text)
            elements.append(Paragraph(f"<b>{text}</b>", body_style))
        
        # Handle horizontal rules
        elif line.strip() == '---':
            elements.append(Spacer(1, 0.05*inch))
            from reportlab.platypus import HRFlowable
            elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#9fa8da')))
            elements.append(Spacer(1, 0.05*inch))
        
        # Handle bullet points
        elif line.strip().startswith('- ') or line.strip().startswith('* '):
            bullet_text = line.strip()[2:]
            # Handle bold text
            bullet_text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', bullet_text)
            # Handle inline code
            bullet_text = re.sub(r'`(.+?)`', r'<font name="Courier" color="#d32f2f">\1</font>', bullet_text)
            elements.append(Paragraph(f'• {bullet_text}', bullet_style))
        
        # Handle numbered lists
        elif line.strip() and len(line.strip()) > 2 and line.strip()[0].isdigit() and '. ' in line[:5]:
            list_text = line.strip()
            list_text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', list_text)
            list_text = re.sub(r'`(.+?)`', r'<font name="Courier" color="#d32f2f">\1</font>', list_text)
            elements.append(Paragraph(list_text, bullet_style))
        
        # Handle regular paragraphs
        elif line.strip():
            para_text = line.strip()
            # Handle bold text
            para_text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', para_text)
            # Handle inline code
            para_text = re.sub(r'`(.+?)`', r'<font name="Courier" color="#d32f2f">\1</font>', para_text)
            # Handle links
            para_text = re.sub(r'\[(.+?)\]\((.+?)\)', r'<u><font color="blue">\1</font></u>', para_text)
            
            elements.append(Paragraph(para_text, body_style))
        else:
            # Empty line - small spacer
            if elements and not isinstance(elements[-1], Spacer):
                elements.append(Spacer(1, 0.05*inch))
        
        i += 1
    
    # Build PDF
    doc.build(elements)
    print(f"\n✅ PDF generated successfully!")
    print(f"📄 File: {output_pdf_file}")
    print(f"📍 Location: {output_pdf_file}")
    print(f"\nThe PDF is ready for download and distribution!")

if __name__ == "__main__":
    # File paths
    input_file = "PROJECT_WORKFLOW.md"
    output_file = "HealthWatch_AI_Complete_Workflow.pdf"
    
    print("🔄 Converting PROJECT_WORKFLOW.md to PDF...")
    print("=" * 60)
    
    # Generate PDF
    create_enhanced_pdf(input_file, output_file)
