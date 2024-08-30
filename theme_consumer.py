from kafka import KafkaConsumer
import mysql.connector
import json
import time

def connect_with_retry():
    connected = False
    attempts = 0
    while not connected and attempts < 5:
        try:
            db = mysql.connector.connect(
                host="mysql",
                user="root",
                passwd="root_password",
                database="naver_stock",
                # charset='utf8mb4',  # 이것은 문자셋
                # collation='utf8mb4_unicode_ci'  # 이것은 콜레이션
            )
            if db.is_connected():
                print("Successfully connected to MySQL")
                connected = True
                return db
            else:
                print("Waiting for MySQL to be ready...")
                time.sleep(10)
        except mysql.connector.Error as e:
            print(f"Error connecting to MySQL: {e}")
            attempts += 1
            time.sleep(10)
    if not connected:
        print("Failed to connect to MySQL after several attempts.")
        return None

# Use the connection
db = connect_with_retry()


# # 데이터베이스 연결 설정
# db = mysql.connector.connect(
#     host="mysql",
#     user="root",
#     passwd="root",
#     database="naver_stock"
# )
cursor = db.cursor()

"""
# 데이터베이스의 캐릭터셋과 콜레이션 변경
cursor.execute("ALTER DATABASE {} CHARACTER SET = %s COLLATE = %s".format(db.database), ('utf8mb4', 'utf8mb4_unicode_ci'))
# 테이블의 캐릭터셋과 콜레이션 변경
cursor.execute("ALTER TABLE theme_data CONVERT TO CHARACTER SET %s COLLATE %s", ('utf8mb4', 'utf8mb4_unicode_ci'))
"""

# 테마 정보 테이블 삭제
cursor.execute("""drop table if exists theme_data""")

# 테마 정보 테이블 생성
cursor.execute("""
CREATE TABLE IF NOT EXISTS theme_data (
    id INT AUTO_INCREMENT PRIMARY KEY,
    ThemeName VARCHAR(255),
    UpDown VARCHAR(50),
    ChangeRate VARCHAR(50),
    idx INT,
    collectTime DATETIME
)
""")

consumer = KafkaConsumer(
    'naver_theme',
    # bootstrap_servers='112.161.8.195:9092',
    bootstrap_servers=['kafka:9092'],
    # bootstrap_servers=['localhost:9092'],
    group_id='naver',  # 컨슈머 그룹 ID 설정
    auto_offset_reset='earliest',
    value_deserializer=lambda x: json.loads(x.decode('utf-8'))
)
print("Consumer is starting...")

for m in consumer:
    # print(m.offset, m.value)
    data = m.value
    print(m.offset, m.value)
    sql = "INSERT INTO theme_data (ThemeName, UpDown, ChangeRate, idx, collectTime) VALUES (%s, %s, %s, %s, %s)"
    val = (data['ThemeName'], data['UpDown'], data['ChangeRate'], data['idx'], data['collectTime'])
    cursor.execute(sql, val)
    db.commit()

db.close()

# import pandas as pd
# import networkx as nx
# import matplotlib.pyplot as plt

# # 데이터 준비
# G = nx.Graph()
# edges = [("A", "B"), ("A", "C"), ("B", "C"), ("C", "D")]
# G.add_edges_from(edges)

# # 랜덤 상태를 명시적으로 설정하지 않고 기본값 사용
# pos = nx.spring_layout(G)

# # 그래프 시각화
# nx.draw(G, pos, with_labels=True, node_color='skyblue', node_size=2000, edge_color='k', linewidths=1, font_size=15)
# plt.show()