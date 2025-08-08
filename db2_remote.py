import MySQLdb # MySQL 데이터베이스 연결을 위한 라이브러리
import numpy as np # 수치 연산을 위한 라이브러리 (여기서는 직접 사용되지 않음)
import pandas as pd # 데이터 분석 및 조작을 위한 라이브러리
import matplotlib.pyplot as plt # 데이터 시각화를 위한 라이브러리
plt.rc('font', family='malgun gothic') # matplotlib에서 한글 폰트(맑은 고딕)를 사용하도록 설정
plt.rcParams['axes.unicode_minus'] = False # matplotlib에서 마이너스 기호가 깨지지 않도록 설정
import sys # 시스템 관련 기능을 사용하기 위한 라이브러리 (여기서는 프로그램 종료에 사용)
import pickle # 객체를 파일로 저장하고 불러오기 위한 라이브러리
import csv # csv 파일 읽기/쓰기를 위한 라이브러리

# 주석 처리된 DB 연결 정보
# conn = MySQLdb.connect(...)
# config = { ... }

try:
    # 'mymaria.dat' 파일에서 DB 연결 정보를 불러옴
    # pickle 모듈을 사용하여 딕셔너리 형태의 config 객체를 읽어옴
    with open('mymaria.dat', mode='rb') as obj:
        config = pickle.load(obj)

except Exception as e:
    # 파일 읽기 오류 발생 시, 오류 메시지 출력 후 프로그램 종료
    print('읽기오류 : ', e)
    sys.exit()

try:
    # 딕셔너리 unpacking(**config)을 사용하여 DB에 연결
    conn = MySQLdb.connect(**config)
    cursor = conn.cursor() # SQL 쿼리를 실행하기 위한 커서 객체 생성

    # JIKWON 테이블과 BUSER 테이블을 JOIN하여 필요한 컬럼을 선택하는 SQL 쿼리
    sql = """
        select jikwonno, jikwonname, busername, jikwonjik, jikwongen, jikwonpay
        from jikwon inner join buser
        on jikwon.busernum = buser.buserno
    """
    cursor.execute(sql) # SQL 쿼리 실행

    # 출력 1 : console
    # 실행 결과(cursor)를 반복문을 통해 한 줄씩 출력
    # for (a,b,c,d,e,f) in cursor: 와 같이 변수명을 지정하여 값을 가져옴
    for (jikwonno, jikwonname, busername, jikwonjik, jikwongen, jikwonpay) in cursor:
        print(jikwonno, jikwonname, busername, jikwonjik, jikwongen, jikwonpay)
    print()

    # 출력 2 : DataFrame
    # fetchall()을 사용하여 모든 데이터를 가져와 pandas DataFrame으로 생성
    # 컬럼 이름을 지정하여 가독성을 높임
    df1 = pd.DataFrame(cursor.fetchall(),
                       columns=['jikwonno', 'jikwonname', 'busername', 'jikwonjik', 'jikwongen', 'jikwonpay'])
    print(df1.head(3)) # DataFrame의 상위 3개 행 출력

    # 출력 3 : csv file -> csv 모듈 사용
    # 다시 SQL 쿼리를 실행하여 커서를 초기화 (for 문으로 데이터를 이미 읽었기 때문에)
    cursor.execute(sql)
    # 'jik_data.csv' 파일을 쓰기 모드(w)로 열고, CSV writer를 사용하여 데이터 저장
    with open('jik_data.csv', mode='w', encoding='utf-8') as fobj:
        writer = csv.writer(fobj)
        for r in cursor:
            writer.writerow(r) # 커서의 각 행을 csv 파일에 쓰기

    # csv 파일을 읽어 DataFrame에 저장
    # pandas.read_csv() 함수를 사용하여 'jik_data.csv' 파일을 읽어옴
    # header=None으로 헤더가 없음을 지정하고, names로 컬럼 이름 설정
    df2 = pd.read_csv('jik_data.csv', header=None,
                      names=['번호', '이름', '부서', '직급', '성별', '연봉'])
    print(df2.head(3))

    print('\nDB의 자료를 pandas의 sql처리 기능으로 읽기 --')
    # pandas.read_sql() 함수를 사용하여 DB에서 직접 DataFrame으로 데이터 읽기
    # SQL 쿼리와 DB 연결 객체를 인자로 전달
    df = pd.read_sql(sql, conn)
    # 컬럼 이름을 한글로 변경하여 가독성 향상
    df.columns = ['번호', '이름', '부서', '직급', '성별', '연봉']
    print(df.head(3))

    print('\nDB의 자료를 DataFrame으로 읽었으므로 pandas의 기능을 적용 가능 ---')
    # DataFrame의 다양한 기능 활용
    print('건 수 : ', len(df)) # DataFrame의 행(row) 개수 출력
    print('건 수 : ', df['이름'].count()) # '이름' 컬럼의 비결측치(non-null) 개수 출력
    print('직급별 인원 수 : ', df['직급'].value_counts()) # '직급'별 데이터 개수(빈도) 계산
    print('연봉 평균 : ', df.loc[:, '연봉'].mean()) # '연봉' 컬럼의 평균 계산
    print()

    # crosstab을 사용하여 성별과 직급에 따른 교차표(빈도수) 생성
    # margins=True를 통해 총합(All) 행과 열 추가
    ctab = pd.crosstab(df['성별'], df['직급'], margins=True)
    print(ctab)

    # 시각화 (직급별 연봉 평균) - 파이 그래프
    # groupby()와 mean()을 사용하여 직급별 연봉 평균 계산
    jik_ypay = df.groupby(['직급'])['연봉'].mean()
    print('직급별 연봉 평균 :', jik_ypay)
    print(jik_ypay.index) # 그룹화된 인덱스(직급) 출력
    print(jik_ypay.values) # 그룹화된 값(연봉 평균) 출력

    # 파이 그래프 생성
    # explode: 특정 조각을 강조하기 위해 중심에서 떨어뜨리는 정도
    # labels: 각 조각의 라벨
    # shadow: 그림자 효과 추가
    # labeldistance: 라벨과 원의 중심과의 거리
    # counterclock=False: 시계 방향으로 그래프 그리기 (기본값은 True로 반시계 방향)
    plt.pie(jik_ypay, explode=(0.2, 0, 0, 0.3, 0), labels=jik_ypay.index,
            shadow=True,
            labeldistance=0.7,
            counterclock=False)
    plt.show() # 그래프 화면에 표시

except Exception as e:
    # 예외 발생 시 오류 메시지 출력
    print('처리 오류: ', e)
finally:
    # 프로그램이 성공적으로 실행되거나 예외가 발생해도 항상 실행되는 부분
    # DB 연결을 닫아 리소스 해제
    conn.close()