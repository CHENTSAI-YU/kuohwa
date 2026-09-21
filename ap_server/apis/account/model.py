from flask_restplus import Namespace, Resource, fields, model

api = Namespace("account", description=u"帳號及權限管理")


base_input_payload = api.model(u'基礎輸入參數定義', {
    'result': fields.Integer(required=True, default=0),
    'message': fields.String(required=True, default=""),
})


account_input_payload = api.model(u'帳號input', {
    'username': fields.String(required=True, example="tami"),
    'passwd': fields.String(required=True, example="tami")
})

account_output_payload = api.clone(u'帳號output', base_input_payload, {
    'data': fields.String(required=True),
    "test": fields.String(required=True)
})

#1 忘記密碼 輸入格式定義
#api.model: 定義 JSON 資料結構，第一個參數為在 Swagger 顯示的模型名稱
forget_input_payload=api.model(u'忘記密碼', {
    # required=True: 標示欄位為必填
    # example: 在 Swagger UI 上顯示的範例資料
    'user_id': fields.String(required=True, example="itri@kuohwa.com") #定義 user_id 欄位為字串
})

#共用 驗證成功時輸出格式
#default=0 預設值為0, default="" 預設字串為空字串
output_payload=api.model(u'output', {
    "result": fields.Integer(required=True, default=0),
    "message": fields.String(required=True, default="")
})

#2. get_account_list
getaccount_payload=api.model(u'帳號', {
    'user_id':fields.String(required=True, default=""),
    #role 為 List型態，裡面資料為字串型態
    'role':fields.List(fields.String, required=True, example=["admin", "super_user"]),
    'email':fields.String(required=True, default=""),
    'update_time':fields.String(required=True, example="")
})
get_account_list_payload=api.clone(u'帳號清單', output_payload, {
    #複製 output_payload 的結構，加上data
    #fields.Nested ：告訴 RESTX，data 欄位是一個列表 (fields.List)，
    # 且列表裡面的每一個元素都必須符合 getaccount_payload 定義的 JSON 結構！
    "data":fields.List(fields.Nested(getaccount_payload), required=True)
})

#3 add
addaccount_input_payload=api.model(u'新增帳號', {
    'user_id': fields.String(required=True, default=""),
    'role': fields.List(fields.String, required=True, default=[]),
    'email': fields.String(required=True, default="")
})

#4 
delete_account_payload=api.model(u'刪除帳號', {
    'user_id': fields.String(required=True, default="")
})

# 5-1. 定義內部 data 物件的模型
account_data_model = api.model('AccountData', {
    'new_user_id': fields.String(required=True, default="", description='新帳號'),
    'new_role': fields.List(fields.String, required=True, default=[], description='新角色清單'),
    'new_email': fields.String(required=True, default="", description='新信箱')
})
# 5-2. 定義外層的主模型
update_account_payload = api.model('更新帳號', {
    'old_user_id': fields.String(required=True, description='舊帳號'),
    'data': fields.Nested(account_data_model, required=True, description='更新資料內容')
})

#6
autosave_detect_table_payload=api.model(u'表格偵測自動儲存 API', {
    "uuid": fields.String(required=True, description='文件 uuid', example="sa5e122hy215cb3degrt"),
    "data": fields.Raw(required=True, description='動態 JSON 資料')
})
#7
get_detect_table_payload=api.model(u'表格偵測 API', {
    "uuid": fields.String(required=True, description='文件 uuid')
})
getdetecttable_output_payload=api.model(u'表格偵測輸出', {
    "result": fields.Integer(required=True, default=0),
    "message": fields.String(required=True, default=""),
    # data 底下的 key（page_number、table_id）是動態的，無固定 schema，
    # 用 dict 會讓 flask_restplus 產生 swagger.json 時對 dict 呼叫 __schema__ 而 500，
    # 改用 fields.Raw 直接放行任意結構
    "data": fields.Raw(required=True, description='動態表格偵測結果')
})
#8
get_key_value_mapping_payload=api.model(u'對照表輸入', {
    "vendor":fields.String(required=True, description='名稱'),
    "file_type":fields.String(required=True, description='檔案類型')
})

getkeyvalue_output_payload=api.model(u'對照表輸出', {
    "result": fields.Integer(required=True, default=0),
    "message": fields.String(required=True, default=""),
    # 巢狀 model 要用 fields.Nested，不能直接放 dict
    "data":fields.Raw(required=True, description='key-value 對照表資料')
})
#9-1
data_payload=api.model(u'data', {
    "field":fields.String(required=True, example="epr_key1"),
    "fieldvalue":fields.List(fields.String, required=True, example=["Bo", "Borad"]), #指定列表裝的是什麼型別
    "vendor":fields.String(required=True, example=""),
    "file_type":fields.String(required=True, description='檔案類型', example="")
})
#9-2
autosave_key_value_mapping_payload=api.model(u'自動儲存 API',{
    "data":fields.List(fields.Nested(data_payload), required=True)
})
#10
get_image_path_payload=api.model(u'圖片路徑 API', {
    "uuid":fields.String(required=True, description='圖片 uuid')
})
getimage_model=api.model(u'圖片路徑', {
    "uuid":fields.String(required=True, example=""),
    "front_path":fields.String(required=True, example=""), 
    "back_path":fields.String(required=True, example="")
})
getimage_output_payload=api.model(u'圖片路徑輸出', {
    "result": fields.Integer(required=True, default=0),
    "message": fields.String(required=True, default=""),
    "data":fields.Nested(getimage_model, required=True)
})
#11
autosave_image_path_payload=api.model(u'自動儲存圖片路徑 API', {
    "uuid":fields.String(required=True, description='圖片 uuid'), 
    "front_path":fields.String(required=True, description=''), 
    "back_path":fields.String(required=True, description='')
})