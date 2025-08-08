# local Database 연동 후 자료를 읽어 DataFrame에 저장

import sqlite3

sql = "create table if not exists test(product varchar(10), maker varchar(10), weight real, price integer)"
conn = sqlite3.connect(':memory:')  #실험용 랜에만 저장, testdb 파일로 저장
conn.execute(sql)
conn.commit()
# 한 개씩 추가
stmt = "insert into test values(?,?,?,?)"   #?를 써서 맵핑, 시큐어코딩에 위배
data1 = ('mouse','samsung', 12.5, 5000)  # 데이터 하나일땐 , 찍어줘야함 튜플(4,) //  (4)면 오류남
conn.execute(stmt, data1)
data2 = ('mouse2','samsung', 15, 8000)  
conn.execute(stmt, data2)

# 복수 개 추가
datas = [('mouse3','lg',22.5,15000),('mouse3','lg',22.5,15500)]
conn.executemany(stmt,datas)
cursor = conn.execute("select * from test")
rows = cursor.fetchall()
# print(rows[0], '', rows[1], rows[0][0])
for a in rows:
    print(a)

import pandas as pd
df = pd.DataFrame(rows, columns=['product', 'maker', 'weight', 'price'])
print(df)
# print(df.to_html)
df2 = pd.read_sql("select * from test", conn)  #관경 데이터는 구조가 갖춰져 있어서 구조를 맞춰야 함
print(df2)
print()
pdata = {
    'product' : ['연필', '볼펜', '지우개'],
    'maker' : ['동아', '모나미', '모나미'],
    'weight' : [1.5, 5.5, 10],
    'price' :  [500, 1000, 1500]


}
frame = pd.DataFrame(pdata)
print(frame)
frame.to_sql("test", conn, if_exists='append', index=False)    # sql 처리 

print('-------------------------------------')
df3 = pd.read_sql("select product, maker,price, weight as 무게 from test", conn)  #  sql 처리 - 관경 데이터는 구조가 갖춰져 있어서 구조를 맞춰야 함
print(df3)

cursor.close()
conn.close()


