#!/usr/bin/env python3
"""
Campaign Creator — called by GitHub Actions with content from the web tool.
Receives all campaign data via environment variables and creates a MailerLite draft.
"""

import os
import sys
import json
import requests
from datetime import datetime, timezone

# ── Config from secrets ───────────────────────────────────────────────────────
MAILERLITE_API_KEY  = os.environ["MAILERLITE_API_KEY"]
MAILERLITE_GROUP_ID = os.environ["MAILERLITE_GROUP_ID"]
FROM_NAME           = "TheREsource.tv"
FROM_EMAIL          = "theguys@theresource.tv"

# ── Content from workflow inputs (passed by the web tool) ─────────────────────
SUBJECT     = os.environ["INPUT_SUBJECT"]
PREHEADER   = os.environ.get("INPUT_PREHEADER", "")
IMAGE_URL   = os.environ.get("INPUT_IMAGE_URL", "")
BODY_COPY   = os.environ.get("INPUT_BODY_COPY", "")
YOUTUBE_URL = os.environ.get("INPUT_YOUTUBE_URL", "")
BLOG_URL    = os.environ.get("INPUT_BLOG_URL", "")
INSTAGRAM   = os.environ.get("INPUT_INSTAGRAM_URL", "")
FACEBOOK    = os.environ.get("INPUT_FACEBOOK_URL", "")
LINKEDIN    = os.environ.get("INPUT_LINKEDIN_URL", "")
PODCAST     = os.environ.get("INPUT_PODCAST_URL", "")

def log(msg):
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    print(f"[{ts}] {msg}")

def btn(label, url):
    if not url:
        return ""
    return (
        f'<table role="presentation" cellpadding="0" cellspacing="0" border="0" '
        f'align="left" style="margin-bottom:10px;">'
        f'<tr><td align="center" style="font-family:\'Montserrat\',sans-serif;">'
        f'<a href="{url}" target="_blank" style="font-family:\'Montserrat\',sans-serif;'
        f'background-color:#ffffff;border:2px solid #cb0000;border-radius:1px;color:#dc3545;'
        f'display:inline-block;font-size:14px;font-weight:700;line-height:20px;padding:9px 0;'
        f'text-align:center;text-decoration:none;width:166px;">{label}</a>'
        f'</td></tr></table>'
    )

