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
TEST_CAMPAIGN_ID   = os.environ.get("TEST_CAMPAIGN_ID", "")
DRY_RUN            = os.environ.get("DRY_RUN", "true").lower() == "true"  # Safe by default

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

def get_non_openers(campaign_id):
    """Fetch all subscribers who did not open the campaign."""
    non_openers = []
    cursor = None
    while True:
        params = {"filter[type]": "unopened", "limit": 100}
        if cursor:
            params["cursor"] = cursor
        r = requests.get(
            f"https://connect.mailerlite.com/api/campaigns/{campaign_id}/reports/subscriber-activity",
            headers=headers,
            params=params,
            timeout=30,
        )
        if not r.ok:
            log(f"⚠️  Failed to fetch non-openers: {r.text[:200]}")
            break
        data = r.json()
        batch = data.get("data", [])
        non_openers.extend([s["subscriber"]["id"] for s in batch if s.get("subscriber")])
        # Pagination
        next_cursor = data.get("meta", {}).get("next_cursor") or data.get("links", {}).get("next")
        if not next_cursor or not batch:
            break
        cursor = next_cursor
    return non_openers

def create_resend(campaign):
    """Clone a sent campaign and send to non-openers."""
    campaign_id   = campaign["id"]
    original_name = campaign["name"]
    original_subj = campaign["emails"][0]["subject"]
    from_name     = campaign["emails"][0].get("from_name", "TheREsource.tv")
    from_email    = campaign["emails"][0].get("from", "theguys@theresource.tv")

    resend_subject = f"{{$name}}, {original_subj}"
    resend_name    = f"{original_name} [resend]"

    log(f"Creating resend for: {original_name}")
    log(f"Resend subject: {resend_subject}")

    # Step 1 — Fetch non-openers
    log("Fetching non-openers...")
    non_openers = get_non_openers(campaign_id)
    log(f"Non-openers: {len(non_openers)}")
    if not non_openers:
        log("No non-openers found — skipping resend")
        return False

    # Step 2 — Copy the sent campaign
    copy_r = requests.post(
        f"https://connect.mailerlite.com/api/campaigns/{campaign_id}/copy",
        headers=headers, timeout=30,
    )
    if not copy_r.ok:
        log(f"⚠️  Copy failed: {copy_r.status_code} {copy_r.text[:200]}")
        return False

    new_id   = copy_r.json()["data"]["id"]
    new_type = copy_r.json()["data"]["type"]
    log(f"Cloned — new campaign ID: {new_id} | type: {new_type}")

    # Step 3 — Update name and subject
    update_payload = {
        "name":        resend_name,
        "language_id": 4,
        "type":        new_type,
        "emails":      [{"subject": resend_subject, "from_name": from_name, "from": from_email}],
    }
    if new_type == "resend":
        update_payload["resend_settings"] = {
            "test_type":         "subject",
            "select_winner_by":  "c",
            "b_value":           {"subject": resend_subject},
            "resend_delay":      24,
            "resend_delay_type": "hours",
        }

    update_r = requests.put(
        f"https://connect.mailerlite.com/api/campaigns/{new_id}",
        headers=headers,
        json=update_payload,
        timeout=30,
    )
    log(f"Update: {update_r.status_code} | {update_r.text[:150]}")
    if not update_r.ok:
        log("⚠️  Update failed")
        return False

    # Step 4 — Send/schedule
    if DRY_RUN:
        log(f"🧪 DRY RUN — would send to {len(non_openers)} non-openers")
        log(f"   Subject: {resend_subject}")
        log(f"   First 5 subscriber IDs: {non_openers[:5]}")
        log(f"   Run with DRY_RUN=false to actually send")
        return True

    send_r = requests.post(
        f"https://connect.mailerlite.com/api/campaigns/{new_id}/schedule",
        headers=headers,
        json={"delivery": "instant"},
        timeout=30,
    )
    log(f"Send: {send_r.status_code} | {send_r.text[:200]}")
    if send_r.ok:
        log(f"✅ Resend sent to {len(non_openers)} non-openers! Campaign ID: {new_id}")
        return True
    else:
        log(f"⚠️  Send failed: {send_r.text[:200]}")
        return False

def main():
    log("🔄 Auto-resend check starting...")

    # Test mode — process a specific campaign regardless of send time
    if TEST_CAMPAIGN_ID:
        log(f"🧪 TEST MODE — processing campaign: {TEST_CAMPAIGN_ID}")
        r = requests.get(
            f"https://connect.mailerlite.com/api/campaigns/{TEST_CAMPAIGN_ID}",
            headers=headers, timeout=30,
        )
        if not r.ok:
            log(f"❌ Campaign not found: {r.text[:200]}")
            return
        campaign = r.json()["data"]
        log(f"Campaign: {campaign['name']} | type: {campaign['type']} | status: {campaign['status']}")
        create_resend(campaign)
        return
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
