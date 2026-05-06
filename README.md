# 📺 YouTube → WordPress → MailerLite Automation

Automatically creates a **draft MailerLite email campaign** every time a new video is uploaded to your YouTube channel — pulling in the matching WordPress blog post title, excerpt, featured image, and URL.

Runs entirely on **GitHub Actions** (free, no server needed).

---

## ✅ What It Does

1. **Checks your YouTube channel** for new videos (runs every hour)
2. **Searches your WordPress site** for a matching blog post by title
3. **Builds a polished HTML email** with:
   - Featured image from WordPress (or YouTube thumbnail as fallback)
   - Video title as the subject line
   - Blog excerpt as the body
   - "Read the Full Article" button → WordPress post URL
   - "Watch on YouTube" button → YouTube video URL
4. **Creates a draft campaign in MailerLite** — ready for you to review and send
5. **Saves processed video IDs** so it never creates duplicate campaigns

---

## 🚀 Setup Guide

### Step 1 — Fork / Clone this Repo

```bash
git clone https://github.com/YOUR_USERNAME/youtube-to-mailerlite.git
cd youtube-to-mailerlite
```

Or click **"Use this template"** on GitHub.

---

### Step 2 — Get Your API Keys

#### YouTube Data API v3
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project → Enable **YouTube Data API v3**
3. Create an **API Key** under Credentials
4. Find your Channel ID: go to your YouTube channel → View Page Source → search `channelId`

#### WordPress Application Password
1. In your WordPress dashboard → **Users → Profile**
2. Scroll to **Application Passwords**
3. Enter a name (e.g. `GitHub Actions`) → click **Add New**
4. Copy the generated password (shown only once)

#### MailerLite API Key
1. In MailerLite → **Integrations → Developer API**
2. Generate a new API token
3. Find your **Group ID**: Go to **Subscribers → Groups** → click your group → copy the ID from the URL

---

### Step 3 — Add GitHub Secrets

In your GitHub repo → **Settings → Secrets and variables → Actions → New repository secret**

Add all of these:

| Secret Name | Value |
|---|---|
| `YOUTUBE_API_KEY` | Your YouTube Data API key |
| `YOUTUBE_CHANNEL_ID` | e.g. `UCxxxxxxxxxxxxxxxxxxxxxx` |
| `WP_BASE_URL` | e.g. `https://yourblog.com` |
| `WP_USERNAME` | Your WordPress username |
| `WP_APP_PASSWORD` | The Application Password you generated |
| `MAILERLITE_API_KEY` | Your MailerLite API token |
| `MAILERLITE_GROUP_ID` | Your subscriber group ID (number) |
| `FROM_NAME` | e.g. `Jane at Your Brand` |
| `FROM_EMAIL` | e.g. `hello@yourbrand.com` |

---

### Step 4 — Push & Enable Actions

```bash
git add .
git commit -m "Initial setup"
git push origin main
```

Then go to your repo → **Actions tab** → enable workflows if prompted.

---

### Step 5 — Test It Manually

1. Go to **Actions** tab in your repo
2. Click **"YouTube → MailerLite Email Automation"**
3. Click **"Run workflow"** → **"Run workflow"**
4. Watch the logs — a draft campaign will appear in MailerLite within seconds

---

## ⏰ Schedule

The workflow runs **every hour** by default (`cron: "0 * * * *"`).

To change the frequency, edit `.github/workflows/youtube-to-mailerlite.yml`:

```yaml
# Every 30 minutes
- cron: "*/30 * * * *"

# Every 6 hours
- cron: "0 */6 * * *"

# Once a day at 9am UTC
- cron: "0 9 * * *"
```

---

## 📁 File Structure

```
youtube-to-mailerlite/
├── .github/
│   └── workflows/
│       └── youtube-to-mailerlite.yml   # GitHub Actions workflow
├── scripts/
│   └── run.py                          # Main automation script
├── seen_videos.json                    # Tracks processed video IDs
├── requirements.txt
└── README.md
```

---

## 🔧 Customizing the Email Template

Edit the `build_email_html()` function in `scripts/run.py` to change:
- Colors and fonts
- Button labels and styles
- Email layout and sections
- Footer text and unsubscribe link

---

## ⚠️ Notes

- Campaigns are created as **drafts** — you must manually review and send in MailerLite
- If no WordPress post matches the video title, it falls back to the YouTube description
- The `seen_videos.json` file is committed back to the repo after each run to prevent duplicates
- GitHub Actions free tier includes **2,000 minutes/month** — more than enough for hourly runs