def build_html():
    today = datetime.now(timezone.utc).strftime("%b %d, %Y")

    preheader_div = (
        f'<div style="display:none;max-height:0;overflow:hidden;mso-hide:all;'
        f'font-size:1px;color:#f6f8f9;">{PREHEADER}'
        f'&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;</div>'
    ) if PREHEADER else ""

    thumb = (
        f'<a href="{YOUTUBE_URL}" target="_blank">'
        f'<img src="{IMAGE_URL}" border="0" alt="{SUBJECT}" width="560" '
        f'style="display:block;width:100%;max-width:560px;height:auto;"></a>'
    ) if IMAGE_URL else ""

    body_paragraphs = "".join(
        f'<p style="margin-top:0;margin-bottom:10px;line-height:150%;">{line}</p>'
        for line in BODY_COPY.split("\n") if line.strip()
    )

    row1 = btn("Instagram", INSTAGRAM) + btn("Facebook", FACEBOOK) + btn("Podcast", PODCAST)
    row2 = btn("Website", BLOG_URL) + btn("LinkedIn", LINKEDIN) + btn("YouTube", YOUTUBE_URL)

    return f"""<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 3.2//EN">
<html lang="">
<head>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{SUBJECT}</title>
<style type="text/css">
body{{margin:0;padding:0;background-color:#f6f8f9;}}
body,table,td,p,a,li{{-webkit-text-size-adjust:100%;-ms-text-size-adjust:100%;}}
table{{border-spacing:0;border-collapse:collapse;}}
img{{border:0;outline:none;text-decoration:none;-ms-interpolation-mode:bicubic;}}
@media screen{{body{{font-family:'Montserrat',sans-serif;}}}}
@media only screen and (max-width:640px){{
  .mlContentOuter{{padding-left:15px!important;padding-right:15px!important;}}
  .mlContentButton a{{display:block!important;width:auto!important;}}
  .mobileHide{{display:none!important;}}
  .marginBottom{{margin-bottom:15px!important;}}
  .mlContentImage img{{width:100%!important;height:auto!important;}}
}}
</style>
</head>
<body style="padding:0;margin:0;background-color:#f6f8f9;">
{preheader_div}
<table width="100%" border="0" cellspacing="0" cellpadding="0" bgcolor="#f6f8f9">
<tr><td align="center">

  <table cellpadding="0" cellspacing="0" border="0" align="center" width="640" style="width:640px;min-width:640px;">
    <tr><td colspan="2" height="20"></td></tr>
    <tr>
      <td align="left" style="font-family:'Montserrat',sans-serif;color:#111111;font-size:12px;line-height:18px;">{PREHEADER}</td>
      <td align="right" style="font-family:'Montserrat',sans-serif;color:#111111;font-size:12px;line-height:18px;"><a href="{{$url}}" style="color:#111111;">View in browser</a></td>
    </tr>
    <tr><td colspan="2" height="20"></td></tr>
  </table>

  <table align="center" border="0" bgcolor="#ffffff" cellpadding="0" cellspacing="0" width="640" style="width:640px;min-width:640px;">
  <tr><td>

    <table role="presentation" cellpadding="0" cellspacing="0" border="0" align="center" width="640" style="width:640px;min-width:640px;">
      <tr><td align="center" style="padding:0;">
        <img src="https://storage.mlcdn.com/account_image/318100/S7zmBlAJIt7XKgyLUqSgmNMmnla5iQRvcn2nHClK.png" border="0" alt="The RE Source" width="637" style="display:block;">
      </td></tr>
    </table>

    <table role="presentation" cellpadding="0" cellspacing="0" border="0" align="center" width="640" style="width:640px;min-width:640px;">
      <tr><td height="20" style="line-height:20px;min-height:20px;"></td></tr>
    </table>

    <table role="presentation" cellpadding="0" cellspacing="0" border="0" align="center" width="640" style="width:640px;min-width:640px;">
      <tr><td align="center" style="padding:0 40px;">
        <table role="presentation" cellpadding="0" cellspacing="0" border="0" align="center" width="100%">
          <tr><td align="center" style="font-family:'Montserrat',sans-serif;font-size:13px;font-weight:400;line-height:150%;color:#dc3545;text-align:center;">NEW EPISODE</td></tr>
          <tr><td height="20"></td></tr>
          <tr><td align="center" style="font-family:'Montserrat',sans-serif;font-size:29px;font-weight:700;line-height:150%;color:#111111;text-align:center;">
            <a href="{YOUTUBE_URL}" style="text-decoration:none;color:#111111;" target="_blank">{SUBJECT}</a>
          </td></tr>
        </table>
      </td></tr>
    </table>

    <table role="presentation" cellpadding="0" cellspacing="0" border="0" align="center" width="640" style="width:640px;min-width:640px;">
      <tr><td height="20" style="line-height:20px;min-height:20px;"></td></tr>
    </table>

    <table role="presentation" cellpadding="0" cellspacing="0" border="0" align="center" width="640" style="width:640px;min-width:640px;">
      <tr><td align="center" style="padding:0 40px;">
        <table role="presentation" cellpadding="0" cellspacing="0" border="0" align="center" width="100%">
          <tr><td align="center">{thumb}</td></tr>
        </table>
      </td></tr>
    </table>

    <table role="presentation" cellpadding="0" cellspacing="0" border="0" align="center" width="640" style="width:640px;min-width:640px;">
      <tr><td height="20" style="line-height:20px;min-height:20px;"></td></tr>
    </table>

    <table role="presentation" cellpadding="0" cellspacing="0" border="0" align="center" width="640" style="width:640px;min-width:640px;">
      <tr><td align="center" style="padding:0 40px;">
        <table role="presentation" cellpadding="0" cellspacing="0" border="0" align="center" width="100%">
          <tr><td style="font-family:'Montserrat',sans-serif;font-size:14px;line-height:150%;color:#6f6f6f;">{body_paragraphs}</td></tr>
        </table>
      </td></tr>
    </table>

    <table role="presentation" cellpadding="0" cellspacing="0" border="0" align="center" width="640" style="width:640px;min-width:640px;">
      <tr><td height="40" style="line-height:40px;min-height:40px;"></td></tr>
    </table>

    <table role="presentation" cellpadding="0" cellspacing="0" border="0" align="center" width="640" style="width:640px;min-width:640px;">
      <tr><td align="center" style="padding:0 40px;">{row1}</td></tr>
    </table>

    <table role="presentation" cellpadding="0" cellspacing="0" border="0" align="center" width="640" style="width:640px;min-width:640px;">
      <tr><td height="20" style="line-height:20px;min-height:20px;"></td></tr>
    </table>

    <table role="presentation" cellpadding="0" cellspacing="0" border="0" align="center" width="640" style="width:640px;min-width:640px;">
      <tr><td align="center" style="padding:0 40px;">{row2}</td></tr>
    </table>

    <table role="presentation" cellpadding="0" cellspacing="0" border="0" align="center" width="640" style="width:640px;min-width:640px;">
      <tr><td height="20" style="line-height:20px;min-height:20px;"></td></tr>
    </table>
    <table role="presentation" cellpadding="0" cellspacing="0" border="0" align="center" width="640" style="width:640px;min-width:640px;">
      <tr><td align="center">
        <table role="presentation" cellpadding="0" cellspacing="0" border="0" align="center" width="100%" style="border-top:1px solid #ededf3;border-collapse:initial;">
          <tr><td height="20" style="line-height:20px;min-height:20px;"></td></tr>
        </table>
      </td></tr>
    </table>

    <table role="presentation" cellpadding="0" cellspacing="0" border="0" align="center" width="640" style="width:640px;min-width:640px;">
      <tr><td align="center" style="padding:0 40px;">
        <table role="presentation" cellpadding="0" cellspacing="0" border="0" align="center" width="100%">
          <tr><td align="center" style="font-family:'Montserrat',sans-serif;font-size:28px;font-weight:700;line-height:150%;color:#111111;text-align:center;">Industry Partner Spotlight</td></tr>
        </table>
      </td></tr>
    </table>

    <table role="presentation" cellpadding="0" cellspacing="0" border="0" align="center" width="640" style="width:640px;min-width:640px;">
      <tr><td height="20" style="line-height:20px;min-height:20px;"></td></tr>
    </table>

    <table role="presentation" cellpadding="0" cellspacing="0" border="0" align="center" width="640" style="width:640px;min-width:640px;">
      <tr><td align="center" style="padding:0 40px;">
        <table role="presentation" cellpadding="0" cellspacing="0" border="0" align="center" width="100%">
          <tr><td style="font-family:'Montserrat',sans-serif;font-size:14px;line-height:150%;color:#6f6f6f;text-align:center;">
            <p style="margin-top:0;margin-bottom:0;line-height:150%;text-align:center;">A longtime partner and trusted source for daily mortgage industry insights.</p>
          </td></tr>
        </table>
      </td></tr>
    </table>

    <table role="presentation" cellpadding="0" cellspacing="0" border="0" align="center" width="640" style="width:640px;min-width:640px;">
      <tr><td height="20" style="line-height:20px;min-height:20px;"></td></tr>
    </table>

    <table role="presentation" cellpadding="0" cellspacing="0" border="0" align="center" width="640" style="width:640px;min-width:640px;">
      <tr><td align="center" style="padding:0;">
        <a href="https://www.chrismancommentary.com/" target="_blank">
          <img src="https://storage.mlcdn.com/account_image/318100/BrGoqFUD9UYLkqhmhltu3YEqQdUtDxMunlMGyUlc.png" border="0" alt="Chrisman Commentary" width="600" style="display:block;width:100%;max-width:600px;height:auto;">
        </a>
      </td></tr>
    </table>

    <table role="presentation" cellpadding="0" cellspacing="0" border="0" align="center" width="640" style="width:640px;min-width:640px;">
      <tr><td height="20" style="line-height:20px;min-height:20px;"></td></tr>
    </table>
    <table role="presentation" cellpadding="0" cellspacing="0" border="0" align="center" width="640" style="width:640px;min-width:640px;">
      <tr><td align="center">
        <table role="presentation" cellpadding="0" cellspacing="0" border="0" align="center" width="100%" style="border-top:1px solid #ededf3;border-collapse:initial;">
          <tr><td height="20" style="line-height:20px;min-height:20px;"></td></tr>
        </table>
      </td></tr>
    </table>

    <table role="presentation" cellpadding="0" cellspacing="0" border="0" align="center" width="640" style="width:640px;min-width:640px;">
      <tr><td height="20" style="line-height:20px;min-height:20px;"></td></tr>
    </table>
    <table role="presentation" cellpadding="0" cellspacing="0" border="0" align="center" width="640" style="width:640px;min-width:640px;">
      <tr><td align="center" style="padding:0 40px;">
        <table role="presentation" cellpadding="0" cellspacing="0" border="0" align="center" width="560" style="border-radius:2px;border-collapse:separate;">
          <tr><td align="center" style="padding:0 40px;border:1px solid #E6E6E6;border-radius:2px;" bgcolor="#FCFCFC">
            <table role="presentation" cellpadding="0" cellspacing="0" border="0" align="center" width="100%">
              <tr><td height="30"></td></tr>
              <tr><td style="font-family:'Montserrat',sans-serif;font-size:14px;line-height:150%;color:#6f6f6f;">
                <p style="margin-top:0;margin-bottom:10px;line-height:150%;text-align:center;"><strong>Our community of over 50,000 subscribers depend on our weekly shows to help keep them inspired, avoid burnout &amp; keep them extremely relevant in their local communities.</strong></p>
                <p style="margin-top:0;margin-bottom:0;line-height:150%;text-align:center;">We invite you to watch a few trending episodes to help you reset your mindset &amp; focus on thriving during a challenging market.</p>
              </td></tr>
              <tr><td height="30"></td></tr>
            </table>
          </td></tr>
        </table>
      </td></tr>
    </table>

    <table role="presentation" cellpadding="0" cellspacing="0" border="0" align="center" width="640" style="width:640px;min-width:640px;">
      <tr><td height="20" style="line-height:20px;min-height:20px;"></td></tr>
    </table>
    <table role="presentation" cellpadding="0" cellspacing="0" border="0" align="center" width="640" style="width:640px;min-width:640px;">
      <tr><td align="center">
        <table role="presentation" cellpadding="0" cellspacing="0" border="0" align="center" width="100%" style="border-top:1px solid #ededf3;border-collapse:initial;">
          <tr><td height="20" style="line-height:20px;min-height:20px;"></td></tr>
        </table>
      </td></tr>
    </table>

  </td></tr>
  </table>

  <table align="center" border="0" bgcolor="#ffffff" cellpadding="0" cellspacing="0" width="640" style="width:640px;min-width:640px;">
  <tr><td>
    <table role="presentation" cellpadding="0" cellspacing="0" border="0" align="center" width="640" style="width:640px;min-width:640px;">
      <tr><td height="30" style="line-height:30px;min-height:30px;"></td></tr>
    </table>
    <table role="presentation" cellpadding="0" cellspacing="0" border="0" align="center" width="640" style="width:640px;min-width:640px;">
      <tr><td align="center" style="padding:0 40px;">
        <table role="presentation" cellpadding="0" cellspacing="0" border="0" align="center" width="100%">
          <tr><td align="left" style="font-family:'Montserrat',sans-serif;font-size:14px;font-weight:700;line-height:150%;color:#111111;">TheREsource.tv</td></tr>
        </table>
      </td></tr>
    </table>
    <table role="presentation" cellpadding="0" cellspacing="0" border="0" align="center" width="640" style="width:640px;min-width:640px;">
      <tr><td height="10"></td></tr>
    </table>
    <table role="presentation" cellpadding="0" cellspacing="0" border="0" align="center" width="640" style="width:640px;min-width:640px;">
      <tr><td align="center" style="padding:0 40px;">
        <table role="presentation" cellpadding="0" cellspacing="0" border="0" align="center" width="100%">
          <tr><td align="center">
            <table role="presentation" cellpadding="0" cellspacing="0" border="0" align="left" width="267" style="width:267px;min-width:267px;">
              <tr><td align="left" style="font-family:'Montserrat',sans-serif;font-size:12px;line-height:150%;color:#111111;">
                <p style="margin-top:0;margin-bottom:10px;">1029 E Main</p>
                <p style="margin-top:0;margin-bottom:0;">Puyallup, WA 98372</p>
              </td></tr>
              <tr><td height="25"></td></tr>
              <tr><td align="center">
                <table role="presentation" cellpadding="0" cellspacing="0" border="0" align="left">
                  <tr>
                    <td align="center" width="24" style="padding:0 5px;"><a href="https://www.instagram.com/theresourcetv/" target="_blank"><img width="24" alt="instagram" src="https://assets.mlcdn.com/ml/images/icons/default/round/black/instagram.png" style="display:block;" border="0"></a></td>
                    <td align="center" width="24" style="padding:0 5px;"><a href="http://www.facebook.com/theresourcetv" target="_blank"><img width="24" alt="facebook" src="https://assets.mlcdn.com/ml/images/icons/default/round/black/facebook.png" style="display:block;" border="0"></a></td>
                    <td align="center" width="24" style="padding:0 5px;"><a href="https://youtube.com/theresourcetv?sub_confirmation=1" target="_blank"><img width="24" alt="youtube" src="https://assets.mlcdn.com/ml/images/icons/default/round/black/youtube.png" style="display:block;" border="0"></a></td>
                    <td align="center" width="24" style="padding:0 5px;"><a href="https://www.linkedin.com/in/the-resourcetv-1a635926/" target="_blank"><img width="24" alt="linkedin" src="https://assets.mlcdn.com/ml/images/icons/default/round/black/linkedin.png" style="display:block;" border="0"></a></td>
                    <td align="center" width="24" style="padding:0 5px;"><a href="https://theresource.tv/?utm_source=newsletter&utm_campaign=welcomeemail" target="_blank"><img width="24" alt="website" src="https://assets.mlcdn.com/ml/images/icons/default/round/black/website.png" style="display:block;" border="0"></a></td>
                  </tr>
                </table>
              </td></tr>
            </table>
            <table role="presentation" cellpadding="0" cellspacing="0" border="0" align="right" width="267" style="width:267px;min-width:267px;">
              <tr><td align="right" style="font-family:'Montserrat',sans-serif;font-size:12px;line-height:150%;color:#111111;">
                <p style="margin-top:0;margin-bottom:10px;">As an industry leader &amp; a committed expert, we want to help you continue to thrive.</p>
                <p style="margin-top:0;margin-bottom:0;">If you prefer not to receive our weekly emails, please use the link below.</p>
              </td></tr>
              <tr><td height="10"></td></tr>
              <tr><td align="right" style="font-family:'Montserrat',sans-serif;font-size:12px;line-height:150%;color:#111111;">
                <a href="{{$unsubscribe}}" style="color:#111111;text-decoration:underline;">Unsubscribe</a>
              </td></tr>
            </table>
          </td></tr>
        </table>
      </td></tr>
    </table>
    <table role="presentation" cellpadding="0" cellspacing="0" border="0" align="center" width="640" style="width:640px;min-width:640px;">
      <tr><td height="40" style="line-height:40px;min-height:40px;"></td></tr>
    </table>
  </td></tr>
  </table>

</td></tr>
</table>
</body>
</html>"""

