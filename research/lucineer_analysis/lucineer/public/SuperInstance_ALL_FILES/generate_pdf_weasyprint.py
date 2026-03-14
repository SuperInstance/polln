#!/usr/bin/env python3
"""
Generate professional PDF from HTML using WeasyPrint
"""

import subprocess
import os

# Paths
html_path = '/home/z/my-project/download/SuperInstance_Business_Model_10out10_temp.html'
output_pdf = '/home/z/my-project/download/SuperInstance_Business_Model_10out10.pdf'
css_path = '/home/z/my-project/download/business_model_style.css'

# Create professional CSS
css_content = '''
@page {
    size: A4;
    margin: 2cm 2.5cm;
    @top-right {
        content: "SuperInstance.AI Business Model v10.0";
        font-size: 8pt;
        color: #666;
        font-family: Helvetica, Arial, sans-serif;
    }
    @bottom-center {
        content: "Page " counter(page);
        font-size: 8pt;
        color: #666;
        font-family: Helvetica, Arial, sans-serif;
    }
}

@page:first {
    @top-right { content: none; }
}

* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
    font-size: 10pt;
    line-height: 1.5;
    color: #1a1a1a;
}

h1 {
    font-size: 20pt;
    font-weight: 700;
    color: #0a0a0a;
    margin: 0.8em 0 0.4em 0;
    padding-bottom: 0.2em;
    border-bottom: 3px solid #0066cc;
    page-break-after: avoid;
}

h1:first-of-type {
    font-size: 26pt;
    text-align: center;
    border: none;
    color: #0066cc;
    margin-top: 2cm;
}

h2 {
    font-size: 15pt;
    font-weight: 600;
    color: #1a1a1a;
    margin: 0.8em 0 0.4em 0;
    padding-bottom: 0.15em;
    border-bottom: 2px solid #3399ff;
    page-break-after: avoid;
}

h3 {
    font-size: 12pt;
    font-weight: 600;
    color: #2a2a2a;
    margin: 0.6em 0 0.3em 0;
    page-break-after: avoid;
}

h4 {
    font-size: 11pt;
    font-weight: 600;
    color: #3a3a3a;
    margin: 0.5em 0 0.25em 0;
}

p {
    margin: 0.4em 0;
    text-align: justify;
}

pre, code {
    font-family: 'Courier New', Courier, monospace;
    font-size: 8pt;
    line-height: 1.35;
}

pre {
    background: #f8f9fa;
    border: 1px solid #e1e4e8;
    border-radius: 4px;
    padding: 10px;
    margin: 0.5em 0;
    white-space: pre-wrap;
    page-break-inside: avoid;
}

code {
    background: #f1f3f5;
    padding: 1px 4px;
    border-radius: 3px;
}

table {
    width: 100%;
    border-collapse: collapse;
    margin: 0.5em 0;
    font-size: 9pt;
    page-break-inside: avoid;
}

th {
    background: #0066cc;
    color: white;
    font-weight: 600;
    padding: 6px 4px;
    text-align: left;
    border: 1px solid #0055aa;
}

td {
    padding: 5px 4px;
    border: 1px solid #ddd;
    vertical-align: top;
}

tr:nth-child(even) {
    background: #f8f9fa;
}

ul, ol {
    margin: 0.3em 0 0.3em 1.5em;
}

li {
    margin: 0.15em 0;
}

strong {
    font-weight: 600;
    color: #0a0a0a;
}

em {
    font-style: italic;
}

hr {
    border: none;
    border-top: 1px solid #e1e4e8;
    margin: 0.8em 0;
}

blockquote {
    border-left: 4px solid #0066cc;
    margin: 0.5em 0;
    padding: 0.3em 0 0.3em 1em;
    background: #f0f7ff;
}

#TOC {
    background: #f8f9fa;
    border: 1px solid #ddd;
    padding: 15px;
    margin: 1em 0;
    border-radius: 4px;
}

#TOC ul {
    list-style-type: none;
    margin-left: 0;
}

#TOC > ul > li {
    margin: 0.3em 0;
    font-weight: 600;
}

#TOC ul ul {
    margin-left: 1.5em;
    font-weight: normal;
}

.title {
    display: none;
}

@media print {
    h1 {
        page-break-before: always;
    }
    h1:first-of-type {
        page-break-before: avoid;
    }
}
'''

# Write CSS file
with open(css_path, 'w') as f:
    f.write(css_content)

# Generate PDF using weasyprint
cmd = [
    '/home/z/.venv/bin/weasyprint',
    html_path,
    output_pdf,
    '-s', css_path
]

result = subprocess.run(cmd, capture_output=True, text=True)

if os.path.exists(output_pdf):
    file_size = os.path.getsize(output_pdf)
    print(f"SUCCESS: PDF generated at {output_pdf}")
    print(f"File size: {file_size:,} bytes ({file_size/1024:.1f} KB)")
else:
    print(f"ERROR: PDF not generated")
    print(result.stderr)

# Clean up temp HTML
if os.path.exists('/home/z/my-project/download/SuperInstance_Business_Model_10out10_temp.html'):
    os.remove('/home/z/my-project/download/SuperInstance_Business_Model_10out10_temp.html')
