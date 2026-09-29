from apis.account.model import * #匯入 model.py 裡定義的所有輸入/輸出格式模型
from apis.account.module import * #匯入 module.py 裡的 Account class 匯入進來，這個檔案才能呼叫 Account.forget()、Account.login() 這些實際處理商業邏輯的方法。
from flask import session #匯入 Flask 提供的 session 物件，功能是在使用者兩次請求之間「記住東西」，這個專案拿它來記住使用者登入後的角色（session["roles"] = [...]），之後每次呼叫其他 API 都能從 session 讀出角色判斷有沒有權限。
from base_api import CustomResource #匯入專案自訂的 CustomResource 基礎類別，每一支 API 的 class（像 Forget、Login）都要繼承它，才能拿到共用的權限檢查、輸入驗證失敗處理等邏輯。


ROLE_ADMIN = "Admin" #定義變數


# @api.route("/test")
# class Login2(CustomResource):
#     allow_roles = [ROLE_ADMIN]
#     def post(self):
#         print(api.payload)
#         return "OK"


@api.route("/login")
class Login(CustomResource):
    @api.expect(account_input_payload)
    @api.marshal_with(account_output_payload)
    def post(self):
        #把前端傳來的 JSON Request Body 解析成 Python 字典，存到 data
        data = api.payload
        #從 data 取出 username、passwd，Account.login()
        result = Account.login(username=data["username"], passwd=data["passwd"])
        #如果 result 欄位是 0，代表帳號密碼驗證成功
        if result.get("result") == 0:
            #把登入結果裡的角色清單（role）寫進 Flask session
            #之後每次呼叫其他 API，CustomResource 會從這個 session 讀角色去比對 allow_roles
            session["roles"] = result.get("role", [])
        return result

#1
#@api.route是 Flask-RESTX 提供的裝飾器，功能是把底下的 class 註冊成一個 API 路由。
#當有人打這個網址時，要交給 forget 這個 class 處理。
#/api 是在 設定的 url_prefix，/account 是 namespace 前綴，/forget 才是這裡指定的路徑）
@api.route("/forget") #設定路由
#定義Forget類別，繼承 CustomResource
#CustomResource：Forget 繼承自 base_api/custom_cls.py 定義的 CustomResource 基礎類別
class Forget(CustomResource):

    # @api.expect: 是 Flask-RESTX 的裝飾器，功能是宣告這支 API 預期收到的輸入格式
    @api.expect(forget_input_payload) 
    # @api.marshal_with: 定義並過濾 API 成功時的回應 JSON 結構 (過濾輸出)
    @api.marshal_with(output_payload) 

    #處理使用者忘記密碼請求
    def post(self): #定義 class 收到 HTTP POST 請求時要執行的方法
        #self 代表「這個物件實例本身」
        
        # api.payload: Flask-RESTX 全域變數，自動將前端傳入的 JSON Request Body 解析為 Python 字典，存到data
        # data = {"user_id": "itri@kuohwa.com"}
        data = api.payload 

        # 呼叫 module.py 的 forget()，傳入從字典中取得的 user_id
        # result 接收商業邏輯層回傳的字典結果
        result=Account.forget(user_id=data["user_id"]) #從 data 字典裡取出 user_id，呼叫 module.py 的 Account.forget()，執行「查帳號→產生新密碼→寄信→更新密碼」整套商業邏輯，結果存到 result。

        # 驗證結果判斷：
        # 若 result 字典中的 "result" 鍵值不等於 0 (代表帳號不存在/驗證失敗)，
        # 回傳查詢結果字典與 HTTP 狀態碼 400 (Bad Request)
        # Note: 回傳的 Tuple 格式為 (JSON內容, HTTP狀態碼)
        if result.get("result")!=0:
            return result, 400
        #驗證成功
        return result, 200

#2
@api.route("/get_account_list") #設定路由
# CustomResource 說明：
# 專案自訂的基礎類別 (繼承自 Flask-RESTX Resource)，用於統一所有 API 的共用邏輯，
class GetAccountList(CustomResource):
    #allow_roles 是 CustomResource定義好的
    #設定只有角色為 Admin 的使用者才能呼叫這個 api
    allow_roles = [ROLE_ADMIN]
    #將回傳資料轉為規格書指定的完整結構
    @api.marshal_with(get_account_list_payload)

    def get(self): #定義處理 HTTP GET 請求的方法

        #呼叫 module.py 的邏輯，查出全部帳號清單，結果存到 result 回傳結果為字典
        result=Account.get_account_list()

        #如果查詢結果的 result 欄位不是 0
        if result.get("result")!=0:
            return result, 400

        return result, 200

#3 
@api.route("/add_account_list") #設定路由
class AddAccountList(CustomResource): #定義API 的處理類別，繼承 CustomResource 拿到共用邏輯
    #只有 session["roles"] 裡包含 ROLE_ADMIN 這個角色的人，才能成功呼叫 add_account_list
    allow_roles = [ROLE_ADMIN] #允許呼叫這支 API 的角色清單
    #allow_roles：CustomResource 這個基礎類別定義好的屬性名稱

    #宣告輸入格式要符合 addaccount_input_payload
    @api.expect(addaccount_input_payload)
    #回傳格式
    @api.marshal_with(output_payload)
    
    #定義處理 HTTP POST 請求的方法
    def post(self):
        data = api.payload #把前端傳來的 JSON Request Body 解析成 Python 字典
        #從 data 字典取出 user_id、role、email，呼叫 module.py 執行新增
        result=Account.add_account_list(user_id=data["user_id"], role=data["role"], email=data["email"])

        #如果新增結果的 result 欄位不是 0 回傳狀態碼
        if result.get("result")!=0:
            return result, 400

        return result, 200

#4
@api.route("/delete_account_list") #設定路由
#定義處理這支 API 的類別，繼承 CustomResource 拿到權限檢查、輸入驗證等共用邏輯
class DeleteAccountList(CustomResource):
    #只有角色是 Admin 的使用者才能呼叫
    allow_roles = [ROLE_ADMIN]
    #前端傳來的資料格式要符合 delete_account_payload 定義的格式
    @api.expect(delete_account_payload)
    #回傳的 JSON 要符合 output_payload 的格式
    @api.marshal_with(output_payload)

    def post(self): #定義處理 HTTP POST 請求的方法
        #將前端傳來的資料轉成字典
        data = api.payload
        #將取出來的user_id傳入函式 執行刪除帳號 用result接收結果(字典)
        result=Account.delete_account_list(user_id=data["user_id"])

        if result.get("result")!=0:
            return result, 400

        return result, 200

#5
@api.route("/update_account_list") #設定路由
#定義處理API的類別，繼承CustomResource拿到權限檢查、輸入驗證
class UpdateAccountList(CustomResource):
    #角色是 Admin 的使用者才能呼叫api
    allow_roles = [ROLE_ADMIN]
    #前端傳來的資料格式要符合定義格式
    @api.expect(update_account_payload)
    #回傳的資料要符合的格式
    @api.marshal_with(output_payload)
    #定義處理 HTTP POST 請求的方法
    def post(self):
        data = api.payload #前端傳進來資料解析成字典 存到data
        #取出data裡面的值 傳到函式 再用reesult接收結果
        result= Account.update_account_list(
            old_user_id=data["old_user_id"],
            data=data["data"]
        )

        if result.get("result")!=0:
            return result, 400 #回傳失敗結果與 HTTP 400

        return result, 200
