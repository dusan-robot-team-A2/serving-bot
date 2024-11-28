import sqlite3
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from ament_index_python.packages import get_package_share_directory
import os

class OrderManager:
    # 테이블: 생성
    def __init__(self):
        package_share_directory = get_package_share_directory('ssts')
        # 데이터베이스 파일 경로 생성
        self.order_db_path = os.path.join(package_share_directory, 'database', 'order_datas.db')
        self.menu_db_path = os.path.join(package_share_directory, 'database', 'menu.db') 

    def update_db(self, table_id, orders):
        self.insert_order(table_id, orders)

    # 테이블: 메뉴 구성
    def update_menu(self, input_menu):
        """
        입력 데이터를 기반으로 데이터베이스를 업데이트
        menu_id는 첫 메뉴부터 1로 순차적 부여
        ex)
        <input>
        input_menu = {
            '로스카츠': 10000,
            '히레카츠': 11000,
            '모둠카츠': 16000,
            '치즈카츠': 13000
        }

        <output>
        menu_id  menu_name  menu_price
        -------  ---------  ----------
        1        로스카츠       10000     
        2        히레카츠       11000     
        3        모둠카츠       16000     
        4        치즈카츠       13000  
        """

        # SQLite DB 연결
        conn = sqlite3.connect(self.menu_db_path)
        cursor = conn.cursor()

        # 테이블 생성
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS menu (
                menu_id INTEGER PRIMARY KEY AUTOINCREMENT,
                menu_name TEXT UNIQUE,
                menu_price INTEGER
            );
        ''')
        conn.commit()
        print("Table created (if it did not exist).")

        # 기존 데이터 초기화
        cursor.execute('DELETE FROM menu;')  # 테이블 비우기
        cursor.execute('DELETE FROM sqlite_sequence WHERE name = "menu";')  # AUTOINCREMENT 리셋
        conn.commit()
        print("Table(menu) cleared and menu_id reset.")

        # 입력 데이터 삽입
        for menu_name, menu_price in input_menu.items():
            cursor.execute('''
                INSERT INTO menu (menu_name, menu_price)
                VALUES (?, ?);
            ''', (menu_name, menu_price))
            print(f"Inserted: {menu_name} -> {menu_price}")

        # 변경 사항 커밋
        conn.commit()
        print("Database(menu.db) updated with input menu.")

        # 연결 종료
        conn.close()
        print("Database(menu.db) connection closed.")

    # 테이블: 주문수락 데이터 추출 및 삽입
    def insert_order(self, table_id, orders):
        time_stamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        """
        주문이 수락되면 database에 추가되도록 처리하며,
        menu 테이블이 비어 있는 경우 메시지를 출력합니다.
        ex)
        <input>
        place_order = {
            "table_id": 5,
            "orders": [
                {"menu_id": "1", "quantity": 2},
                {"menu_id": "2", "quantity": 2},
                {"menu_id": "3", "quantity": 2}
            ]
        }

        <result>
        order_id  time_stamp           table_id  menu_id  total_price
        --------  -------------------  --------  -------  -----------
        1         2024-11-27 13:52:31  5         1        10,000     
        2         2024-11-27 13:52:31  5         2        11,000     
        3         2024-11-27 13:52:31  5         3        12,000     
        4         2024-11-27 13:52:32  5         1        10,000   
        """
        # SQLite DB 연결
        conn = sqlite3.connect(self.order_db_path)  # 주문 데이터베이스 연결
        cursor = conn.cursor()

        # orders 테이블 생성
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS orders (
                order_id INTEGER PRIMARY KEY AUTOINCREMENT,
                time_stamp TEXT,
                table_id INTEGER,
                menu_id TEXT,
                total_price TEXT
            );
        ''')
        conn.commit()
        print("Table(orders) created (if it did not exist).")

        # 메뉴 데이터베이스(menu) 연결
        menu_conn = sqlite3.connect(self.menu_db_path)  # 메뉴 정보가 저장된 DB 연결
        menu_cursor = menu_conn.cursor()

        # 메뉴 테이블 확인
        menu_cursor.execute('SELECT COUNT(*) FROM menu;')
        menu_count = menu_cursor.fetchone()[0]  # 메뉴 데이터 개수 확인

        if menu_count == 0:
            print("Menu is empty. No orders can be processed.")
            menu_conn.close()
            print("Database(menu.db) connection closed.")
            return

        for order in orders:
            menu_id = order.menu_id
            quantity = order.quantity

            # menu 테이블에서 menu_id에 맞는 가격 조회
            menu_cursor.execute('SELECT menu_price FROM menu WHERE menu_id = ?;', (menu_id,))
            result = menu_cursor.fetchone()

            if result:
                menu_price = result[0]  # 가격 가져오기
                price = menu_price * quantity
                formatted_price = '{:,}'.format(price)

                # orders 테이블에 주문 데이터 삽입
                cursor.execute('''
                    INSERT INTO orders (time_stamp, table_id, menu_id, total_price)
                    VALUES (?, ?, ?, ?);
                ''', (time_stamp, table_id, menu_id, formatted_price))
                print(f"Order inserted: Menu ID {menu_id}, Quantity {quantity}, Total Price {formatted_price}")
            else:
                print(f"Error: Menu ID {menu_id} not found in the menu database.")

        # 커밋 및 연결 종료
        conn.commit()
        print("Order saved to database.")
        conn.close()
        print("Database(order_datas.db) connection closed.")
        menu_conn.close()
        print("Database(menu.db) connection closed.")

