import os

from dotenv import load_dotenv
from neo4j import GraphDatabase
import pandas as pd

class Neo4jConnector:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def create_graph(self, data):
        with self.driver.session() as session:
            try:
                # アドレスノードの作成
                session.run("""
                    UNWIND $addresses AS addr
                    MERGE (a:Address {address: addr})
                    ON CREATE SET a.created_at = datetime()
                """, addresses=list(set(data['from_address'].tolist() + data['to_address'].tolist())))
                
                print("ノードの作成完了")
                
                # トランザクション関係の作成
                session.run("""
                    UNWIND $pairs AS pair
                    MATCH (from:Address {address: pair.from})
                    MATCH (to:Address {address: pair.to})
                    MERGE (from)-[r]-(to)
                    ON CREATE SET r.created_at = datetime()
                """, pairs=[{'from': row['from_address'], 'to': row['to_address']} 
                          for _, row in data.iterrows()])
                print("リレーションシップの作成完了")
                
            except Exception as e:
                print(f"エラーが発生しました: {e}")
                raise

if __name__ == '__main__':
    # データの読み込み
    data = pd.read_csv('dataset/contracts.csv')
    
    # Neo4jへの接続情報
    load_dotenv('.env')

    URI = os.getenv("URI")
    AUTH = (os.getenv("USER"), os.getenv("PASSWORD"))
    
    # グラフの作成
    connector = Neo4jConnector(URI, auth=AUTH)
    try:
        connector.create_graph(data)
    finally:
        connector.close()
