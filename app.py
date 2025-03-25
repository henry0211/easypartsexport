from flask import Flask, request, send_file, render_template_string
import pandas as pd
import requests
from bs4 import BeautifulSoup
import os
from io import BytesIO

app = Flask(__name__)

HTML_FORM = """
<!DOCTYPE html>
<html>
<head>
    <title>easypartsexport.com</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            background-color: #f5f5f5;
        }
        .container {
            text-align: center;
            background-color: white;
            padding: 40px;
            border-radius: 10px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        }
        input[type="text"] {
            width: 80%;
            padding: 10px;
            font-size: 16px;
        }
        input[type="submit"] {
            padding: 10px 20px;
            font-size: 16px;
            background-color: #007BFF;
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
        }
        input[type="submit"]:hover {
            background-color: #0056b3;
        }
    </style>
</head>
<body>
    <div class="container">
        <h2>easypartsexport.com</h2>
        <form method="post">
            <label for="url">Enter OEM Parts Page URL:</label><br><br>
            <input type="text" id="url" name="url" required><br><br>
            <input type="submit" value="Scrape Parts">
        </form>
    </div>
</body>
</html>
"""

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        user_url = request.form['url']

        # TEMP: Replace this with your actual ScraperAPI key
        proxy_api_key = "your_actual_scraperapi_key_here"
        proxy_url = f"http://api.scraperapi.com/?api_key={proxy_api_key}&url={user_url}&render=true"

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Referer": "https://www.google.com/"
        }

        try:
            response = requests.get(proxy_url, headers=headers)
            response.raise_for_status()
        except Exception as e:
            return f"Error loading page: {e}"

        soup = BeautifulSoup(response.text, 'html.parser')
        rows = soup.select("div.c1a")
        part_data = []

        for index, row in enumerate(rows):
            try:
                part = row.get_text(strip=True)
                parent = row.find_parent()

                part_number_elem = parent.select_one("span.itemnum")
                part_number = part_number_elem.get_text(strip=True) if part_number_elem else ""

                qty_input = parent.select_one("input.qtyinput")
                qty = qty_input.get("value").strip() if qty_input else "1"

                if part:
                    part_data.append({"Ref#": str(index + 1), "Part": part, "Part Number": part_number, "QTY": qty})
            except:
                continue

        if not part_data:
            return "No part data found. Please check the URL and try again."

        df = pd.DataFrame(part_data)
        output = BytesIO()
        df.to_excel(output, index=False)
        output.seek(0)

        return send_file(output, download_name="oem_parts.xlsx", as_attachment=True)

    return render_template_string(HTML_FORM)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)