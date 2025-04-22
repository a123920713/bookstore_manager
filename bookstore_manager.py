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

def create_db(db_name)-> str:
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

def add_salereport():
    return

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
            add_sale_report()
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
