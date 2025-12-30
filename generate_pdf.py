"""
PDF Generator for HealthWatch AI Project Documentation
Converts markdown documentation to professional PDF format
"""

from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle, Image
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from datetime import datetime
import os

def create_pdf(input_md_file, output_pdf_file):
    """
    Convert markdown documentation to PDF
    """
    # Create PDF document
    doc = SimpleDocTemplate(
        output_pdf_file,
        pagesize=letter,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=18,
    )
    
    # Container for the 'Flowable' objects
    elements = []
    
    # Define styles
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1a237e'),
        spaceAfter=30,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    heading1_style = ParagraphStyle(
        'CustomHeading1',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=colors.HexColor('#283593'),
        spaceAfter=12,
        spaceBefore=12,
        fontName='Helvetica-Bold'
    )
    
    heading2_style = ParagraphStyle(
        'CustomHeading2',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#3949ab'),
        spaceAfter=10,
        spaceBefore=10,
        fontName='Helvetica-Bold'
    )
    
    heading3_style = ParagraphStyle(
        'CustomHeading3',
        parent=styles['Heading3'],
        fontSize=12,
        textColor=colors.HexColor('#5c6bc0'),
        spaceAfter=8,
        spaceBefore=8,
        fontName='Helvetica-Bold'
    )
    
    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['BodyText'],
        fontSize=10,
        alignment=TA_JUSTIFY,
        spaceAfter=6,
    )
    
    code_style = ParagraphStyle(
        'Code',
        parent=styles['Code'],
        fontSize=9,
        fontName='Courier',
        backgroundColor=colors.HexColor('#f5f5f5'),
        borderColor=colors.HexColor('#e0e0e0'),
        borderWidth=1,
        borderPadding=5,
    )
    
    # Read markdown file
    with open(input_md_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Add cover page
    elements.append(Spacer(1, 2*inch))
    elements.append(Paragraph("HealthWatch AI", title_style))
    elements.append(Spacer(1, 0.3*inch))
    elements.append(Paragraph("Complete Project Documentation", heading1_style))
    elements.append(Spacer(1, 0.5*inch))
    elements.append(Paragraph("Digital Twin for Hospital Records", heading2_style))
    elements.append(Paragraph("Predictive Healthcare Analytics System", heading2_style))
    elements.append(Spacer(1, 1*inch))
    
    # Add metadata table
    metadata = [
        ['Document Version:', '1.0.0'],
        ['Date:', datetime.now().strftime('%B %d, %Y')],
        ['Project Type:', 'AI/ML Healthcare System'],
        ['Status:', 'Production Ready']
    ]
    
    metadata_table = Table(metadata, colWidths=[2*inch, 3*inch])
    metadata_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e8eaf6')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#c5cae9'))
    ]))
    
    elements.append(metadata_table)
    elements.append(PageBreak())
    
    # Process markdown content
    lines = content.split('\n')
    in_code_block = False
    code_buffer = []
    in_table = False
    table_buffer = []
    
    for line in lines:
        # Skip empty lines at the start
        if not line.strip() and not elements:
            continue
            
        # Handle code blocks
        if line.strip().startswith('```'):
            if in_code_block:
                # End of code block
                if code_buffer:
                    code_text = '<br/>'.join(code_buffer)
                    elements.append(Paragraph(code_text, code_style))
                    elements.append(Spacer(1, 0.1*inch))
                code_buffer = []
                in_code_block = False
            else:
                # Start of code block
                in_code_block = True
            continue
        
        if in_code_block:
            code_buffer.append(line.replace('<', '&lt;').replace('>', '&gt;'))
            continue
        
        # Handle headings
        if line.startswith('# '):
            elements.append(Spacer(1, 0.2*inch))
            elements.append(Paragraph(line[2:], heading1_style))
        elif line.startswith('## '):
            elements.append(Spacer(1, 0.15*inch))
            elements.append(Paragraph(line[3:], heading2_style))
        elif line.startswith('### '):
            elements.append(Spacer(1, 0.1*inch))
            elements.append(Paragraph(line[4:], heading3_style))
        elif line.startswith('#### '):
            elements.append(Paragraph(line[5:], heading3_style))
        
        # Handle horizontal rules
        elif line.strip() == '---':
            elements.append(Spacer(1, 0.1*inch))
            elements.append(Paragraph('<hr/>', body_style))
            elements.append(Spacer(1, 0.1*inch))
        
        # Handle bullet points
        elif line.strip().startswith('- ') or line.strip().startswith('* '):
            bullet_text = line.strip()[2:]
            elements.append(Paragraph(f'• {bullet_text}', body_style))
        
        # Handle numbered lists
        elif line.strip() and line.strip()[0].isdigit() and '. ' in line:
            elements.append(Paragraph(line.strip(), body_style))
        
        # Handle bold text
        elif '**' in line:
            formatted_line = line.replace('**', '<b>').replace('**', '</b>')
            # Fix if odd number of **
            if formatted_line.count('<b>') != formatted_line.count('</b>'):
                formatted_line = line
            elements.append(Paragraph(formatted_line, body_style))
        
        # Handle regular paragraphs
        elif line.strip():
            # Skip table separator lines
            if '|' in line and ('-' in line or line.count('|') > 2):
                if not in_table:
                    in_table = True
                    table_buffer = []
                
                # Skip separator lines
                if set(line.replace('|', '').replace('-', '').strip()) == set():
                    continue
                
                # Parse table row
                cells = [cell.strip() for cell in line.split('|') if cell.strip()]
                table_buffer.append(cells)
            else:
                # End table if we were in one
                if in_table and table_buffer:
                    # Create table
                    t = Table(table_buffer)
                    t.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e8eaf6')),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('FONTSIZE', (0, 0), (-1, -1), 8),
                        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)
                    ]))
                    elements.append(t)
                    elements.append(Spacer(1, 0.1*inch))
                    table_buffer = []
                    in_table = False
                
                # Regular paragraph
                if line.strip():
                    elements.append(Paragraph(line, body_style))
    
    # Build PDF
    doc.build(elements)
    print(f"PDF generated successfully: {output_pdf_file}")

if __name__ == "__main__":
    # File paths
    input_file = "PROJECT_DOCUMENTATION.md"
    output_file = "HealthWatch_AI_Project_Documentation.pdf"
    
    # Generate PDF
    create_pdf(input_file, output_file)
