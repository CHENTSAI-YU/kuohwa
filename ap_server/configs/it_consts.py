
FLASK_PORT = 5000 #flask 的埠號

#API 伺服器跟資料庫建立連線時要用的位址跟埠號。
MYSQL_HOST = "localhost" # MySQL 資料庫伺服器位址
MYSQL_PORT = 3306 # MySQL 資料庫連線埠號
MYSQL_DATABASE = "project" # 要連的資料庫名稱
MYSQL_USER = "root" #資料庫登入帳號
MYSQL_PASSWD = "jessica4020"
MYSQL_CHARSET = "utf8mb4" #是資料庫連線時使用的字元編碼，決定文字資料在 API 伺服器跟 MySQL 之間傳輸、以及存進資料庫時怎麼轉換成位元組。
#確保你的帳號資料、信箱、備註等欄位如果之後有特殊字元，資料庫存得進去、讀出來也不會亂碼