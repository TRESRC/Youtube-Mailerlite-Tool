# 📺 YouTube → MailerLite Campaign System

A two-part system for The Resource TV that automates the weekly email campaign workflow — from YouTube upload to MailerLite draft.

---

## 🗂 How It Works

This repo contains two tools that work together:

| Tool | Who uses it | Where it runs |
|---|---|---|
| **GitHub Action** (`run.py`) | Runs automatically | Cloud — GitHub Actions |
| **Campaign Creator** (`mailerlite-campaign-creator.html`) | Content manager | Locally in Chrome |

### Typical weekly workflow

1. A new video is uploaded to YouTube
2. The **GitHub Action** detects it hourly and logs it to `seen_videos.json`
3. The **content manager** opens the HTML file in Chrome, clicks **Fetch**, reviews and edits the content, adds social links, and creates the MailerLite draft in minutes
4. Someone reviews the draft in MailerLite and hits **Send**

---

## 📁 File Structure

```
your-repo/
├── .github/
│   └── workflows/
│       └── youtube-to-mailerlite.yml   # GitHub Actions workflow (hourly check)
├── scripts/
│   └── run.py                          # Automation script
├── mailerlite-campaign-creator.html    # Content manager tool (open locally in Chrome)
├── seen_videos.json                    # Tracks processed video IDs (auto-updated)
├── requirements.txt
└── README.md
```

---

## 🛠 Part 1 — GitHub Action (Cloud Automation)

Runs every hour on GitHub's servers. Detects new YouTube videos and logs the video ID to `seen_videos.json` to prevent duplicate processing.

### Setup

#### Step 1 — Clone the repo

```bash
git clone https://github.com/YOUR_USERNAME/YOUR-REPO-NAME.git
cd YOUR-REPO-NAME
```

#### Step 2 — Add GitHub Secrets

Go to your repo → **Settings → Secrets and variables → Actions → New repository secret**

| Secret | Value |
|---|---|
| `YOUTUBE_API_KEY` | YouTube Data API v3 key |
| `YOUTUBE_CHANNEL_ID` | e.g. `UCxxxxxxxxxxxxxxxxxxxxxx` |
| `WP_BASE_URL` | e.g. `https://theresource.tv` |
| `WP_USERNAME` | Your WordPress username |
| `WP_APP_PASSWORD` | WordPress Application Password |
| `MAILERLITE_API_KEY` | MailerLite API token |
| `MAILERLITE_GROUP_ID` | Subscriber group ID |
| `FROM_NAME` | e.g. `The Resource TV` |
| `FROM_EMAIL` | e.g. `hello@theresource.tv` |

#### Step 3 — Grant write permission

Go to **Settings → Actions → General → Workflow permissions** → set to **Read and write permissions**. This allows the workflow to commit `seen_videos.json` back to the repo after each run.

#### Step 4 — Test manually

1. Go to the **Actions** tab
2. Click **"YouTube → MailerLite Email Automation"**
3. Click **"Run workflow"**
4. Check the logs — you should see new videos detected and logged

#### Schedule

Runs every hour by default. To change, edit `.github/workflows/youtube-to-mailerlite.yml`:

```yaml
# Every hour (default)
- cron: "0 * * * *"

# Every 6 hours
- cron: "0 */6 * * *"

# Once a day at 9am UTC
- cron: "0 9 * * *"
```

---

## 🖥 Part 2 — Campaign Creator (Content Manager Tool)

A standalone HTML file the content manager opens locally in Chrome. No login, no install, no server — just open the file and go.

### First-time setup (one time per device)

1. Download `mailerlite-campaign-creator.html` from this repo
2. Open it in **Chrome**
3. Go to the **Configuration** tab
4. Enter all API credentials (same values as the GitHub secrets above)
5. Click **Save configuration** — credentials are stored in Chrome's local storage and remembered permanently on this device

### Weekly workflow (~3 minutes)

1. Open `mailerlite-campaign-creator.html` in Chrome
2. Go to **Content** → click **Fetch latest video + blog post**
   - Subject line, thumbnail, body copy, and YouTube URL auto-populate from YouTube
   - WordPress blog URL auto-populates from the latest `videos` custom post type entry
3. Edit the body copy and preheader text as needed
4. Go to **Social links**
   - Instagram, Facebook, LinkedIn, and Podcast are pre-filled with The Resource's channel URLs
   - Update any that point to a specific post this week
5. Go to **Create draft** → review the summary → click **Create MailerLite draft**
6. Open MailerLite → **Campaigns → Drafts** → review and send

### Getting updates

When the HTML file is updated in this repo:
1. Download the new version from GitHub
2. Replace the old file on your computer in the same folder location
3. Open in Chrome — saved credentials carry over automatically

### Pre-filled social channels

The following URLs are hardcoded as defaults and restore automatically each week:

| Platform | Default URL |
|---|---|
| Instagram | https://www.instagram.com/theresourcetv/ |
| Facebook | https://www.facebook.com/theresource.tv |
| LinkedIn | https://www.linkedin.com/company/the-re-source/ |
| Podcast | https://theresource.tv/podcast/ |

To update these defaults, edit the `SOCIAL_DEFAULTS` object in the `<script>` section of the HTML file.

---

## 🔑 Where to Get API Keys

**YouTube Data API v3**
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a project → Enable **YouTube Data API v3**
3. Create an **API Key** under Credentials
4. Find your Channel ID: go to your YouTube channel → View Source → search `channelId`

**WordPress Application Password**
1. WordPress dashboard → **Users → Profile**
2. Scroll to **Application Passwords**
3. Enter a name (e.g. `Campaign Creator`) → click **Add New**
4. Copy the generated password — shown only once

**MailerLite API Key & Group ID**
1. MailerLite → **Integrations → Developer API** → generate a token
2. Group ID: **Subscribers → Groups** → click your group → copy the number from the URL

---

## ⚠️ Notes

- Campaigns are always created as **drafts** — nothing sends automatically
- `seen_videos.json` is auto-committed after each GitHub Action run to prevent duplicates
- If no WordPress `videos` post is found, the YouTube description is used as fallback body copy
- GitHub Actions free tier includes 2,000 minutes/month — hourly runs use well under 100 minutes/month
- The HTML tool works offline except for the two API calls (fetch and campaign creation require internet)
