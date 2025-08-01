import asyncio
from playwright.async_api import async_playwright
import json
from datetime import datetime, timedelta, timezone
from urllib.parse import quote
from sentiment import analyze_sentiment
from constants import SEARCH_QUERY, TWEETS_FILE, DATA_FILE, DURATION_MINUTES, TIME_LIMIT_HOURS, MAX_RETRIES
import os

async def run():
    print("🚀 Launching browser...")
    retry_count = 0
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(viewport={'width': 1920, 'height': 1080})
        page = await context.new_page()

        print("🌐 Opening Twitter login...")
        await page.goto("https://twitter.com/login")
        input("⏸️ Please log in to Twitter in the browser window. Press Enter here when done...")

        search_url = f"https://twitter.com/search?q={quote(SEARCH_QUERY)}&src=typed_query&f=live"
        print("🔍 Searching Twitter for:", SEARCH_QUERY)
        await page.goto(search_url)
        await page.wait_for_timeout(5000)

        tweets = set()
        start_time = datetime.now(timezone.utc)
        end_time = start_time + timedelta(minutes=DURATION_MINUTES)
        recent_threshold = start_time - timedelta(hours=TIME_LIMIT_HOURS)

        print(f"⏰ Collecting tweets from last {TIME_LIMIT_HOURS} hours")

        while datetime.now(timezone.utc) < end_time:
            try:
                await page.wait_for_selector("article", timeout=10000)
                
                elements = await page.query_selector_all("article")
                initial_count = len(tweets)

                for el in elements:
                    try:
                        content_span = await el.query_selector("div[lang]")
                        time_element = await el.query_selector("time")

                        if content_span and time_element:
                            tweet_time_str = await time_element.get_attribute("datetime")
                            tweet_time = datetime.fromisoformat(tweet_time_str.replace("Z", "+00:00"))
                            
                            if tweet_time >= recent_threshold:
                                tweet_text = await content_span.inner_text()
                                tweets.add(tweet_text)
                    except Exception as e:
                        continue

                print(f"📝 Found {len(tweets)} unique tweets...")

                # Aggressive scrolling strategy
                for _ in range(5):
                    await page.evaluate("window.scrollBy(0, 1000)")
                    await page.wait_for_timeout(1000)

                # Check if we're getting new tweets
                if len(tweets) == initial_count:
                    retry_count += 1
                    print(f"⚠️ No new tweets found. Retry attempt {retry_count}/{MAX_RETRIES}")
                    
                    if retry_count >= MAX_RETRIES:
                        print("🛑 Maximum retry attempts reached. Stopping...")
                        break
                        
                    await page.reload()
                    await page.wait_for_timeout(3000)
                else:
                    retry_count = 0  # Reset counter when new tweets are found

            except Exception as e:
                retry_count += 1
                print(f"⚠️ Error during scrolling (attempt {retry_count}/{MAX_RETRIES}): {str(e)}")
                
                if retry_count >= MAX_RETRIES:
                    print("🛑 Maximum retry attempts reached. Stopping...")
                    break
                    
                await page.wait_for_timeout(2000)
                continue

        await browser.close()

        tweets_list = list(tweets)
        with open(TWEETS_FILE, "w", encoding='utf-8') as f:
            json.dump({
                "query": SEARCH_QUERY,
                "fetched_at": datetime.now(timezone.utc).isoformat(),
                "tweets": tweets_list
            }, f, indent=2, ensure_ascii=False)

        print(f"✅ Successfully saved {len(tweets_list)} tweets to {TWEETS_FILE}")
        return tweets_list

def update_data_json(score_data):
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            try:
                history = json.load(f)
                if isinstance(history, dict):
                    history = [history]
            except:
                history = []
    else:
        history = []

    history.insert(0, score_data)
    history = history[:20]

    with open(DATA_FILE, "w") as f:
        json.dump(history, f, indent=2)

if __name__ == "__main__":
    tweets = asyncio.run(run())
    if not tweets:
        print("❌ No tweets found in the specified time period!")
        exit(1)
        
    print("📊 Analyzing sentiment from tweets.json...")
    summary = analyze_sentiment(TWEETS_FILE)

    final_data = {
        "movie": "Kingdom",
        "last_updated": datetime.now(timezone.utc).isoformat(),
        "tweets_analyzed": len(tweets),
        "positive": summary.get("positive", 0),
        "neutral": summary.get("neutral", 0),
        "negative": summary.get("negative", 0),
        "rating": summary.get("rating", 0)
    }

    update_data_json(final_data)
    print(f"✅ Dashboard updated: {summary['rating']}/5 from {len(tweets)} tweets")
    
    file_path = os.path.abspath("data.json")
    os.system(f"open '{file_path}'")