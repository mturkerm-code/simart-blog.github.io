import os
import glob
import re

def parse_markdown_tables(text):
    """Convert markdown tables to HTML tables."""
    lines = text.split('\n')
    result = []
    i = 0
    while i < len(lines):
        if lines[i].strip().startswith('|') and i + 1 < len(lines) and '---' in lines[i + 1]:
            table_rows = []
            while i < len(lines) and lines[i].strip().startswith('|'):
                table_rows.append(lines[i])
                i += 1
            if len(table_rows) >= 2:
                html_table = ['<table>']
                headers = [c.strip() for c in table_rows[0].split('|')[1:-1]]
                html_table.append('<thead><tr>')
                for h in headers:
                    html_table.append(f'<th>{h}</th>')
                html_table.append('</tr></thead>')
                html_table.append('<tbody>')
                for row in table_rows[2:]:
                    cells = [c.strip() for c in row.split('|')[1:-1]]
                    html_table.append('<tr>')
                    for c in cells:
                        html_table.append(f'<td>{c}</td>')
                    html_table.append('</tr>')
                html_table.append('</tbody>')
                html_table.append('</table>')
                result.append('\n'.join(html_table))
            else:
                result.extend(table_rows)
        else:
            result.append(lines[i])
            i += 1
    return '\n'.join(result)

def markdown_to_html(text):
    """Simple markdown to HTML converter."""
    text = parse_markdown_tables(text)
    lines = text.split('\n')
    new_lines = []
    in_quote = False
    for line in lines:
        if line.strip().startswith('> '):
            if not in_quote:
                new_lines.append('<blockquote>')
                in_quote = True
            new_lines.append(line.strip()[2:])
        else:
            if in_quote:
                new_lines.append('</blockquote>')
                in_quote = False
            new_lines.append(line)
    if in_quote:
        new_lines.append('</blockquote>')
    text = '\n'.join(new_lines)
    text = re.sub(r'^###### (.+)$', r'<h6>\1</h6>', text, flags=re.MULTILINE)
    text = re.sub(r'^##### (.+)$', r'<h5>\1</h5>', text, flags=re.MULTILINE)
    text = re.sub(r'^#### (.+)$', r'<h4>\1</h4>', text, flags=re.MULTILINE)
    text = re.sub(r'^### (.+)$', r'<h3>\1</h3>', text, flags=re.MULTILINE)
    text = re.sub(r'^## (.+)$', r'<h2>\1</h2>', text, flags=re.MULTILINE)
    text = re.sub(r'^# (.+)$', r'<h1>\1</h1>', text, flags=re.MULTILINE)
    text = re.sub(r'\*\*\*(.+?)\*\*\*', r'<strong><em>\1</em></strong>', text)
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'\*(.+?)\*', r'<em>\1</em>', text)
    text = re.sub(r'\[(.+?)\]\((.+?)\)', r'<a href="\2">\1</a>', text)
    text = re.sub(r'`(.+?)`', r'<code>\1</code>', text)
    lines = text.split('\n')
    new_lines = []
    in_ul = False
    in_ol = False
    for line in lines:
        ul_match = re.match(r'^(\s*)[-\*] (.+)$', line)
        ol_match = re.match(r'^(\s*)\d+\. (.+)$', line)
        if ul_match:
            if not in_ul:
                new_lines.append('<ul>')
                in_ul = True
            new_lines.append(f'<li>{ul_match.group(2)}</li>')
        elif ol_match:
            if not in_ol:
                new_lines.append('<ol>')
                in_ol = True
            new_lines.append(f'<li>{ol_match.group(2)}</li>')
        else:
            if in_ul:
                new_lines.append('</ul>')
                in_ul = False
            if in_ol:
                new_lines.append('</ol>')
                in_ol = False
            new_lines.append(line)
    if in_ul:
        new_lines.append('</ul>')
    if in_ol:
        new_lines.append('</ol>')
    text = '\n'.join(new_lines)
    paragraphs = text.split('\n\n')
    new_paragraphs = []
    for p in paragraphs:
        p = p.strip()
        if not p:
            continue
        if p.startswith('<') and not p.startswith('<code>'):
            new_paragraphs.append(p)
        else:
            lines_in_p = p.split('\n')
            if len(lines_in_p) > 1:
                new_paragraphs.append('<p>' + '<br>'.join(lines_in_p) + '</p>')
            else:
                new_paragraphs.append(f'<p>{p}</p>')
    text = '\n\n'.join(new_paragraphs)
    return text

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
posts_dir = os.path.join(SCRIPT_DIR, '_posts')
output_dir = SCRIPT_DIR

