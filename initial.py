#%%
import requests
from bs4 import BeautifulSoup
import pandas as pd
import re 
import time

url = "https://finance.naver.com/sise/theme.naver?&page=8"

response = requests.get(url)
rescode = response.status_code  # 요청이 성공적으로 이루어졌는지 확인

# BeautifulSoup 객체 생성
soup = BeautifulSoup(response.text, "html.parser")

# 테마 리스트 테이블 찾기
table = soup.find("table", class_="type_1 theme")

data = []
rows = table.find_all("tr")
# print(rows)
for row in rows:
    cols = row.find_all("td")
    if len(cols) > 0 and cols[0].get_text(strip=True):  # 데이터가 있는 행인지 확인
        theme_name  = cols[0].get_text(strip=True)
        mtch        = re.search(r'no=(\d+)', cols[0].find('a')['href'])
        idx         = mtch.group(1)
        up_down     = cols[1].get_text(strip=True)
        change_rate = cols[2].get_text(strip=True)
        data.append([theme_name, up_down, change_rate, idx])
# print(data)

# DataFrame으로 변환
df = pd.DataFrame(data, columns=["Theme", "Up/Down", "Change Rate", "idx"])

# 데이터 확인
df.head()


# %%
