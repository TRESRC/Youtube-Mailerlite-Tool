#!/usr/bin/env python3
"""
Playwright browser automation to update MailerLite draft content.
Called after create_campaign.py creates the draft.
Logs into MailerLite, opens the builder, and updates all dynamic content.
"""

import os
import sys
import asyncio
from datetime import datetime, timezone

# ── Config ─────────────────────────────────────────────────────────────────────
ML_EMAIL    = os.environ["MAILERLITE_EMAIL"]
ML_PASSWORD = os.environ["MAILERLITE_PASSWORD"]
CAMPAIGN_ID = os.environ["CAMPAIGN_ID"]
EMAIL_ID    = os.environ["EMAIL_ID"]
IMAGE_URL   = os.environ.get("INPUT_IMAGE_URL", "")
BODY_COPY   = os.environ.get("INPUT_BODY_COPY", "")
SUBJECT     = os.environ.get("INPUT_SUBJECT", "")
YOUTUBE_URL = os.environ.get("INPUT_YOUTUBE_URL", "")
BLOG_URL    = os.environ.get("INPUT_BLOG_URL", "")
INSTAGRAM   = os.environ.get("INPUT_INSTAGRAM_URL", "")
FACEBOOK    = os.environ.get("INPUT_FACEBOOK_URL", "")
LINKEDIN    = os.environ.get("INPUT_LINKEDIN_URL", "")
PODCAST     = os.environ.get("INPUT_PODCAST_URL", "")

def log(msg):
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    print(f"[{ts}] {msg}", flush=True)