template = """<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} | Şımart Teknoloji Blog</title>
    <meta name="description" content="{description}">
    <meta name="keywords" content="{keywords}">
    <meta name="author" content="{author}">
    <meta property="og:title" content="{title}">
    <meta property="og:description" content="{description}">
    <meta property="og:type" content="article">
    <meta property="og:url" content="{canonical_url}">
    <link rel="canonical" href="{canonical_url}">
    <script type="application/ld+json">
    {{"@context":"https://schema.org","@type":"BlogPosting","headline":"{title}","description":"{description}","author":{{"@type":"Organization","name":"{author}"}},"publisher":{{"@type":"Organization","name":"Şımart Teknoloji","logo":{{"@type":"ImageObject","url":"https://simart.me/assets/logo.png"}}}},"datePublished":"{date_iso}","dateModified":"{date_iso}","mainEntityOfPage":{{"@type":"WebPage","@id":"{canonical_url}"}}}}
    </script>
    <style>
        body {{ font-family: 'Segoe UI', Arial, sans-serif; max-width: 850px; margin: 0 auto; padding: 20px; background: #f8f9fa; line-height: 1.7; color: #333; }}
        h1 {{ color: #1a5276; font-size: 2em; margin-bottom: 0.3em; }}
        h2 {{ color: #2874a6; font-size: 1.5em; margin-top: 1.5em; border-bottom: 2px solid #eaf2f8; padding-bottom: 0.3em; }}
        h3 {{ color: #3498db; font-size: 1.2em; margin-top: 1.2em; }}
        .content {{ background: white; padding: 40px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }}
        .meta {{ color: #7f8c8d; font-size: 0.9em; margin-bottom: 30px; padding-bottom: 15px; border-bottom: 1px solid #eee; }}
        a {{ color: #2980b9; text-decoration: none; }}
        a:hover {{ text-decoration: underline; }}
        .back {{ margin-top: 40px; padding-top: 20px; border-top: 2px solid #eee; }}
        footer {{ margin-top: 50px; padding-top: 25px; border-top: 2px solid #eee; color: #7f8c8d; text-align: center; font-size: 0.9em; }}
        table {{ border-collapse: collapse; width: 100%; margin: 20px 0; font-size: 0.95em; }}
        th {{ background: #2874a6; color: white; padding: 12px; text-align: left; font-weight: 600; }}
        td {{ padding: 10px 12px; border-bottom: 1px solid #e0e0e0; }}
        tr:nth-child(even) {{ background: #f8f9fa; }}
        tr:hover {{ background: #eaf2f8; }}
        blockquote {{ border-left: 4px solid #3498db; margin: 20px 0; padding: 15px 20px; background: #f8f9fa; color: #555; font-style: italic; }}
        img {{ max-width: 100%; height: auto; border-radius: 8px; margin: 20px 0; }}
        ul, ol {{ margin: 15px 0; padding-left: 25px; }}
        li {{ margin: 8px 0; }}
        strong {{ color: #1a5276; }}
        code {{ background: #f4f4f4; padding: 2px 6px; border-radius: 4px; font-size: 0.9em; }}
    </style>
</head>
<body>
    <div class="content">
        <div class="meta">{date_display} | {author} | {categories}</div>
        <h1>{title}</h1>
        {content}
        <div class="back"><a href="/">← Ana Sayfaya Dön</a></div>
    </div>
    <footer>
        <p>&copy; 2026 Şımart Teknoloji. Tüm hakları saklıdır.</p>
        <p><a href="https://simart.me">simart.me</a> | <a href="/">Blog</a></p>
    </footer>
</body>
</html>
"""

for md_file in sorted(glob.glob(os.path.join(posts_dir, '*.md'))):
    try:
        with open(md_file, 'r', encoding='utf-8') as f:
            content = f.read()
        if content.startswith('---'):
            parts = content.split('---', 2)
            if len(parts) >= 3:
                front_matter = parts[1]
                body = parts[2]
            else:
                print(f"SKIP: {os.path.basename(md_file)} - invalid front matter")
                continue
        else:
            print(f"SKIP: {os.path.basename(md_file)} - no front matter")
            continue
        title = ""
        date_str = ""
        description = ""
        keywords = ""
        author = "Şımart Teknoloji"
        categories = ""
        for line in front_matter.strip().split('\n'):
            line = line.strip()
            if line.startswith('title:'):
                title = line.split(':', 1)[1].strip().strip('"').strip("'")
            elif line.startswith('date:'):
                date_str = line.split(':', 1)[1].strip()
            elif line.startswith('meta_description:') or line.startswith('description:'):
                description = line.split(':', 1)[1].strip().strip('"').strip("'")
            elif line.startswith('keywords:'):
                keywords = line.split(':', 1)[1].strip().strip('"').strip("'")
            elif line.startswith('author:'):
                author = line.split(':', 1)[1].strip().strip('"').strip("'")
            elif line.startswith('categories:'):
                cats = line.split(':', 1)[1].strip()
                categories = cats.strip('[]').replace(',', ' ·')
        date_match = re.search(r'(\d{4}-\d{2}-\d{2})', date_str)
        if date_match:
            date_iso = date_match.group(1)
            date_display = date_iso
        else:
            date_iso = "2026-05-20"
            date_display = "20 Mayıs 2026"
        basename = os.path.basename(md_file)
        slug = basename[11:].replace('.md', '')
        html_content = markdown_to_html(body)
        canonical_url = f"https://simart-blog.github.io/{slug}.html"
        html = template.format(
            title=title,
            description=description or title,
            keywords=keywords or "robot süpürge, akıllı ev, IoT",
            author=author,
            date_iso=date_iso,
            date_display=date_display,
            categories=categories or "Blog",
            canonical_url=canonical_url,
            content=html_content
        )
        output_file = os.path.join(output_dir, f'{slug}.html')
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html)
        print(f"Generated: {output_file}")
    except Exception as e:
        print(f"ERROR processing {os.path.basename(md_file)}: {e}")
        import traceback
        traceback.print_exc()

print("\nDone! Static site generated.")
