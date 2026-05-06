# 📺 The RE Source — Email Automation

A branded web tool that automates the weekly email campaign workflow for The RE Source — from a new YouTube upload to a fully built MailerLite draft in about 3 minutes.

**Live tool:** [tresrc.github.io/Youtube-Mailerlite-Tool](https://tresrc.github.io/Youtube-Mailerlite-Tool/)

---

## How It Works

1. Content manager opens the tool and clicks **Fetch** — pulls the latest YouTube video title, thumbnail, description, and URL, plus the matching WordPress post URL
2. Thumbnail is processed automatically — play button overlay and chevron corner cuts applied in the browser, then uploaded to WordPress media
3. Content manager reviews and edits body copy, preheader, and social links
4. Clicks **Create MailerLite draft** — triggers a GitHub Actions workflow that builds the full email and creates a draft in MailerLite
5. Draft appears in MailerLite ~30 seconds later, ready to review and send

---

## File Structure

```
├── .github/
│   └── workflows/
│       ├── create-campaign.yml       # Triggered by the web tool to create MailerLite drafts
│       ├── deploy-pages.yml          # Deploys the web tool to GitHub Pages on push
│       └── youtube-to-mailerlite.yml # Retired — kept for reference only
├── scripts/
│   ├── create_campaign.py            # Campaign creation script (called by create-campaign.yml)
│   └── run.py                        # Retired — kept for reference only
├── index.html                        # The web tool (served via GitHub Pages)
├── img-resourcelogo-v5.png           # RE Source logo used in the tool
├── seen_videos.json                  # Kept for reference — no longer actively used
├── requirements.txt
└── README.md
```

---

## GitHub Secrets Required

| Secret | Description |
|---|---|
| `MAILERLITE_API_KEY` | MailerLite API token |
| `MAILERLITE_GROUP_ID` | Subscriber group ID |
| `YOUTUBE_API_KEY` | YouTube Data API v3 key |
| `YOUTUBE_CHANNEL_ID` | The RE Source channel ID |
| `WP_BASE_URL` | WordPress site URL |
| `WP_USERNAME` | WordPress username |
| `WP_APP_PASSWORD` | WordPress application password |

---

## Content Manager Setup (One Time)

1. Open [tresrc.github.io/Youtube-Mailerlite-Tool](https://tresrc.github.io/Youtube-Mailerlite-Tool/) in Chrome
2. Click **Configuration** (bottom left of sidebar)
3. Enter your GitHub Personal Access Token (`ghp_...`) with `workflow` scope and the repo (`tresrc/Youtube-Mailerlite-Tool`)
4. Enter YouTube API key, Channel ID, WordPress URL, username, and app password
5. Click **Save configuration** — credentials are stored in your browser and remembered permanently
6. Upload the play button PNG once on the Content page — also remembered permanently

---

## Weekly Workflow (~3 minutes)

1. Open the tool
2. **Content** → click **Fetch latest video + blog post**
3. Edit body copy and preheader as needed
4. **Social links** → update any platform links that changed this week
5. **Create draft** → review summary → click **Create MailerLite draft**
6. Open MailerLite → Campaigns → Drafts → review and send

---

## Social Channel Defaults

Pre-filled every week — update only if the specific post URL changes:

| Platform | URL |
|---|---|
| Instagram | instagram.com/theresourcetv |
| Facebook | facebook.com/theresource.tv |
| LinkedIn | linkedin.com/company/the-re-source |
| Podcast | theresource.tv/podcast |

To change defaults, edit `SOCIAL_DEFAULTS` in the `<script>` section of `index.html`.
