from flask import Flask, request, jsonify, render_template
import csv
import json
from apify_client import ApifyClient
import sys
import tweepy

# ตั้งค่าภาษาไทย
sys.stdout.reconfigure(encoding='utf-8')

# สร้าง Flask App
app = Flask(__name__)

# ตั้งค่า Apify Client
client = ApifyClient("apify_api_94Yzgj5mMsob9slaokjQLcuUAt46e21oMatK")

# คีย์ที่ได้จาก Twitter Developer 
api_key = "3gIOgvNDslJwFQsPBrtJmlP7G"
api_secret_key = "KUqHdeui51m8GJrs92qW304h221j2ikGY4hUvyvyNa8C3X2Ysy"
access_token = "1774107847724609536-9AahyoX0zXKJiKMMpgq1tWs6yuqwRy"
access_token_secret = "bJQB2PE4f6sI6mkmbF5AYgCQibIdqMtxxqyTtQsCMxaU5"
bearer_token = "AAAAAAAAAAAAAAAAAAAAAD1dwwEAAAAAs7F0Ce%2F8xr3MzqZ5Uxrsq2eI7iA%3DnA6Uc7ckBft1U2QwAstuacJLrhSgkTKhzqlbku9xDIPo4skXm7"

# ยืนยันการเชื่อมต่อ Twitter API
tweet_client = tweepy.Client(bearer_token=bearer_token)

@app.route('/')
def index():
    return render_template('index.html')  # หน้า HTML สำหรับกรอกข้อมูล

@app.route('/fetch', methods=['POST'])
def fetch_facebook_data():
    try:
        # รับค่า Input จากหน้าเว็บ
        urls = request.form.get('urls')  # รับค่า URL ของเพจ (คั่นด้วยบรรทัดใหม่)
        results_limit = int(request.form.get('results_limit', 40))  # จำนวนโพสต์ที่ต้องการดึงข้อมูล

        # แปลง URL ที่รับมาเป็นลิสต์
        start_urls = [{"url": url.strip()} for url in urls.splitlines() if url.strip()]

        # ตรวจสอบว่ามี URL ที่ส่งเข้ามาหรือไม่
        if not start_urls:
            return jsonify({"error": "กรุณาระบุ URL ของเพจอย่างน้อยหนึ่งรายการ"}), 400

        # กำหนดค่า run_input
        run_input = {
            "startUrls": start_urls,
            "resultsLimit": results_limit,
            "proxyConfiguration": {
                "useApifyProxy": True,
                "apifyProxyGroups": ["RESIDENTIAL"]
            },
        }

        # เรียกใช้งาน Actor
        run = client.actor("KoJrdxJCTtpon81KY").call(run_input=run_input)

        # ตรวจสอบสถานะ
        if run["status"] != "SUCCEEDED":
            return jsonify({"error": f"Actor ทำงานไม่สำเร็จ: {run['status']}"}), 500

        # เตรียมข้อมูลสำหรับบันทึก
        data = []
        for item in client.dataset(run["defaultDatasetId"]).iterate_items():
            page_name = item.get("pageName", "ไม่ระบุชื่อเพจ")
            post_text = item.get("text", "ไม่มีข้อความ")
            post_date = item.get("time", "ไม่ระบุวันที่")
            post_link = item.get("topLevelUrl", "ไม่มีลิงก์")

            data.append({
                'pageName': page_name,
                'postText': post_text,
                'postDate': post_date,
                'postLink': post_link
            })

        # บันทึกข้อมูลในไฟล์ CSV
        csv_file = "facebook_posts1.csv"
        with open(csv_file, 'w', newline='', encoding='utf-8-sig') as csvfile:
            fieldnames = ['pageName', 'postText', 'postDate', 'postLink']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)

        # บันทึกข้อมูลในไฟล์ JSON
        json_file = "facebook_posts1.json"
        with open(json_file, 'w', encoding='utf-8-sig') as jsonfile:
            json.dump(data, jsonfile, ensure_ascii=False, indent=4)

        return jsonify({
            "message": "ดึงข้อมูลและบันทึกสำเร็จ",
            "csv_file": csv_file,
            "json_file": json_file,
            "data": data
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Route สำหรับดึงข้อมูล Instagram
@app.route('/pull', methods=['POST'])
def fetch_instagram_data():
    try:
        # รับค่าอินพุตจากฟอร์ม
        urls = request.form.get('urls')  # URLs เป็นข้อความหลายบรรทัด
        results_limit = int(request.form.get('results_limit', 40))  # ค่า default เป็น 40

        # ตรวจสอบว่ามี URL หรือไม่
        start_urls = [url.strip() for url in urls.splitlines() if url.strip()]
        if not start_urls:
            return jsonify({"error": "กรุณาระบุ URL อย่างน้อย 1 รายการ"}), 400

        # ตั้งค่าข้อมูลสำหรับ Apify Actor
        run_input = {
            "directUrls": start_urls,
            "resultsType": "posts",
            "resultsLimit": results_limit,
            "addParentData": True,
        }

        # เรียกใช้ Actor บน Apify
        run = client.actor("apify/instagram-scraper").call(run_input=run_input)

        # ตรวจสอบสถานะการทำงาน
        if run["status"] != "SUCCEEDED":
            return jsonify({"error": f"Actor ทำงานไม่สำเร็จ: {run['status']}"}), 500

        # ดึงผลลัพธ์จาก Dataset
        data = []
        for item in client.dataset(run["defaultDatasetId"]).iterate_items():
            page_name = item.get("ownerFullName", "N/A")
            text = item.get("caption", "No caption")
            post_url = item.get("url", "No URL")
            post_date = item.get("timestamp", "No date")

            data.append({
                'Page Name': page_name,
                'Text': text,
                'Post URL': post_url,
                'Post Date': post_date,
            })

        # บันทึกข้อมูลลง CSV
        csv_file = "Instagram.csv"
        with open(csv_file, 'w', newline='', encoding='utf-8-sig') as csvfile:
            fieldnames = ['Page Name', 'Text', 'Post URL', 'Post Date']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)

        # ส่งผลลัพธ์กลับไปยังผู้ใช้
        return jsonify({"message": "Data fetched and saved successfully.", "file": csv_file}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
#tweet
def get_multiple_users_tweets(usernames, max_results):
    all_tweets = []  # เก็บข้อมูลทวีตทั้งหมด
    for username in usernames:
        try:
            user = tweet_client.get_user(username=username)
            user_id = user.data.id

            tweets = tweet_client.get_users_tweets(id=user_id, max_results=max_results, tweet_fields=["created_at"])
            for tweet in tweets.data:
                tweet_link = f"https://twitter.com/{username}/status/{tweet.id}"
                created_at = tweet.created_at.strftime('%Y-%m-%d %H:%M:%S')
                all_tweets.append({
                    "username": username,
                    "tweet_text": tweet.text,
                    "created_at": created_at,
                    "link": tweet_link
                })
        except Exception as e:
            print(f"An error occurred for {username}: {e}")
    return all_tweets

def index():
    return render_template('index.html')

@app.route('/get_tweets', methods=['POST'])
def get_tweets():
    usernames = request.form.get("usernames").split(",")  # รับ usernames จากฟอร์ม
    max_results = int(request.form.get("max_results"))    # รับจำนวนโพสต์สูงสุดจากฟอร์ม

    tweetss = get_multiple_users_tweets(usernames, max_results)
    
    return render_template('index.html', tweets=tweetss)

if __name__ == '__main__':
    app.run(debug=True)