# 통계: 지난 한 달간의 일일매출을 시각화(꺾은선 그래프)
def generate_sales_graph():
    conn = sqlite3.connect(os.path.join(get_package_share_directory('ssts'), 'database', 'order_datas.db'))  # SQLite DB 연결
    cursor = conn.cursor()
    
    # 오늘 날짜 기준으로 한 달 전 날짜 계산
    one_month_ago = datetime.now() - timedelta(days=30)
    one_month_ago_str = one_month_ago.strftime('%Y-%m-%d')

    # 한 달 간의 매출 합산: 날짜별로 총 매출 계산
    cursor.execute('''
        SELECT strftime('%Y-%m-%d', time_stamp) AS date, 
               SUM(CAST(REPLACE(total_price, ',', '') AS INTEGER)) AS daily_sales
        FROM orders
        WHERE time_stamp >= ?
        GROUP BY date
        ORDER BY date;
    ''', (one_month_ago_str,))

    sales_data = cursor.fetchall()

    # 데이터가 있을 경우 꺾은선 그래프 생성
    if sales_data:
        # pandas DataFrame으로 변환
        df = pd.DataFrame(sales_data, columns=['Date', 'Daily Sales'])
        df['Date'] = pd.to_datetime(df['Date'])  # 날짜 형식 변환
        df['Daily Sales (KRW in 10k)'] = df['Daily Sales'] / 10000  # 만 원 단위로 변환

        # seaborn을 이용한 꺾은선 그래프
        plt.figure(figsize=(10, 6))
        ax = sns.lineplot(x='Date', y='Daily Sales (KRW in 10k)', data=df, marker='o', color='b')

        # 각 데이터 포인트에 값 표시 (만원 단위)
        for i, row in df.iterrows():
            ax.text(row['Date'], row['Daily Sales (KRW in 10k)'], 
                    f'{row["Daily Sales (KRW in 10k)"]:.1f} (10k)', 
                    color='black', ha='center', va='bottom')  # va는 value 위치 설정 (위쪽, 아래쪽)

    #     # 지난 한 달간의 기간 표시
    #     plt.xlabel('Date')
    #     plt.ylabel('Daily Sales (KRW in 10k)')
    #     plt.title(f'Daily Sales for the Last Month ({one_month_ago_str} to {datetime.now().strftime("%Y-%m-%d")})')
    #     plt.xticks(rotation=45)
    #     plt.grid(True)
    #     plt.tight_layout()
    #     plt.show()
    # else:
    #     # 데이터가 없으면 로그 메시지 출력
    #     print("No sales data available for the last month.")
    
    conn.close()


