import json

# 원본 데이터
record = {
    '종목명': '피에스케이홀딩스',
    '시장구분': '코스닥',
    '편입사유': '피에스케이홀딩스반도체 후공정 장비 사업을 주요 사업으로 영위하며, 반도체 후공정 Packaging 분야(WLP/FOWLP/FOPLP)에 Descum, Reflow 장비를 납품/양산 적용중. HBM(고대역폭메모리) 시장 개화 속 HBM 공정에 필요한 장비인 Descum, Reflow 장비를 납품/양산 중인 점이 부각.',
    '현재가': '49,300',
    '전일비': '하락6,700',
    '등락률': '-11.96%',
    '매수호가': '49,300',
    '매도호가': '49,350',
    '거래량': '847,215',
    '거래대금': '42,343',
    '전일거래량': '546,853',
    '수집시간': '2024-08-29 22:20:29'
}

# 데이터를 JSON 문자열로 인코딩
encoded_record = json.dumps(record, ensure_ascii=False).encode('utf-8')

# 인코딩된 데이터 출력
print("Encoded Data:")
print(encoded_record)

# 인코딩된 데이터를 다시 디코딩
decoded_record = json.loads(encoded_record.decode('utf-8'))

# 디코딩된 데이터 출력
print("Decoded Data:")
print(decoded_record)
