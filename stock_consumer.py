from kafka import KafkaConsumer
import json
import mysql.connector

# 데이터베이스 연결 설정
db = mysql.connector.connect(
    host="mysql",
    user="root",
    passwd="root_password",
    database="naver_stock",
    # charset='utf8mb4',  # 이것은 문자셋
    # collation='utf8mb4_unicode_ci'  # 이것은 콜레이션
)
cursor = db.cursor()

# 데이터베이스의 캐릭터셋과 콜레이션 변경
cursor.execute("ALTER DATABASE {} CHARACTER SET = %s COLLATE = %s".format(db.database), ('utf8mb4', 'utf8mb4_unicode_ci'))
# 테이블의 캐릭터셋과 콜레이션 변경
cursor.execute("ALTER TABLE stock_data CONVERT TO CHARACTER SET %s COLLATE %s", ('utf8mb4', 'utf8mb4_unicode_ci'))


# 테마 정보 테이블 삭제
cursor.execute("""drop table if exists stock_data""")

# 주식 정보 테이블 생성
cursor.execute("""
CREATE TABLE IF NOT EXISTS stock_data (
    id INT AUTO_INCREMENT PRIMARY KEY,
    stockName VARCHAR(255),
    marketType VARCHAR(50),
    reason TEXT,
    currentPrice VARCHAR(50),
    prevDayDiff VARCHAR(50),
    changeRate VARCHAR(50),
    buyPrice VARCHAR(50),
    sellPrice VARCHAR(50),
    volume VARCHAR(50),
    tradingValue VARCHAR(50),
    prevVolume VARCHAR(50),
    currentTime DATETIME,
    idx INT
)
""")

consumer = KafkaConsumer(
    'naver_stock',
    # bootstrap_servers='112.161.8.195:9092',
    bootstrap_servers=['kafka:9092'],
    # bootstrap_servers=['localhost:9092'],
    group_id='naver',  # 컨슈머 그룹 ID 설정
    auto_offset_reset='earliest',
    value_deserializer=lambda x: json.loads(x.decode('utf-8'))
)
print("Consumer is starting...")

for m in consumer:
    print(m.offset, m.value)
    data = m.value
    sql = """INSERT INTO stock_data (stockName, marketType, reason, currentPrice, prevDayDiff, changeRate, 
             buyPrice, sellPrice, volume, tradingValue, prevVolume, currentTime, idx) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
    val = (data['stockName'], data['marketType'], data['reason'], data['currentPrice'], data['prevDayDiff'], 
           data['changeRate'], data['buyPrice'], data['sellPrice'], data['volume'], data['tradingValue'], 
           data['prevVolume'], data['currentTime'], data['idx'])
    cursor.execute(sql, val)
    db.commit()

db.close()