def create_campaign(html: str) -> str:
    today = datetime.now(timezone.utc).strftime("%b %d, %Y")
    safe_name = f"{SUBJECT} - {today}"
    headers = {
        "Authorization": f"Bearer {MAILERLITE_API_KEY}",
        "Content-Type":  "application/json",
        "Accept":        "application/json",
    }

    SOURCE_CAMPAIGN_ID = "186558527880300307"

    # Step 1 — Copy the last sent campaign to drafts
    log(f"Copying campaign {SOURCE_CAMPAIGN_ID}...")
    r = requests.post(
        f"https://connect.mailerlite.com/api/campaigns/{SOURCE_CAMPAIGN_ID}/copy",
        headers=headers,
        timeout=30,
    )
    if not r.ok:
        raise RuntimeError(f"Copy failed: {r.status_code} {r.text}")

    data = r.json()["data"]
    campaign_id = data["id"]
    email_id    = data["emails"][0]["id"]
    old_content = data["emails"][0].get("content", "")
    old_subject = data["emails"][0].get("subject", "")
    log(f"Copied — campaign: {campaign_id} email: {email_id}")
    log(f"Old subject: {old_subject}")
    log(f"Old content length: {len(old_content)}")

    # Step 2 — Find and replace dynamic content in the copied HTML
    # The copied content is the real builder HTML — we swap the variable parts
    new_content = old_content

    # Replace title (appears as linked text in the email)
    new_content = new_content.replace(old_subject, SUBJECT)

    # Replace thumbnail image URL
    if IMAGE_URL and old_content:
        import re
        # Find existing image URLs that look like stored ML CDN or WordPress uploads
        img_pattern = r'(https://storage\.mlcdn\.com/account_image/318100/[^"\']+\.(?:png|jpg|jpeg|gif)|https://theresource\.tv/wp-content/uploads/[^"\']+\.(?:png|jpg|jpeg|gif))'
        existing_imgs = re.findall(img_pattern, old_content)
        # The thumbnail is typically the largest image — find the one that's not the logo or partner image
        logo_url = "S7zmBlAJIt7XKgyLUqSgmNMmnla5iQRvcn2nHClK"
        partner_url = "BrGoqFUD9UYLkqhmhltu3YEqQdUtDxMunlMGyUlc"
        thumb_candidates = [u for u in existing_imgs if logo_url not in u and partner_url not in u]
        if thumb_candidates:
            old_thumb = thumb_candidates[0]
            log(f"Replacing thumbnail: {old_thumb[:80]}...")
            new_content = new_content.replace(old_thumb, IMAGE_URL)
        else:
            log("⚠️  Could not find thumbnail URL to replace")

    # Replace YouTube button links
    if YOUTUBE_URL and old_content:
        yt_pattern = r'https://(?:youtu\.be|www\.youtube\.com/watch\?v=)[^"\'&]+'
        old_yt_urls = re.findall(yt_pattern, old_content)
        for old_url in set(old_yt_urls):
            log(f"Replacing YouTube URL: {old_url}")
            new_content = new_content.replace(old_url, YOUTUBE_URL)

    # Replace WordPress blog URL
    if BLOG_URL and old_content:
        wp_pattern = r'https://theresource\.tv/video/[^"\'&]+'
        old_wp_urls = re.findall(wp_pattern, old_content)
        for old_url in set(old_wp_urls):
            log(f"Replacing blog URL: {old_url}")
            new_content = new_content.replace(old_url, BLOG_URL)

    # Replace body text paragraphs (between the title and the buttons)
    if BODY_COPY and old_content:
        # Find the bodyText section
        body_pattern = r'(<td[^>]*id="bodyText-10"[^>]*>)(.*?)(</td>)'
        body_match = re.search(body_pattern, new_content, re.DOTALL)
        if body_match:
            new_body_html = ''.join(
                f'<p style="margin-top: 0px; margin-bottom: 10px; line-height: 150%;">{p}</p>'
                for p in BODY_COPY.split('\n') if p.strip()
            )
            new_content = new_content[:body_match.start(2)] + new_body_html + new_content[body_match.end(2):]
            log("Replaced body text")
        else:
            log("⚠️  Could not find bodyText-10 block to replace")

    log(f"New content length: {len(new_content)}")

    # Step 3 — Update name, subject, content, resend_settings
    # Resend campaigns require emails as array of arrays: [[{email_obj}]]
    email_a = {
        "subject":   SUBJECT,
        "from_name": FROM_NAME,
        "from":      FROM_EMAIL,
        "content":   new_content,
    }
    if PREHEADER:
        email_a["preheader_text"] = PREHEADER

    update = requests.put(
        f"https://connect.mailerlite.com/api/campaigns/{campaign_id}",
        headers=headers,
        json={
            "name":        safe_name,
            "language_id": 4,
            "type":        "resend",
            "emails":      [[email_a]],
            "groups":      [MAILERLITE_GROUP_ID],
            "resend_settings": {
                "test_type":         "subject",
                "select_winner_by":  "c",
                "b_value":           {"subject": SUBJECT},
                "resend_delay":      24,
                "resend_delay_type": "hours",
            },
        },
        timeout=30,
    )
    log(f"Update status: {update.status_code}")
    if not update.ok:
        log(f"Update response: {update.text[:500]}")
    else:
        log("✅ Content and subject updated successfully")
    log(f"✅ Draft ready — ID: {campaign_id}")
    return campaign_id

def main():
    log("🚀 Campaign Creator starting")
    log(f"   Subject: {SUBJECT}")

    html = build_html()
    log(f"   HTML length: {len(html)} chars")

    campaign_id = create_campaign(html)

    # Write campaign ID to output for GitHub Actions summary
    with open(os.environ.get("GITHUB_STEP_SUMMARY", "/dev/null"), "a") as f:
        f.write(f"## ✅ MailerLite Draft Created\n")
        f.write(f"**Campaign ID:** {campaign_id}\n\n")
        f.write(f"**Subject:** {SUBJECT}\n\n")
        f.write(f"Go to [MailerLite Drafts](https://dashboard.mailerlite.com/campaigns/draft) to review and send.\n")

    print(f"::set-output name=campaign_id::{campaign_id}")
    log("Done.")

if __name__ == "__main__":
    main()
