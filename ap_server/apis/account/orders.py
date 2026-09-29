from apis.account.model import *
from apis.account.module import *
from flask import session
from base_api import CustomResource

ROLE_ADMIN = "Admin"

#6
@order_api.route("/autosave_detect_table") #定義路由
#定義處理api的類別 繼承CustomResource 拿到共用邏輯
class AutosaveDetectTable(CustomResource):
    #只有角色是 Admin 的使用者才能呼叫api
    allow_roles = [ROLE_ADMIN]
    #傳進來的資料要符合格式
    @api.expect(autosave_detect_table_payload)
    #輸出要符合的格式
    @api.marshal_with(output_payload)
    def post(self): #定義 POST 請求方法
        data = api.payload #前端傳進來的JSON轉成字典
        #呼叫函式 取出來的資料傳入函式
        result= Account.autosave_detect_table(
            uuid=data["uuid"],
            data=data["data"]
        )

        if result.get("result")!=0:
            return result, 400

        return result, 200


#7
@order_api.route("/get_detect_table") #定義路由
class GetDetectTable(CustomResource): #定義處理的類別
    #只有Adnmin使用者才可以呼叫
    allow_roles = [ROLE_ADMIN]
    #前端輸入要符合的格式
    @api.expect(get_detect_table_payload)
    #回傳結果要符合的格式
    @api.marshal_with(getdetecttable_output_payload)
    
    def post(self): #定義處理請求的方法
        data=api.payload #前端傳進來的JSON轉成字典
        result=Account.get_detect_table(uuid=data["uuid"]) #將取出來的資料傳進函式
        if result.get("result")!=0:
            return result, 400

        return result, 200
#8
@order_api.route("/get_key_value_mapping")
class GetKeyValueMapping(CustomResource):
    allow_roles = [ROLE_ADMIN]
    @api.expect(get_key_value_mapping_payload)
    @api.marshal_with(getkeyvalue_output_payload)
    def post(self):
        data=api.payload
        result= Account.get_key_value_mapping(vendor=data["vendor"],file_type= data["file_type"])

        if result.get("result")!=0:
            return result, 400

        return result, 200
#9
@order_api.route("/autosave_key_value_mapping")
class AutosaveKeyValueMapping(CustomResource):
    allow_roles = [ROLE_ADMIN]
    @api.expect(autosave_key_value_mapping_payload)
    @api.marshal_with(output_payload)
    def post(self):
        payload = api.payload #payload 是字典
        data = payload.get("data", [])  # 去拿 Key 為 "data" 的內容
        result=Account.autosave_key_value_mapping(data)

        if result.get("result")!=0:
            return result, 400

        return result, 200
#10
@order_api.route("/get_image_path")
class GetImagePath(CustomResource):
    allow_roles = [ROLE_ADMIN]
    @api.expect(get_image_path_payload)
    @api.marshal_with(getimage_output_payload)
    def post(self):
        data=api.payload
        result=Account.get_image_path(uuid=data["uuid"])
        if result.get("result")!=0:
            return result, 400

        return result, 200
#11
@order_api.route("/autosave_image_path")
class autosave_image_path(CustomResource):
    allow_roles = [ROLE_ADMIN]
    @api.expect(autosave_image_path_payload)
    @api.marshal_with(output_payload)
    def post(self):
        data=api.payload
        result= Account.autosave_image_path(uuid=data["uuid"], front_path=data["front_path"], back_path=data["back_path"])
        if result.get("result")!=0:
            return result, 400

        return result, 200