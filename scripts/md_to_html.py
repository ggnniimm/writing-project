
import markdown
import os

def convert_md_to_html(md_path, html_path):
    with open(md_path, "r", encoding="utf-8") as f:
        md_content = f.read()
        
    html_content = markdown.markdown(md_content)
    
    # Add some basic styling
    final_html = f"""
<!DOCTYPE html>
<html lang="th">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>EP.162(v3): Improper Contract Termination</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f9f9f9;
        }}
        h1 {{
            color: #2c3e50;
            border-bottom: 2px solid #3498db;
            padding-bottom: 10px;
        }}
        h2 {{
            color: #2980b9;
            margin-top: 30px;
        }}
        h3 {{
            color: #34495e;
        }}
        blockquote {{
            background: #ecf0f1;
            border-left: 5px solid #3498db;
            margin: 1.5em 10px;
            padding: 0.5em 10px;
            font-style: italic;
        }}
        strong {{
            color: #e74c3c;
        }}
        hr {{
            border: 0;
            height: 1px;
            background: #bdc3c7;
            margin: 40px 0;
        }}
        .container {{
            background: white;
            padding: 40px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
    </style>
</head>
<body>
    <div class="container">
        {html_content}
    </div>
</body>
</html>
    """
    
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(final_html)
    
    print(f"Successfully converted {md_path} to {html_path}")

if __name__ == "__main__":
    input_file = "articles/learning_from_judgments/ep162v3_medium_improper_termination_o_774_2564.md"
    output_file = "articles/learning_from_judgments/ep162v3_medium_improper_termination_o_774_2564.html"
    convert_md_to_html(input_file, output_file)
