#!/usr/bin/env python3
"""
YouTube → WordPress → MailerLite Automation
Checks for new YouTube videos, matches them to WordPress posts,
and creates draft MailerLite email campaigns.
"""

import os
import json
import hashlib
import requests
from datetime import datetime, timezone
from urllib.parse import urljoin, quote

# ── Config from environment variables ────────────────────────────────────────
YOUTUBE_API_KEY     = os.environ["YOUTUBE_API_KEY"]
YOUTUBE_CHANNEL_ID  = os.environ["YOUTUBE_CHANNEL_ID"]

WP_BASE_URL         = os.environ["WP_BASE_URL"].rstrip("/")   # e.g. https://yourblog.com
WP_USERNAME         = os.environ["WP_USERNAME"]
WP_APP_PASSWORD     = os.environ["WP_APP_PASSWORD"]           # WordPress Application Password

MAILERLITE_API_KEY  = os.environ["MAILERLITE_API_KEY"]
MAILERLITE_GROUP_ID = os.environ["MAILERLITE_GROUP_ID"]       # Subscriber group/list ID
FROM_NAME           = os.environ.get("FROM_NAME", "Your Brand")
FROM_EMAIL          = os.environ.get("FROM_EMAIL", "hello@yourbrand.com")

SEEN_FILE = "seen_videos.json"   # Tracks already-processed video IDs


# ── Helpers ───────────────────────────────────────────────────────────────────

def load_seen_videos():
    if os.path.exists(SEEN_FILE):
        with open(SEEN_FILE) as f:
            return set(json.load(f))
    return set()

def save_seen_videos(seen: set):
    with open(SEEN_FILE, "w") as f:
        json.dump(list(seen), f, indent=2)

def log(msg: str):
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    print(f"[{ts}] {msg}")


# ── Step 1: Fetch latest YouTube videos ──────────────────────────────────────

def get_latest_videos(max_results=5):
    url = "https://www.googleapis.com/youtube/v3/search"
    params = {
        "key": YOUTUBE_API_KEY,
        "channelId": YOUTUBE_CHANNEL_ID,
        "part": "snippet",
        "order": "date",
        "type": "video",
        "maxResults": max_results,
    }
    r = requests.get(url, params=params, timeout=15)
    r.raise_for_status()
    items = r.json().get("items", [])

    videos = []
    for item in items:
        video_id = item["id"]["videoId"]
        snippet  = item["snippet"]
        videos.append({
            "id":          video_id,
            "title":       snippet["title"],
            "description": snippet["description"],
            "published":   snippet["publishedAt"],
            "url":         f"https://www.youtube.com/watch?v={video_id}",
            "thumbnail":   snippet["thumbnails"].get("high", {}).get("url", ""),
        })
    return videos


# ── Step 2: Search WordPress for a matching post ──────────────────────────────

def find_wp_post(video_title: str):
    """Search WordPress REST API for a post matching the video title."""
    search_query = video_title[:60]   # Keep search concise
    url = f"{WP_BASE_URL}/wp-json/wp/v2/posts"
    params = {
        "search":   search_query,
        "per_page": 1,
        "_embed":   1,            # Embeds featured image, author, etc.
    }
    auth = (WP_USERNAME, WP_APP_PASSWORD)
    r = requests.get(url, params=params, auth=auth, timeout=15)
    r.raise_for_status()
    posts = r.json()

    if not posts:
        log(f"  ⚠️  No WordPress post found for: '{video_title}'")
        return None

    post = posts[0]

    # Extract featured image URL
    featured_image = ""
    try:
        media = post["_embedded"]["wp:featuredmedia"][0]
        featured_image = (
            media.get("media_details", {})
                 .get("sizes", {})
                 .get("large", {})
                 .get("source_url")
            or media.get("source_url", "")
        )
    except (KeyError, IndexError):
        pass

    # Extract clean excerpt
    excerpt = post.get("excerpt", {}).get("rendered", "")
    excerpt = excerpt.replace("<p>", "").replace("</p>", "").replace("&#8230;", "…").strip()

    return {
        "title":         post["title"]["rendered"],
        "excerpt":       excerpt,
        "content":       post["content"]["rendered"],
        "url":           post["link"],
        "featured_image": featured_image,
    }


# ── Step 3: Build HTML email body ─────────────────────────────────────────────

def build_email_html(video: dict, wp_post: dict | None) -> str:
    title         = video["title"]
    video_url     = video["url"]
    description   = wp_post["excerpt"]   if wp_post else video["description"][:300] + "…"
    blog_url      = wp_post["url"]       if wp_post else video_url
    hero_image    = wp_post["featured_image"] if (wp_post and wp_post["featured_image"]) else video["thumbnail"]
    read_btn_text = "Read the Full Article" if wp_post else "Watch on YouTube"
    read_btn_url  = blog_url

    hero_img_html = (
        f'<img src="{hero_image}" alt="{title}" style="width:100%;max-width:600px;height:auto;display:block;border-radius:8px 8px 0 0;">'
        if hero_image else ""
    )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title}</title>
