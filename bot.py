import requests
from flask import Flask, request, jsonify
from atproto import Client, exceptions
import os
import certifi

app = Flask(__name__)

# تنظیمات از محیطی دریافت می‌شود
BLUESKY_HANDLE = os.getenv("BLUESKY_HANDLE")
BLUESKY_APP_PASSWORD = os.getenv("BLUESKY_APP_PASSWORD")
WEBHOOK_AUTH_TOKEN = os.getenv("WEBHOOK_AUTH_TOKEN")  # توکن امنیتی دلخواه

# تنظیم کلاینت BlueSky
client = Client()

def login_to_bluesky():
    """لاگین به حساب BlueSky با مدیریت خطاها"""
    try:
        client.login(
            identifier=BLUESKY_HANDLE,
            password=BLUESKY_APP_PASSWORD
        )
        return True, "✅ لاگین موفقیت‌آمیز بود!"
    except exceptions.LoginError as e:
        return False, f"❌ خطای لاگین: {e}"
    except Exception as e:
        return False, f"❌ خطای ناشناخته: {e}"

@app.route("/status", methods=["GET"])
def check_login_status():
    """بررسی وضعیت اتصال به BlueSky"""
    if client.session:
        return jsonify({
            "status": "connected",
            "did": client.session.did,
            "handle": client.session.handle
        }), 200
    return jsonify({"status": "not_connected"}), 401

@app.route("/post", methods=["POST"])
def send_post():
    """ارسال پست جدید با احراز هویت"""
    # بررسی توکن امنیتی
    if request.headers.get("X-Auth-Token") != WEBHOOK_AUTH_TOKEN:
        return jsonify({"error": "Unauthorized"}), 401
    
    data = request.json
    if not data or "text" not in data:
        return jsonify({"error": "متن پست الزامی است"}), 400
    
    text = data["text"]
    try:
        # ارسال پست
        client.send_post(text=text)
        return jsonify({"status": "پست ارسال شد!", "text": text}), 200
    except exceptions.NetworkError as e:
        return jsonify({"error": f"خطای شبکه: {e}"}), 500
    except Exception as e:
        return jsonify({"error": f"خطای ناشناخته: {e}"}), 500

@app.route("/webhook", methods=["POST"])
def webhook():
    """وب هوک برای پاسخ خودکار"""
    if request.headers.get("X-Auth-Token") != WEBHOOK_AUTH_TOKEN:
        return jsonify({"error": "Unauthorized"}), 401
    
    data = request.json
    text = data.get("text", "")
    
    if not text:
        return jsonify({"error": "متن پیام الزامی است"}), 400
    
    try:
        client.send_post(text=f"🔵 پاسخ خودکار: {text}")
        return jsonify({"status": "ok"}), 200
    except exceptions.NetworkError as e:
        return jsonify({"error": f"خطای شبکه: {e}"}), 500

if __name__ == "__main__":
    # لاگین اولیه
    login_success, message = login_to_bluesky()
    print(message)
    
    if login_success:
        port = os.getenv("PORT", 5000)  # دریافت پورت از محیط (برای Render)
        app.run(host="0.0.0.0", port=int(port))  # تنظیم پورت مناسب برای Render
    else:
        print("سرور راه‌اندازی نشد!")
