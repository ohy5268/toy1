import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import logging
from abc import ABC, abstractmethod
import time
import os
from datetime import datetime
from kafka import KafkaProducer
import json

logging.basicConfig(level=logging.INFO)

# Kafka Producer 초기화 #toy1-kafka-1:9092
producer = KafkaProducer(bootstrap_servers='kafka:9092',
                         value_serializer=lambda v: json.dumps(v).encode('utf-8'))

def send_to_kafka(topic, data):
    producer.send(topic, value=data)
    producer.flush()

class ThemeScraper(ABC):
    def __init__(self, base_url, start_page, end_page):
        self.base_url = base_url
        self.start_page = start_page
        self.end_page = end_page

    def scrape(self):
        all_data = pd.DataFrame()
        for page in range(self.start_page, self.end_page + 1):
            logging.info(f"Fetching data from page {page}")
            url = self.build_url(page)
            html = self.fetch_html(url)
            data = self.parse_html(html)
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
        soup = BeautifulSoup(html, "html.parser")
        table = soup.find("table", class_="type_1 theme")
        if table is None:
            logging.error("Failed to find the theme table on the page.")
            raise Exception("Failed to find the theme table on the page.")

        data = []
        rows = table.find_all("tr")
        current_time = time.strftime('%Y-%m-%d %H:%M:%S')  # 현재 시간

        for row in rows:
            cols = row.find_all("td")
            if len(cols) > 0 and cols[0].get_text(strip=True):
                theme_name = cols[0].get_text(strip=True)
                link_tag = cols[0].find('a')
                mtch = re.search(r'no=(\d+)', link_tag['href']) if link_tag else None
                idx = mtch.group(1) if mtch else None
                up_down = cols[1].get_text(strip=True)
                change_rate = cols[2].get_text(strip=True)
                data.append([theme_name, up_down, change_rate, idx, current_time])

        # 데이터프레임 생성 후 Kafka에 전송
        df = pd.DataFrame(data, columns=["ThemeName", "UpDown", "ChangeRate", "idx", "collectTime"])
        for record in df.to_dict(orient="records"):
            # send_to_kafka('naver_stock_topic', record)
            send_to_kafka('naver_theme', record)

        return df


class NaverThemeDetailScraper(ThemeScraper):
    def __init__(self, base_url, idx):
        super().__init__(base_url, start_page=1, end_page=1)
        self.idx = idx  # idx를 저장

    def scrape(self):
        logging.info(f"Fetching data for idx {self.idx}")  # idx로 로그 출력

        # HTML 가져오기
        url = self.build_url(1)  # 페이지 1은 고정
        html = self.fetch_html(url)
        data = self.parse_html(html)

        return data

    def parse_html(self, html):
        soup = BeautifulSoup(html, "html.parser")
        table = soup.find("table", class_="type_5")
        if table is None:
            logging.error(f"Failed to find the detail table on the page.")
            raise Exception("Failed to find the detail table on the page.")

        data = []
        rows = table.find_all("tr")
        current_time = time.strftime('%Y-%m-%d %H:%M:%S')  # 현재 시간

        for row in rows:
            cols = row.find_all("td")
            if len(cols) > 0 and cols[0].get_text(strip=True):
                stock_name = cols[0].get_text(strip=True)
                # 코스피/코스닥 구분
                market = "코스닥" if '*' in stock_name else "코스피"
                stock_name = stock_name.replace('*', '').strip()
                
                # "테마 편입 사유" 제거
                inclusion_reason = cols[1].get_text(strip=True).replace("테마 편입 사유", "").strip()
                
                current_price = cols[2].get_text(strip=True)
                prev_day_diff = cols[3].get_text(strip=True)
                change_rate = cols[4].get_text(strip=True)
                buy_price = cols[5].get_text(strip=True)
                sell_price = cols[6].get_text(strip=True)
                volume = cols[7].get_text(strip=True)
                trading_value = cols[8].get_text(strip=True)
                prev_volume = cols[9].get_text(strip=True)

                data.append([
                    stock_name, market, inclusion_reason, current_price,
                    prev_day_diff, change_rate, buy_price,
                    sell_price, volume, trading_value,
                    prev_volume, current_time, self.idx
                ])

        # 데이터프레임 생성 후 Kafka에 전송
        df = pd.DataFrame(data, columns=[
            "stockName", "marketType", "reason", "currentPrice", "prevDayDiff", "changeRate",
            "buyPrice", "sellPrice", "volume", "tradingValue", "prevVolume", "currentTime", "idx"
        ])
        for record in df.to_dict(orient="records"):
            # send_to_kafka('naver_stock_topic', record)
            send_to_kafka('naver_stock', record)

        return df


def save_to_excel(df, directory, filename):
    if not os.path.exists(directory):
        os.makedirs(directory)
    file_path = os.path.join(directory, filename)
    df.to_excel(file_path, index=False)
    print(f"Data saved to {file_path}")


def main():
    # 현재 실행 중인 파이썬 파일의 디렉토리 위치 가져오기
    current_dir = os.path.dirname(os.path.abspath(__file__))

    # 현재 날짜로 폴더명 생성
    today_str = datetime.today().strftime('%Y%m%d')

    # 저장 디렉토리 설정 (현재 실행 중인 파이썬 파일의 디렉토리 내)
    base_dir = os.path.join(current_dir, "Data_Records", today_str)

    # 1. 테마 정보 수집 및 저장
    theme_scraper = NaverThemeScraper(base_url="https://finance.naver.com/sise/theme.naver?&type=theme", start_page=1, end_page=8)
    theme_df = theme_scraper.scrape()
    print("테마 정보 수집 완료:")
    # print(theme_df.head())

    # save_to_excel(theme_df, base_dir, "테마정보수집.xlsx")

    all_stock_data = pd.DataFrame()

    # 2. 각 테마의 idx를 사용하여 세부 종목 정보 수집 및 저장
    for idx in theme_df['idx']:
        detail_scraper = NaverThemeDetailScraper(base_url=f"https://finance.naver.com/sise/sise_group_detail.naver?type=theme&no={idx}", idx=idx)
        stock_df = detail_scraper.scrape()
        stock_df['테마 idx'] = idx  # 테마 idx 정보를 추가
        all_stock_data = pd.concat([all_stock_data, stock_df], ignore_index=True)

    print("세부 종목 정보 수집 완료:")
    # print(all_stock_data.head())

    # save_to_excel(all_stock_data, base_dir, "테마세부종목정보수집.xlsx")


if __name__ == "__main__":
    start_time = time.time()
    main()
    end_time = time.time()
    print(f"Elapsed Time : {end_time - start_time:.2f} seconds")
