"""Atatürk gönderi sırası.

python3 siradaki.py              -> sıradaki (media_id'si boş ilk) gönderiyi JSON yazdırır; bittiyse {"bitti": true}
python3 siradaki.py siluet       -> sadece silüet (ATPS + silüet kapak) gönderilerinden sıradakini yazdırır
python3 siradaki.py kaydet N ID  -> N. sıradaki gönderinin media_id'sini plan.json'a yazar
"""
import json
import os
import sys

P = os.path.join(os.path.dirname(os.path.abspath(__file__)), "plan.json")
BASE = "https://raw.githubusercontent.com/hkaankirdi/urun-gorselleri/main/ig_ataturk/"

plan = json.load(open(P, encoding="utf-8"))

if len(sys.argv) >= 4 and sys.argv[1] == "kaydet":
    n, mid = int(sys.argv[2]), sys.argv[3]
    for p in plan:
        if p["sira"] == n:
            p["media_id"] = mid
    json.dump(plan, open(P, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"kaydedildi: {n} -> {mid}")
else:
    kalan = [p for p in plan if not p["media_id"]]
    if len(sys.argv) >= 2 and sys.argv[1] == "siluet":
        kalan = [p for p in kalan if p["dosya"].startswith("ATPS") or "siluet" in p["dosya"]]
    if not kalan:
        print(json.dumps({"bitti": True}))
    else:
        p = kalan[0]
        print(json.dumps({"sira": p["sira"], "dosya": p["dosya"], "image_url": BASE + p["dosya"],
                          "caption": p["aciklama"], "kalan": len(kalan)}, ensure_ascii=False))
