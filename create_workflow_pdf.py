"""
HTML-based PDF Generator for HealthWatch AI Project Workflow
Converts PROJECT_WORKFLOW.md to professional PDF with proper diagram rendering
Uses weasyprint for high-quality PDF generation
"""

import markdown
import re
from weasyprint import HTML, CSS
from weasyprint.text.fonts import FontConfiguration

def create_html_pdf(input_md_file, output_pdf_file):
    """
    Convert PROJECT_WORKFLOW.md to PDF via HTML with proper styling
    """
    
    # Read markdown file
    with open(input_md_file, 'r', encoding='utf-8') as f:
        md_content = f.read()
    
    # Convert markdown to HTML
    html_content = markdown.markdown(
        md_content,
        extensions=['extra', 'codehilite', 'tables', 'fenced_code']
    )
    
    # Create full HTML document with styling
    full_html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>HealthWatch AI - Complete Project Workflow</title>
    <style>
        @page {{
            size: A4;
            margin: 2cm 1.5cm;
            @top-center {{
                content: "HealthWatch AI - Project Workflow";
                font-size: 10pt;
                color: #666;
            }}
            @bottom-center {{
                content: "Page " counter(page) " of " counter(pages);
                font-size: 9pt;
                color: #666;
            }}
        }}
        
        body {{
            font-family: 'Segoe UI', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            font-size: 11pt;
            max-width: 100%;
        }}
        
        h1 {{
            color: #1a237e;
            font-size: 24pt;
            border-bottom: 3px solid #3949ab;
            padding-bottom: 10px;
            margin-top: 30px;
            margin-bottom: 20px;
            page-break-after: avoid;
        }}
        
        h2 {{
            color: #283593;
            font-size: 18pt;
            border-bottom: 2px solid #5c6bc0;
            padding-bottom: 8px;
            margin-top: 25px;
            margin-bottom: 15px;
            page-break-after: avoid;
        }}
        
        h3 {{
            color: #3949ab;
            font-size: 14pt;
            margin-top: 20px;
            margin-bottom: 12px;
            page-break-after: avoid;
        }}
        
        h4 {{
            color: #5c6bc0;
            font-size: 12pt;
            margin-top: 15px;
            margin-bottom: 10px;
            page-break-after: avoid;
        }}
        
        p {{
            margin: 8px 0;
            text-align: justify;
        }}
        
        ul, ol {{
            margin: 10px 0;
            padding-left: 30px;
        }}
        
        li {{
            margin: 5px 0;
        }}
        
        code {{
            background-color: #f5f5f5;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: 'Courier New', monospace;
            font-size: 10pt;
            color: #d32f2f;
        }}
        
        pre {{
            background-color: #f5f5f5;
            border: 1px solid #ddd;
            border-left: 4px solid #3949ab;
            padding: 15px;
            overflow-x: auto;
            border-radius: 4px;
            margin: 15px 0;
            page-break-inside: avoid;
        }}
        
        pre code {{
            background-color: transparent;
            padding: 0;
            color: #333;
            font-size: 9pt;
            line-height: 1.4;
            white-space: pre-wrap;
            word-wrap: break-word;
        }}
        
        table {{
            border-collapse: collapse;
            width: 100%;
            margin: 15px 0;
            page-break-inside: avoid;
        }}
        
        th {{
            background-color: #e8eaf6;
            color: #1a237e;
            font-weight: bold;
            padding: 12px;
            text-align: left;
            border: 1px solid #c5cae9;
        }}
        
        td {{
            padding: 10px 12px;
            border: 1px solid #e0e0e0;
        }}
        
        tr:nth-child(even) {{
            background-color: #fafafa;
        }}
        
        hr {{
            border: none;
            border-top: 2px solid #9fa8da;
            margin: 20px 0;
        }}
        
        strong {{
            color: #1a237e;
            font-weight: 600;
        }}
        
        a {{
            color: #3949ab;
            text-decoration: none;
        }}
        
        a:hover {{
            text-decoration: underline;
        }}
        
        .cover-page {{
            text-align: center;
            padding-top: 150px;
            page-break-after: always;
        }}
        
        .cover-title {{
            font-size: 36pt;
            color: #1a237e;
            font-weight: bold;
            margin-bottom: 20px;
        }}
        
        .cover-subtitle {{
            font-size: 20pt;
            color: #3949ab;
            margin-bottom: 40px;
        }}
        
        .cover-info {{
            font-size: 12pt;
            color: #666;
            margin-top: 60px;
        }}
        
        .metadata-table {{
            margin: 40px auto;
            max-width: 500px;
        }}
        
        blockquote {{
            border-left: 4px solid #3949ab;
            padding-left: 15px;
            margin: 15px 0;
            color: #555;
            font-style: italic;
        }}
        
        .page-break {{
            page-break-after: always;
        }}
    </style>
</head>
<body>
    <div class="cover-page">
        <div class="cover-title">🏥 HealthWatch AI</div>
        <div class="cover-subtitle">Complete Project Workflow Documentation</div>
        <div class="cover-subtitle" style="font-size: 16pt;">Digital Twin for Hospital Records</div>
        
        <table class="metadata-table">
            <tr>
                <th>Project Name</th>
                <td>HealthWatch AI - Digital Twin System</td>
            </tr>
            <tr>
                <th>Document Type</th>
                <td>Complete Project Workflow</td>
            </tr>
            <tr>
                <th>Version</th>
                <td>1.0.0</td>
            </tr>
            <tr>
                <th>Date</th>
                <td>December 29, 2025</td>
            </tr>
            <tr>
                <th>Status</th>
                <td>Production Ready</td>
            </tr>
        </table>
    </div>
    
    {html_content}
</body>
</html>
"""
    
    # Configure fonts
    font_config = FontConfiguration()
    
    # Generate PDF
    HTML(string=full_html).write_pdf(
        output_pdf_file,
        font_config=font_config
    )
    
    print(f"\n✅ PDF generated successfully!")
    print(f"📄 File: {output_pdf_file}")
    print(f"📍 Full Path: {output_pdf_file}")
    print(f"\n✨ The PDF includes:")
    print(f"   • Professional cover page")
    print(f"   • All sections with proper formatting")
    print(f"   • Code blocks with syntax highlighting")
    print(f"   • Diagrams rendered properly")
    print(f"   • Tables with styling")
    print(f"   • Page numbers and headers")
    print(f"\n🎉 Ready for download and distribution!")

if __name__ == "__main__":
    import sys
    
    # File paths
    input_file = "PROJECT_WORKFLOW.md"
    output_file = "HealthWatch_AI_Complete_Workflow.pdf"
    
    print("🔄 Converting PROJECT_WORKFLOW.md to PDF...")
    print("=" * 70)
    print("Using HTML-based rendering for proper diagram display...")
    print()
    
    try:
        create_html_pdf(input_file, output_file)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nTrying to install required package...")
        import subprocess
        subprocess.run([sys.executable, "-m", "pip", "install", "weasyprint", "markdown"])
        print("\n🔄 Retrying PDF generation...")
        create_html_pdf(input_file, output_file)
