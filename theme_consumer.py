# from kafka import KafkaConsumer
# import json
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt

# consumer = KafkaConsumer(
#     'naver_stock_topic',
#     bootstrap_servers='112.161.8.195:9092',
#     # bootstrap_servers=['localhost:9092'],
#     group_id='naver',  # 컨슈머 그룹 ID 설정
#     auto_offset_reset='earliest',
#     value_deserializer=lambda x: json.loads(x.decode('utf-8'))
# )
# print("Consumer is starting...")
# for m in consumer:
#     print(m.offset, m.value)
#     # break




# 데이터 준비
G = nx.Graph()
edges = [("A", "B"), ("A", "C"), ("B", "C"), ("C", "D")]
G.add_edges_from(edges)

# 랜덤 상태를 명시적으로 설정하지 않고 기본값 사용
pos = nx.spring_layout(G)

# 그래프 시각화
nx.draw(G, pos, with_labels=True, node_color='skyblue', node_size=2000, edge_color='k', linewidths=1, font_size=15)
plt.show()