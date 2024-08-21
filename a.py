"""
# z --> 주석
# R --> 리팩토링
# C --> 코드리뷰
# G --> 코드로 만들어줌
# M --> GPT로부터의 답
"""
import requests
from bs4 import BeautifulSoup
import pandas as pd

url = "https://finance.naver.com/sise/theme.naver?&page=1"

response = requests.get(url)
rescode = response.status_code  # 요청이 성공적으로 이루어졌는지 확인
print(response)

print(rescode)


# # BeautifulSoup 객체 생성
# soup = BeautifulSoup(response.text, "html.parser")
# # print(soup)
# # 테마 리스트 테이블 찾기
# table = soup.find("table", class_="type_1 theme")
# # print(table)
# data = []
# rows = table.find_all("tr")
# # print(rows)
# for row in rows:
#     cols = row.find_all("td")
#     if len(cols) > 0:  # 데이터가 있는 행인지 확인
#         print(cols)
#         break
# #         theme_name = cols[0].get_text(strip=True)
# #         up_down = cols[1].get_text(strip=True)
# #         change_rate = cols[2].get_text(strip=True)
# #         data.append([theme_name, up_down, change_rate])

# # # DataFrame으로 변환
# # df = pd.DataFrame(data, columns=["Theme", "Up/Down", "Change Rate"])

# # # 데이터 확인
# # print(df)