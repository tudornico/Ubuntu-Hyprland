import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

BASE_URL = "https://monitoruloficial.ro"
START_URL = "https://monitoruloficial.ro/acte-publicate-in-monitorul-oficial-partea-i/"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36"
}

def get_soup(url):
    resp = requests.get(url, headers=HEADERS, timeout=15)
    resp.raise_for_status()
    return BeautifulSoup(resp.text, "html.parser")

def parse_acte(soup):
    container = soup.find(id="dynamic_content")
    if not container:
        return []

    items = []
    for item in container.find_all("article"):
        title_tag = item.find("h2", class_="entry-title")
        title = title_tag.get_text(strip=True) if title_tag else ""

        link = ""
        if title_tag and title_tag.a:
            link = title_tag.a.get("href", "")

        publish_date = ""
        date_tag = item.find("time", class_="entry-date")
        if date_tag:
            publish_date = date_tag.get_text(strip=True)

        items.append({
            "title": title,
            "link": link,
            "publish_date": publish_date
        })
    return items

def find_next_page(soup):
    pag_ul = soup.find("ul", class_="pagination")
    if not pag_ul:
        return None

    # find the active current and next
    current = pag_ul.find("li", class_="active")
    if not current:
        return None

    next_li = current.find_next_sibling("li")
    if next_li and next_li.a:
        href = next_li.a.get("href")
        return href

    return None

def scrape_all():
    url = START_URL
    all_data = []
    page_num = 1

    while url:
        print(f"[INFO] Scraping page {page_num}: {url}")
        soup = get_soup(url)
        page_acts = parse_acte(soup)
        all_data.extend(page_acts)

        next_page = find_next_page(soup)
        if not next_page:
            break

        url = next_page
        page_num += 1

        time.sleep(1.2)  # be polite

    return all_data

def save(dataset):
    df = pd.DataFrame(dataset)
    df.to_csv("monitorul_official_dataset.csv", index=False)
    df.to_json("monitorul_official_dataset.json", orient="records", force_ascii=False)
    print(f"[OK] Saved CSV and JSON with {len(df)} items.")

if __name__ == "__main__":
    data = scrape_all()
    save(data)