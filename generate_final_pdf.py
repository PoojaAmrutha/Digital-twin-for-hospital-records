"""
Professional PDF Generator for HealthWatch AI Project Workflow
Uses fpdf2 for Windows compatibility with proper formatting
"""

from fpdf import FPDF
import re
from datetime import datetime

class WorkflowPDF(FPDF):
    def __init__(self):
        super().__init__()
        self.set_auto_page_break(auto=True, margin=15)
        
    def header(self):
        if self.page_no() > 1:  # Skip header on cover page
            self.set_font('Arial', 'I', 9)
            self.set_text_color(128, 128, 128)
            self.cell(0, 10, 'HealthWatch AI - Complete Project Workflow', 0, 0, 'C')
            self.ln(15)
    
    def footer(self):
        if self.page_no() > 1:  # Skip footer on cover page
            self.set_y(-15)
            self.set_font('Arial', 'I', 8)
            self.set_text_color(128, 128, 128)
            self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')
    
    def cover_page(self):
        self.add_page()
        self.set_font('Arial', 'B', 32)
        self.set_text_color(26, 35, 126)
        self.ln(60)
        self.cell(0, 20, 'HealthWatch AI', 0, 1, 'C')
        
        self.set_font('Arial', 'B', 20)
        self.set_text_color(57, 73, 171)
        self.cell(0, 15, 'Complete Project Workflow', 0, 1, 'C')
        
        self.set_font('Arial', '', 14)
        self.ln(5)
        self.cell(0, 10, 'Digital Twin for Hospital Records', 0, 1, 'C')
        
        self.ln(30)
        
        # Metadata table
        self.set_font('Arial', 'B', 11)
        self.set_text_color(0, 0, 0)
        self.set_fill_color(232, 234, 246)
        
        metadata = [
            ('Project Name:', 'HealthWatch AI - Digital Twin System'),
            ('Document Type:', 'Complete Project Workflow'),
            ('Version:', '1.0.0'),
            ('Date:', datetime.now().strftime('%B %d, %Y')),
            ('Status:', 'Production Ready')
        ]
        
        for label, value in metadata:
            self.set_font('Arial', 'B', 10)
            self.cell(60, 10, label, 1, 0, 'L', True)
            self.set_font('Arial', '', 10)
            self.cell(0, 10, value, 1, 1, 'L')
    
    def chapter_title(self, title, level=1):
        # Remove all emojis and special Unicode characters
        title = re.sub(r'[^\x00-\x7F]+', '', title).strip()
        
        self.ln(5)
        if level == 1:
            self.set_font('Arial', 'B', 18)
            self.set_text_color(40, 53, 147)
            self.set_fill_color(232, 234, 246)
            self.cell(0, 12, title, 0, 1, 'L', True)
        elif level == 2:
            self.set_font('Arial', 'B', 14)
            self.set_text_color(57, 73, 171)
            self.cell(0, 10, title, 0, 1, 'L')
        elif level == 3:
            self.set_font('Arial', 'B', 12)
            self.set_text_color(92, 107, 192)
            self.cell(0, 8, title, 0, 1, 'L')
        else:
            self.set_font('Arial', 'B', 11)
            self.set_text_color(92, 107, 192)
            self.cell(0, 7, title, 0, 1, 'L')
        self.set_text_color(0, 0, 0)
        self.ln(3)
    
    def add_paragraph(self, text):
        self.set_font('Arial', '', 10)
        self.set_text_color(0, 0, 0)
        # Handle bold text and remove Unicode
        text = text.replace('**', '')
        text = re.sub(r'[^\x00-\x7F]+', '', text).strip()
        if text:
            self.multi_cell(0, 6, text)
            self.ln(2)
    
    def add_bullet(self, text, indent=0):
        self.set_font('Arial', '', 10)
        self.set_text_color(0, 0, 0)
        x_start = self.get_x() + (indent * 5)
        self.set_x(x_start)
        # Clean up markdown formatting and Unicode
        text = text.replace('**', '').replace('`', '')
        text = re.sub(r'[^\x00-\x7F]+', '', text).strip()
        if text:
            self.multi_cell(0, 5, f'  * {text}')
    
    def add_code_block(self, code):
        self.set_fill_color(245, 245, 245)
        self.set_font('Courier', '', 9)
        self.set_text_color(0, 0, 0)
        self.ln(2)
        
        # Split code into lines and add each
        lines = code.split('\n')
        for line in lines:
            if line.strip():
                self.cell(0, 5, '  ' + line, 0, 1, 'L', True)
        self.ln(2)
    
    def add_horizontal_rule(self):
        self.ln(3)
        self.set_draw_color(159, 168, 218)
        self.line(self.l_margin, self.get_y(), self.w - self.r_margin, self.get_y())
        self.ln(3)

