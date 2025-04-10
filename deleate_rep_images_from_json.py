import os
import json
import requests

# ✅ スクリプトのあるフォルダを取得
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ファイルパスを絶対パスで指定
INPUT_JSON = os.path.join(BASE_DIR, "haifuu_logs_2025-04.json")
OUTPUT_JSON = os.path.join(BASE_DIR, "haifuu_logs_2025-04_updated.json")
IMAGE_DIR = os.path.join(BASE_DIR, "images")

# フォルダがなければ作成
os.makedirs(IMAGE_DIR, exist_ok=True)

with open(INPUT_JSON, "r", encoding="utf-8") as f:
    logs = json.load(f)

updated = 0

for entry in logs:
    image_url = entry.get("image_url")
    if image_url:
        msg_id = str(entry["id"])
        ext = os.path.splitext(image_url.split("?")[0])[-1] or ".png"
        filename = f"{msg_id}{ext}"
        local_path = os.path.join(IMAGE_DIR, filename)

        if not os.path.exists(local_path):
            try:
                r = requests.get(image_url, timeout=10)
                if r.status_code == 200:
                    with open(local_path, "wb") as img_file:
                        img_file.write(r.content)
                    print(f"✅ 保存: {filename}")
                    # ✅ 成功したときだけ記録する
                    entry["local_image"] = os.path.relpath(local_path, BASE_DIR).replace("\\", "/")
                    updated += 1
                else:
                    print(f"⚠️ ダウンロード失敗: {image_url}")
                    continue
            except Exception as e:
                print(f"❌ エラー: {e}")
                continue
        else:
            # 既に保存済みの場合も記録する
            entry["local_image"] = os.path.relpath(local_path, BASE_DIR).replace("\\", "/")
            updated += 1

with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
    json.dump(logs, f, ensure_ascii=False, indent=2)

print(f"🎉 完了！{updated} 件の画像に local_image を追加しました")
