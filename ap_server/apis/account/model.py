#從 flask_restplus 這個套件匯入四個工具：
from flask_restplus import Namespace, Resource, fields, model
#Namespace：用來把相關的 API 分組管理
#Resource：定義 API 路由 class 時要繼承的基礎類別（CustomResource 就是繼承它擴充的）。
#fields：用來定義 JSON 欄位的型態
#model：底層的資料結構定義工具

api = Namespace("account", description=u"帳號及權限管理") #建立一個叫 "account" 的命名空間（Namespace），代表「這個檔案裡定義的 API 都屬於帳號及權限管理這一類」。
#description 是給 Swagger 文件顯示用的說明文字。
#這個 api 變數之後會被 auth.py 用 @api.route(...)、@api.expect(...) 這些裝飾器使用，串起路由跟這裡定義的資料格式。

order_api=Namespace("order", description=u"訂單相關功能") #建立order_api的命名空間


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
#用 api.model(...) 定義一個叫 '忘記密碼'（這個名稱會顯示在 Swagger 文件上）的資料結構
#參數為在 Swagger 顯示的模型名稱
forget_input_payload=api.model(u'忘記密碼', {
    # example: 在 Swagger UI 上顯示的範例資料
    'user_id': fields.String(required=True, example="itri@kuohwa.com") #定義 user_id 欄位為字串
})
#結構只有一個欄位 user_id
#fields.String：這個欄位的型態必須是字串。
#required=True：這個欄位是必填的，前端沒傳就會被 @api.expect 擋下來,回傳 400 錯誤。
#example=""：給 Swagger 文件顯示的範例

#共用 驗證成功時輸出格式
#定義一個叫 'output' 的資料結構,規定回傳結果要有 result message
output_payload=api.model(u'output', {
    "result": fields.Integer(required=True, default=0),
    "message": fields.String(required=True, default="")
})
#default=0 預設值為0, default="" 預設字串為空字串


#2. get_account_list
#定義資料結構
getaccount_payload=api.model(u'帳號', {
    #為字串型態 必填 預設空字串
    'user_id':fields.String(required=True, default=""),
    #role 為 List型態，裡面資料為字串型態
    #型態是「字串的陣列」，一個帳號可以有多個角色
    'role':fields.List(fields.String, required=True, example=["admin", "super_user"]),
    'email':fields.String(required=True, default=""),
    'update_time':fields.String(required=True, example="")
})
#定義回傳格式
#aip.clone：複製output_payload的結構再加上data
get_account_list_payload=api.clone(u'帳號清單', output_payload, {
    #fields.Nested ：告訴 RESTX，data 欄位是一個列表 (fields.List)，且列表裡面的每一個元素都必須符合 getaccount_payload 定義的結構
    #data 是一個陣列，陣列裡每一個元素都要符合 user_id / role / email / update_time
    "data":fields.List(fields.Nested(getaccount_payload), required=True)
})
#定義「一筆帳號資料」的欄位結構，get_account_list_payload 則是把它包進 data 陣列裡，組成 get_account_list 這支 API 完整的回傳格式。

#3 add
#定義輸入格式
addaccount_input_payload=api.model(u'新增帳號', {
    'user_id': fields.String(required=True, default=""), #字串型態，必填欄位，預設空字串
    'role': fields.List(fields.String, required=True, default=[]), #角色清單，型態是串列，裡面的資料為字串，必填，預設空串列
    'email': fields.String(required=True, default="") #字串型態，必填欄位，預設空字串
})

#4 
#定義這個api收到的格式
delete_account_payload=api.model(u'刪除帳號', {
    #字串型態 必填 預設空字串
    'user_id': fields.String(required=True, default="")
})

