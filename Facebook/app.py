from flask import Flask, request, jsonify, render_template
import csv
import json
from apify_client import ApifyClient
import sys

# ตั้งค่าภาษาไทย
sys.stdout.reconfigure(encoding='utf-8')

# สร้าง Flask App
app = Flask(__name__)

# ตั้งค่า Apify Client
client = ApifyClient("apify_api_94Yzgj5mMsob9slaokjQLcuUAt46e21oMatK")

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

if __name__ == '__main__':
    app.run(debug=True)
