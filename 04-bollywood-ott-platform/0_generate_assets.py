import os
import requests
from PIL import Image, ImageDraw, ImageFont
import json

# ─────────────────────────────────────────────────────────
# STEP 1 — Paste your S3 URLs below
# You already uploaded videos + posters to S3 bucket
# Just copy each Object URL from S3 console and paste here
# ─────────────────────────────────────────────────────────

VIDEO_URLS = [
    "https://bollywood-ott-2026.s3.us-east-1.amazonaws.com/videos/vidssave.com+stree+2+movie_+comedy+scene+_++Rajkumar+rao_+Shraddha+Kapoor_+Aparshakti+Khurana+%23stree2movie+%23funny+360P.mp4",   # movie1 - Stree 2
    "https://bollywood-ott-2026.s3.us-east-1.amazonaws.com/videos/PUSHPA+2_+_Rappa+Rappa+Scene%F0%9F%A9%B8+-+Pushpa's+Final+Warning+%F0%9F%94%A5%F0%9F%94%A5_+_+Allu+Arjun+_+Movie+Dialogue+Clip.mp4",  # movie2 - Pushpa 2
    "https://bollywood-ott-2026.s3.us-east-1.amazonaws.com/videos/Jawan+Mask+Scene.mp4",  # movie3 - Jawan
    "https://bollywood-ott-2026.s3.us-east-1.amazonaws.com/videos/vidssave.com+Animal_+Arjan+Vailly+Full+Video+(Film+Version)+Ranbir+Kapoor%2C+Sandeep%2CBhupinder+B%2CManan+_+Bhushan+K+1+240P.mp4",  # movie4 - Animal
    "PASTE_YOUR_5TH_VIDEO_S3_URL_HERE",                                                    # movie5 - Dunki
]

POSTER_URLS = [
    "https://bollywood-ott-2026.s3.us-east-1.amazonaws.com/posters/stree+2.jpg",    # poster1 - Stree 2
    "https://bollywood-ott-2026.s3.us-east-1.amazonaws.com/posters/pushpa+2.jpg",   # poster2 - Pushpa 2
    "https://bollywood-ott-2026.s3.us-east-1.amazonaws.com/posters/jawan.jpg",     # poster3 - Jawan
    "https://bollywood-ott-2026.s3.us-east-1.amazonaws.com/posters/animal.jpg",    # poster4 - Animal
    "https://bollywood-ott-2026.s3.us-east-1.amazonaws.com/posters/dunky.jpg",     # poster5 - Dunki
]

# ─────────────────────────────────────────────────────────
# Movie details — update titles/genre/year if needed
# ─────────────────────────────────────────────────────────
MOVIES = [
    {"id":1,"title":"Stree 2","genre":"Horror Comedy","year":2024,"rating":"8.5","video":"movie1.mp4","poster":"poster1.jpg"},
    {"id":2,"title":"Pushpa 2: The Rule","genre":"Action Thriller","year":2024,"rating":"7.9","video":"movie2.mp4","poster":"poster2.jpg"},
    {"id":3,"title":"Jawan","genre":"Action Drama","year":2023,"rating":"7.2","video":"movie3.mp4","poster":"poster3.jpg"},
    {"id":4,"title":"Animal","genre":"Crime Drama","year":2023,"rating":"6.8","video":"movie4.mp4","poster":"poster4.jpg"},
    {"id":5,"title":"Dunki","genre":"Drama Comedy","year":2023,"rating":"6.5","video":"movie5.mp4","poster":"poster5.jpg"},
]

# ─────────────────────────────────────────────────────────
# Poster generation (only used if POSTER_URLS has
# "PASTE_YOUR_..." placeholders — auto-generates instead)
# ─────────────────────────────────────────────────────────
POSTER_DESIGNS = [
    {"color1":"#1a0030","color2":"#6a0dad","accent":"#ff6fff","emoji":"👻","subtitle":"Sarkate Ka Aatank"},
    {"color1":"#1a0a00","color2":"#8b2500","accent":"#ff6600","emoji":"🔥","subtitle":"The Rule"},
    {"color1":"#000d1a","color2":"#003366","accent":"#00aaff","emoji":"⚔️","subtitle":"Prevail or Perish"},
    {"color1":"#0d0000","color2":"#3d0000","accent":"#ff2222","emoji":"🐺","subtitle":"Family. Blood. Revenge."},
    {"color1":"#001a00","color2":"#004d00","accent":"#00ff88","emoji":"✈️","subtitle":"A Journey Home"},
]


def hex_to_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))


