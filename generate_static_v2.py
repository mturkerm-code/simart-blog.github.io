import os
import glob
import re

# Read all markdown posts
posts_dir = '/tmp/simart-blog.github.io/_posts'
output_dir = '/tmp/simart-blog.github.io'

# Simple HTML template
template = """<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} | Şımart Teknoloji Blog</title>
    <meta name="description" content="{description}">
    <style>
        body {{ font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; background: #f5f5f5; line-height: 1.6; }}
        h1 {{ color: #2c3e50; }}
        .content {{ background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .meta {{ color: #7f8c8d; font-size: 0.9em; margin-bottom: 20px; }}
        a {{ color: #3498db; }}
        .back {{ margin-top: 30px; padding-top: 20px; border-top: 1px solid #ddd; }}
        footer {{ margin-top: 40px; padding-top: 20px; border-top: 1px solid #ddd; color: #7f8c8d; text-align: center; }}
    </style>
</head>
<body>
    <div class="content">
        <div class="meta">{date} | Şımart Teknoloji</div>
        <h1>{title}</h1>
        {content}
        <div class="back"><a href="/">← Ana Sayfaya Dön</a></div>
    </div>
    <footer>
        <p>&copy; 2026 Şımart Teknoloji. Tüm hakları saklıdır.</p>
        <p><a href="https://simart.me">simart.me</a></p>
    </footer>
</body>
</html>
"""

# Process each post
for md_file in sorted(glob.glob(os.path.join(posts_dir, '*.md'))):
    with open(md_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extract front matter
    if content.startswith('---'):
        parts = content.split('---', 2)
        if len(parts) >= 3:
            front_matter = parts[1]
            body = parts[2]
        else:
            continue
    else:
        continue
    
    # Parse front matter
    title = ""
    date = ""
    description = ""
    
    for line in front_matter.strip().split('\n'):
        if line.startswith('title:'):
            title = line.split(':', 1)[1].strip().strip('"\'')
        elif line.startswith('date:'):
            date_str = line.split(':', 1)[1].strip()
            date_match = re.search(r'(\d{4}-\d{2}-\d{2})', date_str)
            if date_match:
                date = date_match.group(1)
        elif line.startswith('meta_description:') or line.startswith('description:'):
            description = line.split(':', 1)[1].strip().strip('"\'')
    
    # Generate slug from filename
    basename = os.path.basename(md_file)
    slug = basename[11:].replace('.md', '')
    
    # Convert basic markdown to HTML
    html_content = body
    html_content = re.sub(r'^# (.+)$', r'<h1>\1</h1>', html_content, flags=re.MULTILINE)
    html_content = re.sub(r'^## (.+)$', r'<h2>\1</h2>', html_content, flags=re.MULTILINE)
    html_content = re.sub(r'^### (.+)$', r'<h3>\1</h3>', html_content, flags=re.MULTILINE)
    html_content = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html_content)
    html_content = re.sub(r'\[(.+?)\]\((.+?)\)', r'<a href="\2">\1</a>', html_content)
    paragraphs = html_content.split('\n\n')
    new_paragraphs = []
    for p in paragraphs:
        p = p.strip()
        if p and not p.startswith('<') and not p.startswith('|') and not p.startswith('-'):
            new_paragraphs.append(f'<p>{p}</p>')
        else:
            new_paragraphs.append(p)
    html_content = '\n\n'.join(new_paragraphs)
    
    # Generate HTML file using str.replace to avoid brace conflicts
    html = template
    html = html.replace('{title}', title)
    html = html.replace('{description}', description or title)
    html = html.replace('{date}', date)
    html = html.replace('{content}', html_content)
    
    output_file = os.path.join(output_dir, f'{slug}.html')
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"Generated: {output_file}")

print("\nDone! Static site generated.")
