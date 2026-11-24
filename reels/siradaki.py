"""Reels sırası. python3 reels/siradaki.py -> sıradaki reels JSON | kaydet N MEDIA_ID"""
import json, os, sys
P = os.path.join(os.path.dirname(os.path.abspath(__file__)), "plan.json")
BASE = "https://raw.githubusercontent.com/hkaankirdi/urun-gorselleri/main/reels/"
plan = json.load(open(P, encoding="utf-8"))
if len(sys.argv) >= 4 and sys.argv[1] == "kaydet":
    for r in plan:
        if r["sira"] == int(sys.argv[2]):
            r["media_id"] = sys.argv[3]
    json.dump(plan, open(P, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("kaydedildi")
else:
    k = [r for r in plan if not r["media_id"]]
    print(json.dumps({"bitti": True}) if not k else json.dumps({
        "sira": k[0]["sira"], "id": k[0]["id"], "video_url": BASE + k[0]["id"] + ".mp4",
        "cover_url": BASE + k[0]["id"] + "_kapak.jpg", "caption": k[0]["caption"], "kalan": len(k)}, ensure_ascii=False))
