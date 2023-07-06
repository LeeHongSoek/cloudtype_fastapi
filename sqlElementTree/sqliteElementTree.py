import xml.etree.ElementTree as ET
import sqlite3

# XML 파일 읽기
tree = ET.parse('sqlElementTree\\queries.xml')
root = tree.getroot()

# SQLite 데이터베이스 연결
conn = sqlite3.connect('sqlElementTree\\users.db')
cursor = conn.cursor()

# 쿼리 실행
query_id = 'create_table'
if (query := root.find(f"query[@id='{query_id}']")) is not None:
    sql = query.text.strip()
    cursor.execute(sql)


# 쿼리 실행
query_id = 'insert_user'  # 실행할 쿼리의 id 지정

if (query := root.find(f"query[@id='{query_id}']")) is not None:
    sql = query.text.strip()

    # INSERT 쿼리에 실제 값 대입
    user_id = 2
    name = 'lee'
    age = 30

    cursor.execute(sql, (user_id, name, age))

# 변경 내용 저장 및 연결 종료
conn.commit()
conn.close()