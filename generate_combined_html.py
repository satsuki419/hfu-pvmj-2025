import json
import glob
import re

def make_links(text):
    # 改行を <br> に、URL をリンクに
    text = text.replace("\n", "<br>")
    text = re.sub(r"(https?://\S+)", r'<a href="\1" target="_blank">\1</a>', text)
    return text

log_files = sorted(glob.glob("haifuu_logs_20*.json"))

all_logs = []
for file in log_files:
    with open(file, "r", encoding="utf-8") as f:
        logs = json.load(f)
        all_logs.extend(logs)

# HTMLベース
html = """
<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<title>はいふぅ ログビュー（まとめ）</title>
<style>
body { font-family: sans-serif; padding: 20px; background: #f9f9f9; }
.entry { border-bottom: 1px solid #ccc; margin-bottom: 15px; padding: 10px; background: #fff; border-radius: 8px; }
.comment { font-weight: normal; margin: 8px 0; white-space: pre-wrap; }
img.thumb { max-height: 120px; border: 1px solid #ccc; border-radius: 4px; }
.meta { font-size: 0.85em; color: #666; }
</style>
</head>
<body>
<h1>はいふぅ ログビュー（まとめ）</h1>
<input type="text" id="search" placeholder="キーワードで検索..." style="width:100%; padding:8px; margin-bottom:20px;">
<div id="log-entries">
"""

# HTMLの中身
for entry in all_logs:
    comment_html = make_links(entry["comment"])
    img_tag = f'<img src="{entry["image_url"]}" class="thumb">' if entry.get("image_url") else ""

    html += f"""
    <div class="entry">
        {img_tag}
        <div class="comment">{comment_html}</div>
        <div class="meta">🕒 {entry["timestamp"]} | {entry['reply_author']} → {entry['target_author']}</div>
    </div>
    """

# JSで検索機能
html += """
</div>
<script>
const searchInput = document.getElementById("search");
searchInput.addEventListener("input", function() {
    const keyword = this.value.toLowerCase();
    const entries = document.querySelectorAll(".entry");
    entries.forEach(entry => {
        const text = entry.textContent.toLowerCase();
        entry.style.display = text.includes(keyword) ? "" : "none";
    });
});
</script>
</body>
</html>
"""

# 保存
with open("haifuu_combined_logs.html", "w", encoding="utf-8") as f:
    f.write(html)

print("✅ まとめビューを生成しました → haifuu_combined_logs.html")
