from utils.mysql_utils import MysqlAccess
import os
from werkzeug.utils import secure_filename
from utils.mail_utils import MailUtils
import secrets
import string
#datetime 是 Python 內建處理日期時間的模組，from datetime import datetime 是從裡面把 datetime 這個 class 匯入進來，才能直接用 datetime.now() 抓「現在的時間」。
from datetime import datetime


class Account(object):
    @staticmethod
    def login(username, passwd):
        sql = """SELECT USER_ID, PASSWORD, ROLE FROM TBL_USER_ACCOUNT WHERE USER_ID = %s"""
        result = MysqlAccess.query(sql, (username,))

        if not result:
            return {"result": 1, "message": "帳號或密碼錯誤"}

        stored_password = result[0].get("PASSWORD")
        if passwd != stored_password:
            return {"result": 1, "message": "帳號或密碼錯誤"}

        return {
            "result": 0,
            "message": ""
        }

    #1
    @staticmethod
    def forget(user_id):
        #檢查使用者帳號是否在資料庫

        #SQL 查詢語法
        sql = """SELECT USER_ID, EMAIL FROM TBL_USER_ACCOUNT WHERE USER_ID = %s"""

        # 執行 SQL 查詢：
        # 1. 傳入 sql 語法
        # 2. 參數以 Tuple (user_id,) 傳入 換掉佔位符 (單一元素的 Tuple 必須加上逗號，否則 Python 會視為一般括號字串導致傳參失敗)
        # 3. result 接收資料庫回傳的查詢結果 List
        #MysqlAccess: 封裝 DB 連線與操作的工具類別
        result = MysqlAccess.query(sql, (user_id,))
        if not result:
            return {"result": 1, 
                    "message": "查無此帳號"
                    }

        # 2. 取得使用者的 Email (若資料庫的 EMAIL 欄位為空，則預設使用 user_id)
        to_email = result[0].get("EMAIL")
        #防呆
        if not to_email:
            return {
                "result": 1,
                "message": "此帳號尚未設定信箱，請聯絡管理員"
            }
        # 3. 產生 8 位數隨機英數字密碼
        alphabet = string.ascii_letters + string.digits
        new_password = ''.join(secrets.choice(alphabet) for _ in range(8))

        # 4. 呼叫 MailUtils 發送重設密碼信件
        mail_sent = MailUtils.send_forget_password_mail(
            to_email=to_email, 
            new_password=new_password
        )

        # 5. 判斷寄信結果
        if not mail_sent:
            return {
                "result": 1,
                "message": "郵件發送失敗，請確認信箱設定或稍後再試"
            }
        #Step 6. 寄信成功才更新密碼：寫回資料庫並回傳成功
        # secrets.choice(alphabet)：從傳入的序列（這裡的 alphabet 代表所有大寫字母、小寫字母與數字）中，隨機抽取「一個」字元。
        # for _ in range(8)：生一個從 0 到 7 的數列，代表這個動作要重複執行 8 次。
        # 整合效果：(secrets.choice(alphabet) for _ in range(8)) 會連續進行 8 次隨機抽字，產生出包含 8 個單一字元的清單/產生器
        # ''.join(...)：將傳入的字元串列，用指定的連接符號黏合成一個完整的字串。
        # 單引號 ''：代表「中間不加任何分隔符號（空字串）」。寫 ''.join(['a', 'B', '3']) 結果為 "aB3"
        # upadte_sql="""UPDATE TBL_USER_ACCOUNT SET PASSWORD = %s WHERE USER_ID = %s"""
        update_sql = """UPDATE TBL_USER_ACCOUNT SET PASSWORD = %s WHERE USER_ID = %s"""
        MysqlAccess.execute(update_sql, (new_password, user_id))

        return {
           "result": 0,
           "message": ""
        }
    #2
    @staticmethod
    def get_account_list():  # 沒有傳參數進來
        #查詢指令存到sql
        sql = """ SELECT USER_ID, ROLE, EMAIL, UPDATE_TIME FROM TBL_USER_ACCOUNT """

        # 執行查詢指令 result接收回傳結果(字典)
        result = MysqlAccess.query(sql)
        #建立空串列 放取出的資料
        result_data = []

        #result的每一筆值存到row直到迴圈結束(取到result的最後一筆值)
        for row in result:
            # 1. 處理 user_id (用字典 Key 取值) 如果資料不存在回傳空字串(防呆)
            #row.get("USER_ID") 取字典的值(user_id對應的值)
            user_id = row.get("USER_ID") if row.get("USER_ID") is not None else ""

            # 2. 處理 role_raw (用字典 Key 取值)
            role_raw = row.get("ROLE") if row.get("ROLE") is not None else ""
            # 3. 處理 email (用字典 Key 取值) 
            email = row.get("EMAIL") if row.get("EMAIL") is not None else ""

            # 4. 處理 update_time (用字典 Key 取值)
            update_time = str(row.get("UPDATE_TIME")) if row.get("UPDATE_TIME") is not None else ""

            # 5. 處理 role 切割成 List
            # 語法拆解：
            # 1. if role_raw: 檢查角色字串是否有值 (非空字串與非 None)
            # 2. .split(","): 用逗號作為分隔符，將字串切成串列 (例如 "admin,super_user" -> ["admin", "super_user"])
            # 3. else []: 若 role_raw 為空，則賦予空串列 [] 防呆，避免程式崩潰
            role_list = role_raw.split(",") if role_raw else []

            #取出來的值加到新串列
            result_data.append({
                "user_id": user_id,
                "role": role_list,
                "email": email,
                "update_time": update_time
            })

        #回傳格式
        return {
            "result": 0,
            "message": "",
                "data": result_data
        }

    

    #3 add
    @staticmethod
    def add_account_list(user_id, role, email):
        #先檢查是否有一樣的user_id
        check_sql = """SELECT USER_ID FROM TBL_USER_ACCOUNT WHERE USER_ID=%s"""
        check_result = MysqlAccess.query(check_sql, (user_id,))

        if check_result:
            return {
            "result": 1,
            "message": "帳號已存在"
        }

        # 1. 將 role 清單轉為逗號分隔的字串 (例如 ["admin", "super_user"] -> "admin,super_user")
        if isinstance(role, list):
            role_str = ",".join(role)
        else:
            role_str = str(role) if role else ""

        #取得目前時間字串
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        #寫入資料指令
        sql="""INSERT INTO TBL_USER_ACCOUNT (USER_ID, ROLE, EMAIL, UPDATE_TIME) VALUES (%s, %s, %s, %s)"""

        try:
            #執行sql寫入指令
            MysqlAccess.execute(sql, (user_id, role_str, email, now))

            return {
                "result": 0,
                "message": ""
            }
        except Exception as e:
            return{
                "result":1,
                "message":"新增帳號失敗"
            }

    #4
    @staticmethod
    def delete_account_list(user_id):
        #先檢查帳號是存在
        check_sql="""SELECT USER_ID FROM TBL_USER_ACCOUNT WHERE USER_ID=%s"""
        check_reusult=MysqlAccess.query(check_sql, (user_id,))

        #如果找不到使用者，回傳錯誤訊息
        if not check_reusult:
            return{
                "result":1,
                "message": "找不到使用者"
            }
        #刪除指定帳號
        sql = "DELETE FROM TBL_USER_ACCOUNT WHERE user_id = %s"

        MysqlAccess.execute(sql, (user_id,))

        return {
            "result": 0, 
            "message": ""
        }

    #5
    @staticmethod
    def update_account_list(old_user_id, data):
        #檢查舊帳號是否存在
        check_sql="""SELECT USER_ID FROM TBL_USER_ACCOUNT WHERE USER_ID=%s"""
        check_result=MysqlAccess.query(check_sql, (old_user_id,))
        if not check_result:
            return{
                "result":1,
                "message":"找不到使用者"
            }

        #取data裡面的資料
        new_user_id=data.get("new_user_id")
        new_role_list=data.get("new_role", []) #回傳預設的空陣列 []
        new_email=data.get("new_email")

        #取輸入的資料後檢查帳號是否存在
        if new_user_id != old_user_id:
            user_check_sql = """SELECT USER_ID FROM TBL_USER_ACCOUNT WHERE USER_ID=%s"""
            user_check_result = MysqlAccess.query(user_check_sql, (new_user_id,))
            if user_check_result:
                return {
                    "result": 1,
                    "message": "帳號已存在"
                }

        # 1. 將角色陣列轉為逗號分隔字串 (例如: ['Admin', 'Super User'] -> 'Admin,Super User')
        role_str = ",".join(new_role_list)

        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # 2. 組裝 UPDATE SQL 語法
        sql = """UPDATE TBL_USER_ACCOUNT SET USER_ID = %s, ROLE = %s, EMAIL = %s, UPDATE_TIME = %s WHERE USER_ID = %s"""

        # 3. 執行 SQL 更新動作
        MysqlAccess.execute(sql, (new_user_id, role_str, new_email, now, old_user_id))

        return {
            "result": 0,
            "message": ""
        }

    #6
    @staticmethod
    def autosave_detect_table(uuid, data):
         # 先刪除這個 uuid 底下的舊資料，再寫入新資料，避免重複疊加
        delete_sql = """DELETE FROM USER_DETECT_TABLE WHERE UUID = %s"""
        MysqlAccess.execute(delete_sql, (uuid,))
        
        #拆解 data 字典，取得頁碼 (page_number) 與該頁對應的表格資料 (table)
        for page_number, table in data.items(): #.items() 會同時將字典的 Key 與 Value 打包成一對對的組合，沒用會只拿到字典的 Key（鍵），拿不到內部的 Value（值）
            #拆解 table 字典，取得表格識別碼 (table_id) 與表格詳細資訊 (table_info)
            for table_id, table_info in table.items():
                upper_left=table_info.get("upper_left")
                upper_right=table_info.get("upper_right")
                lower_right=table_info.get("lower_right")
                lower_left=table_info.get("lower_left")

                #從 table_info 中取出儲存格清單 (cells)，若不存在則預設回傳空陣列 []
                cells = table_info.get("cells", [])

                #逐一取出該表格內部的每一個單元格資訊 (cell)
                for cell in cells: 
                    sql="""INSERT INTO USER_DETECT_TABLE 
                        (UUID, UPPER_LEFT, UPPER_RIGHT, LOWER_RIGHT, LOWER_LEFT, 
                        NAME, CELLS_UPPER_LEFT, CELLS_UPPER_RIGHT, CELLS_LOWER_RIGHT, CELLS_LOWER_LEFT, START_ROW, END_ROW, START_COL, END_COL, CONTENT) 
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""

                    #執行 SQL 語法並帶入對應的參數值#
                    result= MysqlAccess.execute(sql, (uuid, upper_left, upper_right, lower_right, lower_left,  #上面已取出
                                                      cell.get("name"), 
                                                      cell.get("upper_left"),
                                                      cell.get("upper_right"), 
                                                      cell.get("lower_right"), 
                                                      cell.get("lower_left"),
                                                      cell.get("start_row"),
                                                      cell.get("end_row"),
                                                      cell.get("start_col"),
                                                      cell.get("end_col"),
                                                      cell.get("content")
                                                )) 
                    # 每次執行寫入後，立刻檢查結果；若失敗則即時中斷並回傳
                    if not result:
                                return{
                                    "result":1, 
                                    "message":"資料儲存失敗"
                                    }

        return {
            "result": 0, 
            "message": ""
        }
    
    #7
    @staticmethod 
    def get_detect_table(uuid):
        #根據傳入的 uuid 查詢 USER_DETECT_TABLE 表格的資料
        sql="""SELECT UPPER_LEFT, UPPER_RIGHT, LOWER_RIGHT, LOWER_LEFT, 
        NAME, CELLS_UPPER_LEFT, CELLS_UPPER_RIGHT, CELLS_LOWER_RIGHT, CELLS_LOWER_LEFT, START_ROW, END_ROW, START_COL, END_COL, CONTENT
        FROM USER_DETECT_TABLE WHERE UUID=%s"""

        # 執行 SQL 查詢，取得該 uuid 的所有平鋪紀錄 (傳回 List of Dicts)
        rows=MysqlAccess.query(sql, (uuid, ))

        #若資料庫內查無此 uuid 的資料，直接回傳錯誤訊息與空字典
        if not rows:
            return{
                "result": 1,
                "message": "找不到此文件",
                "data": {}
            }

        # 3. 初始化動態 JSON 字典
        data={}

        #4. 走訪每一筆 DB 紀錄，動態建立「頁碼 -> 表格 -> 儲存格」階層
        for row in rows:
            # 動態抓取 DB 頁碼與表格 ID；若欄位不存在，則以預設變數值替代 (確保 key 不會寫死)
            page_num = str(row.get("PAGE_NUMBER", "0"))
            table_id = str(row.get("TABLE_ID", "table_0"))

            # 第一層動態建立：檢查當前頁碼是否存在，不存在則初始化
            if page_num not in data:
                data[page_num] = {}

            # 第二層動態建立：檢查當前表格 ID 是否存在，不存在則建立外圍座標與 cells 陣列
            if table_id not in data[page_num]:
                data[page_num][table_id] = {
                    "upper_left": row.get("UPPER_LEFT"),
                    "upper_right": row.get("UPPER_RIGHT"),
                    "lower_right": row.get("LOWER_RIGHT"),
                    "lower_left": row.get("LOWER_LEFT"),
                    "cells": []
            }

            # 第三層儲存格組裝：打包當前 cell 的詳細資料
            cell = {
                "name": row.get("NAME"),
                "upper_left": row.get("CELLS_UPPER_LEFT"), 
                "upper_right": row.get("CELLS_UPPER_RIGHT"),
                "lower_right": row.get("CELLS_LOWER_RIGHT"),
                "lower_left": row.get("CELLS_LOWER_LEFT"),
                "start_row": row.get("START_ROW"),
                "end_row": row.get("END_ROW"),
                "start_col": row.get("START_COL"),
                "end_col": row.get("END_COL"),
                "content": row.get("CONTENT")
            }

            # 將 cell 自動推入對應「頁碼」與「表格」底下的 cells 清單
            data[page_num][table_id]["cells"].append(cell)

        return{
            "result":0,
            "message": "",
            "data": data
        }
    #8
    @staticmethod
    def get_key_value_mapping(vendor, file_type):
        #根據傳入的資料查詢，已經知道 VENDOR 和 FILETYPE 了，SQL 只需要抓出剩下還沒抓的
        sql="""SELECT FIELD,FIELDVALUE FROM USER_MAPPING_TABLE WHERE VENDOR=%s AND FILETYPE=%s"""

        rows=MysqlAccess.query(sql, (vendor, file_type))

        if not rows:
            return{
                "result": 1,
                "message": "查無對照資料",
                "data": {}
            }
        #存放分類後的 key-value 對照表
        data={}
        # 5. 走訪 SQL 查詢出來的每一筆紀錄 (row)
        for row in rows:
            filed=row.get("FIELD")
            filedvalue=row.get("FIELDVALUE")

            # 若當前 field (Key) 還沒在 data 字典中，則初始化為空陣列 []
            if filed not in data:
                data[filed]=[]

            # 將對應的 field_value 自動推入 (append) 該 key 底下的陣列中
            data[filed].append(filedvalue)

        return{
            "result":0,
            "message": "",
            "data": data
        }
    #9
    @staticmethod
    def autosave_key_value_mapping(data): # 將輸入的資料存進資料表
        for item in data: #跑串列裡的資料
            field=item.get("field")
            fieldvalue=item.get("fieldvalue")
            vendor=item.get("vendor")
            file_type=item.get("file_type")

            # 先刪除同一組 vendor+file_type+field 的舊資料，避免重複疊加
            delete_sql = """DELETE FROM USER_MAPPING_TABLE WHERE VENDOR=%s AND FILETYPE=%s AND FIELD=%s"""
            MysqlAccess.execute(delete_sql, (vendor, file_type, field))

            sql="""INSERT INTO USER_MAPPING_TABLE (VENDOR, FILETYPE, FIELD, FIELDVALUE) VALUES (%s, %s, %s, %s)"""
            # fieldvalue：["Bo", "Borad"]
            for value in fieldvalue:
                MysqlAccess.execute(sql, (vendor, file_type, field, value))

        return{
            "result":0, 
            "message":""
        }
    #10
    @staticmethod
    def get_image_path(uuid):
        sql="""SELECT * FROM USER_IMAGE_PATH_TABLE WHERE UUID=%s"""
        temp=MysqlAccess.query(sql, (uuid, ))

        if not temp:
            return{
                "result":1,
                "message":"uuid 不存在",
                "data":{}
            }
        # 取得查詢結果（因 UUID 具唯一性，符合條件的資料只會有一筆，故取清單的第一項 res[0]）
        data=temp[0]
        return{
            "result":0,
            "message":"",
            "data":{
                "uuid":data.get("UUID"),
                "front_path":data.get("FRONT_PATH"),
                "back_path":data.get("BACK_PATH")
            }
        }

    #11
    @staticmethod
    def autosave_image_path(uuid, front_path, back_path):
        delete_sql="""DELETE FROM USER_IMAGE_PATH_TABLE WHERE UUID=%s"""
        MysqlAccess.execute(delete_sql, (uuid, ))
        insert_sql="""INSERT INTO USER_IMAGE_PATH_TABLE (UUID, FRONT_PATH, BACK_PATH) VALUES (%s, %s, %s)"""
        MysqlAccess.execute(insert_sql, (uuid, front_path, back_path))

        return{
            "result":0, 
            "message":""
        }