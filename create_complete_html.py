"""
Create complete standalone HTML file with all PROJECT_WORKFLOW.md content embedded
"""

import markdown

# Read the markdown file
with open('PROJECT_WORKFLOW.md', 'r', encoding='utf-8') as f:
    md_content = f.read()

# Convert markdown to HTML
html_body = markdown.markdown(
    md_content,
    extensions=['extra', 'fenced_code', 'tables', 'nl2br']
)

# Create complete HTML document
complete_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>HealthWatch AI - Complete Project Workflow</title>
    <style>
        @page {{
            size: A4;
            margin: 2cm;
        }}
        
        @media print {{
            body {{ margin: 0; padding: 0; }}
            .page-break {{ page-break-after: always; }}
            h1, h2, h3 {{ page-break-after: avoid; }}
            pre {{ page-break-inside: avoid; }}
            .print-button {{ display: none; }}
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 210mm;
            margin: 0 auto;
            padding: 20px;
            background: white;
        }}
        
        .cover-page {{
            text-align: center;
            padding: 150px 20px;
            page-break-after: always;
        }}
        
        .cover-title {{
            font-size: 48px;
            color: #1a237e;
            font-weight: bold;
            margin-bottom: 20px;
        }}
        
        .cover-subtitle {{
            font-size: 28px;
            color: #3949ab;
            margin-bottom: 40px;
        }}
        
        .cover-info {{
            font-size: 16px;
            color: #666;
            margin-top: 60px;
        }}
        
        h1 {{
            color: #1a237e;
            font-size: 28px;
            border-bottom: 3px solid #3949ab;
            padding-bottom: 10px;
            margin-top: 40px;
            margin-bottom: 20px;
        }}
        
        h2 {{
            color: #283593;
            font-size: 22px;
            border-bottom: 2px solid #5c6bc0;
            padding-bottom: 8px;
            margin-top: 30px;
            margin-bottom: 15px;
        }}
        
        h3 {{
            color: #3949ab;
            font-size: 18px;
            margin-top: 25px;
            margin-bottom: 12px;
        }}
        
        h4 {{
            color: #5c6bc0;
            font-size: 16px;
            margin-top: 20px;
            margin-bottom: 10px;
        }}
        
        p {{
            margin: 10px 0;
            text-align: justify;
        }}
        
        ul, ol {{
            margin: 15px 0;
            padding-left: 30px;
        }}
        
        li {{
            margin: 8px 0;
        }}
        
        code {{
            background-color: #f5f5f5;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: 'Courier New', monospace;
            font-size: 90%;
            color: #d32f2f;
        }}
        
        pre {{
            background-color: #f5f5f5;
            border: 1px solid #ddd;
            border-left: 4px solid #3949ab;
            padding: 15px;
            overflow-x: auto;
            border-radius: 4px;
            margin: 20px 0;
        }}
        
        pre code {{
            background-color: transparent;
            padding: 0;
            color: #333;
            font-size: 13px;
            line-height: 1.5;
        }}
        
        hr {{
            border: none;
            border-top: 2px solid #9fa8da;
            margin: 30px 0;
        }}
        
        strong {{
            color: #1a237e;
            font-weight: 600;
        }}
        
        table {{
            border-collapse: collapse;
            width: 100%;
            margin: 20px 0;
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
        
        .print-button {{
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 15px 30px;
            background-color: #3949ab;
            color: white;
            border: none;
            border-radius: 5px;
            font-size: 16px;
            cursor: pointer;
            box-shadow: 0 2px 5px rgba(0,0,0,0.2);
            z-index: 1000;
        }}
        
        .print-button:hover {{
            background-color: #283593;
        }}
    </style>
</head>
<body>
    <button class="print-button" onclick="window.print()">📄 Save as PDF</button>
    
    <div class="cover-page">
        <div class="cover-title">🏥 HealthWatch AI</div>
        <div class="cover-subtitle">Complete Project Workflow Documentation</div>
        <div class="cover-info">
            <p><strong>Digital Twin for Hospital Records</strong></p>
            <p>Predictive Healthcare Analytics System</p>
            <p style="margin-top: 40px;">Version 1.0.0</p>
            <p>December 2025</p>
            <p style="margin-top: 40px;">Production Ready</p>
        </div>
    </div>
    
    {html_body}
    
    <div style="margin-top: 60px; padding: 20px; background-color: #e8eaf6; border-radius: 5px;">
        <p style="text-align: center; margin: 0;"><strong>End of Document</strong></p>
        <p style="text-align: center; margin: 10px 0 0 0; font-size: 14px; color: #666;">
            HealthWatch AI - Digital Twin for Hospital Records<br>
            © 2025 | Version 1.0.0
        </p>
    </div>
</body>
</html>
"""

# Write the complete HTML file
with open('HealthWatch_AI_Workflow_Complete.html', 'w', encoding='utf-8') as f:
    f.write(complete_html)

print("✅ Complete HTML file created successfully!")
print("📄 File: HealthWatch_AI_Workflow_Complete.html")
print(f"📊 Content: {len(md_content)} characters from PROJECT_WORKFLOW.md")
print(f"📝 HTML Size: {len(complete_html)} characters")
print("\n🎉 Ready to open and save as PDF!")
print("\nInstructions:")
print("1. Open 'HealthWatch_AI_Workflow_Complete.html' in your browser")
print("2. Click the 'Save as PDF' button (or press Ctrl+P)")
print("3. Save as PDF")
