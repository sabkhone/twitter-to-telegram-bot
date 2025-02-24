import os
import snscrape.modules.twitter as sntwitter
import requests
from time import sleep

# تنظیمات محیطی
TELEGRAM_API_URL = "https://api.telegram.org/bot" + os.getenv("TELEGRAM_BOT_TOKEN") + "/sendMessage"
CHANNEL_ID = os.getenv("TELEGRAM_CHANNEL_ID")
TWITTER_HANDLE = os.getenv("TWITTER_HANDLE")

# تابع برای ارسال پیام به تلگرام
def send_to_telegram(message):
    payload = {
        'chat_id': CHANNEL_ID,
        'text': message
    }
    try:
        response = requests.post(TELEGRAM_API_URL, data=payload)
        response.raise_for_status()  # بررسی برای خطاهای HTTP
    except requests.exceptions.RequestException as e:
        print(f"خطا در ارسال پیام به تلگرام: {e}")

# تابع برای گرفتن آخرین پست‌های توییتر
def fetch_twitter_posts():
    tweets = sntwitter.TwitterUserScraper(TWITTER_HANDLE).get_items()
    for tweet in tweets:
        # ارسال متن توییت به تلگرام
        message = f"🧵 جدید از {TWITTER_HANDLE}:\n\n{tweet.content}"
        send_to_telegram(message)
        sleep(10)  # صبر برای جلوگیری از ارسال بیش از حد سریع

# اجرای تابع اسکراب توییتر به صورت منظم
if __name__ == "__main__":
    while True:
        fetch_twitter_posts()
        sleep(60)  # هر یک دقیقه یک بار پست‌های جدید رو چک می‌کنه
