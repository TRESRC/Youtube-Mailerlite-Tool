#!/usr/bin/env python3
"""
Auto-resend script — runs hourly via GitHub Actions.
Finds campaigns sent ~24 hours ago, clones them, and resends to non-openers.
"""

import os
import json
import requests
from datetime import datetime, timezone, timedelta

MAILERLITE_API_KEY = os.environ["MAILERLITE_API_KEY"]
RESEND_DELAY_HOURS = 24

def log(msg):
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    print(f"[{ts}] {msg}", flush=True)

headers = {
    "Authorization": f"Bearer {MAILERLITE_API_KEY}",
    "Content-Type":  "application/json",
    "Accept":        "application/json",
}

def get_sent_campaigns():
    """Fetch recently sent regular campaigns."""
    r = requests.get(
        "https://connect.mailerlite.com/api/campaigns",
        headers=headers,
        params={"filter[status]": "sent", "filter[type]": "regular", "limit": 25},
        timeout=30,
    )
    r.raise_for_status()
    return r.json()["data"]

def get_campaign_stats(campaign_id):
    """Get open/click stats for a campaign."""
    r = requests.get(
        f"https://connect.mailerlite.com/api/campaigns/{campaign_id}/reports/subscriber-activity",
        headers=headers,
        params={"filter[type]": "unopened", "limit": 1},
        timeout=30,
    )
    return r.json() if r.ok else None

def already_resent(campaign_name):
    """Check if we already sent a resend for this campaign."""
    r = requests.get(
        "https://connect.mailerlite.com/api/campaigns",
        headers=headers,
        params={"filter[status]": "sent", "limit": 25},
        timeout=30,
    )
    if not r.ok:
        return False
    for c in r.json()["data"]:
        if c["name"].endswith("[resend]") and campaign_name in c["name"]:
            return True
    # Also check drafts
    r2 = requests.get(
        "https://connect.mailerlite.com/api/campaigns",
        headers=headers,
        params={"filter[status]": "draft", "limit": 25},
        timeout=30,
    )
    if r2.ok:
        for c in r2.json()["data"]:
            if "[resend]" in c.get("name", "") and campaign_name in c.get("name", ""):
                return True
    return False

def create_resend(campaign):
    """Clone a sent campaign and send to non-openers."""
    campaign_id   = campaign["id"]
    original_name = campaign["name"]
    original_subj = campaign["emails"][0]["subject"]
    from_name     = campaign["emails"][0].get("from_name", "TheREsource.tv")
    from_email    = campaign["emails"][0].get("from", "theguys@theresource.tv")

    # New subject with personalization
    resend_subject = f"{{$name}}, {original_subj}"
    resend_name    = f"{original_name} [resend]"

    log(f"Creating resend for: {original_name}")
    log(f"Resend subject: {resend_subject}")

    # Step 1 — Copy the sent campaign
    copy_r = requests.post(
        f"https://connect.mailerlite.com/api/campaigns/{campaign_id}/copy",
        headers=headers,
        timeout=30,
    )
    if not copy_r.ok:
        log(f"⚠️  Copy failed: {copy_r.status_code} {copy_r.text[:200]}")
        return False

    new_id      = copy_r.json()["data"]["id"]
    new_email_id = copy_r.json()["data"]["emails"][0]["id"]
    log(f"Cloned — new campaign ID: {new_id}")

    # Step 2 — Update name, subject, and filter to non-openers of original
    update_r = requests.put(
        f"https://connect.mailerlite.com/api/campaigns/{new_id}",
        headers=headers,
        json={
            "name":        resend_name,
            "language_id": 4,
            "type":        "regular",
            "emails":      [{"subject": resend_subject, "from_name": from_name, "from": from_email}],
            # Filter: subscribers who did NOT open the original campaign
            "filter": [[
                {
                    "operator": "not_opened",
                    "args":     ["campaign", campaign_id],
                }
            ]],
        },
        timeout=30,
    )
    log(f"Update: {update_r.status_code} | {update_r.text[:200]}")

    if not update_r.ok:
        log(f"⚠️  Update failed")
        return False

    # Step 3 — Schedule immediately
    send_r = requests.post(
        f"https://connect.mailerlite.com/api/campaigns/{new_id}/schedule",
        headers=headers,
        json={"delivery": "instant"},
        timeout=30,
    )
    log(f"Send: {send_r.status_code} | {send_r.text[:200]}")

    if send_r.ok:
        log(f"✅ Resend sent! Campaign ID: {new_id}")
        return True
    else:
        log(f"⚠️  Send failed: {send_r.text[:200]}")
        return False

def main():
    log("🔄 Auto-resend check starting...")
    now = datetime.now(timezone.utc)
    window_start = now - timedelta(hours=RESEND_DELAY_HOURS + 1)
    window_end   = now - timedelta(hours=RESEND_DELAY_HOURS)

    log(f"Looking for campaigns sent between {window_start.strftime('%H:%M')} and {window_end.strftime('%H:%M')} UTC")

    campaigns = get_sent_campaigns()
    log(f"Found {len(campaigns)} recent sent campaigns")

    resent = 0
    for campaign in campaigns:
        # Check if sent in our target window
        finished_at = campaign.get("finished_at") or campaign.get("scheduled_for")
        if not finished_at:
            continue

        try:
            sent_time = datetime.fromisoformat(finished_at.replace("Z", "+00:00"))
        except Exception:
            continue

        if not (window_start <= sent_time <= window_end):
            continue

        name = campaign.get("name", "")
        log(f"Found campaign in window: {name} (sent: {finished_at})")

        # Skip if already resent
        if already_resent(name):
            log(f"Already resent — skipping: {name}")
            continue

        # Skip campaigns that are themselves resends
        if "[resend]" in name:
            log(f"Skipping resend campaign: {name}")
            continue

        success = create_resend(campaign)
        if success:
            resent += 1

    if resent == 0:
        log("No campaigns needed resending this hour.")
    else:
        log(f"✅ Done — {resent} resend(s) sent.")

main()
