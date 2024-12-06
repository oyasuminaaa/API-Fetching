import tweepy
from flask import Flask, request, render_template
from datetime import datetime

app = Flask(__name__)

# คีย์ที่ได้จาก Twitter Developer 
api_key = "3gIOgvNDslJwFQsPBrtJmlP7G"
api_secret_key = "KUqHdeui51m8GJrs92qW304h221j2ikGY4hUvyvyNa8C3X2Ysy"
access_token = "1774107847724609536-9AahyoX0zXKJiKMMpgq1tWs6yuqwRy"
access_token_secret = "bJQB2PE4f6sI6mkmbF5AYgCQibIdqMtxxqyTtQsCMxaU5"
bearer_token = "AAAAAAAAAAAAAAAAAAAAAD1dwwEAAAAAs7F0Ce%2F8xr3MzqZ5Uxrsq2eI7iA%3DnA6Uc7ckBft1U2QwAstuacJLrhSgkTKhzqlbku9xDIPo4skXm7"

# ยืนยันการเชื่อมต่อ Twitter API
client = tweepy.Client(bearer_token=bearer_token)

# ฟังก์ชันดึงข้อมูลโพสต์จาก username
def get_multiple_users_tweets(usernames, max_results):
    all_tweets = []  # เก็บข้อมูลทวีตทั้งหมด
    for username in usernames:
        try:
            user = client.get_user(username=username)
            user_id = user.data.id

            tweets = client.get_users_tweets(id=user_id, max_results=max_results, tweet_fields=["created_at"])
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

@app.route('/')
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
