import json
import glob

files = glob.glob("haifuu_logs_*.json")
for file in files:
    with open(file, "r", encoding="utf-8") as f:
        logs = json.load(f)

    updated = False
    for entry in logs:
        if "channel_id" not in entry or not entry["channel_id"]:
            entry["channel_id"] = 1359371138043740401  # デフォルトのチャンネルID（仮）

            updated = True

    if updated:
        with open(file, "w", encoding="utf-8") as f:
            json.dump(logs, f, ensure_ascii=False, indent=2)
        print(f"✅ {file} を更新しました")