import json

with open("haifuu_logs.json", "r", encoding="utf-8") as f:
    logs = json.load(f)

html = """
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <title>はいふぅログビュー</title>
    <style>
        body { font-family: sans-serif; padding: 20px; }
        .entry { margin-bottom: 20px; padding: 10px; border-bottom: 1px solid #ccc; }
        .comment { font-weight: bold; }
        .image-link { margin: 5px 0; display: block; }
        .meta { color: #555; font-size: 0.9em; }
    </style>
</head>
<body>
<h1>はいふぅ ログビュー</h1>
"""

for entry in logs:
    html += f"""
    <div class="entry">
        <div class="comment">■ {entry["comment"]}</div>
        <a class="image-link" href="{entry["image_url"]}" target="_blank">📷 画像を開く</a>
        <div class="meta">🕒 {entry["timestamp"]}（by {entry["reply_author"]} → {entry["target_author"]}）</div>
    </div>
    """

html += "</body></html>"

with open("haifuu_logs.html", "w", encoding="utf-8") as f:
    f.write(html)

print("✅ HTMLビューを生成しました！ → haifuu_logs.html")
