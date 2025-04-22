import sqlite3

DB_NAME = 'D:/Web程式設計/bookstore_manager/bookstore.db'

def check_db()->None:

    """檢查資料表是否存在，若不存在則新增資料表。"""

    try:
        print(create_db(DB_NAME))
    except sqlite3.IntegrityError :
        print("")
        print("資料表已存在，無須新增資料表")
        print("")

def create_db(db_name: str)-> str:

    """建立一個新的資料表"""

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

def check_id(db_name: str, mid: str, bid: str)->bool:

    """檢查book_id與menber_id是否存在"""

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

def check_stock(db_name: str, sqty: int, bid: str)->str:

    """確認書籍的庫存"""

    with sqlite3.connect(db_name) as conn:
        cursor = conn.cursor()

        try:
            cursor.execute("SELECT bstock FROM book WHERE bid = ?", (bid,))
            result = cursor.fetchone()
            if sqty > result[0]:
                return f'=> 錯誤：書籍庫存不足 (現有庫存: {result[0]})'
                conn.rollback()
        except sqlite3.Error as error:
            print(f"執行 SELECT 操作時發生錯誤：{error}")

def sub_total(db_name: str, sqty: int, bid: str, sdiscount: int)->int:

    """計算扣除折扣後的總金額"""

    with sqlite3.connect(db_name) as conn:
        cursor = conn.cursor()

        try:
            cursor.execute("SELECT bprice FROM book WHERE bid = ?", (bid,))
            result = cursor.fetchone()
            total =(result[0]*sqty)-sdiscount
            return total
        except sqlite3.Error as error:
            print(f"執行 SELECT 操作時發生錯誤：{error}")

def add_salereport(db_name: str)-> None:

    """新增銷售紀錄"""

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
                conn.rollback()

            try:
                sdiscount = int(input("請輸入折扣金額："))
                if sdiscount < 0:
                    print("=> 錯誤：折扣必須為正整數，請重新輸入")
            except ValueError as e:
                print("=> 錯誤：折扣必須為整數，請重新輸入")
                conn.rollback()

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

def show_salereport(db_name: str)->None:

    """顯示所有銷售紀錄"""

    with sqlite3.connect(db_name) as conn:
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT
                    sale.sid,
                    sale.sdate,
                    member.mname,
                    book.btitle,
                    book.bprice,
                    sale.sqty,
                    sale.sdiscount
                FROM sale
                JOIN member ON sale.mid = member.mid
                JOIN book ON sale.bid = book.bid
                ORDER BY sale.sid
            """)

            results = cursor.fetchall()
            print("==================== 銷售報表 ====================")

            for idx, row in enumerate(results, start=1):
                sid, sdate, mname, btitle, bprice, sqty, sdiscount = row
                subtotal = bprice * sqty - sdiscount
                print(f"銷售 #{idx}")
                print(f"銷售編號: {sid}")
                print(f"銷售日期: {sdate}")
                print(f"會員姓名: {mname}")
                print(f"書籍標題: {btitle}")
                print("--------------------------------------------------")
                print("單價\t數量\t折扣\t小計")
                print("--------------------------------------------------")
                print(f"{bprice:,}\t{sqty}\t{sdiscount:,}\t{subtotal:,}")
                print("--------------------------------------------------")
                print(f"銷售總額: {subtotal:,}")
                print("==================================================\n")

        except sqlite3.Error as e:
            print(f"=> 錯誤：無法查詢銷售資料：{e}")

def get_salereport(db_name: str)->None:

    """取得當前資料表內的銷售紀錄並顯示，確認是否要刪除或修改"""

    with sqlite3.connect(db_name) as conn:
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT
                    sale.sid,
                    sale.sdate,
                    member.mname,
                    sale.sdiscount,
                    sale.stotal
                FROM sale
                JOIN member ON sale.mid = member.mid
                JOIN book ON sale.bid = book.bid
                ORDER BY sale.sid
            """)

            results = cursor.fetchall()
            print("======== 銷售記錄列表 ========")

            for idx, row in enumerate(results, start=1):
                sid, sdate, mname,sdiscount,stotal = row
                #1. 銷售編號: 1 - 會員: Alice - 日期: 2024-01-15
                print(f"{idx}. 銷售編號:{idx} - 會員:{mname} - 日期:{sdate}")

            print("================================")


        except sqlite3.Error as e:
            print(f"=> 錯誤：無法查詢銷售資料：{e}")