# 5-1定義內部 data 物件的模型
#定義巢狀物件data裡面要有哪些欄位，取名叫 AccountData，會顯示在 Swagger 文件上
account_data_model = api.model('AccountData', {
    #字串型態 必填 預設為空字串 欄位的說明文字
    'new_user_id': fields.String(required=True, default="", description='新帳號'),
    #欄位是串列型態 裡面的元素是字串型態 必填 預設空串列
    'new_role': fields.List(fields.String, required=True, default=[], description='新角色清單'),
    'new_email': fields.String(required=True, default="", description='新信箱')
})
# 5-2定義外層的主模型
#定義輸入格式
update_account_payload = api.model('更新帳號', {
    'old_user_id': fields.String(required=True, description='舊帳號'),
    #data：欄位名稱 Nested：代表這個欄位的值是另一個 model（巢狀物件），不是單純的字串或數字。
    #account_data_model：Nested() 的第一個參數，指定這個巢狀物件裡面要符合哪一個 model 的結構。
    'data': fields.Nested(account_data_model, required=True, description='更新資料內容')
    #fields.Nested：這個欄位的值要符合 account_data_model 這個 model
})

#6
#定義輸入格式
autosave_detect_table_payload=order_api.model(u'表格偵測自動儲存 API', {
    #字串型態 必填
    "uuid": fields.String(required=True, description='文件 uuid', example="sa5e122hy215cb3degrt"),
    #fields.Raw 代表任意結構
    "data": fields.Raw(required=True, description='動態 JSON 資料')
    #因為裡面是「頁碼 -> 表格 -> 儲存格」這種動態巢狀結構，key 是浮動的頁碼/表格 ID，沒有固定的定義，
    #沒辦法用 fields.Nested 定義固定欄位，所以直接放行讓後端自己解析
})
#7
#定義輸入格式，掛在 order_api 這個 namespace
get_detect_table_payload=order_api.model(u'表格偵測 API', {
    #字串型態 必填 欄位名稱
    "uuid": fields.String(required=True, description='文件 uuid')
})
#定義回傳格式
getdetecttable_output_payload=order_api.clone(u'表格偵測輸出', output_payload, {
    #fields.Raw：這個欄位不限制、不驗證內部結構，前端或後端給什麼型態的資料都直接放行
    #因為data裡的頁碼、表格 ID 都不是固定名稱(key 會動態變化的巢狀結構)，無法像fields.Nested 那樣定義固定欄位去驗證
    "data": fields.Raw(required=True, description='動態表格偵測結果')
})
#8
get_key_value_mapping_payload=order_api.model(u'對照表輸入', {
    "vendor":fields.String(required=True, description='名稱'),
    "file_type":fields.String(required=True, description='檔案類型')
})

getkeyvalue_output_payload=order_api.model(u'對照表輸出', {
    "result": fields.Integer(required=True, default=0),
    "message": fields.String(required=True, default=""),
    # 巢狀 model 要用 fields.Nested，不能直接放 dict
    "data":fields.Raw(required=True, description='key-value 對照表資料')
})
#9-1
data_payload=order_api.model(u'data', {
    "field":fields.String(required=True, example="epr_key1"),
    "fieldvalue":fields.List(fields.String, required=True, example=["Bo", "Borad"]), #指定列表裝的是什麼型別
    "vendor":fields.String(required=True, example=""),
    "file_type":fields.String(required=True, description='檔案類型', example="")
})
#9-2
autosave_key_value_mapping_payload=order_api.model(u'自動儲存 API',{
    "data":fields.List(fields.Nested(data_payload), required=True)
})
#10
get_image_path_payload=order_api.model(u'圖片路徑 API', {
    "uuid":fields.String(required=True, description='圖片 uuid')
})
getimage_model=order_api.model(u'圖片路徑', {
    "uuid":fields.String(required=True, example=""),
    "front_path":fields.String(required=True, example=""), 
    "back_path":fields.String(required=True, example="")
})
getimage_output_payload=order_api.model(u'圖片路徑輸出', {
    "result": fields.Integer(required=True, default=0),
    "message": fields.String(required=True, default=""),
    "data":fields.Nested(getimage_model, required=True)
})
#11
autosave_image_path_payload=order_api.model(u'自動儲存圖片路徑 API', {
    "uuid":fields.String(required=True, description='圖片 uuid'), 
    "front_path":fields.String(required=True, description=''), 
    "back_path":fields.String(required=True, description='')
})