import os
import requests
import snscrape.modules.twitter as sntwitter
import time

# دریافت اطلاعات از متغیرهای محیطی
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHANNEL_ID = os.getenv("TELEGRAM_CHANNEL_ID")
TWITTER_USERNAME = os.getenv("TWITTER_USERNAME")

# بررسی اینکه متغیرهای محیطی مقدار دارند
if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHANNEL_ID or not TWITTER_USERNAME:
    raise ValueError("❌ لطفاً مقادیر متغیرهای محیطی را در Render تنظیم کنید!")

def send_telegram_message(text):
    """ارسال پیام به تلگرام"""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHANNEL_ID, "text": text}
    requests.post(url, json=payload)

def get_latest_tweet(username):
    """دریافت آخرین توییت یک کاربر"""
    tweets = list(sntwitter.TwitterUserScraper(username).get_items())
    return tweets[0].content if tweets else None

# حلقه چک کردن توییت‌های جدید
last_tweet = None
while True:
    try:
        latest_tweet = get_latest_tweet(TWITTER_USERNAME)
        if latest_tweet and latest_tweet != last_tweet:
            send_telegram_message(f"📢 توییت جدید از @{TWITTER_USERNAME}:\n\n{latest_tweet}")
            last_tweet = latest_tweet
    except Exception as e:
        print(f"⚠️ خطا: {e}")
    
    time.sleep(60)  # چک کردن هر 60 ثانیه
