# -*- coding:utf-8 -*-
import logging
import pymysql
from dbutils.pooled_db import PooledDB
from configs import (
    MYSQL_HOST,
    MYSQL_PORT,
    MYSQL_DATABASE,
    MYSQL_USER,
    MYSQL_PASSWD,
    MYSQL_CHARSET
)


logger = logging.getLogger(__name__)



class MysqlAccess(object):
    pool = None

    @staticmethod
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

    @staticmethod
    def _get_conn():
        if MysqlAccess.pool is None:
            MysqlAccess.initialise()
        return MysqlAccess.pool.connection()

    @staticmethod
    def query(sql, args=None):
        """執行 SELECT 查詢"""
        conn = None
        try:
            conn = MysqlAccess._get_conn()
            with conn.cursor() as cursor:
                cursor.execute(sql, args or [])
                return cursor.fetchall()
        except Exception as e:
            logger.error(f"Query Error: {e}")
            raise e
        finally:
            if conn:
                conn.close()  # 將連線歸還給池子

    @staticmethod
    def execute(sql, args=None):
        """執行 INSERT / UPDATE / DELETE 單筆異動"""
        conn = None
        try:
            conn = MysqlAccess._get_conn()
            with conn.cursor() as cursor:
                result = cursor.execute(sql, args or [])
                conn.commit()
                return result
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"Execute Error: {e}")
            raise e
        finally:
            if conn:
                conn.close()

    @staticmethod
    def insert_many(sql, rows):
        """批次新增數據 (executemany)"""
        conn = None
        try:
            conn = MysqlAccess._get_conn()
            with conn.cursor() as cursor:
                result = cursor.executemany(sql, rows)
                conn.commit()
                return result
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"Insert Many Error: {e}")
            raise e
        finally:
            if conn:
                conn.close()
