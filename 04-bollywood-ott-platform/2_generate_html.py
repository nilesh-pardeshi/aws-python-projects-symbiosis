import json
import os

# Reads movie_urls.json (created by script 1) and builds website/index.html

def build_html(movies):

    # Build movie cards
    cards = ""
    for m in movies:
        video_url  = m.get("video_url")  or "#"
        poster_url = m.get("poster_url") or ""
        title      = m["title"]
        genre      = m["genre"]
        year       = m["year"]
        rating     = m["rating"]
        mid        = m["id"]

        cards += f"""
        <div class="card" id="card-{mid}">

          <!-- Poster with overlay play button -->
          <div class="poster-wrap" onclick="playVideo({mid})">
            <img class="poster" src="{poster_url}"
                 alt="{title}"
                 onerror="this.src='https://via.placeholder.com/400x560/1a1a2e/e50914?text={title.replace(' ', '+')}'" />
            <div class="poster-overlay">
              <div class="play-icon">
                <svg viewBox="0 0 60 60" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <circle cx="30" cy="30" r="29" stroke="white" stroke-width="2" fill="rgba(0,0,0,0.5)"/>
                  <polygon points="24,18 46,30 24,42" fill="white"/>
                </svg>
              </div>
            </div>
            <div class="card-badge">HD</div>
            <div class="card-rating">⭐ {rating}</div>
          </div>

          <!-- Info below poster -->
          <div class="card-info">
            <h3 class="card-title">{title}</h3>
            <p class="card-meta">{genre} &nbsp;·&nbsp; {year}</p>
          </div>

          <!-- Video player (hidden until play clicked) -->
          <div class="video-wrap" id="video-wrap-{mid}" style="display:none;">
            <video id="vid-{mid}" controls autoplay
                   poster="{poster_url}"
                   style="width:100%; border-radius:0 0 12px 12px; background:#000;">
              <source src="{video_url}" type="video/mp4">
              Your browser does not support video.
            </video>
            <button class="close-btn" onclick="closeVideo({mid})">✕ Close</button>
          </div>

        </div>
"""

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>BollywoodOTT — Stream Bollywood</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link href="https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
  <style>

    /* ── RESET & BASE ── */
    *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}

    body {{
      background: #0a0a0f;
      color: #e8e8e8;
      font-family: 'Inter', sans-serif;
      min-height: 100vh;
      overflow-x: hidden;
    }}

    /* ── NAVBAR ── */
    nav {{
      position: sticky;
      top: 0;
      z-index: 100;
      background: linear-gradient(180deg, #000 0%, transparent 100%);
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 16px 40px;
      backdrop-filter: blur(8px);
      border-bottom: 1px solid rgba(229,9,20,0.15);
    }}

    .logo {{
      font-family: 'Bebas Neue', cursive;
      font-size: 2rem;
      letter-spacing: 3px;
      color: #e50914;
      text-shadow: 0 0 30px rgba(229,9,20,0.6);
    }}

    .logo span {{ color: #fff; }}

    nav ul {{
      display: flex;
      gap: 28px;
      list-style: none;
    }}

    nav ul li a {{
      color: #ccc;
      text-decoration: none;
      font-size: 0.88rem;
      font-weight: 500;
      letter-spacing: 0.5px;
      transition: color 0.2s;
    }}

    nav ul li a:hover {{ color: #e50914; }}

    /* ── HERO BANNER ── */
    .hero {{
      position: relative;
      height: 420px;
      background: linear-gradient(135deg, #0a0a0f 0%, #1a0a0a 40%, #2d0000 100%);
      display: flex;
      align-items: center;
      padding: 0 60px;
      overflow: hidden;
      margin-bottom: 10px;
    }}

    .hero::before {{
      content: '';
      position: absolute;
      inset: 0;
      background:
        radial-gradient(ellipse at 70% 50%, rgba(229,9,20,0.12) 0%, transparent 60%),
        radial-gradient(ellipse at 30% 80%, rgba(255,100,0,0.07) 0%, transparent 50%);
    }}

    .hero-text {{ position: relative; z-index: 2; max-width: 580px; }}

    .hero-eyebrow {{
      font-size: 0.75rem;
      letter-spacing: 3px;
      text-transform: uppercase;
      color: #e50914;
      margin-bottom: 14px;
      font-weight: 600;
    }}

    .hero-title {{
      font-family: 'Bebas Neue', cursive;
      font-size: 4.5rem;
      line-height: 1;
      color: #fff;
      letter-spacing: 2px;
      text-shadow: 0 2px 40px rgba(0,0,0,0.8);
    }}

    .hero-title em {{
      color: #e50914;
      font-style: normal;
    }}

    .hero-sub {{
      margin-top: 16px;
      font-size: 1rem;
      color: #999;
      font-weight: 300;
      line-height: 1.6;
    }}

    .hero-glow {{
      position: absolute;
      right: -80px;
      top: 50%;
      transform: translateY(-50%);
      width: 500px;
      height: 500px;
      background: radial-gradient(circle, rgba(229,9,20,0.15) 0%, transparent 65%);
      border-radius: 50%;
    }}

    /* ── SECTION HEADER ── */
    .section-header {{
      padding: 32px 40px 16px;
      display: flex;
      align-items: center;
      gap: 14px;
    }}

    .section-header h2 {{
      font-size: 1.3rem;
      font-weight: 700;
      color: #fff;
      letter-spacing: 0.3px;
    }}

    .section-header .line {{
      flex: 1;
      height: 1px;
      background: linear-gradient(90deg, rgba(229,9,20,0.4), transparent);
    }}

    .section-header .badge {{
      background: #e50914;
      color: #fff;
      font-size: 0.7rem;
      font-weight: 700;
      padding: 3px 10px;
      border-radius: 4px;
      letter-spacing: 1px;
      text-transform: uppercase;
    }}

    /* ── MOVIE GRID ── */
    .grid {{
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
      gap: 24px;
      padding: 0 40px 60px;
    }}

    /* ── CARD ── */
    .card {{
      border-radius: 12px;
      overflow: hidden;
      background: #111118;
      transition: transform 0.3s ease, box-shadow 0.3s ease;
      cursor: pointer;
      border: 1px solid rgba(255,255,255,0.05);
    }}

    .card:hover {{
      transform: translateY(-6px) scale(1.02);
      box-shadow: 0 20px 60px rgba(229,9,20,0.25);
      border-color: rgba(229,9,20,0.3);
    }}

    /* ── POSTER ── */
    .poster-wrap {{
      position: relative;
      aspect-ratio: 2/3;
      overflow: hidden;
    }}

    .poster {{
      width: 100%;
      height: 100%;
      object-fit: cover;
      display: block;
      transition: transform 0.4s ease;
    }}

    .card:hover .poster {{ transform: scale(1.05); }}

    /* hover overlay */
    .poster-overlay {{
      position: absolute;
      inset: 0;
      background: rgba(0,0,0,0);
      display: flex;
      align-items: center;
      justify-content: center;
      transition: background 0.3s;
    }}

    .card:hover .poster-overlay {{ background: rgba(0,0,0,0.45); }}

    .play-icon {{
      width: 64px;
      height: 64px;
      opacity: 0;
      transform: scale(0.7);
      transition: opacity 0.3s, transform 0.3s;
    }}

    .card:hover .play-icon {{
      opacity: 1;
      transform: scale(1);
    }}

    /* corner badges */
    .card-badge {{
      position: absolute;
      top: 10px;
      left: 10px;
      background: #e50914;
      color: #fff;
      font-size: 0.65rem;
      font-weight: 700;
      padding: 2px 7px;
      border-radius: 4px;
      letter-spacing: 1px;
    }}

    .card-rating {{
      position: absolute;
      top: 10px;
      right: 10px;
      background: rgba(0,0,0,0.75);
      color: #ffd700;
      font-size: 0.75rem;
      font-weight: 600;
      padding: 2px 8px;
      border-radius: 4px;
      backdrop-filter: blur(4px);
    }}

    /* ── CARD INFO ── */
    .card-info {{
      padding: 14px 14px 16px;
    }}

    .card-title {{
      font-size: 0.95rem;
      font-weight: 700;
      color: #fff;
      margin-bottom: 5px;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }}

    .card-meta {{
      font-size: 0.78rem;
      color: #777;
      font-weight: 400;
    }}

    /* ── VIDEO PLAYER ── */
    .video-wrap {{
      background: #000;
      position: relative;
    }}

    .close-btn {{
      display: block;
      width: 100%;
      background: #1a1a1a;
      color: #aaa;
      border: none;
      padding: 10px;
      font-size: 0.82rem;
      cursor: pointer;
      font-family: 'Inter', sans-serif;
      transition: background 0.2s, color 0.2s;
    }}

    .close-btn:hover {{ background: #e50914; color: #fff; }}

    /* ── FOOTER ── */
    footer {{
      text-align: center;
      padding: 30px 20px;
      color: #333;
      font-size: 0.8rem;
      border-top: 1px solid #1a1a1a;
      letter-spacing: 0.5px;
    }}

    footer span {{ color: #e50914; }}

    /* ── RESPONSIVE ── */
    @media (max-width: 600px) {{
      nav {{ padding: 14px 20px; }}
      nav ul {{ display: none; }}
      .hero {{ padding: 0 24px; height: 280px; }}
      .hero-title {{ font-size: 2.8rem; }}
      .grid {{ padding: 0 16px 40px; gap: 14px; grid-template-columns: repeat(2, 1fr); }}
      .section-header {{ padding: 20px 16px 10px; }}
    }}

  </style>
</head>
<body>

  <!-- NAVBAR -->
  <nav>
    <div class="logo">Bollywood<span>OTT</span></div>
    <ul>
      <li><a href="#">Home</a></li>
      <li><a href="#">Movies</a></li>
      <li><a href="#">Trending</a></li>
      <li><a href="#">New Releases</a></li>
    </ul>
  </nav>

  <!-- HERO -->
  <div class="hero">
    <div class="hero-text">
      <p class="hero-eyebrow">🔴 Now Streaming</p>
      <h1 class="hero-title">Stream <em>Bollywood</em><br>Like Never Before</h1>
      <p class="hero-sub">Top 5 blockbuster clips — hosted on AWS S3, streamed directly in your browser. No buffering. No sign-up.</p>
    </div>
    <div class="hero-glow"></div>
  </div>

  <!-- SECTION HEADER -->
  <div class="section-header">
    <span class="badge">Trending</span>
    <h2>Top Bollywood Hits</h2>
    <div class="line"></div>
  </div>

  <!-- MOVIE GRID -->
  <div class="grid">
{cards}
  </div>

  <!-- FOOTER -->
  <footer>
    Built with <span>♥</span> using Python · AWS S3 · EC2 · Boto3 &nbsp;·&nbsp; BollywoodOTT 2026
  </footer>

  <script>
    // Play video inline inside the card
    function playVideo(id) {{
      // hide any other open players
      document.querySelectorAll('.video-wrap').forEach(el => {{
        if (el.id !== 'video-wrap-' + id) {{
          el.style.display = 'none';
          const v = el.querySelector('video');
          if (v) v.pause();
        }}
      }});

      const wrap = document.getElementById('video-wrap-' + id);
      wrap.style.display = 'block';
      wrap.querySelector('video').play();

      // scroll card into view
      document.getElementById('card-' + id).scrollIntoView({{behavior:'smooth', block:'center'}});
    }}

    function closeVideo(id) {{
      const wrap = document.getElementById('video-wrap-' + id);
      wrap.querySelector('video').pause();
      wrap.style.display = 'none';
    }}
  </script>

</body>
</html>
"""
    return html


def main():
    print("=" * 55)
    print("  🌐  BollywoodOTT — Generating index.html")
    print("=" * 55)

    if not os.path.exists("movie_urls.json"):
        print("❌  movie_urls.json not found!")
        print("   Run  python 1_upload_to_s3.py  first.")
        return

    with open("movie_urls.json") as f:
        movies = json.load(f)

    os.makedirs("website", exist_ok=True)
    html = build_html(movies)

    with open("website/index.html", "w", encoding="utf-8") as f:
        f.write(html)

    print("✅  website/index.html created!")
    print("👉  Run next:  python 3_launch_ec2.py")
    print("=" * 55)


if __name__ == "__main__":
    main()