def generate_poster(movie, design):
    """Generate a poster image locally when no S3 poster URL is given."""
    W, H = 400, 560
    img = Image.new("RGB", (W, H))
    draw = ImageDraw.Draw(img)

    c1, c2 = hex_to_rgb(design["color1"]), hex_to_rgb(design["color2"])
    for y in range(H):
        t = y / H
        r = int(c1[0]+(c2[0]-c1[0])*t)
        g = int(c1[1]+(c2[1]-c1[1])*t)
        b = int(c1[2]+(c2[2]-c1[2])*t)
        draw.line([(0,y),(W,y)], fill=(r,g,b))

    ac = hex_to_rgb(design["accent"])
    for r_size, alpha in [(200,30),(140,50),(80,80)]:
        overlay = Image.new("RGBA",(W,H),(0,0,0,0))
        od = ImageDraw.Draw(overlay)
        cx, cy = W//2, H//2-40
        od.ellipse([cx-r_size,cy-r_size,cx+r_size,cy+r_size], outline=(*ac,alpha), width=2)
        img = Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")
        draw = ImageDraw.Draw(img)

    try:
        font_big   = ImageFont.truetype("arial.ttf", 80)
        font_title = ImageFont.truetype("arialbd.ttf", 40)
        font_sub   = ImageFont.truetype("arial.ttf", 17)
        font_small = ImageFont.truetype("arial.ttf", 13)
    except Exception:
        font_big = font_title = font_sub = font_small = ImageFont.load_default()

    # Emoji
    try:
        eb = draw.textbbox((0,0), design["emoji"], font=font_big)
        draw.text(((W-(eb[2]-eb[0]))//2, H//2-150), design["emoji"], font=font_big, fill="white")
    except Exception:
        draw.text((W//2-40, H//2-150), design["emoji"], font=font_big, fill="white")

    draw.rectangle([30,H-180,W-30,H-177], fill=ac)

    try:
        tb = draw.textbbox((0,0), movie["title"].upper(), font=font_title)
        draw.text(((W-(tb[2]-tb[0]))//2, H-170), movie["title"].upper(), font=font_title, fill="white")
    except Exception:
        draw.text((20,H-170), movie["title"].upper(), font=font_title, fill="white")

    try:
        sb = draw.textbbox((0,0), design["subtitle"], font=font_sub)
        draw.text(((W-(sb[2]-sb[0]))//2, H-118), design["subtitle"], font=font_sub, fill=ac)
    except Exception:
        draw.text((20,H-118), design["subtitle"], font=font_sub, fill=ac)

    meta = f"{movie['genre']}  ·  {movie['year']}"
    try:
        mb = draw.textbbox((0,0), meta, font=font_small)
        draw.text(((W-(mb[2]-mb[0]))//2, H-85), meta, font=font_small, fill=(180,180,180))
    except Exception:
        draw.text((20,H-85), meta, font=font_small, fill=(180,180,180))

    draw.rectangle([0,H-55,W,H], fill=(0,0,0))
    label = "▶  WATCH NOW"
    try:
        bb = draw.textbbox((0,0), label, font=font_small)
        draw.text(((W-(bb[2]-bb[0]))//2, H-38), label, font=font_small, fill=ac)
    except Exception:
        draw.text((W//2-30,H-38), label, font=font_small, fill=ac)

    img.save(movie["poster"], quality=95)
    print(f"   ✅ Generated: {movie['poster']}")


def build_movie_urls_json():
    """
    Build movie_urls.json directly from S3 URLs.
    No downloading needed — videos and posters stay in S3.
    """
    results = []
    for i, movie in enumerate(MOVIES):
        video_url  = VIDEO_URLS[i]  if i < len(VIDEO_URLS)  else None
        poster_url = POSTER_URLS[i] if i < len(POSTER_URLS) else None

        # Warn if placeholder not replaced
        if video_url and "PASTE_YOUR" in video_url:
            print(f"   ⚠️  movie{i+1} video URL not set — update VIDEO_URLS[{i}]")
            video_url = None
        if poster_url and "PASTE_YOUR" in poster_url:
            print(f"   ⚠️  poster{i+1} URL not set — will auto-generate poster locally")
            poster_url = None

        results.append({
            **movie,
            "video_url":  video_url,
            "poster_url": poster_url,
        })
    return results


def main():
    print("=" * 55)
    print("  🎨  BollywoodOTT — Preparing Assets")
    print("=" * 55)

    results = build_movie_urls_json()

    # Generate posters locally only for movies with no poster URL
    needs_poster = [r for r in results if not r["poster_url"]]
    if needs_poster:
        print(f"\n🖼️  Auto-generating {len(needs_poster)} poster(s)...")
        for r in needs_poster:
            idx = r["id"] - 1
            generate_poster(r, POSTER_DESIGNS[idx])
            # Use local filename as fallback — upload_to_s3 will push it
            r["poster_url"] = f"posters/{r['poster']}"

    # Save final URLs
    with open("movie_urls.json", "w") as f:
        json.dump(results, f, indent=2)

    print("\n✅  movie_urls.json saved!")
    print("\n📋  Summary:")
    for r in results:
        v = "✅ S3 URL set" if r["video_url"]  else "❌ Missing"
        p = "✅ S3 URL set" if r["poster_url"] else "❌ Missing"
        print(f"   [{r['id']}] {r['title']:20s}  video={v}  poster={p}")

    print("\n" + "=" * 55)
    print("  🎉  Done! Next steps:")
    print("  1️⃣   python 1_upload_to_s3.py   ← (uploads local posters if any)")
    print("  2️⃣   python 2_generate_html.py")
    print("  3️⃣   python 5_redeploy.py")
    print("=" * 55)


if __name__ == "__main__":
    main()