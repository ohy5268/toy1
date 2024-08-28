# Python 이미지를 기반으로 함
FROM python:3.9-slim

# 작업 디렉토리 설정
WORKDIR /app

# 필요한 패키지 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 데이터 수집 스크립트 복사
COPY . .

# 스크립트를 실행하도록 설정
CMD ["python", "producer.py"]
