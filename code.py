# import requests
# from bs4 import BeautifulSoup
# import pandas as pd


# url = "https://smartbid.co"

# headers = {
#     "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
#                   "AppleWebKit/537.36 (KHTML, like Gecko) "
#                   "Chrome/114.0.0.0 Safari/537.36"
# }


# response = requests.get(url, headers=headers)
# if response.status_code == 200:
#     soup = BeautifulSoup(response.text, "html.parser")
    
  
#     data = []
#     for link in soup.find_all("a", href=True):
#         text = link.get_text(strip=True)
#         href = link['href']
#         data.append({"text": text, "link": href})
    
   
#     df = pd.DataFrame(data)
#     df.to_csv("smartbid_data.csv", index=False, encoding="utf-8")
#     print("✅ Data saved to smartbid_data.csv")
# else:
#     print("❌ Failed to fetch webpage. Status:", response.status_code)     

# import requests
# from bs4 import BeautifulSoup
# import pandas as pd
# import time

# # ========================
# # CONFIG
# # ========================
# LOGIN_URL = "https://securecc.smartbidnet.com/Login.aspx?d=201606271114"
# TENDER_LIST_URL = "https://securecc.smartbidnet.com/Tender/List.aspx"  # replace with real page
# BASE_URL = "https://securecc.smartbidnet.com"

# USERNAME = "your_username"
# PASSWORD = "your_password"

# HEADERS = {
#     "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
#                   "AppleWebKit/537.36 (KHTML, like Gecko) "
#                   "Chrome/114.0.0.0 Safari/537.36"
# }

# # ========================
# # LOGIN
# # ========================
# session = requests.Session()
# session.headers.update(HEADERS)

# # Step 1: Load login page
# resp = session.get(LOGIN_URL)
# soup = BeautifulSoup(resp.text, "html.parser")

# # Extract hidden ASP.NET fields
# payload = {
#     "__VIEWSTATE": soup.find("input", {"name": "__VIEWSTATE"})["value"],
#     "__EVENTVALIDATION": soup.find("input", {"name": "__EVENTVALIDATION"})["value"],
#     "ctl00$MainContent$LoginUser$UserName": USERNAME,
#     "ctl00$MainContent$LoginUser$Password": PASSWORD,
#     "ctl00$MainContent$LoginUser$LoginButton": "Login"
# }

# # Step 2: Perform login
# login_resp = session.post(LOGIN_URL, data=payload)

# if "Logout" not in login_resp.text and "Welcome" not in login_resp.text:
#     print("❌ Login failed! Check credentials or field names.")
#     exit()
# print("✅ Login successful!")

# # ========================
# # GET TENDER LIST
# # ========================
# list_resp = session.get(TENDER_LIST_URL)
# if list_resp.status_code != 200:
#     print("❌ Unable to load tender list page.")
#     exit()

# soup = BeautifulSoup(list_resp.text, "html.parser")

# # Example: tender links have class "tender-link"
# tender_links = [BASE_URL + a["href"] for a in soup.find_all("a", class_="tender-link")]
# print(f"Found {len(tender_links)} tenders.")

# # ========================
# # SCRAPE EACH TENDER DETAIL
# # ========================
# all_data = []

# for url in tender_links:
#     detail_resp = session.get(url)
#     detail_soup = BeautifulSoup(detail_resp.text, "html.parser")

#     # Define field selectors (adjust using Inspect tool)
#     selectors = {
#         "Tender Name": ("h1", None),
#         "Bid Number": ("span", {"class": "bid-number"}),
#         "Owner": ("div", {"class": "owner"}),
#         "Date": ("span", {"class": "date"}),
#         "Pricing": ("div", {"class": "pricing"}),
#         "Location": ("span", {"class": "location"}),
#         "Status": ("span", {"class": "status"}),
#         "Description": ("div", {"class": "description"}),
#         "Contact": ("div", {"class": "contact-info"})
#     }

#     fields = {}
#     for field, (tag, attrs) in selectors.items():
#         el = detail_soup.find(tag, attrs) if attrs else detail_soup.find(tag)
#         fields[field] = el.get_text(strip=True) if el else "N/A"

#     all_data.append(fields)
#     time.sleep(1)  # avoid hammering server

# # ========================
# # SAVE TO CSV
# # ========================
# df = pd.DataFrame(all_data)
# df.to_csv("smartbid_tenders.csv", index=False, encoding="utf-8")
# print(f"✅ Extracted {len(all_data)} tenders and saved to smartbid_tenders.csv")


import requests
from bs4 import BeautifulSoup
import pandas as pd
import re

# Base site
BASE_URL = "https://smartbid.co"

# Start session
session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/114.0.0.0 Safari/537.36"
})

# Step 1: Get homepage
resp = session.get(BASE_URL)
soup = BeautifulSoup(resp.text, "html.parser")

# Step 2: Collect all internal links
links = [a['href'] for a in soup.find_all("a", href=True)
         if a['href'].startswith("http") and "smartbid.co" in a['href']]
links = list(set(links))  # unique

print(f"✅ Found {len(links)} public pages.")

data = []

# Step 3: Visit each page and extract info
for url in links:
    try:
        page = session.get(url, timeout=10)
        if page.status_code != 200:
            continue

        page_soup = BeautifulSoup(page.text, "html.parser")

        # Extract page title
        title = page_soup.find("title").get_text(strip=True) if page_soup.find("title") else "N/A"

        # Extract meta description
        meta_desc = page_soup.find("meta", attrs={"name": "description"})
        description = meta_desc['content'] if meta_desc else "N/A"

        # Extract first visible paragraph
        first_para = page_soup.find("p")
        if description == "N/A" and first_para:
            description = first_para.get_text(strip=True)

        # Extract emails and phone numbers
        emails = ", ".join(set(re.findall(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", page.text)))
        phones = ", ".join(set(re.findall(r"\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}", page.text)))

        data.append({
            "Title": title,
            "URL": url,
            "Description": description,
            "Emails": emails if emails else "N/A",
            "Phone Numbers": phones if phones else "N/A"
        })

    except Exception as e:
        print(f"⚠️ Skipping {url}: {e}")
        continue

# Step 4: Save results
df = pd.DataFrame(data)
df.to_csv("smartbid_public_data.csv", index=False, encoding="utf-8")
print("✅ Scraping complete. Data saved to smartbid_public_data.csv")
