#!/usr/bin/env python3
"""
SuperInstance.AI Business Model PDF Generator
Creates investment-grade PDF from markdown source
"""

import subprocess
import sys
import os

def install_and_generate():
    """Install dependencies and generate PDF"""
    
    # Install required packages
    packages = ['markdown2', 'weasyprint', 'pygments']
    for pkg in packages:
        subprocess.run([sys.executable, '-m', 'pip', 'install', pkg, '-q'], check=False)
    
    # Read markdown content
    md_path = '/home/z/my-project/download/SuperInstance_Business_Model_10out10.md'
    with open(md_path, 'r', encoding='utf-8') as f:
        md_content = f.read()
    
    # Convert markdown to HTML with syntax highlighting
    import markdown2
    
    html_content = markdown2.markdown(
        md_content,
        extras={
            'tables': True,
            'fenced-code-blocks': True,
            'code-friendly': True,
            'cuddled-lists': True,
            'header-ids': True,
            'strike': True,
            'task_list': True,
        }
    )
    
    # Create styled HTML document
    styled_html = f'''
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>SuperInstance.AI Business Model - Investment Grade</title>
    <style>
        @page {{
            size: A4;
            margin: 2cm 2.5cm;
            @top-right {{
                content: "SuperInstance.AI Business Model v10.0";
                font-size: 9pt;
                color: #666;
            }}
            @bottom-center {{
                content: "Page " counter(page) " of " counter(pages);
                font-size: 9pt;
                color: #666;
            }}
        }}
        
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
            font-size: 10pt;
            line-height: 1.5;
            color: #1a1a1a;
        }}
        
        /* Typography */
        h1 {{
            font-size: 22pt;
            font-weight: 700;
            color: #0a0a0a;
            margin: 0.8em 0 0.4em 0;
            padding-bottom: 0.2em;
            border-bottom: 3px solid #0066cc;
            page-break-after: avoid;
        }}
        
        h2 {{
            font-size: 16pt;
            font-weight: 600;
            color: #1a1a1a;
            margin: 0.8em 0 0.4em 0;
            padding-bottom: 0.15em;
            border-bottom: 2px solid #3399ff;
            page-break-after: avoid;
        }}
        
        h3 {{
            font-size: 13pt;
            font-weight: 600;
            color: #2a2a2a;
            margin: 0.6em 0 0.3em 0;
            page-break-after: avoid;
        }}
        
        h4 {{
            font-size: 11pt;
            font-weight: 600;
            color: #3a3a3a;
            margin: 0.5em 0 0.25em 0;
        }}
        
        p {{
            margin: 0.4em 0;
            text-align: justify;
        }}
        
        /* Code blocks and preformatted text */
        pre {{
            font-family: 'SF Mono', 'Consolas', 'Monaco', monospace;
            font-size: 8pt;
            line-height: 1.35;
            background: #f8f9fa;
            border: 1px solid #e1e4e8;
            border-radius: 6px;
            padding: 12px;
            margin: 0.5em 0;
            overflow-wrap: break-word;
            white-space: pre-wrap;
            page-break-inside: avoid;
        }}
        
        code {{
            font-family: 'SF Mono', 'Consolas', 'Monaco', monospace;
            font-size: 9pt;
            background: #f1f3f5;
            padding: 1px 4px;
            border-radius: 3px;
        }}
        
        pre code {{
            background: transparent;
            padding: 0;
        }}
        
        /* Tables */
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 0.5em 0;
            font-size: 9pt;
            page-break-inside: avoid;
        }}
        
        th {{
            background: linear-gradient(180deg, #4a90d9 0%, #2a6db5 100%);
            color: white;
            font-weight: 600;
            padding: 8px 6px;
            text-align: left;
            border: 1px solid #2a6db5;
        }}
        
        td {{
            padding: 6px;
            border: 1px solid #ddd;
            vertical-align: top;
        }}
        
        tr:nth-child(even) {{
            background: #f8f9fa;
        }}
        
        tr:hover {{
            background: #e8f4fd;
        }}
        
        /* Lists */
        ul, ol {{
            margin: 0.3em 0 0.3em 1.5em;
        }}
        
        li {{
            margin: 0.15em 0;
        }}
        
        /* Special formatting */
        strong {{
            font-weight: 600;
            color: #0a0a0a;
        }}
        
        em {{
            font-style: italic;
        }}
        
        /* Blockquotes */
        blockquote {{
            border-left: 4px solid #0066cc;
            margin: 0.5em 0;
            padding: 0.3em 0 0.3em 1em;
            background: #f0f7ff;
            font-style: italic;
        }}
        
        /* Horizontal rules */
        hr {{
            border: none;
            border-top: 1px solid #e1e4e8;
            margin: 1em 0;
        }}
        
        /* Cover page styles */
        .cover {{
            text-align: center;
            padding-top: 3cm;
        }}
        
        .cover h1 {{
            font-size: 28pt;
            border: none;
            color: #0066cc;
        }}
        
        .cover h2 {{
            font-size: 18pt;
            border: none;
            color: #333;
        }}
        
        /* Key metrics highlight boxes */
        .highlight {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 15px;
            border-radius: 8px;
            margin: 0.5em 0;
        }}
        
        /* Print optimizations */
        @media print {{
            body {{
                font-size: 9pt;
            }}
            
            h1 {{
                page-break-before: always;
            }}
            
            h1:first-of-type {{
                page-break-before: avoid;
            }}
            
            table, pre, blockquote {{
                page-break-inside: avoid;
            }}
        }}
        
        /* Investment metrics box */
        .metrics-box {{
            background: #f8f9fa;
            border: 2px solid #0066cc;
            border-radius: 8px;
            padding: 12px;
            margin: 0.5em 0;
        }}
        
        /* ASCII art preservation */
        .ascii-art {{
            font-family: 'Courier New', monospace;
            font-size: 7pt;
            line-height: 1.2;
            white-space: pre;
        }}
    </style>
</head>
<body>
{html_content}
</body>
</html>
'''
    
    # Write HTML file
    html_path = '/home/z/my-project/download/SuperInstance_Business_Model_10out10.html'
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(styled_html)
    
    # Generate PDF using WeasyPrint
    from weasyprint import HTML, CSS
    
    pdf_path = '/home/z/my-project/download/SuperInstance_Business_Model_10out10.pdf'
    
    HTML(string=styled_html).write_pdf(
        pdf_path,
        stylesheets=[CSS(string='''
            @page {
                size: A4;
                margin: 2cm 2.5cm;
            }
        ''')]
    )
    
    print(f"PDF generated successfully: {pdf_path}")
    return pdf_path

if __name__ == "__main__":
    try:
        install_and_generate()
    except Exception as e:
        print(f"Error generating PDF: {e}")
        import traceback
        traceback.print_exc()
