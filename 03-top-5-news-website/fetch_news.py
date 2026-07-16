import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

BUCKET_NAME = os.getenv("S3_BUCKET_NAME", "your-bucket-name")
AWS_REGION  = os.getenv("AWS_REGION", "us-east-1")
S3_BASE     = f"https://{BUCKET_NAME}.s3.{AWS_REGION}.amazonaws.com"

# ✅ Top 5 current news (June 25, 2026)
NEWS = [
    {
        "id": 1,
        "title": "Trump has testy meeting with GOP senators",
        "summary": "President Trump met with Republican senators after canceling plans to sign bipartisan housing affordability legislation at the Capitol.",
        "source": "CBS News",
        "image_url": "https://images.unsplash.com/photo-1529107386315-e1a2ed48a620?w=800"
    },
    {
        "id": 2,
        "title": "US-Iran nuclear deal talks continue",
        "summary": "The UN nuclear agency chief says Iran inspections will happen at some point. Senate Republicans blocked Democrats' bid to rein in Trump's war powers in Iran.",
        "source": "CBS News",
        "image_url": "https://images.unsplash.com/photo-1504711434969-e33886168f5c?w=800"
    },
    {
        "id": 3,
        "title": "NY primaries: Mamdani-backed socialists sweep",
        "summary": "New York AG Letitia James expressed disappointment after socialist candidates endorsed by Mayor Zohran Mamdani swept Democratic primaries across the state.",
        "source": "Fox News",
        "image_url": "https://images.unsplash.com/photo-1540910419892-4a36d2c3266c?w=800"
    },
    {
        "id": 4,
        "title": "Ebola outbreak spreading in DR Congo",
        "summary": "An Ebola outbreak is spreading across eastern Democratic Republic of the Congo. Over 1,000 cases confirmed and more than 250 deaths in just over a month.",
        "source": "NPR",
        "image_url": "https://images.unsplash.com/photo-1584308666744-24d5c474f2ae?w=800"
    },
    {
        "id": 5,
        "title": "Europe faces extreme heat wave",
        "summary": "Punishing temperatures hit UK, France, and Spain. France placed 54 departments under red heat wave alert as temperatures soared across Western Europe.",
        "source": "NPR",
        "image_url": "https://images.unsplash.com/photo-1504370805625-d32c54b16100?w=800"
    }
]

def download_image(url, save_path):
    """Downloads an image from URL and saves it locally."""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        with open(save_path, "wb") as f:
            f.write(response.content)
        print(f"  ✅ Image saved: {save_path}")
        return True
    except Exception as e:
        print(f"  ❌ Failed to download image: {e}")
        return False

def generate_html():
    """Generates index.html with image + article layout using S3 URLs."""
    cards_html = ""
    for article in NEWS:
        img_s3_url = f"{S3_BASE}/news/images/article_{article['id']}.jpg"
        cards_html += f"""
        <div class="card">
            <img src="{img_s3_url}" alt="{article['title']}">
            <div class="card-body">
                <span class="source">{article['source']}</span>
                <h2>{article['title']}</h2>
                <p>{article['summary']}</p>
            </div>
        </div>
"""

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Top 5 News Today</title>
  <style>
    * {{ margin: 0; padding: 0; box-sizing: border-box; }}

    body {{
      font-family: 'Georgia', serif;
      background: #f4f4f0;
      color: #222;
    }}

    header {{
      background: #1a1a2e;
      color: white;
      text-align: center;
      padding: 32px 20px 24px;
    }}

    header h1 {{
      font-size: 2.4rem;
      letter-spacing: 1px;
    }}

    header p {{
      margin-top: 6px;
      font-size: 0.95rem;
      color: #aaa;
      font-family: sans-serif;
    }}

    .container {{
      max-width: 780px;
      margin: 40px auto;
      padding: 0 20px;
      display: flex;
      flex-direction: column;
      gap: 48px;
    }}

    .card {{
      background: white;
      border-radius: 10px;
      overflow: hidden;
      box-shadow: 0 4px 20px rgba(0,0,0,0.08);
    }}

    .card img {{
      width: 100%;
      height: 320px;
      object-fit: cover;
      display: block;
    }}

    .card-body {{
      padding: 24px 28px 30px;
    }}

    .source {{
      display: inline-block;
      background: #1a1a2e;
      color: white;
      font-size: 0.72rem;
      font-family: sans-serif;
      letter-spacing: 1.5px;
      text-transform: uppercase;
      padding: 4px 10px;
      border-radius: 4px;
      margin-bottom: 14px;
    }}

    .card-body h2 {{
      font-size: 1.45rem;
      line-height: 1.4;
      margin-bottom: 12px;
      color: #111;
    }}

    .card-body p {{
      font-size: 1rem;
      line-height: 1.75;
      color: #444;
    }}

    footer {{
      text-align: center;
      padding: 32px;
      font-family: sans-serif;
      font-size: 0.82rem;
      color: #999;
    }}
  </style>
</head>
<body>

  <header>
    <h1>📰 Top 5 News Today</h1>
    <p>June 25, 2026 &nbsp;·&nbsp; Hosted on AWS S3</p>
  </header>

  <div class="container">
{cards_html}
  </div>

  <footer>Built with Python · Boto3 · AWS S3</footer>

</body>
</html>"""

    with open("news_data/index.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("✅ index.html generated!")

def fetch_news():
    """Saves news text to JSON, downloads all images, and generates HTML."""
    os.makedirs("news_data/images", exist_ok=True)

    # Save text to JSON
    with open("news_data/articles.json", "w") as f:
        json.dump(NEWS, f, indent=2)
    print("✅ articles.json saved!\n")

    # Download images
    print("📥 Downloading images...")
    for article in NEWS:
        img_filename = f"news_data/images/article_{article['id']}.jpg"
        download_image(article["image_url"], img_filename)

    # Generate HTML page
    print("\n🌐 Generating index.html...")
    generate_html()

    print("\n🎉 All news fetched successfully!")

if __name__ == "__main__":
    fetch_news()