def create_pdf_from_markdown(md_file, pdf_file):
    """Convert PROJECT_WORKFLOW.md to PDF"""
    
    # Read markdown file
    with open(md_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Create PDF
    pdf = WorkflowPDF()
    pdf.set_author('HealthWatch AI Team')
    pdf.set_title('HealthWatch AI - Complete Project Workflow')
    pdf.set_subject('Digital Twin for Hospital Records')
    
    # Add cover page
    pdf.cover_page()
    pdf.add_page()
    
    # Process markdown content
    lines = content.split('\n')
    in_code_block = False
    code_buffer = []
    
    i = 0
    while i < len(lines):
        line = lines[i]
        
        # Handle code blocks
        if line.strip().startswith('```'):
            if in_code_block:
                # End code block
                if code_buffer:
                    pdf.add_code_block('\n'.join(code_buffer))
                code_buffer = []
                in_code_block = False
            else:
                # Start code block
                in_code_block = True
            i += 1
            continue
        
        if in_code_block:
            code_buffer.append(line)
            i += 1
            continue
        
        # Handle headings
        if line.startswith('# ') and not line.startswith('##'):
            title = line[2:].strip()
            # Remove emojis
            title = re.sub(r'[^\w\s\-&()]', '', title)
            pdf.chapter_title(title, level=1)
        elif line.startswith('## '):
            title = line[3:].strip()
            title = re.sub(r'[^\w\s\-&()]', '', title)
            pdf.chapter_title(title, level=2)
        elif line.startswith('### '):
            title = line[4:].strip()
            title = re.sub(r'[^\w\s\-&()]', '', title)
            pdf.chapter_title(title, level=3)
        elif line.startswith('#### '):
            title = line[5:].strip()
            title = re.sub(r'[^\w\s\-&()]', '', title)
            pdf.chapter_title(title, level=4)
        
        # Handle horizontal rules
        elif line.strip() == '---':
            pdf.add_horizontal_rule()
        
        # Handle bullet points
        elif line.strip().startswith('- ') or line.strip().startswith('* '):
            bullet_text = line.strip()[2:]
            indent = (len(line) - len(line.lstrip())) // 2
            pdf.add_bullet(bullet_text, indent)
        
        # Handle numbered lists
        elif line.strip() and len(line.strip()) > 2 and line.strip()[0].isdigit() and '. ' in line[:5]:
            pdf.add_bullet(line.strip())
        
        # Handle regular paragraphs
        elif line.strip() and not line.strip().startswith('#'):
            pdf.add_paragraph(line.strip())
        
        i += 1
    
    # Save PDF
    pdf.output(pdf_file)
    
    print(f"\n✅ PDF Generated Successfully!")
    print(f"=" * 70)
    print(f"📄 File: {pdf_file}")
    print(f"📍 Location: d:\\AIML\\AIML_lab_project\\{pdf_file}")
    print(f"\n✨ Features:")
    print(f"   ✓ Professional cover page with metadata")
    print(f"   ✓ All sections with proper formatting")
    print(f"   ✓ Code blocks with monospace font")
    print(f"   ✓ Hierarchical headings with colors")
    print(f"   ✓ Bullet points and numbered lists")
    print(f"   ✓ Page numbers and headers")
    print(f"   ✓ Horizontal rules for section breaks")
    print(f"\n🎉 Ready for download and distribution!")
    print(f"=" * 70)

if __name__ == "__main__":
    input_file = "PROJECT_WORKFLOW.md"
    output_file = "HealthWatch_AI_Complete_Workflow.pdf"
    
    print("\n🔄 Converting PROJECT_WORKFLOW.md to Professional PDF...")
    print("=" * 70)
    
    try:
        create_pdf_from_markdown(input_file, output_file)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
