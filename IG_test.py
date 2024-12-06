import sys
import csv
sys.stdout.reconfigure(encoding='utf-8')  # ตั้งค่า encoding ของ stdout เป็น UTF-8
from apify_client import ApifyClient

# Initialize the ApifyClient with your API token
client = ApifyClient("apify_api_94Yzgj5mMsob9slaokjQLcuUAt46e21oMatK")

page_scrape = [
    "https://www.instagram.com/thairath/",
    "https://www.instagram.com/thestandardth.ig/",
    "https://www.instagram.com/sanook.com/" 
]

# Prepare the Actor input
run_input = {
    "directUrls":page_scrape,  # ใส่ URL ของเพจ Instagram ในแบบ list
    "resultsType": "posts",  # เลือกผลลัพธ์แบบโพสต์
    "resultsLimit": 5,  # จำนวนโพสต์ที่ต้องการดึงข้อมูล
    "addParentData": True,  # เพื่อเพิ่มข้อมูลของเพจ
}

# Run the Actor and wait for it to finish
run = client.actor("apify/instagram-scraper").call(run_input=run_input)

# Fetch and print Actor results from the run's dataset
for item in client.dataset(run["defaultDatasetId"]).iterate_items():
    # ดึงข้อมูลที่ต้องการ: ชื่อเพจ, ข้อความ, ลิงก์ และวันที่โพสต์
    page_name = item.get("ownerFullName","N/A")
    text = item.get("caption", "No caption")
    post_url = item.get("url", "No URL")
    post_date = item.get("timestamp", "No date")
    
    # แสดงผล
    print(f"Page Name: {page_name}")
    print(f"Text: {text}")
    print(f"Post URL: {post_url}")
    print(f"Post Date: {post_date}")
    print("--*--" * 50)

csv_file = "Instargram.csv"
with open(csv_file, 'w', newline='', encoding='utf-8-sig') as csvfile:
    fieldnames = ['Page Name', 'Text', 'Post URL', 'Post Date']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(data)