# 통계: 일주일간 요일 별 매출(막대 그래프), 수정 필요
# def generate_weekday_sales_graph():
#     conn = sqlite3.connect('database/order_chit.db')  # SQLite DB 연결
#     cursor = conn.cursor()
    
#     # 오늘 날짜 기준으로 7일 전 날짜 계산
#     one_week_ago = datetime.now() - timedelta(days=7)
#     one_week_ago_str = one_week_ago.strftime('%Y-%m-%d')

#     # 일주일 간의 매출 합산: 요일별로 총 매출 계산
#     cursor.execute('''
#         SELECT strftime('%Y-%m-%d', time_stamp) AS date, 
#                strftime('%w', time_stamp) AS weekday,  -- 요일을 숫자로 추출 (0: 일요일, 1: 월요일, ...)
#                total_price
#         FROM orders
#         WHERE time_stamp >= ?
#         ORDER BY date;
#     ''', (one_week_ago_str,))

#     sales_data = cursor.fetchall()  # 리스트로 저장 
#     print("Sales Data:", sales_data)  # sales_data 확인

#     # 데이터가 있을 경우 요일별 매출 계산 및 그래프 생성
#     if sales_data:
#         # pandas DataFrame으로 변환
#         df = pd.DataFrame(sales_data, columns=['Date', 'Weekday', 'Total Price'])

#         # 쉼표 제거 및 숫자 변환
#         df['Total Price'] = df['Total Price'].str.replace(',', '', regex=False).astype(float)
#         print("DataFrame after price conversion:", df)  # 데이터프레임 확인

#         # 만 원 단위로 변환한 'Daily Sales' 컬럼 추가
#         df['Daily Sales (KRW in 10k)'] = df['Total Price'] / 10000
#         print("DataFrame with Daily Sales:", df)  # Daily Sales 컬럼 확인

#         # 요일별 매출 합산
#         weekday_sales = df.groupby('Weekday')['Daily Sales (KRW in 10k)'].sum().reset_index()

#         # 요일 순서대로 DataFrame을 고정
#         weekdays = [0, 1, 2, 3, 4, 5, 6]  # 0: 일요일, 1: 월요일, ..., 6: 토요일
#         weekday_sales = weekday_sales.set_index('Weekday').reindex(weekdays).reset_index()

#         # NaN 값을 0으로 처리
#         weekday_sales['Daily Sales (KRW in 10k)'] = weekday_sales['Daily Sales (KRW in 10k)'].fillna(0)
#         print("Weekday Sales after filling NaN:", weekday_sales)  # NaN 처리 후 데이터 확인

#         # seaborn을 이용한 막대 그래프
#         plt.figure(figsize=(10, 6))
#         ax = sns.barplot(x='Weekday', y='Daily Sales (KRW in 10k)', data=weekday_sales, palette='Blues')

#         # 각 데이터 포인트에 값 표시 (만원 단위)
#         for i, row in weekday_sales.iterrows():
#             ax.text(i, row['Daily Sales (KRW in 10k)'], 
#                     f'{row["Daily Sales (KRW in 10k)"]:.1f} (10k)', 
#                     color='black', ha='center', va='bottom')

#         # Y축의 레이블을 만 원 단위로 표시
#         plt.xlabel('Day of the Week')
#         plt.ylabel('Total Sales (KRW in 10k)')
#         plt.title(f'Weekday Sales for the Last Week ({one_week_ago_str} to {datetime.now().strftime("%Y-%m-%d")})')

