import markdown
import os
import glob

# Premium CSS Template
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="th">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <link href="https://fonts.googleapis.com/css2?family=Sarabun:wght@300;400;500;700&display=swap" rel="stylesheet">
    <style>
        :root {{
            --primary-color: #2c3e50;
            --accent-color: #c0392b;
            --text-color: #333;
            --bg-color: #f8f9fa;
            --paper-color: #ffffff;
        }}
        
        body {{
            font-family: 'Sarabun', sans-serif;
            line-height: 1.8;
            color: var(--text-color);
            background-color: var(--bg-color);
            margin: 0;
            padding: 40px 20px;
        }}

        .container {{
            max-width: 210mm; /* A4 width */
            margin: 0 auto;
            background-color: var(--paper-color);
            padding: 25mm 25mm; /* A4 margins */
            box-shadow: 0 4px 6px rgba(0,0,0,0.05);
            border-radius: 4px;
        }}

        h1 {{
            color: var(--primary-color);
            font-size: 24pt;
            font-weight: 700;
            text-align: center;
            margin-bottom: 2em;
            border-bottom: 2px solid var(--primary-color);
            padding-bottom: 15px;
        }}

        h2 {{
            color: var(--primary-color);
            font-size: 18pt;
            font-weight: 700;
            margin-top: 1.5em;
            border-left: 5px solid var(--primary-color);
            padding-left: 10px;
        }}

        h3 {{
            color: var(--text-color);
            font-size: 16pt;
            font-weight: 700;
            margin-top: 1.2em;
        }}

        p {{
            margin-bottom: 1em;
            text-align: justify;
        }}

        ul, ol {{
            margin-bottom: 1em;
            padding-left: 40px;
        }}

        li {{
            margin-bottom: 0.5em;
        }}

        blockquote {{
            background-color: #f1f8ff;
            border-left: 5px solid #0366d6;
            margin: 1.5em 0;
            padding: 15px 20px;
            font-style: italic;
            color: #555;
        }}

        a {{
            color: var(--accent-color);
            text-decoration: none;
            transition: all 0.2s ease;
        }}

        a:hover {{
            color: #a93226;
            text-decoration: underline;
        }}

        hr {{
            border: 0;
            height: 1px;
            background: #e0e0e0;
            margin: 3em 0;
        }}

        code {{
            background-color: #f6f8fa;
            padding: 0.2em 0.4em;
            border-radius: 3px;
            font-family: monospace;
            font-size: 0.9em;
        }}

        sup {{
            color: var(--accent-color);
            font-weight: bold;
        }}
        
        .footer {{
            margin-top: 50px;
            text-align: center;
            font-size: 0.9em;
            color: #777;
            border-top: 1px solid #ddd;
            padding-top: 20px;
        }}

        @media print {{
            body {{
                background: none;
                padding: 0;
            }}
            .container {{
                box-shadow: none;
                margin: 0;
                padding: 0;
                width: 100%;
                max-width: 100%;
            }}
            a {{
                text-decoration: none;
                color: black;
            }}
            .no-print {{
                display: none;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        {content}
        
        <div class="footer">
            <p>เอกสารฉบับนี้จัดทำขึ้นโดยนายมิ่งศักดิ์ แสงวิไลพร ด้วยระบบ AI Assistant (Antigravity) | ปรับปรุงล่าสุด: {timestamp}</p>
        </div>
    </div>
</body>
</html>
"""

from datetime import datetime

def generate_html():
    # Target directory
    input_dir = "articles"
    output_dir = "articles/html"
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Created directory: {output_dir}")

    # Find all MD files
    md_files = glob.glob(os.path.join(input_dir, "*.md"))
    
    if not md_files:
        print("No markdown files found to convert.")
        return

    print(f"Found {len(md_files)} markdown files. Converting...")
    
    for md_file in md_files:
        filename = os.path.basename(md_file)
        html_filename = filename.replace('.md', '.html')
        output_path = os.path.join(output_dir, html_filename)
        
        print(f"Converting: {filename} -> {html_filename}")
        
        # Read Markdown
        with open(md_file, 'r', encoding='utf-8') as f:
            text = f.read()
            
        # Get Title (assume first line header)
        lines = text.split('\n')
        title = "Document"
        for line in lines:
            if line.startswith('# '):
                title = line.replace('# ', '').strip()
                break
        
        # Convert to HTML
        html_content = markdown.markdown(text, extensions=['tables', 'fenced_code'])
        
        # Fill Template
        final_html = HTML_TEMPLATE.format(
            title=title,
            content=html_content,
            timestamp=datetime.now().strftime("%d/%m/%Y %H:%M")
        )
        
        # Write HTML
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(final_html)
            
    print("✅ HTML generation complete!")

if __name__ == "__main__":
    generate_html()