def update_salereport(db_name: str) -> None:

    """更新銷售紀錄內容"""

    with sqlite3.connect(db_name) as conn:
        cursor = conn.cursor()

        try:
            sid_input = input("請選擇要更新的銷售編號 (輸入數字或按 Enter 取消): ").strip()
            if not sid_input:
                print("=> 已取消更新。")
                return
            sid = int(sid_input)
            if sid < 0:
                print("=> 錯誤：數量必須為正整數，請重新輸入")
                conn.rollback()
        except ValueError as e:
                print("=> 錯誤：數量必須為整數，請重新輸入")
                conn.rollback()
                return

        cursor.execute("SELECT * FROM sale WHERE sid = ?", (sid,))
        sale = cursor.fetchone()

        if not sale:
            print(f"=> 查無銷售編號 {sid}")
            return

        try:
            discount_input = input("請輸入新的折扣金額：").strip()
            if not discount_input.isdigit():
                print("=> 請輸入有效的折扣金額（整數）")
                return

            new_discount = int(discount_input)

            cursor.execute("SELECT stotal FROM sale WHERE sid = ?", (sid,))
            result = cursor.fetchone()
            unit_price = result[0]

            cursor.execute("SELECT sdiscount FROM sale WHERE sid = ?",(sid,))
            result = cursor.fetchone()
            old_discount = result[0]

            new_total = unit_price + old_discount -  new_discount

            cursor.execute("""
                UPDATE sale
                SET sdiscount = ?, stotal = ?
                WHERE sid = ?
            """, (new_discount, new_total, sid))
            conn.commit()

            print(f"=> 銷售編號 {sid} 已更新！(銷售總額: {new_total})")

        except Exception as e:
            print(f"=> 更新失敗：{e}")

def delete_salereport(db_name: str)->None:

     """刪除銷售紀錄"""

     with sqlite3.connect(db_name) as conn:
        cursor = conn.cursor()

        try:
            sid_input = input("請選擇要刪除的銷售編號 (輸入數字或按 Enter 取消): ").strip()
            if not sid_input:
                print("=> 已取消刪除。")
                return
            sid = int(sid_input)
            if sid < 0:
                print("=> 錯誤：數量必須為正整數，請重新輸入")
                conn.rollback()
        except ValueError as e:
                print("=> 錯誤：數量必須為整數，請重新輸入")
                conn.rollback()
                return

        cursor.execute("SELECT * FROM sale WHERE sid = ?", (sid,))
        sale = cursor.fetchone()

        if not sale:
            print(f"=> 查無銷售編號 {sid}")
            return

        try:
            cursor.execute('DELETE FROM sale WHERE sid = ?', (sid,))
            print(f"銷售編號 {sid} 已刪除")
            conn.commit()
        except sqlite3.Error as error:
            print(f"執行 DELETE 操作時發生錯誤：{error}")

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
            add_salereport(DB_NAME)

        elif mode == "2" :
            show_salereport(DB_NAME)

        elif mode == "3" :
            get_salereport(DB_NAME)
            update_salereport(DB_NAME)

        elif mode == "4" :
            get_salereport(DB_NAME)
            delete_salereport(DB_NAME)

        elif mode == "5":
            break

        else:
            print("=> 請輸入有效的選項（1-5）\n")

if __name__ == '__main__':
    main()
