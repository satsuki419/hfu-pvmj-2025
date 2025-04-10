from datetime import datetime
import json
import glob
import re

def make_links(text):
    text = text.replace("\n", "<br>")
    text = re.sub(r"(https?://\S+)", r'<a href="\1" target="_blank">\1</a>', text)
    return text

# ログ読み込み
log_files = sorted(glob.glob("haifuu_logs_20*.json"))
all_logs = []
for file in log_files:
    with open(file, "r", encoding="utf-8") as f:
        logs = json.load(f)
        all_logs.extend(logs)

# 親投稿（画像あり・reply_to_idなし）を探す
parents = [msg for msg in all_logs if msg["reply_to_id"] is None and msg.get("image_url")]

# HTMLのヘッダーとスタイル
html_output = """
<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8">
  <title>牌譜検討ログ</title>

  <style>
    body {
      font-family: sans-serif;
      line-height: 1.6;
      background-color: #f9f9f9;
      padding: 20px;
    }
    .post {
      background: #fff;
      border: 1px solid #ccc;
      border-radius: 8px;
      padding: 15px;
      margin-bottom: 40px;
      box-shadow: 2px 2px 5px rgba(0,0,0,0.05);
      max-width: 800px;
      margin: 0 auto;
    }
    .post img {
      max-width: 100%;
      height: auto;
      border-radius: 4px;
    }
    .haishi {
      font-weight: bold;
      font-size: 14px;
      margin: 10px 0;
      background: #fffae6;
      padding: 5px;
      border-left: 4px solid #ffa500;
    }
    .comments {
      margin-top: 10px;
      padding-left: 10px;
      border-left: 2px solid #ddd;
    }
    .comment {
      margin-bottom: 12px;
    }
    a {
    color: #0077cc;
    text-decoration: none;
    }

    a:hover {
    text-decoration: underline;
    }

    .tag {
    background: #eef;
    color: #444; /* ←ここがポイント！タグの文字色を落ち着いたグレーに */
    padding: 2px 6px;
    margin-right: 5px;
    border-radius: 4px;
    font-size: 12px;
    }
    .taglist {
     margin: 10px 0;
    }
    .meta {
  font-size: 12px;
  color: #777;
  margin-top: 10px;
}

.meta-item {
  margin-bottom: 2px;
}

hr {
  border: none;
  border-top: 1px dashed #ccc;
  margin: 10px 0;
}
  </style>
</head>
<body>


<h1>牌譜検討まとめ</h1>


<input type="text" id="searchBox" placeholder="キーワード検索..." oninput="filterPostsByText()" style="width: 300px; padding: 5px; margin: 10px 0; font-size: 14px;">
<p id="resultCount" style="font-size: 13px; color: #555;">🔎 全件表示中</p>

"""


# 投稿ごとにHTML化
for parent in parents:
    parent_id = parent["id"]
    replies = [msg for msg in all_logs if msg["reply_to_id"] == parent_id]

    # === 投稿に登場したすべてのタグを収集 ===
    all_tags = set()
    for reply in replies:
        all_tags.update(reply.get("tags", []))

    html_output += '<div class="post">\n'
    # image_url と local_image の両方を見て、local_image を優先
    img_src = parent.get("local_image") or parent.get("image_url")
    html_output += f'  <img src="{img_src}" alt="牌譜画像" onclick="toggleDetails(this)"><br>\n'



    # haishi があれば表示
    if parent.get("haishi"):
        haishi_text = parent["haishi"][0]
        html_output += f'  <div class="haishi">🀄{haishi_text}</div>\n'

    # タグ一覧を表示
    if all_tags:
        html_output += '  <div class="taglist">\n'
        for tag in sorted(all_tags):
            html_output += f'    <span class="tag">#{tag}</span>\n'
        html_output += '  </div>\n'
    
    # 🔽 折りたたみブロックの開始
    html_output += '  <div class="details" style="display: none;">\n'

    # コメント表示（補足なしの本文だけ）
    html_output += '    <div class="comments">\n'
    for reply in sorted(replies, key=lambda x: x["timestamp"]):
        comment_text = reply["comment"]

        body_lines = [
            line for line in comment_text.split("\n")
            if not line.strip().startswith("@")
            and not line.strip().startswith("📌")
            and not re.match(r"https?://", line.strip())
        ]
        comment_body = "<br>".join(body_lines)

        html_output += '      <div class="comment">\n'
        html_output += f'        <div class="body">{make_links(comment_body)}</div>\n'
        html_output += '      </div>\n'
    html_output += '    </div>\n'

    # === 補足情報を投稿末尾にまとめて表示（1つ目の返信から）
    if replies:
        first = replies[0]
        reply_time = datetime.fromisoformat(first["timestamp"].replace("Z", "+00:00"))
        reply_date = reply_time.strftime("%Y-%m-%d")
        urls = first.get("urls", [])
        mentions = [line.strip() for line in first["comment"].split("\n") if line.strip().startswith("@")]
        pinned = [line.strip() for line in first["comment"].split("\n") if line.strip().startswith("📌")]
        combined_line = " ".join(mentions + pinned)

        html_output += '  <div class="meta">\n'
        html_output += '    <hr style="border: none; border-top: 1px dashed #ccc; margin: 10px 0;">\n'
        combined_line = f"投稿日: {reply_date}"
        extra = " ".join(mentions + pinned)
        if extra:
            combined_line += f" {extra}"
        html_output += f'    <div class="meta-item">{combined_line}</div>\n'


        for url_info in urls:
            if isinstance(url_info, dict) and "url" in url_info:
                link = url_info["url"]
                source = url_info.get("source", "")
                
                # 日本語ラベルに変換
                if source == "jantama":
                    label = "雀魂"
                elif source == "naga":
                    label = "NAGA"
                else:
                    label = "リンク"

                html_output += f'    <div class="meta-item"><a href="{link}" target="_blank">🔗 {label}</a></div>\n'
            
            elif isinstance(url_info, str):
                html_output += f'    <div class="meta-item"><a href="{url_info}" target="_blank">{url_info}</a></div>\n'

        html_output += '  </div>\n'
    
    # 🔼 折りたたみブロックの終わり
    html_output += '  </div>\n'

    html_output += '</div>\n\n'

html_output += """
<script>
function toggleDetails(img) {
  const post = img.closest(".post");
  const details = post.querySelector(".details");
  const isHidden = details.style.display === "none";
  details.style.display = isHidden ? "block" : "none";
}

function filterPostsByText() {
  const keyword = document.getElementById("searchBox").value.toLowerCase();
  const posts = document.querySelectorAll(".post");
  let matchCount = 0;

  posts.forEach(post => {
    const text = post.textContent.toLowerCase();
    const isMatch = text.includes(keyword);
    post.style.display = isMatch ? "block" : "none";
    if (isMatch) matchCount++;
  });

  const resultText = keyword
    ? `🔎 ${matchCount}件ヒットしました`
    : "🔎 全件表示中";

  document.getElementById("resultCount").textContent = resultText;
}
</script>
"""

# HTMLフッター
html_output += "</body>\n</html>"

# ファイルに保存
with open("index.html", "w", encoding="utf-8") as f:
    f.write(html_output)

print("✅ HTMLファイルを出力しました: index.html")
