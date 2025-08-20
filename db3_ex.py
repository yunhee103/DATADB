import MySQLdb
import pandas as pd
import matplotlib.pyplot as plt
import sys
import pickle
import csv
import seaborn as sns
import numpy as np

# 한글 폰트 설정 및 마이너스 부호 처리
plt.rc('font', family='malgun gothic')
plt.rcParams['axes.unicode_minus'] = False

# DB 연결 설정 파일을 불러오는 부분 (mymaria.dat)
# 이 파일이 없거나 오류가 발생하면 종료
try:
    with open('mymaria.dat', mode='rb') as obj:
        config = pickle.load(obj)
except Exception as e:
    print('DB 연결 설정 파일(mymaria.dat) 읽기 오류:', e)
    sys.exit()

conn = None # conn 변수 초기화
cursor = None # cursor 변수 초기화

try:
    # 1. MariaDB에 연결
    conn = MySQLdb.connect(**config)
    cursor = conn.cursor()

    print("DB 연결 성공")

    # =======================================================
    # a) MariaDB에 저장된 jikwon, buser, gogek 테이블을 이용하여 문제 해결
    # =======================================================
    print("\n\n=============== pandas 문제 7 - a) 시작 ===============")

    # 사번, 이름, 부서명, 연봉, 직급, 성별을 읽어 DataFrame 작성
    sql_jikwon = """
        SELECT
            j.jikwonno AS 사번,
            j.jikwonname AS 이름,
            b.busername AS 부서명,
            j.jikwonpay AS 연봉,
            j.jikwonjik AS 직급,
            j.jikwongen AS 성별
        FROM jikwon AS j
        INNER JOIN buser AS b ON j.busernum = b.buserno
    """
    
    # 쿼리 실행 후 fetchall()로 데이터 가져와 DataFrame 생성
    cursor.execute(sql_jikwon)
    rows = cursor.fetchall()
    df_jikwon = pd.DataFrame(rows, columns=['사번', '이름', '부서명', '연봉', '직급', '성별'])
    print("\n[DataFrame 작성 완료]")
    print(df_jikwon.head())

    # DataFrame의 자료를 파일로 저장
    file_name = 'jikwon_info.csv'
    df_jikwon.to_csv(file_name, index=False, encoding='utf-8')
    print(f"\n[DataFrame을 '{file_name}' 파일로 저장 완료]")
    
    # 부서명별 연봉의 합, 연봉의 최대/최소값 출력
    dept_salary_stats = df_jikwon.groupby('부서명')['연봉'].agg(['sum', 'max', 'min'])
    print("\n[부서명별 연봉 통계]")
    print(dept_salary_stats)

    # 부서명, 직급으로 교차 테이블(빈도표)을 작성
    cross_tab = pd.crosstab(df_jikwon['부서명'], df_jikwon['직급'])
    print("\n[부서명, 직급별 교차 테이블]")
    print(cross_tab)
    
    # 직원별 담당 고객자료(고객번호, 고객명, 고객전화)를 출력
    sql_customer = """
        SELECT
            j.jikwonname AS 직원명,
            g.gogekno AS 고객번호,
            g.gogekname AS 고객명,
            g.gogektel AS 고객전화
        FROM jikwon AS j
        LEFT JOIN gogek AS g ON j.jikwonno = g.gogekdamsano
        ORDER BY j.jikwonname
    """
    cursor.execute(sql_customer)
    print("\n[직원별 담당 고객 자료]")
    for (emp_name, cust_no, cust_name, cust_tel) in cursor:
        if cust_no is None:
            print(f"{emp_name} - 담당 고객 X")
        else:
            print(f"{emp_name} - 고객번호: {cust_no}, 고객명: {cust_name}, 전화: {cust_tel}")

    # 부서명별 연봉의 평균으로 가로 막대 그래프 작성
    dept_avg_salary = df_jikwon.groupby('부서명')['연봉'].mean()
    print("\n[부서명별 연봉 평균]")
    print(dept_avg_salary)

    plt.figure(figsize=(10, 6))
    sns.barplot(x=dept_avg_salary.values, y=dept_avg_salary.index)
    plt.title('부서명별 연봉 평균')
    plt.xlabel('연봉 평균')
    plt.ylabel('부서명')
    plt.show()

    # =======================================================
    # b) MariaDB에 저장된 jikwon 테이블을 이용하여 문제 해결
    # =======================================================
    print("\n\n=============== pandas 문제 7 - b) 시작 ===============")

    # pivot_table을 사용하여 성별 연봉의 평균을 출력
    pivot_avg_salary = df_jikwon.pivot_table(index='성별', values='연봉', aggfunc='mean')
    print("\n[성별 연봉 평균 (pivot_table)]")
    print(pivot_avg_salary)

    # 성별(남, 여) 연봉의 평균으로 시각화 - 세로 막대 그래프
    plt.figure(figsize=(8, 6))
    pivot_avg_salary.plot(kind='bar', rot=0)
    plt.title('성별 연봉 평균')
    plt.xlabel('성별')
    plt.ylabel('연봉 평균')
    plt.show()

    # 부서명, 성별로 교차 테이블을 작성
    cross_tab_b = pd.crosstab(df_jikwon['부서명'], df_jikwon['성별'])
    print("\n[부서명, 성별 교차 테이블]")
    print(cross_tab_b)
    
    # =======================================================
    # c) 키보드 로그인 기능
    # =======================================================
    print("\n\n=============== pandas 문제 7 - c) 시작 ===============")
    
    # 사용자로부터 사번과 직원명 입력받기
    try:
        user_jikwonno = input("사번 입력: ")
        user_jikwonname = input("직원명 입력: ")

        # 로그인 정보를 확인하는 SQL 쿼리 (jikwon, buser 테이블 조인)
        sql_login = """
            SELECT
                j.jikwonno,
                j.jikwonname,
                b.busername,
                j.jikwonjik,
                b.busertel,
                j.jikwongen
            FROM jikwon AS j
            INNER JOIN buser AS b ON j.busernum = b.buserno
            WHERE j.jikwonno = %s AND j.jikwonname = %s
        """
        cursor.execute(sql_login, (user_jikwonno, user_jikwonname))
        
        # 결과 가져오기
        login_result = cursor.fetchone()

        if login_result:
            print("\n로그인 성공!")
            print("사번\t직원명\t부서명\t직급\t부서전화\t성별")
            print("-" * 50)
            print(f"{login_result[0]}\t{login_result[1]}\t{login_result[2]}\t{login_result[3]}\t{login_result[4]}\t{login_result[5]}")

            # 전체 직원수 출력
            sql_count = "SELECT count(*) FROM jikwon"
            cursor.execute(sql_count)
            count_result = cursor.fetchone()
            print(f"\n인원수 : {count_result[0]} 명")

        else:
            print("\n로그인 실패: 사번 또는 직원명이 올바르지 않습니다.")
            
    except MySQLdb.OperationalError as e:
        print("MySQLdb OperationalError:", e)
    except Exception as e:
        print("로그인 처리 중 오류 발생:", e)


except MySQLdb.Error as e:
    print('DB 처리 오류:', e)
except Exception as e:
    print('일반 오류:', e)
finally:
    # 연결이 설정되었으면 항상 닫아줌
    if cursor:
        cursor.close()
    if conn:
        conn.close()
    print("DB 연결 종료")




