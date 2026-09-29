#匯入與設定
# -*- coding:utf-8 -*-
import logging 
import pymysql ##匯入 pymysql（實際跟 MySQL 溝通的驅動程式）
from dbutils.pooled_db import PooledDB #PooledDB（連線池套件，管理多條資料庫連線重複使用）
from configs import ( #從 configs 拿資料庫連線資訊
    MYSQL_PORT,
    MYSQL_HOST,
    MYSQL_DATABASE,
    MYSQL_USER,
    MYSQL_PASSWD,
    MYSQL_CHARSET
)

#建立這個檔案專用的 log 記錄器（logger），之後每次查詢或執行失敗都會透過它記錄錯誤訊息。
logger = logging.getLogger(__name__)


#class MysqlAccess：整個資料庫存取的入口
class MysqlAccess(object):
    pool = None #pool 是一個類別屬性，存放連線池物件，一開始是 None，代表還沒建立連線池。

    #整個 class 用 @staticmethod 寫，代表不用先 MysqlAccess() 建立實例，直接 MysqlAccess.query(...) 這樣呼叫就好。

    @staticmethod #initialise()：建立連線池
    #負責跟 MySQL 建立一批可重複使用的連線（連線池），而不是每次查詢都重新連一次資料庫。
    def initialise(mincached=1, maxcached=5, maxconnections=10):
        """初始化 MySQL 連線池"""
        try:
            MysqlAccess.pool = PooledDB(
                creator=pymysql,  # 使用 pymysql 驅動
                maxconnections=maxconnections,  # 連線池允許的最大連線數
                mincached=mincached,            # 初始化時，連線池中最少空閒的連線數
                maxcached=maxcached,            # 連線池中最多空閒的連線數
                blocking=True,                  # 連線池滿時是否等待
                host=MYSQL_HOST,
                port=int(MYSQL_PORT),
                user=MYSQL_USER,
                password=MYSQL_PASSWD,
                database=MYSQL_DATABASE,
                charset=MYSQL_CHARSET,
                cursorclass=pymysql.cursors.DictCursor  # 讓查詢結果回傳字典格式 (Dict)，方便 API 使用
            )
            logger.info("MySQL Connection Pool Initialized Success.")
        except Exception as e:
            logger.error(f"MySQL Connection Pool Failed: {e}")

    #_get_conn()：拿一條可用連線
    @staticmethod
    def _get_conn(): #內部方法： _ 代表不對外開放，只給這個檔案內部用
        #如果連線池還沒建立（第一次呼叫），先自動呼叫 initialise() 建好，再從池子裡借一條連線出來用，是所有查詢/寫入方法的共用入口。
        if MysqlAccess.pool is None:
            MysqlAccess.initialise()
        return MysqlAccess.pool.connection()

    #query()：處理 SELECT 查詢
    @staticmethod
    #是 module.py 裡所有 MysqlAccess.query(...) 呼叫背後實際執行的地方。
    def query(sql, args=None): #args 是要傳入 SQL 裡 %s 佔位符的參數（防止 SQL injection）
        """執行 SELECT 查詢"""
        conn = None
        try:
            conn = MysqlAccess._get_conn() #呼叫前面的 _get_conn()，跟連線池借一條實際的資料庫連線出來，指派給 conn。
            with conn.cursor() as cursor: #游標（cursor），游標是實際拿來下 SQL 指令、讀取結果的工具。
                cursor.execute(sql, args or []) #把 SQL 指令送去資料庫執行，ql 是傳進來的查詢語法，args 是要塞進 %s 佔位符的實際值，如果呼叫時沒傳 args（預設是 None），就改用空 list []，避免 execute() 收到 None 出錯。
                return cursor.fetchall() #查完用 fetchall() 拿到全部結果（一個 list，每筆是一個字典）
        except Exception as e:
            logger.error(f"Query Error: {e}") #出錯就記 log 並往外丟例外（raise e，讓呼叫它的 module.py 那層可以決定怎麼處理）
            raise e
        finally: #無論成功失敗最後都會把連線 close() 還給連線池（finally 區塊保證一定執行）
            if conn:
                conn.close()  # 將連線歸還給連線池

    #execute()：處理 INSERT／UPDATE／DELETE
    @staticmethod
    def execute(sql, args=None):
        """執行 INSERT / UPDATE / DELETE 單筆異動"""
        conn = None
        try:
            conn = MysqlAccess._get_conn() #呼叫前面的 _get_conn()，跟連線池借一條實際的資料庫連線出來，指派給 conn。
            with conn.cursor() as cursor: #游標（cursor），游標是實際拿來下 SQL 指令、讀取結果的工具。
                result = cursor.execute(sql, args or []) #把 SQL 指令送去資料庫執行
                conn.commit() #把這次的異動真正寫進資料庫
                return result
        except Exception as e:
            if conn:
                conn.rollback() #把這次沒 commit 成功的異動復原，避免資料庫留下寫一半的資料
            logger.error(f"Execute Error: {e}")
            raise e
        finally:
            if conn:
                conn.close()

    #insert_many()：批次寫入
    @staticmethod
    def insert_many(sql, rows):
        """批次新增數據 (executemany)"""
        conn = None
        try:
            conn = MysqlAccess._get_conn() #呼叫前面的 _get_conn()，跟連線池借一條實際的資料庫連線出來，指派給 conn。
            with conn.cursor() as cursor: #游標，游標是實際拿來下 SQL 指令、讀取結果的工具。
                result = cursor.executemany(sql, rows) #用 executemany() 一次塞很多筆資料（rows 是一個 list，裡面每個元素是一組參數）
                conn.commit() #異動寫進資料庫
                return result
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"Insert Many Error: {e}")
            raise e
        finally: #把連線 close() 還給連線池
            if conn:
                conn.close()
