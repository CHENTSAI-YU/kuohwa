from apis.account.model import *
from apis.account.module import *
from flask import session
from base_api import CustomResource
from flask import request

ROLE_ADMIN = "Admin"


@api.route("/test")
class Login2(CustomResource):
    allow_roles = [ROLE_ADMIN]
    def post(self):
        print(api.payload)
        return "OK"


@api.route("/login")
class Login(CustomResource):
    @api.expect(account_input_payload)
    @api.marshal_with(account_output_payload)
    def post(self):
        data = api.payload
        result = Account.login(username=data["username"], passwd=data["passwd"])
        if result.get("result") == 0:
            session["roles"] = [ROLE_ADMIN]
        return result

#1
@api.route("/forget") #設定路由
class Forget(CustomResource):

    # @api.expect: 驗證並定義前端傳入的 Request Body 格式 (驗證輸入)
    @api.expect(forget_input_payload) 

    # @api.marshal_with: 定義並過濾 API 成功時的回應 JSON 結構 (過濾輸出)
    @api.marshal_with(output_payload) 

    def post(self):
        #處理使用者忘記密碼請求
        
        # api.payload: Flask-RESTX 全域變數，自動將前端傳入的 JSON Request Body 解析為 Python 字典
        # 範例結果：data = {"user_id": "itri@kuohwa.com"}
        data = api.payload 

        # 呼叫 module.py 的 forget()，傳入從字典中取得的 user_id
        # result 接收商業邏輯層回傳的字典結果
        result=Account.forget(user_id=data["user_id"]) #透過 data["user_id"] 取出前端傳入的字典中的 user_id 值。

        # 驗證結果判斷：
        # 若 result 字典中的 "result" 鍵值不等於 0 (代表帳號不存在/驗證失敗)，
        # 回傳查詢結果字典與 HTTP 狀態碼 400 (Bad Request)
        # Note: 回傳的 Tuple 格式為 (JSON內容, HTTP狀態碼)
        if result.get("result")!=0:
            return result, 400
        #驗證成功
        return result, 200

#2
@api.route("/get_account_list")
# CustomResource 說明：
# 專案自訂的基礎類別 (繼承自 Flask-RESTX Resource)，用於統一所有 API 的共用邏輯，
# 例如 Session 權限檢查、API Log 紀錄以及全域錯誤例外捕捉處理。
class GetAccountList(CustomResource):
    # @api.expect: 載入系統 base_input_payload 的原因：
    # 1. 於 Swagger UI 上為前端產生標準 Request 範例與規範
    # 2. 確保 Request 符合基礎資安/驗證結構，避免接收格式異常的 JSON
    #@api.expect(input_payload)
    #將回傳資料轉為規格書指定的完整結構
    @api.marshal_with(get_account_list_payload)

    # 規用 GET。理由：
    #圖片規格寫的是 Payload 空白，代表這支 API 不帶任何請求參數，純粹查資料，符合 GET 的語意（安全、可快取、無副作用）。
    def get(self):

        ## 呼叫商業邏輯層取得帳號清單 回傳結果為字典
        result=Account.get_account_list()

        if result.get("result")!=0:
            return result, 400

        return result, 200

#3 
@api.route("/add_account_list")
class AddAccountList(CustomResource):

    # 驗證傳入的 Request Body 格式
    @api.expect(addaccount_input_payload)
    #格式化 Response (回傳 result 與 message)
    @api.marshal_with(output_payload)
    def post(self):
        data = api.payload
        result=Account.add_account_list(user_id=data["user_id"], role=data["role"], email=data["email"])

        if result.get("result")!=0:
            return result, 400

        return result, 200

#4
@api.route("/delete_account_list")
class DeleteAccountList(CustomResource):
    # 驗證傳入 Request Body
    @api.expect(delete_account_payload)
    # 格式化 Response (回傳 result 與 message)
    @api.marshal_with(output_payload)
    def post(self):
        data = api.payload
        # 呼叫商業邏輯層執行刪除
        result=Account.delete_account_list(user_id=data["user_id"])

        if result.get("result")!=0:
            return result, 400

        return result, 200

#5
@api.route("/update_account_list")
class UpdateAccountList(CustomResource):
    @api.expect(update_account_payload)
    @api.marshal_with(output_payload)
    def post(self):
        data = api.payload
        result= Account.update_account_list(
            old_user_id=data["old_user_id"],
            data=data["data"]
        )

        if result.get("result")!=0:
            return result, 400

        return result, 200
