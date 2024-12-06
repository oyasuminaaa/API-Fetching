import tweepy
import csv
from datetime import datetime


#คีย์ที่ได้จาก Twitter Developer 
api_key = "3gIOgvNDslJwFQsPBrtJmlP7G"
api_secret_key = "KUqHdeui51m8GJrs92qW304h221j2ikGY4hUvyvyNa8C3X2Ysy"
access_token = "1774107847724609536-9AahyoX0zXKJiKMMpgq1tWs6yuqwRy "
access_token_secret = "bJQB2PE4f6sI6mkmbF5AYgCQibIdqMtxxqyTtQsCMxaU5"
bearer_token = "AAAAAAAAAAAAAAAAAAAAAD1dwwEAAAAAs7F0Ce%2F8xr3MzqZ5Uxrsq2eI7iA%3DnA6Uc7ckBft1U2QwAstuacJLrhSgkTKhzqlbku9xDIPo4skXm7 "

#ยืนยัน
client = tweepy.Client(bearer_token=bearer_token)

#ฟังก์ชันดึงข้อมูลโพสต์ตาม username
def get_multiple_users_tweets(usernames, max_results=10, csv_filename="Mix_tweets.csv"):
    # เปิดไฟล์ CSV เพื่อเขียนข้อมูล
    with open(csv_filename, mode='w', newline='', encoding='utf-8-sig') as file:
        writer = csv.writer(file)
        
        # เขียน header (คอลัมน์)
        writer.writerow(["Username", "Tweet Text", "Created At", "Link"])
        
        for username in usernames:
            try:
                # ค้นหา user id จาก username
                user = client.get_user(username=username)
                user_id = user.data.id

                # ดึงข้อมูลโพสต์จาก user id พร้อมวันที่โพสต์
                tweets = client.get_users_tweets(id=user_id, max_results=max_results, tweet_fields=["created_at"])

                # เขียนข้อมูลทวีตในไฟล์ CSV
                for tweet in tweets.data:
                    tweet_link = f"https://twitter.com/{username}/status/{tweet.id}"  # สร้างลิงก์ของโพสต์
                    created_at = tweet.created_at.strftime('%Y-%m-%d %H:%M:%S')  # แปลงวันที่เป็นสตริง
                    writer.writerow([username, tweet.text, created_at, tweet_link])
                
                print(f"Data for {username} has been written to {csv_filename}")
            except Exception as e:
                print(f"An error occurred for {username}: {e}")

# ใช้ฟังก์ชันนี้เพื่อดึงโพสต์จากหลายบัญชีและบันทึกลงในไฟล์ CSV
usernames = ["RedSkullxxx" ,"HoneKrasae"]  # รายการ username ที่ต้องการดึงข้อมูล
get_multiple_users_tweets(usernames, max_results=5, csv_filename="Mix_tweets.csv")