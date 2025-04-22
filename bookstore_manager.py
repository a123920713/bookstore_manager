import sqlite3

DB_NAME = 'D:/Web程式設計/bookstore_manager/bookstore.db'

def check_db()->None:
    try:
        print(create_db(DB_NAME))
    except sqlite3.IntegrityError :
        print("")
        print("資料表已存在，無須新增資料表")
        print("")
    #檢查資料表是否存在

def create_db(db_name:str)-> str:
    with sqlite3.connect(db_name) as conn:
        conn.row_factory = sqlite3.Row  # 使查詢結果可以用欄位名稱存取
        cursor = conn.cursor()

        # 建立資料表
        cursor.executescript('''
        CREATE TABLE IF NOT EXISTS member (
            mid TEXT PRIMARY KEY,
            mname TEXT NOT NULL,
            mphone TEXT NOT NULL,
            memail TEXT
        );

        CREATE TABLE IF NOT EXISTS book (
            bid TEXT PRIMARY KEY,
            btitle TEXT NOT NULL,
            bprice INTEGER NOT NULL,
            bstock INTEGER NOT NULL
        );

        CREATE TABLE IF NOT EXISTS sale (
            sid INTEGER PRIMARY KEY AUTOINCREMENT,
            sdate TEXT NOT NULL,
            mid TEXT NOT NULL,
            bid TEXT NOT NULL,
            sqty INTEGER NOT NULL,
            sdiscount INTEGER NOT NULL,
            stotal INTEGER NOT NULL
        );
    ''')
        members = [
        ('M001', 'Alice', '0912-345678', 'alice@example.com'),
        ('M002', 'Bob', '0923-456789', 'bob@example.com'),
        ('M003', 'Cathy', '0934-567890', 'cathy@example.com')
        ]
        books = [
        ('B001', 'Python Programming', 600, 50),
        ('B002', 'Data Science Basics', 800, 30),
        ('B003', 'Machine Learning Guide', 1200, 20)
        ]
        sales = [
        ('2024-01-15', 'M001', 'B001', 2, 100, 1100),
        ('2024-01-16', 'M002', 'B002', 1, 50, 750),
        ('2024-01-17', 'M001', 'B003', 3, 200, 3400),
        ('2024-01-18', 'M003', 'B001', 1, 0, 600)
        ]
        # 插入會員資料
        cursor.executemany(
            "INSERT INTO member (mid, mname, mphone, memail) VALUES (?, ?, ?, ?)",
            members
        )
        conn.commit()
        # 插入書籍資料
        cursor.executemany(
            "INSERT INTO book (bid, btitle, bprice, bstock) VALUES (?, ?, ?, ?)",
            books
        )
        conn.commit()
        # 插入銷售資料（注意：不要插入 sid，因為它是 AUTOINCREMENT，自動產生）
        cursor.executemany(
            "INSERT INTO sale (sdate, mid, bid, sqty, sdiscount, stotal) VALUES (?, ?, ?, ?, ?, ?)",
            sales
        )
        conn.commit()
    return f'{db_name} 產生成功'

def check_id(db_name:str,mid:str,bid:str)->bool:
    with sqlite3.connect(db_name) as conn:
        cursor = conn.cursor()
        try:
            # 檢查會員是否存在
            cursor.execute('SELECT 1 FROM member WHERE mid = ?', (mid,))
            member_exists = cursor.fetchone() is not None

            # 檢查書籍是否存在
            cursor.execute('SELECT 1 FROM book WHERE bid = ?', (bid,))
            book_exists = cursor.fetchone() is not None

            if not member_exists or not book_exists:
                return False
            return True
        except sqlite3.Error as error:
            print(f"執行 SELECT 操作時發生錯誤：{error}")
            return False

def check_stock(db_name:str,sqty:int,bid:str)->str:
    with sqlite3.connect(db_name) as conn:
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT bstock FROM book WHERE bid = ?", (bid,))
            result = cursor.fetchone()
            if sqty > result[0]:
                return f'=> 錯誤：書籍庫存不足 (現有庫存: {result[0]})'
        except sqlite3.Error as error:
            print(f"執行 SELECT 操作時發生錯誤：{error}")

def sub_total(db_name:str,sqty:int,bid:str,sdiscount:int)->int:
    with sqlite3.connect(db_name) as conn:
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT bprice FROM book WHERE bid = ?", (bid,))
            result = cursor.fetchone()
            total =(result[0]*sqty)-sdiscount
            return total
        except sqlite3.Error as error:
            print(f"執行 SELECT 操作時發生錯誤：{error}")

def add_salereport(db_name:str)-> str:
    with sqlite3.connect(db_name) as conn:
        cursor = conn.cursor()
        while True:
            sdate = input("請輸入銷售日期 (YYYY-MM-DD)：")
            if not(len(sdate) == 10 and sdate.count('-') == 2):
                print("=> 錯誤：日期格式應為 YYYY-MM-DD，請重新輸入")
                continue   #
            mid = input("請輸入會員編號：").upper()
            bid = input("請輸入書籍編號：").upper()
            try:
                sqty = int(input("請輸入購買數量："))
                if sqty < 0:
                    print("=> 錯誤：數量必須為正整數，請重新輸入")
            except ValueError as e:
                print("=> 錯誤：數量必須為整數，請重新輸入")
            try:
                sdiscount = int(input("請輸入折扣金額："))
                if sdiscount < 0:
                    print("=> 錯誤：折扣必須為正整數，請重新輸入")
            except ValueError as e:
                print("=> 錯誤：折扣必須為整數，請重新輸入")
            if check_id(db_name,mid,bid) == False:
                print("=> 錯誤：會員編號或書籍編號無效")
                break
            stock_msg = check_stock(db_name, sqty, bid)
            if stock_msg:
                print(stock_msg)
                continue
            stotal = sub_total(db_name,sqty,bid,sdiscount)
            cursor.execute("INSERT INTO sale (sdate, mid, bid, sqty, sdiscount, stotal) VALUES (?, ?, ?, ?, ?, ?)", (sdate, mid, bid, sqty, sdiscount, stotal))
            print(f'=> 銷售記錄已新增！(銷售總額: {stotal})')
            conn.commit()
            break


def main():
    check_db()
    while True:
        print("*"*15+"選單"+"*"*15,end='')
        print(
"""
1. 新增銷售記錄
2. 顯示銷售報表
3. 更新銷售記錄
4. 刪除銷售記錄
5. 離開
""",end='')
        print("*"*35)
        mode = (input("請選擇操作項目(Enter 離開)：")).strip()
        if mode == "":
            break
        elif mode == "1" :
            print(mode)
            add_salereport(DB_NAME)
        elif mode == "2" :
            print(mode)
        elif mode == "3" :
            print(mode)
        elif mode == "4" :
            print(mode)
        elif mode == "5":
            break
        else:
            print("=> 請輸入有效的選項（1-5）\n")


if __name__ == '__main__':
    main()
