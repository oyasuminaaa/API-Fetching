import csv
import json
from apify_client import ApifyClient
import sys

# ตั้งค่าภาษาไทย
sys.stdout.reconfigure(encoding='utf-8')

# API
client = ApifyClient("apify_api_94Yzgj5mMsob9slaokjQLcuUAt46e21oMatK")

# กำหนดค่า
run_input = {
    "startUrls": [
        {"url": "https://www.facebook.com/HKS2017/"},
        {"url": "https://www.facebook.com/DramaAdd/"},
        {"url": "https://www.facebook.com/ejan2016/"},
        {"url": "https://www.facebook.com/khobsanung/"},
        {"url": "https://www.facebook.com/newsth.18/"}
    ],
    "resultsLimit": 40 ,
    "proxyConfiguration": {
        "useApifyProxy": True,
        "apifyProxyGroups": ["RESIDENTIAL"]
    },
}

# เรียกใช้งาน Actor
run = client.actor("KoJrdxJCTtpon81KY").call(run_input=run_input)

# ตรวจสอบสถานะ
if run["status"] != "SUCCEEDED":
    print(f"Actor ทำงานไม่สำเร็จ: {run['status']}")
    sys.exit()

# เตรียมข้อมูลสำหรับบันทึก
data = []

for item in client.dataset(run["defaultDatasetId"]).iterate_items():
    # ตรวจสอบฟิลด์ที่มีอยู่
    page_name = item.get("pageName", "ไม่ระบุชื่อเพจ")  # ตรวจสอบว่า "pageName" มีหรือไม่
    post_text = item.get("text", "ไม่มีข้อความ")
    post_date = item.get("time", "ไม่ระบุวันที่")
    post_link = item.get("topLevelUrl", "ไม่มีลิงก์")

    # เพิ่มข้อมูลลงในลิสต์
    data.append({
        'pageName': page_name,
        'postText': post_text,
        'postDate': post_date,
        'postLink': post_link
    })

# บันทึกข้อมูลในไฟล์ CSV
csv_file = "facebook_posts.csv"
with open(csv_file, 'w', newline='', encoding='utf-8-sig') as csvfile:
    fieldnames = ['pageName', 'postText', 'postDate', 'postLink']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(data)

print(f"บันทึกข้อมูลลงไฟล์ CSV: {csv_file} เรียบร้อย")

# บันทึกข้อมูลในไฟล์ JSON
json_file = "facebook_posts.json"
with open(json_file, 'w', encoding='utf-8-sig') as jsonfile:
    json.dump(data, jsonfile, ensure_ascii=False, indent=4)

print(f"บันทึกข้อมูลลงไฟล์ JSON: {json_file} เรียบร้อย")