</head>
<body style="margin:0;padding:0;background:#f4f4f5;font-family:Georgia,serif;">
  <table width="100%" cellpadding="0" cellspacing="0" style="background:#f4f4f5;padding:40px 0;">
    <tr><td align="center">
      <table width="600" cellpadding="0" cellspacing="0" style="max-width:600px;width:100%;background:#ffffff;border-radius:8px;overflow:hidden;box-shadow:0 2px 12px rgba(0,0,0,0.08);">

        <!-- Hero Image -->
        <tr><td>{hero_img_html}</td></tr>

        <!-- Content -->
        <tr><td style="padding:40px 48px 32px;">
          <h1 style="margin:0 0 16px;font-size:26px;line-height:1.3;color:#111827;font-family:Georgia,serif;">
            {title}
          </h1>
          <p style="margin:0 0 28px;font-size:16px;line-height:1.7;color:#4b5563;font-family:Georgia,serif;">
            {description}
          </p>

          <!-- Primary CTA -->
          <table cellpadding="0" cellspacing="0" style="margin-bottom:16px;">
            <tr>
              <td style="background:#111827;border-radius:6px;">
                <a href="{read_btn_url}"
                   style="display:inline-block;padding:14px 28px;color:#ffffff;text-decoration:none;font-family:Arial,sans-serif;font-size:15px;font-weight:600;letter-spacing:0.3px;">
                  {read_btn_text} →
                </a>
              </td>
            </tr>
          </table>

          <!-- Secondary CTA -->
          <table cellpadding="0" cellspacing="0">
            <tr>
              <td style="background:#ff0000;border-radius:6px;">
                <a href="{video_url}"
                   style="display:inline-block;padding:14px 28px;color:#ffffff;text-decoration:none;font-family:Arial,sans-serif;font-size:15px;font-weight:600;letter-spacing:0.3px;">
                  ▶ Watch on YouTube
                </a>
              </td>
            </tr>
          </table>
        </td></tr>

        <!-- Footer -->
        <tr>
          <td style="padding:24px 48px;border-top:1px solid #f0f0f0;background:#fafafa;">
            <p style="margin:0;font-size:13px;color:#9ca3af;font-family:Arial,sans-serif;text-align:center;">
              You're receiving this because you subscribed to our newsletter.<br>
              <a href="{{{{unsubscribe}}}}" style="color:#9ca3af;">Unsubscribe</a>
            </p>
          </td>
        </tr>

      </table>
    </td></tr>
  </table>
</body>
</html>"""


# ── Step 4: Create MailerLite draft campaign ──────────────────────────────────

def create_mailerlite_campaign(video: dict, html_content: str) -> str:
    today = datetime.now(timezone.utc).strftime("%b %d, %Y")
    campaign_name = f"{video['title']} — {today}"
    subject       = video["title"]

    headers = {
        "Authorization": f"Bearer {MAILERLITE_API_KEY}",
        "Content-Type":  "application/json",
        "Accept":        "application/json",
    }

    # 1. Create the campaign
    payload = {
        "name":     campaign_name,
        "type":     "regular",
        "emails": [{
            "subject":    subject,
            "from_name":  FROM_NAME,
            "from":       FROM_EMAIL,
            "content":    html_content,
        }],
        "groups": [MAILERLITE_GROUP_ID],
    }

    r = requests.post(
        "https://connect.mailerlite.com/api/campaigns",
        headers=headers,
        json=payload,
        timeout=20,
    )

    if r.status_code not in (200, 201):
        raise RuntimeError(f"MailerLite API error {r.status_code}: {r.text}")

    campaign = r.json().get("data", {})
    campaign_id = campaign.get("id", "unknown")
    log(f"  ✅ MailerLite draft campaign created — ID: {campaign_id}")
    return campaign_id


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    log("🚀 Starting YouTube → WordPress → MailerLite routine")

    seen = load_seen_videos()
    videos = get_latest_videos(max_results=5)

    new_count = 0
    for video in videos:
        if video["id"] in seen:
            log(f"  ⏭️  Already processed: {video['title']}")
            continue

        log(f"\n📹 New video found: {video['title']}")
        log(f"   URL: {video['url']}")

        # Step 2 — Find WordPress post
        wp_post = find_wp_post(video["title"])
        if wp_post:
            log(f"  📝 Matched WordPress post: {wp_post['url']}")
        else:
            log(f"  ⚠️  Falling back to YouTube description only")

        # Step 3 — Build email HTML
        html = build_email_html(video, wp_post)

        # Step 4 — Create MailerLite draft
        try:
            campaign_id = create_mailerlite_campaign(video, html)
        except Exception as e:
            log(f"  ❌ Failed to create campaign: {e}")
            continue

        seen.add(video["id"])
        new_count += 1

    save_seen_videos(seen)
    log(f"\n✅ Done — {new_count} new campaign(s) created.")


if __name__ == "__main__":
    main()
