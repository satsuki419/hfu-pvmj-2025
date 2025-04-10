import json
import glob
from collections import defaultdict

# ✅ all_logs を読み込む処理を最初に追加！
log_files = sorted(glob.glob("haifuu_logs_2025-*.json"))
all_logs = []
for file in log_files:
    with open(file, "r", encoding="utf-8") as f:
        logs = json.load(f)
        all_logs.extend(logs)


# 🔁 IDごとにエントリを保存
entry_by_id = {entry["id"]: entry for entry in all_logs if "id" in entry}

# 🧵 スレッドの親IDごとにコメントをまとめる
threads = defaultdict(list)

for entry in all_logs:
    parent_id = entry.get("reply_to_id")
    if parent_id:
        # 返信であれば、その親にぶら下げる
        threads[parent_id].append(entry)

# 👑 親とみなすべきエントリを集める（スレッドの起点）
for entry in all_logs:
    if "id" not in entry or entry.get("reply_to_id"):
        continue  # IDがない or リプライならスキップ

    # 親になりうる条件：画像がある or 牌姿がある
    if entry.get("image_url") or entry.get("haishi"):
        threads[entry["id"]]  # 空のスレッドとして確保
# 🔧 親が存在しない場合は、仮の親エントリを作成
for parent_id in threads:
    if parent_id not in entry_by_id:
        entry_by_id[parent_id] = {
            "id": parent_id,
            "comment": "(この投稿は記録されていませんが、返信があります)",
            "reply_author": "不明",
            "timestamp": "不明",
            "image_url": None,
        }


# HTML生成
# 📄 HTML化
html = """
<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<title>はいふぅ スレッドビュー</title>
<style>
body { font-family: sans-serif; padding: 20px; }
.thread { border: 2px solid #ccc; margin-bottom: 25px; padding: 15px; border-radius: 8px; }
.comment { font-weight: bold; white-space: pre-wrap; }
.image-link { display: inline-block; margin: 4px 0; }
.meta { font-size: 0.9em; color: #666; margin-top: 5px; }
.reply { border-top: 1px dashed #aaa; margin-top: 10px; padding-top: 8px; }
</style>
</head>
<body>
<h1>はいふぅ スレッドビュー（まとめ）</h1>
"""

for parent_id, replies in threads.items():
    parent = entry_by_id.get(parent_id)
    if not parent:
        continue  # 親エントリがない場合はスキップ

    html += '<div class="thread">'
    html += f'<div class="comment">{parent.get("comment", "(本文なし)")}</div>'

    if parent.get("image_url"):
        html += f'<a href="{parent["image_url"]}" target="_blank"><img src="{parent["image_url"]}" style="max-width:300px; border:1px solid #ccc; margin-top:5px;"></a>'

    html += f'<div class="meta">🕒 {parent.get("timestamp", "時刻不明")} | by {parent.get("reply_author", "不明")}</div>'

    for reply in replies:
        html += '<div class="reply">'
        html += f'<div class="comment">{reply.get("comment", "(本文なし)")}</div>'
        html += f'<div class="meta">↳ {reply.get("timestamp", "不明")} | by {reply.get("reply_author", "不明")}</div>'
        html += '</div>'

    html += '</div>'

html += "</body></html>"

with open("haifuu_thread_view.html", "w", encoding="utf-8") as f:
    f.write(html)

print("✅ スレッドビュー（haifuu_thread_view.html）を生成しました！")
