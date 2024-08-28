import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import logging
from abc import ABC, abstractmethod
import time

logging.basicConfig(level=logging.INFO)

class ThemeScraper(ABC):
    def __init__(self, base_url, start_page, end_page):
        self.base_url   = base_url
        self.start_page = start_page
        self.end_page   = end_page

    def scrape(self):
        all_data = pd.DataFrame()
        for page in range(self.start_page, self.end_page + 1):
            logging.info(f"Fetching data from page {page}")
            url      = self.build_url(page)
            html     = self.fetch_html(url)
            data     = self.parse_html(html)
            all_data = pd.concat([all_data, data], ignore_index=True)
        return all_data

    def build_url(self, page_number):
        return f"{self.base_url}&page={page_number}"

    def fetch_html(self, url):
        response = requests.get(url)
        if response.status_code != 200:
            logging.error(f"Failed to fetch data from {url}")
            raise Exception(f"Failed to fetch data from {url}")
        return response.text

    @abstractmethod
    def parse_html(self, html):
        pass

class NaverThemeScraper(ThemeScraper):
    def parse_html(self, html):
        soup  = BeautifulSoup(html, "html.parser")
        table = soup.find("table", class_="type_1 theme")
        if table is None:
            logging.error("Failed to find the theme table on the page.")
            raise Exception("Failed to find the theme table on the page.")

        data = []
        rows = table.find_all("tr")

        for row in rows:
            cols = row.find_all("td")
            if len(cols) > 0 and cols[0].get_text(strip=True):
                theme_name  = cols[0].get_text(strip=True)
                link_tag    = cols[0].find('a')
                mtch        = re.search(r'no=(\d+)', link_tag['href']) if link_tag else None
                idx         = mtch.group(1) if mtch else None
                up_down     = cols[1].get_text(strip=True)
                change_rate = cols[2].get_text(strip=True)
                data.append([theme_name, up_down, change_rate, idx])

        return pd.DataFrame(data, columns=["Theme_name", "Up/Down", "Change Rate", "idx"])

# 사용 예시
st = time.time()

scraper = NaverThemeScraper(base_url="https://finance.naver.com/sise/theme.naver?&type=theme", start_page=1, end_page=8)
df = scraper.scrape()
ed = time.time()

print(len(df), df.head())
print(f'Elapsed Time : {ed-st:.2f}s')    

df.to_excel("result.xlsx")