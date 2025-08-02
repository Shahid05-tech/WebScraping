import requests
from bs4 import BeautifulSoup
import pandas as pd

# Target website
url = "https://smartbid.co"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/114.0.0.0 Safari/537.36"
}

# Send request
response = requests.get(url, headers=headers)
if response.status_code == 200:
    soup = BeautifulSoup(response.text, "html.parser")
    
    # Example: Extract all links and text
    data = []
    for link in soup.find_all("a", href=True):
        text = link.get_text(strip=True)
        href = link['href']
        data.append({"text": text, "link": href})
    
    # Save to CSV
    df = pd.DataFrame(data)
    df.to_csv("smartbid_data.csv", index=False, encoding="utf-8")
    print("✅ Data saved to smartbid_data.csv")
else:
    print("❌ Failed to fetch webpage. Status:", response.status_code)      explain the code 