async def run():
    from playwright.async_api import async_playwright

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={"width": 1400, "height": 900},
            user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()

        # ── Step 1: Log in ──────────────────────────────────────────────────────
        log("Navigating to MailerLite login...")
        await page.goto("https://dashboard.mailerlite.com/signin", wait_until="networkidle")
        await page.wait_for_timeout(1000)

        log("Filling credentials...")
        await page.fill('input[type="email"]', ML_EMAIL)
        await page.fill('input[type="password"]', ML_PASSWORD)
        await page.click('button[type="submit"]')
        await page.wait_for_load_state("networkidle")
        await page.wait_for_timeout(3000)

        current_url = page.url
        log(f"Post-login URL: {current_url}")
        if "signin" in current_url:
            log("ERROR: Still on signin page — check credentials")
            await browser.close()
            sys.exit(1)

        # ── Step 2: Open the email builder ──────────────────────────────────────
        builder_url = f"https://dashboard.mailerlite.com/emails/{EMAIL_ID}/edit"
        log(f"Opening builder: {builder_url}")
        await page.goto(builder_url, wait_until="networkidle")
        await page.wait_for_timeout(5000)
        log(f"Builder URL: {page.url}")

        # ── Step 3: Update thumbnail image ─────────────────────────────────────
        if IMAGE_URL:
            log(f"Updating thumbnail to: {IMAGE_URL}")
            try:
                # Click on the image block
                img = page.locator('img[src*="storage.mlcdn.com"]').first
                await img.click(timeout=10000)
                await page.wait_for_timeout(1500)

                # Look for image URL input in the settings panel
                url_input = page.locator('input[type="text"][ng-model*="src"], input[type="url"], input[placeholder*="URL"], input[placeholder*="url"]').first
                if await url_input.count() > 0:
                    await url_input.triple_click()
                    await url_input.fill(IMAGE_URL)
                    await page.wait_for_timeout(500)

                    # Save settings
                    save_btn = page.locator('button:has-text("Save settings"), button[type="submit"]').first
                    if await save_btn.count() > 0:
                        await save_btn.click()
                        await page.wait_for_timeout(1500)
                        log("Thumbnail URL updated")
                    else:
                        log("⚠️  Save button not found for image")
                else:
                    log("⚠️  Image URL input not found")
            except Exception as e:
                log(f"⚠️  Thumbnail update error: {e}")

        # ── Step 4: Update body copy ────────────────────────────────────────────
        if BODY_COPY:
            log("Updating body copy...")
            try:
                # Click somewhere neutral first to deselect
                await page.click('body', position={"x": 693, "y": 30})
                await page.wait_for_timeout(1000)

                # Find and click the body text block
                body_block = page.locator('[id*="bodyText"], td[id*="body"]').first
                await body_block.click(timeout=10000)
                await page.wait_for_timeout(2000)

                # The text editor appears in the right panel - find it
                text_editor = page.locator('.ql-editor, [contenteditable="true"]').last
                if await text_editor.count() > 0:
                    await text_editor.click()
                    await page.keyboard.press("Control+a")
                    await page.wait_for_timeout(300)

                    # Type the new body copy
                    await page.keyboard.type(BODY_COPY, delay=5)
                    await page.wait_for_timeout(500)

                    # Save settings
                    save_btn = page.locator('button:has-text("Save settings")').first
                    if await save_btn.count() > 0:
                        await save_btn.click()
                        await page.wait_for_timeout(1500)
                        log("Body copy updated")
                    else:
                        log("⚠️  Save button not found for body text")
                else:
                    log("⚠️  Text editor not found")
            except Exception as e:
                log(f"⚠️  Body copy update error: {e}")

        # ── Step 5: Update YouTube button links ─────────────────────────────────
        if YOUTUBE_URL:
            log(f"Updating YouTube links to: {YOUTUBE_URL}")
            try:
                # Find YouTube button by text content
                yt_btn = page.locator('a:has-text("YouTube"), td:has-text("YouTube")').first
                await yt_btn.click(timeout=10000)
                await page.wait_for_timeout(1500)

                # Find link input in settings panel
                link_input = page.locator('input[ng-model*="link"], input[placeholder*="link"], input[placeholder*="URL"]').first
                if await link_input.count() > 0:
                    await link_input.triple_click()
                    await link_input.fill(YOUTUBE_URL)
                    await page.wait_for_timeout(300)
                    save_btn = page.locator('button:has-text("Save settings")').first
                    if await save_btn.count() > 0:
                        await save_btn.click()
                        await page.wait_for_timeout(1000)
                        log("YouTube link updated")
                else:
                    log("⚠️  Link input not found for YouTube button")
            except Exception as e:
                log(f"⚠️  YouTube link update error: {e}")

        # ── Step 6: Update blog/website button link ─────────────────────────────
        if BLOG_URL:
            log(f"Updating blog link to: {BLOG_URL}")
            try:
                website_btn = page.locator('a:has-text("Website"), td:has-text("Website")').first
                await website_btn.click(timeout=10000)
                await page.wait_for_timeout(1500)

                link_input = page.locator('input[ng-model*="link"], input[placeholder*="link"], input[placeholder*="URL"]').first
                if await link_input.count() > 0:
                    await link_input.triple_click()
                    await link_input.fill(BLOG_URL)
                    await page.wait_for_timeout(300)
                    save_btn = page.locator('button:has-text("Save settings")').first
                    if await save_btn.count() > 0:
                        await save_btn.click()
                        await page.wait_for_timeout(1000)
                        log("Blog/website link updated")
                else:
                    log("⚠️  Link input not found for website button")
            except Exception as e:
                log(f"⚠️  Blog link update error: {e}")

        # ── Step 7: Click Done editing ──────────────────────────────────────────
        log("Clicking Done editing...")
        try:
            done_btn = page.locator('button:has-text("Done editing"), a:has-text("Done editing")').first
            await done_btn.click(timeout=10000)
            await page.wait_for_load_state("networkidle")
            await page.wait_for_timeout(2000)
            log(f"Done — final URL: {page.url}")
        except Exception as e:
            log(f"⚠️  Done editing click error: {e}")

        await browser.close()
        log("✅ Browser automation complete")

asyncio.run(run())