#         # X축 레이블을 회전하여 가독성 높이기
#         plt.xticks(rotation=45)

#         # X축 레이블을 숫자로 설정 (0: 일요일, 1: 월요일, ...)
#         plt.xticks(ticks=range(7), labels=['0', '1', '2', '3', '4', '5', '6'])

#         # 그리드 추가
#         plt.grid(True)

#         # 그래프 레이아웃을 최적화
#         plt.tight_layout()

#         # 그래프 출력
#         plt.show()
#     else:
#         # 데이터가 없으면 로그 메시지 출력
#         print("No sales data available for the last week.")

#     conn.close()





# 메뉴별 매출 시각화 (날짜 범위 입력)
def generate_menu_sales_graph(start_date, end_date):
    conn = sqlite3.connect(os.path.join(get_package_share_directory('ssts'), 'database', 'order_datas.db'))  # SQLite DB 연결
    cursor = conn.cursor()

    # 날짜 범위에 따른 메뉴별 매출 합산
    cursor.execute('''
        SELECT menu_id, 
               SUM(CAST(REPLACE(total_price, ',', '') AS INTEGER)) AS total_sales
        FROM orders
        WHERE time_stamp BETWEEN ? AND ?
        GROUP BY menu_id
        ORDER BY total_sales DESC;
    ''', (start_date, end_date))

    sales_data = cursor.fetchall()

    # 데이터가 있을 경우 메뉴별 매출 계산 및 그래프 생성
    if sales_data:
        # pandas DataFrame으로 변환
        df = pd.DataFrame(sales_data, columns=['Menu ID', 'Total Sales'])
        
        # 메뉴 ID를 문자열로 처리하고 매출을 만 원 단위로 변환
        df['Menu ID'] = df['Menu ID'].astype(str)
        df['Total Sales (KRW in 10k)'] = df['Total Sales'] / 10000  # 만 원 단위로 변환

        # seaborn을 이용한 막대 그래프
        plt.figure(figsize=(10, 6))
        ax = sns.barplot(x='Menu ID', y='Total Sales (KRW in 10k)', data=df, palette='Blues')
        
        # 각 데이터 포인트에 값 표시
        for i, row in df.iterrows():
            ax.text(row.name, row['Total Sales (KRW in 10k)'], 
                    f'{row["Total Sales (KRW in 10k)"]:.1f} (10k)', 
                    color='black', ha='center', va='bottom')

        # 그래프 제목 및 레이블
        plt.xlabel('Menu ID')
        plt.ylabel('Total Sales (KRW in 10k)')
        plt.title(f'Menu Sales from {start_date} to {end_date}')
        plt.xticks(rotation=45)
        plt.grid(True)
        plt.tight_layout()
        plt.show()

    else:
        # 데이터가 없으면 로그 메시지 출력
        print(f"No sales data available for the period from {start_date} to {end_date}.")
    
    conn.close()

def main():
    # OrderManager 객체 생성 및 데이터 삽입
    node = OrderManager()

    # # 메뉴와 가격 정보
    # menu_price = {
    #     "1": 10000,
    #     "2": 11000,
    #     "3": 12000
    # }

    # # 요청 예시 데이터
    # request = {
    #     "table_id": 5,
    #     "orders": [
    #         {"menu_id": "1", "quantity": 2},
    #         {"menu_id": "2", "quantity": 2},
    #         {"menu_id": "3", "quantity": 2}
    #     ]
    # }

    # 시작일과 종료일 입력받기 (YYYY-MM-DD 형식)
    start_date = "2024-11-01"
    end_date = "2024-11-28" # 28일을 포함하지 않음

    # 현재 시간 생성
    

    # # 데이터 삽입 실행
    # node.get_and_insert_order(request, menu_price, time_stamp)

    # 통계
    generate_sales_graph()
    # generate_weekday_sales_graph()
    generate_menu_sales_graph(start_date, end_date)

if __name__ == '__main__':
    main()